#!/usr/bin/env bash
set -euo pipefail

echo "[pr164_ruff_fix] Fetching PR merge ref into local branch pr-164-merge..."
# Fetch the GitHub PR merge ref into a local branch
git fetch origin pull/164/merge:refs/heads/pr-164-merge
if ! git rev-parse --verify pr-164-merge >/dev/null 2>&1; then
  echo "[pr164_ruff_fix] ERROR: pr-164-merge branch not found after fetch." >&2
  exit 1
fi

# Checkout the merge ref
git checkout pr-164-merge

echo "[pr164_ruff_fix] Ensuring ruff==0.6.9 is installed (quiet)..."
python -m pip install --upgrade pip >/dev/null
python -m pip install "ruff==0.6.9" >/dev/null

echo "[pr164_ruff_fix] Ruff version: $(ruff --version)"

TARGET=serve/ui/dashboard.py

echo "[pr164_ruff_fix] Running ruff --fix on $TARGET (merge ref)..."
# Run ruff fix; allow non-zero exit without killing script
ruff check --config pyproject.toml --fix "$TARGET" || true

echo "[pr164_ruff_fix] git status (merge ref):"
git status --porcelain || true

PATCH=scripts/pr164_merge_fix.patch

echo "[pr164_ruff_fix] Creating patch if any changes..."
git diff --no-color > "$PATCH" || true

if [ -s "$PATCH" ]; then
  echo "[pr164_ruff_fix] Patch created at $PATCH. Applying to branch chore/ci-make-check..."
  # Switch back to the feature branch and apply the patch
  git checkout chore/ci-make-check
  git apply --index "$PATCH" || true
  git add -A
  if git diff --staged --quiet; then
    echo "[pr164_ruff_fix] No staged changes after applying patch." 
  else
    echo "[pr164_ruff_fix] Committing staged changes..."
    git commit -m "style: ruff --fix import-order (apply fix from PR merge ref)"
    echo "[pr164_ruff_fix] Pushing to origin chore/ci-make-check..."
    git push origin HEAD
  fi
else
  echo "[pr164_ruff_fix] No changes from ruff --fix on merge ref; nothing to apply." 
  # Return to the original branch
  git checkout chore/ci-make-check
fi

echo "[pr164_ruff_fix] Done." 
