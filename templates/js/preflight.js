// Preflight: run on each database's results/search page BEFORE a full run. It checks that the page elements and
// endpoints the recipes rely on still exist, so a platform redesign is caught early instead of mid-export.
// Usage: paste, then  await window._preflight('cochrane'|'embase'|'cinahl'|'airiti')
window._preflight = async (db) => {
  const ok = (cond, what) => ({ check: what, pass: !!cond });
  const r = [];
  if (db === 'cochrane') {
    r.push(ok(document.querySelector('form.download-citation-form'), 'download-citation-form present'));
    r.push(ok(document.querySelector('[data-option="endnote"]') || /RIS \(EndNote\)/.test(document.body.innerHTML), 'RIS (EndNote) option'));
    r.push(ok(/Access provided by/.test(document.body.innerText), 'institutional access banner'));
  } else if (db === 'embase') {
    r.push(ok(document.querySelector('#search-query, #searchField'), 'query textarea'));
    const s = await fetch('/rest/search-history', { credentials: 'include' }).then((x) => x.status).catch(() => 0);
    r.push(ok(s === 200, 'REST /rest/search-history reachable (' + s + ')'));
    r.push(ok(/results for search #|Quick search|Advanced search/.test(document.body.innerText), 'Embase app loaded'));
  } else if (db === 'cinahl') {
    const m = location.pathname.match(/\/c\/([^/]+)\//);
    r.push(ok(m, 'opid in URL (' + (m ? m[1] : '-') + ')'));
    if (m) {
      const s = await fetch('/api/search/v1/search?applyAllLimiters=true', { method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ advancedSearchStrategy: 'NONE', query: 'nursing', autoCorrect: false, profileIdentifier: m[1],
          expanders: [], filters: [{ id: 'databases', values: ['ccm'], type: 'LIMITER' }], sort: 'relevance', offset: 0, count: 1 }) })
        .then((x) => x.json()).then((j) => j.search && j.search.totalItems).catch(() => null);
      r.push(ok(s, 'JSON search API answers (totalItems ' + s + ')'));
    }
  } else if (db === 'airiti') {
    r.push(ok(localStorage.getItem('_airTpl'), 'query template saved (_airTpl)'));
    const h = await fetch('/Article/CiteWindow', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' },
      body: new URLSearchParams({ jsString: encodeURIComponent('[]') }) }).then((x) => x.text()).catch(() => '');
    r.push(ok(/ajaxRequestVerificationToken_CiteWindow/.test(h), 'CiteWindow returns export token'));
  }
  return { db, allPass: r.every((x) => x.pass), checks: r };
};
'preflight ready';
