// CINAHL (EBSCO research.ebsco.com) — pull all records with abstracts through the results-page JSON API.
// Usage: paste on any research.ebsco.com page, then
//   const items = await window._eall(QUERY, '3h2q4r');   window._addFile('cinahl_<topic>.json', JSON.stringify(items))
window._pf = window._pf || window.fetch;
window._esearch = async (q, opid, offset, count) => {
  const body = {
    advancedSearchStrategy: 'NONE', query: q, autoCorrect: false, profileIdentifier: opid,
    expanders: ['thesaurus', 'fullText', 'concept'],          // UI defaults — keep for matching counts
    filters: [{ id: 'databases', values: ['ccm'], type: 'LIMITER' }],
    sort: 'relevance', isNovelistEnabled: false, includePlacards: false,
    offset, count, highlightTag: 'mark', userDirectAction: false,
  };
  const r = await window._pf('/api/search/v1/search?applyAllLimiters=true&includeSavedItems=false&excludeLinkValidation=true&includeHbrRestrictedLinks=true&useV3CoverArt=true', {
    method: 'POST', credentials: 'include',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body),
  });
  return JSON.parse(await r.text()).search;
};
window._eall = async (q, opid) => {
  const strip = (s) => (s || '').replace(/<\/?mark>/g, '');
  const out = [];
  let total = Infinity;
  for (let off = 0; off < total; off += 50) {
    const s = await window._esearch(q, opid, off, 50);
    total = s.totalItems;
    for (const it of s.items) {
      out.push({ an: it.an, title: strip(it.title && it.title.value), abstract: strip(it.abstract && it.abstract.value),
        authors: (it.contributors || []).map((c) => c.name), doi: it.doi || '', source: it.source || '',
        date: it.publicationDate || '', volume: it.volume || '', pageStart: it.pageStart || '', pageEnd: it.pageEnd || '',
        docTypes: it.docTypes || [], pubTypes: it.pubTypes || [] });
    }
    await new Promise((r) => setTimeout(r, 800));
  }
  window._cinTotal = total;
  return out;
};
'cinahl api ready';
