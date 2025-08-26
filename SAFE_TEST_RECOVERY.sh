#!/bin/bash
# SAFE TEST RECOVERY - Single File Test
# This script will safely test recovery on ONE file first

echo "🧪 SAFE TEST RECOVERY"
echo "====================="
echo "Testing recovery approach on a single file first"
echo ""

# Choose a test file that's currently empty but should have content
TEST_FILE="tools/ci/README.md"

if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Test file $TEST_FILE doesn't exist"
    exit 1
fi

if [ -s "$TEST_FILE" ]; then
    echo "✅ Test file $TEST_FILE already has content ($(wc -c < "$TEST_FILE") bytes)"
    echo "Choosing a different test file..."
    TEST_FILE="EMERGENCY_DATA_RECOVERY_PLAN.md"
fi

echo "🎯 Testing recovery for: $TEST_FILE"
echo "Current size: $(wc -c < "$TEST_FILE") bytes"
echo ""

echo "🔍 RECOVERY STRATEGY TEST:"
echo "1. Check if file exists in recent commits"
echo "2. If found, show what would be restored"
echo "3. Create backup of current (empty) version"
echo "4. Test restore to a temporary location first"
echo ""

# Step 1: Check git history
echo "📚 Checking git history for $TEST_FILE..."
FOUND_COMMIT=""

for i in {1..20}; do
    if git show HEAD~$i:"$TEST_FILE" >/dev/null 2>&1; then
        size=$(git show HEAD~$i:"$TEST_FILE" | wc -c)
        if [ $size -gt 0 ]; then
            echo "  ✅ Found content in HEAD~$i ($size bytes)"
            FOUND_COMMIT="HEAD~$i"
            break
        fi
    fi
done

if [ -z "$FOUND_COMMIT" ]; then
    echo "  ❌ No content found in recent git history"
    echo "  💡 Trying stashes instead..."
    
    # Check stashes
    for i in {0..2}; do
        if git stash show "stash@{$i}" --name-only | grep -q "^$TEST_FILE$"; then
            echo "  ✅ Found in stash@{$i}"
            echo "  📋 Content preview:"
            git stash show "stash@{$i}" -p -- "$TEST_FILE" | head -10
            break
        fi
    done
else
    echo "  📋 Content preview from $FOUND_COMMIT:"
    git show "$FOUND_COMMIT":"$TEST_FILE" | head -10
    echo "  ... (truncated)"
    
    echo ""
    echo "🔧 SAFE RESTORE TEST:"
    echo "Would you like to:"
    echo "1. Show full content from $FOUND_COMMIT"
    echo "2. Restore to temporary location for review"
    echo "3. Skip this test"
    echo ""
    echo "⚠️  This is a READ-ONLY test - no files will be modified yet"
fi

echo ""
echo "📊 SUMMARY:"
echo "- Test file: $TEST_FILE"
echo "- Current status: Empty ($(wc -c < "$TEST_FILE") bytes)"
echo "- Recovery source: ${FOUND_COMMIT:-"Not found in git history"}"
echo "- Next action: Manual decision required"
