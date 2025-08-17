#!/bin/bash
# Script to organize and validate tests directory
# Created: 2025-08-17

set -e

echo "🧪 LUKHAS Tests Organization & Validation"
echo "========================================="

cd tests

# Count initial state
INITIAL_FILES=$(find . -type f -name "*.py" | wc -l | tr -d ' ')
echo "📊 Initial test files: $INITIAL_FILES"

# 1. Find and report STUB tests
echo ""
echo "🔍 Finding STUB tests..."
STUB_FILES=$(find . -name "*STUB*" -type f)
STUB_COUNT=$(echo "$STUB_FILES" | grep -c "STUB" || echo "0")
echo "  Found $STUB_COUNT STUB test files"

if [[ $STUB_COUNT -gt 0 ]]; then
    echo "  STUB files:"
    echo "$STUB_FILES" | while read file; do
        echo "    - $file"
    done
fi

# 2. Find empty test files
echo ""
echo "🗑️ Finding empty test files..."
EMPTY_COUNT=0
for file in $(find . -name "*.py" -type f); do
    # Check if file has any actual test functions
    if ! grep -q "def test_\|class Test" "$file" 2>/dev/null; then
        if ! grep -q "pytest\|unittest" "$file" 2>/dev/null; then
            echo "    - $file (no tests found)"
            ((EMPTY_COUNT++))
        fi
    fi
done
echo "  Found $EMPTY_COUNT files without tests"

# 3. Find duplicate test files
echo ""
echo "🔄 Finding duplicate test files..."
find . -name "*.py" -type f -exec basename {} \; | sort | uniq -d > /tmp/dup_tests.txt
if [[ -s /tmp/dup_tests.txt ]]; then
    echo "  Duplicate test file names:"
    while read name; do
        echo "    - $name:"
        find . -name "$name" -type f | while read path; do
            echo "      * $path"
        done
    done < /tmp/dup_tests.txt
else
    echo "  No duplicate test file names found"
fi

# 4. Check test organization structure
echo ""
echo "📁 Test directory structure:"
echo "  Unit tests: $(find unit -name "*.py" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  Integration tests: $(find integration -name "*.py" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  E2E tests: $(find e2e -name "*.py" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  Module tests:"
for dir in */; do
    if [[ "$dir" != "unit/" && "$dir" != "integration/" && "$dir" != "e2e/" && "$dir" != "__pycache__/" ]]; then
        count=$(find "$dir" -name "*.py" -type f | wc -l | tr -d ' ')
        if [[ $count -gt 0 ]]; then
            echo "    - $dir: $count files"
        fi
    fi
done

# 5. Run a quick test discovery to see what pytest finds
echo ""
echo "🔬 Running pytest discovery (dry run)..."
cd ..
pytest_output=$(python -m pytest tests --collect-only -q 2>&1 || true)
test_count=$(echo "$pytest_output" | grep -E "test.*selected|tests.*selected" | grep -oE "[0-9]+" | head -1 || echo "0")
echo "  Pytest discovered: $test_count tests"

# 6. Identify broken imports
echo ""
echo "🔧 Checking for broken imports..."
cd tests
BROKEN_IMPORTS=0
for file in $(find . -name "*.py" -type f); do
    if python -c "import sys; sys.path.insert(0, '..'); exec(open('$file').read())" 2>&1 | grep -q "ImportError\|ModuleNotFoundError"; then
        echo "    - $file has import errors"
        ((BROKEN_IMPORTS++))
    fi
done 2>/dev/null
echo "  Found $BROKEN_IMPORTS files with import issues"

# 7. Generate test report
echo ""
echo "📊 Generating test organization report..."
cat > test_organization_report.md << EOF
# Test Organization Report
Generated: $(date)

## Summary
- Total test files: $INITIAL_FILES
- STUB tests: $STUB_COUNT
- Empty test files: $EMPTY_COUNT
- Files with import errors: $BROKEN_IMPORTS
- Tests discovered by pytest: $test_count

## Recommendations

### 1. Remove or implement STUB tests
These files contain placeholder tests that should be implemented or removed:
$(echo "$STUB_FILES" | sed 's/^/- /')

### 2. Clean up empty test files
These files don't contain actual tests and could be removed.

### 3. Fix import errors
$BROKEN_IMPORTS files have import issues that need to be resolved.

### 4. Organize tests by type
Consider reorganizing tests into:
- \`unit/\` - Fast, isolated unit tests
- \`integration/\` - Tests that verify module interactions
- \`e2e/\` - End-to-end system tests
- \`performance/\` - Performance and benchmark tests

## Next Steps
1. Run: \`make test\` to validate all tests
2. Fix broken imports
3. Implement or remove STUB tests
4. Clean up empty test files
EOF

echo "  Report saved to: tests/test_organization_report.md"

# 8. Create a test runner script
echo ""
echo "🏃 Creating test runner script..."
cat > run_valid_tests.sh << 'EOF'
#!/bin/bash
# Run only valid tests, skipping known issues

echo "Running valid LUKHAS tests..."
echo "============================"

# Skip STUB tests and known broken tests
pytest -v \
    --ignore=tests/unit/test_STUB_* \
    --ignore=tests/test_stubs_old.py \
    -k "not STUB and not stub" \
    --tb=short \
    "$@"
EOF

chmod +x run_valid_tests.sh
echo "  Created: tests/run_valid_tests.sh"

echo ""
echo "✅ Test organization complete!"
echo "=============================="
echo "📄 Full report: tests/test_organization_report.md"
echo "🏃 Run valid tests: tests/run_valid_tests.sh"
echo ""
echo "Quick test run command:"
echo "  cd tests && ./run_valid_tests.sh -x"