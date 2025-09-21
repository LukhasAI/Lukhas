#!/bin/bash
# 🧪 Simple Test Script

echo "🧪 LUKHAS MCP Simple Test"
echo "========================="

# Check if we're in the right directory
if [ ! -f "simple_server.py" ]; then
    echo "❌ Please run this from the mcp-lukhas-sse directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q fastmcp python-jose[cryptography] uvicorn starlette

# Generate test JWT
echo "🔑 Generating test JWT token..."
python generate_test_jwt.py

# Check if token was generated
if [ ! -f "test-jwt-token.txt" ]; then
    echo "❌ Failed to generate test token"
    exit 1
fi

# Set environment
export ALLOWED_ROOTS="/Users/cognitive_dev/LOCAL-REPOS/Lukhas"

# Start simple server
echo "🚀 Starting simple MCP server (port 8080)..."
python simple_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test without token
echo "🧪 Testing without token (should fail):"
curl -s -w "HTTP %{http_code}\n" http://localhost:8080/sse/ || true
echo

# Test with token
echo "🧪 Testing with valid token (should work):"
TOKEN=$(cat test-jwt-token.txt)
curl -s -w "HTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" http://localhost:8080/sse/ || true
echo

# Test health endpoint
echo "🧪 Testing health endpoint (no auth needed):"
curl -s http://localhost:8080/health
echo
echo

echo "✅ Test complete!"
echo
echo "📍 Your MCP Server Details:"
echo "   URL: http://localhost:8080/sse"
echo "   Authentication: OAuth 2.1 (JWT Bearer token)"
echo "   Health Check: http://localhost:8080/health"
echo
echo "🔑 Your JWT Token:"
echo "$TOKEN"
echo
echo "🛑 Server is running (PID: $SERVER_PID)"
echo "   Press Ctrl+C to stop, or run: kill $SERVER_PID"
echo
echo "💡 Test MCP connection with:"
echo "   curl -H 'Authorization: Bearer $TOKEN' http://localhost:8080/sse/"

# Keep running
wait