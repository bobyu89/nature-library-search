# Reporting standards and the TWNA rubric

## Structured search log → PRISMA-S appendix
Keep `<work>/searches_<topic>.json` in the shape of `templates/searches.example.json` while you search (every line,
hits, limits, filters, platform, access route, search and export dates, notes on differences). Then
```bash
python -I scripts/prisma_s.py --log <work>/searches_<topic>.json --out <work>/PRISMA-S_<topic>.md [--docx ...]
```
gives the full-strategy appendix and a PRISMA-S 16-item status table (✗ = something reviewers will ask for:
usually item 14 peer review of the strategy, item 12 updates, item 11 prior work).

PRISMA-S items in one line each: 1 database names · 2 platforms · 3 trial registries · 4 websites/browsing ·
5 citation searching · 6 contacting authors/experts · 7 other methods · 8 full strategies for all sources ·
9 limits · 10 validated filters with citation · 11 prior work reused · 12 update searches · 13 dates ·
14 peer review (PRESS) · 15 total records per source · 16 deduplication method.

## TWNA A類 rubric — 4-2 文獻搜尋的方法與分析（20 分；1141020 修訂版）
Self-check before handing the draft over:
| 項目 | 配分 | 檢查 |
|---|---|---|
| 4-2-1 關鍵字使用合適 | 5 | 關鍵字與 PICO 一致、完整；列出 MeSH／Emtree／CINAHL Headings 與自然語言（PICO 表的五欄：PICO、中文、英文、同義字、MeSH） |
| 4-2-2 清楚敘述檢索策略及利用檢索功能 | 8 | 逐資料庫的完整檢索式與筆數；布林運算元、截字、限制與篩選的理由；**必須包含 Cochrane 與 PubMed**，護理主題加 CINAHL，並有本土資料庫（華藝等）；**註明檢索日期** |
| 4-2-3 清楚描述挑選文獻的理由 | 7 | 納入／排除標準與理由（表格）；**PRISMA 流程圖**；選文符合回答問題的最佳研究設計（治療型 → SR／RCT）與 PICO |

Other rubric facts that affect this stage:
- 刊登頁數：內文至多 16 頁（B 類 20 頁），**自前言開始，含圖表及所有附件**。The full-text exclusion appendix and a
  PRISMA-S appendix count toward the limit — keep them compact (12 pt table, short reasons) or agree with the
  editor/teacher to supply them as supplementary files; tell the user which choice was made.
- Abstract 2.2 must state inclusion/exclusion criteria and database sources.
- A類 appraises 2–3 papers (1 SR + 1–2 RCT); the screening should still be complete — the selection logic for the
  final 2–3 must be stated (best design, most direct PICO match, most recent / most complete).

## GRADE / Summary of Findings hand-off
When screening ends, fill `templates/sof_template.md` with what the counts and extraction already know (outcome,
studies, participants, effect, certainty placeholders) and hand it to `twna-ebhc-report` for the appraisal and
conclusion sections. Certainty ratings are the author's judgement — leave them marked for review.

## Scoping reviews and theses
For scoping reviews use PRISMA-ScR (no risk-of-bias requirement; charting instead of appraisal) — hand off to
`scoping-review-master`. For theses, the same pipeline applies; the appendix limits usually do not, so include the
full PRISMA-S appendix and the exclusion list.
