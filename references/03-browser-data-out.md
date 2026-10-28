# Getting large exports out of the browser pane

The built-in browser cannot save downloads (ERR_ABORTED) and cannot reach localhost, so a local receiver
does not work. What does work: when a `javascript_exec` result is too large, the harness saves it to a file in
the session's `tool-results/` folder (`mcp-Claude_Browser-javascript_tool-<ts>.txt`, a JSON array whose
first element's `text` is the JSON-encoded return value). Results up to ~300 K characters are saved intact.

## Recipe (`templates/js/chunk_dump.js`)
1. Keep each finished export in page memory: `window._store['<file name>'] = text`.
2. Build one dump string: `@@FILE <name>\n<content>\n@@END\n` for every file of a database.
3. Return it in 290,000-character chunks, each prefixed `@@CHUNK <group> <i>\n`; pad the last chunk with
   `x` × 300,000 + `@@PAD` so it is also large enough to be saved to a file rather than inlined into context.
4. Call `window._chunk('<group>', i)` once per chunk (one tool call each — they run quickly).
5. Run `scripts/collect_chunks.py <tool-results dir> <work>/raw` — it reassembles every group, splits the
   `@@FILE` blocks and prints record counts (`TY  -` lines) per file.

Tips
- Use a new group name per database (`cai`, `emb`, `cin`, `air`) so chunk numbers never collide.
- Compact before dumping (Embase index terms, Embase CT records) to keep the number of chunks low.
- Page navigation wipes `window` variables — dump before you leave the page.
- Navigate to a short URL before long loops; the tab URL is echoed into every result.
- The tool-results folder is `~/.claude/projects/<project>/<session-id>/tool-results/`.
