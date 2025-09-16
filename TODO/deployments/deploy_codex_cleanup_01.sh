#!/bin/bash
# Deploy Codex-CLEANUP-01 - Tools directory cleanup and automation

echo "🤖 Deploying Codex-CLEANUP-01..."
echo "📋 Task Count: 100"
echo "⏰ Estimated: 24 hours"
echo "🎯 Priority: LOW"

# Create agent workspace
mkdir -p "../agent_workspaces/Codex-CLEANUP-01"
cd "../agent_workspaces/Codex-CLEANUP-01"

# Copy batch configuration
cp "../../agent_batches/BATCH-CODEX-CLEANUP-001.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ Codex-CLEANUP-01 deployed and ready!"
