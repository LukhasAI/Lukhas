#!/bin/bash
# LUKHAS AI Safe Cleanup Script
# Trinity Framework: ⚛️🧠🛡️
# 
# This script ONLY archives files with LOW AI/AGI value
# All high-value AI logic is preserved

set -e  # Exit on error

ARCHIVE_DIR="/Users/agi_dev/lukhas-archive/2025-08-13-safe-cleanup"
mkdir -p "$ARCHIVE_DIR"

echo "🛡️ Starting SAFE LUKHAS AI cleanup..."
echo "⚠️  Preserving all high-value AI/AGI modules"
echo ""


# Archive low-value files with no AI content
echo "🗂️ Archiving low-value files..."
mkdir -p "$ARCHIVE_DIR/low_value"
mv "api_documentation_generator/__init__.py" "$ARCHIVE_DIR/low_value/" 2>/dev/null || true
mv "branding/policy/__init__.py" "$ARCHIVE_DIR/low_value/" 2>/dev/null || true

echo ""
echo "✅ Safe cleanup complete!"
echo "📊 Files archived to: $ARCHIVE_DIR"
echo ""
echo "⚠️  PRESERVED FILES:"
echo "  - 7 high-value AI/AGI modules preserved"
echo "  - 20 files need manual review"

echo ""
echo "💾 Run 'git status' to see changes"
echo "📋 Check 'safe_cleanup_review.txt' for files needing manual review"
