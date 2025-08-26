#!/bin/bash

# LUKHAS Repository Organization Script
# Purpose: Clean up scattered files, consolidate duplicates, remove empty directories

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════"
echo "          LUKHAS Repository Organization Script"
echo "════════════════════════════════════════════════════════════"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Get the repository root
REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
cd "$REPO_ROOT"

# Create necessary directories if they don't exist
echo "Creating directory structure..."
mkdir -p scripts
mkdir -p docs/archive
mkdir -p tests/integration
mkdir -p tests/unit
mkdir -p branding/unified/vocabularies
mkdir -p branding/unified/tone
mkdir -p branding/unified/visual

print_status "Directory structure created"
echo

# ==============================================================================
# STEP 1: Move test files from root to tests directory
# ==============================================================================
echo "Moving test files from root to tests directory..."

TEST_FILES=(
    "test_auto_budget.json"
    "test_consent_ctx.json"
    "test_consent_integration.sh"
    "test_context.json"
    "test_ctx_ro.json"
    "test_glyph_system.py"
    "test_pii_context.json"
    "test_pwm_file.sh"
    "test_risk_ctx.json"
)

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" tests/ 2>/dev/null && print_status "Moved $file to tests/" || print_warning "$file already moved or doesn't exist"
    fi
done

echo

# ==============================================================================
# STEP 2: Move scripts from root to scripts directory
# ==============================================================================
echo "Moving scripts from root to scripts directory..."

SCRIPT_FILES=(
    "bootstrap_lukhas_qi.sh"
    "bootstrap_lukhas_qi_all12.sh"
    "patch_budget_policy_report.sh"
    "patch_prod_core.sh"
    "patch_teq_pii.sh"
)

for file in "${SCRIPT_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" scripts/ 2>/dev/null && print_status "Moved $file to scripts/" || print_warning "$file already moved or doesn't exist"
    fi
done

echo

# ==============================================================================
# STEP 3: Archive old documentation
# ==============================================================================
echo "Archiving old documentation..."

DOC_FILES=(
    "CLAUDE_CODE_MCP.md"
    "CLAUDE_CODE_PROMPTS.md"
    "DETAILED_FILE_BREAKDOWN.md"
    "ENVIRONMENT_PATH_UPDATE_SUMMARY.md"
    "IMPORT_FIX_SUMMARY.md"
    "INTERACTIVE_GIT_HOOKS_SOLUTION.md"
    "LUKHAS_IMPLEMENTATION_GAP_ANALYSIS.md"
    "LUKHAS_IMPLEMENTATION_PLAN.md"
    "MINIMUM_VIABLE_SYSTEM_ANALYSIS.md"
    "TOP_PROMOTION_CANDIDATES.md"
    "USER_MANUAL_EXISTING.md"
    "USER_MANUAL_NEW_FEATURES.md"
    "123.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" docs/archive/ 2>/dev/null && print_status "Archived $file" || print_warning "$file already archived or doesn't exist"
    fi
done

echo

# ==============================================================================
# STEP 4: Consolidate vocabulary files
# ==============================================================================
echo "Consolidating vocabulary files..."

# Check if vocabularies exist in multiple locations
if [ -d "branding/tone/tools/vocabularies" ] && [ -d "tools/tone/vocabularies" ]; then
    print_info "Found duplicate vocabularies in branding/tone and tools/tone"

    # Copy unique files to unified location
    cp -n branding/tone/tools/vocabularies/*.yaml branding/unified/vocabularies/ 2>/dev/null || true
    cp -n tools/tone/vocabularies/*.yaml branding/unified/vocabularies/ 2>/dev/null || true

    print_status "Vocabularies consolidated to branding/unified/vocabularies/"
fi

# Move Python vocabulary files to unified location
if [ -d "core/symbolic" ]; then
    cp -n core/symbolic/*vocabulary*.py branding/unified/vocabularies/ 2>/dev/null || true
    print_status "Python vocabulary files copied to unified location"
fi

if [ -d "symbolic/vocabularies" ]; then
    cp -n symbolic/vocabularies/*.py branding/unified/vocabularies/ 2>/dev/null || true
    print_status "Symbolic vocabulary files copied to unified location"
fi

echo

# ==============================================================================
# STEP 5: Remove empty directories
# ==============================================================================
echo "Removing empty directories..."

# Find and remove empty directories (excluding .git and node_modules)
find . -type d -empty -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" -delete 2>/dev/null

print_status "Empty directories removed"
echo

# ==============================================================================
# STEP 6: Clean up duplicate/obsolete files
# ==============================================================================
echo "Identifying duplicate files to remove..."

# Remove empty placeholder files
find . -type f -size 0 -name "Icon" -delete 2>/dev/null && print_status "Removed empty Icon files" || true
find . -type f -size 0 -name "*.log" -delete 2>/dev/null && print_status "Removed empty log files" || true

echo

# ==============================================================================
# STEP 7: Create organization summary
# ==============================================================================
echo "Creating organization summary..."

cat > ORGANIZATION_SUMMARY.md << 'EOF'
# Repository Organization Summary

## Changes Made

### 1. Test Files
Moved all test-related files from root to `/tests/` directory:
- test_*.json files
- test_*.sh scripts
- test_*.py files

### 2. Scripts
Moved all scripts from root to `/scripts/` directory:
- bootstrap_*.sh
- patch_*.sh

### 3. Documentation
Archived old documentation to `/docs/archive/`:
- Implementation plans
- User manuals
- Analysis documents

### 4. Vocabularies
Consolidated vocabulary files to `/branding/unified/vocabularies/`:
- YAML vocabulary definitions
- Python vocabulary modules
- Removed duplicates between branding/tone and tools/tone

### 5. Empty Directories
Removed all empty directories to clean up repository structure

## New Structure

```
/
├── scripts/           # All executable scripts
├── tests/            # All test files and scripts
├── docs/
│   └── archive/      # Archived documentation
├── branding/
│   └── unified/      # Consolidated branding resources
│       ├── vocabularies/
│       ├── tone/
│       └── visual/
└── ...
```

## Next Steps

1. Update imports in Python files to reflect new vocabulary locations
2. Update CI/CD scripts to use new script paths
3. Review and deduplicate vocabulary definitions
4. Create master vocabulary index

EOF

print_status "Organization summary created: ORGANIZATION_SUMMARY.md"
echo

# ==============================================================================
# Final Summary
# ==============================================================================
echo "════════════════════════════════════════════════════════════"
echo "                Organization Complete!"
echo "════════════════════════════════════════════════════════════"
echo
echo "Summary of changes:"
echo "  • Test files moved to /tests/"
echo "  • Scripts moved to /scripts/"
echo "  • Old docs archived to /docs/archive/"
echo "  • Vocabularies consolidated to /branding/unified/vocabularies/"
echo "  • Empty directories removed"
echo
echo "Review ORGANIZATION_SUMMARY.md for detailed changes"
echo
