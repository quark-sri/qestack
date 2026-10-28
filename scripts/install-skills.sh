#!/usr/bin/env bash
# Install the qestack skills for AI coding agents that read SKILL.md.
#
# Usage:
#   scripts/install-skills.sh --agent <name>|all (--user | --project <repo>) [--copy] [--library-only]
#   scripts/install-skills.sh <target-skills-folder>     (old form: links the source skills into one folder)
#
# The --agent form installs the portable packages from dist/skills/. It builds them first (needs python3).
# The skill folders come from the official documentation of each agent (docs/other-agents.md, 2026-10-27).
# Works with bash 3.2 (macOS) and later.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS="claude codex cursor copilot gemini antigravity devin opencode cline"

usage() {
  cat <<EOF
Install the qestack skills for an AI coding agent.

Usage:
  $0 --agent <name>|all (--user | --project <repo>) [--copy] [--library-only]
  $0 <target-skills-folder>

Options:
  --agent <name>    one of: $AGENTS, or all
                    (all: every agent except claude; Claude Code gets the skills from the qestack plugin)
  --user            install for your user (all projects)
  --project <repo>  install into one repository
  --copy            copy the skills (default: symbolic links to dist/skills/; on Windows, use --copy)
  --library-only    install only the 39 library skills, not the gated skills (qestack, qe-*)
  -h, --help        show this help

Skill folders:
  agent        project              user
  claude       .claude/skills       ~/.claude/skills
  codex        .agents/skills       ~/.agents/skills
  cursor       .agents/skills       ~/.agents/skills
  copilot      .agents/skills       ~/.agents/skills
  gemini       .agents/skills       ~/.agents/skills
  antigravity  .agents/skills       ~/.gemini/antigravity-cli/skills and ~/.gemini/config/skills
  devin        .agents/skills       ~/.agents/skills
  opencode     .agents/skills       ~/.agents/skills
  cline        .cline/skills        ~/.cline/skills

Links point to dist/skills/ of this clone. After git pull, run the same command again to rebuild them.
EOF
}

# The skill folders of one agent, one for each line. $1: agent, $2: user or project.
folders() {
  case "$1:$2" in
    claude:user) echo "$HOME/.claude/skills" ;;
    claude:project) echo ".claude/skills" ;;
    cline:user) echo "$HOME/.cline/skills" ;;
    cline:project) echo ".cline/skills" ;;
    antigravity:user) echo "$HOME/.gemini/antigravity-cli/skills"; echo "$HOME/.gemini/config/skills" ;;
    *:user) echo "$HOME/.agents/skills" ;;
    *:project) echo ".agents/skills" ;;
  esac
}

gated() { [ "$1" = "qestack" ] || [ "${1#qe-}" != "$1" ]; }

# Install the skills of $1 (a folder of skill folders) into $2. $3: link or copy.
install_into() {
  local from="$1" target="$2" mode="$3" n=0 d name dst
  mkdir -p "$target"
  for d in "$from"/*/; do
    name="$(basename "$d")"
    if [ "$LIBRARY_ONLY" = 1 ] && gated "$name"; then
      continue
    fi
    dst="$target/$name"
    if [ -e "$dst" ] && [ ! -L "$dst" ] && ! grep -qs "source: https://github.com/quark-sri/qestack" "$dst/SKILL.md"; then
      echo "skip $name: $dst exists and is not a qestack skill"
      continue
    fi
    rm -rf "$dst"
    if [ "$mode" = copy ]; then
      cp -R "${d%/}" "$dst"
    else
      ln -s "${d%/}" "$dst"
    fi
    n=$((n + 1))
  done
  echo "$target: $n skills (${mode})"
}

# Old form: one target folder, links to the source skills.
if [ $# -eq 1 ] && [ "${1#-}" = "$1" ]; then
  TARGET="$1"
  mkdir -p "$TARGET"
  for d in "$HERE"/plugins/*/skills/*/; do
    name="$(basename "$d")"
    if [ -e "$TARGET/$name" ] && [ ! -L "$TARGET/$name" ]; then
      echo "skip $name: $TARGET/$name exists and is not a link"
      continue
    fi
    ln -sfn "$d" "$TARGET/$name"
    echo "linked $name"
  done
  echo "Done. The library skills work without the engine. The gated skills (qestack, qe-*) also need the engine:"
  echo "  pipx install \"git+https://github.com/quark-sri/qestack#subdirectory=engine\""
  exit 0
fi

AGENT="" SCOPE="" PROJECT="" MODE=link LIBRARY_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="${2:-}"; shift 2 || { usage >&2; exit 2; } ;;
    --user) SCOPE=user; shift ;;
    --project) SCOPE=project; PROJECT="${2:-}"; shift 2 || { usage >&2; exit 2; } ;;
    --copy) MODE=copy; shift ;;
    --library-only) LIBRARY_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

LIST=""
[ "$AGENT" = all ] && LIST="${AGENTS#claude }"
for a in $AGENTS; do
  [ "$a" = "$AGENT" ] && LIST="$a"
done
if [ -z "$LIST" ]; then
  echo "unknown agent: '${AGENT}'. Use one of: $AGENTS, or all" >&2
  exit 2
fi
if [ -z "$SCOPE" ] || { [ "$SCOPE" = project ] && [ ! -d "$PROJECT" ]; }; then
  echo "give --user, or --project with an existing repository folder" >&2
  exit 2
fi

command -v python3 >/dev/null || { echo "python3 is needed to build dist/skills/" >&2; exit 1; }
python3 "$HERE/scripts/build_skills.py" --out "$HERE/dist" >/dev/null

DONE=""
for a in $LIST; do
  while IFS= read -r f; do
    [ "$SCOPE" = project ] && f="$(cd "$PROJECT" && pwd)/$f"
    case " $DONE " in *" $f "*) continue ;; esac  # agents that share one folder get one install
    DONE="$DONE $f"
    install_into "$HERE/dist/skills" "$f" "$MODE"
  done <<EOF
$(folders "$a" "$SCOPE")
EOF
done

case " $LIST " in *" claude "*)
  echo "Note: if the qestack Claude Code plugin is also installed, Claude Code shows each skill two times." ;;
esac
if [ "$LIBRARY_ONLY" = 0 ]; then
  echo "The gated skills (qestack, qe-*) also need the engine:"
  echo "  pipx install \"git+https://github.com/quark-sri/qestack#subdirectory=engine\""
fi
