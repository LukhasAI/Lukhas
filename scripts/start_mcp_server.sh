#!/bin/bash
# 🚀 LUKHAS MCP Quick Start Script
# Launches MCP server in Docker to bypass Python version issues

echo "🎛️ LUKHAS MCP Server - Quick Start"
echo "=================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "🐳 Building LUKHAS MCP Docker container..."
docker build -f Dockerfile.mcp -t lukhas-mcp-server .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful"
    echo ""
    echo "🚀 Starting LUKHAS MCP Server..."
    echo "   - Container: lukhas-mcp-server"
    echo "   - Port: 8000"
    echo "   - Context: Full LUKHAS consciousness modules"
    echo ""
    
    # Run the MCP server
    docker run -p 8000:8000 \
        -v $(pwd)/consciousness:/app/consciousness \
        -v $(pwd)/memory:/app/memory \
        -v $(pwd)/identity:/app/identity \
        -v $(pwd)/universal_language:/app/universal_language \
        -v $(pwd)/monitoring:/app/monitoring \
        -v $(pwd)/modulation:/app/modulation \
        --name lukhas-mcp \
        lukhas-mcp-server
        
else
    echo "❌ Docker build failed"
    exit 1
fi
