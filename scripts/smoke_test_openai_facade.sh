#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# scripts/smoke_test_openai_facade.sh
#
# Smoke tests for OpenAI Façade - verifies basic functionality
# Uses readiness loop to prevent race conditions with server startup

set -euo pipefail

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-15}"
TEST_INDEX_ID="smoke-test-$(date +%s)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

test_endpoint() {
    local name="$1"
    local method="$2"
    local path="$3"
    local expected_status="$4"
    local data="${5:-}"
    
    echo -n "Testing ${name}... "
    
    local temp_response
    temp_response=$(mktemp)
    
    if [ -n "$data" ]; then
        curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${path}" > "$temp_response"
    else
        curl -s -w "\n%{http_code}" -X "$method" \
            "${BASE_URL}${path}" > "$temp_response"
    fi
    
    # Extract status code (last line) and body (all but last line)
    local status_code
    status_code=$(tail -1 "$temp_response")
    local body
    body=$(sed '$d' "$temp_response")
    
    rm -f "$temp_response"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} (HTTP ${status_code})"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} (Expected HTTP ${expected_status}, got ${status_code})"
        log_error "Response body: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Wait for server to be ready
log_info "Waiting for server at ${BASE_URL}..."
for i in $(seq 1 $((MAX_WAIT_SECONDS * 2))); do
    if curl -sf "${BASE_URL}/healthz" >/dev/null 2>&1; then
        log_info "Server is ready after $((i / 2)) seconds"
        break
    fi
    
    if [ "$i" -eq $((MAX_WAIT_SECONDS * 2)) ]; then
        log_error "Server did not become ready within ${MAX_WAIT_SECONDS} seconds"
        exit 1
    fi
    
    sleep 0.5
done

log_info "Starting smoke tests..."
echo

# Health checks
test_endpoint "Health check" GET "/healthz" 200
test_endpoint "Readiness check" GET "/readyz" 200

# OpenAPI spec
test_endpoint "OpenAPI spec" GET "/openapi.json" 200

# Note: Most OpenAI endpoints require Bearer token auth
# Testing only public endpoints and index API in basic smoke test
log_info "Note: Auth-required endpoints (/v1/models, /v1/responses) skipped in smoke test"

# Index CRUD workflow
log_info ""
log_info "Testing index CRUD workflow..."

# Create index and extract the ID from response
log_info "Creating test index..."
create_response=$(mktemp)
curl -s -X POST "${BASE_URL}/v1/indexes" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"${TEST_INDEX_ID}\",\"metric\":\"angular\",\"dimension\":128}" \
    > "$create_response"

# Extract the ID field from the JSON response
INDEX_ID=$(python3 -c "import json; print(json.load(open('$create_response'))['id'])" 2>/dev/null || echo "")
rm -f "$create_response"

if [ -z "$INDEX_ID" ]; then
    log_error "Failed to create index or extract ID"
    TESTS_FAILED=$((TESTS_FAILED + 1))
else
    log_info "Created index with ID: ${INDEX_ID}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # List indexes
    test_endpoint "List indexes" GET "/v1/indexes" 200
    
    # Get specific index (using ID, not name)
    test_endpoint "Get index" GET "/v1/indexes/${INDEX_ID}" 200
    
    # Add vectors
    test_endpoint "Add vectors" POST "/v1/indexes/${INDEX_ID}/vectors" 200 \
        "{\"vectors\":[{\"id\":\"vec1\",\"vector\":$(python3 -c 'import json; print(json.dumps([0.1]*128))')}]}"
    
    # Search vectors
    test_endpoint "Search vectors" POST "/v1/indexes/${INDEX_ID}/search" 200 \
        "{\"vector\":$(python3 -c 'import json; print(json.dumps([0.1]*128))'),\"top_k\":5}"
    
    # Delete index
    test_endpoint "Delete index" DELETE "/v1/indexes/${INDEX_ID}" 200
fi

# Summary
echo
log_info "=========================================="
log_info "Smoke Test Results"
log_info "=========================================="
log_info "Passed: ${TESTS_PASSED}"
if [ "$TESTS_FAILED" -gt 0 ]; then
    log_error "Failed: ${TESTS_FAILED}"
    exit 1
else
    log_info "Failed: ${TESTS_FAILED}"
    log_info "All smoke tests passed! ✓"
    exit 0
fi
