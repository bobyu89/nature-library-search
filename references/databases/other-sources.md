# Other sources (verify on first use)

The recipes in this file follow the same patterns as the verified databases but have **not yet been run end to
end** in this skill. On first use, confirm each step, then move the database into its own verified file and note
the date in CHANGELOG.md.

## Web of Science Core Collection (Clarivate)
- Advanced search: `TS=(semaglutide OR wegovy) AND TS=(obes* OR overweight) AND TS=(cardiovascular OR MACE)`;
  `PY=(2015-2026)`; document types via refine panel.
- Export: "Export → RIS (other reference software)" or "Plain text file", **≤ 1,000 records per export** without a
  personal login; choose "Full record" for abstracts. If the download cannot be saved from the built-in browser,
  look in the network panel for the export request (`/api/wosnx/indic/export/saveToFile`) and replay it with
  `fetch` inside the page, then dump in chunks (`03-browser-data-out.md`).

## APA PsycInfo, MEDLINE (EBSCO) and other EBSCO databases
Same interface as CINAHL — reuse `templates/js/cinahl_search.js` and change the database code in `filters`
(`ccm` CINAHL Complete; PsycInfo is usually `psyh`; MEDLINE `cmedm`). Read the actual code from the results URL
(`db=` parameter) after opening the database from the library portal. Headings differ (PsycInfo uses `DE "..."`).

## 臺灣博碩士論文知識加值系統（NDLTD, ndltd.ncl.edu.tw）
Session-based site with frequent captchas — the user may need to pass them. Search with 進階查詢 (論文名稱／摘要
／關鍵詞), record counts, and use the 書目匯出 function per page (EndNote/RIS) or record theses by hand.
Theses are usually excluded by design in A類 reports but count as local grey literature in theses and reviews.

## 華藝 thesis and CEPS content
Airiti Library already covers CEPS journals and 華藝 theses (資料類型 facets); the main Airiti recipe applies.

## 中國知網 CNKI／萬方
Through the `nature-downloader` skill's CNKI institutional route (user-authorised Chrome session). Export
"NoteExpress/EndNote/RefWorks" from the result list in batches of ≤ 500.

## Google Scholar (grey literature only)
Not reproducible and capped at 1,000 results; use for grey literature and seed discovery only. Record the
query, date and the number screened (e.g. first 200 by relevance). Do not scrape automatically — scan pages
in the browser and note relevant items by hand.

## Study registries
See `07-validation-and-supplementary.md` (ClinicalTrials.gov API script; WHO ICTRP by hand).
