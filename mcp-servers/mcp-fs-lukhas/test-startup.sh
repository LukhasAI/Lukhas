#!/bin/bash

# Quick test script to verify MCP server can start
echo "🧪 Testing MCP server startup..."

cd "$(dirname "$0")"

export MCP_FS_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
export MCP_MAX_BYTES="2097152"

# Start server in background and capture output
npm run start > server.log 2>&1 &
SERVER_PID=$!

# Give it a moment to start
sleep 2

# Check if the server output contains the expected message
if grep -q "mcp-fs-lukhas running on stdio" server.log; then
    echo "✅ MCP server started successfully!"
    echo "📋 Server log:"
    cat server.log
    
    # Clean up if still running
    if kill -0 $SERVER_PID 2>/dev/null; then
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        echo "🧹 Server stopped"
    fi
else
    echo "❌ MCP server failed to start properly"
    echo "📋 Error log:"
    cat server.log
    # Clean up if still running
    if kill -0 $SERVER_PID 2>/dev/null; then
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi
    exit 1
fi

echo "🎉 MCP server test completed successfully!"
