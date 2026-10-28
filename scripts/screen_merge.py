"""Merge subagent title/abstract decisions and the full-text spec into screen/counts JSON.

usage: python -I screen_merge.py --topic sema --work WORK
reads  WORK/records_<topic>.json, WORK/decisions/<topic>_*.json, WORK/ft_<topic>.json, WORK/dedup_<topic>.json
writes WORK/screen_<topic>.json (per uid) and WORK/counts_<topic>.json (PRISMA numbers)

ft_<topic>.json:
{"categories": {"SEL": {"label": "...", "short": "..."}},
 "include": ["S0939"], "not_retrieved": {"A0318": "reason"},
 "exclude": {"SEL": ["S0081"]}, "notes": {"S0214": "specific note"},
 "basis": {"S0081": "abstract"}}   # optional; default fulltext
"""
import argparse, glob, json, os, sys
from collections import Counter

TA = {'P': '族群不符', 'I': '介入不符', 'O': '結果不符', 'D': '研究設計不符', 'L': '語言不符'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--topic', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--decisions', default='decisions', help='folder under WORK (decisions_final after adjudication)')
    a = ap.parse_args()
    W = lambda *p: os.path.join(a.work, *p)
    recs = {r['uid']: r for r in json.load(open(W('records_%s.json' % a.topic), encoding='utf8'))}
    dec = {}
    for f in sorted(glob.glob(W(a.decisions, '%s_*.json' % a.topic))):
        for d in json.load(open(f, encoding='utf8')):
            dec[d['uid']] = d
    missing = set(recs) - set(dec)
    extra = set(dec) - set(recs)
    if missing or extra:
        sys.exit('decision files do not match records: missing %d, extra %d' % (len(missing), len(extra)))
    ft_uids = [u for u, d in dec.items() if d['decision'] == 'FT']

    spec = json.load(open(W('ft_%s.json' % a.topic), encoding='utf8')) if os.path.exists(W('ft_%s.json' % a.topic)) else None
    assigned = {}
    if spec:
        for u in spec.get('include', []):
            assigned[u] = 'include'
        for u in spec.get('not_retrieved', {}):
            assigned[u] = 'not_retrieved'
        for cat, uids in spec.get('exclude', {}).items():
            for u in uids:
                if u in assigned:
                    sys.exit('uid assigned twice: ' + u)
                assigned[u] = cat
        miss, ext = set(ft_uids) - set(assigned), set(assigned) - set(ft_uids)
        if miss or ext:
            sys.exit('ft spec mismatch — not decided: %s; not FT: %s' % (sorted(miss), sorted(ext)))
    notes = (spec or {}).get('notes', {})
    basis = (spec or {}).get('basis', {})   # uid -> 'fulltext' | 'abstract' (what the full-text decision rested on)
    cats = (spec or {}).get('categories', {})

    screen = {}
    for u, d in dec.items():
        s = {'ta': d['decision'], 'ta_reason': d.get('reason', ''), 'ta_note': d.get('note', ''),
             'ft': None, 'ft_cat': '', 'ft_code': '', 'ft_reason': ''}
        k = assigned.get(u)
        if k == 'include':
            s['ft'], s['ft_reason'] = 'include', '符合納入條件，納入評讀'
        elif k == 'not_retrieved':
            s['ft'], s['ft_reason'] = 'not_retrieved', spec['not_retrieved'][u]
        elif k:
            s['ft'], s['ft_cat'], s['ft_code'] = 'exclude', k, cats[k]['short']
            s['ft_reason'] = cats[k]['label'] + ('（%s）' % notes[u] if u in notes else '')
        if k:
            s['ft_basis'] = basis.get(u, 'fulltext')
        screen[u] = s
    json.dump(screen, open(W('screen_%s.json' % a.topic), 'w', encoding='utf8'), ensure_ascii=False, indent=0)

    ta_ex = Counter(TA[d['decision']] for d in dec.values() if d['decision'] != 'FT')
    ft_ex = Counter(cats[assigned[u]]['short'] for u in assigned if assigned[u] not in ('include', 'not_retrieved'))
    dd = json.load(open(W('dedup_%s.json' % a.topic), encoding='utf8')) if os.path.exists(W('dedup_%s.json' % a.topic)) else {}
    counts = {
        'per_database': dd.get('per_database', {}), 'total': dd.get('total'), 'duplicates': dd.get('duplicates'),
        'screened': len(recs), 'ta_excluded': sum(ta_ex.values()), 'ta_reasons': ta_ex.most_common(),
        'sought': len(ft_uids), 'not_retrieved': [[u, (recs[u]['authors'][0].split(',')[0] if recs[u]['authors'] else ''), recs[u]['year'], recs[u]['title'][:80], spec['not_retrieved'][u]] for u in (spec or {}).get('not_retrieved', {})],
        'assessed': len(ft_uids) - len((spec or {}).get('not_retrieved', {})),
        'ft_excluded': sum(ft_ex.values()), 'ft_reasons': ft_ex.most_common(),
        'ft_basis_abstract_only': sorted(u for u in assigned if basis.get(u) == 'abstract'),
        'included': [[u, (recs[u]['authors'][0].split(',')[0] if recs[u]['authors'] else ''), recs[u]['year'], recs[u]['title'][:80]] for u in (spec or {}).get('include', [])],
    }
    json.dump(counts, open(W('counts_%s.json' % a.topic), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(json.dumps(counts, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
