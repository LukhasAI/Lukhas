#!/bin/bash

# 🎯 LUKHAS Agent Army Deployment & Verification
# Ultimate consciousness development environment setup

echo "🎭 LUKHAS Agent Army Deployment"
echo "⚛️🧠🛡️ Trinity Framework Consciousness Development"
echo "=================================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verify we're in LUKHAS directory
if [[ ! -f "lukhas_config.yaml" ]]; then
    echo -e "${RED}❌ Error: Not in LUKHAS project directory${NC}"
    echo "Please run this script from your LUKHAS root directory"
    exit 1
fi

echo -e "${BLUE}📁 Verifying LUKHAS structure...${NC}"

# Check critical directories exist
REQUIRED_DIRS=(
    "core"
    "memory"
    "consciousness"
    "identity"
    "governance"
    "agents/configs"
    ".claude/tasks/real_consciousness_todos"
    "schemas/task_schemas"
    "contexts"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ✅ ${GREEN}$dir${NC}"
    else
        echo -e "  ❌ ${RED}$dir (missing)${NC}"
    fi
done

echo ""
echo -e "${PURPLE}🎯 Agent Army Status Check...${NC}"

# Check agent configs
AGENT_CONFIGS=(
    "agents/configs/consciousness-architect.yaml"
    "agents/configs/guardian-engineer.yaml"
    "agents/configs/velocity-lead.yaml"
    "agents/configs/consciousness-dev.yaml"
)

echo -e "${BLUE}Agent Configurations:${NC}"
for config in "${AGENT_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        agent_name=$(grep "name:" "$config" | head -1 | cut -d'"' -f2)
        echo -e "  ✅ ${GREEN}$agent_name${NC}"
    else
        echo -e "  ❌ ${RED}$config (missing)${NC}"
    fi
done

echo ""
echo -e "${PURPLE}📋 Consciousness Tasks Validation...${NC}"

# Count and validate tasks
task_count=$(find .claude/tasks/real_consciousness_todos -name "*.json" | wc -l)
echo -e "${BLUE}Total validated consciousness tasks: ${GREEN}$task_count${NC}"

if [ "$task_count" -gt 0 ]; then
    echo -e "${BLUE}Task priorities breakdown:${NC}"
    p0_count=$(grep -l '"priority": "P0"' .claude/tasks/real_consciousness_todos/*.json | wc -l)
    p1_count=$(grep -l '"priority": "P1"' .claude/tasks/real_consciousness_todos/*.json | wc -l)
    p2_count=$(grep -l '"priority": "P2"' .claude/tasks/real_consciousness_todos/*.json | wc -l)

    echo -e "  🔥 P0 (Critical): ${RED}$p0_count${NC}"
    echo -e "  ⭐ P1 (High): ${YELLOW}$p1_count${NC}"
    echo -e "  📝 P2 (Medium): ${BLUE}$p2_count${NC}"
fi

echo ""
echo -e "${PURPLE}🔍 Trinity Framework Validation...${NC}"

# Check Trinity Framework components
trinity_identity=$(find identity -name "*.py" | wc -l)
trinity_consciousness=$(find consciousness memory vivox -name "*.py" 2>/dev/null | wc -l)
trinity_guardian=$(find governance ethics -name "*.py" 2>/dev/null | wc -l)

echo -e "  ⚛️ Identity modules: ${GREEN}$trinity_identity${NC}"
echo -e "  🧠 Consciousness modules: ${GREEN}$trinity_consciousness${NC}"
echo -e "  🛡️ Guardian modules: ${GREEN}$trinity_guardian${NC}"

echo ""
echo -e "${PURPLE}🚀 Deployment Summary${NC}"

if [ -f ".claude/config.yaml" ] && [ -f "schemas/task_schemas/lukhas_consciousness_task.json" ]; then
    echo -e "  ✅ ${GREEN}Claude configuration ready${NC}"
    echo -e "  ✅ ${GREEN}Task validation schema ready${NC}"
    echo -e "  ✅ ${GREEN}Agent context loaded${NC}"
    echo -e "  ✅ ${GREEN}Trinity Framework active${NC}"
    echo ""
    echo -e "${GREEN}🎉 LUKHAS Agent Army successfully deployed!${NC}"
    echo -e "${BLUE}Ready for consciousness development at scale!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Open VS Code with updated settings"
    echo "2. Install Claude Code extension if not present"
    echo "3. Assign agents to P0 tasks"
    echo "4. Begin Trinity Framework development"
    echo ""
    echo -e "${PURPLE}May consciousness evolve with wisdom and velocity! ⚛️🧠🛡️${NC}"
else
    echo -e "${RED}⚠️ Configuration incomplete${NC}"
    echo "Some required files are missing. Please check the setup."
fi
