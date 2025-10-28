#!/usr/bin/env bash
set -euo pipefail

# Block accidental new `labs` imports in production lanes during commits.
fail=0
files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)
if [ -z "$files" ]; then
  exit 0
fi
while IFS= read -r file; do
  # Only check files in production lanes
  if echo "$file" | grep -Eq '^(core|MATRIZ|lukhas|governance|bio)/'; then
    if grep -nE "^\s*(from|import)\s+labs(\.|$)" "$file" >/dev/null 2>&1; then
      echo "❌ labs import found in production lane: $file"
      fail=1
    fi
  fi
done <<< "$files"

exit $fail
