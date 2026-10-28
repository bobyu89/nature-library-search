// Embase export of the CURRENT results (≤ 500 records per job when not signed in).
// Usage: paste, then  const t = await window._emb(272, 0)          (articles)
//                     const t = await window._emb(94, 0, true)     (Clinical trials tab must be active)
// Then compact: window._compact(t)  (articles)  /  window._compactCT(t)  (registry records)
window._pf = window._pf || window.fetch;
window._dl = async (tries) => {
  for (let k = 0; k < tries; k++) {
    const h = await (await window._pf('/search/download', { credentials: 'include' })).text();
    const m = h.match(/href="(https:\/\/www\.embase\.com\/rest\/download\/[^"]+)"/);
    if (m) return await (await window._pf(m[1], { credentials: 'include' })).text();
    await new Promise((r) => setTimeout(r, 2000));
  }
  return 'no link';
};
window._emb = async (count, offset, ct = false) => {
  const body = {
    orderBy: 'PUBLICATION_DATE', fromSearchResults: true,
    recordsSelection: { batch: { count, offset } },
    preferences: {
      formatValue: ct ? 'RIS_CT_RECORDS' : 'RIS_RECORDS', customFieldValues: null,
      additionalOptions: { includeHighlightedResults: false, includeSearchQuery: false },
      openUrlEnabled: false, defaultExportEnabled: false, outputTypeValue: null,
    },
  };
  let st = 0;
  for (let k = 0; k < 20; k++) {           // 400 {} = previous job still pending → wait and retry
    const r = await window._pf(ct ? '/rest/export/ct-records' : '/rest/export/records', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json; charset=utf-8', Accept: 'application/json, text/plain, */*' },
      body: JSON.stringify(body),
    });
    st = r.status;
    if (st === 202) break;
    await window._dl(5);
  }
  if (st !== 202) return 'export status ' + st;
  return await window._dl(60);
};
window._compact = (t) => t.split('\n').filter((l) => !/^(M1|KW|LK|AD|L2|UR|SN|C1|C2|C3|C4|JO)  -/.test(l)).join('\n');
window._compactCT = (s) => s.split(/\nER  -[^\n]*\n?/).filter((r) => r.trim()).map((r) =>
  r.split('\n').filter((l) => /^(TY|AN|TI|AB|PY|Y1|DA|UR|M3|DB)  -/.test(l))
    .map((l) => (l.startsWith('AB  -') ? l.slice(0, 2500) : l)).join('\n') + '\nER  - ').join('\n');
// Set the query box (results page) without auto-mapping:
// const ta=document.querySelector('#search-query'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta, Q); ta.dispatchEvent(new Event('input',{bubbles:true}));
// Counts: (document.body.innerText.match(/\d[\d,]* results for search #\d+/)||[''])[0]
'embase export ready';
