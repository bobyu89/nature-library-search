---
name: nature-library-search
description: >-
  Systematic literature search through the user's own university/hospital library
  proxy (default: 國軍醫院聯合圖書館／國防醫學大學 800a.flysheet.com.tw) across PubMed,
  Cochrane Library, Embase, CINAHL Complete, Scopus and 華藝線上圖書館 (Airiti), plus trial
  registries and citation chasing; bulk-export every record, deduplicate, validate the
  strategy against known key papers, run calibrated dual independent title/abstract
  screening with parallel subagents (Cohen's kappa, author adjudication), full-text
  screening, PRISMA 2020 flow diagram, PRISMA-S search appendix, full-text exclusion
  appendix, TWNA rubric self-check, Zotero import by PRISMA stage, living updates and a
  reproducibility archive. Use this skill whenever the user wants a 完整檢索、K2 搜尋、
  系統性搜尋、用圖書館帳號查 Embase/Cochrane/CINAHL/華藝、匯出全部文獻、去重、逐筆篩選、
  雙人篩選、PRISMA 流程圖填數字、PRISMA-S、檢索策略附錄、全文排除附表、把檢索結果匯入
  Zotero、更新檢索, or is preparing the search section of a TWNA EBHC A類／B類實證報告,
  systematic review, scoping review or thesis — even if they only say「幫我查文獻」
  「用我們圖書館」「PRISMA 待填」「把文獻丟進 Zotero」.
license: MIT
---

# Nature Library Search — Router

End-to-end, reproducible database search through an institutional library proxy:
**strategy → login → export → seed check → dedup → pilot → dual screening → adjudication → full text → outputs → Zotero → archive**.
Built from a real run (2026-10, two TWNA A類 reports, 8 database exports, 2,680 records); every database recipe
in `references/databases/` was verified there unless the file says otherwise.

Do not run the database steps from memory. Load the fragments named in `manifest.yaml` for the stage you are in.

## Routing protocol
1. Read `manifest.yaml`. Always load `references/00-principles.md`, `references/09-carriers.md` (tool names for
   Claude Code vs Codex) and the active library config (`config/library.ndmu.yaml` unless the user names another
   library or has a `config/library.*.yaml`).
2. If a work folder exists, run `scripts/state.py show --work <work>` first and resume from the next stage.
   Otherwise `state.py init` the work folder **inside the user's project folder** (not the scratchpad).
3. Work out which stages the request needs; a full "幫我做完整搜尋" is all of them, in order.
4. For exports, load only the database files you are about to use. Run `templates/js/preflight.js` on each
   database page first; if a check fails, the platform changed — inspect before exporting.
5. Use `scripts/` instead of rewriting helpers (each prints `--help`); after editing any script run
   `python -I tests/run_tests.py`.

## Stages
| Stage | What happens | Load |
|---|---|---|
| strategy | PICO → concept blocks → per-database syntax; seed papers listed | `02-search-strategy.md` |
| login | The **user** logs in to the library in the agent's browser | `01-login-and-safety.md` |
| export | Search, record every line in `searches_<topic>.json`, export all records | `databases/<db>.md`, `03-browser-data-out.md` |
| seed check | Known key papers found by the exports? Fix the strategy if not | `07-validation-and-supplementary.md` |
| dedup | Parse, merge duplicates, list near-duplicates | `04-dedup-and-screening.md` |
| pilot | 50-record calibration: author vs AI, κ, refine criteria | `04-dedup-and-screening.md` |
| screening A/B | Two independent subagent screeners; κ; author adjudicates conflicts | `04-dedup-and-screening.md`, `templates/criteria_template.md` |
| full text | Retrieve and judge full texts; record decision basis | `04-…`, `nature-downloader` skill |
| supplementary | Citation chasing (OpenAlex), trial registries, sensitivity variants | `07-validation-and-supplementary.md` |
| outputs | PRISMA diagram, methods text, PRISMA-S appendix, exclusion appendix, CSV, rubric check | `05-outputs.md`, `08-reporting-and-rubric.md` |
| zotero | BibTeX per stage → sub-collections; `check` and `--skip-existing` first | `06-zotero-import.md` |
| archive / living | SHA-256 package; later re-run and screen only new records | `08-…`, `scripts/archive.py`, `scripts/living_update.py` |

## Work folder (in the user's project folder)
```
<work>/ pipeline_state.json  searches_<t>.json  raw/  records_<t>.json  dedup_<t>.json
        pilot_<t>.csv  decisions/  decisions_B/  conflicts_<t>.csv  decisions_final/
        fulltext/  ft_<t>.json  screen_<t>.json  counts_<t>.json  out/
```

## Hand-offs to the user's other skills
- Report writing → `twna-ebhc-report` (A類 appraises 2–3 papers: 1 SR + 1–2 RCT); SoF skeleton in `templates/sof_template.md`.
- PRISMA 2020 checklist wording → `prisma-2020-master`; scoping reviews → `scoping-review-master`.
- MeSH strategy and citation-file conversion → `nature-academic-search` (wf3, wf4).
- Full text → `nature-downloader` (lawful routes). References → `apa7-master`.

## Non-negotiables (reasons in 00-principles)
- The user logs in; never type credentials or sign in to personal accounts; never create accounts.
- Export citation records only; respect download limits and database licences (no mining beyond the review).
- Decline non-essential cookies; leave accept-only banners alone.
- Report counts exactly as observed, with dates; explain every difference.
- AI screening is disclosed; every conflict and every full-text exclusion is decided or checked by the author.
