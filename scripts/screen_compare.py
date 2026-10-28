"""Compare two independent screeners (or a screener vs the author's pilot decisions): agreement, Cohen's kappa,
and a conflict sheet for adjudication.

usage:
  python -I screen_compare.py --a WORK/decisions --b WORK/decisions_B --topic sema --out WORK/conflicts_sema.csv
  python -I screen_compare.py --a WORK/decisions --b WORK/pilot_author_sema.csv --topic sema --out WORK/pilot_report.csv

--a / --b accept a decisions folder (<topic>_*.json from subagents) or a CSV with columns uid,decision[,reason].
Kappa is reported on the binary include-for-full-text decision (FT vs any exclusion) — the decision that matters
for PRISMA — and on the 6-category code. The conflict sheet lists only records where FT/exclude differ.
After adjudication, fill the 'final' column (FT|P|I|O|D|L) and run with --resolve to write decisions_final/.
"""
import argparse, csv, glob, json, os, sys
from collections import Counter


def load(path, topic):
    out = {}
    if os.path.isdir(path):
        for f in sorted(glob.glob(os.path.join(path, '%s_*.json' % topic))):
            for d in json.load(open(f, encoding='utf8')):
                out[d['uid']] = (d['decision'], d.get('reason', ''))
    else:
        for r in csv.DictReader(open(path, encoding='utf-8-sig')):
            out[r['uid']] = (r['decision'].strip().upper(), r.get('reason', ''))
    return out


def kappa(pairs):
    n = len(pairs)
    if not n:
        return float('nan')
    po = sum(1 for x, y in pairs if x == y) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--topic', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--records', help='records_<topic>.json for titles in the conflict sheet')
    ap.add_argument('--resolve', help='filled conflict CSV → writes <dir of --a>_final/<topic>_1.json')
    a = ap.parse_args()
    A, B = load(a.a, a.topic), load(a.b, a.topic)
    common = sorted(set(A) & set(B))
    if a.resolve:
        final = {u: A[u][0] for u in A}
        why = {u: A[u][1] for u in A}
        for r in csv.DictReader(open(a.resolve, encoding='utf-8-sig')):
            if r.get('final'):
                final[r['uid']] = r['final'].strip().upper()
                why[r['uid']] = 'adjudicated: ' + (r.get('note') or '')
        outdir = a.a.rstrip('/\\') + '_final'
        os.makedirs(outdir, exist_ok=True)
        json.dump([{'uid': u, 'decision': final[u], 'reason': why[u]} for u in A],
                  open(os.path.join(outdir, '%s_1.json' % a.topic), 'w', encoding='utf8'), ensure_ascii=False)
        print('final decisions written to', outdir)
        return
    binary = [(A[u][0] == 'FT', B[u][0] == 'FT') for u in common]
    full = [(A[u][0], B[u][0]) for u in common]
    agree = sum(1 for x, y in binary if x == y)
    titles = {}
    if a.records:
        titles = {r['uid']: r['title'] for r in json.load(open(a.records, encoding='utf8'))}
    conflicts = [u for u in common if (A[u][0] == 'FT') != (B[u][0] == 'FT')]
    with open(a.out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['uid', 'title', 'A', 'A_reason', 'B', 'B_reason', 'final', 'note'])
        for u in conflicts:
            w.writerow([u, titles.get(u, ''), A[u][0], A[u][1], B[u][0], B[u][1], '', ''])
    report = {'n_common': len(common), 'only_in_A': len(set(A) - set(B)), 'only_in_B': len(set(B) - set(A)),
              'agreement_FT_vs_exclude': round(agree / len(common), 3) if common else None,
              'kappa_FT_vs_exclude': round(kappa(binary), 3), 'kappa_6_codes': round(kappa(full), 3),
              'FT_A': sum(x for x, _ in binary), 'FT_B': sum(y for _, y in binary), 'conflicts': len(conflicts),
              'conflict_sheet': a.out}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    json.dump(report, open(os.path.splitext(a.out)[0] + '_kappa.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
