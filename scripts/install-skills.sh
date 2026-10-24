#!/usr/bin/env bash
# Link the qestack skills into a skills folder of an agent that reads SKILL.md.
# Usage: scripts/install-skills.sh <target-skills-folder>
# Example: scripts/install-skills.sh ~/.agents/skills
set -euo pipefail
TARGET="${1:?Give the target skills folder, for example ~/.agents/skills}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$TARGET"
for d in "$HERE"/plugins/qestack/skills/*/; do
  name="$(basename "$d")"
  if [ -e "$TARGET/$name" ] && [ ! -L "$TARGET/$name" ]; then
    echo "skip $name: $TARGET/$name exists and is not a link"
    continue
  fi
  ln -sfn "$d" "$TARGET/$name"
  echo "linked $name"
done
echo "Done. Install the engine too: pipx install \"git+https://github.com/quark-sri/qestack#subdirectory=engine\""
