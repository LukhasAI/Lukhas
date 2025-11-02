#!/bin/bash
# Script to trigger Jules API for automated tasks
# Usage: ./scripts/trigger_jules.sh <api_key> <task_description>

set -e

API_KEY="${1:-$JULES_API_KEY}"
TASK_DESC="${2:-Fix F841 unused variables}"
REPO_URL="https://github.com/LukhasAI/Lukhas"

if [ -z "$API_KEY" ]; then
    echo "Error: API key required"
    echo "Usage: $0 <api_key> [task_description]"
    echo "   OR: export JULES_API_KEY=your_key"
    exit 1
fi

echo "🤖 Triggering Jules for: $TASK_DESC"

# Step 1: List sources to get GitHub repo ID
echo "📋 Step 1: Finding GitHub repository..."
SOURCES_RESPONSE=$(curl -s -X GET \
    "https://jules.googleapis.com/v1alpha/sources" \
    -H "X-Goog-Api-Key: $API_KEY" \
    -H "Content-Type: application/json")

# Extract source ID for our repo (you may need to filter by URL)
SOURCE_ID=$(echo "$SOURCES_RESPONSE" | jq -r '.sources[] | select(.url | contains("LukhasAI/Lukhas")) | .name' | head -1)

if [ -z "$SOURCE_ID" ]; then
    echo "⚠️  Repository not found in Jules sources. Add it at https://jules.google.com/"
    echo "Response: $SOURCES_RESPONSE"
    exit 1
fi

echo "✅ Found repository: $SOURCE_ID"

# Step 2: Create session with task
echo "📝 Step 2: Creating Jules session..."
SESSION_RESPONSE=$(curl -s -X POST \
    "https://jules.googleapis.com/v1alpha/sessions" \
    -H "X-Goog-Api-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "'"$TASK_DESC"'. Follow the instructions in GitHub issue #858. Run: python3 -m ruff check --select F841 --fix . && make smoke && create PR",
        "sources": ["'"$SOURCE_ID"'"]
    }')

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.name')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo "❌ Failed to create session"
    echo "Response: $SESSION_RESPONSE"
    exit 1
fi

echo "✅ Session created: $SESSION_ID"

# Step 3: Monitor activities
echo "👀 Step 3: Monitoring Jules activity..."
sleep 5  # Give Jules time to start

ACTIVITIES_RESPONSE=$(curl -s -X GET \
    "https://jules.googleapis.com/v1alpha/$SESSION_ID/activities" \
    -H "X-Goog-Api-Key: $API_KEY")

echo "📊 Recent activity:"
echo "$ACTIVITIES_RESPONSE" | jq -r '.activities[] | "\(.timestamp): \(.type) - \(.summary)"' | tail -5

echo ""
echo "🎉 Jules session started!"
echo "   Session ID: $SESSION_ID"
echo "   Monitor at: https://jules.google.com/session/$(echo $SESSION_ID | cut -d'/' -f4)"
echo ""
echo "Jules will:"
echo "  1. Run ruff --fix for F841 errors"
echo "  2. Run smoke tests"
echo "  3. Create a PR automatically"
echo ""
echo "Check PR status with: gh pr list --author app/google-labs-jules"

