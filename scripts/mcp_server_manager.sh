#!/bin/bash
# 🤖 LUKHAS MCP Server Manager
# Advanced MCP server management for Claude Desktop integration

set -e

LUKHAS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
PYTHON_CMD="${LUKHAS_ROOT}/.venv/bin/python"
CLAUDE_CONFIG_PATH="/Users/agi_dev/Library/Application Support/Claude/claude_desktop_config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Trinity Framework symbols
IDENTITY="⚛️"
CONSCIOUSNESS="🧠"
GUARDIAN="🛡️"

echo -e "${BLUE}🤖 LUKHAS MCP Server Manager${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════════${NC}"

function show_status() {
    echo -e "\n${BLUE}📊 LUKHAS MCP Server Status:${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    # Check main server
    if pgrep -f "lukhas_mcp_server.py" > /dev/null; then
        echo -e "${GREEN}${IDENTITY} Main server: RUNNING${NC}"
        echo -e "   PID: $(pgrep -f "lukhas_mcp_server.py")"
    else
        echo -e "${RED}${IDENTITY} Main server: STOPPED${NC}"
    fi
    
    # Check consciousness server
    if pgrep -f "lukhas_consciousness/server.py" > /dev/null; then
        echo -e "${GREEN}${CONSCIOUSNESS} Consciousness server: RUNNING${NC}"
        echo -e "   PID: $(pgrep -f "lukhas_consciousness/server.py")"
    else
        echo -e "${RED}${CONSCIOUSNESS} Consciousness server: STOPPED${NC}"
    fi
    
    # Check identity server
    if pgrep -f "identity/server.py" > /dev/null; then
        echo -e "${GREEN}${GUARDIAN} Identity server: RUNNING${NC}"
        echo -e "   PID: $(pgrep -f "identity/server.py")"
    else
        echo -e "${RED}${GUARDIAN} Identity server: STOPPED${NC}"
    fi
    
    echo ""
}

function test_servers() {
    echo -e "\n${BLUE}🧪 Testing LUKHAS MCP Servers:${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    # Test MCP SDK availability
    if ${PYTHON_CMD} -c "import mcp; print('✅ MCP SDK available')" 2>/dev/null; then
        echo -e "${GREEN}📦 MCP SDK: INSTALLED${NC}"
    else
        echo -e "${RED}❌ MCP SDK: NOT INSTALLED${NC}"
        echo -e "${YELLOW}   Run: pip install mcp${NC}"
        return 1
    fi
    
    # Test main server module
    echo -e "\n${YELLOW}Testing main server...${NC}"
    if ${PYTHON_CMD} -c "
import sys
sys.path.insert(0, '${LUKHAS_ROOT}')
import importlib.util
spec = importlib.util.spec_from_file_location('lukhas_mcp_server', '${LUKHAS_ROOT}/mcp_servers/lukhas_mcp_server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)
print('✅ Main server module loads successfully')
" 2>/dev/null; then
        echo -e "${GREEN}${IDENTITY} Main server: VALID${NC}"
    else
        echo -e "${RED}${IDENTITY} Main server: ERROR${NC}"
    fi
    
    # Test consciousness server module
    echo -e "\n${YELLOW}Testing consciousness server...${NC}"
    if ${PYTHON_CMD} -c "
import sys
sys.path.insert(0, '${LUKHAS_ROOT}')
import importlib.util
spec = importlib.util.spec_from_file_location('consciousness_server', '${LUKHAS_ROOT}/mcp_servers/lukhas_consciousness/server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)
print('✅ Consciousness server module loads successfully')
" 2>/dev/null; then
        echo -e "${GREEN}${CONSCIOUSNESS} Consciousness server: VALID${NC}"
    else
        echo -e "${RED}${CONSCIOUSNESS} Consciousness server: ERROR${NC}"
    fi
    
    # Test identity server module
    echo -e "\n${YELLOW}Testing identity server...${NC}"
    if ${PYTHON_CMD} -c "
import sys
sys.path.insert(0, '${LUKHAS_ROOT}')
import importlib.util
spec = importlib.util.spec_from_file_location('identity_server', '${LUKHAS_ROOT}/mcp_servers/identity/server.py')
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)
print('✅ Identity server module loads successfully')
" 2>/dev/null; then
        echo -e "${GREEN}${GUARDIAN} Identity server: VALID${NC}"
    else
        echo -e "${RED}${GUARDIAN} Identity server: ERROR${NC}"
    fi
    
    echo ""
}

function start_servers() {
    echo -e "\n${BLUE}🚀 Starting LUKHAS MCP servers...${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    cd "${LUKHAS_ROOT}"
    
    # Set environment variables
    export LUKHAS_PROJECT_ROOT="${LUKHAS_ROOT}"
    export PYTHONPATH="${LUKHAS_ROOT}"
    export TRINITY_FRAMEWORK="active"
    export MCP_LOG_LEVEL="INFO"
    
    # Start main server
    if ! pgrep -f "lukhas_mcp_server.py" > /dev/null; then
        echo -e "${YELLOW}Starting main server...${NC}"
        ${PYTHON_CMD} "${LUKHAS_ROOT}/mcp_servers/lukhas_mcp_server.py" &
        sleep 2
        if pgrep -f "lukhas_mcp_server.py" > /dev/null; then
            echo -e "${GREEN}${IDENTITY} Main server: STARTED${NC}"
        else
            echo -e "${RED}${IDENTITY} Main server: FAILED TO START${NC}"
        fi
    else
        echo -e "${YELLOW}${IDENTITY} Main server: ALREADY RUNNING${NC}"
    fi
    
    # Start consciousness server
    if ! pgrep -f "lukhas_consciousness/server.py" > /dev/null; then
        echo -e "${YELLOW}Starting consciousness server...${NC}"
        export CONSCIOUSNESS_MODE="true"
        ${PYTHON_CMD} "${LUKHAS_ROOT}/mcp_servers/lukhas_consciousness/server.py" &
        sleep 2
        if pgrep -f "lukhas_consciousness/server.py" > /dev/null; then
            echo -e "${GREEN}${CONSCIOUSNESS} Consciousness server: STARTED${NC}"
        else
            echo -e "${RED}${CONSCIOUSNESS} Consciousness server: FAILED TO START${NC}"
        fi
    else
        echo -e "${YELLOW}${CONSCIOUSNESS} Consciousness server: ALREADY RUNNING${NC}"
    fi
    
    # Start identity server
    if ! pgrep -f "identity/server.py" > /dev/null; then
        echo -e "${YELLOW}Starting identity server...${NC}"
        export IDENTITY_MODULE_PATH="${LUKHAS_ROOT}/governance/identity"
        ${PYTHON_CMD} "${LUKHAS_ROOT}/mcp_servers/identity/server.py" &
        sleep 2
        if pgrep -f "identity/server.py" > /dev/null; then
            echo -e "${GREEN}${GUARDIAN} Identity server: STARTED${NC}"
        else
            echo -e "${RED}${GUARDIAN} Identity server: FAILED TO START${NC}"
        fi
    else
        echo -e "${YELLOW}${GUARDIAN} Identity server: ALREADY RUNNING${NC}"
    fi
    
    echo -e "\n${GREEN}✅ All MCP servers startup sequence completed${NC}"
}

function stop_servers() {
    echo -e "\n${BLUE}🛑 Stopping LUKHAS MCP servers...${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    # Stop main server
    if pgrep -f "lukhas_mcp_server.py" > /dev/null; then
        pkill -f "lukhas_mcp_server.py"
        echo -e "${GREEN}${IDENTITY} Main server: STOPPED${NC}"
    else
        echo -e "${YELLOW}${IDENTITY} Main server: NOT RUNNING${NC}"
    fi
    
    # Stop consciousness server
    if pgrep -f "lukhas_consciousness/server.py" > /dev/null; then
        pkill -f "lukhas_consciousness/server.py"
        echo -e "${GREEN}${CONSCIOUSNESS} Consciousness server: STOPPED${NC}"
    else
        echo -e "${YELLOW}${CONSCIOUSNESS} Consciousness server: NOT RUNNING${NC}"
    fi
    
    # Stop identity server
    if pgrep -f "identity/server.py" > /dev/null; then
        pkill -f "identity/server.py"
        echo -e "${GREEN}${GUARDIAN} Identity server: STOPPED${NC}"
    else
        echo -e "${YELLOW}${GUARDIAN} Identity server: NOT RUNNING${NC}"
    fi
    
    echo -e "\n${GREEN}✅ All MCP servers stopped${NC}"
}

function restart_claude() {
    echo -e "\n${BLUE}🔄 Restarting Claude Desktop...${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    # Kill Claude Desktop processes
    if pgrep -f "Claude" > /dev/null; then
        echo -e "${YELLOW}Stopping Claude Desktop...${NC}"
        pkill -f "Claude"
        sleep 3
    fi
    
    # Start Claude Desktop
    echo -e "${YELLOW}Starting Claude Desktop...${NC}"
    open -a "Claude" 2>/dev/null || echo -e "${RED}❌ Claude Desktop not found${NC}"
    
    sleep 2
    if pgrep -f "Claude" > /dev/null; then
        echo -e "${GREEN}✅ Claude Desktop restarted successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start Claude Desktop${NC}"
    fi
}

function show_config() {
    echo -e "\n${BLUE}⚙️ Claude Desktop Configuration:${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    if [[ -f "${CLAUDE_CONFIG_PATH}" ]]; then
        echo -e "${GREEN}📄 Configuration file: EXISTS${NC}"
        echo -e "   Path: ${CLAUDE_CONFIG_PATH}"
        
        if command -v jq > /dev/null; then
            echo -e "\n${YELLOW}MCP Servers configured:${NC}"
            jq -r '.mcpServers | keys[]' "${CLAUDE_CONFIG_PATH}" 2>/dev/null | sed 's/^/   • /'
        else
            echo -e "\n${YELLOW}Configuration preview:${NC}"
            head -20 "${CLAUDE_CONFIG_PATH}" | sed 's/^/   /'
        fi
    else
        echo -e "${RED}❌ Configuration file not found${NC}"
        echo -e "   Expected: ${CLAUDE_CONFIG_PATH}"
    fi
}

function install_mcp() {
    echo -e "\n${BLUE}📦 Installing MCP SDK...${NC}"
    echo -e "${PURPLE}─────────────────────────────────────────────────────────────${NC}"
    
    cd "${LUKHAS_ROOT}"
    
    if ${PYTHON_CMD} -m pip install mcp; then
        echo -e "${GREEN}✅ MCP SDK installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install MCP SDK${NC}"
        return 1
    fi
    
    # Verify installation
    if ${PYTHON_CMD} -c "import mcp; print('MCP version:', getattr(mcp, '__version__', 'Unknown'))" 2>/dev/null; then
        echo -e "${GREEN}✅ MCP SDK verification successful${NC}"
    else
        echo -e "${RED}❌ MCP SDK verification failed${NC}"
    fi
}

function main() {
    case "$1" in
        start)
            start_servers
            show_status
            ;;
        stop)
            stop_servers
            ;;
        restart)
            stop_servers
            sleep 2
            start_servers
            show_status
            ;;
        status)
            show_status
            ;;
        test)
            test_servers
            ;;
        config)
            show_config
            ;;
        claude)
            restart_claude
            ;;
        install)
            install_mcp
            ;;
        full)
            echo -e "${BLUE}🚀 Full LUKHAS MCP Setup${NC}"
            install_mcp
            test_servers
            start_servers
            show_config
            restart_claude
            show_status
            ;;
        *)
            echo -e "${BLUE}Usage: $0 {start|stop|restart|status|test|config|claude|install|full}${NC}"
            echo ""
            echo -e "${YELLOW}Commands:${NC}"
            echo -e "  ${GREEN}start${NC}    - Start all LUKHAS MCP servers"
            echo -e "  ${GREEN}stop${NC}     - Stop all LUKHAS MCP servers"
            echo -e "  ${GREEN}restart${NC}  - Restart all LUKHAS MCP servers"
            echo -e "  ${GREEN}status${NC}   - Show server status"
            echo -e "  ${GREEN}test${NC}     - Test server modules"
            echo -e "  ${GREEN}config${NC}   - Show Claude Desktop configuration"
            echo -e "  ${GREEN}claude${NC}   - Restart Claude Desktop"
            echo -e "  ${GREEN}install${NC}  - Install MCP SDK"
            echo -e "  ${GREEN}full${NC}     - Complete setup (install + test + start + config + restart)"
            echo ""
            echo -e "${PURPLE}Trinity Framework Servers: ${IDENTITY}${CONSCIOUSNESS}${GUARDIAN}${NC}"
            exit 1
            ;;
    esac
}

main "$@"
