# Cochrane Library (Reviews + CENTRAL)

## Search
1. Open the config `search_manager` URL (after the user is logged in through the library entry).
2. Type the **whole strategy as one line** in row #1 (find the textbox "Enter a search term here", click it,
   `type`, press Return). One line avoids line-number clashes and is easy to record. Mixing `[mh X]` and
   `:ti,ab,kw` blocks in one line works.
3. Read the hit count from `button.search-manager-result` (the window is narrow, the number is off-screen):
   `Array.from(document.querySelectorAll('button.search-manager-result')).map(b=>b.textContent.trim())`
4. Click that button to open results; the tab links show the split, e.g. `Cochrane Reviews 4`, `Trials 153`.
   Record both.

Notes: phrase truncation must use `NEXT` (`(conversational NEXT agent*)`); the Limits dialog's
"Original publication year" only affects CENTRAL, so it is simpler to export everything and filter `PY`
afterwards (2018–2026 filtering of 239 CENTRAL records gave exactly the 224 shown with the limit).

## Export (all records, RIS with abstracts)
The page's bulk export is a three-step async job. Use `templates/js/cochrane_export.js`:
- POST the `form.download-citation-form` fields to `/search` with `exportAll=true`, `downloadType=endnote`
  (= RIS), `style=cochrane-cdsr-endnote` or `cochrane-central-endnote`, `selectedType=review|central`,
  `siteId=20181`, `withAbstract=on`, `date_id=<Date.now()>`;
- poll `/search?…&p_p_resource_id=citation-export-status&date_id=<id>` until it returns `100`;
- GET `…citation-export-get-file&date_id=<id>` → RIS text (`Record #n of N` headers, tags `TY  -  JOUR`).

It exports the result set of the search that is currently open. Run it once per tab (review, central).
153 CENTRAL records ≈ 530 KB; then dump with `03-browser-data-out.md`.

RIS quirks handled by `scripts/dedup.py`: two spaces after the dash, `C3 - PUBMED 41138739,EMBASE …`
gives the PMID, HTML entities (`&amp;`).
