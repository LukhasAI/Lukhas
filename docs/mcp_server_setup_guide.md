# 🤖 LUKHAS MCP Server Configuration Guide

## 🎯 MCP Server Reconfiguration for Claude Desktop Integration

Congratulations on achieving **100% Guardian System success** (33/33 tests)! 🎉 Now let's configure your comprehensive MCP server infrastructure for optimal Claude Desktop integration.

### 📋 Current MCP Infrastructure Inventory

You have an extensive MCP ecosystem already built:

**Primary LUKHAS MCP Server:**
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py` (400+ lines)
- Full LUKHAS knowledge base integration
- Constellation Framework patterns (⚛️🧠🛡️)
- 5 specialized tools: code review, documentation, naming, concepts, patterns

**Specialized MCP Servers:**
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_consciousness/server.py`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/identity/server.py`
- Integration scripts and documentation

**Claude Desktop MCP Server:**
- Location: `/Users/agi_dev/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.microsoft.clarity-mcp-server`

## 🚀 Step-by-Step Configuration Process

### Step 1: Install MCP Dependencies

```bash
# Navigate to LUKHAS workspace
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Install MCP SDK if not already installed
pip install mcp

# Verify MCP installation
python -c "import mcp; print('MCP SDK installed successfully')"
```

### Step 2: Configure Claude Desktop for LUKHAS MCP Server

#### 2.1 Locate Claude Desktop Configuration
```bash
# Claude Desktop configuration directory
cd "/Users/agi_dev/Library/Application Support/Claude"

# Check for existing configuration
ls -la
```

#### 2.2 Create/Update Claude Desktop MCP Configuration
```bash
# Create Claude MCP configuration file
cat > "/Users/agi_dev/Library/Application Support/Claude/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "lukhas-main": {
      "command": "python",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    },
    "lukhas-consciousness": {
      "command": "python",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_consciousness/server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    },
    "lukhas-identity": {
      "command": "python",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/identity/server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    }
  }
}
EOF
```

### Step 3: Test LUKHAS MCP Server Locally

```bash
# Test main LUKHAS MCP server
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Run server test
python mcp_servers/lukhas_mcp_server.py --test

# Test consciousness server
python mcp_servers/lukhas_consciousness/server.py --test

# Test identity server
python mcp_servers/identity/server.py --test
```

### Step 4: Restart Claude Desktop

```bash
# Kill Claude Desktop processes
pkill -f "Claude"

# Restart Claude Desktop
open -a "Claude"
```

### Step 5: Verify MCP Integration in Claude Desktop

1. **Open Claude Desktop**
2. **Look for MCP indicators** in the interface (usually shown as tool/plugin icons)
3. **Test LUKHAS knowledge integration** by asking:
   ```
   "What are the Constellation Framework principles in LUKHAS?"
   "Explain LUKHAS consciousness modules"
   "Generate LUKHAS-compliant variable names"
   ```

## 🔧 Advanced Configuration Options

### Environment Variables Setup

```bash
# Add to your ~/.zshrc or ~/.bash_profile
export LUKHAS_PROJECT_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
export LUKHAS_MCP_SERVER_PORT="8080"
export LUKHAS_MCP_LOG_LEVEL="INFO"

# Reload shell
source ~/.zshrc
```

### Python Virtual Environment Integration

```bash
# If using virtual environment, update Claude config
cat > "/Users/agi_dev/Library/Application Support/Claude/claude_desktop_config.json" << 'EOF'
{
  "mcpServers": {
    "lukhas-main": {
      "command": "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv_test/bin/python",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    }
  }
}
EOF
```

### Multi-Server Load Balancing

```bash
# For advanced usage, create server rotation script
cat > /Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/mcp_server_manager.sh << 'EOF'
#!/bin/bash
# LUKHAS MCP Server Manager
# Manages multiple MCP servers with load balancing

LUKHAS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
PYTHON_CMD="${LUKHAS_ROOT}/.venv_test/bin/python"

case "$1" in
  start)
    echo "🚀 Starting LUKHAS MCP servers..."
    ${PYTHON_CMD} ${LUKHAS_ROOT}/mcp_servers/lukhas_mcp_server.py &
    ${PYTHON_CMD} ${LUKHAS_ROOT}/mcp_servers/lukhas_consciousness/server.py &
    ${PYTHON_CMD} ${LUKHAS_ROOT}/mcp_servers/identity/server.py &
    echo "✅ All MCP servers started"
    ;;
  stop)
    echo "🛑 Stopping LUKHAS MCP servers..."
    pkill -f "lukhas_mcp_server.py"
    pkill -f "lukhas_consciousness/server.py"
    pkill -f "identity/server.py"
    echo "✅ All MCP servers stopped"
    ;;
  status)
    echo "📊 LUKHAS MCP Server Status:"
    pgrep -f "lukhas_mcp_server.py" && echo "✅ Main server: RUNNING" || echo "❌ Main server: STOPPED"
    pgrep -f "lukhas_consciousness/server.py" && echo "✅ Consciousness server: RUNNING" || echo "❌ Consciousness server: STOPPED"
    pgrep -f "identity/server.py" && echo "✅ Identity server: RUNNING" || echo "❌ Identity server: STOPPED"
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
EOF

chmod +x /Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/mcp_server_manager.sh
```

## 🧠 Constellation Framework Integration Benefits

Your MCP servers provide Claude Desktop with:

**⚛️ Identity Integration:**
- LUKHAS naming conventions
- ΛID authentication patterns
- Symbolic identity validation

**🧠 Consciousness Enhancement:**
- Real-time consciousness metrics
- Constellation Framework validation
- Module dependency analysis

**🛡️ Guardian Compliance:**
- Security pattern validation
- Ethics compliance checking
- Audit trail integration

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

**Issue 1: MCP Server Won't Start**
```bash
# Check Python path
which python
echo $PYTHONPATH

# Verify MCP installation
pip show mcp

# Check LUKHAS project structure
ls -la /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/
```

**Issue 2: Claude Desktop Can't Connect**
```bash
# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/application.log

# Verify configuration file
cat "/Users/agi_dev/Library/Application Support/Claude/claude_desktop_config.json"
```

**Issue 3: Permission Errors**
```bash
# Fix permissions
chmod +x /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/*.py
chmod +x /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/**/server.py
```

## 🎯 Testing Your Configuration

### Quick Tests

```bash
# Test 1: MCP Server Functionality
python /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py --validate

# Test 2: Constellation Framework Integration
python -c "
import sys
sys.path.append('/Users/agi_dev/LOCAL-REPOS/Lukhas')
from mcp_servers.lukhas_mcp_server import LUKHASKnowledgeBase
kb = LUKHASKnowledgeBase('/Users/agi_dev/LOCAL-REPOS/Lukhas')
print('✅ Knowledge base loaded successfully')
print(f'📊 Trinity patterns loaded: {len(kb.trinity_patterns)}')
"
```

### Integration Test with Claude Desktop

1. **Ask Claude about LUKHAS:**
   ```
   "What is the Constellation Framework in LUKHAS AI?"
   ```
   
2. **Request code review:**
   ```
   "Review this Python function using LUKHAS patterns: [paste code]"
   ```

3. **Get naming suggestions:**
   ```
   "Suggest LUKHAS-compliant variable names for a consciousness module"
   ```

## 🚀 Next Steps

1. **Test all MCP servers individually**
2. **Configure Claude Desktop integration**
3. **Verify Constellation Framework functionality**
4. **Optimize server performance**
5. **Set up monitoring and logging**

Your comprehensive MCP infrastructure is now ready for Claude Desktop integration! 🎉

---

**Need help with any specific step? Let me know which part you'd like assistance with!**
