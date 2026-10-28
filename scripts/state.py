"""Pipeline state for resuming after interruptions (session end, context reset, scratchpad purge).

usage:
  python -I state.py init --work "G:/.../project/search_sema" --topic sema --question "..."
  python -I state.py mark --work WORK --stage export:embase --note "762 records, pinned to 2026-10-14" [--file raw/embase_sema.ris]
  python -I state.py show --work WORK

Stages (in order): strategy, login, export:<db> (one per database), seed-check, dedup, pilot, screening-A,
screening-B, adjudication, fulltext, merge, outputs, zotero, archive.
`show` prints what is done, the recorded counts/notes, and verifies the SHA-256 of every registered file —
a changed or missing file is flagged so you know which stage to redo. Keep WORK in the user's project folder
(cloud drive), never only in the scratchpad: the scratchpad can be purged between sessions.
"""
import argparse, hashlib, json, os, sys, time

ORDER = ['strategy', 'login', 'export', 'seed-check', 'dedup', 'pilot', 'screening-A', 'screening-B', 'adjudication',
         'fulltext', 'merge', 'outputs', 'zotero', 'archive']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def path(work):
    return os.path.join(work, 'pipeline_state.json')


def load(work):
    p = path(work)
    return json.load(open(p, encoding='utf8')) if os.path.exists(p) else None


def save(work, st):
    json.dump(st, open(path(work), 'w', encoding='utf8'), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init')
    i.add_argument('--work', required=True)
    i.add_argument('--topic', required=True)
    i.add_argument('--question', default='')
    m = sub.add_parser('mark')
    m.add_argument('--work', required=True)
    m.add_argument('--stage', required=True)
    m.add_argument('--note', default='')
    m.add_argument('--file', action='append', default=[])
    s = sub.add_parser('show')
    s.add_argument('--work', required=True)
    a = ap.parse_args()
    if a.cmd == 'init':
        os.makedirs(a.work, exist_ok=True)
        for d in ('raw', 'decisions', 'decisions_B', 'fulltext', 'out'):
            os.makedirs(os.path.join(a.work, d), exist_ok=True)
        st = load(a.work) or {'topic': a.topic, 'question': a.question, 'created': time.strftime('%Y-%m-%d %H:%M'), 'stages': {}}
        save(a.work, st)
        print('initialised', path(a.work))
    elif a.cmd == 'mark':
        st = load(a.work)
        if st is None:
            sys.exit('run init first')
        files = {f: sha(os.path.join(a.work, f)) for f in a.file}
        st['stages'][a.stage] = {'done': time.strftime('%Y-%m-%d %H:%M'), 'note': a.note, 'files': files}
        save(a.work, st)
        print('marked', a.stage)
    else:
        st = load(a.work)
        if st is None:
            sys.exit('no pipeline_state.json in ' + a.work)
        print('topic:', st['topic'], '|', st.get('question', ''))
        key = lambda k: (ORDER.index(k.split(':')[0]) if k.split(':')[0] in ORDER else 99, k)
        for k in sorted(st['stages'], key=key):
            v = st['stages'][k]
            flags = []
            for f, h in v['files'].items():
                p = os.path.join(a.work, f)
                flags.append('%s %s' % (f, 'ok' if os.path.exists(p) and sha(p) == h else 'CHANGED/MISSING'))
            print('✓ %-14s %s  %s  %s' % (k, v['done'], v['note'], '; '.join(flags)))
        done = {k.split(':')[0] for k in st['stages']}
        nxt = next((s for s in ORDER if s not in done), None)
        print('next stage:', nxt or 'all done')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
