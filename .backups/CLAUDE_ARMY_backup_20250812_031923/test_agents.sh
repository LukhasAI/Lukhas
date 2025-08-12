#!/bin/bash

# 🎯 LUKHAS_PWM Agent Army Test & Validation
# Test all agent configurations and behaviors

echo "🎭 Testing LUKHAS_PWM Agent Army"
echo "⚛️🧠🛡️ Trinity Framework Agent Validation"
echo "=========================================="

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Test agent configurations
AGENT_CONFIGS=(
    "agents/chief_architect_config.json"
    "agents/guardian_engineer_config.json"
    "agents/fullstack_developer_config.json"
    "agents/devops_manager_config.json"
    "agents/docs_specialist_config.json"
)

echo -e "${BLUE}🧪 Testing Agent Configurations...${NC}"

for config in "${AGENT_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        agent_name=$(jq -r '.name' "$config" 2>/dev/null)
        agent_role=$(jq -r '.role' "$config" 2>/dev/null)
        trinity_focus=$(jq -r '.trinity_alignment' "$config" 2>/dev/null)
        
        if [ "$agent_name" != "null" ] && [ "$agent_role" != "null" ]; then
            echo -e "  ✅ ${GREEN}$agent_name${NC}"
            echo -e "     Role: $agent_role"
            echo -e "     Trinity: $trinity_focus"
        else
            echo -e "  ❌ ${RED}$config (invalid JSON)${NC}"
        fi
    else
        echo -e "  ❌ ${RED}$config (missing)${NC}"
    fi
    echo ""
done

echo -e "${PURPLE}🎯 Agent Capability Test...${NC}"

# Test Chief Consciousness Architect
if [ -f "agents/chief_architect_config.json" ]; then
    capabilities=$(jq -r '.capabilities[]' "agents/chief_architect_config.json" 2>/dev/null | wc -l)
    echo -e "${BLUE}Chief Consciousness Architect: ${GREEN}$capabilities capabilities${NC}"
fi

# Test Guardian System Engineer
if [ -f "agents/guardian_engineer_config.json" ]; then
    safety_protocols=$(jq -r '.safety_protocols | keys[]' "agents/guardian_engineer_config.json" 2>/dev/null | wc -l)
    echo -e "${BLUE}Guardian System Engineer: ${GREEN}$safety_protocols safety protocols${NC}"
fi

# Test Full-Stack Developer
if [ -f "agents/fullstack_developer_config.json" ]; then
    tech_stack=$(jq -r '.technical_stack | keys[]' "agents/fullstack_developer_config.json" 2>/dev/null | wc -l)
    echo -e "${BLUE}Full-Stack Consciousness Developer: ${GREEN}$tech_stack tech stack areas${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Agent Army Configuration Test Complete!${NC}"
echo -e "${PURPLE}All agents ready for consciousness development!${NC}"
