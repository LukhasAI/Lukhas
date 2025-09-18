#!/bin/bash
# Test script for Auth0 JWT integration

echo "🧪 Testing Auth0 JWT Integration"
echo "================================"

# Check if server starts
echo "1. Testing server startup..."
python server.py &
SERVER_PID=$!
sleep 3

# Test health endpoint
echo "2. Testing health endpoint..."
curl -s http://localhost:8080/healthz

# Test protected endpoint without token
echo "3. Testing SSE without token (should fail)..."
curl -s -w "%{http_code}" http://localhost:8080/sse/ | tail -n1

# Test with JWT token (you'll provide this)
echo "4. Ready to test with your JWT token:"
echo "   curl -H 'Authorization: Bearer <YOUR-JWT>' http://localhost:8080/sse/"

# Cleanup
kill $SERVER_PID 2>/dev/null

echo
echo "✅ Ready for Auth0 JWT testing!"