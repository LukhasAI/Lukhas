#!/usr/bin/env bash
# Verification steps for v0.9.1-syntax-zero release
set -euo pipefail

echo "=== Syntax Zero Verification Suite ==="
echo "Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# 1. Compile check
echo "1. Python compilation check..."
python3 -m compileall -q . 2>&1 | tee release_artifacts/compile_check.log
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ Compilation: PASS (0 syntax errors)"
else
    echo "❌ Compilation: FAIL"
    exit 1
fi

# 2. Ruff syntax/pyflakes check
echo ""
echo "2. Ruff E,F checks (syntax + pyflakes)..."
ruff check --select E,F --statistics . 2>&1 | tee release_artifacts/ruff_ef_check.log
echo "✅ Ruff E,F check complete"

# 3. Ruff full statistics
echo ""
echo "3. Ruff full statistics..."
ruff check --statistics . 2>&1 | tee release_artifacts/ruff_full_stats.log

# 4. Black format check
echo ""
echo "4. Black format check..."
black --check . 2>&1 | tee release_artifacts/black_check.log || true
echo "✅ Black check complete"

# 5. Smoke tests
echo ""
echo "5. Running smoke tests..."
if [ -f "scripts/run_smoke_tests.sh" ]; then
    bash scripts/run_smoke_tests.sh 2>&1 | tee release_artifacts/smoke_tests.log
else
    make smoke 2>&1 | tee release_artifacts/smoke_tests.log
fi

echo ""
echo "=== Verification Complete ==="
echo "Finished: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "Artifacts saved to: release_artifacts/"
