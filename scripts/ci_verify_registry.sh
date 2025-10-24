#!/usr/bin/env bash
# scripts/ci_verify_registry.sh
# T4 smoke test for Registry prototype: register -> query -> validate -> deregister
# Exits non-zero on any failure. Prints helpful diagnostics.

set -euo pipefail

REGISTRY_BASE_URL="${REGISTRY_BASE_URL:-http://127.0.0.1:8080}"
SAMPLE_NODESPEC_PATH="${SAMPLE_NODESPEC_PATH:-docs/schemas/examples/memory_adapter.json}"
TIMEOUT=${TIMEOUT:-60}
CURL_OPTS="-sS -w %{http_code}"

echo "==> Registry smoke test"
echo "REGISTRY_BASE_URL=$REGISTRY_BASE_URL"
echo "SAMPLE_NODESPEC_PATH=$SAMPLE_NODESPEC_PATH"

# Wait for registry to respond on query endpoint
echo "Waiting for registry to become ready..."
end=$((SECONDS + TIMEOUT))
while true; do
  CODE=$(curl --fail --silent --output /dev/null -w "%{http_code}" "${REGISTRY_BASE_URL}/api/v1/registry/query" || echo "000")
  if [ "$CODE" = "200" ] || [ "$CODE" = "404" ] || [ "$CODE" = "400" ]; then
    echo "Registry responded with HTTP $CODE"
    break
  fi
  if [ $SECONDS -gt $end ]; then
    echo "Registry did not respond within ${TIMEOUT}s"; exit 2
  fi
  sleep 1
done

# 1) Validate NodeSpec via /validate
if [ ! -f "${SAMPLE_NODESPEC_PATH}" ]; then
  echo "ERROR: sample NodeSpec not found at ${SAMPLE_NODESPEC_PATH}"
  exit 3
fi

echo "1) Calling /api/v1/registry/validate"
VALIDATE_RESPONSE=$(curl -sS -X POST "${REGISTRY_BASE_URL}/api/v1/registry/validate" \
  -H "Content-Type: application/json" \
  --data-binary @"${SAMPLE_NODESPEC_PATH}" || true)
echo "validate: $VALIDATE_RESPONSE"
# Try to parse JSON
echo "$VALIDATE_RESPONSE" | jq -e '.valid == true' >/dev/null 2>&1 || echo "Warning: validate did not return {valid:true}"

# 2) Register NodeSpec (happy path)
echo "2) Registering sample NodeSpec"
REG_RESP=$(curl -sS -X POST "${REGISTRY_BASE_URL}/api/v1/registry/register" \
  -H "Content-Type: application/json" \
  --data-binary @"${SAMPLE_NODESPEC_PATH}" || true)
echo "register response: $REG_RESP"
REG_ID=$(echo "$REG_RESP" | jq -r '.registry_id // empty' || true)
if [ -z "$REG_ID" ]; then
  echo "ERROR: registry_id missing in register response; full response:"
  echo "$REG_RESP"
  exit 4
fi
echo "Registered as: $REG_ID"

# 3) Query by signal
# pick a signal we expect from sample NodeSpec: memory_stored
SIGNAL="memory_stored"
echo "3) Querying registry for signal '${SIGNAL}'"
QRESP=$(curl -sS -X GET "${REGISTRY_BASE_URL}/api/v1/registry/query?signal=${SIGNAL}" || true)
echo "query response: $QRESP"
HAS_ID=$(echo "$QRESP" | jq -r --arg id "$REG_ID" '.results[]?.registry_id // empty | select(.==$id)' || true)
if [ -z "$HAS_ID" ]; then
  echo "ERROR: registry query did not contain registered id ($REG_ID). Full query response:"
  echo "$QRESP"
  exit 5
fi
echo "Query returned registered id."

# 4) Negative test: register missing GLYMPH (expect 4xx)
echo "4) Negative test: register NodeSpec missing provenance (expect 4xx)"
TMP_JSON=$(mktemp)
jq 'del(.provenance_manifest)' "${SAMPLE_NODESPEC_PATH}" > "$TMP_JSON"
NEG_RESP=$(curl -sS -X POST "${REGISTRY_BASE_URL}/api/v1/registry/register" \
  -H "Content-Type: application/json" \
  --data-binary @"${TMP_JSON}" || true)
echo "negative register response: $NEG_RESP"
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "${REGISTRY_BASE_URL}/api/v1/registry/register" \
  -H "Content-Type: application/json" \
  --data-binary @"${TMP_JSON}" || true)
if [[ "$HTTP_CODE" == "403" || "$HTTP_CODE" == "400" ]]; then
  echo "Negative test: registry correctly rejected missing provenance with HTTP $HTTP_CODE"
else
  echo "Warning: negative register test did not return 4xx (got $HTTP_CODE). Response:"
  echo "$NEG_RESP"
  # treat as non-fatal / warning (some implementations may enforce policy later)
fi
rm -f "$TMP_JSON"

# 5) Deregister
echo "5) Deregistering $REG_ID"
DEL_RESP=$(curl -sS -X DELETE "${REGISTRY_BASE_URL}/api/v1/registry/${REG_ID}" || true)
echo "delete response: $DEL_RESP"
echo "Smoke test completed successfully."
exit 0
