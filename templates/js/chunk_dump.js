// Paste once per page (javascript_exec). Then: window._addFile(name, text) for each export,
// window._buildDump(), and call window._chunk('<group>', i) for i = 0 .. n-1 (one call each).
window._store = window._store || {};
window._addFile = (name, text) => { window._store[name] = text; return [name, text.length]; };
window._buildDump = () => {
  window._dump = Object.entries(window._store).map(([n, t]) => '@@FILE ' + n + '\n' + t + '\n@@END\n').join('');
  return [window._dump.length, Math.ceil(window._dump.length / 290000)];
};
window._chunk = (group, i) => {
  const s = window._dump.slice(i * 290000, (i + 1) * 290000);
  // pad small chunks so the harness saves them to a tool-results file instead of inlining them
  return '@@CHUNK ' + group + ' ' + i + '\n' + s + (s.length < 200000 ? 'x'.repeat(300000) + '@@PAD' : '');
};
'chunk helpers ready';
