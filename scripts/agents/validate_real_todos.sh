#!/bin/bash

# 🎯 LUKHAS Real TODO Task Validator & Registry
# Validates that TODO tasks are from current, legitimate LUKHAS consciousness modules

echo "🔍 Validating LUKHAS Consciousness TODO Tasks..."
echo "⚛️🧠🛡️ Trinity Framework Task Analysis"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TASK_DIR=".claude/tasks/real_consciousness_todos"
VALID_TASKS=0
TOTAL_TASKS=0

echo -e "${BLUE}📋 Analyzing TODO task files...${NC}"

for task_file in "$TASK_DIR"/*.json; do
    if [ -f "$task_file" ]; then
        TOTAL_TASKS=$((TOTAL_TASKS + 1))

        # Extract task info
        task_id=$(jq -r '.task_id' "$task_file")
        title=$(jq -r '.title' "$task_file")
        source_file=$(jq -r '.source_file // .source_files[0]' "$task_file")
        priority=$(jq -r '.priority' "$task_file")
        domain=$(jq -r '.domain' "$task_file")
        trinity_focus=$(jq -r '.trinity_focus' "$task_file")

        echo -e "${PURPLE}🎯 Task: ${task_id}${NC}"
        echo -e "   📂 ${title}"
        echo -e "   🔗 Source: ${source_file}"
        echo -e "   ⭐ Priority: ${priority}"
        echo -e "   🏷️ Domain: ${domain}"
        echo -e "   ${trinity_focus}"

        # Validate source file exists and contains actual TODOs
        if [ -f "$source_file" ]; then
            todo_count=$(grep -c "TODO:" "$source_file" 2>/dev/null || echo "0")
            lambda_todo_count=$(grep -c "ΛTODO:" "$source_file" 2>/dev/null || echo "0")

            if [ "$todo_count" -gt 0 ] || [ "$lambda_todo_count" -gt 0 ]; then
                echo -e "   ✅ ${GREEN}VALID - Source file contains TODOs${NC}"
                VALID_TASKS=$((VALID_TASKS + 1))
            else
                echo -e "   ⚠️ ${YELLOW}WARNING - No TODOs found in source file${NC}"
            fi
        else
            echo -e "   ❌ ${RED}ERROR - Source file not found${NC}"
        fi
        echo ""
    fi
done

echo -e "${PURPLE}📊 VALIDATION SUMMARY${NC}"
echo -e "${BLUE}Total Tasks: ${TOTAL_TASKS}${NC}"
echo -e "${GREEN}Valid Tasks: ${VALID_TASKS}${NC}"

if [ "$VALID_TASKS" -eq "$TOTAL_TASKS" ]; then
    echo -e "${GREEN}🎉 All tasks validated successfully!${NC}"
    echo -e "${PURPLE}Ready for agent army deployment!${NC}"
else
    invalid_count=$((TOTAL_TASKS - VALID_TASKS))
    echo -e "${YELLOW}⚠️ ${invalid_count} tasks need attention${NC}"
fi

echo ""
echo -e "${BLUE}🎭 Agent Army Task Assignment Ready!${NC}"
echo -e "${PURPLE}Trinity Framework: ⚛️🧠🛡️${NC}"
