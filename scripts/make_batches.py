"""Split records_<topic>.json into screening batches for parallel subagents.

usage: python -I make_batches.py --records WORK/records_sema.json --n 5 [--abstract-chars 2500]
writes WORK/batches/<topic>_1.jsonl … (one JSON object per line: uid, title, year, journal, type, sources, abstract)
"""
import argparse, json, math, os, re, sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--records', required=True)
    ap.add_argument('--n', type=int, default=5)
    ap.add_argument('--abstract-chars', type=int, default=2500)
    a = ap.parse_args()
    topic = re.match(r'records_(.+)\.json$', os.path.basename(a.records)).group(1)
    recs = json.load(open(a.records, encoding='utf8'))
    out = os.path.join(os.path.dirname(a.records), 'batches')
    os.makedirs(out, exist_ok=True)
    size = math.ceil(len(recs) / a.n)
    for b in range(a.n):
        part = recs[b * size:(b + 1) * size]
        with open(os.path.join(out, '%s_%d.jsonl' % (topic, b + 1)), 'w', encoding='utf8') as f:
            for r in part:
                f.write(json.dumps({'uid': r['uid'], 'title': r['title'], 'year': r['year'], 'journal': r['journal'],
                                    'type': r['type'], 'sources': r['sources'],
                                    'abstract': (r['abstract'] or '')[:a.abstract_chars]}, ensure_ascii=False) + '\n')
        print(topic, b + 1, len(part))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
