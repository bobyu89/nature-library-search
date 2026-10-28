# Search strategy: PICO → per-database syntax

## 1. Concept blocks
Build 3–4 blocks from the PICO and AND them. Usually: **P** (condition/population), **I** (intervention),
optionally **O** (outcome), and a **design filter** where the database needs one (PubMed, Embase).
Leave subtle eligibility criteria (e.g. "without diabetes", "adults") to screening — putting them in the
query silently loses records whose abstract does not say it.

Each block = controlled vocabulary (exploded) OR free-text synonyms in title/abstract.

## 2. Syntax per database (verified 2026-10)

| Element | PubMed | Cochrane (Search manager) | Embase | CINAHL (EBSCO) | Airiti 華藝 |
|---|---|---|---|---|---|
| Subject heading, exploded | `"Obesity"[MeSH]` | `[mh Obesity]` | `'obesity'/exp` | `(MH "Obesity+")` | — |
| Title/abstract | `obes*[tiab]` | `(obes* OR overweight):ti,ab,kw` | `obes*:ti,ab` | `TI obes* OR AB obes*` | all fields (default) |
| Phrase + truncation | `"large language model*"[tiab]` | `(large NEXT language NEXT model*)` — quoted phrase with `*` triggers a warning and loses records | `'large language model*':ti,ab` | `"large language model*"` | — |
| Design filter | `randomized controlled trial[pt] OR randomi*[tiab] OR systematic review[pt] OR meta-analysis[pt]` | none (Reviews + CENTRAL already) | `'randomized controlled trial'/exp OR random*:ti,ab OR 'systematic review'/exp OR 'meta analysis'/exp` | usually none — PT limits drop key RCTs (SELECT/NEJM had no PT tag) | none |
| Years | E-utilities `mindate/maxdate` (`datetype=pdat`) | export all, filter `PY` afterwards (Limits only touch CENTRAL) | `[2015-2026]/py` | `AND DT 2015-2026` | filter `PY` afterwards (URL year fields are ignored) |
| Other limits | — | — | `[humans]/lim`, `NOT 'conference abstract'/it` | — | — |

Platform traps:
- **Embase auto-mapping**: the Advanced page maps terms and adds free-text `'term'` in all fields
  (916 vs 767 records for the same query). Submit the final query from the results-page box with every
  Mapping option unchecked, and record the query as shown in Search history.
- **EBSCO expanders**: the UI default applies `thesaurus`, `fullText`, `concept`. Counts reported from the
  UI include them; use the same expanders in the API so numbers match (`expanders=None` gave 1,876 vs 2,577).
- **Airiti**: Boolean works in the simple box (`A AND (B OR C)`); the search is over all fields including
  full text, so expect noise — that is fine, screening removes it.

## 3. Record keeping template (`search_log.md`)
```
## Embase — searched 2026-10-14, exported 2026-10-20
#1 <query as shown in history>                             767
#4 #3 AND [1-1-1900]/sd NOT [15-10-2026]/sd                 762   ← pinned to records added ≤ 2026-10-14
Exported: 762 (Articles 762, Clinical trials 0) → raw/embase_sema_*.ris
Note: 1 fewer than 2026-10-14 (record merged/withdrawn upstream).
```

## 4. Sensitivity checks worth doing
- A broader variant (class terms instead of the drug, outcome block removed) — count only, screen the delta
  by title if small.
- Scopus as a supplementary source (count and title scan, not a full export) — say so in PRISMA.
