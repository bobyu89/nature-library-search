"""BibTeX per PRISMA stage (each record in exactly one file). keywords → Zotero tags, note/annote → notes.

usage: python -I to_bib.py --topic sema --label semaglutide --work WORK --out DIR
writes DIR/<label>_1_標題摘要排除.bib, _2_全文排除.bib, _3_無法取得全文.bib, _4_納入評讀.bib (empty stages skipped)
"""
import argparse, json, os, re, sys

TA = {'P': '族群不符', 'I': '介入不符', 'O': '結果不符', 'D': '研究設計不符', 'L': '語言不符'}
STAGES = [('1_標題摘要排除', lambda s: s['ta'] != 'FT'),
          ('2_全文排除', lambda s: s['ft'] == 'exclude'),
          ('3_無法取得全文', lambda s: s['ft'] == 'not_retrieved'),
          ('4_納入評讀', lambda s: s['ft'] == 'include')]


def esc(t):
    t = (t or '').replace('\\', '/')
    t = re.sub(r'([&%$#_])', r'\\\1', t)
    return t.replace('{', '\\{').replace('}', '\\}')


def author(n):
    n = n.strip()
    if re.search(r'[一-鿿]', n):
        return '{' + esc(re.sub(r'\(.*?\)', '', n).strip()) + '}'
    return esc(n)


def entry(r, s):
    tags = ['來源:' + d for d in r['sources']]
    if s['ta'] == 'FT':
        tags.append('篩選1_標題摘要:進入全文')
        tags.append({'include': '篩選2_全文:納入評讀', 'not_retrieved': '篩選2_全文:無法取得全文'}.get(s['ft'], '篩選2_全文:排除-' + s.get('ft_code', '')))
    else:
        tags.append('篩選1_標題摘要:排除-' + TA[s['ta']])
    note = 'PRISMA ID: %s；資料庫: %s。標題摘要初篩：%s — %s。' % (
        r['uid'], ', '.join(r['sources']), '進入全文' if s['ta'] == 'FT' else '排除（%s）' % TA[s['ta']], s['ta_reason'])
    if s['ft']:
        note += '全文評估：%s — %s。' % ({'include': '納入評讀', 'exclude': '排除', 'not_retrieved': '無法取得全文'}[s['ft']], s['ft_reason'])
    note += '（AI 初篩，請作者複核）'
    reg = 'registry' in (r['type'] or '').lower() or (r.get('accession') or '').startswith('NCT')
    f = [('title', esc(r['title'] or '(無標題)'))]
    if r['authors']:
        f.append(('author', ' and '.join(author(x) for x in r['authors'] if x.strip())))
    if r['year']:
        f.append(('year', str(r['year'])))
    if r['journal'] and not reg:
        f.append(('journal', esc(r['journal'])))
    if r.get('volume'):
        f.append(('volume', esc(r['volume'])))
    if r.get('issue'):
        f.append(('number', esc(r['issue'])))
    if r.get('pages'):
        f.append(('pages', esc(r['pages'].replace('-', '--'))))
    if r['doi']:
        f.append(('doi', esc(r['doi'])))
    if r.get('url'):
        f.append(('url', r['url'].replace('%', '\\%')))
    if r['abstract']:
        f.append(('abstract', esc(r['abstract'])))
    if r.get('lang'):
        f.append(('language', esc(r['lang'])))
    f.append(('keywords', esc('; '.join(tags))))
    f.append(('note', esc(' | '.join(['PRISMA ID: ' + r['uid']] + (['PMID: ' + r['pmid']] if r['pmid'] else [])))))
    f.append(('annote', esc(note)))
    return '@%s{%s,\n%s\n}\n' % ('misc' if reg else 'article', r['uid'], ',\n'.join('  %s = {%s}' % kv for kv in f))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--topic', required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    recs = json.load(open(os.path.join(a.work, 'records_%s.json' % a.topic), encoding='utf8'))
    scr = json.load(open(os.path.join(a.work, 'screen_%s.json' % a.topic), encoding='utf8'))
    os.makedirs(a.out, exist_ok=True)
    total = 0
    for stage, pick in STAGES:
        sel = [r for r in recs if pick(scr[r['uid']])]
        if not sel:
            continue
        path = os.path.join(a.out, '%s_%s.bib' % (a.label, stage))
        open(path, 'w', encoding='utf8').write('\n'.join(entry(r, scr[r['uid']]) for r in sel))
        total += len(sel)
        print(path, len(sel))
    print('total', total, 'of', len(recs))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
