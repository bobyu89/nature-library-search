# 華藝線上圖書館 Airiti Library

## Search
Type the Boolean query into the home-page search box and press Enter (do not click the cookie banner).
The results URL is `/Article/Query?queryString=<JSON>`; the count is in the page text `118 個查詢結果`.
Page links contain the full JSON template (`DSF.SearchFileds[0].SearchKeyWord`, `DSF.PageSize`, `DSF.Page`).
Save one page-2 link's decoded JSON as a template (`localStorage`), then navigate back to the home page so the
tab title stays short (the long URL is echoed into every tool result).

Year fields in the JSON (`IssueSYear/IssueEYear`) are ignored — collect everything and filter `PY` after export.

## Collect all document IDs
Fetch `/Article/Query?queryString=` + JSON with `PageSize=50`, `Page=1..n`, parse with `DOMParser`, and read
`.searchResultGroup[key]` (docID such as `P20141022001-N202509240018-00008`). Pace requests (~0.7 s).
Long loops exceed the 45 s tool timeout: start them as a detached async function writing into `window._…`
and poll.

## Export RIS (with abstracts) — `templates/js/airiti_export.js`
1. POST `/Article/CiteWindow` with form field `jsString = encodeURIComponent(JSON.stringify(docIDs))`
   (50 per batch). The returned HTML contains `var jsString = '…'` and
   `ajaxRequestVerificationToken_CiteWindow = '…'`.
2. POST `/Article/CiteExport` with `jsString=<that value>&type=RIS` and header
   `AjaxRequestVerificationToken: <token>` → JSON; RIS text is in `ReturnData.Content`.

Fields: `T1 AU JO VL IS PY SP EP AB KW LA PB UR(Article/Detail?docID=…)`. Chinese author strings look like
`楊佳容(Chia-Jung Yang)`; `dedup.py` strips the English part for display.
