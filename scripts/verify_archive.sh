#!/bin/bash
# LUKHAS Archive Verification Script

if [ $# -eq 0 ]; then
    echo "Usage: $0 <archive_file.tar.gz>"
    exit 1
fi

ARCHIVE="$1"
TEMP_DIR=$(mktemp -d)

echo "🔍 Verifying LUKHAS archive: $(basename $ARCHIVE)"
echo ""

# Check if archive exists
if [ ! -f "$ARCHIVE" ]; then
    echo "❌ Archive file not found: $ARCHIVE"
    exit 1
fi

# Check archive integrity
echo "📦 Testing archive integrity..."
if tar -tzf "$ARCHIVE" > /dev/null 2>&1; then
    echo "✅ Archive integrity: OK"
else
    echo "❌ Archive integrity: FAILED"
    exit 1
fi

# Extract to temp directory for verification
echo "🗂️  Extracting for verification..."
cd "$TEMP_DIR"
tar -xzf "$ARCHIVE"

# Find the extracted directory
EXTRACTED_DIR=$(find . -maxdepth 1 -type d ! -name "." | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "❌ Could not find extracted directory"
    rm -rf "$TEMP_DIR"
    exit 1
fi

cd "$EXTRACTED_DIR"

# Verify key components
echo "🔍 Verifying key components..."

# Check for essential directories
COMPONENTS=(
    "lukhas"
    "candidate" 
    "tests"
    "CLAUDE.md"
    "pytest.ini"
    "pyproject.toml"
)

ALL_GOOD=true
for component in "${COMPONENTS[@]}"; do
    if [ -e "$component" ]; then
        echo "  ✅ $component"
    else
        echo "  ❌ $component (missing)"
        ALL_GOOD=false
    fi
done

# Count Python files
PY_FILES=$(find . -name "*.py" | wc -l)
echo "  📊 Python files: $PY_FILES"

# Check if T4 improvements are present
echo ""
echo "🛡️ Checking T4 improvements..."

# Check for security fixes
if grep -q "secrets" lukhas/bio/utilities.py 2>/dev/null; then
    echo "  ✅ Security fixes applied (secrets module)"
else
    echo "  ❌ Security fixes not found"
    ALL_GOOD=false
fi

# Check for T4 logging
if [ -f "lukhas/utils/logging_config.py" ]; then
    echo "  ✅ T4 logging system present"
else
    echo "  ❌ T4 logging system missing"
    ALL_GOOD=false
fi

# Check for test framework
if grep -q "T4-Grade" pytest.ini 2>/dev/null; then
    echo "  ✅ T4 test configuration present"
else
    echo "  ❌ T4 test configuration missing"
    ALL_GOOD=false
fi

# Check for component exports
if grep -q "ConsciousnessKernel" lukhas/consciousness/__init__.py 2>/dev/null; then
    echo "  ✅ Core component exports present"
else
    echo "  ❌ Core component exports missing"
    ALL_GOOD=false
fi

echo ""
if [ "$ALL_GOOD" = true ]; then
    echo "🎉 Archive verification: PASSED"
    echo "✅ All critical components verified"
    echo "✅ T4 improvements confirmed"
    echo "🚀 Archive ready for deployment"
else
    echo "❌ Archive verification: FAILED"
    echo "⚠️  Some components missing or outdated"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "Archive size: $(du -sh "$ARCHIVE" | cut -f1)"
echo "Verification complete."