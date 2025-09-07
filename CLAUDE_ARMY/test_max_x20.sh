#!/bin/bash

echo "🧪 Testing Claude Max x20 Deployment"
echo "===================================="

# Test each agent's readiness
agents=(
    "identity-auth-specialist"
    "consent-compliance-specialist"
    "adapter-integration-specialist"
    "context-orchestrator-specialist"
    "testing-devops-specialist"
    "ux-feedback-specialist"
)

for agent in "${agents[@]}"; do
    echo "Testing $agent..."
    if [ -f "workspaces/$agent/config.json" ]; then
        echo "  ✅ Config found"
    else
        echo "  ❌ Config missing"
    fi
done

echo ""
echo "Running coordination test..."
python3 coordination_hub.py
