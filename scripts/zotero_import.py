"""Import into a running Zotero desktop through the connector (http://127.0.0.1:23119).

usage:
  python -I zotero_import.py selected
  python -I zotero_import.py mkcoll "1_標題摘要排除（n = 1,090）" "2_全文排除（n = 45）"
  python -I zotero_import.py import --file x.bib --target C24 [--batch 100] [--skip-existing C:/Users/<you>/Zotero]
  python -I zotero_import.py check --data-dir C:/Users/<you>/Zotero

selected  prints the currently selected collection and all collection ids.
mkcoll    creates empty sub-collections under the selected collection (tiny Zotero RDF import).
import    sends BibTeX in batches; after each batch, updateSession moves the items to --target.
          Large files take ~1.5 s per record — run in the background. Never resend a batch that timed out
          without checking Zotero first (see references/06-zotero-import.md); --skip-existing makes a rerun safe.
check     counts PRISMA IDs already in Zotero (from the notes) and lists any ID present more than once.
"""
import argparse, json, re, sys, time, urllib.request
from xml.sax.saxutils import escape

BASE = 'http://127.0.0.1:23119/connector/'
HDR = {'X-Zotero-Connector-API-Version': '3'}


def call(path, data, ctype, timeout):
    req = urllib.request.Request(BASE + path, data=data, method='POST', headers={**HDR, 'Content-Type': ctype})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')


def selected():
    _, body = call('getSelectedCollection', b'{}', 'application/json', 20)
    d = json.loads(body)
    print('selected:', d.get('id'), d.get('name'))
    for t in d.get('targets', []):
        print('  ' * t['level'] + '%s %s' % (t['id'], t['name']))
    return d


def mkcoll(names):
    rdf = ('<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
           'xmlns:z="http://www.zotero.org/namespaces/export#" xmlns:dc="http://purl.org/dc/elements/1.1/" '
           'xmlns:dcterms="http://purl.org/dc/terms/">\n')
    rdf += ''.join('<z:Collection rdf:about="#c%d"><dc:title>%s</dc:title></z:Collection>\n' % (i, escape(n)) for i, n in enumerate(names))
    rdf += '</rdf:RDF>\n'
    st, _ = call('import?session=coll-%d' % int(time.time()), rdf.encode('utf8'), 'text/plain; charset=utf-8', 60)
    print('import status', st)
    d = selected()
    for t in d.get('targets', []):
        if t['name'] in names:
            print('created', t['id'], t['name'])


def existing_ids(data_dir):
    """PRISMA IDs already in Zotero (not in trash). Copies the DB + WAL so a running Zotero is not disturbed."""
    import os, shutil, sqlite3, tempfile
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(data_dir, 'zotero.sqlite'), os.path.join(tmp, 'z.sqlite'))
    if os.path.exists(os.path.join(data_dir, 'zotero.sqlite-wal')):
        shutil.copy(os.path.join(data_dir, 'zotero.sqlite-wal'), os.path.join(tmp, 'z.sqlite-wal'))
    con = sqlite3.connect(os.path.join(tmp, 'z.sqlite'))
    ids = {}
    q = ("select n.note, coalesce(n.parentItemID, n.itemID) from itemNotes n "
         "where n.note like '%PRISMA ID:%' and coalesce(n.parentItemID, n.itemID) not in (select itemID from deletedItems)")
    for note, item in con.execute(q):
        for m in re.finditer(r'PRISMA ID:\s*([A-Z]+\d{3,5})', note):
            ids.setdefault(m.group(1), set()).add(item)
    con.close()
    shutil.rmtree(tmp, ignore_errors=True)
    return ids


def check(data_dir):
    ids = existing_ids(data_dir)
    dup = {k: v for k, v in ids.items() if len(v) > 1}
    print('PRISMA IDs in Zotero: %d; IDs present more than once: %d' % (len(ids), len(dup)))
    for k in sorted(dup)[:30]:
        print('  duplicate', k, sorted(dup[k]))
    return ids


def import_bib(path, target, batch, skip_existing=None):
    text = open(path, encoding='utf8').read().strip()
    entries = ['@' + e if not e.startswith('@') else e for e in re.split(r'\n(?=@)', text)]
    if skip_existing:
        have = existing_ids(skip_existing)
        before = len(entries)
        entries = [e for e in entries if re.match(r'@\w+\{([^,]+),', e).group(1) not in have]
        print('skip-existing: %d already in Zotero, %d to import' % (before - len(entries), len(entries)))
        if not entries:
            return
    for i in range(0, len(entries), batch):
        part = '\n\n'.join(entries[i:i + batch]) + '\n'
        ses = 'nls-%d-%d' % (int(time.time()), i)
        t0 = time.time()
        st, _ = call('import?session=' + ses, part.encode('utf8'), 'text/plain; charset=utf-8', 1800)
        st2, _ = call('updateSession', json.dumps({'sessionID': ses, 'target': target}).encode(), 'application/json', 600)
        print('%s records %d-%d import %s move %s %.0fs' % (time.strftime('%H:%M:%S'), i + 1, min(i + batch, len(entries)), st, st2, time.time() - t0), flush=True)
    print('done', len(entries))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('selected')
    ck = sub.add_parser('check', help='count PRISMA IDs already in Zotero and list duplicates')
    ck.add_argument('--data-dir', required=True, help='Zotero data directory, e.g. C:/Users/<you>/Zotero')
    m = sub.add_parser('mkcoll')
    m.add_argument('names', nargs='+')
    im = sub.add_parser('import')
    im.add_argument('--file', required=True)
    im.add_argument('--target', required=True, help='collection id such as C24')
    im.add_argument('--batch', type=int, default=100)
    im.add_argument('--skip-existing', metavar='ZOTERO_DATA_DIR', help='skip entries whose PRISMA ID is already in Zotero')
    a = ap.parse_args()
    if a.cmd == 'selected':
        selected()
    elif a.cmd == 'mkcoll':
        mkcoll(a.names)
    elif a.cmd == 'check':
        check(a.data_dir)
    else:
        import_bib(a.file, a.target, a.batch, a.skip_existing)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
