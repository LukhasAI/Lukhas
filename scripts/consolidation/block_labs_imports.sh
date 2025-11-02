#!/usr/bin/env bash
set -euo pipefail
fail=0
files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)
for f in $files; do
  if grep -nE '^\s*(from|import)\s+labs(\.|$)' "$f" >/dev/null; then
    echo "❌ labs import in production lane: $f"
    fail=1
  fi
done
exit $fail
