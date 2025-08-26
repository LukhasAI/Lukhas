#!/bin/bash

# Fix Diagnostic Issues in LUKHAS
# This script helps resolve the "unresolved diagnostics" messages during commits

echo "🔧 LUKHAS  Diagnostic Fixer"
echo "================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating .venv..."
    source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

echo "📊 Current Diagnostic Summary:"
echo "------------------------------"

# Count total errors
TOTAL_ERRORS=$(python3 -m ruff check . --select=E,F 2>&1 | grep "Found" | grep -oE '[0-9]+' | head -1)
echo "Total errors in codebase: $TOTAL_ERRORS"

# Check for critical errors
CRITICAL_ERRORS=$(python3 -m ruff check . --select=F821,F822,F823 2>&1 | grep "Found" | grep -oE '[0-9]+' | head -1)
echo "Critical errors (undefined names): ${CRITICAL_ERRORS:-0}"

echo ""
echo "🔍 Checking modified files for issues..."
echo "----------------------------------------"

# Get list of modified Python files
MODIFIED_FILES=$(git diff --name-only --diff-filter=ACM | grep '\.py$')

if [ -z "$MODIFIED_FILES" ]; then
    echo "No modified Python files found."
else
    for file in $MODIFIED_FILES; do
        if [ -f "$file" ]; then
            echo ""
            echo "Checking: $file"
            ERROR_COUNT=$(python3 -m ruff check "$file" --select=E,F 2>&1 | grep "Found" | grep -oE '[0-9]+' | head -1)
            if [ -n "$ERROR_COUNT" ] && [ "$ERROR_COUNT" -gt 0 ]; then
                echo "  ❌ $ERROR_COUNT errors found"

                # Offer to auto-fix
                echo "  🔧 Attempting auto-fix..."
                python3 -m ruff check "$file" --fix --select=F401,E501 2>/dev/null

                # Check if still has errors
                REMAINING=$(python3 -m ruff check "$file" --select=E,F 2>&1 | grep "Found" | grep -oE '[0-9]+' | head -1)
                if [ -n "$REMAINING" ] && [ "$REMAINING" -gt 0 ]; then
                    echo "  ⚠️  $REMAINING errors remain (manual fix needed)"
                    # Show first 5 remaining errors
                    python3 -m ruff check "$file" --select=E,F 2>&1 | head -10
                else
                    echo "  ✅ All errors fixed!"
                fi
            else
                echo "  ✅ No errors found"
            fi
        fi
    done
fi

echo ""
echo "🎯 Quick Fixes Available:"
echo "------------------------"
echo "1. Fix all unused imports:     python3 -m ruff check . --fix --select=F401"
echo "2. Fix all in current dir:     python3 -m ruff check . --fix"
echo "3. Format with black:          python3 -m black ."
echo "4. Check specific file:        python3 -m ruff check path/to/file.py"
echo ""

echo "📝 Common Issues and Solutions:"
echo "------------------------------"
echo "• F401: Unused import → Remove the import or add to __all__"
echo "• F821: Undefined name → Import missing module or define variable"
echo "• E501: Line too long → Break line or ignore with # noqa: E501"
echo "• F841: Local variable assigned but never used → Use or remove variable"
echo ""

# Summary
echo "📊 Final Summary:"
echo "----------------"
if [ -n "$TOTAL_ERRORS" ] && [ "$TOTAL_ERRORS" -gt 100 ]; then
    echo "⚠️  High error count detected. Consider:"
    echo "   - Running: python3 -m ruff check . --fix"
    echo "   - Excluding more directories in pyproject.toml"
    echo "   - Adding per-file ignores for generated code"
elif [ -n "$TOTAL_ERRORS" ] && [ "$TOTAL_ERRORS" -gt 0 ]; then
    echo "🔧 Moderate error count. Most can be auto-fixed."
else
    echo "✅ No diagnostic issues found!"
fi

echo ""
echo "💡 Tip: Add this to your git pre-commit hook to catch issues early:"
echo "   python3 -m ruff check --diff --exit-non-zero-on-fix"
