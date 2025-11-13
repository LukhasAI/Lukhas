#!/usr/bin/env bash
# Smoke test runner - wrapper for make smoke target
# Part of LUKHAS AI quality gates
# Expected runtime: ~15 seconds for 10 core smoke tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "=== LUKHAS Smoke Tests ==="
echo "Running core smoke tests with pytest marker..."
echo ""

# Run smoke tests with CI quality gates enabled
# - Tests marked with @pytest.mark.smoke
# - Fail fast on first failure (--maxfail=1)
# - Quiet output (-q)
# - Disable warnings for cleaner output
CI_QUALITY_GATES=1 python3 -m pytest -q tests/smoke -m "smoke" --maxfail=1 --disable-warnings

echo ""
echo "✅ Smoke tests passed"
