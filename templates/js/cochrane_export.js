// Cochrane Library bulk RIS export of the search that is currently open (results tab visible).
// Usage: paste, then  await window._cx('review')  or  await window._cx('central')
// Result text is kept in window._ris; returns [length, records].
window._cx = async (type, dl = 'endnote') => {
  const t = Date.now();
  const f = document.querySelector('form.download-citation-form');
  const p = new URLSearchParams(new FormData(f));
  p.set('siteId', '20181');
  p.set('downloadType', dl);                       // endnote = RIS (EndNote)
  p.set('style', (type === 'central' ? 'cochrane-central-' : 'cochrane-cdsr-') + dl);
  p.set('exportAll', 'true');
  p.set('selectedType', type);                     // review | central
  p.set('withAbstract', 'on');
  p.set('date_id', String(t));
  fetch('/search', { method: 'POST', body: p, credentials: 'include' });
  const base = '/search?p_p_id=scolarissearchresultsportlet_WAR_scolarissearchresults&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=';
  let st = '';
  for (let i = 0; i < 120; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    st = await (await fetch(base + 'citation-export-status&date_id=' + t, { credentials: 'include' })).text();
    if (st === '100' || st === '-1') break;
  }
  if (st !== '100') return 'status ' + st;
  const tx = await (await fetch(base + 'citation-export-get-file&date_id=' + t, { credentials: 'include' })).text();
  window._ris = tx;
  return [tx.length, (tx.match(/^TY  -/gm) || []).length];
};
// Hit counts in Search manager:
// Array.from(document.querySelectorAll('button.search-manager-result')).map(b => b.textContent.trim())
'cochrane export ready';
