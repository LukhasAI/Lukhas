#!/bin/bash
# Deploy Codex-CLEANUP-02 - Legacy code triage and cleanup

echo "🤖 Deploying Codex-CLEANUP-02..."
echo "📋 Task Count: 100"
echo "⏰ Estimated: 24 hours"
echo "🎯 Priority: LOW"

# Create agent workspace
mkdir -p "../agent_workspaces/Codex-CLEANUP-02"
cd "../agent_workspaces/Codex-CLEANUP-02"

# Copy batch configuration
cp "../../agent_batches/BATCH-CODEX-CLEANUP-002.json" ./batch_config.json

# Initialize agent environment
python ../../scripts/initialize_agent.py --batch-config ./batch_config.json

echo "✅ Codex-CLEANUP-02 deployed and ready!"
