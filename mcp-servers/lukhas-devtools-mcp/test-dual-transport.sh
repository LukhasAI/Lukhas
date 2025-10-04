#!/bin/bash
# Comprehensive Dual Transport MCP Server Test Suite
# Tests both single-endpoint and split transport modes

echo "🧪 Testing Enhanced Dual-Transport MCP Server"
echo "=============================================="

HOST="http://localhost:8766"

echo ""
echo "1️⃣ Testing Tool Discovery..."
echo "----------------------------------------"

# Test tool list
echo "📋 Available tools:"
curl -s $HOST/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
| jq '.result.tools | map(.name)' 2>/dev/null || echo "❌ Tool list failed"

echo ""
echo "2️⃣ Testing Fetch Tool Schema..."
echo "----------------------------------------"

# Test fetch requires ID
echo "🔍 Fetch tool schema validation:"
curl -s $HOST/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
| jq '.result.tools[] | select(.name=="fetch") | {hasId: (.inputSchema.properties.id!=null), required: .inputSchema.required}' 2>/dev/null || echo "❌ Fetch schema test failed"

echo ""
echo "3️⃣ Testing Search Function..."
echo "----------------------------------------"

# Test search returns IDs
echo "🔍 Search for 'lukhas mcp':"
SEARCH_RESULT=$(curl -s $HOST/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"query":"lukhas mcp","limit":2}}}' 2>/dev/null)

echo "Search result:"
echo "$SEARCH_RESULT" | jq '.result.content[0].text' | jq '.' 2>/dev/null || echo "❌ Search failed"

# Extract first ID for fetch test
FIRST_ID=$(echo "$SEARCH_RESULT" | jq -r '.result.content[0].text' | jq -r '.ids[0]' 2>/dev/null)
echo "📝 First ID extracted: $FIRST_ID"

echo ""
echo "4️⃣ Testing Fetch by ID..."
echo "----------------------------------------"

if [ "$FIRST_ID" != "null" ] && [ -n "$FIRST_ID" ]; then
    echo "📖 Fetching document by ID: $FIRST_ID"
    curl -s $HOST/mcp -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{\"name\":\"fetch\",\"arguments\":{\"id\":\"$FIRST_ID\"}}}" \
    | jq '.result.content[0].text' | jq '.' 2>/dev/null || echo "❌ Fetch by ID failed"
else
    echo "❌ No valid ID to test fetch"
fi

echo ""
echo "5️⃣ Testing Single-Endpoint SSE..."
echo "----------------------------------------"

echo "🌊 Single-endpoint SSE (first 3 lines):"
timeout 3s curl -N -H "Accept: text/event-stream" $HOST/mcp 2>/dev/null | head -3 || echo "❌ Single-endpoint SSE failed"

echo ""
echo "6️⃣ Testing Split Transport SSE..."
echo "----------------------------------------"

echo "🌊 Split SSE endpoint /sse (should emit endpoint event):"
timeout 3s curl -N -H "Accept: text/event-stream" $HOST/sse 2>/dev/null | head -3 || echo "❌ Split SSE endpoint failed"

echo ""
echo "7️⃣ Testing File Editing Tools..."
echo "----------------------------------------"

echo "📝 Testing writeFile tool:"
curl -s $HOST/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"writeFile","arguments":{"path":"test_dual_transport.txt","content":"Dual transport test successful!","overwrite":true}}}' \
| jq '.result.content[0].text' | jq '.' 2>/dev/null || echo "❌ WriteFile test failed"

echo ""
echo "8️⃣ Testing Health Endpoint..."
echo "----------------------------------------"

echo "❤️ Health check:"
curl -s $HOST/health | jq '.' 2>/dev/null || echo "❌ Health endpoint failed"

echo ""
echo "9️⃣ Testing Root Endpoint Info..."
echo "----------------------------------------"

echo "ℹ️ Server info:"
curl -s $HOST/ | jq '.usage' 2>/dev/null || echo "❌ Root endpoint failed"

echo ""
echo "✅ Dual Transport Test Suite Complete!"
echo "======================================"