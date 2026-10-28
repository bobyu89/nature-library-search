"""ClinicalTrials.gov (API v2) search for ongoing/completed trials → JSON + RIS (registry records).

usage: python -I ctgov.py --cond "obesity" --intr "semaglutide" --term "cardiovascular" --out WORK/raw/ctgov_sema
writes <out>.json (slim study list) and <out>.ris (TY RPRT records, AN NCT id) for dedup.py (--input CTgov=<out>.ris)

Use it as a grey-literature / ongoing-trial check (e.g. finding SURMOUNT-MMO). WHO ICTRP has no stable public API:
search https://trialsearch.who.int in the browser and record counts manually.
"""
import argparse, json, sys, urllib.parse, urllib.request

API = 'https://clinicaltrials.gov/api/v2/studies'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cond', default='')
    ap.add_argument('--intr', default='')
    ap.add_argument('--term', default='')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    params = {'pageSize': 100, 'format': 'json'}
    if a.cond:
        params['query.cond'] = a.cond
    if a.intr:
        params['query.intr'] = a.intr
    if a.term:
        params['query.term'] = a.term
    studies, token = [], None
    while True:
        p = dict(params, **({'pageToken': token} if token else {}))
        d = json.loads(urllib.request.urlopen(API + '?' + urllib.parse.urlencode(p), timeout=60).read())
        studies += d.get('studies', [])
        token = d.get('nextPageToken')
        if not token:
            break
    slim, ris = [], []
    for s in studies:
        ps = s.get('protocolSection', {})
        idm, st, ds = ps.get('identificationModule', {}), ps.get('statusModule', {}), ps.get('descriptionModule', {})
        rec = {'nct': idm.get('nctId'), 'title': idm.get('officialTitle') or idm.get('briefTitle'), 'status': st.get('overallStatus'),
               'start': (st.get('startDateStruct') or {}).get('date'), 'completion': (st.get('primaryCompletionDateStruct') or {}).get('date'),
               'sponsor': ps.get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('name'),
               'summary': ds.get('briefSummary', '')}
        slim.append(rec)
        ris.append('\n'.join(['TY  - RPRT', 'AN  - ' + rec['nct'], 'TI  - ' + (rec['title'] or ''), 'PY  - ' + (rec['start'] or '')[:4],
                              'AB  - ' + rec['summary'].replace('\n', ' '), 'M3  - Clinical trial registry record',
                              'UR  - https://clinicaltrials.gov/study/' + rec['nct'], 'DB  - ClinicalTrials.gov', 'ER  - ']))
    json.dump(slim, open(a.out + '.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    open(a.out + '.ris', 'w', encoding='utf8').write('\n\n'.join(ris) + '\n')
    print('studies', len(slim), '→', a.out + '.json/.ris')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
