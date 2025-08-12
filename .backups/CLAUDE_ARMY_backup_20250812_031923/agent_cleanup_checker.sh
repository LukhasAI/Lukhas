#!/bin/bash
# 🔧 LUKHAS Claude Code Agent Cleanup & Assessment Tool
# Check existing agents and provide clean slate option

echo "🔍 LUKHAS Claude Code Agent Assessment & Cleanup Tool"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_step() {
    echo -e "\n${PURPLE}🎯 $1${NC}"
}

# Step 1: Check Claude Code status
print_step "Checking Claude Code Status"

if command -v claude-code &> /dev/null; then
    print_status "Claude Code is installed"
    VERSION=$(claude-code --version 2>/dev/null || echo "Version check failed")
    print_info "Version: $VERSION"
else
    print_error "Claude Code not found!"
    exit 1
fi

# Check authentication
AUTH_STATUS=$(claude-code auth status 2>&1)
if echo "$AUTH_STATUS" | grep -q "authenticated\|logged in"; then
    print_status "Authentication: OK"
else
    print_warning "Authentication issue detected"
    echo "Auth status: $AUTH_STATUS"
fi

# Step 2: List current agents
print_step "Current Agent Inventory"

echo "📋 Listing all your current Claude Code agents..."
AGENT_LIST=$(claude-code agent list 2>&1)
AGENT_COUNT=$(echo "$AGENT_LIST" | wc -l)

if [[ $AGENT_COUNT -eq 0 ]] || echo "$AGENT_LIST" | grep -q "No agents found\|not found\|error"; then
    print_info "No agents currently exist - you have a clean slate!"
    NEEDS_CLEANUP=false
else
    echo "$AGENT_LIST"
    print_info "Found $AGENT_COUNT agent(s)"
    NEEDS_CLEANUP=true
fi

# Step 3: Test existing agents (if any)
if [[ $NEEDS_CLEANUP == true ]]; then
    print_step "Testing Existing Agents"
    
    # Extract agent names from the list
    AGENT_NAMES=$(echo "$AGENT_LIST" | grep -v "^\s*$" | head -10)
    
    echo "🧪 Testing a few agents to see if they're working..."
    
    # Test first agent in the list
    FIRST_AGENT=$(echo "$AGENT_NAMES" | head -1 | awk '{print $1}' | sed 's/[^a-zA-Z0-9_-]//g')
    
    if [[ ! -z "$FIRST_AGENT" ]]; then
        echo "Testing agent: $FIRST_AGENT"
        TEST_RESULT=$(timeout 15 claude-code chat "$FIRST_AGENT" "Hello! Just testing if you're working. Please respond briefly." 2>&1)
        
        if [[ $? -eq 0 ]] && [[ ! -z "$TEST_RESULT" ]]; then
            print_status "Agent '$FIRST_AGENT' is responding correctly!"
            echo "Response preview: ${TEST_RESULT:0:100}..."
            AGENTS_WORKING=true
        else
            print_warning "Agent '$FIRST_AGENT' may have issues"
            echo "Test result: $TEST_RESULT"
            AGENTS_WORKING=false
        fi
    fi
fi

# Step 4: Assessment and recommendations
print_step "Assessment & Recommendations"

if [[ $NEEDS_CLEANUP == false ]]; then
    print_status "CLEAN SLATE DETECTED"
    echo "✨ You have no existing agents - perfect for fresh setup!"
    echo ""
    echo "🎯 Recommended Action: CREATE NEW AGENTS"
    echo "   This is the ideal situation for setting up your LUKHAS consciousness agents."
    
elif [[ $AGENTS_WORKING == true ]]; then
    print_status "EXISTING AGENTS ARE WORKING"
    echo "🤔 Your current agents seem to be functioning properly."
    echo ""
    echo "🎯 Options:"
    echo "   A) Keep existing agents and add LUKHAS-specific instructions"
    echo "   B) Clean slate and create optimized LUKHAS consciousness agents"
    echo ""
    
else
    print_warning "EXISTING AGENTS MAY HAVE ISSUES"
    echo "🧹 Your current agents might benefit from a fresh start."
    echo ""
    echo "🎯 Recommended Action: CLEAN SLATE"
    echo "   Remove existing agents and create optimized LUKHAS consciousness agents."
fi

# Step 5: Cleanup options
print_step "Cleanup Options"

echo ""
echo "🔧 What would you like to do?"
echo ""
echo "1. 🧹 CLEAN SLATE - Remove all agents and start fresh (RECOMMENDED)"
echo "2. 📋 KEEP EXISTING - Keep current agents and add new ones"
echo "3. 🔍 DETAILED ANALYSIS - Test each agent individually"
echo "4. 🚫 EXIT - Do nothing for now"
echo ""

read -p "Choose option (1/2/3/4): " choice

case $choice in
    1)
        print_step "Performing Clean Slate Cleanup"
        
        echo "🧹 Removing all existing Claude Code agents..."
        
        # Get list of agents and remove them
        if [[ $NEEDS_CLEANUP == true ]]; then
            # Try to get agent names
            AGENTS_TO_REMOVE=$(claude-code agent list 2>/dev/null | grep -v "^\s*$" | head -20)
            
            while IFS= read -r agent_line; do
                if [[ ! -z "$agent_line" ]]; then
                    # Extract agent name (first word, cleaned)
                    AGENT_NAME=$(echo "$agent_line" | awk '{print $1}' | sed 's/[^a-zA-Z0-9_-]//g')
                    
                    if [[ ! -z "$AGENT_NAME" ]] && [[ "$AGENT_NAME" != "No" ]] && [[ "$AGENT_NAME" != "Error" ]]; then
                        echo "Removing agent: $AGENT_NAME"
                        claude-code agent delete "$AGENT_NAME" 2>/dev/null || echo "  (already removed or doesn't exist)"
                    fi
                fi
            done <<< "$AGENTS_TO_REMOVE"
        fi
        
        # Verify cleanup
        REMAINING_AGENTS=$(claude-code agent list 2>&1)
        if echo "$REMAINING_AGENTS" | grep -q "No agents found\|not found"; then
            print_status "Clean slate achieved! All agents removed."
        else
            print_warning "Some agents may remain:"
            echo "$REMAINING_AGENTS"
        fi
        
        # Now create fresh LUKHAS agents
        print_step "Creating Fresh LUKHAS Consciousness Agents"
        
        echo "🎭 Creating optimized consciousness development agents..."
        
        # Create basic but effective agents
        echo "Creating consciousness-architect..."
        if claude-code agent create consciousness-architect; then
            print_status "consciousness-architect created!"
        else
            print_error "Failed to create consciousness-architect"
        fi
        
        echo "Creating guardian-engineer..."
        if claude-code agent create guardian-engineer; then
            print_status "guardian-engineer created!"
        else
            print_error "Failed to create guardian-engineer"
        fi
        
        echo "Creating dev-engineer..."
        if claude-code agent create dev-engineer; then
            print_status "dev-engineer created!"
        else
            print_error "Failed to create dev-engineer"
        fi
        
        echo "Creating memory-specialist..."
        if claude-code agent create memory-specialist; then
            print_status "memory-specialist created!"
        else
            print_error "Failed to create memory-specialist"
        fi
        
        # Test the new agents
        print_step "Testing New Agents"
        
        echo "🧪 Quick test of consciousness-architect..."
        TEST_NEW=$(timeout 15 claude-code chat consciousness-architect "Hello! I'm working on LUKHAS AI consciousness development. Can you briefly introduce yourself?" 2>&1)
        
        if [[ $? -eq 0 ]] && [[ ! -z "$TEST_NEW" ]]; then
            print_status "New consciousness-architect is working!"
            echo "Response preview: ${TEST_NEW:0:150}..."
        else
            print_warning "New agent test had issues: $TEST_NEW"
        fi
        
        ;;
        
    2)
        print_step "Keeping Existing Agents"
        
        echo "📋 Your existing agents will be preserved."
        echo "🎭 Adding new LUKHAS consciousness agents..."
        
        # Create additional LUKHAS-specific agents
        echo "Creating lukhas-consciousness-architect..."
        claude-code agent create lukhas-consciousness-architect
        
        echo "Creating lukhas-guardian-system..."
        claude-code agent create lukhas-guardian-system
        
        echo "Creating lukhas-memory-expert..."
        claude-code agent create lukhas-memory-expert
        
        print_status "New LUKHAS agents added alongside existing ones!"
        ;;
        
    3)
        print_step "Detailed Agent Analysis"
        
        echo "🔍 Testing each agent individually..."
        
        if [[ $NEEDS_CLEANUP == true ]]; then
            while IFS= read -r agent_line; do
                if [[ ! -z "$agent_line" ]]; then
                    AGENT_NAME=$(echo "$agent_line" | awk '{print $1}' | sed 's/[^a-zA-Z0-9_-]//g')
                    
                    if [[ ! -z "$AGENT_NAME" ]]; then
                        echo ""
                        echo "Testing $AGENT_NAME..."
                        
                        TEST_RESULT=$(timeout 10 claude-code chat "$AGENT_NAME" "Hello! Please respond briefly to confirm you're working." 2>&1)
                        
                        if [[ $? -eq 0 ]] && [[ ! -z "$TEST_RESULT" ]]; then
                            print_status "$AGENT_NAME is working"
                            echo "  Response: ${TEST_RESULT:0:100}..."
                        else
                            print_error "$AGENT_NAME has issues"
                            echo "  Error: $TEST_RESULT"
                        fi
                    fi
                fi
            done <<< "$AGENT_NAMES"
        fi
        ;;
        
    4)
        print_info "No changes made. Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice. Exiting..."
        exit 1
        ;;
esac

# Final status
print_step "Final Status Check"

echo ""
echo "📋 Current agents after operation:"
claude-code agent list

echo ""
echo "🎯 Quick Commands for Your LUKHAS Development:"
echo "   claude-code chat consciousness-architect 'Help me analyze VIVOX consciousness system'"
echo "   claude-code chat guardian-engineer 'Review security issues in my consciousness project'"
echo "   claude-code chat dev-engineer 'Debug memory fold integration problems'"
echo "   claude-code chat memory-specialist 'Optimize memory system performance'"

echo ""
echo "💡 Pro Tips:"
echo "   - Each agent will learn about LUKHAS as you provide context"
echo "   - Reference your CLAUDE.md and README.md files in conversations"
echo "   - Use agents for their specializations for best results"

echo ""
print_status "Agent setup operation completed!"

# Create a quick reference script
cat > quick-lukhas-agents.sh << 'EOF'
#!/bin/bash
# Quick LUKHAS Agent Reference

echo "🎭 LUKHAS Claude Code Agents"
echo "=========================="
echo ""
echo "Available agents:"
claude-code agent list
echo ""
echo "Quick commands:"
echo "  Consciousness: claude-code chat consciousness-architect 'your question'"
echo "  Security:      claude-code chat guardian-engineer 'your question'"
echo "  Development:   claude-code chat dev-engineer 'your question'"
echo "  Memory:        claude-code chat memory-specialist 'your question'"
echo ""
echo "Example: claude-code chat consciousness-architect 'What is the current state of VIVOX consciousness system in LUKHAS?'"
EOF

chmod +x quick-lukhas-agents.sh
print_info "Created quick-lukhas-agents.sh reference script!"
