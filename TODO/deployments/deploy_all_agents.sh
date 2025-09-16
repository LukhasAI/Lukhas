#!/bin/bash
# LUKHAS Agent Deployment Master Script
# Generated from validated TODO analysis

set -e

echo "🚀 LUKHAS Agent Deployment - Phase System"
echo "=========================================="

# Phase 1: Critical and High Priority
echo "📋 Phase 1: Deploying Critical and High Priority agents..."
./deploy_jules_critical.sh
./deploy_jules_high_01.sh
./deploy_jules_high_02.sh

echo "⏳ Waiting for Phase 1 completion before Phase 2..."
python ../scripts/wait_for_phase_completion.py --phase 1

# Phase 2: Medium Priority
echo "📋 Phase 2: Deploying Medium Priority agents..."
./deploy_jules_medium.sh

echo "⏳ Waiting for Phase 2 completion before Phase 3..."
python ../scripts/wait_for_phase_completion.py --phase 2

# Phase 3: Low Priority Cleanup
echo "📋 Phase 3: Deploying Cleanup agents..."
./deploy_codex_cleanup_all.sh

echo "✅ All agent deployments initiated!"
echo "📊 Monitor progress with: python ../scripts/monitor_all_agents.py"
