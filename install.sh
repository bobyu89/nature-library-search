#!/usr/bin/env bash
# Install nature-library-search for Claude Code and/or Codex (macOS / Linux / Git Bash).
# Usage: bash install.sh [both|claude|codex]
# The repo folder stays the single source: each carrier's skills folder gets a symlink to it.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME=nature-library-search
TARGET="${1:-both}"
dests=()
[[ "$TARGET" == both || "$TARGET" == claude ]] && dests+=("$HOME/.claude/skills")
[[ "$TARGET" == both || "$TARGET" == codex ]] && dests+=("$HOME/.codex/skills")
for d in "${dests[@]}"; do
  mkdir -p "$d"
  link="$d/$NAME"
  if [[ "$(cd "$d" && pwd)/$NAME" == "$SRC" ]]; then echo "already the source: $link"; continue; fi
  if [[ -L "$link" ]]; then echo "already linked: $link"; continue; fi
  if [[ -e "$link" ]]; then echo "WARNING: $link exists and is not a link; leaving it alone" >&2; continue; fi
  ln -s "$SRC" "$link" && echo "linked $link -> $SRC"
done
python3 -c "import matplotlib" 2>/dev/null || echo "WARNING: pip install matplotlib (needed for PRISMA diagrams)"
echo 'Next: copy config/library.template.yaml to config/library.<yours>.yaml and point manifest.yaml at it.'
