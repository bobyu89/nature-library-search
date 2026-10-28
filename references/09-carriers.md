# Running on Claude Code or Codex

The skill is carrier-neutral: the same SKILL.md, references, templates and scripts work in Claude Code (desktop or
CLI) and in OpenAI Codex (CLI / app). Only the tool names differ. Map them like this and keep everything else as written.

| Need | Claude Code | Codex |
|---|---|---|
| Open a page, user logs in | built-in browser `navigate` / `preview_start`; or Claude in Chrome | Codex browser / Chrome tools (`codex` Chrome extension or a browser MCP such as Playwright / Chrome DevTools) |
| Run page JavaScript (all recipes in `templates/js/`) | `javascript_exec` (`mcp__Claude_Browser__javascript_tool`) | the browser tool's evaluate/execute-script call (`browser_evaluate`, `evaluate_script`, …) |
| Click / type / screenshot | `computer` actions with `action_summary` | the browser tool's click/type/screenshot |
| Get large exports to disk | chunk dump → `tool-results` → `scripts/collect_chunks.py` (`03-browser-data-out.md`) | in a real Chrome profile downloads work: create a Blob in the page and click a download link (`a.download = name`), then move the file from Downloads into `<work>/raw/` (each download needs the user's OK). If the tool returns large values directly, write them to `<work>/raw/` instead. |
| Parallel screening batches | `Agent` subagents in one turn, background | run `codex exec` processes in parallel (one per batch, same prompt as in `04-dedup-and-screening.md`), or screen batches sequentially in the main thread |
| Second independent screener | second set of subagents (different model if available) | a second `codex exec` run with another model (`-m`) or the other carrier (Claude) — mixing carriers is the most independent option |
| Run scripts | Bash / PowerShell tool | shell tool (`python -I scripts/...`) |
| Long jobs (Zotero import) | `run_in_background` | run in a separate terminal or `nohup … &`; poll the log |
| Ask the user | AskUserQuestion / plain message | plain message |

Shared rules regardless of carrier:
- The user logs in; the agent never types credentials (same in Codex — stop and ask).
- Keep the work folder in the user's project folder and use `scripts/state.py` so either carrier can resume the
  other's run (e.g. export with Claude, screen with Codex as screener B).
- On Windows run Python with `-I` and UTF-8 output; heredocs that contain Chinese break under `-I` (stdin decoded
  as cp950) — write scripts to files instead.
- Paths: Claude Code skills live in `~/.claude/skills/`, Codex skills in `~/.codex/skills/`. `install.ps1` / `install.sh`
  link both to one checkout of the GitHub repo, so `git pull` updates both.
