#!/usr/bin/env bash
set -euo pipefail
H=${H:-http://localhost:8766}
echo "Smoke against $H"

# Quick smoke test - reusing the workflow steps
echo "🧪 Running MCP smoke test..."

# initialize
echo "✅ Testing initialize..."
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"local","version":"1.0"},"capabilities":{"tools":{}}}}' | jq -e '.result.serverInfo.name' > /dev/null

# Test new eval tools
echo "✅ Testing run_eval, status, promote_model..."
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/list","params":{}}' | jq -e '.result.tools | map(.name) | index("run_eval")' > /dev/null
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/list","params":{}}' | jq -e '.result.tools | map(.name) | index("status")' > /dev/null
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":8,"method":"tools/list","params":{}}' | jq -e '.result.tools | map(.name) | index("promote_model")' > /dev/null

# Test eval workflow
JOB=$(curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":20,"method":"tools/call","params":{"name":"run_eval","arguments":{"taskId":"local.test","configId":"default"}}}' \
  | jq -r '.result.content[0].text' | jq -r '.jobId')

echo "✅ Job created: $JOB"

# Check status
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d "{\"jsonrpc\":\"2.0\",\"id\":21,\"method\":\"tools/call\",\"params\":{\"name\":\"status\",\"arguments\":{\"jobId\":\"$JOB\"}}}" \
  | jq -e '.result.content[0].text | fromjson | .status' > /dev/null

# Test model promotion
curl -s $H/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":23,"method":"tools/call","params":{"name":"promote_model","arguments":{"modelId":"local-test-v1","gate":"experiments"}}}' \
  | jq -e '.result.content[0].text | fromjson | .currentGates | index("experiments")' > /dev/null

echo "🎉 All eval runner tests passed!"