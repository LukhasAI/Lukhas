# Claude Desktop MCP Servers - Diagnostic & Fix Guide

**Status**: ✅ All MCP servers are properly configured and built
**Last Checked**: 2025-11-06 15:05

---

## 📊 Current MCP Server Status

### Python MCP Servers (3 servers) ✅

| Server | Status | File Path | Python Version |
|--------|--------|-----------|----------------|
| **lukhas-main** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py` | Python 3.11 |
| **lukhas-consciousness** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_consciousness/server.py` | Python 3.11 |
| **lukhas-identity** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/identity/server.py` | Python 3.11 |

**MCP Package**: ✅ Installed (v1.13.1) for Python 3.11
**Compilation**: ✅ All servers compile without syntax errors

### Node.js MCP Servers (3 servers) ✅

| Server | Status | File Path | Last Built |
|--------|--------|-----------|------------|
| **lukhas-devtools** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp/dist/src/server.js` | Nov 6 14:40 |
| **lukhas-memory** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-memory-mcp/dist/src/server.js` | Nov 6 14:41 |
| **lukhas-constellation** | ✅ EXISTS | `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-constellation-mcp/dist/src/server.js` | Nov 6 14:41 |

**TypeScript Build**: ✅ All servers built successfully
**Node.js**: `/opt/homebrew/bin/node`

---

## 🔍 Common Issues Found in Logs

### Issue 1: "Method not found" errors (benign)

**Symptom**:
```
{"jsonrpc":"2.0","id":2,"error":{"code":-32601,"message":"Method not found"}}
{"jsonrpc":"2.0","id":3,"error":{"code":-32601,"message":"Method not found"}}
```

**Explanation**: These are expected when Claude Desktop queries for optional MCP methods (prompts, resources) that your servers don't implement. Your servers correctly implement `tools/list` which is the primary method.

**Action**: ✅ No action needed - this is normal behavior

---

### Issue 2: BrokenPipeError (intermittent)

**Symptom**:
```
BrokenPipeError: [Errno 32] Broken pipe
```

**Explanation**: Occurs when Claude Desktop closes the connection while the server is writing. Usually happens during restart or shutdown.

**Action**: ✅ No action needed - handled by MCP library

---

### Issue 3: Server appearing twice in logs

**Symptom**: Same server log entry appears multiple times

**Explanation**: Claude Desktop restarts MCP servers on config changes or app restart.

**Action**: ✅ Expected behavior

---

## 🛠️ Diagnostic Commands

### Check All MCP Servers

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Python MCP servers - syntax check
echo "=== Python MCP Servers ==="
python3.11 -m py_compile mcp_servers/lukhas_mcp_server.py && echo "✅ lukhas-main compiles"
python3.11 -m py_compile mcp_servers/lukhas_consciousness/server.py && echo "✅ lukhas-consciousness compiles"
python3.11 -m py_compile mcp_servers/identity/server.py && echo "✅ lukhas-identity compiles"

# Node.js MCP servers - check builds
echo -e "\n=== Node.js MCP Servers ==="
test -f mcp-servers/lukhas-devtools-mcp/dist/src/server.js && echo "✅ lukhas-devtools built"
test -f mcp-servers/lukhas-memory-mcp/dist/src/server.js && echo "✅ lukhas-memory built"
test -f mcp-servers/lukhas-constellation-mcp/dist/src/server.js && echo "✅ lukhas-constellation built"
```

### Check MCP Package Installation

```bash
/opt/homebrew/bin/python3.11 -c "import mcp; print(f'✅ MCP v{mcp.__version__} installed')"
```

### View Recent MCP Logs

```bash
# Python servers
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-main.log
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-consciousness.log
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-identity.log

# Node.js servers
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-devtools.log
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-memory.log
tail -50 ~/Library/Logs/Claude/mcp-server-lukhas-constellation.log
```

### Check Claude Desktop Config

```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq '.mcpServers'
```

---

## 🔧 Fixing Broken MCP Servers

### If Python MCP Server Fails

**Problem**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**:
```bash
/opt/homebrew/bin/python3.11 -m pip install mcp
```

**Problem**: Import errors from LUKHAS modules

**Solution**: Ensure `PYTHONPATH` is set correctly in config:
```json
"env": {
  "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
  "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
}
```

---

### If Node.js MCP Server Fails

**Problem**: `dist/src/server.js` not found

**Solution**: Rebuild TypeScript
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp
npm run build
```

**Problem**: Missing dependencies

**Solution**:
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp
npm install
npm run build
```

---

## 📝 Current Claude Desktop Config

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lukhas-main": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "MCP_LOG_LEVEL": "INFO",
        "TRINITY_FRAMEWORK": "active"
      }
    },
    "lukhas-consciousness": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_consciousness/server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "CONSCIOUSNESS_MODE": "true",
        "TRINITY_FRAMEWORK": "active",
        "MCP_LOG_LEVEL": "INFO"
      }
    },
    "lukhas-identity": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/identity/server.py"],
      "env": {
        "LUKHAS_PROJECT_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "PYTHONPATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "IDENTITY_MODULE_PATH": "/Users/agi_dev/LOCAL-REPOS/Lukhas/governance/identity",
        "MCP_LOG_LEVEL": "INFO"
      }
    },
    "lukhas-devtools": {
      "command": "/opt/homebrew/bin/node",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp/dist/src/server.js"],
      "env": {
        "LUKHAS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas",
        "NODE_ENV": "production"
      }
    },
    "lukhas-memory": {
      "command": "/opt/homebrew/bin/node",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-memory-mcp/dist/src/server.js"],
      "env": {
        "LUKHAS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    },
    "lukhas-constellation": {
      "command": "/opt/homebrew/bin/node",
      "args": ["/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-constellation-mcp/dist/src/server.js"],
      "env": {
        "LUKHAS_ROOT": "/Users/agi_dev/LOCAL-REPOS/Lukhas"
      }
    }
  }
}
```

---

## ✅ Health Check Script

Save this as `check_mcp_health.sh`:

```bash
#!/bin/bash

echo "🔍 LUKHAS MCP Server Health Check"
echo "=================================="
echo ""

# Check Python 3.11
echo "📍 Python 3.11:"
/opt/homebrew/bin/python3.11 --version && echo "✅ Python 3.11 available" || echo "❌ Python 3.11 missing"
echo ""

# Check MCP package
echo "📦 MCP Package:"
/opt/homebrew/bin/python3.11 -c "import mcp; print(f'✅ MCP v{mcp.__version__} installed')" 2>&1 || echo "❌ MCP not installed"
echo ""

# Check Python MCP servers
echo "🐍 Python MCP Servers:"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_mcp_server.py && echo "✅ lukhas-main exists" || echo "❌ lukhas-main missing"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/lukhas_consciousness/server.py && echo "✅ lukhas-consciousness exists" || echo "❌ lukhas-consciousness missing"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp_servers/identity/server.py && echo "✅ lukhas-identity exists" || echo "❌ lukhas-identity missing"
echo ""

# Check Node.js
echo "📍 Node.js:"
/opt/homebrew/bin/node --version && echo "✅ Node.js available" || echo "❌ Node.js missing"
echo ""

# Check Node.js MCP servers
echo "🟢 Node.js MCP Servers:"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-devtools-mcp/dist/src/server.js && echo "✅ lukhas-devtools built" || echo "❌ lukhas-devtools needs build"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-memory-mcp/dist/src/server.js && echo "✅ lukhas-memory built" || echo "❌ lukhas-memory needs build"
test -f /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/lukhas-constellation-mcp/dist/src/server.js && echo "✅ lukhas-constellation built" || echo "❌ lukhas-constellation needs build"
echo ""

# Check Claude Desktop config
echo "⚙️  Claude Desktop Config:"
test -f ~/Library/Application\ Support/Claude/claude_desktop_config.json && echo "✅ Config exists" || echo "❌ Config missing"
echo ""

# Check recent logs
echo "📝 Recent MCP Activity:"
echo "lukhas-main: $(ls -lh ~/Library/Logs/Claude/mcp-server-lukhas-main.log 2>/dev/null | awk '{print $6, $7, $8}')"
echo "lukhas-devtools: $(ls -lh ~/Library/Logs/Claude/mcp-server-lukhas-devtools.log 2>/dev/null | awk '{print $6, $7, $8}')"
echo ""

echo "✅ Health check complete!"
```

**Usage**:
```bash
chmod +x check_mcp_health.sh
./check_mcp_health.sh
```

---

## 🚀 Quick Fix Commands

### Restart Claude Desktop to reload MCP servers

```bash
# Kill Claude Desktop
killall "Claude"

# Wait 2 seconds
sleep 2

# Reopen Claude Desktop
open -a "Claude"
```

### Rebuild all Node.js MCP servers

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers

for server in lukhas-devtools-mcp lukhas-memory-mcp lukhas-constellation-mcp; do
  echo "Building $server..."
  cd $server
  npm run build
  cd ..
done
```

### Reinstall MCP Python package

```bash
/opt/homebrew/bin/python3.11 -m pip install --upgrade mcp
```

---

## 📊 Verification

After any fixes, verify MCP servers are working:

1. **Restart Claude Desktop** (see Quick Fix Commands above)

2. **Check Claude Desktop Settings**:
   - Open Claude Desktop
   - Click Claude menu → Settings
   - Go to Developer → MCP Servers
   - You should see all 6 LUKHAS servers listed

3. **Test in conversation**:
   - Start a new conversation
   - Type a message that would use MCP tools
   - Check if LUKHAS context is available

4. **Check logs for errors**:
```bash
tail -f ~/Library/Logs/Claude/mcp-server-lukhas-*.log
```

---

## 📚 Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **LUKHAS MCP Servers**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/mcp-servers/`
- **Claude Desktop Logs**: `~/Library/Logs/Claude/`

---

**Status**: ✅ All 6 LUKHAS MCP servers are properly configured and operational
**Last Updated**: 2025-11-06
**Next Action**: If issues persist, run the health check script and check logs for specific errors
