# Principles (always loaded)

## Reproducibility is the product
A search section is only worth something if a reviewer could rerun it. So for every database keep:
- the exact query string as submitted (after any auto-mapping the platform applied),
- the line-by-line counts, limits (years, humans, language, record type) and the date searched,
- the date the records were exported, if different, and why counts differ from an earlier run
  (databases add records daily; Embase can be pinned with an entry-date limit, CINAHL and Airiti cannot).

Write these into `<work>/search_log.md` as you go, not afterwards.

## The user stays in control of identity
The library account belongs to the user. They log in and solve captchas; Claude never types passwords,
never signs in to personal accounts (MyEBSCO, Embase personal, Elsevier ID) and never creates accounts.
When a platform says an action needs a personal login (EBSCO bulk export, Embase > 500 records),
use the alternative route documented in the database file rather than asking for credentials.

## Be a polite heavy user
Exports are bibliographic records, a few MB in total. Still: run one export job at a time per platform,
add short pauses between batch requests, and stop if the platform throttles or errors repeatedly.
Never bulk-download full-text PDFs (the NDMU policy locks accounts above 500 MB per 5 minutes).

## Licences and text-and-data mining
Database records (abstracts, index terms) are licensed content. Use exports only to screen and report this
review: keep them in the user's project folder, do not post them publicly, do not use them to train or tune
models, and do not redistribute full exports (the reproducibility archive is for reviewers/OSF with the user's
consent; strip abstracts if a public deposit is required). Elsevier pages carry `tdm-reservation` metadata —
bibliographic export for a review is normal use; bulk mining beyond the search is not.

## Work where it survives
Create the work folder in the user's project folder (cloud drive) at the start — `scripts/state.py init` — not in
the scratchpad: the scratchpad can be purged between sessions (this happened in the 2026-10 run and every helper
script was lost). Mark each finished stage with `state.py mark`, and start any resumed session with
`state.py show` to see what is done and whether files changed.

## Check before you change shared state
Before any Zotero import, run `zotero_import.py check` (and import with `--skip-existing`) — the user may already
have imported some of the files by hand. Before re-running an export, compare with the counts already logged.

## Shared browser pane
All subagents share one built-in browser. Two agents typing into the same Cochrane search manager or
Embase history will corrupt each other's line numbers. Do browser work in the main thread (or one agent
at a time) and parallelise only the offline work (screening, extraction).

## Honest numbers
If a re-run gives 762 instead of 763, say so and explain it; never force a number to match a draft.
If screening changes the full-text count from 12 to 48, update the manuscript, do not hide it.

## AI disclosure (TWNA and most journals)
AI-assisted screening and extraction must be disclosed (tool, version, period, tasks) and the author must
verify every decision. Put "AI 初篩，請作者複核" in every Zotero note and CSV row, and remind the user
that a two-reviewer claim in the methods must be true.
