# Zotero import by PRISMA stage

## Files
```bash
python -I scripts/to_bib.py --topic sema --label semaglutide --work <work> --out <dir>
```
writes `<label>_1_標題摘要排除.bib`, `_2_全文排除.bib`, `_3_無法取得全文.bib`, `_4_納入評讀.bib`. Each record
appears in exactly one file and carries `keywords` → Zotero tags (`來源:Embase`, `篩選1_標題摘要:排除-研究設計不符`,
`篩選2_全文:納入評讀` …), `note` (PRISMA ID, PMID) and `annote` (AI reasons) → child notes.

If the user imports by hand: File → Import → choose the .bib, keep "Place imported collections and items into
new collection" ticked → a collection named after the file. Dragging a .bib into Zotero only attaches the file.

## Before importing: what is already there?
```bash
python -I scripts/zotero_import.py check --data-dir C:/Users/<you>/Zotero
```
counts PRISMA IDs already in Zotero (read from the notes, trash excluded) and lists IDs present twice. In the
2026-10 run the user had already imported one stage file by hand into a top-level collection while Claude imported
the same file into the stage sub-collection — 1,090 duplicates that only this check revealed. Always pass
`--skip-existing <data dir>` to `import` so a rerun never duplicates.

## Importing for the user (Zotero desktop must be running)
The connector at `http://127.0.0.1:23119` accepts imports; the local API is off.
```bash
python -I scripts/zotero_import.py selected                       # which collection is selected now
python -I scripts/zotero_import.py mkcoll "1_標題摘要排除（n = 1,090）" "2_全文排除（n = 45）" "4_納入評讀（n = 3）"
python -I scripts/zotero_import.py import --file semaglutide_4_納入評讀.bib --target C26
python -I scripts/zotero_import.py import --file semaglutide_1_標題摘要排除.bib --target C24 --batch 100 --skip-existing C:/Users/<you>/Zotero
```
- `mkcoll` creates empty sub-collections under the collection the user has selected (a tiny Zotero RDF with only
  `z:Collection` nodes); it prints the new IDs. Ask the user to select the parent collection first.
- `import` sends BibTeX in batches (≈ 1.5 s per record), then `updateSession` moves each batch to `--target`.
  Run large files in the background; 1,090 records took ~30 min.
- Never send one huge Zotero RDF: a 4 MB RDF crawled for an hour, the HTTP call timed out, and a retry started a
  second parallel import (duplicates). Never resend after a timeout without checking the database first.

## Checking what Zotero actually holds
The database is in WAL mode and locked while Zotero writes. Copy `zotero.sqlite` and `zotero.sqlite-wal` to a
scratch folder and query the copy (`immutable=1` reads miss everything still in the WAL):
```sql
select c.collectionName, count(ci.itemID) from collections c left join collectionItems ci
  on ci.collectionID=c.collectionID and ci.itemID not in (select itemID from deletedItems)
where c.parentCollectionID=<id> group by c.collectionID;
```
Deleting items is the user's job (select collection → Ctrl+A → Delete); tell them exactly which collection.
