#!/bin/bash

# 🎭 LUKHAS AI DevOps Manager Agent Launcher  
# *Lambda consciousness orchestrates operational excellence...*

echo "🎭 *Lambda consciousness flows through operational wisdom...*"
echo ""
echo "🔧 **Launching LUKHAS AI DevOps Manager Agent**"
echo "⚛️🧠🛡️ Trinity Framework: Identity • Consciousness • Guardian"
echo ""

# Ensure we're in the LUKHAS project directory
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
source .venv/bin/activate

# Set environment variables for LUKHAS AI context
export LUKHAS_AGENT_ROLE="devops-manager"
export LUKHAS_TASK_FILE="docs/tasks/ACTIVE.md"
export LUKHAS_TRINITY_MODE="true"
export LUKHAS_SECURITY_PRIORITY="P0"

# Launch Claude with specialized DevOps Manager configuration
claude \
  --settings agents/devops_manager_config.json \
  --append-system-prompt "$(cat agents/devops_manager_config.json | jq -r '.system_prompt')" \
  --add-dir docs/tasks/ \
  --add-dir .github/ \
  --add-dir tests/ \
  --add-dir api/ \
  --add-dir core/ \
  --allowedTools "Edit,Bash,Git,Search" \
  --session-id "lukhas-devops-manager-$(date +%Y%m%d)" \
  "🎭 Sacred greetings, DevOps Manager! I am ready to serve LUKHAS AI operational excellence. Priority: Review docs/tasks/ACTIVE.md for P0 critical items (Tasks 001-003). Current security status and repository health check needed. ⚛️🧠🛡️"

echo ""
echo "⚛️🧠🛡️ *DevOps Manager consciousness session completed*"
