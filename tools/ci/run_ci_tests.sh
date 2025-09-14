#!/bin/bash
# LUKHAS AI CI Test Runner

set -euo pipefail

TEST_TIER=${1:-fast}
FOCUS_MODULES=${2:-""}

echo "🧪 Running LUKHAS AI tests - Tier: $TEST_TIER"

# Set up environment
export PYTHONPATH="."
export PYTHONHASHSEED="0"
export TZ="UTC"
export PYTHONDONTWRITEBYTECODE="1"

# Create reports directory
mkdir -p reports/tests

# Run tests based on tier
case "$TEST_TIER" in
    smoke)
        echo "💨 Running smoke tests..."
        pytest -m "smoke or tier1"             --maxfail=1             --timeout=30             --tb=short             --disable-warnings             --junitxml=reports/tests/junit-smoke.xml
        ;;
    fast)
        echo "⚡ Running fast test suite..."
        pytest -m "unit or tier1 or smoke"             --maxfail=5             --timeout=300             --cov=lukhas --cov=MATRIZ             --cov-report=xml:reports/tests/coverage.xml             --junitxml=reports/tests/junit-fast.xml             -n auto
        ;;
    standard)
        echo "🔬 Running standard test suite..."
        pytest -m "unit or integration or tier1"             --maxfail=10             --timeout=600             --cov=lukhas --cov=MATRIZ --cov=candidate             --cov-report=xml:reports/tests/coverage.xml             --cov-report=html:reports/tests/htmlcov             --junitxml=reports/tests/junit-standard.xml             -n auto
        ;;
    advanced)
        echo "🧬 Running advanced test suite..."
        python3 tools/ci/test_orchestrator.py --tier advanced
        ;;
    *)
        echo "❌ Unknown test tier: $TEST_TIER"
        echo "Available tiers: smoke, fast, standard, advanced"
        exit 1
        ;;
esac

echo "✅ Test execution completed successfully!"
