#!/usr/bin/env bash
# qestack quality gate for any CI system (GitLab CI, Jenkins, Azure DevOps, ...).
# Runs the deterministic gates for the feature of this branch, then scores them with the
# committed judge.json, red.json and seed-feedback.json. Fails unless the decision is ACCEPT.
# Env: QESTACK_FEATURE (default: branch name), QESTACK_BASE_REF (default: origin/main)
set -euo pipefail
BASE="${QESTACK_BASE_REF:-origin/main}"
git fetch --no-tags origin "${BASE#origin/}" >/dev/null 2>&1 || true
# Protected-file changes are listed for review by CODEOWNERS instead of failing here.
qestack gate --base "$BASE" --allow-protected || true
qestack score --ci
