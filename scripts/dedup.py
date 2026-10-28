"""Parse database exports (RIS, CINAHL JSON) for one topic, deduplicate, write records_<topic>.json.

usage:
  python -I dedup.py --topic sema --prefix S --out WORK \
      --input PubMed=raw/pubmed.ris --input Embase=raw/embase.ris --input CINAHL=raw/cinahl.json \
      --input "Cochrane=raw/cochrane_central_all.ris@2018-2026" [--near-dups]

Matching: same DOI, same PMID, or same normalised title with years within 1 or the same first author.
Master record priority: PubMed > Embase > Cochrane > Scopus > CINAHL > Airiti.
"""
import argparse, html, json, os, re, sys
from collections import Counter, defaultdict

PRIORITY = {'PubMed': 0, 'Embase': 1, 'Cochrane': 2, 'Scopus': 3, 'CINAHL': 4, 'Airiti': 5}


def parse_ris(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    recs, cur = [], None
    for line in text.split('\n'):
        m = re.match(r'^([A-Z][A-Z0-9])  -  ?(.*)$', line)
        if not m:
            if cur is not None and line.strip() and cur.get('_last'):
                cur[cur['_last']][-1] += ' ' + line.strip()
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == 'TY':
            cur = {'_last': None}
            recs.append(cur)
        if cur is None:
            continue
        if tag == 'ER':
            cur = None
            continue
        cur.setdefault(tag, []).append(val)
        cur['_last'] = tag
    return recs


def first(r, *tags):
    for t in tags:
        if r.get(t):
            return r[t][0]
    return ''


def norm_doi(d):
    d = (d or '').strip().lower()
    d = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', d)
    return d.replace('‐', '-').replace('‑', '-').rstrip('.')


def norm_text(t):
    t = html.unescape(t or '').lower().replace('‐', '-').replace('‑', '-')
    return re.sub(r'[\W_]+', '', t)


def year_of(s):
    m = re.search(r'(19|20)\d{2}', s or '')
    return int(m.group(0)) if m else None


def from_ris(db, r, fname):
    rec = {'db': db, 'file': fname,
           'title': html.unescape(first(r, 'TI', 'T1')),
           'authors': [html.unescape(x) for x in (r.get('AU') or r.get('A1') or []) if x != 'et al.'],
           'year': year_of(first(r, 'PY', 'Y1', 'DA')),
           'journal': html.unescape(first(r, 'T2', 'JF', 'JO', 'JA')),
           'volume': first(r, 'VL'), 'issue': first(r, 'IS'),
           'doi': norm_doi(first(r, 'DO')),
           'abstract': html.unescape(' '.join(r.get('AB', []) or r.get('N2', []))),
           'type': first(r, 'M3') or first(r, 'TY'), 'lang': first(r, 'LA'),
           'accession': first(r, 'AN'), 'url': first(r, 'UR')}
    sp, ep = first(r, 'SP'), first(r, 'EP')
    rec['pages'] = sp + ('-' + ep if ep else '')
    pmid = rec['accession'][5:] if rec['accession'].startswith('PMID:') else ''
    for c in r.get('C3', []) + r.get('C5', []):
        m = re.search(r'(\d{7,8})\b', c)
        if m and ('PUBMED' in c or re.fullmatch(r'\d{7,8}', c.strip())):
            pmid = m.group(1)
            break
    rec['pmid'] = pmid
    if db == 'Airiti' and rec['url'] and not rec['url'].startswith('http'):
        rec['url'] = 'https://www.airitilibrary.com/' + rec['url']
    if first(r, 'TY') == 'RPRT' or rec['accession'].startswith('NCT'):
        rec['type'] = 'Clinical trial registry record'
    return rec


def from_cinahl(it):
    return {'db': 'CINAHL', 'file': 'cinahl', 'title': it.get('title', ''), 'authors': it.get('authors', []),
            'year': year_of(it.get('date', '')), 'journal': it.get('source', ''), 'volume': it.get('volume', ''),
            'issue': '', 'pages': it.get('pageStart', '') + ('-' + it['pageEnd'] if it.get('pageEnd') else ''),
            'doi': norm_doi(it.get('doi', '')), 'abstract': it.get('abstract', ''),
            'type': '; '.join(it.get('docTypes', []) + it.get('pubTypes', [])), 'lang': '', 'pmid': '',
            'accession': 'CINAHL AN ' + str(it.get('an', '')), 'url': ''}


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def load(spec):
    db, rest = spec.split('=', 1)
    path, yr = (rest.split('@') + [None])[:2]
    if path.endswith('.json'):
        items = [from_cinahl(i) for i in json.load(open(path, encoding='utf8'))]
    else:
        items = [from_ris(db, r, os.path.basename(path)) for r in parse_ris(open(path, encoding='utf8').read())]
    if yr:
        lo, hi = [int(x) for x in yr.split('-')]
        items = [i for i in items if i['year'] and lo <= i['year'] <= hi]
    return db, items


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--topic', required=True)
    ap.add_argument('--prefix', default=None, help='uid prefix (default: first letter of topic, upper case)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--input', action='append', required=True, help='DB=path[@yyyy-yyyy]')
    ap.add_argument('--near-dups', action='store_true', help='list unmerged titles with similarity > 0.9')
    a = ap.parse_args()
    prefix = a.prefix or a.topic[0].upper()

    recs, counts = [], Counter()
    for spec in a.input:
        db, items = load(spec)
        counts[db] += len(items)
        recs += items
    for i, r in enumerate(recs):
        r['rid'] = i
        r['nt'] = norm_text(r['title'])

    uf = UF(len(recs))
    for key in ('doi', 'pmid'):
        seen = {}
        for r in recs:
            if r[key]:
                if r[key] in seen:
                    uf.union(seen[r[key]], r['rid'])
                else:
                    seen[r[key]] = r['rid']
    by_title = defaultdict(list)
    for r in recs:
        if len(r['nt']) >= 12:
            by_title[r['nt']].append(r)
    for group in by_title.values():
        for x in group:
            for y in group:
                if x['rid'] >= y['rid']:
                    continue
                same_au = bool(x['authors'] and y['authors'] and norm_text(x['authors'][0])[:6] == norm_text(y['authors'][0])[:6])
                if same_au or x['year'] is None or y['year'] is None or abs(x['year'] - y['year']) <= 1:
                    uf.union(x['rid'], y['rid'])

    clusters = defaultdict(list)
    for r in recs:
        clusters[uf.find(r['rid'])].append(r)
    unique = []
    for members in clusters.values():
        members.sort(key=lambda r: (PRIORITY.get(r['db'], 9), -len(r['abstract'])))
        m = dict(members[0])
        if not m['abstract']:
            m['abstract'] = max((x['abstract'] for x in members), key=len)
        for f in ('doi', 'pmid'):
            if not m[f]:
                m[f] = next((x[f] for x in members if x[f]), '')
        m['sources'] = sorted({x['db'] for x in members}, key=lambda d: PRIORITY.get(d, 9))
        m['n_records'] = len(members)
        m.pop('nt', None)
        m.pop('rid', None)
        unique.append(m)
    unique.sort(key=lambda r: (-(r['year'] or 0), r['title']))
    for i, r in enumerate(unique, 1):
        r['uid'] = '%s%04d' % (prefix, i)
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, 'records_%s.json' % a.topic)
    json.dump(unique, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    summary = {'per_database': dict(counts), 'total': len(recs), 'unique': len(unique), 'duplicates': len(recs) - len(unique)}
    json.dump(summary, open(os.path.join(a.out, 'dedup_%s.json' % a.topic), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))

    if a.near_dups:
        from difflib import SequenceMatcher
        items = [(norm_text(r['title']), r) for r in unique]
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (ta, ra), (tb, rb) = items[i], items[j]
                if len(ta) < 20 or abs(len(ta) - len(tb)) > 15 or (ta[:15] != tb[:15] and ta[-15:] != tb[-15:]):
                    continue
                s = SequenceMatcher(None, ta, tb).ratio()
                if s > 0.9:
                    print('near-dup %.3f %s(%s,%s) | %s(%s,%s) | %s' % (s, ra['uid'], ra['db'], ra['year'], rb['uid'], rb['db'], rb['year'], ra['title'][:90]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
