#!/bin/bash
# 🧪 Simple OAuth Test Script

set -e # Exit immediately if a command exits with a non-zero status.

PORT=8080
SERVER_URL="http://localhost:$PORT"

echo "🧪 LUKHAS OAuth Test"
echo "===================="
# Set environment
export ALLOWED_ROOTS="/Users/cognitive_dev/LOCAL-REPOS/Lukhas"

# Cleanup function to kill the server
cleanup() {
    echo ""
    echo "🛑 Stopping server (PID: $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    echo "🧹 Cleanup complete."
}

# Register the cleanup function to be called on script exit
trap cleanup EXIT

# Check venv and activate
if [ ! -d "venv" ]; then
    echo "❌ venv not found. Please install dependencies first."
    exit 1
fi

source venv/bin/activate

# Check for test token
if [ ! -f "test-jwt-token.txt" ]; then
    echo "🔑 Generating test JWT token..."
    python generate_test_jwt.py
fi

# Start basic server
echo "🚀 Starting OAuth test server on port $PORT..."
python basic_oauth_server.py &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Test without token
echo ""
echo "🧪 Test 1: Without token (should fail with 401):"
curl -s -o /dev/null -w "HTTP %{http_code}\n" "$SERVER_URL/sse/" || true

# Test with token
echo ""
echo "🧪 Test 2: With valid token (should work with 200):"
TOKEN=$(cat test-jwt-token.txt)
curl -s -w "HTTP %{http_code}\n" -H "Authorization: Bearer $TOKEN" "$SERVER_URL/sse/"
echo ""

# Test health endpoint
echo "🧪 Test 3: Health endpoint (no auth needed):"
curl -s "$SERVER_URL/health"
echo ""
echo ""

# Test protected endpoint
echo "🧪 Test 4: Protected endpoint with token:"
curl -s -H "Authorization: Bearer $TOKEN" "$SERVER_URL/protected"
echo ""
echo ""

echo "✅ Tests complete!"
echo ""
echo "💡 Manual testing:"
echo "   Server URL: $SERVER_URL"
echo "   JWT Token: $TOKEN"
echo ""
echo "   # Test SSE endpoint:"
echo "   curl -H 'Authorization: Bearer \$(cat test-jwt-token.txt)' $SERVER_URL/sse/"
echo ""
echo "   # Test protected endpoint:"
echo "   curl -H 'Authorization: Bearer \$(cat test-jwt-token.txt)' $SERVER_URL/protected"
echo ""
echo "🛑 Press Ctrl+C to stop the server"

# Wait for user to terminate
wait $SERVER_PID
