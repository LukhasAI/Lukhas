#!/bin/bash
# Memory Safety, Interleavings & Slow Tests Runner
#
# This script runs the combined test suite for:
# - memory_safety: Property-based invariants for memory systems
# - memory_interleavings: Concurrency and race condition testing
# - slow: Long-running validation and stress tests
#
# Usage: ./scripts/run_memory_slow_tests.sh

set -e

echo "🧠 Memory Safety, Interleavings & Slow Tests Runner"
echo "=================================================="

# Set environment for memory testing
export LUKHAS_LANE=candidate
export LUKHAS_PERF=1
export PYTHONPATH=.

# Check if we're in the right directory
if [ ! -f "pytest.ini" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "🔧 Environment:"
echo "  LUKHAS_LANE: $LUKHAS_LANE"
echo "  LUKHAS_PERF: $LUKHAS_PERF"
echo "  PYTHONPATH: $PYTHONPATH"
echo ""

echo "🧪 Running combined test command:"
echo "  pytest -m 'memory_safety or memory_interleavings or slow'"
echo ""

# Run the combined test command
pytest -m "memory_safety or memory_interleavings or slow" -v --tb=short --timeout=600

echo ""
echo "✅ Memory safety, interleavings, and slow test suite completed!"
echo ""
echo "📋 Test Categories:"
echo "  🧠 memory_safety: Property-based invariants for memory systems"
echo "  🔄 memory_interleavings: Concurrency and race condition testing"
echo "  ⏳ slow: Long-running validation and stress tests"