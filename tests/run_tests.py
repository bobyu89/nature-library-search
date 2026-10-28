"""Regression tests for the offline scripts. Run after every change to scripts/.

usage: python -I tests/run_tests.py                 # synthetic fixtures (always)
       python -I tests/run_tests.py --real DIR      # plus the 2026-10 real exports (DIR holds the raw files)

Synthetic fixtures cover: DOI case difference, PMID from Cochrane C3, title match one year apart, title case
difference CINAHL vs Embase, Chinese Airiti record; dual-screener kappa; merge; BibTeX stage files.
The real-data check reproduces the published numbers (1,403 → 1,138; 1,277 → 1,092).
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(os.path.dirname(HERE), 'scripts')
F = os.path.join(HERE, 'fixtures')
PY = [sys.executable, '-I']
fails = []


def run(*args):
    r = subprocess.run(PY + [os.path.join(S, args[0])] + list(args[1:]), capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        fails.append('%s exited %d: %s' % (args[0], r.returncode, r.stderr[-400:]))
    return r.stdout


def expect(name, got, want):
    ok = got == want
    print('%s %-45s got %s%s' % ('PASS' if ok else 'FAIL', name, got, '' if ok else ' want %s' % want))
    if not ok:
        fails.append(name)


def synthetic():
    w = tempfile.mkdtemp()
    run('dedup.py', '--topic', 't', '--prefix', 'T', '--out', w,
        '--input', 'PubMed=' + os.path.join(F, 'pubmed.ris'), '--input', 'Embase=' + os.path.join(F, 'embase.ris'),
        '--input', 'Cochrane=' + os.path.join(F, 'cochrane.ris'), '--input', 'CINAHL=' + os.path.join(F, 'cinahl.json'),
        '--input', 'Airiti=' + os.path.join(F, 'airiti.ris'))
    d = json.load(open(os.path.join(w, 'dedup_t.json'), encoding='utf8'))
    expect('dedup total', d['total'], 9)
    expect('dedup unique', d['unique'], 5)
    recs = json.load(open(os.path.join(w, 'records_t.json'), encoding='utf8'))
    alpha = next(r for r in recs if r['title'].startswith('Alpha'))
    expect('alpha merged from 3 databases', alpha['sources'], ['PubMed', 'Embase', 'Cochrane'])
    gamma = next(r for r in recs if r['title'].lower().startswith('gamma'))
    expect('gamma abstract filled from Embase copy', gamma['abstract'].startswith('Embase abstract gamma'), True)
    expect('uid order (year desc, title)', [r['uid'] for r in recs][:2], ['T0001', 'T0002'])

    for sub, src in (('decisions', 'decisions_A.json'), ('decisions_B', 'decisions_B.json')):
        os.makedirs(os.path.join(w, sub))
        shutil.copy(os.path.join(F, src), os.path.join(w, sub, 't_1.json'))
    out = run('screen_compare.py', '--a', os.path.join(w, 'decisions'), '--b', os.path.join(w, 'decisions_B'), '--topic', 't',
              '--records', os.path.join(w, 'records_t.json'), '--out', os.path.join(w, 'conf.csv'))
    rep = json.loads(out) if out.strip().startswith('{') else {}
    expect('kappa FT vs exclude', rep.get('kappa_FT_vs_exclude'), 0.615)
    expect('conflicts', rep.get('conflicts'), 1)

    spec = {'categories': {'POP': {'label': '族群不符', 'short': '族群不符'}}, 'include': ['T0001', 'T0004'],
            'not_retrieved': {}, 'exclude': {'POP': ['T0003']}, 'basis': {'T0003': 'abstract'}}
    json.dump(spec, open(os.path.join(w, 'ft_t.json'), 'w', encoding='utf8'), ensure_ascii=False)
    run('screen_merge.py', '--topic', 't', '--work', w)
    c = json.load(open(os.path.join(w, 'counts_t.json'), encoding='utf8'))
    expect('counts screened/sought/assessed', (c['screened'], c['sought'], c['assessed']), (5, 3, 3))
    expect('ft excluded + abstract-only basis', (c['ft_excluded'], c['ft_basis_abstract_only']), (1, ['T0003']))
    run('to_bib.py', '--topic', 't', '--label', 'test', '--work', w, '--out', os.path.join(w, 'bib'))
    n = sum(open(os.path.join(w, 'bib', f), encoding='utf8').read().count('\n@') + 1 for f in os.listdir(os.path.join(w, 'bib')))
    expect('bib records across stage files', n, 5)
    run('prisma_diagram.py', '--counts', os.path.join(w, 'counts_t.json'), '--out', os.path.join(w, 'p.png'))
    expect('prisma png written', os.path.exists(os.path.join(w, 'p.png')), True)
    run('export_formats.py', '--topic', 't', '--work', w, '--out', os.path.join(w, 'x'), '--format', 'rayyan')
    expect('rayyan csv written', os.path.exists(os.path.join(w, 'x', 't_rayyan.csv')), True)
    shutil.rmtree(w, ignore_errors=True)


def real(d):
    w = tempfile.mkdtemp()
    x = lambda f: os.path.join(d, f)
    run('dedup.py', '--topic', 'sema', '--prefix', 'S', '--out', w, '--input', 'PubMed=' + x('semaglutide_PubMed檢索結果_195筆.ris'),
        '--input', 'Cochrane=' + x('cochrane_sema_reviews.ris'), '--input', 'Cochrane=' + x('cochrane_sema_central.ris'),
        '--input', 'Embase=' + x('embase_sema_2026.ris'), '--input', 'Embase=' + x('embase_sema_pre2026.ris'),
        '--input', 'CINAHL=' + x('cinahl_sema.json'), '--input', 'Airiti=' + x('airiti_sema.ris'))
    s = json.load(open(os.path.join(w, 'dedup_sema.json'), encoding='utf8'))
    expect('real semaglutide 1,403 → 1,138', (s['total'], s['unique']), (1403, 1138))
    run('dedup.py', '--topic', 'ai', '--prefix', 'A', '--out', w, '--input', 'PubMed=' + x('AI衛教_PubMed檢索結果_167筆.ris'),
        '--input', 'Cochrane=' + x('cochrane_ai_central_all.ris') + '@2018-2026', '--input', 'Embase=' + x('embase_ai_articles.ris'),
        '--input', 'Embase=' + x('embase_ai_ct.ris'), '--input', 'CINAHL=' + x('cinahl_ai.json'), '--input', 'Airiti=' + x('airiti_ai.ris'))
    s = json.load(open(os.path.join(w, 'dedup_ai.json'), encoding='utf8'))
    expect('real AI education 1,277 → 1,092', (s['total'], s['unique']), (1277, 1092))
    shutil.rmtree(w, ignore_errors=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--real')
    a = ap.parse_args()
    synthetic()
    if a.real:
        real(a.real)
    print('\n%s' % ('ALL PASS' if not fails else 'FAILURES:\n  ' + '\n  '.join(fails)))
    sys.exit(1 if fails else 0)
