#!/usr/bin/env bash
# Feature Flag Snapshot Helper for Governance Ledger
# Usage: ./guardian/flag_snapshot.sh | curl -X POST ledger-endpoint
set -euo pipefail

jq -n \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg git_sha "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" \
  --arg lane "${LUKHAS_LANE:-candidate}" \
  --argjson enforce "${ENFORCE_ETHICS_DSL:-0}" \
  --argjson adv "${LUKHAS_ADVANCED_TAGS:-0}" \
  --argjson guard "${ENABLE_LLM_GUARDRAIL:-1}" \
  --argjson canary "${LUKHAS_CANARY_PERCENT:-10}" \
  '{
     timestamp: $ts,
     git_sha: $git_sha,
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
     version: "guardian-safety-tags-v1.0.0"
   }'