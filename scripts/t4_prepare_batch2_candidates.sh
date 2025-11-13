#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/t4_batch2_candidates.txt

if [ -f F401_UNUSED_IMPORTS_REPORT.json ]; then
  jq -r '.categories.functions[].file' F401_UNUSED_IMPORTS_REPORT.json | sort | uniq -c | sort -rn | awk '{print $2}' > $OUT
else
  python3 -m ruff check --select F401 --output-format json . > /tmp/ruff_f401.json
  jq -r '.[].filename' /tmp/ruff_f401.json | sort | uniq -c | sort -rn | awk '{print $2}' > $OUT
fi

echo "Candidates written to $OUT"
head -n 40 $OUT
