# Validating the search and supplementary methods

## Seed-set validation (do this before screening)
List 3–10 papers that any competent search on the question must find (from the protocol, a known review, the
user's draft, or the index trial and its main SR). Save `seeds.csv` (`label,doi,pmid,title`). Then
```bash
python -I scripts/seed_check.py --seeds seeds.csv --raw "PubMed=raw/pubmed_<t>.ris" --raw "Embase=raw/embase_<t>.ris" ...
```
Every seed should be found by at least one database, and the core ones by PubMed and Embase. A miss means a
concept block or a limit is too narrow (typical culprits: an outcome block, a design filter, a PT limit in CINAHL,
quoted phrases with wildcards in Cochrane). Fix the strategy, re-export, and keep the before/after counts in the log.
Report it in the methods ("以 n 篇已知關鍵文獻檢核檢索策略，均被檢出").

## Citation chasing (PRISMA "other methods")
After the included studies are fixed:
```bash
python -I scripts/citation_chase.py --doi <included DOI> [--doi ...] --records <work>/records_<t>.json --out <work>/chase_<t>.json --mailto <user email only if they agree>
```
It returns backward (reference list) and forward (cited-by) records not already in the deduplicated set. Screen
them with the same criteria (small numbers — screen in the main thread). Put the counts in the diagram header or a
second column: "其他方法：引文追蹤 n 筆，篩選後新增 0 篇".

## Trial registries and grey literature
- ClinicalTrials.gov: `scripts/ctgov.py` (API v2) → JSON + RIS; add `--input CTgov=raw/ctgov_<t>.ris` to dedup if
  registries are part of the protocol, otherwise use the list for the discussion ("進行中試驗").
  Search registries broadly — condition + intervention only — and screen the list: registry titles use their own
  wording ("morbidity and mortality" rather than "cardiovascular outcomes"), so an outcome term silently drops trials
  (tested 2026-10-28: `--cond obesity --intr tirzepatide` finds SURMOUNT-MMO NCT05556512; adding
  `--term "cardiovascular outcomes"` loses it).
- WHO ICTRP: browser search at trialsearch.who.int, record the count and relevant IDs by hand.
- Theses (臺灣博碩士論文知識加值系統) and conference abstracts: see `databases/other-sources.md`.

## Sensitivity variants
Run one broader variant per database (drop the outcome block or use class terms) and record only the count and the
number of new relevant titles found by a quick scan. If the broader variant finds an eligible paper, the main
strategy was too narrow — adopt the broader one.
