#!/usr/bin/env bash
set -euo pipefail
echo "🔧 LUKHAS-MCP bootstrap"
: "${LUKHAS_MCP_MODE:=stdio}"
: "${LUKHAS_MCP_CMD:=python3 -m lukhas_mcp_server}"
: "${LUKHAS_MCP_ENDPOINT:=}"
test -f lukhas-mcp/config.yaml || { echo "❌ missing lukhas-mcp/config.yaml"; exit 1; }
echo "✅ MCP config present"
# No-op start hints; real start is done by your host (Claude Code / MCP runner)
echo "ℹ️  Ensure your MCP host points at lukhas-mcp/config.yaml"