"""PRISMA 2020 flow diagram (databases only) from counts_<topic>.json.

usage: python -I prisma_diagram.py --counts WORK/counts_sema.json --out PRISMA.png \
         --included "RCT 1 篇：Lincoff et al. (2023)" --included "SR/MA 2 篇：…" \
         [--db-label "Cochrane=Cochrane Library（Reviews 4、CENTRAL 153）"] [--header "..."] [--footer "..."]
Labels default to the database names; reasons are listed largest first. Requires matplotlib.
"""
import argparse, json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from matplotlib import font_manager
_have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams['font.family'] = [f for f in ('Microsoft JhengHei', 'DFKai-SB', 'Noto Sans CJK TC', 'PingFang TC', 'Heiti TC')
                               if f in _have] + ['sans-serif']
DB_NAMES = {'CINAHL': 'CINAHL Complete', 'Airiti': '華藝線上圖書館', 'Cochrane': 'Cochrane Library'}


def box(ax, x, y, w, h, text, fc='white', fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0', fc=fc, ec='black', lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs)


def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', lw=1, color='black'))


def fmt(n):
    return '{:,}'.format(n) if isinstance(n, int) else str(n)


def wrap(s, width=22):
    out, line = [], ''
    for ch in s:
        line += ch
        if len(line) >= width and ch in '，、；）) ':
            out.append(line)
            line = ''
    return '\n'.join(out + [line] if line else out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--counts', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--included', action='append', default=[])
    ap.add_argument('--db-label', action='append', default=[])
    ap.add_argument('--header', default='')
    ap.add_argument('--footer', default='')
    a = ap.parse_args()
    c = json.load(open(a.counts, encoding='utf8'))
    labels = dict(x.split('=', 1) for x in a.db_label)
    dbs = '\n'.join('%s（n = %s）' % (labels.get(k, DB_NAMES.get(k, k)), fmt(v)) for k, v in c['per_database'].items())
    ta = '\n'.join('%s %s' % (k, fmt(v)) for k, v in c['ta_reasons'])
    ft = '\n'.join(wrap('%s %s' % (k, fmt(v))) for k, v in c['ft_reasons'])
    nr = '\n'.join('%s (%s)' % (x[1], x[2]) for x in c['not_retrieved'])
    inc = '\n'.join(a.included) or '\n'.join('%s (%s)' % (x[1], x[2]) for x in c['included'])

    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 100); ax.set_ylim(0, 120); ax.axis('off')
    if a.header:
        ax.text(50, 116, a.header, ha='center', fontsize=8.5)
    for y, h, lab in [(88, 22, '辨\n識'), (36, 50, '篩\n選'), (4, 30, '納\n入')]:
        box(ax, 0, y, 7, h, lab, fc='#BDD7EE', fs=11)
    L, W, R, RW = 10, 42, 58, 40
    box(ax, L, 88, W, 22, '資料庫檢索所得紀錄（n = %s）\n%s' % (fmt(c['total']), dbs), fs=8.5)
    box(ax, R, 92, RW, 16, '篩選前移除之紀錄：\n重複紀錄（n = %s）' % fmt(c['duplicates']))
    arrow(ax, L + W, 100, R, 100)
    box(ax, L, 74, W, 10, '標題與摘要篩選之紀錄\n（n = %s）' % fmt(c['screened']))
    box(ax, R, 70, RW, 18, '排除之紀錄（n = %s）：\n%s' % (fmt(c['ta_excluded']), ta), fs=8)
    arrow(ax, L + W / 2, 88, L + W / 2, 84); arrow(ax, L + W, 79, R, 79)
    box(ax, L, 58, W, 10, '尋求全文之報告（n = %s）' % fmt(c['sought']))
    box(ax, R, 58, RW, 10, '無法取得全文之報告（n = %d）%s' % (len(c['not_retrieved']), ('\n' + nr) if nr else ''), fs=8.5)
    arrow(ax, L + W / 2, 74, L + W / 2, 68); arrow(ax, L + W, 63, R, 63)
    box(ax, L, 38, W, 14, '全文評估資格之報告（n = %s）' % fmt(c['assessed']))
    box(ax, R, 30, RW, 24, '排除之報告（n = %s）：\n%s' % (fmt(c['ft_excluded']), ft), fs=8.5)
    arrow(ax, L + W / 2, 58, L + W / 2, 52); arrow(ax, L + W, 45, R, 45)
    box(ax, L, 8, W, 22, '納入評讀之研究（n = %d）\n%s' % (len(c['included']), inc), fc='#E2EFDA', fs=8.5)
    arrow(ax, L + W / 2, 38, L + W / 2, 30)
    if a.footer:
        ax.text(50, 1, a.footer, ha='center', fontsize=8)
    fig.savefig(a.out, dpi=200, bbox_inches='tight')
    print('saved', a.out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
