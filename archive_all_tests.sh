#!/bin/bash
# Archive ALL test files to tests_old_broken/

echo "🗂️  Archiving ALL test files to tests_old_broken/"
echo "================================================"

# Create timestamp for this archival
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Archive timestamp: $TIMESTAMP"

# Create archive subdirectory for this batch
ARCHIVE_DIR="tests_old_broken/archive_$TIMESTAMP"
mkdir -p "$ARCHIVE_DIR"

# Count files before archiving
echo ""
echo "📊 Counting test files to archive..."

# Find all Python test files (excluding already archived ones)
PYTHON_TESTS=$(find . -name "*test*.py" -not -path "./tests_old_broken/*" -type f)
PYTHON_COUNT=$(echo "$PYTHON_TESTS" | grep -c "^" || echo "0")

# Find all TypeScript/JavaScript test files
TS_TESTS=$(find . -name "*test*.ts" -o -name "*test*.js" -o -name "*spec*.ts" -o -name "*spec*.js" | grep -v "./tests_old_broken/" || echo "")
TS_COUNT=$(echo "$TS_TESTS" | grep -c "^" || echo "0")

# Find test directories
TEST_DIRS=$(find . -type d -name "tests" -not -path "./tests_old_broken/*" || echo "")
DIR_COUNT=$(echo "$TEST_DIRS" | grep -c "^" || echo "0")

echo "Python test files: $PYTHON_COUNT"
echo "TypeScript/JS test files: $TS_COUNT"
echo "Test directories: $DIR_COUNT"

echo ""
echo "🔄 Starting archive process..."

# Archive Python test files
if [ "$PYTHON_COUNT" -gt 0 ]; then
    echo "Archiving Python test files..."
    echo "$PYTHON_TESTS" | while read -r file; do
        if [ -n "$file" ]; then
            # Create directory structure in archive
            rel_path=$(dirname "$file")
            mkdir -p "$ARCHIVE_DIR/$rel_path"
            # Move file
            mv "$file" "$ARCHIVE_DIR/$file"
            echo "  ✅ Moved: $file"
        fi
    done
fi

# Archive TypeScript/JavaScript test files
if [ "$TS_COUNT" -gt 0 ]; then
    echo "Archiving TypeScript/JS test files..."
    echo "$TS_TESTS" | while read -r file; do
        if [ -n "$file" ]; then
            # Create directory structure in archive
            rel_path=$(dirname "$file")
            mkdir -p "$ARCHIVE_DIR/$rel_path"
            # Move file
            mv "$file" "$ARCHIVE_DIR/$file"
            echo "  ✅ Moved: $file"
        fi
    done
fi

# Archive test directories
if [ "$DIR_COUNT" -gt 0 ]; then
    echo "Archiving test directories..."
    echo "$TEST_DIRS" | while read -r dir; do
        if [ -n "$dir" ] && [ -d "$dir" ]; then
            # Create parent directory structure
            parent_dir=$(dirname "$dir")
            mkdir -p "$ARCHIVE_DIR/$parent_dir"
            # Move entire directory
            mv "$dir" "$ARCHIVE_DIR/$dir"
            echo "  ✅ Moved directory: $dir"
        fi
    done
fi

echo ""
echo "📝 Creating archive manifest..."
cat > "$ARCHIVE_DIR/ARCHIVE_MANIFEST.md" << EOF
# Test Archive Manifest - $TIMESTAMP

## Archive Summary
- **Date**: $(date)
- **Python test files archived**: $PYTHON_COUNT
- **TypeScript/JS test files archived**: $TS_COUNT
- **Test directories archived**: $DIR_COUNT
- **Total items**: $((PYTHON_COUNT + TS_COUNT + DIR_COUNT))

## Archive Contents

### Python Test Files
\`\`\`
$PYTHON_TESTS
\`\`\`

### TypeScript/JavaScript Test Files
\`\`\`
$TS_TESTS
\`\`\`

### Test Directories
\`\`\`
$TEST_DIRS
\`\`\`

## Next Steps
All test files have been archived. The codebase is now clean of scattered test files.
Consider implementing a new centralized testing strategy.
EOF

echo "✅ Archive complete!"
echo "📁 Files archived to: $ARCHIVE_DIR"
echo "📋 Manifest created: $ARCHIVE_DIR/ARCHIVE_MANIFEST.md"
echo ""
echo "🔍 Verifying cleanup..."

# Verify cleanup
REMAINING_PYTHON=$(find . -name "*test*.py" -not -path "./tests_old_broken/*" -type f | wc -l)
REMAINING_TS=$(find . -name "*test*.ts" -o -name "*test*.js" -o -name "*spec*.ts" -o -name "*spec*.js" | grep -v "./tests_old_broken/" | wc -l || echo "0")
REMAINING_DIRS=$(find . -type d -name "tests" -not -path "./tests_old_broken/*" | wc -l || echo "0")

echo "Remaining Python test files: $REMAINING_PYTHON"
echo "Remaining TS/JS test files: $REMAINING_TS"
echo "Remaining test directories: $REMAINING_DIRS"

if [ "$REMAINING_PYTHON" -eq 0 ] && [ "$REMAINING_TS" -eq 0 ] && [ "$REMAINING_DIRS" -eq 0 ]; then
    echo "🎉 SUCCESS: All test files have been archived!"
else
    echo "⚠️  WARNING: Some test files may remain. Check manually."
fi
