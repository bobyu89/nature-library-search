"""Rebuild export files from @@CHUNK dumps that the harness saved into tool-results/.

usage: python -I collect_chunks.py <tool-results dir> <out dir> [--group emb]
Each dump is '@@CHUNK <group> <i>\n<text>' (last one padded with x…@@PAD); the joined text holds
'@@FILE <name>\n<content>\n@@END\n' blocks. See references/03-browser-data-out.md.
"""
import argparse, glob, json, os, re, sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tool_results')
    ap.add_argument('out')
    ap.add_argument('--group', help='only rebuild this group')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    chunks = {}
    for f in glob.glob(os.path.join(a.tool_results, 'mcp-Claude_Browser-javascript_tool-*.txt')):
        try:
            t = json.load(open(f, encoding='utf8'))[0]['text']
        except Exception:
            continue
        t = re.sub(r'\n\n\(captured at origin [^)]*\)\s*$', '', t)
        try:
            s = json.loads(t)
        except Exception:
            continue
        if not isinstance(s, str):
            continue
        m = re.match(r'@@CHUNK (?:([A-Za-z]\w*) )?(\d+)\n', s)
        if not m:
            continue
        g = m.group(1) or 'g0'
        if a.group and g != a.group:
            continue
        body = re.sub(r'x+@@PAD$', '', s[m.end():])
        chunks.setdefault(g, {})[int(m.group(2))] = (os.path.getmtime(f), body)
    for g, parts in chunks.items():
        keys = sorted(parts)
        if keys != list(range(len(keys))):
            print('group %s: missing chunks, have %s' % (g, keys))
            continue
        full = ''.join(parts[k][1] for k in keys)
        for name, content in re.findall(r'@@FILE (\S+)\n(.*?)\n@@END\n', full, re.S):
            open(os.path.join(a.out, name), 'w', encoding='utf8').write(content)
            n = len(re.findall(r'^TY  -', content, re.M))
            if name.endswith('.json'):
                try:
                    n = len(json.loads(content))
                except Exception:
                    n = '?'
            print(g, name, len(content), 'records', n)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
