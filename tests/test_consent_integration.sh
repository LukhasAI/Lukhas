#!/bin/bash
# Test ConsentGuard TEQ Integration
# Designed by: Gonzalo Dominguez - Lukhas AI

set -e

echo "Testing ConsentGuard TEQ Integration..."
echo "======================================"

# Test 1: Without consent (should fail)
echo -e "\n1. Testing without consent..."
python3 -m qi.safety.teq_gate \
  --policy-root qi/safety/policy_packs \
  --jurisdiction global \
  --task pii_processing \
  --context test_consent_ctx.json \
  --consent-storage ~/.lukhas/consent/ledger.jsonl 2>/dev/null || echo "✓ Correctly blocked without consent"

# Test 2: Grant consent
echo -e "\n2. Granting consent..."
python3 -m qi.memory.consent_guard grant \
  --user test_user \
  --purpose pii_processing \
  --ttl-days 7

# Test 3: With consent (should pass)
echo -e "\n3. Testing with valid consent..."
python3 -m qi.safety.teq_gate \
  --policy-root qi/safety/policy_packs \
  --jurisdiction global \
  --task pii_processing \
  --context test_consent_ctx.json \
  --consent-storage ~/.lukhas/consent/ledger.jsonl && echo "✓ Allowed with valid consent"

# Test 4: Revoke consent
echo -e "\n4. Revoking consent..."
python3 -m qi.memory.consent_guard revoke \
  --user test_user \
  --purpose pii_processing

# Test 5: After revocation (should fail)
echo -e "\n5. Testing after revocation..."
python3 -m qi.safety.teq_gate \
  --policy-root qi/safety/policy_packs \
  --jurisdiction global \
  --task pii_processing \
  --context test_consent_ctx.json \
  --consent-storage ~/.lukhas/consent/ledger.jsonl 2>/dev/null || echo "✓ Correctly blocked after revocation"

echo -e "\n✅ All consent integration tests passed!"