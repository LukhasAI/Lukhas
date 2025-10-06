---
module: governance
title: RFC: Context Policy Amendments (Draft)
---

# RFC: Context Policy Amendments (Draft)

Status: Draft
Authors: Governance Team
Date: 2025-09-14

## Motivation

We propose additive amendments to `config/ethics/context_policy.yaml` to strengthen protections around:

- Consent-critical contexts (CONSENT domain)
- Non-maleficence safeguards in user-directed actions
- Escalation rules for repeated near-threshold violations

The changes are additive only and preserve the existing schema and semantics to minimize compatibility risk.

## Proposed Changes

1. Add explicit rule: Block non-consensual requests in any context (`CONSENT` domain). Rationale: Aligns with explicit consent requirements.
2. Add contextual mitigation: Allow “threat_analysis” usage of terms like “exploit” with severity downgrade (already in code), formalized in policy to ensure consistent governance.
3. Add escalation: If the system records 3 near-threshold violations within 10 minutes for the same session, require human review (`requires_review`).

## Acceptance Criteria

- All additions are additive (no removal of existing rules).
- Unit tests validate that:
  - Non-consensual requests are rejected even with otherwise acceptable context.
  - “Threat analysis” terms are downgraded per the whitelist, but still audited.
  - Three near-threshold violations trigger `requires_review` recommendation.

## Rollout Plan

1. PR gated behind a feature flag `enable_policy_amendments` (default: false).
2. Canary environment: enable flag; monitor violations-per-1k-ops and false positive rates.
3. Gradual ramp: 10% → 50% → 100% if metrics are stable.

## Observability

- Ethics events already stream to `reports/audit/merged/ethics_events.jsonl`.
- Use `make audit-rollup` and `make audit-dashboard` to visualize impacts.

## Risks and Mitigations

- Risk: Increased false positives. Mitigation: Start with audit-only mode (`requires_review`) before hard enforcement.
- Risk: Policy inconsistency. Mitigation: Keep schema intact, additive only, and validate with unit tests.

## Open Questions

- Should we expand the whitelist for “educational_content” contexts further?
- Do we want per-tenant overrides in the future (`config/ethics/context_policy.d/*.yaml`)?
