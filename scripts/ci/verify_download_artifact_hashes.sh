#!/usr/bin/env bash
# verify_download_artifact_hashes.sh
# Purpose: Check GitHub Actions download-artifact hash pins against known vulnerable versions
# Vulnerable range: v4.0.0 through v4.1.2
# Safe versions: v3.x, v4.1.3+, v4.1.8 (current recommended)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== GitHub Actions download-artifact Hash Verification ==="
echo "Vulnerable versions: v4.0.0 through v4.1.2"
echo "Safe versions: v3.x, v4.1.3+, v4.1.8 (current)"
echo ""

# Create temporary directory for analysis
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extract all download-artifact references
echo "## Step 1: Extracting all download-artifact references..."
grep -rn "uses:.*actions/download-artifact@" .github/workflows/ > "$TEMP_DIR/all_refs.txt" 2>/dev/null || true

if [ ! -s "$TEMP_DIR/all_refs.txt" ]; then
    echo "No download-artifact references found."
    exit 0
fi

echo "Found $(wc -l < "$TEMP_DIR/all_refs.txt") references"
echo ""

# Categorize by version type
echo "## Step 2: Categorizing by version type..."
echo ""

echo "### Hash-pinned versions (need manual verification):"
grep -E "actions/download-artifact@[a-f0-9]{7,40}" "$TEMP_DIR/all_refs.txt" | while IFS=: read -r file line content; do
    hash=$(echo "$content" | sed -n 's/.*actions\/download-artifact@\([a-f0-9]\{7,40\}\).*/\1/p')
    echo "  $file:$line -> Hash: $hash"
done || echo "  None found"
echo ""

echo "### Tagged versions (v3.x - SAFE):"
grep -E "actions/download-artifact@v3\." "$TEMP_DIR/all_refs.txt" || echo "  None found"
echo ""

echo "### Tagged versions (v4.0.0 - v4.1.2 - VULNERABLE!):"
grep -E "actions/download-artifact@v4\.(0\.[0-9]+|1\.[0-2])" "$TEMP_DIR/all_refs.txt" || echo "  None found"
echo ""

echo "### Tagged versions (v4.1.3+ - SAFE):"
grep -E "actions/download-artifact@v4\.1\.[3-9]|v4\.1\.[1-9][0-9]|v4\.[2-9]\." "$TEMP_DIR/all_refs.txt" || echo "  None found"
echo ""

# Check specific hashes identified in the review
echo "## Step 3: Checking specific hashes from review..."
echo ""

HASH_fa0a91b8="fa0a91b85d4f404e444e00e005971372dc801d16"
HASH_c14a0b9e="c14a0b9e72d31fbb7b7f3466e2a4f96c6498a1b0"

echo "### Checking hash $HASH_fa0a91b8:"
if grep -q "$HASH_fa0a91b8" "$TEMP_DIR/all_refs.txt"; then
    echo "  ⚠️  FOUND - Workflows using this hash:"
    grep "$HASH_fa0a91b8" "$TEMP_DIR/all_refs.txt" | cut -d: -f1 | sort -u | sed 's/^/    - /'
    echo ""
    echo "  ACTION REQUIRED: Verify this hash against actions/download-artifact git tags"
    echo "  Command to check: git ls-remote --tags https://github.com/actions/download-artifact.git | grep $HASH_fa0a91b8"
else
    echo "  ✅ Not found in any workflows"
fi
echo ""

echo "### Checking hash $HASH_c14a0b9e:"
if grep -q "$HASH_c14a0b9e" "$TEMP_DIR/all_refs.txt"; then
    echo "  ⚠️  FOUND - Workflows using this hash:"
    grep "$HASH_c14a0b9e" "$TEMP_DIR/all_refs.txt" | cut -d: -f1 | sort -u | sed 's/^/    - /'
    echo ""
    echo "  ACTION REQUIRED: Verify this hash against actions/download-artifact git tags"
    echo "  Command to check: git ls-remote --tags https://github.com/actions/download-artifact.git | grep $HASH_c14a0b9e"
else
    echo "  ✅ Not found in any workflows"
fi
echo ""

# Generate summary report
echo "## Summary Report"
echo ""

TOTAL_REFS=$(wc -l < "$TEMP_DIR/all_refs.txt")
HASH_PINNED=$(grep -c -E "actions/download-artifact@[a-f0-9]{7,40}" "$TEMP_DIR/all_refs.txt" || echo 0)
V3_SAFE=$(grep -c -E "actions/download-artifact@v3\." "$TEMP_DIR/all_refs.txt" || echo 0)
V4_VULNERABLE=$(grep -c -E "actions/download-artifact@v4\.(0\.[0-9]+|1\.[0-2])" "$TEMP_DIR/all_refs.txt" || echo 0)
V4_SAFE=$(grep -c -E "actions/download-artifact@v4\.1\.[3-9]|v4\.1\.[1-9][0-9]|v4\.[2-9]\." "$TEMP_DIR/all_refs.txt" || echo 0)

echo "Total download-artifact references: $TOTAL_REFS"
echo ""
echo "By version type:"
echo "  - Hash-pinned (needs verification): $HASH_PINNED"
echo "  - v3.x (SAFE): $V3_SAFE"
echo "  - v4.0.0-v4.1.2 (VULNERABLE!): $V4_VULNERABLE"
echo "  - v4.1.3+ (SAFE): $V4_SAFE"
echo ""

if [ "$V4_VULNERABLE" -gt 0 ]; then
    echo "❌ CRITICAL: Found $V4_VULNERABLE vulnerable references!"
    echo "   Update immediately to v4.1.8"
    exit 1
elif [ "$HASH_PINNED" -gt 0 ]; then
    echo "⚠️  WARNING: Found $HASH_PINNED hash-pinned references"
    echo "   Verify these are not in vulnerable range and consider updating to v4.1.8"
    exit 0
else
    echo "✅ All download-artifact references use safe versions"
    exit 0
fi
