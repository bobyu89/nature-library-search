# Deduplication and screening

## Deduplicate
```bash
python -I scripts/dedup.py --topic sema --out <work> \
  --input PubMed=raw/pubmed_sema.ris --input Cochrane=raw/cochrane_sema_reviews.ris \
  --input Cochrane=raw/cochrane_sema_central.ris --input Embase=raw/embase_sema_2026.ris \
  --input Embase=raw/embase_sema_pre2026.ris --input CINAHL=raw/cinahl_sema.json \
  --input Airiti=raw/airiti_sema.ris
# year filter for exports that could not be limited in the database:
#   --input "Cochrane=raw/cochrane_ai_central_all.ris@2018-2026"
```
Matching (union-find): same DOI, same PMID, or same normalised title with years within 1 or the same first
author. Master record priority PubMed > Embase > Cochrane > CINAHL > Airiti; empty abstract/DOI/PMID are
filled from the other copies; `sources` lists every database. Output `records_<topic>.json` with ids
`S0001…` (prefix from `--prefix`). The script prints per-database counts, total, unique and duplicates — these
are the PRISMA identification numbers.

Afterwards, run the near-duplicate check (`--near-dups` flag) and decide the few it lists by hand: preprint vs
published (keep both, different reports), registry records with similar titles (keep), same title + same
authors in different years (merge — the script already merges same-first-author pairs).

## Calibrate before screening everything (pilot)
`python -I scripts/pilot_sample.py --records <work>/records_<topic>.json --n 50 --hint randomi --hint <key term> --out <work>/pilot_<topic>.csv`
The author screens the 50 by hand (fill `decision`, `reason`); run screener A on the same uids; then
`screen_compare.py --a <work>/decisions_pilot --b <work>/pilot_<topic>.csv`. If FT-vs-exclude κ < 0.6 or the AI misses
any author FT, revise the criteria file (usually a vague special rule) and repeat on a fresh sample. Report the
pilot κ in the methods ("篩選前以 50 筆進行校準，κ = …").

## Title/abstract screening with parallel subagents (dual, independent)
1. Copy `templates/criteria_template.md` to `<work>/criteria_<topic>.md` and fill it from the protocol's
   inclusion/exclusion table. Spell out the special rules that matter for the topic (e.g. "secondary analyses
   of the index RCT → FT with note", "conference abstracts → D", "registry records → D").
2. `python -I scripts/make_batches.py --records <work>/records_<topic>.json --n 5` → `batches/<topic>_<k>.jsonl`
   (~220 records each, abstracts cut at 2,500 characters).
3. Launch one subagent per batch in the same turn (model: a fast one is fine), background mode. Prompt:
   read the criteria completely; read every record (title + abstract), judge each one — no keyword-only rules;
   write `decisions/<topic>_<k>.json` as a JSON array `{uid, decision: FT|P|I|O|D|L, reason ≤ 15 words, note}`
   in input order; verify with Python that the uid set matches the input; reply with counts and the FT list.
   Tell them to use uniquely named helper scripts — agents sharing one folder overwrite each other's `show.py`.
4. Read every FT list in the replies; borderline notes ("check at full text") are expected.
5. **Second, independent screener (B)**: launch a second set of subagents on the same batches, writing to
   `decisions_B/`. Make them genuinely independent: a different model if available, records in reversed order,
   and a prompt that does not show screener A's output. Then
   ```bash
   python -I scripts/screen_compare.py --a <work>/decisions --b <work>/decisions_B --topic <topic> \
     --records <work>/records_<topic>.json --out <work>/conflicts_<topic>.csv
   ```
   prints agreement and Cohen's κ (FT vs exclude, and 6 codes) and writes a conflict sheet. **The author
   adjudicates every conflict** (fill `final`), then `--resolve conflicts_<topic>.csv` writes `decisions_final/`
   which `screen_merge.py --decisions decisions_final` uses. This makes "兩人獨立篩選、不一致時由作者裁定" a true
   sentence: two independent screeners plus a human decision on every disagreement. Still disclose that the two
   screeners were AI.

## Full-text stage
Write `<work>/ft_<topic>.json`:
```json
{"categories": {"SEL": {"label": "同一 RCT 之次要分析，改於證據整合引用", "short": "SELECT次要分析"},
                "POP": {"label": "以糖尿病病人為主，或無法分離未伴隨糖尿病族群結果", "short": "族群不符"}},
 "include": ["S0939", "S0558", "S0432"],
 "not_retrieved": {"A0318": "出版社與圖書館均無全文"},
 "exclude": {"SEL": ["S0081", "S0097"], "POP": ["S0047"]},
 "notes": {"S0214": "semaglutide 試驗未報告心血管結果"}}
```
Every FT uid must appear exactly once (the merge script checks).

Read the full text for every FT record: get it through the library (publisher page via the proxy) or the
`nature-downloader` skill (lawful OA / publisher API / institutional route), save PDFs under `<work>/fulltext/`,
and judge against the criteria. Only when the full text truly cannot be obtained, either mark the record
`not_retrieved` or decide on the abstract and record `"basis": {"<uid>": "abstract"}` — the counts file then lists
these in `ft_basis_abstract_only` and the appendix must say so. Full-text screening can be split across
subagents the same way (one PDF batch per agent), with the author checking every exclusion.
Then:
```bash
python -I scripts/screen_merge.py --topic sema --work <work>
```
→ `screen_<topic>.json` (per-record state) and `counts_<topic>.json` (all PRISMA numbers, reasons sorted by size).

## Keep the manuscript in step
If the full-text count or reasons change, rewrite the screening paragraph and the PRISMA figure together
(see `05-outputs.md`). The final included set should be the papers actually appraised; if screening finds a
better candidate, raise it with the user instead of silently swapping.
