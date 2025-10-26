#!/usr/bin/env bash
set -euo pipefail

OUTFILE="/tmp/matriz_imports_report.txt"
echo "MATRIZ legacy import check" > "$OUTFILE"
echo "Searching repository for legacy 'matriz' imports..." >> "$OUTFILE"
echo >> "$OUTFILE"

# Perform a repository-wide grep (exclude .git, artifacts, manifests, third_party, archive, build dirs)
# Pattern matches "from matriz." and "import matriz" (word boundary).
matches=$(grep -R --exclude-dir={.git,artifacts,manifests,third_party,archive,dist,build,.pytest_cache,__pycache__} -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" . || true)

if [ -z "$matches" ]; then
  echo "No legacy 'matriz' imports found." | tee -a "$OUTFILE"
  exit 0
fi

echo "FOUND legacy 'matriz' imports:" | tee -a "$OUTFILE"
echo "$matches" | tee -a "$OUTFILE"

# If BLOCK_LEGACY is set to 1, fail the job; otherwise warn (exit 0)
if [ "${BLOCK_LEGACY:-0}" = "1" ]; then
  echo "::error::Legacy 'matriz' imports found and BLOCK_LEGACY=1. Failing job." | tee -a "$OUTFILE"
  exit 1
else
  echo "::warning::Legacy 'matriz' imports found. This CI job is currently in warning mode. To block, set BLOCK_LEGACY=1 in the workflow or repo variables." | tee -a "$OUTFILE"
  exit 0
fi
