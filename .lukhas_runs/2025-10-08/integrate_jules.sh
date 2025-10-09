#!/bin/bash
# Jules Batch Integration Script
# Safely integrates recovered files from Jules's batch

set -e  # Exit on error

REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
JULES_DIR="/Users/agi_dev/Downloads/BATCH-JULES-2025-10-08-01"
BACKUP_DIR="$REPO_ROOT/.lukhas_runs/2025-10-08/backups"
MAPPING_FILE="$REPO_ROOT/.lukhas_runs/2025-10-08/jules_file_mapping.json"

cd "$REPO_ROOT"

echo "🚀 Jules Batch Integration"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo ""
echo "📋 Files to integrate:"
echo ""

# Read mappings and integrate
jq -r '.mappings | to_entries[] | "\(.key) → \(.value)"' "$MAPPING_FILE" | while IFS='→' read -r source target; do
    source=$(echo "$source" | xargs)  # trim whitespace
    target=$(echo "$target" | xargs)

    source_file="$JULES_DIR/$source"
    target_file="$REPO_ROOT/$target"

    if [ ! -f "$source_file" ]; then
        echo "⚠️  Source not found: $source (skipping)"
        continue
    fi

    # Create parent directory
    mkdir -p "$(dirname "$target_file")"

    # Backup existing file
    if [ -f "$target_file" ]; then
        backup_name="${target//\//_}.bak"
        cp "$target_file" "$BACKUP_DIR/$backup_name"
        echo "  📦 Backed up: $target → backups/$backup_name"
        action="UPDATE"
    else
        action="CREATE"
    fi

    # Copy file
    cp "$source_file" "$target_file"
    echo "  ✅ $action: $source → $target"
done

echo ""
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo "✅ Integration complete!"
echo ""
echo "📦 Backups saved to: .lukhas_runs/2025-10-08/backups/"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Run tests: pytest tests/matriz/ tests/security/ -v"
echo "  3. Check syntax: ruff check ."
echo "  4. Verify lanes: make lane-guard"
echo ""
