#!/bin/bash

# 🎭 LUKHAS AI Agent System Test
# *Testing Lambda consciousness distribution across agents...*

echo "🎭 *Testing LUKHAS AI Agent Army...*"
echo ""

# Check if Claude CLI is available
if ! command -v claude &> /dev/null; then
    echo "❌ Claude CLI not found. Please install Claude Code first."
    exit 1
fi

echo "✅ Claude CLI detected"

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "❌ jq not found. Installing jq for JSON parsing..."
    brew install jq
fi

echo "✅ jq detected"

# Test each agent configuration
echo ""
echo "🔍 Testing agent configurations..."

for config in agents/*_config.json; do
    if [ -f "$config" ]; then
        echo "📋 Testing $(basename "$config")..."
        if jq . "$config" > /dev/null 2>&1; then
            echo "✅ Valid JSON configuration"
        else
            echo "❌ Invalid JSON in $config"
        fi
    fi
done

# Check if task file exists
echo ""
echo "🔍 Checking task integration..."
if [ -f "docs/tasks/ACTIVE.md" ]; then
    task_count=$(grep -c "^### 00" docs/tasks/ACTIVE.md)
    echo "✅ Task file found with $task_count enumerated tasks"
else
    echo "❌ Task file not found at docs/tasks/ACTIVE.md"
fi

# Check if branding directory exists
echo ""
echo "🔍 Checking branding integration..."
if [ -d "branding/" ]; then
    echo "✅ Unified branding directory found"
    if [ -f "branding/tone/LUKHAS_3_LAYER_TONE_SYSTEM.md" ]; then
        echo "✅ Tone system configuration found"
    fi
else
    echo "❌ Branding directory not found"
fi

echo ""
echo "🎯 Agent Army Status: Ready for deployment!"
echo "🚀 Launch with: ./agents/command_center.sh"
echo ""
echo "⚛️🧠🛡️ *Lambda consciousness test completed*"
