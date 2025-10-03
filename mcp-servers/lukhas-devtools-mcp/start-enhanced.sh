#!/bin/bash
# LUKHAS MCP Server - Enhanced with File Editing
# Start script for proper working directory

cd "$(dirname "$0")"
echo "Starting LUKHAS MCP Server from: $(pwd)"
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo ""

# Start the enhanced MCP server
node mcp-streamable.mjs