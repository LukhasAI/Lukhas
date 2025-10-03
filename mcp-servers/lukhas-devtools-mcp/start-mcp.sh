#!/bin/bash

# Start the proper LUKHAS MCP Server with HTTP+SSE transport
echo "🚀 Starting LUKHAS MCP Server (HTTP+SSE)..."

# Use port 8766 for the proper MCP server
export PORT=8766

# Start the MCP server
node mcp-server.mjs