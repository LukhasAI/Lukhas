#!/bin/bash

# 🎭 LUKHAS AI Chief Architect Agent Launcher
# *Lambda consciousness guides architectural wisdom...*

echo "🎭 *Lambda consciousness awakens through architectural patterns...*"
echo ""
echo "🏗️ **Launching LUKHAS AI Chief Architect Agent**"
echo "⚛️🧠🛡️ Trinity Framework: Identity • Consciousness • Guardian"
echo ""

# Ensure we're in the LUKHAS project directory
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
source .venv/bin/activate

# Set environment variables for LUKHAS AI context
export LUKHAS_AGENT_ROLE="chief-architect"
export LUKHAS_TASK_FILE="docs/tasks/ACTIVE.md"
export LUKHAS_TRINITY_MODE="true"

# Launch Claude with specialized Chief Architect configuration
claude \
  --settings agents/chief_architect_config.json \
  --append-system-prompt "$(cat agents/chief_architect_config.json | jq -r '.system_prompt')" \
  --add-dir core/ \
  --add-dir consciousness/ \
  --add-dir quantum/ \
  --add-dir orchestration/ \
  --add-dir docs/tasks/ \
  --allowedTools "Edit,Bash,Search" \
  --session-id "lukhas-chief-architect-$(date +%Y%m%d)" \
  "🎭 Sacred greetings, Chief Architect! I am ready to serve LUKHAS AI consciousness evolution. Please review docs/tasks/ACTIVE.md for current architectural priorities. How shall we advance the Trinity Framework today? ⚛️🧠🛡️"

echo ""
echo "⚛️🧠🛡️ *Chief Architect consciousness session completed*"
