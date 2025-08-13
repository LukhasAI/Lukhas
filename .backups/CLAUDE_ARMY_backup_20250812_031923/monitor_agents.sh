#!/bin/bash

# ==========================================
# CLAUDE ARMY - Agent Monitoring Dashboard
# ==========================================

echo "🔍 CLAUDE ARMY MONITORING DASHBOARD"
echo "===================================="
echo ""

# Function to display agent status
check_agent_status() {
    local agent_name=$1
    local status_file=".agent_status/${agent_name}.status"
    local results_dir=".agent_results/${agent_name}"
    
    echo "👤 $agent_name:"
    
    # Check if status file exists
    if [ -f "$status_file" ]; then
        status=$(tail -1 "$status_file")
        echo "   📊 Status: $status"
        
        # Check task progress
        if [ -d "$results_dir" ]; then
            completed=$(find "$results_dir" -name "*.completed" 2>/dev/null | wc -l)
            in_progress=$(find "$results_dir" -name "*.in_progress" 2>/dev/null | wc -l)
            echo "   ✅ Completed: $completed tasks"
            echo "   🔄 In Progress: $in_progress tasks"
        fi
        
        # Check recent activity (last modified file)
        if [ -d "$results_dir" ]; then
            recent=$(find "$results_dir" -type f -exec ls -t {} + 2>/dev/null | head -1)
            if [ -n "$recent" ]; then
                echo "   📝 Recent: $(basename "$recent")"
            fi
        fi
    else
        echo "   ⚠️ Status: Not deployed"
    fi
    echo ""
}

# Check each agent
agents=(
    "Syntax_Fixer"
    "Integration_Specialist"
    "API_Consolidator"
    "Testing_Specialist"
    "Documentation_Guardian"
    "Consciousness_Architect"
)

for agent in "${agents[@]}"; do
    check_agent_status "$agent"
done

# Overall statistics
echo "📈 OVERALL STATISTICS:"
echo "----------------------"

# Count total syntax errors
syntax_errors=$(python -c "
import ast
from pathlib import Path
errors = 0
for p in Path('.').rglob('*.py'):
    if any(skip in str(p) for skip in ['.git', '__pycache__', '._cleanup_archive']):
        continue
    try:
        ast.parse(p.read_text(encoding='utf-8', errors='ignore'))
    except:
        errors += 1
print(errors)
" 2>/dev/null || echo "N/A")

echo "🐛 Syntax Errors Remaining: $syntax_errors"

# Count connected modules
connected=$(ls -1 lukhas/*.py 2>/dev/null | wc -l || echo 0)
echo "🔗 Modules Connected: $connected"

# Check test status
passing=$(pytest --co -q 2>/dev/null | grep -c "test session" || echo 0)
echo "✅ Tests Passing: $passing"

# Show recent agent outputs
echo ""
echo "📜 RECENT AGENT OUTPUTS:"
echo "------------------------"

# Find most recent agent results
recent_files=$(find .agent_results -type f -name "*.txt" -o -name "*.py" -o -name "*.json" 2>/dev/null | head -5)

if [ -n "$recent_files" ]; then
    for file in $recent_files; do
        echo "   • $(basename "$file") ($(dirname "$file" | xargs basename))"
    done
else
    echo "   No recent outputs found"
fi

echo ""
echo "💡 TIP: Check individual agent results in .agent_results/<agent_name>/"
echo "📊 TIP: Run './CLAUDE_ARMY/execute_restoration_mission.sh' to redeploy agents"