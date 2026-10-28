"""Backward (reference lists) and forward (cited-by) citation chasing for included studies via OpenAlex.

usage: python -I citation_chase.py --doi 10.1056/nejmoa2307563 --doi 10.1111/1753-0407.70082 \
          --records WORK/records_sema.json --out WORK/chase_sema.json [--mailto you@example.org] [--max-cited-by 400]

Writes candidates that are NOT already in records_<topic>.json (matched by DOI or normalised title), each with
title, year, venue, doi, abstract (reconstructed from OpenAlex's inverted index) and how it was found.
Screen them with the same criteria; report the counts in the PRISMA box "Records identified from other methods:
citation searching".
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from dedup import norm_doi, norm_text  # noqa: E402

API = 'https://api.openalex.org/'


def get(url, mailto):
    if mailto:
        url += ('&' if '?' in url else '?') + 'mailto=' + urllib.parse.quote(mailto)
    for attempt in range(4):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=60).read())
        except Exception:
            time.sleep(2 + 3 * attempt)
    return None


def abstract(inv):
    if not inv:
        return ''
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return ' '.join(w for _, w in pos)


def slim(w, how):
    return {'how': how, 'openalex': w.get('id'), 'title': w.get('title') or '', 'year': w.get('publication_year'),
            'venue': ((w.get('primary_location') or {}).get('source') or {}).get('display_name', ''),
            'doi': norm_doi(w.get('doi') or ''), 'type': w.get('type'), 'abstract': abstract(w.get('abstract_inverted_index'))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--doi', action='append', required=True)
    ap.add_argument('--records')
    ap.add_argument('--out', required=True)
    ap.add_argument('--mailto', default='')
    ap.add_argument('--max-cited-by', type=int, default=400)
    a = ap.parse_args()
    have_doi, have_t = set(), set()
    if a.records:
        for r in json.load(open(a.records, encoding='utf8')):
            have_doi.add(r['doi'])
            have_t.add(norm_text(r['title']))
    found, stats = {}, {}
    for d in a.doi:
        w = get(API + 'works/doi:' + urllib.parse.quote(norm_doi(d)), a.mailto)
        if not w:
            stats[d] = 'not found in OpenAlex'
            continue
        refs = w.get('referenced_works', [])
        back = []
        for i in range(0, len(refs), 50):
            ids = '|'.join(x.rsplit('/', 1)[-1] for x in refs[i:i + 50])
            res = get(API + 'works?per-page=50&filter=openalex:' + ids, a.mailto) or {}
            back += res.get('results', [])
        fwd, cursor = [], '*'
        while cursor and len(fwd) < a.max_cited_by:
            res = get(API + 'works?per-page=200&cursor=%s&filter=cites:%s' % (cursor, w['id'].rsplit('/', 1)[-1]), a.mailto) or {}
            fwd += res.get('results', [])
            cursor = (res.get('meta') or {}).get('next_cursor')
        for x, how in [(b, 'backward:' + d) for b in back] + [(f, 'forward:' + d) for f in fwd]:
            s = slim(x, how)
            if (s['doi'] and s['doi'] in have_doi) or norm_text(s['title']) in have_t:
                continue
            key = s['doi'] or norm_text(s['title'])
            if key in found:
                found[key]['how'] += '; ' + how
            else:
                found[key] = s
        stats[d] = {'references': len(back), 'cited_by': len(fwd)}
    out = sorted(found.values(), key=lambda r: -(r['year'] or 0))
    json.dump(out, open(a.out, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print(json.dumps({'seeds': stats, 'new_candidates': len(out)}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
