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
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${path}")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${BASE_URL}${path}")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
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

# Models endpoint
test_endpoint "List models" GET "/v1/models" 200

# Responses endpoint (stub)
test_endpoint "List responses" GET "/v1/responses" 200

# Index CRUD workflow
log_info ""
log_info "Testing index CRUD workflow..."

# Create index
test_endpoint "Create index" POST "/v1/indexes" 201 \
    "{\"name\":\"${TEST_INDEX_ID}\",\"metric\":\"angular\",\"dimension\":128}"

# List indexes
test_endpoint "List indexes" GET "/v1/indexes" 200

# Get specific index
test_endpoint "Get index" GET "/v1/indexes/${TEST_INDEX_ID}" 200

# Add vectors
test_endpoint "Add vectors" POST "/v1/indexes/${TEST_INDEX_ID}/vectors" 200 \
    "{\"vectors\":[{\"id\":\"vec1\",\"vector\":$(python3 -c 'import json; print(json.dumps([0.1]*128))')}]}"

# Query vectors
test_endpoint "Query vectors" POST "/v1/indexes/${TEST_INDEX_ID}/query" 200 \
    "{\"vector\":$(python3 -c 'import json; print(json.dumps([0.1]*128))'),\"top_k\":5}"

# Delete index
test_endpoint "Delete index" DELETE "/v1/indexes/${TEST_INDEX_ID}" 204

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
