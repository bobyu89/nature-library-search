"""PRISMA 2020 flow diagram following the official template (Page et al., 2021, BMJ 372:n71, Figure 1).

usage:
  python -I prisma_diagram.py --counts WORK/counts_sema.json --out PRISMA.png \
      [--labels labels.json] [--registers 0] [--studies 3]
      [--other other.json] [--ta-reasons] [--automation N] [--source]

Layout = template v1 "Identification of studies via databases and registers"; with --other it becomes v2 and adds the
grey "Identification of studies via other methods" column. Boxes and wording (Traditional Chinese):
  辨識：檢索所得之紀錄（資料庫 n、各資料庫 n、登錄系統 n）→ 篩選前移除之紀錄（重複／經自動化工具標記為不符資格／其他原因）
  篩選：篩選之紀錄 → 排除之紀錄；尋求全文之報告 → 無法取得之報告；評估資格之報告 → 排除之報告（各理由 n）
  納入：納入回顧之研究 n；納入研究之報告 n
--ta-reasons  also list title/abstract exclusion reasons (not in the template; off by default).
--automation  N records excluded by automation tools at screening: prints the template's human/automation split
              (PRISMA 2020 footnote **). Off by default.
other.json: {"sources": [["引文追蹤", 88]], "sought": 3, "not_retrieved": 0, "assessed": 3, "excluded": [["族群不符", 3]]}
"""
import argparse, json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

_have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams['font.family'] = [f for f in ('Microsoft JhengHei', 'DFKai-SB', 'Noto Sans CJK TC', 'PingFang TC', 'Heiti TC')
                               if f in _have] + ['sans-serif']
DB_NAMES = {'CINAHL': 'CINAHL Complete', 'Airiti': '華藝線上圖書館', 'Cochrane': 'Cochrane Library'}
STAGE_FC, HEAD_FC, INC_FC, GREY_FC, GREY_HEAD = '#BDD7EE', '#FFE699', 'white', '#F2F2F2', '#D9D9D9'


def fmt(n):
    return '{:,}'.format(n) if isinstance(n, int) else str(n)


def box(ax, x, y, w, h, text, fc='white', fs=9, ha='center', bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='square,pad=0', fc=fc, ec='black', lw=0.9))
    tx = x + w / 2 if ha == 'center' else x + 1.2
    ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, linespacing=1.35, fontweight='bold' if bold else 'normal')


def arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='-|>', lw=0.9, color='black', shrinkA=0, shrinkB=0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--counts', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--db-label', action='append', default=[])
    ap.add_argument('--labels', help='JSON {"db": {"Cochrane": "Cochrane Library|Reviews 4、CENTRAL 153"}, "reasons": {"預印本": "未經同儕審查之預印本"}}')
    ap.add_argument('--registers', type=int, default=0, help='records from trial registers (template line "Registers")')
    ap.add_argument('--studies', type=int, help='studies included (default = number of included reports)')
    ap.add_argument('--other', help='JSON for the "other methods" column (template v2)')
    ap.add_argument('--ta-reasons', action='store_true')
    ap.add_argument('--automation', type=int, help='records excluded by automation tools at screening')
    ap.add_argument('--source', action='store_true', help='add the template source line under the figure')
    a = ap.parse_args()
    c = json.load(open(a.counts, encoding='utf8'))
    other = json.load(open(a.other, encoding='utf8')) if a.other else None
    labels = dict(x.split('=', 1) for x in a.db_label)
    rlabels = {}
    if a.labels:   # JSON file is safer than CLI args for Chinese text on Windows shells
        lj = json.load(open(a.labels, encoding='utf8'))
        labels.update(lj.get('db', {}))
        rlabels.update(lj.get('reasons', {}))
    reports = len(c['included'])
    studies = a.studies if a.studies is not None else reports
    n_db = sum(c['per_database'].values())

    # geometry: x in [0, 100]; v1 → stage | main | right; v2 adds other-methods columns on the right
    if other:
        W, GAP = 20, 3
        X = {'stage': 0, 'main': 6, 'right': 6 + W + GAP, 'omain': 6 + 2 * (W + GAP) + 2, 'oright': 6 + 3 * (W + GAP) + 2}
        fs, small = 7.5, 7
    else:
        W, GAP = 41, 6
        X = {'stage': 0, 'main': 7, 'right': 7 + W + GAP}
        fs, small = 11, 10.5   # readable when the figure is printed ~14 cm wide (insert at ≥ 400 pt in A4 manuscripts)
    SW = 5 if other else 6
    fig, ax = plt.subplots(figsize=(13 if other else 10, 12))
    ax.set_xlim(0, 100); ax.set_ylim(0, 104); ax.axis('off')

    # header bars
    box(ax, X['main'], 97, 2 * W + GAP, 5, '經由資料庫與登錄系統辨識研究', fc=HEAD_FC, fs=fs + 1, bold=True)
    if other:
        box(ax, X['omain'], 97, 2 * W + GAP, 5, '經由其他方法辨識研究', fc=GREY_HEAD, fs=fs + 1, bold=True)
    # stage labels
    for y, h, lab in [(74, 21, '辨\n識'), (28, 44, '篩\n選'), (6, 20, '納\n入')]:
        box(ax, X['stage'], y, SW, h, lab, fc=STAGE_FC, fs=fs + 2, bold=True)

    L, R = X['main'], X['right']
    # identification
    def dbline(k, v):
        name, _, detail = labels.get(k, DB_NAMES.get(k, k)).partition('|')   # "Cochrane Library|Reviews 4、CENTRAL 153"
        return '　%s（n = %s）' % (name, fmt(v)) + ('\n　　%s' % detail if detail else '')
    dbs = '\n'.join(dbline(k, v) for k, v in c['per_database'].items())
    box(ax, L, 74, W, 21, '檢索所得之紀錄：\n資料庫（n = %s）\n%s\n登錄系統（n = %s）' % (fmt(n_db), dbs, fmt(a.registers)), fs=small)
    box(ax, R, 77, W, 15, '篩選前移除之紀錄：\n重複紀錄（n = %s）\n經自動化工具標記為不符資格（n = 0）\n其他原因移除（n = 0）' % fmt(c['duplicates']), fs=small)
    arrow(ax, L + W, 84.5, R, 84.5)
    # screening
    ex_text = '排除之紀錄（n = %s）' % fmt(c['ta_excluded'])
    if a.automation is not None:
        ex_text += '\n由人工排除（n = %s）\n由自動化工具排除（n = %s）' % (fmt(c['ta_excluded'] - a.automation), fmt(a.automation))
    if a.ta_reasons:
        ex_text += '\n' + '\n'.join('%s（n = %s）' % (k, fmt(v)) for k, v in c['ta_reasons'])
    box(ax, L, 62, W, 8, '篩選之紀錄\n（n = %s）' % fmt(c['screened']), fs=fs)
    box(ax, R, 60 if (a.ta_reasons or a.automation is not None) else 62, W, 12 if (a.ta_reasons or a.automation is not None) else 8, ex_text, fs=small)
    arrow(ax, L + W / 2, 74, L + W / 2, 70); arrow(ax, L + W, 66, R, 66)
    box(ax, L, 48, W, 8, '尋求全文之報告\n（n = %s）' % fmt(c['sought']), fs=fs)
    box(ax, R, 48, W, 8, '無法取得之報告\n（n = %s）' % fmt(len(c['not_retrieved'])), fs=fs)
    arrow(ax, L + W / 2, 62, L + W / 2, 56); arrow(ax, L + W, 52, R, 52)
    reasons = '\n'.join('%s（n = %s）' % (rlabels.get(k, k), fmt(v)) for k, v in c['ft_reasons'])
    box(ax, L, 34, W, 8, '評估資格之報告\n（n = %s）' % fmt(c['assessed']), fs=fs)
    nlines = len(c['ft_reasons']) + 1
    eh = max(10, 2.6 * nlines + 3)
    box(ax, R, 38 - eh / 2, W, eh, '排除之報告（n = %s）：\n%s' % (fmt(c['ft_excluded']), reasons), fs=small)
    arrow(ax, L + W / 2, 48, L + W / 2, 42); arrow(ax, L + W, 38, R, 38)
    # included
    box(ax, L, 9, W, 12, '納入回顧之研究（n = %s）\n納入研究之報告（n = %s）' % (fmt(studies), fmt(reports)), fc=INC_FC, fs=fs)
    arrow(ax, L + W / 2, 34, L + W / 2, 21)

    if other:
        OL, OR = X['omain'], X['oright']
        src = '\n'.join('　%s（n = %s）' % (k, fmt(v)) for k, v in other['sources'])
        box(ax, OL, 74, W, 21, '經由其他方法辨識之紀錄：\n%s' % src, fc=GREY_FC, fs=small)
        box(ax, OL, 48, W, 8, '尋求全文之報告\n（n = %s）' % fmt(other['sought']), fc=GREY_FC, fs=fs)
        box(ax, OR, 48, W, 8, '無法取得之報告\n（n = %s）' % fmt(other['not_retrieved']), fc=GREY_FC, fs=fs)
        box(ax, OL, 34, W, 8, '評估資格之報告\n（n = %s）' % fmt(other['assessed']), fc=GREY_FC, fs=fs)
        orr = '\n'.join('%s（n = %s）' % (k, fmt(v)) for k, v in other.get('excluded', []))
        box(ax, OR, 31, W, 14, '排除之報告（n = %s）：\n%s' % (fmt(sum(v for _, v in other.get('excluded', []))), orr), fc=GREY_FC, fs=small)
        arrow(ax, OL + W / 2, 74, OL + W / 2, 56); arrow(ax, OL + W, 52, OR, 52)
        arrow(ax, OL + W / 2, 48, OL + W / 2, 42); arrow(ax, OL + W, 38, OR, 38)
        # elbow into the included box
        ax.plot([OL + W / 2, OL + W / 2], [34, 15], color='black', lw=0.9)
        arrow(ax, OL + W / 2, 15, L + W, 15)
    if a.source:
        ax.text(L, 1.5, '資料來源：Page, M. J., et al. (2021). The PRISMA 2020 statement. BMJ, 372, n71.', fontsize=7, ha='left')
    fig.savefig(a.out, dpi=200, bbox_inches='tight')
    print('saved', a.out, '(template v2)' if other else '(template v1)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
