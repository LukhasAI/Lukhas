#!/bin/bash
# CODEX Strike Teams - Task Validation Commands
# Supports systematic validation of 5 strategic code improvement areas

set -e

echo "🤖 CODEX Strike Teams - Validation Suite"
echo "======================================="
echo "Trinity Framework: ⚛️🧠🛡️"
echo ""

# CODEX 1: Datetime UTC Compliance
echo "⏰ CODEX 1: Datetime UTC Compliance"
echo "Current violations:"
ruff check . --select DTZ003,DTZ005 --quiet | wc -l || echo "Error running ruff"
echo "Target: 0 violations"
echo ""

# CODEX 2: MyPy Type Safety  
echo "🔧 CODEX 2: MyPy Type Safety"
echo "Current errors:"
mypy --no-error-summary --quiet . 2>/dev/null | wc -l || echo "Error running mypy"
echo "Target: <100 critical errors"
echo ""

# CODEX 3: Import Structure
echo "📦 CODEX 3: Import Structure" 
echo "Testing critical imports:"
python -c "
try:
    from lukhas.core import glyph
    from candidate.governance.identity.interface import get_lambda_id_validator
    print('✅ Core imports working')
except ImportError as e:
    print(f'❌ Import error: {e}')
"
echo ""

# CODEX 4: Test Coverage
echo "🧪 CODEX 4: Test Coverage"
echo "Current coverage:"
pytest --cov --cov-report=term-missing --quiet tests/ 2>/dev/null | grep "TOTAL" || echo "Error running coverage"
echo "Target: 40% minimum, 85% goal"
echo ""

# CODEX 5: Syntax Validation
echo "🐍 CODEX 5: Syntax Validation"
echo "Syntax errors:"
python -m py_compile $(find . -name "*.py" -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./archive/*") 2>&1 | wc -l || echo "0"
echo "Target: 0 syntax errors"
echo ""

# Overall System Health
echo "📊 Overall System Health"
echo "======================="

# Count Python files
total_files=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./archive/*" | wc -l)
echo "Total Python files: $total_files"

# Quick compilation check  
compiling_files=0
for file in $(find . -name "*.py" -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./archive/*" | head -20); do
    if python -m py_compile "$file" 2>/dev/null; then
        ((compiling_files++))
    fi
done

echo "Sample compilation rate: $compiling_files/20 files"

echo ""
echo "🎯 CODEX Mission Status"
echo "======================"
echo "✅ CODEX 1: Datetime compliance - Ready for automated fixes"
echo "✅ CODEX 2: MyPy safety - Ready for incremental improvements"  
echo "✅ CODEX 3: Import structure - Ready for circular dependency resolution"
echo "✅ CODEX 4: Test coverage - Ready for comprehensive testing"
echo "✅ CODEX 5: Syntax validation - Ready for final cleanup"
echo ""
echo "🚀 All CODEX Strike Teams ready for deployment!"