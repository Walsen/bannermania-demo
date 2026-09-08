#!/usr/bin/env bash
#
# Installs the project's versioned git hooks (.githooks/) by pointing
# core.hooksPath at that directory, and creates a detect-secrets baseline
# if one doesn't exist yet.
#
# Run once per clone:
#   ./scripts/install-git-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "Configuring git to use .githooks/ ..."
git config core.hooksPath .githooks
chmod +x .githooks/pre-push scripts/check_pii.py

if [ ! -f .secrets.baseline ]; then
  echo "Creating initial .secrets.baseline ..."
  if command -v uv >/dev/null 2>&1; then
    uv run detect-secrets scan --exclude-files '\.venv/' --exclude-files '\.devbox/' --exclude-files 'uv\.lock' --exclude-files '\.git/' > .secrets.baseline
  else
    detect-secrets scan --exclude-files '\.venv/' --exclude-files '\.devbox/' --exclude-files 'uv\.lock' --exclude-files '\.git/' > .secrets.baseline
  fi
  echo "Created .secrets.baseline — review it and commit it."
else
  echo ".secrets.baseline already exists, leaving as-is."
fi

echo "Done. The pre-push quality gate (lint, tests, secrets, PII) will now run on 'git push'."
echo "Bypass in an emergency with: git push --no-verify"
