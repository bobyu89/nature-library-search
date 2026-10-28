# Outputs

## PRISMA 2020 flow diagram
```bash
python -I scripts/prisma_diagram.py --counts <work>/counts_<topic>.json --out PRISMA_<topic>.png \
  --included "RCT 1 篇：Lincoff et al. (2023) SELECT" --included "SR/MA 2 篇：Bracchiglione et al. (2025)；Yin et al. (2025)" \
  --db-label "Cochrane=Cochrane Library（Reviews 4、CENTRAL 153）" \
  --header "敏感度檢查：Scopus 補充檢索（n = 272），未發現新增符合條件之文獻" \
  --footer "檢索日期：2026-10-14；書目匯出：2026-10-20"
```
Boxes: identification by database (with Cochrane Reviews/CENTRAL split), duplicates removed, screened,
excluded with reasons, sought, not retrieved (named), assessed, excluded with reasons, included (named).
Insert at ~360–400 px wide in a 16-page-limited manuscript.

## Methods paragraph (fill from counts JSON)
「五個資料庫共檢得 {total} 筆，以 Zotero 管理書目，依 DOI、PubMed 編號（PMID）及篇名比對去除重複 {dup} 筆，餘
{screened} 筆進行標題與摘要篩選，排除 {ta_excluded} 筆（{ta reasons with counts}）。全文評估 {assessed} 篇，
排除 {ft_excluded} 篇，理由為：{ft reasons with counts}，各篇排除理由見附表一。篩選流程依 PRISMA 2020 繪製如圖一
（Page et al., 2021），最後納入 {included description}（共 {n} 篇）進行評讀。」
Also update the search table: per-database counts, total, and "（檢索日期：…；書目匯出：…）" plus a note on any
database that could not be pinned to the search date.

## Other exports for co-screeners
`scripts/export_formats.py --format ris|rayyan|covidence` — one combined RIS with screening tags for EndNote/Mendeley,
or a blind Rayyan CSV / Covidence RIS (no decisions) so a teacher or classmate can screen independently.

## Full-text exclusion appendix (附表一)
TWNA counts appendices toward the page limit (A類 16 pages "自前言開始，含圖表及所有附件"). Decide with the user
whether the appendix goes inside the manuscript (compact) or is supplied separately with the teacher's/editor's
agreement, and say which in the text.
Columns: #, 作者（年）, 篇名／期刊, 排除理由 (short label + specific note). Put category definitions in a note
under the table and an "AI 協助判讀，作者須逐篇複核" note. Keep it as a separate file when the main text is near a
page limit (45 rows ≈ 6 A4 pages at 12 pt). A docx builder is easy with the `docx` skill / docx-js; sort rows by
category size, then year.

## Per-record log
`python -I scripts/to_csv.py --topic sema --label semaglutide --work <work> --out <dir>` → UTF-8-BOM CSV for
Excel with the AI reason and an empty "作者複核" column.

## Deliverables checklist (copy to the user's folder)
raw exports, `search_log.md`, records/screen/counts JSON, CSV log, PRISMA PNG, appendix, BibTeX per stage.
