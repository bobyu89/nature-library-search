# PubMed

No proxy needed. Use NCBI E-utilities through `scripts/pubmed_ris.py`; it searches, fetches XML in
batches of 200 and writes RIS with abstract, DOI, `AN - PMID:<id>` and an `N1` note.

```bash
python -I scripts/pubmed_ris.py --term-file query.txt --mindate 2015/01/01 --maxdate 2026/10/14 \
  --note "PubMed 檢索 2026-10-14" --out raw/pubmed_<topic>.ris
```

- Put the full boolean query in a text file (`--term-file`) to avoid shell quoting problems.
- `--count-only` prints the count without fetching; use it to record line-by-line counts (#1, #2 …).
- Fixing `--maxdate` makes the count reproducible later (PubMed numbers do not drift with a fixed end date).
- The PubMed MCP tool allows only ~20 Boolean operators per query; use the script for long strategies.
- Book records (`PubmedBookArticle`) are exported as BOOK/CHAP.
