# Embase (embase.com)

## Search
1. Open the config `entry`; it lands on embase.com (Quick search). Reject cookies, dismiss surveys.
2. Run the query from the **results page** box (`textarea#search-query`) with **all Mapping options
   unchecked**; the Advanced page auto-maps and inflates results. Set the value with the native setter and
   dispatch `input`, then click the magnifier button next to the box (coordinates change when panels open —
   take a screenshot).
   ```js
   const ta=document.querySelector('#search-query');
   Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta, Q);
   ta.dispatchEvent(new Event('input',{bubbles:true}));
   ```
3. Read counts from the page text `/\d[\d,]* results for search #\d+/` and the tabs
   `Articles (n)` / `Clinical trials (n)`. Both tabs count toward the total.
4. **Pin to a date** (reproducibility): `#N AND [1-1-1900]/sd NOT [15-10-2026]/sd` keeps records added
   up to 14 Oct 2026. Record the pinned count.

Useful limits: `[2015-2026]/py`, `[humans]/lim`, `NOT 'conference abstract'/it`.

## Export
Unregistered users can export at most **500** records per job. Split the set: `#N AND [2026]/py` and
`#N NOT [2026]/py` (or other year cuts) so each part ≤ 500, then export each part while its results are the
current results. Use `templates/js/embase_export.js`:
- POST `/rest/export/records` with
  `{"orderBy":"PUBLICATION_DATE","fromSearchResults":true,"recordsSelection":{"batch":{"count":N,"offset":0}},"preferences":{"formatValue":"RIS_RECORDS","customFieldValues":null,"additionalOptions":{"includeHighlightedResults":false,"includeSearchQuery":false},"openUrlEnabled":false,"defaultExportEnabled":false,"outputTypeValue":null}}`
  → `202 Accepted`. A `400 {}` means another export job is still pending: wait and retry.
- Poll GET `/search/download` (HTML) until it contains `href="https://www.embase.com/rest/download/…/records.ris"`;
  fetch that link → RIS.
- **Clinical trials tab** (registry records) uses `/rest/export/ct-records` with
  `formatValue: "RIS_CT_RECORDS"`; switch to the tab first.

RIS is large (~5 KB/record because of index terms). Compact before dumping: drop `M1 KW LK AD L2 UR SN C1 C2 C3 C4 JO`
lines. Fields kept: `T1` title, `A1` authors, `Y1` year, `JF` journal, `DO` DOI, `C5` PMID, `N2` abstract, `U2` Embase ID.
