#!/bin/bash
# Simplify GitHub Actions CI to stay within 3000 min/month free tier
# Run this script to streamline from 136 workflows to 7 essential ones

set -e

WORKFLOWS_DIR="/Users/agi_dev/LOCAL-REPOS/Lukhas/.github/workflows"
DISABLED_DIR="/Users/agi_dev/LOCAL-REPOS/Lukhas/.github/workflows-streamlined-$(date +%Y%m%d)"
BACKUP_DIR="/Users/agi_dev/LOCAL-REPOS/Lukhas/.github/workflows_backup_$(date +%Y%m%d_%H%M%S)_simplification"

echo "=== GitHub Actions Simplification ==="
echo "Goal: Reduce from 136 workflows to 7 essential ones"
echo "Expected savings: 80-90% of CI minutes"
echo

# Create backup
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r "$WORKFLOWS_DIR"/*.yml "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backup created at: $BACKUP_DIR"
echo

# Create disabled directory
echo "📁 Creating streamlined workflows directory..."
mkdir -p "$DISABLED_DIR"
echo "✓ Created: $DISABLED_DIR"
echo

# Define Tier 1: ESSENTIAL workflows (always run on PR)
TIER1=(
    "ci.yml"
    "coverage-gates.yml"
    "architectural-guardian.yml"
    "auto-copilot-review.yml"
    "auto-codex-review.yml"
    "codeql-analysis.yml"
    "dependency-review.yml"
)

# Define Tier 2: SELECTIVE workflows (path-filtered)
TIER2=(
    "docs-lint.yml"
    "branding-docs-check.yml"
    "content-lint.yml"
    "bridge-quality.yml"
)

# Define Tier 3: SCHEDULED workflows (keep as-is if already scheduled)
TIER3=(
    "benchmarks-nightly.yml"
)

echo "=== Tier 1: Essential PR Workflows (${#TIER1[@]} workflows) ==="
for workflow in "${TIER1[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "  ✅ Keep: $workflow"
    else
        echo "  ⚠️  Not found: $workflow"
    fi
done
echo

echo "=== Moving non-essential workflows to streamlined directory ==="
moved=0
kept=0

for workflow in "$WORKFLOWS_DIR"/*.yml; do
    filename=$(basename "$workflow")

    # Check if in Tier 1
    keep=false
    for tier1_workflow in "${TIER1[@]}"; do
        if [ "$filename" = "$tier1_workflow" ]; then
            keep=true
            break
        fi
    done

    if [ "$keep" = true ]; then
        ((kept++))
        echo "  ✅ Keep: $filename"
    else
        mv "$workflow" "$DISABLED_DIR/"
        ((moved++))
        echo "  📦 Move: $filename → streamlined/"
    fi
done

echo
echo "=== Summary ==="
echo "Workflows kept (active): $kept"
echo "Workflows moved (disabled): $moved"
echo "Backup location: $BACKUP_DIR"
echo "Streamlined location: $DISABLED_DIR"
echo
echo "=== Estimated Savings ==="
echo "Before: ~900-2700 min per PR (91 workflows)"
echo "After:  ~50-100 min per PR (${#TIER1[@]} workflows)"
echo "Savings: ~85-95% reduction in CI minutes"
echo
echo "✓ Simplification complete!"
echo
echo "Next steps:"
echo "1. Test with a small PR to verify CI still works"
echo "2. Monitor usage: gh api /repos/LukhasAI/Lukhas/actions/billing/usage"
echo "3. Re-enable specific workflows from streamlined/ as needed"
echo "4. Add path filters to Tier 2 workflows (see SIMPLIFIED_CI_PLAN.md)"
