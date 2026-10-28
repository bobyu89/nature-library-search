# Changelog

## 1.2.0 — 2026-10-28
- Carrier-neutral: runs on Claude Code or OpenAI Codex (`references/09-carriers.md`, `agents/openai.yaml`, `AGENTS.md`).
- `install.ps1` / `install.sh` link one git checkout into `~/.claude/skills` and `~/.codex/skills`.
- Published as a GitHub repository; `.gitignore` keeps search data out of version control.

## 1.1.0 — 2026-10-28
Deeper
- Dual independent screening with Cohen's kappa and an author-adjudicated conflict sheet (`screen_compare.py`).
- Calibration pilot sample (`pilot_sample.py`).
- Seed-set validation of the strategy (`seed_check.py`).
- Full-text decision basis recorded (`basis` in ft spec → `ft_basis_abstract_only`).
- Citation chasing via OpenAlex (`citation_chase.py`); ClinicalTrials.gov API (`ctgov.py`) — registry search must
  stay broad (verified: outcome term dropped SURMOUNT-MMO).
Higher
- Structured search log (`templates/searches.example.json`) → PRISMA-S appendix + 16-item status (`prisma_s.py`).
- TWNA 1141020 rubric 4-2 (20 points) self-check; page limit includes all appendices.
- SoF skeleton for GRADE hand-off; living updates (`living_update.py`); SHA-256 archive (`archive.py`).
Wider
- Other proxy patterns (EZproxy, WebVPN, IP), Claude in Chrome route, other sources (WoS, PsycInfo/MEDLINE on
  EBSCO, NDLTD, CNKI, Google Scholar — unverified), Rayyan/Covidence/combined RIS exports (`export_formats.py`).
More mature
- Resumable pipeline state with file hashes (`state.py`); work folder in the user's project folder.
- Zotero `check` + `--skip-existing` (found 1,090 real duplicates from a manual import).
- Platform preflight checks (`templates/js/preflight.js`).
- Regression tests (`tests/run_tests.py`, synthetic + real data); licence/TDM principles.

## 1.0.0 — 2026-10-28
First version from the TWNA A類 run: library login gate, Cochrane/Embase/CINAHL/Airiti/PubMed export recipes,
chunk dump, dedup, subagent screening, PRISMA diagram, CSV log, BibTeX per stage, Zotero connector import.
