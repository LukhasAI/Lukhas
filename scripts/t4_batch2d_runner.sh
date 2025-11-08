#!/usr/bin/env bash
set -euo pipefail

# T4 Batch 2D Runner: Generate F401 candidates (1-3 errors) and dry-run diffs
# Usage: ./scripts/t4_batch2d_runner.sh

CAND=/tmp/t4_batch2d_candidates.txt
TOP20=/tmp/t4_batch2d_top20.txt
DIFFS=/tmp/t4_batch2d_top20_diffs.txt

echo "🔍 T4 Batch 2D: Analyzing F401 candidates (1-3 errors per file)..."

# Generate candidates: files with 1-3 F401 errors
python3 - <<'PY' > $CAND
import json
import subprocess

proc = subprocess.run(
    "python3 -m ruff check --select F401 --output-format json .",
    shell=True,
    capture_output=True,
    text=True
)

data = json.loads(proc.stdout or "[]")

from collections import Counter
c = Counter(d['filename'] for d in data)

for f, n in c.most_common():
    if 1 <= n <= 3:
        print(f)
PY

TOTAL=$(wc -l < $CAND | tr -d ' ')
echo "✅ Found $TOTAL files with 1-3 F401 errors"

# Extract top 20 candidates
head -n 20 $CAND > $TOP20
echo "📋 Selected top 20 for dry-run analysis"

# Generate dry-run diffs
echo "🔬 Generating dry-run diffs..."
python3 -m ruff check --fix --select F401 --diff $(cat $TOP20) > $DIFFS 2>&1 || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ T4 Batch 2D Analysis Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Results:"
echo "  Total candidates (1-3 errors): $TOTAL files"
echo "  Top 20 candidates: $TOP20"
echo "  Dry-run diffs: $DIFFS"
echo ""
echo "Next steps:"
echo "  1. Review diffs: less $DIFFS"
echo "  2. Check for try-except patterns: grep -n 'try:' \$(cat $TOP20)"
echo "  3. Apply safe fixes package by package"
echo ""
