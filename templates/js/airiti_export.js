// Airiti Library — collect docIDs for a query and export RIS (with abstracts) in batches of 50.
// Step 0 (on a results page): save the page-2 link JSON as template
//   const a=[...document.querySelectorAll('a')].find(e=>e.innerText.trim()==='2'&&(e.getAttribute('href')||'').includes('queryString'));
//   localStorage.setItem('_airTpl', decodeURIComponent(a.getAttribute('href').split('queryString=')[1])); location.href='https://www.airitilibrary.com/';
// Step 1 (on the home page): paste this file, then start the detached job and poll window._air.done:
//   window._airRun({ sema: '<boolean query>' })     → window._air.ris.sema  (RIS text), window._air.ids.sema
const _tpl = JSON.parse(localStorage.getItem('_airTpl'));
window._airQ = (kw, page, size) => {
  const j = JSON.parse(JSON.stringify(_tpl));
  Object.assign(j.DSF.SearchFileds[0], { SearchKeyWord: kw, SearchKeyWord_TW: kw, SearchKeyWord_CN: kw });
  j.DSF.PageSize = size; j.DSF.Page = page; j.BSF = null;
  return '/Article/Query?queryString=' + encodeURIComponent(JSON.stringify(j));
};
window._airRIS = async (ids) => {
  const hdr = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' };
  const cw = await (await fetch('/Article/CiteWindow', { method: 'POST', headers: hdr,
    body: new URLSearchParams({ jsString: encodeURIComponent(JSON.stringify(ids)) }) })).text();
  const tok = cw.match(/ajaxRequestVerificationToken_CiteWindow = '([^']+)'/)[1];
  const js = cw.match(/var jsString = '([^']+)'/)[1];
  const r = await fetch('/Article/CiteExport', { method: 'POST', headers: { ...hdr, AjaxRequestVerificationToken: tok },
    body: new URLSearchParams({ jsString: js, type: 'RIS' }) });
  return JSON.parse(await r.text()).ReturnData.Content;
};
window._airRun = (queries) => {
  window._air = { ids: {}, ris: {}, total: {}, err: [], done: false };
  (async () => {
    for (const [k, kw] of Object.entries(queries)) {
      window._air.ids[k] = [];
      for (let p = 1; p < 60; p++) {
        const h = await (await fetch(window._airQ(kw, p, 50))).text();
        const d = new DOMParser().parseFromString(h, 'text/html');
        if (p === 1) window._air.total[k] = (d.body.innerText.match(/[\d,]+ 個查詢結果/) || [''])[0];
        const ids = [...d.querySelectorAll('.searchResultGroup')].map((e) => e.getAttribute('key'));
        if (!ids.length) break;
        window._air.ids[k].push(...ids);
        await new Promise((r) => setTimeout(r, 700));
      }
      const parts = [];
      for (let i = 0; i < window._air.ids[k].length; i += 50) {
        try { parts.push(await window._airRIS(window._air.ids[k].slice(i, i + 50))); } catch (e) { window._air.err.push(k + i + ':' + e); }
        await new Promise((r) => setTimeout(r, 1000));
      }
      window._air.ris[k] = parts.join('\n');
    }
    window._air.done = true;
  })();
  return 'started';
};
'airiti export ready';
