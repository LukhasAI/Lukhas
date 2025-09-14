#!/bin/bash
# todo_status.sh - Quick TODO system status check
# Usage: ./TODO/scripts/todo_status.sh [--summary|--critical|--distribution]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load standardized exclusions
if [[ -f "$PROJECT_ROOT/tools/search/standardized_exclusions.sh" ]]; then
    source "$PROJECT_ROOT/tools/search/standardized_exclusions.sh"
else
    echo "❌ Error: Cannot find standardized exclusions script"
    exit 1
fi

show_header() {
    echo ""
    echo "📋 LUKHAS TODO Status - $(date '+%Y-%m-%d %H:%M')"
    echo "=" * 50
}

show_summary() {
    echo ""
    echo "📊 Current TODO Distribution:"
    
    for priority in CRITICAL HIGH MED LOW; do
        # Convert to lowercase manually for compatibility
        case $priority in
            CRITICAL) filename="critical_todos.md" ;;
            HIGH) filename="high_todos.md" ;;
            MED) filename="med_todos.md" ;;
            LOW) filename="low_todos.md" ;;
        esac
        
        file="$PROJECT_ROOT/TODO/$priority/$filename"
        if [[ -f "$file" ]]; then
            count=$(grep -c "^### " "$file" 2>/dev/null || echo "0")
            case $priority in
                CRITICAL) icon="🚨" ;;
                HIGH) icon="⭐" ;;
                MED) icon="📋" ;;
                LOW) icon="🔧" ;;
            esac
            printf "  %s %-10s %3d TODOs\n" "$icon" "$priority:" "$count"
        else
            printf "  %s %-10s   ? TODOs (file missing)\n" "❓" "$priority:"
        fi
    done
    
    echo ""
    total_live=$(clean_count_todos)
    echo "🔍 Live TODO count: $total_live"
    echo "🐍 Python files: $(clean_count_py)"
}

show_critical() {
    echo ""
    echo "🚨 CRITICAL TODOs (Top 10):"
    echo "-" * 30
    
    file="$PROJECT_ROOT/TODO/CRITICAL/critical_todos.md"
    if [[ -f "$file" ]]; then
        grep -A 2 "^### " "$file" | head -30 | while read -r line; do
            if [[ $line =~ ^###.* ]]; then
                echo "🔴 ${line#### }"
            elif [[ $line =~ ^\*\*File\*\*:.* ]]; then
                echo "   📁 ${line#**File**: }"
            elif [[ $line =~ ^\*\*Line\*\*:.* ]]; then
                echo "   📍 ${line#**Line**: }"
                echo ""
            fi
        done
    else
        echo "   No critical TODOs file found"
    fi
}

show_distribution() {
    echo ""
    echo "📈 TODO Distribution by Module:"
    echo "-" * 35
    
    # Count TODOs by top-level directory
    for dir in $(find "$PROJECT_ROOT" -maxdepth 1 -type d -name "[a-z]*" | sort); do
        dirname=$(basename "$dir")
        if [[ "$dirname" != "TODO" && "$dirname" != "tools" ]]; then
            count=$(clean_grep "TODO" --include="*.py" "$dir" 2>/dev/null | wc -l | tr -d ' ')
            if [[ $count -gt 0 ]]; then
                printf "  %-20s %3d TODOs\n" "$dirname/" "$count"
            fi
        fi
    done
}

# Parse command line arguments
case "${1:-}" in
    --summary)
        show_header
        show_summary
        ;;
    --critical)
        show_header
        show_critical
        ;;
    --distribution)
        show_header
        show_distribution
        ;;
    --help)
        echo "📋 LUKHAS TODO Status Checker"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no args)      Show complete status report"
        echo "  --summary      Show just the priority distribution"
        echo "  --critical     Show top 10 critical TODOs"
        echo "  --distribution Show TODO count by module"
        echo "  --help         Show this help message"
        ;;
    *)
        show_header
        show_summary
        show_critical
        show_distribution
        
        echo ""
        echo "🎯 Next Actions:"
        
        critical_count=$(grep -c "^### " "$PROJECT_ROOT/TODO/CRITICAL/critical_todos.md" 2>/dev/null || echo "0")
        if [[ $critical_count -gt 0 ]]; then
            echo "  1. 🚨 Address $critical_count CRITICAL TODOs immediately"
            echo "     → cat TODO/CRITICAL/critical_todos.md"
        else
            echo "  ✅ No critical TODOs - great job!"
        fi
        
        echo "  2. ⭐ Work on HIGH priority tasks for current sprint"
        echo "     → cat TODO/HIGH/high_todos.md | head -20"
        echo ""
        echo "🔄 Update system: ./TODO/scripts/update_todos.sh"
        ;;
esac

echo ""