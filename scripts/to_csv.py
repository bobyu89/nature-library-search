"""Per-record screening log (UTF-8 with BOM so Excel opens Chinese correctly).

usage: python -I to_csv.py --topic sema --label semaglutide --work WORK --out DIR
"""
import argparse, csv, json, os, sys

TA = {'FT': '進入全文', 'P': '排除-族群不符', 'I': '排除-介入不符', 'O': '排除-結果不符', 'D': '排除-研究設計不符', 'L': '排除-語言不符'}
FT = {'include': '納入評讀', 'exclude': '排除', 'not_retrieved': '無法取得全文', None: ''}


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
    path = os.path.join(a.out, '%s_篩選紀錄.csv' % a.label)
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['PRISMA ID', '第一作者', '年', '篇名', '期刊', 'DOI', 'PMID', '來源資料庫', '標題摘要篩選',
                    '初篩理由（AI）', '全文評估', '全文理由', '作者複核（請填）'])
        for r in recs:
            s = scr[r['uid']]
            ftr = (s['ft_code'] + '：' + s['ft_reason']) if s['ft'] == 'exclude' else s['ft_reason']
            w.writerow([r['uid'], r['authors'][0] if r['authors'] else '', r['year'] or '', r['title'], r['journal'],
                        r['doi'], r['pmid'], '; '.join(r['sources']), TA[s['ta']], s['ta_reason'], FT[s['ft']], ftr, ''])
    print(path, len(recs))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
