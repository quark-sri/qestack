#!/usr/bin/env bash
# One-step install of qestack: the engine (qestack command) and the Claude Code plugin.
# Usage: scripts/install.sh [--skills-only]
#   --skills-only  install only the plugin, without the engine (no Python needed).
#                  The library skills work. The gated qe-* skills ask for the engine.
set -euo pipefail
REPO="quark-sri/qestack"
SKILLS_ONLY=0
[ "${1:-}" = "--skills-only" ] && SKILLS_ONLY=1

if [ "$SKILLS_ONLY" = 0 ]; then
  SPEC="git+https://github.com/$REPO#subdirectory=engine"
  if command -v pipx >/dev/null 2>&1; then pipx install --force "$SPEC"
  elif command -v uv >/dev/null 2>&1; then uv tool install --force "$SPEC"
  else
    echo "Install pipx or uv first (Python 3.11 or later is needed), then run this script again." >&2
    exit 1
  fi
  qestack --version
fi

if command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add "$REPO"
  claude plugin install qestack@qestack
else
  echo "Claude Code not found. In Claude Code, run:"
  echo "  /plugin marketplace add $REPO"
  echo "  /plugin install qestack@qestack"
fi

[ "$SKILLS_ONLY" = 0 ] && echo "Done. In your repository run: qestack init   (use --existing for an existing codebase), then /qe-setup in Claude Code."
[ "$SKILLS_ONLY" = 1 ] && echo "Done. In Claude Code, ask: 'which QA skill should I use?' (qa-navigator)."
exit 0
