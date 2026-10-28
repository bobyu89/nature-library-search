# CINAHL Complete (EBSCO new interface, research.ebsco.com)

## Search
Open the config `entry`; it lands on `https://research.ebsco.com/c/<opid>/search/advanced?...&defaultdb=ccm`.
Run a query by URL (keep the UI's default expanders so counts match what the user would see):
```
https://research.ebsco.com/c/<opid>/search/results?q=<encodeURIComponent(query)>&db=ccm&searchMode=bool&autocorrect=n
```
Count: page text `所有結果：1-10，共 171 項`. Syntax: `(MH "Obesity+")`, `TI (a OR b) OR AB (a OR b)`,
`AND DT 2015-2026`.

## Export without MyEBSCO
"匯出結果 (最多 25,000)" requires a personal MyEBSCO login — do not use it. The per-page "下載" only offers
PDF/Word/CSV/BibTeX/MARC/XML for ≤ 50 items and the XML lacks abstracts. Instead call the same JSON API
the results page uses (`templates/js/cinahl_search.js`):

POST `/api/search/v1/search?applyAllLimiters=true&includeSavedItems=false&excludeLinkValidation=true&includeHbrRestrictedLinks=true&useV3CoverArt=true`
```json
{"advancedSearchStrategy":"NONE","query":"<query>","autoCorrect":false,"profileIdentifier":"<opid>",
 "expanders":["thesaurus","fullText","concept"],"filters":[{"id":"databases","values":["ccm"],"type":"LIMITER"}],
 "sort":"relevance","isNovelistEnabled":false,"includePlacards":false,"offset":0,"count":50,
 "highlightTag":"mark","userDirectAction":false}
```
`search.totalItems` is the count; page with `offset` += 50. Each item has `an, title.value, abstract.value,
contributors[].name, doi, source, publicationDate, volume, pageStart, pageEnd, docTypes, pubTypes`.
Strip `<mark>` tags, keep those fields, and save as `raw/cinahl_<topic>.json` (an array) — `dedup.py` reads it.

CINAHL cannot be pinned to an entry date; report the export date and any +n difference.
