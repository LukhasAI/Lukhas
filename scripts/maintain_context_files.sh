#!/bin/bash
# LUKHAS Context Files Maintenance Script
# Complete maintenance and automation for context file management

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🛠️  LUKHAS Context Files Maintenance"
echo "================================="
echo ""

show_menu() {
    echo "Select an option:"
    echo ""
    echo "1) 🔍 Check sync status"
    echo "2) 🔄 Sync all files (bidirectional)"
    echo "3) ➡️  Sync claude.me → lukhas_context.md"
    echo "4) ⬅️  Sync lukhas_context.md → claude.me"
    echo "5) ➕ Add missing partner files"
    echo "6) 🎯 Dry run (preview changes)"
    echo "7) 📊 Show file statistics"
    echo "8) 🔧 Setup automatic sync"
    echo "9) ❓ Show sync script help"
    echo "0) 🚪 Exit"
    echo ""
}

show_statistics() {
    echo -e "${BLUE}Context Files Statistics:${NC}"
    echo ""

    local claude_count=$(find . -name "claude.me" | wc -l | tr -d ' ')
    local lukhas_count=$(find . -name "lukhas_context.md" | wc -l | tr -d ' ')
    local total_size=$(find . -name "claude.me" -o -name "lukhas_context.md" -exec wc -c {} + | tail -1 | awk '{print $1}')

    echo "📁 File counts:"
    echo "   claude.me files: $claude_count"
    echo "   lukhas_context.md files: $lukhas_count"
    echo "   Total size: $(numfmt --to=iec $total_size)"
    echo ""

    echo "📍 Directory coverage:"
    find . -name "claude.me" -exec dirname {} \; | sort | head -5 | while read dir; do
        echo "   $dir/"
    done
    echo "   ... (showing first 5 directories)"
    echo ""

    echo "🔄 Recent changes:"
    find . -name "claude.me" -o -name "lukhas_context.md" -newermt "1 day ago" | head -5 | while read file; do
        echo "   $file (modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file"))"
    done
    echo ""
}

setup_automatic_sync() {
    echo -e "${BLUE}Setting up automatic sync...${NC}"
    echo ""

    # Create a simple wrapper script for git operations
    cat > scripts/git_with_sync.sh << 'EOF'
#!/bin/bash
# Git wrapper that automatically syncs context files

# Run the git command
git "$@"

# If it was a commit or merge, check sync status
if [[ "$1" == "commit" || "$1" == "merge" ]]; then
    echo ""
    echo "🔍 Checking context file sync..."
    if ./scripts/sync_context_files.sh --check-status 2>/dev/null | grep -q "OUT OF SYNC"; then
        echo "⚠️  Some context files are out of sync"
        echo "💡 Run: ./scripts/sync_context_files.sh --bidirectional"
    else
        echo "✅ Context files are synchronized"
    fi
fi
EOF

    chmod +x scripts/git_with_sync.sh

    echo "✅ Created scripts/git_with_sync.sh"
    echo ""
    echo "Usage options:"
    echo "1) Use wrapper: ./scripts/git_with_sync.sh commit -m 'message'"
    echo "2) Manual sync: Run ./scripts/sync_context_files.sh as needed"
    echo "3) VS Code task: Add sync task to tasks.json"
    echo ""
}

# Main menu loop
while true; do
    show_menu
    read -p "Enter your choice [0-9]: " choice
    echo ""

    case $choice in
        1)
            echo -e "${BLUE}Checking sync status...${NC}"
            ./scripts/sync_context_files.sh --check-status
            ;;
        2)
            echo -e "${BLUE}Running bidirectional sync...${NC}"
            ./scripts/sync_context_files.sh --bidirectional
            ;;
        3)
            echo -e "${BLUE}Syncing claude.me → lukhas_context.md...${NC}"
            ./scripts/sync_context_files.sh --claude-to-lukhas
            ;;
        4)
            echo -e "${BLUE}Syncing lukhas_context.md → claude.me...${NC}"
            ./scripts/sync_context_files.sh --lukhas-to-claude
            ;;
        5)
            echo -e "${BLUE}Adding missing partner files...${NC}"
            ./scripts/sync_context_files.sh --add-missing
            ;;
        6)
            echo -e "${BLUE}Dry run preview...${NC}"
            ./scripts/sync_context_files.sh --bidirectional --dry-run
            ;;
        7)
            show_statistics
            ;;
        8)
            setup_automatic_sync
            ;;
        9)
            ./scripts/sync_context_files.sh --help
            ;;
        0)
            echo -e "${GREEN}Goodbye! 👋${NC}"
            break
            ;;
        *)
            echo -e "${RED}Invalid choice. Please try again.${NC}"
            ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
    echo ""
done
