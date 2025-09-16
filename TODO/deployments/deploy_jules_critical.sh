#!/bin/bash
# Deploy Jules-CRITICAL - Critical security, blocking, and safety TODOs requiring immediate attention

echo "🤖 Deploying Jules-CRITICAL..."
echo "📋 Task Count: 20"
echo "⏰ Estimated: 24 hours"
echo "🎯 Priority: CRITICAL"

# Create agent workspace
mkdir -p "../agent_workspaces/Jules-CRITICAL"
cd "../agent_workspaces/Jules-CRITICAL"

# Copy batch configuration
cp "../../agent_batches/BATCH-JULES-CRITICAL-001.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ Jules-CRITICAL deployed and ready!"
