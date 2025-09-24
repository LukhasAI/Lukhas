#!/bin/bash
"""
Memory System Production Load Test Runner

Runs comprehensive load tests for memory systems with different configurations.

Usage:
    ./scripts/run_memory_load_test.sh [scale] [environment]

Examples:
    ./scripts/run_memory_load_test.sh 1000 development    # Light load
    ./scripts/run_memory_load_test.sh 10000 staging       # Heavy load
    ./scripts/run_memory_load_test.sh 50000 production    # Production-scale test

Environment presets:
    development: 1,000 operations, basic validation
    staging: 10,000 operations, performance validation
    production: 50,000 operations, full SLO validation
"""

set -e

# Default values
SCALE=${1:-1000}
ENVIRONMENT=${2:-development}

# Environment presets
case $ENVIRONMENT in
    "development")
        SCALE=${SCALE:-1000}
        TIMEOUT="300"  # 5 minutes
        ;;
    "staging")
        SCALE=${SCALE:-10000}
        TIMEOUT="900"  # 15 minutes
        ;;
    "production")
        SCALE=${SCALE:-50000}
        TIMEOUT="1800" # 30 minutes
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        echo "Supported environments: development, staging, production"
        exit 1
        ;;
esac

echo "🚀 Starting Memory System Load Test"
echo "=================================="
echo "Scale: $SCALE operations"
echo "Environment: $ENVIRONMENT"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Set environment variables
export MEMORY_LOAD_SCALE=$SCALE
export LUKHAS_LANE=$ENVIRONMENT
export PYTHONPATH="${PYTHONPATH:-}:."

# Create reports directory
mkdir -p reports/performance/memory

# Run the load tests
echo "🔍 Running memory system load tests..."
timeout ${TIMEOUT}s python -m pytest \
    tests/performance/test_memory_production_load.py \
    -v \
    --tb=short \
    --durations=10 \
    --junitxml=reports/performance/memory/load_test_results.xml \
    --html=reports/performance/memory/load_test_report.html \
    --self-contained-html \
    2>&1 | tee reports/performance/memory/load_test_output.log

TEST_EXIT_CODE=$?

echo ""
echo "📊 Load Test Summary"
echo "==================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Memory system load test PASSED"
    echo "All SLO targets met under $ENVIRONMENT load conditions"
else
    echo "❌ Memory system load test FAILED"
    echo "Performance degradation or SLO violations detected"
fi

echo ""
echo "Results saved to:"
echo "  - XML: reports/performance/memory/load_test_results.xml"
echo "  - HTML: reports/performance/memory/load_test_report.html"
echo "  - Log: reports/performance/memory/load_test_output.log"

# Generate system info report
echo ""
echo "📈 System Information"
echo "===================="
echo "CPU: $(nproc) cores"
echo "Memory: $(free -h | awk '/^Mem:/{print $2}') total"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo "Python Version: $(python --version 2>&1)"

# Check for performance issues
if [ -f "reports/performance/memory/load_test_output.log" ]; then
    echo ""
    echo "🔍 Performance Issue Analysis"
    echo "============================"

    # Check for SLO violations
    SLO_VIOLATIONS=$(grep -c "exceeds.*SLO" reports/performance/memory/load_test_output.log || echo "0")
    if [ "$SLO_VIOLATIONS" -gt "0" ]; then
        echo "⚠️ Found $SLO_VIOLATIONS SLO violations:"
        grep "exceeds.*SLO" reports/performance/memory/load_test_output.log || true
    fi

    # Check for errors
    ERROR_COUNT=$(grep -c "FAIL\|ERROR\|Failed" reports/performance/memory/load_test_output.log || echo "0")
    if [ "$ERROR_COUNT" -gt "0" ]; then
        echo "⚠️ Found $ERROR_COUNT error messages:"
        grep "FAIL\|ERROR\|Failed" reports/performance/memory/load_test_output.log | head -5 || true
    fi

    if [ "$SLO_VIOLATIONS" -eq "0" ] && [ "$ERROR_COUNT" -eq "0" ]; then
        echo "✅ No performance issues detected"
    fi
fi

echo ""
echo "🎯 Load Test Complete"
echo "Exit Code: $TEST_EXIT_CODE"

exit $TEST_EXIT_CODE