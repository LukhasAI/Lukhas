#!/usr/bin/env bash
# Synthetic Load Generator for RC Soak Testing
# Generates realistic traffic patterns for embeddings, chat, and health endpoints

set -euo pipefail

BASE_URL="${LUKHAS_API_URL:-http://localhost:8000}"
REQUESTS="${1:-100}"
CONCURRENT="${2:-5}"

echo "🔥 Generating synthetic load..."
echo "   Base URL: ${BASE_URL}"
echo "   Requests: ${REQUESTS}"
echo "   Concurrent: ${CONCURRENT}"
echo ""

# Determine which health endpoint to use (prefer /healthz, fallback to /health)
HEALTH_ENDPOINT="/healthz"
echo "🔍 Checking health endpoint..."
if curl -sf "${BASE_URL}/healthz" > /dev/null 2>&1; then
    echo "✅ Using /healthz endpoint"
    HEALTH_ENDPOINT="/healthz"
elif curl -sf "${BASE_URL}/health" > /dev/null 2>&1; then
    echo "✅ Using /health endpoint (fallback)"
    HEALTH_ENDPOINT="/health"
else
    echo "❌ Neither /healthz nor /health responding at ${BASE_URL}"
    echo "   Server may not be running. Start with: make rc-soak-start"
    exit 1
fi
echo ""

# Counters
SUCCESS=0
FAILURES=0

# Test payloads
EMBEDDING_PAYLOAD='{
  "input": "The quick brown fox jumps over the lazy dog",
  "model": "text-embedding-ada-002"
}'

CHAT_PAYLOAD='{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "model": "gpt-4",
  "max_tokens": 50
}'

# Request function
make_request() {
    local endpoint=$1
    local payload=$2
    local request_num=$3
    
    response=$(curl -sf -X POST "${BASE_URL}${endpoint}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer test-key" \
        -d "${payload}" \
        -w "\n%{http_code}" \
        2>/dev/null || echo -e "\n000")
    
    http_code=$(echo "${response}" | tail -n1)
    
    if [[ "${http_code}" =~ ^2[0-9]{2}$ ]]; then
        echo -n "."
        return 0
    else
        echo -n "x"
        return 1
    fi
}

# Generate load
echo "🚀 Starting load generation..."
echo -n "Progress: "

for i in $(seq 1 "${REQUESTS}"); do
    # Alternate between embeddings and chat
    if (( i % 2 == 0 )); then
        if make_request "/v1/embeddings" "${EMBEDDING_PAYLOAD}" "${i}"; then
            ((SUCCESS++))
        else
            ((FAILURES++))
        fi
    else
        if make_request "/v1/chat/completions" "${CHAT_PAYLOAD}" "${i}"; then
            ((SUCCESS++))
        else
            ((FAILURES++))
        fi
    fi
    
    # Add health check every 20 requests
    if (( i % 20 == 0 )); then
        curl -sf "${BASE_URL}${HEALTH_ENDPOINT}" > /dev/null 2>&1 || echo -n "!"
    fi
    
    # Small delay to simulate realistic traffic
    sleep 0.1
done

echo ""
echo ""
echo "✅ Load generation complete!"
echo ""
echo "📊 Results:"
echo "   Success: ${SUCCESS}"
echo "   Failures: ${FAILURES}"
echo "   Success Rate: $(echo "scale=2; ${SUCCESS} * 100 / ${REQUESTS}" | bc)%"
echo ""
echo "🔍 Next Steps:"
echo "   1. Check Prometheus metrics: ${BASE_URL}/metrics"
echo "   2. View Grafana dashboard: http://localhost:3000/d/guardian-rl-v090"
echo "   3. Run snapshot: make rc-soak-snapshot"
