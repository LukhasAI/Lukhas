#!/bin/bash
#
# RATS Evidence Verification Demo
#
# Verifies JWT evidence against policy requirements.
# Demonstrates the attestation track for runtime trust.

set -e

EVIDENCE="evidence_jwt.json"
POLICY="verifier_policy.json"
TEE_REPORT="tee_report.json"

echo "🛡️ Verifying RATS evidence for attestation demo..."
echo "Evidence: $EVIDENCE"
echo "Policy: $POLICY"
echo "TEE Report: $TEE_REPORT"
echo

# Check if we have the LUKHAS attestation tools
if [ -f "../../../tools/collect_attestation.py" ]; then
    echo "✅ LUKHAS attestation tools available"

    # Extract JWT from JSON structure
    JWT=$(jq -r '.full_jwt' "$EVIDENCE")
    echo "📋 JWT (first 50 chars): ${JWT:0:50}..."

    echo
    echo "🧪 Mock verification (full implementation in development):"
else
    echo "🧪 Mock verification using local files"
fi

# Basic policy validation
echo "📋 Checking policy requirements..."

# Extract claims from mock evidence
MODULE_ISS=$(jq -r '.jwt_payload.iss' "$EVIDENCE")
CODE_HASH=$(jq -r '.jwt_payload.software_components.code_hash' "$EVIDENCE")
TEE_TYPE=$(jq -r '.jwt_payload.tee_evidence.type' "$EVIDENCE")
SNP_VERSION=$(jq -r '.jwt_payload.tee_evidence.report.reported_tcb.snp' "$EVIDENCE")

echo "   Issuer: $MODULE_ISS"
echo "   Code hash: ${CODE_HASH:0:20}..."
echo "   TEE type: $TEE_TYPE"
echo "   SNP version: $SNP_VERSION"

# Check against policy requirements
EXPECTED_ISS=$(jq -r '.required_claims[0].expected' "$POLICY")
MIN_SNP=$(jq -r '.tee_validation."amd-sev-snp".min_tcb_version.snp' "$POLICY")

echo
echo "📊 Policy compliance check:"

if [ "$MODULE_ISS" = "$EXPECTED_ISS" ]; then
    echo "   ✅ Issuer matches policy requirement"
else
    echo "   ❌ Issuer mismatch: expected $EXPECTED_ISS, got $MODULE_ISS"
fi

if [[ "$CODE_HASH" =~ ^sha256:[a-f0-9]{64}$ ]]; then
    echo "   ✅ Code hash format valid"
else
    echo "   ❌ Code hash format invalid"
fi

if [ "$SNP_VERSION" -ge "$MIN_SNP" ]; then
    echo "   ✅ SNP version meets minimum requirement ($MIN_SNP)"
else
    echo "   ❌ SNP version too low: $SNP_VERSION < $MIN_SNP"
fi

# TEE report validation
echo
echo "🔍 TEE report validation:"
CERT_VALID=$(jq -r '.validation.cert_chain_valid' "$TEE_REPORT")
SIG_VALID=$(jq -r '.validation.signature_valid' "$TEE_REPORT")
TCB_ACCEPTABLE=$(jq -r '.validation.tcb_level_acceptable' "$TEE_REPORT")

if [ "$CERT_VALID" = "true" ] && [ "$SIG_VALID" = "true" ] && [ "$TCB_ACCEPTABLE" = "true" ]; then
    echo "   ✅ TEE attestation report valid"
    echo "   ✅ Certificate chain verified"
    echo "   ✅ Signature verified"
    echo "   ✅ TCB level acceptable"
else
    echo "   ❌ TEE report validation failed"
fi

echo
echo "🎯 Demo verification complete!"
echo "   In production: use cryptographic signature verification"
echo "   Next: integrate with matrix gate using attestation.rats_verified metric"