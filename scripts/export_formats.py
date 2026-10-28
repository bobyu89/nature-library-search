"""Collaboration exports of the deduplicated (and optionally screened) set.

usage:
  python -I export_formats.py --topic sema --work WORK --out DIR --format ris      # one RIS for EndNote / Zotero / Mendeley
  python -I export_formats.py --topic sema --work WORK --out DIR --format rayyan   # Rayyan CSV (blind co-screening)
  python -I export_formats.py --topic sema --work WORK --out DIR --format covidence  # RIS with no screening tags

ris: includes screening tags (KW) and AI reasons (N1) when screen_<topic>.json exists.
rayyan/covidence: no decisions included, so a co-screener (teacher, classmate) screens blind.
"""
import argparse, csv, json, os, sys

TA = {'FT': '進入全文', 'P': '族群不符', 'I': '介入不符', 'O': '結果不符', 'D': '研究設計不符', 'L': '語言不符'}


def ris(r, s=None, tags=True):
    out = ['TY  - ' + ('RPRT' if 'registry' in (r['type'] or '').lower() else 'JOUR')]
    out += ['AU  - ' + x for x in r['authors']]
    out += ['TI  - ' + r['title'], 'T2  - ' + r['journal'], 'PY  - ' + str(r['year'] or '')]
    for tag, key in (('VL', 'volume'), ('IS', 'issue'), ('SP', 'pages'), ('DO', 'doi'), ('UR', 'url'), ('LA', 'lang')):
        if r.get(key):
            out.append('%s  - %s' % (tag, r[key]))
    if r.get('abstract'):
        out.append('AB  - ' + r['abstract'].replace('\n', ' '))
    out.append('AN  - ' + r['uid'] + ((' PMID:' + r['pmid']) if r.get('pmid') else ''))
    out.append('DB  - ' + ', '.join(r['sources']))
    if tags and s:
        out.append('KW  - 篩選1:' + TA[s['ta']])
        if s.get('ft'):
            out.append('KW  - 篩選2:' + {'include': '納入評讀', 'exclude': '排除-' + s.get('ft_code', ''), 'not_retrieved': '無法取得全文'}[s['ft']])
        out.append('N1  - ' + s['ta_reason'] + ((' | ' + s['ft_reason']) if s.get('ft_reason') else '') + '（AI 初篩，請作者複核）')
    out.append('ER  - ')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--topic', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--format', choices=['ris', 'rayyan', 'covidence'], required=True)
    a = ap.parse_args()
    recs = json.load(open(os.path.join(a.work, 'records_%s.json' % a.topic), encoding='utf8'))
    sp = os.path.join(a.work, 'screen_%s.json' % a.topic)
    scr = json.load(open(sp, encoding='utf8')) if os.path.exists(sp) else {}
    os.makedirs(a.out, exist_ok=True)
    if a.format in ('ris', 'covidence'):
        path = os.path.join(a.out, '%s_%s.ris' % (a.topic, a.format))
        open(path, 'w', encoding='utf8').write('\n\n'.join(ris(r, scr.get(r['uid']), a.format == 'ris') for r in recs) + '\n')
    else:
        path = os.path.join(a.out, '%s_rayyan.csv' % a.topic)
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['key', 'title', 'authors', 'journal', 'issn', 'volume', 'issue', 'pages', 'year', 'publisher', 'url', 'abstract', 'notes'])
            for r in recs:
                w.writerow([r['uid'], r['title'], ' and '.join(r['authors']), r['journal'], '', r.get('volume', ''), r.get('issue', ''),
                            r.get('pages', ''), r['year'] or '', '', r.get('url') or ('https://doi.org/' + r['doi'] if r.get('doi') else ''),
                            r.get('abstract', ''), 'sources: ' + ', '.join(r['sources'])])
    print(path, len(recs))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
