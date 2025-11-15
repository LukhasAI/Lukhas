#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
REPORT_DIR="$ROOT/reports/latest"
COV_DIR="$ROOT/reports/coverage"
mkdir -p "$REPORT_DIR" "$COV_DIR" "$COV_DIR/html"

echo "1) Running initial pytest + coverage..."
first_rc=0
if ! coverage run -m pytest --json-report --json-report-file="$REPORT_DIR/pytest-report.json" -q; then
  first_rc=$?
fi
# create JSON coverage
coverage json -o "$COV_DIR/coverage.json"
coverage html -d "$COV_DIR/html"

# 2) Generate auto tests
python3 tools/tests/generate_tests.py --sources core consciousness memory governance emotion bridge api --out tests/auto_generated || true

# 3) If new tests were generated, run tests again for consistency
echo "2) Re-running tests after auto-generated test creation..."
second_rc=0
if ! coverage run -m pytest --json-report --json-report-file="$REPORT_DIR/pytest-report.json" -q; then
  second_rc=$?
fi
coverage json -o "$COV_DIR/coverage.json"
coverage html -d "$COV_DIR/html"

echo "Done. Reports:"
ls -la "$REPORT_DIR"
ls -la "$COV_DIR"

if (( first_rc != 0 )); then
  exit "$first_rc"
fi

if (( second_rc != 0 )); then
  exit "$second_rc"
fi
