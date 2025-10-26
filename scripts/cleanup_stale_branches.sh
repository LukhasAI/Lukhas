#!/bin/bash
# Script to help clean up stale git branches
# Usage: ./scripts/cleanup_stale_branches.sh [--dry-run|--delete]

set -e

MODE="${1:---dry-run}"
CUTOFF_DATE="2025-09-01"  # Branches older than this are considered stale

echo "🧹 LUKHAS Branch Cleanup Tool"
echo "=============================="
echo "Mode: $MODE"
echo "Cutoff Date: $CUTOFF_DATE"
echo ""

if [ "$MODE" = "--dry-run" ]; then
    echo "📋 Stale branches (would be deleted in --delete mode):"
    echo ""
    git for-each-ref --sort=committerdate --format='%(refname:short)|%(committerdate:short)' refs/heads/ | \
    while IFS='|' read -r branch date; do
        if [[ "$date" < "$CUTOFF_DATE" ]] && [[ "$branch" != "main" ]]; then
            echo "  🗑️  $branch (last commit: $date)"
        fi
    done
    echo ""
    echo "To actually delete these branches, run:"
    echo "  ./scripts/cleanup_stale_branches.sh --delete"
    
elif [ "$MODE" = "--delete" ]; then
    echo "⚠️  WARNING: This will DELETE stale branches!"
    echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
    sleep 5
    
    DELETED=0
    git for-each-ref --sort=committerdate --format='%(refname:short)|%(committerdate:short)' refs/heads/ | \
    while IFS='|' read -r branch date; do
        if [[ "$date" < "$CUTOFF_DATE" ]] && [[ "$branch" != "main" ]]; then
            echo "  Deleting $branch..."
            git branch -D "$branch" 2>/dev/null && DELETED=$((DELETED+1)) || echo "    ⚠️  Failed to delete"
        fi
    done
    echo ""
    echo "✅ Cleanup complete!"
    
else
    echo "❌ Invalid mode: $MODE"
    echo "Usage: $0 [--dry-run|--delete]"
    exit 1
fi
