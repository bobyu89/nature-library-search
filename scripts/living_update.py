"""Living / update searches: re-run the saved strategy later, then screen only what is new.

usage:
  python -I living_update.py --old WORK/records_sema.json --new WORK_2027/records_sema.json --out WORK_2027/new_only_sema.json

Matches by DOI, PMID or normalised title; writes the new-only records (keeping their new uids) and prints
counts for the update PRISMA diagram ("previous review: n included; new records identified: n").
Screen new_only with the same criteria file and decisions workflow; carry the old screen_<topic>.json forward.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from dedup import norm_text  # noqa: E402


def keys(r):
    k = {('t', norm_text(r['title']))}
    if r.get('doi'):
        k.add(('d', r['doi']))
    if r.get('pmid'):
        k.add(('p', r['pmid']))
    return k


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--old', required=True)
    ap.add_argument('--new', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    old = json.load(open(a.old, encoding='utf8'))
    new = json.load(open(a.new, encoding='utf8'))
    seen = set().union(*(keys(r) for r in old)) if old else set()
    fresh = [r for r in new if not (keys(r) & seen)]
    json.dump(fresh, open(a.out, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print(json.dumps({'previous_unique': len(old), 'current_unique': len(new), 'new_records': len(fresh)}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
