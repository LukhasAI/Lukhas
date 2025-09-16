#!/bin/bash
# Deploy Jules-MEDIUM - Medium priority feature enhancements and optimizations

echo "🤖 Deploying Jules-MEDIUM..."
echo "📋 Task Count: 16"
echo "⏰ Estimated: 36 hours"
echo "🎯 Priority: MEDIUM"

# Create agent workspace
mkdir -p "../agent_workspaces/Jules-MEDIUM"
cd "../agent_workspaces/Jules-MEDIUM"

# Copy batch configuration
cp "../../agent_batches/BATCH-JULES-MEDIUM-001.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ Jules-MEDIUM deployed and ready!"
