#!/bin/bash

# 🎖️ CLAUDE ARMY MASTER ORCHESTRATOR
# Coordinates all agent deployments and monitors progress

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         🎖️  CLAUDE ARMY MASTER ORCHESTRATOR 🎖️          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display agent counts
show_agent_summary() {
    echo -e "${CYAN}📊 AGENT ARMY SUMMARY${NC}"
    echo "========================"
    
    # Original 6 agents
    original_count=$(ls -1 .agent_status/*.status 2>/dev/null | wc -l || echo 0)
    echo -e "🎭 Original Agents: ${GREEN}$original_count deployed${NC}"
    
    # Elite agents (12 new)
    elite_count=$(ls -1 CLAUDE_ARMY/ELITE_AGENTS/*.py 2>/dev/null | wc -l || echo 0)
    echo -e "🎖️ Elite Agents: ${PURPLE}$elite_count ready${NC}"
    
    # Total force
    total=$((original_count + elite_count))
    echo -e "💪 Total Force: ${YELLOW}$total agents${NC}"
    echo ""
}

# Function to check system health
check_system_health() {
    echo -e "${BLUE}🏥 SYSTEM HEALTH CHECK${NC}"
    echo "========================"
    
    # Syntax errors
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
    
    if [ "$syntax_errors" -gt 50 ]; then
        echo -e "🐛 Syntax Errors: ${RED}$syntax_errors (CRITICAL)${NC}"
    elif [ "$syntax_errors" -gt 20 ]; then
        echo -e "🐛 Syntax Errors: ${YELLOW}$syntax_errors (WARNING)${NC}"
    else
        echo -e "🐛 Syntax Errors: ${GREEN}$syntax_errors${NC}"
    fi
    
    # Module connections
    connected=$(ls -1 lukhas/*.py 2>/dev/null | wc -l || echo 0)
    echo -e "🔗 Modules Connected: ${CYAN}$connected${NC}"
    
    # Test status
    passing=$(pytest --co -q 2>/dev/null | grep -c "test session" || echo 0)
    echo -e "✅ Tests Passing: ${GREEN}$passing${NC}"
    echo ""
}

# Function to deploy agents by wave
deploy_wave() {
    local wave=$1
    shift
    local agents=("$@")
    
    echo -e "\n${PURPLE}🌊 WAVE $wave DEPLOYMENT${NC}"
    echo "-------------------------"
    
    for agent in "${agents[@]}"; do
        echo -e "  🚀 Deploying ${YELLOW}$agent${NC}..."
        
        # Check if it's an elite agent
        if [ -f "CLAUDE_ARMY/ELITE_AGENTS/${agent}.py" ]; then
            python "CLAUDE_ARMY/ELITE_AGENTS/${agent}.py" > ".agent_results/${agent}.log" 2>&1 &
            echo -e "     ${GREEN}✓${NC} Elite agent launched (PID: $!)"
        else
            echo -e "     ${YELLOW}⚠${NC} Agent script not found, skipping"
        fi
    done
    
    echo -e "  ${GREEN}Wave $wave deployed!${NC}"
    sleep 2
}

# Main orchestration
case "${1:-status}" in
    deploy-all)
        echo -e "${GREEN}🚀 FULL DEPLOYMENT INITIATED${NC}"
        echo ""
        
        show_agent_summary
        check_system_health
        
        # Deploy in waves by priority
        echo -e "${CYAN}📡 DEPLOYING AGENTS IN PRIORITY WAVES${NC}"
        
        # Wave 1: Critical agents
        deploy_wave 1 "syntax_ninja" "module_weaver" "security_sentinel"
        
        # Wave 2: High priority
        deploy_wave 2 "import_surgeon" "api_sniper" "consciousness_linker"
        
        # Wave 3: Medium priority
        deploy_wave 3 "test_commando" "memory_optimizer" "quantum_engineer" "bio_integrator"
        
        # Wave 4: Low priority
        deploy_wave 4 "doc_assassin" "pipeline_architect"
        
        echo ""
        echo -e "${GREEN}✨ ALL AGENTS DEPLOYED!${NC}"
        echo "Monitor with: $0 monitor"
        ;;
        
    monitor)
        echo -e "${BLUE}📊 REAL-TIME AGENT MONITOR${NC}"
        echo ""
        
        show_agent_summary
        check_system_health
        
        echo -e "${CYAN}👥 AGENT STATUS:${NC}"
        echo "=================="
        
        # Check all status files
        for status_file in .agent_status/*.status CLAUDE_ARMY/ELITE_AGENTS/*.status; do
            if [ -f "$status_file" ]; then
                agent=$(basename "$status_file" .status)
                status=$(tail -1 "$status_file" 2>/dev/null || echo "Unknown")
                
                # Color code by status
                if [[ $status == *"COMPLETED"* ]]; then
                    echo -e "  ${GREEN}✅${NC} $agent: $status"
                elif [[ $status == *"ACTIVE"* ]] || [[ $status == *"STARTED"* ]]; then
                    echo -e "  ${YELLOW}🔄${NC} $agent: $status"
                else
                    echo -e "  ${RED}⚠️${NC} $agent: $status"
                fi
            fi
        done
        
        echo ""
        echo -e "${CYAN}📈 RECENT ACTIVITY:${NC}"
        find .agent_results -type f -name "*.log" -o -name "*.json" -mmin -5 2>/dev/null | head -5 | while read file; do
            echo -e "  ${GREEN}•${NC} $(basename $file) ($(stat -f "%Sm" -t "%H:%M" "$file" 2>/dev/null || date))"
        done
        ;;
        
    status)
        show_agent_summary
        check_system_health
        
        echo -e "${YELLOW}💡 QUICK ACTIONS:${NC}"
        echo "  • Deploy all agents:  $0 deploy-all"
        echo "  • Monitor agents:     $0 monitor"
        echo "  • Kill all agents:    $0 kill-all"
        echo "  • View results:       $0 results"
        ;;
        
    kill-all)
        echo -e "${RED}🛑 TERMINATING ALL AGENTS${NC}"
        pkill -f "CLAUDE_ARMY/ELITE_AGENTS" 2>/dev/null || true
        pkill -f "agent.*\.py" 2>/dev/null || true
        echo -e "${GREEN}✓ All agents terminated${NC}"
        ;;
        
    results)
        echo -e "${CYAN}📊 AGENT RESULTS SUMMARY${NC}"
        echo "=========================="
        
        # Count results
        total_results=$(find .agent_results -type f \( -name "*.json" -o -name "*.txt" -o -name "*.log" \) 2>/dev/null | wc -l)
        echo -e "Total result files: ${GREEN}$total_results${NC}"
        
        echo ""
        echo -e "${YELLOW}Recent Results:${NC}"
        find .agent_results -type f -mmin -60 2>/dev/null | head -10 | while read file; do
            size=$(du -h "$file" | cut -f1)
            echo -e "  • $(basename $file) (${size})"
        done
        ;;
        
    *)
        echo "Usage: $0 {status|deploy-all|monitor|kill-all|results}"
        echo ""
        echo "Commands:"
        echo "  status     - Show agent army summary"
        echo "  deploy-all - Deploy all agents in waves"
        echo "  monitor    - Real-time agent monitoring"
        echo "  kill-all   - Terminate all agents"
        echo "  results    - View agent results"
        ;;
esac