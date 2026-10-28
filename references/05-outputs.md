# Outputs

## PRISMA 2020 flow diagram
The script follows the official template (Page et al., 2021, BMJ 372:n71, Figure 1) box for box:

| Template box | Our wording |
|---|---|
| header: Identification of studies via databases and registers | 經由資料庫與登錄系統辨識研究 |
| Records identified from: Databases (n) / Registers (n) — per-database counts recommended | 檢索所得之紀錄：資料庫（n）＋各資料庫（n）＋登錄系統（n） |
| Records removed before screening: duplicates / marked ineligible by automation tools / other reasons | 篩選前移除之紀錄：重複紀錄／經自動化工具標記為不符資格／其他原因移除 |
| Records screened → Records excluded** | 篩選之紀錄 → 排除之紀錄 |
| Reports sought for retrieval → Reports not retrieved | 尋求全文之報告 → 無法取得之報告 |
| Reports assessed for eligibility → Reports excluded: Reason 1 (n) … | 評估資格之報告 → 排除之報告：各理由（n） |
| Studies included in review / Reports of included studies | 納入回顧之研究（n）／納入研究之報告（n） |
| v2 grey column: Identification of studies via other methods | 經由其他方法辨識研究（`--other other.json`） |

```bash
python -I scripts/prisma_diagram.py --counts <work>/counts_<topic>.json --labels labels_<topic>.json --out PRISMA_<topic>.png
# labels_<topic>.json (UTF-8 file — safer than CLI args for Chinese on Windows):
# {"db": {"Cochrane": "Cochrane Library|Reviews 4、CENTRAL 153"},
#  "reasons": {"預印本": "未經同儕審查之預印本", "SELECT次要分析": "SELECT 試驗之次要分析"}}
```
Keep out of the figure anything the template does not have (sensitivity searches, dates, study names, title/abstract
reasons) — put them in the text or the caption. Options when needed: `--other` (v2 column for citation chasing /
websites), `--studies` (when several reports belong to one study), `--registers`, `--ta-reasons`, `--automation N`
(the template's footnote **: human vs automation-tool exclusions — required once AI exclusions are final).

Insert the PNG at **≥ 400 pt wide** (about 14 cm, the A4 text width with TWNA margins). At 270–300 pt the 11-pt
figure text prints at ~4 pt and is unreadable. Check the page count afterwards (it can add a page).

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
