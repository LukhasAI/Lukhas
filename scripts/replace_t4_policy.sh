#!/usr/bin/env bash
set -euo pipefail

MAIN_BRANCH="main"
BRANCH="replace/t4-policy-platform-$(date +%Y%m%d%H%M%S)"
git checkout -b "$BRANCH"

# Backup old docs (if present)
mkdir -p docs/backup_t4 || true
if [ -f docs/development/T4_UNUSED_IMPORTS_SYSTEM.md ]; then
  git mv -f docs/development/T4_UNUSED_IMPORTS_SYSTEM.md docs/backup_t4/ || true
fi
if [ -f docs/T4_UNUSED_IMPORTS_GUIDE.md ]; then
  git mv -f docs/T4_UNUSED_IMPORTS_GUIDE.md docs/backup_t4/ || true
fi

# Replace tools (backup old versions)
if [ -f tools/ci/unused_imports.py ]; then
  git mv -f tools/ci/unused_imports.py tools/ci/unused_imports_old.py || true
fi
if [ -f tools/ci/check_unused_imports_todo.py ]; then
  git mv -f tools/ci/check_unused_imports_todo.py tools/ci/check_unused_imports_todo_old.py || true
fi

# Move new versions into place
git mv -f tools/ci/unused_imports_new.py tools/ci/unused_imports.py
git mv -f tools/ci/check_unused_imports_todo_new.py tools/ci/check_unused_imports_todo.py

# Add new files
git add docs/policies/T4_UNUSED_IMPORTS_PLATFORM.md
git add tools/ci/intent_registry.py
git add .github/workflows/t4-policy-validation.yml
git add .github/PULL_REQUEST_TEMPLATE/t4_policy.md
git add scripts/replace_t4_policy.sh

git commit -m "chore(t4): replace unused-imports policy with T4 Platform; structured annotations and tooling"
git push --set-upstream origin "$BRANCH"

# Create PR (requires GitHub CLI `gh` authenticated)
if command -v gh >/dev/null 2>&1; then
  gh pr create --title "Replace T4 unused-imports policy with T4 Platform" --body-file .github/PULL_REQUEST_TEMPLATE/t4_policy.md --base "$MAIN_BRANCH"
else
  echo "gh CLI not found. Created branch '$BRANCH' and pushed. Please open a PR manually."
fi
