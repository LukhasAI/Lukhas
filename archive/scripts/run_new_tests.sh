#!/usr/bin/env bash
# Test Coverage Runner
# Quick script to set up environment and run new test suites

set -e

echo "🧪 LUKHAS Test Coverage Improvement - Quick Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "core" ]; then
    echo "❌ Error: Must run from LUKHAS repository root"
    exit 1
fi

echo "📦 Step 1: Setting up clean Python environment..."
if [ ! -d ".venv_test" ]; then
    echo "Creating new virtual environment: .venv_test"
    python3 -m venv .venv_test
else
    echo ".venv_test already exists, using it"
fi

echo ""
echo "📦 Step 2: Installing dependencies..."
source .venv_test/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
pip install --quiet pytest pytest-cov pytest-asyncio pytest-mock

echo ""
echo "✅ Environment ready!"
echo ""

echo "🧪 Step 3: Running new test suites..."
echo ""

echo "Testing: core/agent_tracer.py"
echo "------------------------------"
pytest tests/unit/core/test_agent_tracer.py -v --tb=short

echo ""
echo "Testing: core/minimal_actor.py"
echo "------------------------------"
pytest tests/unit/core/test_minimal_actor.py -v --tb=short

echo ""
echo "📊 Step 4: Generating coverage reports..."
echo ""

echo "Coverage for core/agent_tracer.py:"
echo "-----------------------------------"
pytest tests/unit/core/test_agent_tracer.py \
    --cov=core.agent_tracer \
    --cov-report=term-missing:skip-covered \
    --tb=no \
    -q

echo ""
echo "Coverage for core/minimal_actor.py:"
echo "------------------------------------"
pytest tests/unit/core/test_minimal_actor.py \
    --cov=core.minimal_actor \
    --cov-report=term-missing:skip-covered \
    --tb=no \
    -q

echo ""
echo "✅ Test run complete!"
echo ""
echo "📈 Summary:"
echo "  - Test files: 2"
echo "  - Test cases: 63+"
echo "  - Modules tested: core/agent_tracer.py, core/minimal_actor.py"
echo ""
echo "💡 Next steps:"
echo "  1. Review test output above"
echo "  2. Check coverage reports"
echo "  3. Fix any failures"
echo "  4. Commit tests: git add tests/unit/core/test_*.py"
echo ""
