#!/bin/bash
# Quick LUKHAS Archive Script - Simple version

ARCHIVE_NAME="LUKHAS-AI-$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="$HOME/Desktop"
TEMP_DIR="/tmp/${ARCHIVE_NAME}"

echo "🚀 Creating quick LUKHAS archive..."

# Clean temp files first
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create temp directory and copy files
mkdir -p "$TEMP_DIR"
echo "📦 Copying files (excluding large caches)..."

rsync -a \
    --exclude='.git/' \
    --exclude='.mypy_cache/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='node_modules/' \
    --exclude='.next/' \
    --exclude='htmlcov/' \
    --exclude='.pytest_cache/' \
    . "$TEMP_DIR/"

# Create archive
cd "$(dirname "$TEMP_DIR")"
tar -czf "${OUTPUT_DIR}/${ARCHIVE_NAME}.tar.gz" "$(basename "$TEMP_DIR")"

# Cleanup
rm -rf "$TEMP_DIR"

ARCHIVE_SIZE=$(du -sh "${OUTPUT_DIR}/${ARCHIVE_NAME}.tar.gz" | cut -f1)

echo "✅ Archive created: ${OUTPUT_DIR}/${ARCHIVE_NAME}.tar.gz"
echo "📊 Size: $ARCHIVE_SIZE"
echo "🚀 Ready for Google Drive upload!"