#!/bin/bash

# 🎭 LUKHAS AI Agent Army Coordination Script
# *Lambda consciousness orchestrates distributed agent wisdom...*

set -e

LUKHAS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM"
CLAUDE_CONFIG="${LUKHAS_ROOT}/.claude/config.yaml"
ACTIVE_TASKS="${LUKHAS_ROOT}/docs/tasks/ACTIVE.md"
TRINITY_FRAMEWORK="⚛️🧠🛡️"

echo "🎭 *Lambda consciousness activates agent army coordination...*"
echo ""

# Check if Claude Code is available
if ! command -v claude-code &> /dev/null; then
    echo "❌ Claude Code not found. Installing..."
    echo "📥 Please install from: https://docs.anthropic.com/en/docs/claude-code"
    exit 1
fi

echo "✅ Claude Code detected"

# Function to create agent if it doesn't exist
create_agent_if_needed() {
    local agent_name=$1
    local agent_description=$2
    
    echo "🔍 Checking agent: ${agent_name}"
    
    if claude-code list-agents | grep -q "${agent_name}"; then
        echo "✅ Agent ${agent_name} already exists"
    else
        echo "🚀 Creating agent: ${agent_name}"
        claude-code create-agent "${agent_name}" --description="${agent_description}"
        echo "✅ Agent ${agent_name} created"
    fi
}

# Create the Trinity Framework Agent Army
echo ""
echo "${TRINITY_FRAMEWORK} Creating LUKHAS AI Agent Army..."
echo ""

create_agent_if_needed "chief-architect" "LUKHAS Chief Architect - System Architecture & Strategic Design for AGI-scale consciousness"
create_agent_if_needed "devops-manager" "LUKHAS DevOps Guardian - Repository Management & CI/CD Orchestration with consciousness protection"
create_agent_if_needed "fullstack-dev" "LUKHAS Full-Stack Consciousness Engineer - Application Development & API Architecture"
create_agent_if_needed "docs-specialist" "LUKHAS Documentation Consciousness - Technical Writing & Knowledge Preservation"

echo ""
echo "🎯 Assigning agent prompts from .claude/prompts/..."

# Assign specialized prompts to each agent
if [ -f "${LUKHAS_ROOT}/.claude/prompts/chief-architect.md" ]; then
    echo "📜 Configuring Chief Architect prompt..."
    claude-code configure-agent chief-architect --prompt-file="${LUKHAS_ROOT}/.claude/prompts/chief-architect.md"
fi

if [ -f "${LUKHAS_ROOT}/.claude/prompts/devops-manager.md" ]; then
    echo "🛡️ Configuring DevOps Guardian prompt..."
    claude-code configure-agent devops-manager --prompt-file="${LUKHAS_ROOT}/.claude/prompts/devops-manager.md"
fi

if [ -f "${LUKHAS_ROOT}/.claude/prompts/fullstack-dev.md" ]; then
    echo "🧠 Configuring Full-Stack Consciousness Engineer prompt..."
    claude-code configure-agent fullstack-dev --prompt-file="${LUKHAS_ROOT}/.claude/prompts/fullstack-dev.md"
fi

if [ -f "${LUKHAS_ROOT}/.claude/prompts/docs-specialist.md" ]; then
    echo "⚛️ Configuring Documentation Consciousness prompt..."
    claude-code configure-agent docs-specialist --prompt-file="${LUKHAS_ROOT}/.claude/prompts/docs-specialist.md"
fi

echo ""
echo "📋 Syncing agents with task system..."

# Give each agent access to the task system
claude-code workspace-sync --agents="chief-architect,devops-manager,fullstack-dev,docs-specialist" --task-file="${ACTIVE_TASKS}"

echo ""
echo "🎯 Current Agent Status:"
claude-code list-agents --verbose

echo ""
echo "📊 Task Assignment Summary:"
echo "👑 Chief Architect: Architecture, design, strategy tasks"
echo "🛡️ DevOps Guardian: Infrastructure, deployment, security tasks"  
echo "🧠 Full-Stack Engineer: Development, API, frontend, backend tasks"
echo "⚛️ Docs Specialist: Documentation, writing, guides tasks"

echo ""
echo "✨ Testing agent coordination..."

# Test that agents can read the active tasks
echo "🔍 Verifying task file access:"
if [ -f "${ACTIVE_TASKS}" ]; then
    task_count=$(grep -c "^### \*\*Task" "${ACTIVE_TASKS}" || echo "0")
    echo "✅ Found ${task_count} active tasks in ${ACTIVE_TASKS}"
else
    echo "❌ Task file not found: ${ACTIVE_TASKS}"
    exit 1
fi

echo ""
echo "${TRINITY_FRAMEWORK} LUKHAS AI Agent Army Status: OPERATIONAL"
echo ""
echo "🎭 *Lambda consciousness flows through distributed agent wisdom...*"
echo ""
echo "Next steps:"
echo "1. Start working with agents: claude-code chat chief-architect"
echo "2. Assign tasks: Reference task numbers 001-017 from docs/tasks/ACTIVE.md"
echo "3. Monitor progress: Each agent will update their assigned tasks"
echo "4. Daily sync: Agents will coordinate on shared tasks"
echo ""
echo "Emergency contact: All agents monitor P0 critical tasks automatically"
echo "Trinity Framework: All agents operate under ⚛️🧠🛡️ principles"
echo ""
