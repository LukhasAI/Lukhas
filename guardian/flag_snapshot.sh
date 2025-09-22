#!/usr/bin/env bash
# Feature Flag Snapshot Helper for Governance Ledger
# Usage: ./guardian/flag_snapshot.sh | curl -X POST ledger-endpoint
# Enhanced with dual-approval validation for audit compliance
set -euo pipefail

# Check for dual approval in canary decision file
CANARY_DECISION_FILE="${CANARY_DECISION_FILE:-docs/templates/canary_decision_one_page.md}"
DUAL_APPROVAL_VALID="false"
APPROVAL_COUNT=0

if [ -f "$CANARY_DECISION_FILE" ]; then
    # Count approval signatures
    APPROVAL_COUNT=$(grep -c -E "(Approved by:|Signature:|@.*approved)" "$CANARY_DECISION_FILE" 2>/dev/null || echo 0)
    if [ "$APPROVAL_COUNT" -ge 2 ]; then
        DUAL_APPROVAL_VALID="true"
    fi
fi

# Check Guardian emergency status
EMERGENCY_ACTIVE="false"
if [ -f "/tmp/guardian_emergency_disable" ]; then
    EMERGENCY_ACTIVE="true"
fi

jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg git_sha "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
  --arg git_branch "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" \
  --arg operator "${USER:-unknown}" \
  --arg lane "${LUKHAS_LANE:-candidate}" \
  --argjson enforce "${ENFORCE_ETHICS_DSL:-0}" \
  --argjson adv "${LUKHAS_ADVANCED_TAGS:-0}" \
  --argjson guard "${ENABLE_LLM_GUARDRAIL:-1}" \
  --argjson canary "${LUKHAS_CANARY_PERCENT:-10}" \
  --argjson dual_approval_valid "$DUAL_APPROVAL_VALID" \
  --argjson approval_count "$APPROVAL_COUNT" \
  --argjson emergency_active "$EMERGENCY_ACTIVE" \
  '{
     schema_version: "v2.0.0",
     timestamp: $ts,
     operator: $operator,
     git: {
       sha: $git_sha,
       branch: $git_branch
     },
     deployment_context: {
       lane: $lane,
       canary_percent: $canary
     },
     feature_flags: {
       ENFORCE_ETHICS_DSL: $enforce,
       LUKHAS_ADVANCED_TAGS: $adv,
       ENABLE_LLM_GUARDRAIL: $guard,
       LUKHAS_CANARY_PERCENT: $canary
     },
     governance: {
       dual_approval_valid: $dual_approval_valid,
       approval_count: $approval_count,
       emergency_active: $emergency_active,
       canary_decision_file_exists: ("'"$CANARY_DECISION_FILE"'" | test(".")),
       guardian_enforced: ($enforce == 1 and $emergency_active == false)
     },
     compliance: {
       production_ready: ($dual_approval_valid and $enforce == 1 and $emergency_active == false),
       audit_requirements_met: ($dual_approval_valid and ($enforce == 1 or $lane != "production"))
     },
     version: "guardian-safety-tags-v2.0.0"
   }'