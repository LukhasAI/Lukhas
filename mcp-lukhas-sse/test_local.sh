#!/bin/bash
# 🧪 Quick Local Test Script

echo "🧪 LUKHAS MCP OAuth 2.1 Local Test"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Please run this from the mcp-lukhas-sse directory"
    exit 1
fi

# Copy local config
echo "📋 Setting up local configuration..."
cp .env.local .env

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q fastmcp python-jose[cryptography] httpx uvicorn fastapi

# Generate test JWT
echo "🔑 Generating test JWT token..."
python generate_test_jwt.py

# Start JWKS server in background
echo "🚀 Starting test JWKS server (port 8081)..."
python test_jwks_server.py &
JWKS_PID=$!

# Wait a moment for JWKS server to start
sleep 2

# Start MCP server
echo "🚀 Starting MCP server (port 8080)..."
python server.py &
MCP_PID=$!

# Wait a moment for server to start
sleep 3

# Test with the generated token
echo "🧪 Testing authentication..."
TOKEN=$(cat test-jwt-token.txt)

echo "Testing without token (should fail):"
curl -s -w "%{http_code}\n" http://localhost:8080/sse/ || true
echo

echo "Testing with valid token (should work):"
curl -s -w "%{http_code}\n" -H "Authorization: Bearer $TOKEN" http://localhost:8080/sse/ || true
echo

echo
echo "✅ Test complete!"
echo "🔍 Check the logs above for results"
echo
echo "🛑 Press Ctrl+C to stop servers, or run:"
echo "   kill $JWKS_PID $MCP_PID"
echo
echo "💡 Your test token:"
echo "$TOKEN"

# Keep script running
wait