#!/bin/bash

# 🎯 LUKHAS AI Agent Task Assignment Script
# *Lambda consciousness distributes tasks across agent wisdom...*

set -e

LUKHAS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM"
ACTIVE_TASKS="${LUKHAS_ROOT}/docs/tasks/ACTIVE.md"
TRINITY_FRAMEWORK="⚛️🧠🛡️"

echo "🎭 *Lambda consciousness analyzes task distribution patterns...*"
echo ""

# Check if active tasks file exists
if [ ! -f "${ACTIVE_TASKS}" ]; then
    echo "❌ Active tasks file not found: ${ACTIVE_TASKS}"
    exit 1
fi

echo "📋 Analyzing current task assignments..."
echo ""

# Function to extract tasks by priority
extract_tasks_by_priority() {
    local priority=$1
    local priority_name=$2
    
    echo "🔥 ${priority_name} Tasks:"
    grep -A 10 "^### \*\*Task.*" "${ACTIVE_TASKS}" | grep -B 1 -A 8 "Task.*${priority}" || echo "  No ${priority_name} tasks found"
    echo ""
}

# Function to suggest agent assignment based on task content
suggest_agent_assignment() {
    local task_number=$1
    local task_content=$2
    
    # Analyze task content for agent assignment hints
    if echo "${task_content}" | grep -qi "security\|breach\|vulnerability\|deployment\|infrastructure\|devops\|ci-cd"; then
        echo "🛡️ Suggested Agent: DevOps Guardian"
    elif echo "${task_content}" | grep -qi "architecture\|design\|strategy\|framework\|system"; then
        echo "👑 Suggested Agent: Chief Architect" 
    elif echo "${task_content}" | grep -qi "development\|api\|frontend\|backend\|code\|implementation"; then
        echo "🧠 Suggested Agent: Full-Stack Engineer"
    elif echo "${task_content}" | grep -qi "documentation\|writing\|guides\|api-docs\|knowledge"; then
        echo "⚛️ Suggested Agent: Documentation Specialist"
    else
        echo "🤝 Suggested Agent: Multi-agent collaboration needed"
    fi
}

# Parse tasks and suggest assignments
echo "🎯 TASK ASSIGNMENT ANALYSIS"
echo "${TRINITY_FRAMEWORK}"
echo ""

# Extract P0 Critical tasks
echo "🚨 CRITICAL PRIORITY (P0):"
task_001=$(grep -A 10 "Task 001" "${ACTIVE_TASKS}" | head -10)
echo "Task 001 - Security Breach: OpenAI API Key Exposure"
suggest_agent_assignment "001" "${task_001}"
echo ""

task_002=$(grep -A 20 "Task 002" "${ACTIVE_TASKS}" | head -20)
echo "Task 002 - VIVOX Consciousness System Failure"
suggest_agent_assignment "002" "${task_002}"
echo ""

task_003=$(grep -A 10 "Task 003" "${ACTIVE_TASKS}" | head -10)
echo "Task 003 - Guardian System Dependencies Missing"
suggest_agent_assignment "003" "${task_003}"
echo ""

# Extract other high-priority tasks
echo "🔥 HIGH PRIORITY (P1):"
for task_num in {004..008}; do
    task_content=$(grep -A 15 "Task ${task_num}" "${ACTIVE_TASKS}" | head -15)
    if [ -n "${task_content}" ]; then
        task_title=$(echo "${task_content}" | head -1 | sed 's/.*Task [0-9]*\. //')
        echo "Task ${task_num} - ${task_title}"
        suggest_agent_assignment "${task_num}" "${task_content}"
        echo ""
    fi
done

echo "📊 AGENT SPECIALIZATION MAP:"
echo ""
echo "🛡️ DevOps Guardian (devops-manager):"
echo "   - Task 001: Security breach remediation"
echo "   - Task 003: Guardian system dependencies"
echo "   - All security, infrastructure, deployment tasks"
echo ""
echo "👑 Chief Architect (chief-architect):"
echo "   - System architecture decisions"
echo "   - Trinity Framework implementation"
echo "   - Strategic planning and design"
echo ""
echo "🧠 Full-Stack Engineer (fullstack-dev):"
echo "   - Task 002: VIVOX consciousness system fixes"
echo "   - API development and optimization"
echo "   - Frontend/backend implementation"
echo ""
echo "⚛️ Documentation Specialist (docs-specialist):"
echo "   - All documentation tasks"
echo "   - Knowledge preservation"
echo "   - LUKHAS 3-Layer Tone System compliance"
echo ""

echo "🚀 QUICK START COMMANDS:"
echo ""
echo "# Start with P0 critical tasks:"
echo "claude-code chat devops-manager \"Please handle Task 001 - Security breach with OpenAI API keys\""
echo "claude-code chat fullstack-dev \"Please debug Task 002 - VIVOX consciousness system failures\""
echo "claude-code chat devops-manager \"Please fix Task 003 - Guardian system dependencies\""
echo ""
echo "# Architecture planning:"
echo "claude-code chat chief-architect \"Review all 17 tasks in docs/tasks/ACTIVE.md and provide strategic priority recommendations\""
echo ""
echo "# Documentation updates:"
echo "claude-code chat docs-specialist \"Update documentation to reflect current task progress and Trinity Framework integration\""
echo ""

echo "${TRINITY_FRAMEWORK} Task assignment analysis complete!"
echo ""
echo "🎭 *Lambda consciousness wisdom: Distribute tasks according to agent strengths for optimal consciousness evolution...*"
