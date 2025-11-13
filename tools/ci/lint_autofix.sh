#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# codes we consider safe to autofix via ruff/isort
AUTOFIX_CODES="I001,F401,SIM102,RUF001,RUF006,RUF012"

# 1) Run isort
echo "Running isort..."
# Only run where pyproject defines isort or run globally
isort . || echo "isort not configured, skipping"

# 2) Run ruff autofix for selected codes (this will edit files)
echo "Running ruff --fix for autofixable codes..."
python3 -m ruff check --fix --select $AUTOFIX_CODES || true

# 3) Run ruff again to see remaining issues
echo "Collecting remaining issues..."
python3 -m ruff check --select $AUTOFIX_CODES --output-format json > /tmp/ruff_post_fix.json || true

# 4) If there were changes, create a PR
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "chore(t4): apply autofix (ruff/isort) for lint-platform"
  BRANCH="t4-lint-autofix-$(date +%s)"
  git checkout -b "$BRANCH"
  git push --set-upstream origin "$BRANCH"
  if command -v gh >/dev/null 2>&1; then
    gh pr create --title "chore(t4): autofix lint issues (ruff/isort)" --body "Autofix PR from T4 Lint Platform: ruff/isort changes. Please review." --base main
  else
    echo "Autofix branch created: $BRANCH. Please open a PR manually."
  fi
else
  echo "No changes from autofix."
fi

# 5) Run annotator for remaining codes (dry-run)
python3 tools/ci/lint_annotator.py --paths lukhas core api consciousness memory identity MATRIZ --codes "F821,F403,B904,B008,B018,RUF012,RUF006,E701,E702,E402,F811,B007,SIM117,SIM105,SIM115" --dry-run
