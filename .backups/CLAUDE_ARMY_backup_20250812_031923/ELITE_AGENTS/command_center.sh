#!/bin/bash
# 🎖️ ELITE AGENT COMMAND CENTER

echo "🎖️ ELITE AGENT COMMAND CENTER"
echo "=============================="
echo ""

# Function to execute agents by priority
execute_by_priority() {
    local priority=$1
    echo "🚀 Executing $priority priority agents..."
    
    for script in CLAUDE_ARMY/ELITE_AGENTS/*.py; do
        agent_name=$(basename "$script" .py)
        if grep -q "priority.*$priority" "$script"; then
            echo "   Launching $(basename $script .py)..."
            python "$script" &
        fi
    done
}

# Function to monitor all agents
monitor_agents() {
    echo "📊 AGENT STATUS MONITOR"
    echo "----------------------"
    
    for status_file in .agent_status/*.status; do
        if [ -f "$status_file" ]; then
            agent=$(basename "$status_file" .status)
            status=$(tail -1 "$status_file")
            echo "   • $agent: $status"
        fi
    done
}

# Main execution
case "${1:-deploy}" in
    deploy)
        echo "🚀 Deploying all agents by priority..."
        execute_by_priority "CRITICAL"
        sleep 2
        execute_by_priority "HIGH"
        sleep 2
        execute_by_priority "MEDIUM"
        sleep 2
        execute_by_priority "LOW"
        ;;
    monitor)
        monitor_agents
        ;;
    results)
        echo "📊 Agent Results:"
        find .agent_results -name "*.json" -exec echo "   • {}" \;
        ;;
    *)
        echo "Usage: $0 {deploy|monitor|results}"
        ;;
esac
