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
