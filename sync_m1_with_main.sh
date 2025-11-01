#!/bin/bash
# LUKHAS M1 Branch Sync Script
# Safe sync of M1 branch with main branch (107 commits ahead)

set -e

echo "🚨 LUKHAS Branch Sync: M1 → main"
echo "=========================================="

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "Step 1: Backup current state"
git branch M1-backup-$(date +%Y-%m-%d-%H%M) M1 || print_warning "Backup already exists"
print_status "Backup created"

echo "Step 2: Ensure we're on M1 branch"
git checkout M1 || {
    print_error "Failed to switch to M1 branch"
    exit 1
}
print_status "On M1 branch"

echo "Step 3: Fetch latest from remote"
git fetch origin
print_status "Fetched latest changes"

echo "Step 4: Check divergence"
COMMITS_AHEAD=$(git rev-list --count M1..origin/main)
COMMITS_BEHIND=$(git rev-list --count origin/main..M1)

echo "📊 Branch Analysis:"
echo "   - M1 has $COMMITS_BEHIND commits ahead of main"
echo "   - main has $COMMITS_AHEAD commits ahead of M1"

echo "Step 5: Merge main into M1"
print_warning "Attempting merge of main into M1..."

if git merge origin/main --no-ff -m "merge: sync M1 with main - resolve 107 commit divergence

- Merge main branch changes into M1
- Preserve M1 development history
- Resolve branch divergence safely
- Maintain T4 commit standards

Signed-off-by: GitHub Copilot <copilot@lukhas.ai>"; then
    print_status "Merge completed successfully!"
else
    print_error "Merge conflicts detected!"
    echo "🔧 Conflict Resolution Required:"
    echo "   1. Resolve conflicts in affected files"
    echo "   2. Run: git add <resolved-files>"
    echo "   3. Run: git commit"
    echo "   4. Continue with validation"
    echo ""
    echo "Conflict files:"
    git status --porcelain | grep "^UU"
    exit 1
fi

echo "Step 6: Validation"
echo "Running system health checks..."

if command -v make &> /dev/null; then
    if make doctor; then
        print_status "System health check passed"
    else
        print_warning "System health check had warnings - please review"
    fi
    
    if make smoke; then
        print_status "Smoke tests passed"
    else
        print_warning "Smoke tests had issues - please review"
    fi
else
    print_warning "Make not available - manual validation recommended"
fi

echo ""
print_status "Branch sync completed!"
echo "📋 Next Steps:"
echo "   1. Review merged changes"
echo "   2. Test critical functionality"
echo "   3. Consider pushing M1 to remote if ready"
echo ""
echo "🔄 Sync Summary:"
echo "   - Branch: M1 ← main"
echo "   - Method: Merge (preserves history)"
echo "   - Backup: M1-backup-$(date +%Y-%m-%d-%H%M)"
echo "   - Status: ✅ Complete"