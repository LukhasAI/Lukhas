#!/usr/bin/env bash
# Release Candidate Automation for LUKHAS MATRIZ
#
# Usage: ./scripts/release_rc.sh v0.9.0-rc
#
# This script:
# 1. Generates CHANGELOG from commits since last tag
# 2. Creates SBOM (Software Bill of Materials)
# 3. Creates GitHub release with CHANGELOG + SBOM
# 4. Validates FREEZE checklist requirements

set -euo pipefail

VER="${1:?usage: $0 vX.Y.Z-rc}"

echo "🚀 Preparing Release Candidate: $VER"
echo "========================================="

# Validate version format
if ! [[ "$VER" =~ ^v[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]*$ ]]; then
    echo "❌ Error: Version must follow format vX.Y.Z-rc or vX.Y.Z-rcN"
    echo "   Example: v0.9.0-rc or v0.9.0-rc2"
    exit 1
fi

# Check prerequisites
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) not found. Install: brew install gh"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# Step 1: Generate CHANGELOG
echo ""
echo "📝 Step 1/4: Generating CHANGELOG..."
if command -v cz &> /dev/null; then
    # Use commitizen for semantic changelog
    cz changelog --incremental --unreleased-version="$VER" > CHANGELOG_RC.md || {
        echo "⚠️  commitizen failed, falling back to git log"
        LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
        if [ -z "$LAST_TAG" ]; then
            git log --oneline --no-merges > CHANGELOG_RC.md
        else
            echo "## Changes since $LAST_TAG" > CHANGELOG_RC.md
            git log --oneline --no-merges "$LAST_TAG..HEAD" >> CHANGELOG_RC.md
        fi
    }
else
    # Fallback: use git log
    echo "⚠️  commitizen not installed, using git log"
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -z "$LAST_TAG" ]; then
        echo "## All Changes" > CHANGELOG_RC.md
        git log --oneline --no-merges >> CHANGELOG_RC.md
    else
        echo "## Changes since $LAST_TAG" > CHANGELOG_RC.md
        git log --oneline --no-merges "$LAST_TAG..HEAD" >> CHANGELOG_RC.md
    fi
fi
echo "✅ CHANGELOG generated: CHANGELOG_RC.md"

# Step 2: Generate SBOM
echo ""
echo "🔒 Step 2/4: Generating SBOM..."
if [ -f scripts/sbom.py ]; then
    python3 scripts/sbom.py || {
        echo "⚠️  SBOM generation failed, continuing anyway"
    }
    if [ -f build/sbom.cyclonedx.json ]; then
        echo "✅ SBOM generated: build/sbom.cyclonedx.json"
    else
        echo "⚠️  SBOM file not found (may not be critical)"
    fi
else
    echo "⚠️  scripts/sbom.py not found, skipping SBOM generation"
fi

# Step 3: Validate FREEZE requirements
echo ""
echo "🧊 Step 3/4: Validating FREEZE checklist..."
WARNINGS=0

# Check smoke tests
if [ -d tests/smoke ]; then
    echo "   - Running smoke tests..."
    if python3 -m pytest tests/smoke/ -q --tb=no &> /dev/null; then
        echo "   ✅ Smoke tests passing"
    else
        echo "   ⚠️  Smoke tests failing"
        ((WARNINGS++))
    fi
else
    echo "   ⚠️  tests/smoke/ not found"
    ((WARNINGS++))
fi

# Check for breaking changes in commits
BREAKING=$(git log --oneline --no-merges "$(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD" | grep -i "BREAKING" || true)
if [ -n "$BREAKING" ]; then
    echo "   ⚠️  Breaking changes detected - ensure migration guide exists"
    ((WARNINGS++))
else
    echo "   ✅ No breaking changes detected"
fi

# Check version in pyproject.toml
if [ -f pyproject.toml ]; then
    PYPROJECT_VER=$(grep "^version = " pyproject.toml | cut -d'"' -f2 || echo "")
    if [ -n "$PYPROJECT_VER" ]; then
        echo "   ✅ Version in pyproject.toml: $PYPROJECT_VER"
    else
        echo "   ⚠️  Version not found in pyproject.toml"
        ((WARNINGS++))
    fi
else
    echo "   ⚠️  pyproject.toml not found"
    ((WARNINGS++))
fi

if [ $WARNINGS -gt 0 ]; then
    echo ""
    echo "⚠️  $WARNINGS warning(s) detected (see above)"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Aborted"
        exit 1
    fi
fi

# Step 4: Create GitHub release
echo ""
echo "🏷️  Step 4/4: Creating GitHub release..."
ASSETS=""
if [ -f build/sbom.cyclonedx.json ]; then
    ASSETS="build/sbom.cyclonedx.json"
fi

gh release create "$VER" \
    --title "Release Candidate $VER" \
    --notes-file CHANGELOG_RC.md \
    --prerelease \
    $ASSETS || {
        echo "❌ GitHub release creation failed"
        echo "   You may need to: gh auth login"
        exit 1
    }

echo ""
echo "✅ Release Candidate $VER prepared and published!"
echo ""
echo "📦 View release: gh release view $VER"
echo "🔗 URL: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases/tag/$VER"
echo ""
echo "Next steps:"
echo "  1. Test the RC in staging environment"
echo "  2. Run full eval suite"
echo "  3. If approved, promote to GA with: gh release edit $VER --prerelease=false"
