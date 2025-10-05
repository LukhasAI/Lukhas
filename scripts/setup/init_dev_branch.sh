#!/usr/bin/env bash
# T4/0.01% Development Branch Setup
#
# Initializes a new development branch after production freeze.
# Creates proper branch structure, documentation, and safety checks.
#
# Usage:
#   bash scripts/setup/init_dev_branch.sh [branch-name]
#
# Example:
#   bash scripts/setup/init_dev_branch.sh develop/v0.03-prep

set -euo pipefail

# Configuration
FREEZE_TAG="${FREEZE_TAG:-v0.02-final}"
DEFAULT_BRANCH="${1:-develop/v0.03-prep}"
MAIN_BRANCH="${MAIN_BRANCH:-main}"

echo "🚀 T4/0.01% Development Branch Setup"
echo "   Freeze tag: $FREEZE_TAG"
echo "   New branch: $DEFAULT_BRANCH"
echo "   Main branch: $MAIN_BRANCH"
echo ""

# Step 1: Verify we're on main and it's clean
echo "📌 Step 1: Verifying main branch state..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" != "$MAIN_BRANCH" ]; then
    echo "❌ Not on $MAIN_BRANCH branch (currently on: $CURRENT_BRANCH)"
    echo "   Switch to main first: git checkout $MAIN_BRANCH"
    exit 1
fi

if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Working directory has uncommitted changes"
    echo "   Commit or stash changes before creating dev branch"
    exit 1
fi

echo "   ✅ On $MAIN_BRANCH with clean working directory"
echo ""

# Step 2: Verify freeze tag exists
echo "📌 Step 2: Verifying freeze tag..."
if ! git rev-parse "$FREEZE_TAG" >/dev/null 2>&1; then
    echo "❌ Freeze tag not found: $FREEZE_TAG"
    exit 1
fi

FREEZE_COMMIT=$(git rev-parse "$FREEZE_TAG")
echo "   ✅ Freeze tag exists: $FREEZE_TAG ($FREEZE_COMMIT)"
echo ""

# Step 3: Run freeze verification
echo "📌 Step 3: Running freeze integrity check..."
if ! python3 scripts/ci/verify_freeze_state.py --tag "$FREEZE_TAG" --mode strict >/dev/null 2>&1; then
    echo "⚠️  Freeze verification failed - see details above"
    echo "   This is expected if you've made changes after the freeze"
    echo "   Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi
echo ""

# Step 4: Create new development branch
echo "📌 Step 4: Creating development branch: $DEFAULT_BRANCH"

if git rev-parse --verify "$DEFAULT_BRANCH" >/dev/null 2>&1; then
    echo "⚠️  Branch already exists: $DEFAULT_BRANCH"
    echo "   Switch to it? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git checkout "$DEFAULT_BRANCH"
        echo "   ✅ Switched to existing branch"
    else
        echo "Aborted."
        exit 1
    fi
else
    git checkout -b "$DEFAULT_BRANCH"
    echo "   ✅ Created and switched to: $DEFAULT_BRANCH"
fi
echo ""

# Step 5: Create development documentation
echo "📌 Step 5: Setting up development documentation..."

mkdir -p docs/dev

cat > docs/dev/README.md <<EOF
# Development Branch: $DEFAULT_BRANCH

**Created**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Branched from**: $FREEZE_TAG ($FREEZE_COMMIT)
**Base branch**: $MAIN_BRANCH

## Purpose

This branch is for post-freeze development work that cannot be done on the immutable
\`$MAIN_BRANCH\` branch, which is frozen at \`$FREEZE_TAG\`.

## Freeze Status

- **Freeze tag**: $FREEZE_TAG
- **Freeze commit**: $FREEZE_COMMIT
- **Main branch**: IMMUTABLE (no commits allowed after freeze)
- **This branch**: MUTABLE (active development)

## Development Guidelines

1. **Never commit directly to $MAIN_BRANCH** - it is frozen for archival purposes
2. **All new work goes here** - this is the active development branch
3. **Merge strategy**: When ready, create PR from this branch to a new release branch
4. **Testing**: Run full test suite before merging: \`make test-all\`
5. **Validation**: Run T4 checkpoint: \`make validate-t4-strict\`

## Quick Commands

\`\`\`bash
# Verify freeze integrity
make freeze-verify

# Run development server
make dev

# Run tests
make test-all

# Collect coverage
make cov-all

# Generate dashboards
make meta-registry
make trends

# Validate before PR
make validate-t4-strict
\`\`\`

## Coverage Improvement Targets

Based on $FREEZE_TAG baseline (avg health: 20.3/100):

### Priority 1: High-value modules with 0% coverage
- [ ] adapters
- [ ] ai_orchestration
- [ ] governance_extended
- [ ] guardian
- [ ] healing
- [ ] observability

### Priority 2: Modules with <10% coverage
- [ ] consciousness (currently 4.12%)
- [ ] matriz (currently 1.98%)
- [ ] governance (currently 0.23%)

### Goal: Average health score >30/100 by v0.03

## Branching Strategy

\`\`\`
$MAIN_BRANCH (frozen at $FREEZE_TAG)
  └── $DEFAULT_BRANCH (active development)
       ├── feature/new-feature
       ├── fix/bug-fix
       └── refactor/improvement
\`\`\`

## Release Process

1. Complete all development work on this branch
2. Run comprehensive validation: \`make validate-t4-strict\`
3. Create release PR to new release branch
4. Merge and tag new release (e.g., v0.03-prod)
5. Create new dev branch for next iteration

---

*Initialized by T4/0.01% development branch setup*
*Freeze tag: $FREEZE_TAG*
*Branch: $DEFAULT_BRANCH*
EOF

echo "   ✅ Created docs/dev/README.md"
echo ""

# Step 6: Create development changelog
cat > CHANGELOG.dev.md <<EOF
# Development Changelog - $DEFAULT_BRANCH

## Unreleased

### Added
- Development branch initialized from $FREEZE_TAG
- Development documentation in docs/dev/

### Changed
- (Add changes here as development progresses)

### Fixed
- (Add fixes here as development progresses)

---

## Previous Releases

See CHANGELOG.md in $MAIN_BRANCH for release history up to $FREEZE_TAG.

EOF

echo "   ✅ Created CHANGELOG.dev.md"
echo ""

# Step 7: Commit initialization
echo "📌 Step 6: Committing initialization..."

git add docs/dev/README.md CHANGELOG.dev.md
git commit -m "chore(init): initialize $DEFAULT_BRANCH development branch post-freeze

Created from $FREEZE_TAG ($FREEZE_COMMIT)

- Added docs/dev/README.md with development guidelines
- Added CHANGELOG.dev.md for tracking unreleased changes
- Established post-freeze development workflow

Main branch ($MAIN_BRANCH) remains frozen and immutable.
All new development work proceeds on this branch.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "   ✅ Initialization committed"
echo ""

# Step 8: Summary
echo "=" | tr -d '\n'; for i in {1..80}; do echo -n "="; done; echo
echo "✅ DEVELOPMENT BRANCH READY"
echo "=" | tr -d '\n'; for i in {1..80}; do echo -n "="; done; echo
echo ""
echo "Branch: $DEFAULT_BRANCH"
echo "Base: $FREEZE_TAG"
echo "Status: Ready for development"
echo ""
echo "Next steps:"
echo "  1. Push branch: git push -u origin $DEFAULT_BRANCH"
echo "  2. Start development work"
echo "  3. Run tests: make test-all"
echo "  4. Monitor freeze: python3 scripts/guardian/freeze_guardian.py --once"
echo ""
echo "To switch back to main (frozen): git checkout $MAIN_BRANCH"
echo "To continue development: git checkout $DEFAULT_BRANCH"
echo ""
