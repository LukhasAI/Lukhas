#!/usr/bin/env bash
#
# cleanup_branches.sh - Auto-clean merged remote branches older than N days
#
# Safely deletes remote branches that are:
# 1. Fully merged into origin/main
# 2. Older than N days (default: 45)
# 3. Not protected (main, stable, release/*, prod/*)
#
# Usage:
#   bash scripts/cleanup_branches.sh [DAYS]
#
# Example:
#   bash scripts/cleanup_branches.sh 45  # Delete merged branches >45 days old
#
# Phase 3: Added for repo hygiene after Phase 2/3 completion.

set -euo pipefail

# Configuration
DAYS="${1:-45}"
PROTECTED_PATTERNS=(
    "main"
    "stable"
    "release/*"
    "prod/*"
    "production"
    "master"
    "develop"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧹 Cleaning merged remote branches older than $DAYS days"
echo ""

# Fetch and prune
echo "📡 Fetching latest refs and pruning..."
git fetch -p origin

# Calculate cutoff timestamp
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS date command
    CUTOFF=$(date -v-${DAYS}d +%s)
else
    # Linux date command
    CUTOFF=$(date -d "$DAYS days ago" +%s)
fi

echo "📅 Cutoff date: $(date -r $CUTOFF '+%Y-%m-%d %H:%M:%S')"
echo ""

# Track stats
DELETED=0
SKIPPED=0
ERRORS=0

# Get all merged branches
echo "🔍 Finding merged branches..."
MERGED_BRANCHES=$(git branch -r --merged origin/main | grep 'origin/' | sed 's|^[[:space:]]*origin/||')

# Process each merged branch
while IFS= read -r branch; do
    # Skip empty lines
    [[ -z "$branch" ]] && continue

    # Check if protected
    IS_PROTECTED=false
    for pattern in "${PROTECTED_PATTERNS[@]}"; do
        case "$branch" in
            $pattern)
                IS_PROTECTED=true
                break
                ;;
        esac
    done

    if [[ "$IS_PROTECTED" == "true" ]]; then
        echo -e "${YELLOW}⏭️  Skipping protected: $branch${NC}"
        ((SKIPPED++))
        continue
    fi

    # Get branch age
    COMMIT_TIMESTAMP=$(git log -1 --format=%ct "origin/$branch" 2>/dev/null || echo "0")

    if [[ "$COMMIT_TIMESTAMP" == "0" ]]; then
        echo -e "${YELLOW}⚠️  Skipping (no timestamp): $branch${NC}"
        ((SKIPPED++))
        continue
    fi

    # Check if older than cutoff
    if [[ "$COMMIT_TIMESTAMP" -lt "$CUTOFF" ]]; then
        echo -e "${GREEN}🗑️  Deleting: origin/$branch ($(date -r $COMMIT_TIMESTAMP '+%Y-%m-%d'))${NC}"

        if git push origin --delete "$branch" 2>/dev/null; then
            ((DELETED++))
        else
            echo -e "${RED}❌ Failed to delete: origin/$branch${NC}"
            ((ERRORS++))
        fi
    else
        DAYS_AGO=$(( ($(date +%s) - COMMIT_TIMESTAMP) / 86400 ))
        echo -e "${YELLOW}⏭️  Too recent: $branch (${DAYS_AGO}d old)${NC}"
        ((SKIPPED++))
    fi

done <<< "$MERGED_BRANCHES"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "  ✅ Deleted: $DELETED branches"
echo "  ⏭️  Skipped: $SKIPPED branches"
if [[ "$ERRORS" -gt 0 ]]; then
    echo -e "  ${RED}❌ Errors: $ERRORS branches${NC}"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit 0
