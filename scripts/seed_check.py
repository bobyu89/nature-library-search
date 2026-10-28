"""Search-strategy validation: are the known key papers ("seed set") captured by each database export?

usage: python -I seed_check.py --seeds seeds.csv --raw "PubMed=raw/pubmed.ris" --raw "Embase=raw/embase.ris" ... [--out WORK/seed_check.csv]
seeds.csv columns: label,doi,pmid,title  (any of doi/pmid/title may be blank; title match is normalised)

Report a table seed × database (Y/-) and recall per database and overall. A seed missed everywhere means the
strategy has a hole: inspect which concept block excluded it before running screening.
"""
import argparse, csv, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from dedup import load, norm_doi, norm_text  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--seeds', required=True)
    ap.add_argument('--raw', action='append', required=True, help='DB=path[@yyyy-yyyy]')
    ap.add_argument('--out')
    a = ap.parse_args()
    seeds = list(csv.DictReader(open(a.seeds, encoding='utf-8-sig')))
    dbs = {}
    for spec in a.raw:
        db, items = load(spec)
        idx = dbs.setdefault(db, {'doi': set(), 'pmid': set(), 'title': set()})
        for r in items:
            idx['doi'].add(r['doi'])
            idx['pmid'].add(r['pmid'])
            idx['title'].add(norm_text(r['title']))
    rows, hit_any = [], 0
    for s in seeds:
        d, p, t = norm_doi(s.get('doi', '')), (s.get('pmid') or '').strip(), norm_text(s.get('title', ''))
        row = {'label': s.get('label') or s.get('title', '')[:40]}
        found = False
        for db, idx in dbs.items():
            ok = (d and d in idx['doi']) or (p and p in idx['pmid']) or (t and len(t) > 12 and t in idx['title'])
            row[db] = 'Y' if ok else '-'
            found |= bool(ok)
        row['any'] = 'Y' if found else 'MISSED'
        hit_any += found
        rows.append(row)
    cols = ['label'] + list(dbs) + ['any']
    print(' | '.join(cols))
    for r in rows:
        print(' | '.join(r[c] for c in cols))
    recall = {db: '%d/%d' % (sum(r[db] == 'Y' for r in rows), len(rows)) for db in dbs}
    recall['any'] = '%d/%d' % (hit_any, len(rows))
    print('recall', json.dumps(recall, ensure_ascii=False))
    if a.out:
        with open(a.out, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
