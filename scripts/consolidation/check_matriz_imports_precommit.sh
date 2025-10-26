#!/usr/bin/env bash
set -euo pipefail

# Inspect staged files (Added/Copied/Modified)
STAGED=$(git diff --cached --name-only --diff-filter=ACM || true)
if [ -z "$STAGED" ]; then
  exit 0
fi

FOUND=0
echo "Checking staged Python files for legacy 'matriz' imports..."

# iterate staged files
while IFS= read -r file; do
  # Skip artifact/build directories
  case "$file" in
    artifacts/*|manifests/*|third_party/*|archive/*|dist/*|build/*|.pytest_cache/*|__pycache__/*)
      continue
      ;;
  esac

  # Only check Python files
  case "$file" in
    *.py)
      # Get staged content for the file; fall back if not available
      if ! content=$(git show :"$file" 2>/dev/null); then
        continue
      fi
      # Check for matches
      if echo "$content" | grep -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" >/dev/null; then
        echo "Legacy 'matriz' import found in staged file: $file"
        echo "Matching lines:"
        echo "$content" | grep -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" | sed 's/^/  /'
        FOUND=1
      fi
      ;;
    *) ;;
  esac
done <<< "$STAGED"

if [ "$FOUND" -eq 1 ]; then
  if [ "${PRE_COMMIT_BLOCK_MATRIZ:-0}" = "1" ]; then
    echo "Blocking commit: legacy 'matriz' imports detected and PRE_COMMIT_BLOCK_MATRIZ=1"
    exit 1
  else
    echo "Warning: legacy 'matriz' imports detected in staged files. To block commits, set PRE_COMMIT_BLOCK_MATRIZ=1 in your environment."
    # Return 0 so the hook is warning by default.
    exit 0
  fi
fi

exit 0
