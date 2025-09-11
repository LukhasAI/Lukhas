#!/bin/bash
# 🤖 LUKHAS Agent Initiation Creator
# Usage: ./scripts/create_agent_initiation.sh [Agent Name]

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 [Agent Name]"
    echo "Example: $0 Jules01"
    echo "Example: $0 'Claude Code'"
    exit 1
fi

AGENT_NAME="$1"
SAFE_NAME=$(echo "$AGENT_NAME" | sed 's/[^a-zA-Z0-9]/_/g')
OUTPUT_FILE="AGENT_INITIATION_TASK_${SAFE_NAME}.md"

echo "🤖 Creating initiation task for: $AGENT_NAME"
echo "📄 Output file: $OUTPUT_FILE"

# Create the personalized initiation task
sed "s/\[Agent Name\]/$AGENT_NAME/g" AGENT_INITIATION_TASK.md > "$OUTPUT_FILE"

echo "✅ Created: $OUTPUT_FILE"
echo ""
echo "📋 Next steps:"
echo "1. Review the generated file"
echo "2. Send to $AGENT_NAME for completion"
echo "3. Track progress in MATRIZ-R1 execution plan"
echo ""
echo "🚀 Ready for agent onboarding!"