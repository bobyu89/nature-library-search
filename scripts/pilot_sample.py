"""Draw a calibration (pilot) sample for the author to screen by hand before the full run.

usage: python -I pilot_sample.py --records WORK/records_sema.json --n 50 --out WORK/pilot_sema.csv [--seed 7]

Stratified: half from records whose title/abstract contains any --hint term (likely relevant), half at random,
so the pilot contains enough potential includes to calibrate on. The author fills 'decision' (FT|P|I|O|D|L) and
'reason'; then compare with the AI screener on the same uids using screen_compare.py.
"""
import argparse, csv, json, random, sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--records', required=True)
    ap.add_argument('--n', type=int, default=50)
    ap.add_argument('--out', required=True)
    ap.add_argument('--hint', action='append', default=[], help='term suggesting relevance, e.g. randomi, MACE')
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    random.seed(a.seed)
    recs = json.load(open(a.records, encoding='utf8'))
    hints = [h.lower() for h in a.hint]
    likely = [r for r in recs if hints and any(h in (r['title'] + ' ' + (r['abstract'] or '')).lower() for h in hints)]
    k = min(len(likely), a.n // 2)
    pick = random.sample(likely, k)
    rest = [r for r in recs if r not in pick]
    pick += random.sample(rest, min(len(rest), a.n - k))
    random.shuffle(pick)
    with open(a.out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['uid', 'title', 'abstract', 'decision', 'reason'])
        for r in pick:
            w.writerow([r['uid'], r['title'], (r['abstract'] or '')[:1500], '', ''])
    print('pilot sample', len(pick), '→', a.out, '(likely-relevant stratum: %d)' % k)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
