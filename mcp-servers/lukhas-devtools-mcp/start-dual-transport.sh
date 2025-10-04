#!/bin/bash
# Environment configuration for LUKHAS MCP Server

# Repository settings
export LUKHAS_REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
export GITHUB_VIEW_BASE="https://github.com/LukhasAI/Lukhas/blob/main"

# Server settings
export PORT=8766
export NODE_ENV=development

echo "LUKHAS MCP Server Environment:"
echo "  REPO_ROOT: $LUKHAS_REPO_ROOT"
echo "  GITHUB_BASE: $GITHUB_VIEW_BASE"
echo "  PORT: $PORT"
echo ""

# Start the enhanced dual-transport MCP server
cd "$(dirname "$0")"
node mcp-streamable.mjs