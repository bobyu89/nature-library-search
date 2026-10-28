"""Reproducibility package: zip the work folder with a SHA-256 manifest and a README of what each file is.

usage: python -I archive.py --work WORK --out D:/project/search_package_sema_20261028.zip [--exclude fulltext]

Full-text PDFs are excluded by default (copyright); exports, logs, decisions and scripts are included.
The manifest (MANIFEST.sha256) lets a reviewer verify nothing changed after submission (e.g. deposit on OSF).
"""
import argparse, hashlib, json, os, sys, time, zipfile

SKILL_SCRIPTS = os.path.dirname(os.path.abspath(__file__))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--exclude', action='append', default=['fulltext', 'batches', '__pycache__'])
    a = ap.parse_args()
    files = []
    for root, dirs, names in os.walk(a.work):
        dirs[:] = [d for d in dirs if d not in a.exclude]
        for n in names:
            p = os.path.join(root, n)
            if os.path.abspath(p) != os.path.abspath(a.out):
                files.append(p)
    manifest = []
    with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            rel = os.path.relpath(p, a.work).replace('\\', '/')
            z.write(p, 'work/' + rel)
            manifest.append('%s  work/%s' % (sha(p), rel))
        for n in sorted(os.listdir(SKILL_SCRIPTS)):
            if n.endswith('.py'):
                p = os.path.join(SKILL_SCRIPTS, n)
                z.write(p, 'scripts/' + n)
                manifest.append('%s  scripts/%s' % (sha(p), n))
        z.writestr('MANIFEST.sha256', '\n'.join(manifest) + '\n')
        z.writestr('README.txt', 'Search reproducibility package created %s by nature-library-search.\n'
                   'work/raw: database exports; records_*.json: deduplicated records; decisions*/: screening decisions;\n'
                   'screen_*.json/counts_*.json: merged screening state and PRISMA numbers; searches_*.json: search log;\n'
                   'scripts/: the exact code used. Verify with: sha256sum -c MANIFEST.sha256 (after unzipping).\n' % time.strftime('%Y-%m-%d'))
    print(json.dumps({'files': len(manifest), 'zip': a.out}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
