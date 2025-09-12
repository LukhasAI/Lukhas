#!/bin/bash
# update_todos.sh - Refresh the LUKHAS TODO organization system
# Run this script whenever you want to update the TODO categorization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔄 LUKHAS TODO System Update"
echo "=" * 40

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    echo "❌ Error: Run this script from the LUKHAS project root"
    exit 1
fi

echo "📂 Project Root: $PROJECT_ROOT"
echo "📅 Date: $(date)"

# Load standardized exclusions
if [[ -f "$PROJECT_ROOT/tools/search/standardized_exclusions.sh" ]]; then
    source "$PROJECT_ROOT/tools/search/standardized_exclusions.sh"
    echo "✅ Loaded standardized exclusions"
else
    echo "❌ Error: Cannot find standardized exclusions script"
    exit 1
fi

# Get current TODO count
echo ""
echo "🔍 Current TODO Statistics:"
TODO_COUNT=$(clean_count_todos)
PY_FILES=$(clean_count_py)
echo "  📊 Total TODOs: $TODO_COUNT"
echo "  🐍 Python Files: $PY_FILES"

# Backup existing TODO files
BACKUP_DIR="$PROJECT_ROOT/TODO/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo ""
echo "💾 Creating backup..."
for priority in CRITICAL HIGH MED LOW; do
    if [[ -f "$PROJECT_ROOT/TODO/$priority/${priority,,}_todos.md" ]]; then
        cp "$PROJECT_ROOT/TODO/$priority/${priority,,}_todos.md" "$BACKUP_DIR/" 2>/dev/null || true
    fi
done

if [[ -f "$PROJECT_ROOT/TODO/SUMMARY.md" ]]; then
    cp "$PROJECT_ROOT/TODO/SUMMARY.md" "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "✅ Backup created: $BACKUP_DIR"

# Run categorization
echo ""
echo "🎯 Running TODO categorization..."
cd "$PROJECT_ROOT"
python3 TODO/scripts/categorize_todos.py

# Update summary timestamp
if [[ -f "$PROJECT_ROOT/TODO/SUMMARY.md" ]]; then
    sed -i.bak "s/\*\*Generated\*\*: .*/\*\*Generated\*\*: $(date '+%B %d, %Y')/" "$PROJECT_ROOT/TODO/SUMMARY.md"
    rm -f "$PROJECT_ROOT/TODO/SUMMARY.md.bak"
    echo "✅ Updated summary timestamp"
fi

echo ""
echo "📊 Final Statistics:"
echo "  📁 TODO Files Generated:"
for priority in CRITICAL HIGH MED LOW; do
    file="$PROJECT_ROOT/TODO/$priority/${priority,,}_todos.md"
    if [[ -f "$file" ]]; then
        lines=$(wc -l < "$file")
        todos=$(grep -c "^### " "$file" || echo "0")
        echo "    $priority: $todos TODOs ($lines lines)"
    fi
done

echo ""
echo "✅ TODO system update complete!"
echo "📂 Check TODO/ directories for updated files"
echo "💾 Backup available at: $BACKUP_DIR"

# Optional: Commit changes
read -p "🔄 Commit TODO updates to git? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$PROJECT_ROOT"
    git add TODO/
    git commit -m "📋 Update TODO organization system - $(date '+%Y-%m-%d')"
    echo "✅ Changes committed to git"
fi

echo ""
echo "🎯 Summary: Successfully updated TODO organization system"
echo "   Use the files in TODO/CRITICAL/, TODO/HIGH/, TODO/MED/, TODO/LOW/"
echo "   for prioritized development and agent task assignment."