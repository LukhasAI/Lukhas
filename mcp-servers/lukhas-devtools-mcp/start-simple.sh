#!/bin/bash

# Start LUKHAS DevTools MCP Simple Server for ChatGPT
# Simplified JavaScript version without TypeScript dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR"

echo "🚀 Starting LUKHAS DevTools MCP Simple Server..."

cd "$SERVER_DIR"

# Generate token if not provided
if [[ -z "$MCP_HTTP_TOKEN" ]]; then
    echo "🔓 No MCP_HTTP_TOKEN set - running without authentication"
    MCP_HTTP_TOKEN=""
else
    echo "🔑 Using provided token: ${MCP_HTTP_TOKEN:0:8}..."
fi

# Set port
PORT=${PORT:-8764}

echo "📊 Configuration:"
echo "   - Port: $PORT"
echo "   - Token: ${MCP_HTTP_TOKEN:0:8}..."
echo "   - Server: lukhas-devtools-mcp-simple"

# Start the simple JavaScript server
MCP_HTTP_TOKEN="$MCP_HTTP_TOKEN" PORT="$PORT" node http-simple.mjs