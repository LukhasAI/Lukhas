#!/bin/bash
# Script to trigger Jules API for automated tasks
# Usage: ./scripts/trigger_jules.sh [task_description]

set -e

# Load .env if it exists
if [ -f .env ]; then
    echo "📂 Loading environment from .env"
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Use GOOGLE_API_KEY or JULES_API_KEY
API_KEY="${JULES_API_KEY:-$GOOGLE_API_KEY}"
TASK_DESC="${1:-Fix F841 unused variables from issue #858}"

if [ -z "$API_KEY" ]; then
    echo "❌ Error: API key required"
    echo ""
    echo "Setup options:"
    echo "  1. Add to .env file: GOOGLE_API_KEY=your_key"
    echo "  2. Export in shell: export GOOGLE_API_KEY=your_key"
    echo "  3. Pass as arg: GOOGLE_API_KEY=your_key $0"
    echo ""
    echo "Get API key from: https://makersuite.google.com/app/apikey"
    echo "Or Jules settings: https://jules.google.com/settings"
    exit 1
fi

echo "🤖 Triggering Jules API"
echo "   Task: $TASK_DESC"

# Step 1: List sources to get GitHub repo ID
echo ""
echo "📋 Step 1: Finding GitHub repository..."
SOURCES_RESPONSE=$(curl -s -X GET \
    "https://jules.googleapis.com/v1alpha/sources" \
    -H "X-Goog-Api-Key: $API_KEY" \
    -H "Content-Type: application/json")

# Check for API error
if echo "$SOURCES_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "❌ API Error:"
    echo "$SOURCES_RESPONSE" | jq -r '.error.message'
    echo ""
    echo "Common issues:"
    echo "  - Invalid API key"
    echo "  - Repository not added to Jules sources"
    echo "  - API key doesn't have access to Jules"
    echo ""
    echo "Add repo at: https://jules.google.com/"
    exit 1
fi

# Extract source ID for our repo
SOURCE_ID=$(echo "$SOURCES_RESPONSE" | jq -r '.sources[]? | select(.url | contains("LukhasAI/Lukhas")) | .name' | head -1)

if [ -z "$SOURCE_ID" ]; then
    echo "⚠️  Repository 'LukhasAI/Lukhas' not found in Jules sources"
    echo ""
    echo "Available sources:"
    echo "$SOURCES_RESPONSE" | jq -r '.sources[]? | "  - \(.url)"'
    echo ""
    echo "To add repository:"
    echo "  1. Visit https://jules.google.com/"
    echo "  2. Click 'Add Source'"
    echo "  3. Connect GitHub repo: LukhasAI/Lukhas"
    exit 1
fi

echo "✅ Found repository: $SOURCE_ID"

# Step 2: Create session with task
echo ""
echo "📝 Step 2: Creating Jules session..."
SESSION_RESPONSE=$(curl -s -X POST \
    "https://jules.googleapis.com/v1alpha/sessions" \
    -H "X-Goog-Api-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"prompt\": \"$TASK_DESC. Follow instructions in GitHub issue #858: Run 'python3 -m ruff check --select F841 --fix .' then 'make smoke' then create a PR with the fixes.\",
        \"sources\": [\"$SOURCE_ID\"]
    }")

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.name // empty')

if [ -z "$SESSION_ID" ]; then
    echo "❌ Failed to create session"
    echo "$SESSION_RESPONSE" | jq .
    exit 1
fi

echo "✅ Session created: $SESSION_ID"

# Step 3: Monitor initial activities
echo ""
echo "👀 Step 3: Monitoring Jules activity..."
sleep 3  # Give Jules time to start

ACTIVITIES_RESPONSE=$(curl -s -X GET \
    "https://jules.googleapis.com/v1alpha/$SESSION_ID/activities" \
    -H "X-Goog-Api-Key: $API_KEY")

echo "📊 Recent activity:"
echo "$ACTIVITIES_RESPONSE" | jq -r '.activities[]? | "\(.timestamp // "unknown"): \(.type // "activity") - \(.summary // "processing")"' | head -5

# Extract session ID for URL
SESSION_SHORT_ID=$(echo "$SESSION_ID" | sed 's|.*/||')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Jules session started successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Session ID: $SESSION_ID"
echo "Monitor at: https://jules.google.com/session/$SESSION_SHORT_ID"
echo ""
echo "Jules will:"
echo "  1. ✅ Run ruff --fix for F841 errors (44 violations)"
echo "  2. ✅ Run smoke tests (must pass 10/10)"
echo "  3. ✅ Create a PR automatically"
echo ""
echo "Check PR status:"
echo "  gh pr list --author app/google-labs-jules --limit 5"
echo ""
echo "Monitor progress:"
echo "  ./scripts/check_jules_status.sh $SESSION_SHORT_ID"
echo ""

