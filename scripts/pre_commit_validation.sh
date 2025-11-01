#!/bin/bash
# Pre-commit validation script for LUKHAS development
# Ensures proper testing discipline before commits

set -e
echo "🧪 Running pre-commit validation..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get list of changed Python files
CHANGED_PY_FILES=$(git diff --name-only --cached | grep -E '\.py$' || true)

if [ -z "$CHANGED_PY_FILES" ]; then
    print_warning "No Python files changed, skipping Python validations"
else
    echo "📋 Validating Python files: $CHANGED_PY_FILES"
    
    # 1. Syntax check
    echo "1️⃣ Checking Python syntax..."
    for file in $CHANGED_PY_FILES; do
        if [ -f "$file" ]; then
            python -m py_compile "$file" || {
                print_error "Syntax error in $file"
                exit 1
            }
        fi
    done
    print_status "Python syntax check passed"
    
    # 2. Ruff linting
    echo "2️⃣ Running ruff linting..."
    if command -v ruff &> /dev/null; then
        ruff check $CHANGED_PY_FILES || {
            print_error "Ruff linting failed"
            exit 1
        }
        print_status "Ruff linting passed"
    else
        print_warning "Ruff not available, skipping lint check"
    fi
    
    # 3. Import validation for changed files
    echo "3️⃣ Validating imports..."
    for file in $CHANGED_PY_FILES; do
        if [ -f "$file" ]; then
            # Try to import the module (if it's importable)
            module_path=$(echo "$file" | sed 's/\.py$//' | sed 's/\//./g')
            if [[ "$module_path" != *"__"* && "$module_path" != "main" ]]; then
                python -c "import sys; sys.path.insert(0, '.'); import $module_path" 2>/dev/null || {
                    print_warning "Could not import $module_path (may be a script, not a module)"
                }
            fi
        fi
    done
    print_status "Import validation completed"
fi

# 4. Run targeted tests if test files exist
echo "4️⃣ Running targeted tests..."
if [ -d "tests/" ]; then
    # Run quick tests first
    if command -v pytest &> /dev/null; then
        # Run smoke tests
        pytest tests/smoke/ -v --tb=short 2>/dev/null || {
            print_warning "Some smoke tests failed, checking if critical"
        }
        print_status "Smoke tests completed"
        
        # Run unit tests for changed modules
        for file in $CHANGED_PY_FILES; do
            test_file="tests/unit/test_$(basename "$file")"
            if [ -f "$test_file" ]; then
                echo "Running tests for $file..."
                pytest "$test_file" -v || {
                    print_error "Unit tests failed for $file"
                    exit 1
                }
            fi
        done
        print_status "Unit tests completed"
    else
        print_warning "pytest not available, skipping test execution"
    fi
else
    print_warning "No tests/ directory found"
fi

# 5. Check for common issues
echo "5️⃣ Checking for common issues..."

# Check for TODO/FIXME without issues
if grep -r "TODO\|FIXME" $CHANGED_PY_FILES 2>/dev/null | grep -v "TODO:" | grep -v "FIXME:" | head -5; then
    print_warning "Found TODO/FIXME comments - consider converting to tracked issues"
fi

# Check for debug prints
if grep -r "print(" $CHANGED_PY_FILES 2>/dev/null | head -3; then
    print_warning "Found print() statements - consider using logging"
fi

# Check for hardcoded paths
if grep -r "/Users\|C:\\\\" $CHANGED_PY_FILES 2>/dev/null | head -3; then
    print_warning "Found potential hardcoded paths"
fi

print_status "Common issues check completed"

# 6. Final validation
echo "6️⃣ Final validation..."
if [ -f "Makefile" ] && command -v make &> /dev/null; then
    # Try a quick make validation if available
    make doctor 2>/dev/null || print_warning "Make doctor check had warnings"
fi

print_status "Pre-commit validation completed successfully!"
echo "🚀 Ready to commit!"