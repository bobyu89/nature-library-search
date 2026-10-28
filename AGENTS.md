# AGENTS.md — nature-library-search

This repository is an Agent Skill usable by Claude Code and OpenAI Codex.

- Entry point: `SKILL.md` (router). Follow its routing protocol; load files listed in `manifest.yaml` per stage.
- Carrier differences (browser tools, subagents, downloads): `references/09-carriers.md`.
- Never type library or personal-account credentials; the user logs in.
- Scripts: `python -I scripts/<name>.py --help`. After changing any script run `python -I tests/run_tests.py`.
- Record changes in `CHANGELOG.md` and bump `version` in `manifest.yaml`.
