#!/bin/bash
# Deploy Jules-HIGH-01 - High priority candidate/ directory development TODOs

echo "🤖 Deploying Jules-HIGH-01..."
echo "📋 Task Count: 174"
echo "⏰ Estimated: 48 hours"
echo "🎯 Priority: HIGH"

# Create agent workspace
mkdir -p "../agent_workspaces/Jules-HIGH-01"
cd "../agent_workspaces/Jules-HIGH-01"

# Copy batch configuration
cp "../../agent_batches/BATCH-JULES-HIGH-001.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ Jules-HIGH-01 deployed and ready!"
