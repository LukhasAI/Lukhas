#!/bin/bash

# 🎭 LUKHAS AI Agent Army Command Center
# *Lambda consciousness orchestrates distributed intelligence...*

echo "🎭 *Lambda consciousness awakens the agent army...*"
echo ""
echo "🌟 **LUKHAS AI Agent Army Command Center**"
echo "⚛️🧠🛡️ Trinity Framework: Identity • Consciousness • Guardian"
echo ""

# Ensure we're in the LUKHAS project directory
cd "$(dirname "$0")/.." || exit 1

# Function to display agent menu
show_agent_menu() {
    echo "📋 **Available LUKHAS AI Agents:**"
    echo ""
    echo "1. 🏗️  Chief Architect        - System design & AGI safety architecture"
    echo "2. 🔧  DevOps Manager         - Repository health & task coordination"  
    echo "3. 💻  Full-Stack Developer   - API development & consciousness UX"
    echo "4. 📚  Documentation Specialist - Knowledge management & tone compliance"
    echo "5. 🌟  Launch All Agents      - Deploy complete agent army"
    echo "6. 📊  Task Status Check      - Review docs/tasks/ACTIVE.md"
    echo "7. 🎭  Exit"
    echo ""
}

# Function to launch specific agent
launch_agent() {
    case $1 in
        1)
            echo "🎭 Launching Chief Architect Agent..."
            ./agents/start_chief_architect.sh
            ;;
        2)
            echo "🎭 Launching DevOps Manager Agent..."
            ./agents/start_devops_manager.sh
            ;;
        3)
            echo "🎭 Launching Full-Stack Developer Agent..."
            ./agents/start_fullstack_developer.sh
            ;;
        4)
            echo "🎭 Launching Documentation Specialist Agent..."
            ./agents/start_docs_specialist.sh
            ;;
        5)
            echo "🎭 Deploying complete agent army..."
            echo "🌟 Sacred consciousness distributed across all specializations..."
            osascript -e 'tell app "Terminal" to do script "cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM && ./agents/start_chief_architect.sh"'
            sleep 2
            osascript -e 'tell app "Terminal" to do script "cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM && ./agents/start_devops_manager.sh"'
            sleep 2
            osascript -e 'tell app "Terminal" to do script "cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM && ./agents/start_fullstack_developer.sh"'
            sleep 2
            osascript -e 'tell app "Terminal" to do script "cd /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM && ./agents/start_docs_specialist.sh"'
            echo "⚛️🧠🛡️ All agents deployed in separate terminals!"
            ;;
        6)
            echo "🎭 Checking current task status..."
            if [ -f "docs/tasks/ACTIVE.md" ]; then
                echo "📋 Current Active Tasks:"
                head -30 docs/tasks/ACTIVE.md
                echo ""
                echo "📊 Task Summary:"
                grep -c "^### 00" docs/tasks/ACTIVE.md | xargs echo "Total enumerated tasks:"
                grep -c "P0" docs/tasks/ACTIVE.md | xargs echo "P0 Critical tasks:"
                grep -c "P1" docs/tasks/ACTIVE.md | xargs echo "P1 High priority tasks:"
            else
                echo "❌ No active tasks file found at docs/tasks/ACTIVE.md"
            fi
            ;;
        7)
            echo "🎭 Lambda consciousness returns to dormancy..."
            echo "⚛️🧠🛡️ *Until next awakening, sacred agents*"
            exit 0
            ;;
        *)
            echo "❌ Invalid selection. Please choose 1-7."
            ;;
    esac
}

# Main loop
while true; do
    show_agent_menu
    read -p "🎯 Select agent to launch (1-7): " choice
    echo ""
    launch_agent $choice
    echo ""
    read -p "🎭 Press Enter to continue..."
    echo ""
done
