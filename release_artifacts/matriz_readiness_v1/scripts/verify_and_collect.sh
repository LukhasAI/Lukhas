#!/usr/bin/env bash
set -euo pipefail
OUTDIR=release_artifacts/matriz_readiness_v1/verification
mkdir -p "$OUTDIR"

echo "1) Compile check" > "$OUTDIR/compile_log.txt"
python3 -m compileall . >> "$OUTDIR/compile_log.txt" 2>&1 || { echo "Compile failed" ; exit 2; }

echo "2) Ruff check (E,F)" > "$OUTDIR/ruff_ef_log.txt"
ruff check --select E,F --statistics . >> "$OUTDIR/ruff_ef_log.txt" 2>&1 || true

echo "3) Ruff full stats" > "$OUTDIR/ruff_stats.txt"
ruff check --statistics . >> "$OUTDIR/ruff_stats.txt" 2>&1 || true

echo "4) Black check" > "$OUTDIR/black_log.txt"
black --check . >> "$OUTDIR/black_log.txt" 2>&1 || true

echo "5) Smoke tests" > "$OUTDIR/smoke_test_logs.txt"
if [ -x "./scripts/run_smoke_tests.sh" ]; then
  ./scripts/run_smoke_tests.sh >> "$OUTDIR/smoke_test_logs.txt" 2>&1 || { echo "Smoke tests failed" ; exit 3; }
else
  pytest -q -m "smoke or matriz or tier1" >> "$OUTDIR/smoke_test_logs.txt" 2>&1 || { echo "Smoke tests failed" ; exit 3; }
fi

echo "Artifacts saved to $OUTDIR"
