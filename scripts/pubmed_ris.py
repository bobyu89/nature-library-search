"""PubMed search via NCBI E-utilities and RIS export.

usage:
  python -I pubmed_ris.py --term-file query.txt --mindate 2015/01/01 --maxdate 2026/10/14 --out raw/pubmed.ris
  python -I pubmed_ris.py --term '"semaglutide"[tiab] AND obes*[tiab]' --maxdate 2026/10/14 --count-only
"""
import argparse, json, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

EU = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'


def post(endpoint, params):
    data = urllib.parse.urlencode(params).encode()
    for attempt in range(5):
        try:
            return urllib.request.urlopen(EU + endpoint, data=data, timeout=120).read()
        except Exception:
            time.sleep(2 + attempt * 2)
    raise RuntimeError('E-utilities failed: ' + endpoint)


def txt(el):
    return ''.join(el.itertext()).strip() if el is not None else ''


def ris_article(art, note):
    if art.tag == 'PubmedBookArticle':
        b = art.find('BookDocument')
        out = ['TY  - ' + ('CHAP' if b.find('ArticleTitle') is not None else 'BOOK')]
        for au in b.findall('AuthorList/Author'):
            if au.find('LastName') is not None:
                out.append('AU  - %s, %s' % (txt(au.find('LastName')), txt(au.find('ForeName'))))
        out.append('TI  - ' + (txt(b.find('ArticleTitle')) or txt(b.find('Book/BookTitle'))))
        out.append('PY  - ' + txt(b.find('Book/PubDate/Year')))
        ab = ' '.join(txt(x) for x in b.findall('Abstract/AbstractText'))
        if ab:
            out.append('AB  - ' + ab)
        out.append('AN  - PMID:' + txt(b.find('PMID')))
    else:
        m = art.find('MedlineCitation')
        a = m.find('Article')
        out = ['TY  - JOUR']
        for au in a.findall('AuthorList/Author'):
            if au.find('LastName') is not None:
                out.append('AU  - %s, %s' % (txt(au.find('LastName')), txt(au.find('ForeName'))))
            elif au.find('CollectiveName') is not None:
                out.append('AU  - ' + txt(au.find('CollectiveName')))
        out.append('TI  - ' + txt(a.find('ArticleTitle')))
        out.append('T2  - ' + txt(a.find('Journal/Title')))
        out.append('J2  - ' + txt(a.find('Journal/ISOAbbreviation')))
        ji = a.find('Journal/JournalIssue')
        year = txt(ji.find('PubDate/Year')) or txt(ji.find('PubDate/MedlineDate'))[:4]
        out.append('PY  - ' + year)
        for tag, path in (('VL', 'Volume'), ('IS', 'Issue')):
            if txt(ji.find(path)):
                out.append('%s  - %s' % (tag, txt(ji.find(path))))
        pg = txt(a.find('Pagination/MedlinePgn'))
        if pg:
            out.append('SP  - ' + pg)
        parts = []
        for x in a.findall('Abstract/AbstractText'):
            lab = x.get('Label')
            parts.append((lab + ': ' if lab else '') + txt(x))
        if parts:
            out.append('AB  - ' + ' '.join(parts))
        for eid in art.findall('PubmedData/ArticleIdList/ArticleId'):
            if eid.get('IdType') == 'doi':
                out.append('DO  - ' + txt(eid))
                out.append('UR  - https://doi.org/' + txt(eid))
        out.append('AN  - PMID:' + txt(m.find('PMID')))
        for pt in a.findall('PublicationTypeList/PublicationType'):
            out.append('M3  - ' + txt(pt))
    out.append('DB  - PubMed')
    if note:
        out.append('N1  - ' + note)
    out.append('ER  - ')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--term')
    ap.add_argument('--term-file')
    ap.add_argument('--mindate', default='1800/01/01')
    ap.add_argument('--maxdate', required=True)
    ap.add_argument('--out')
    ap.add_argument('--note', default='')
    ap.add_argument('--count-only', action='store_true')
    a = ap.parse_args()
    term = a.term or open(a.term_file, encoding='utf8').read().strip()
    r = json.loads(post('esearch.fcgi', {'db': 'pubmed', 'term': term, 'retmode': 'json', 'datetype': 'pdat',
                                         'mindate': a.mindate, 'maxdate': a.maxdate, 'retmax': 10000}))
    ids = r['esearchresult']['idlist']
    print('count', r['esearchresult']['count'])
    if a.count_only:
        return
    recs = []
    for i in range(0, len(ids), 200):
        root = ET.fromstring(post('efetch.fcgi', {'db': 'pubmed', 'id': ','.join(ids[i:i + 200]), 'retmode': 'xml'}))
        recs += root.findall('PubmedArticle') + root.findall('PubmedBookArticle')
        time.sleep(0.4)
    open(a.out, 'w', encoding='utf8').write('\n\n'.join(ris_article(x, a.note) for x in recs) + '\n')
    print('written', len(recs), a.out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
