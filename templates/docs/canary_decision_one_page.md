---
module: templates
title: Canary Decision Report — Safety Tags v1
---

# Canary Decision Report — Safety Tags v1

## Deployment Metadata
- PR: https://github.com/LukhasAI/Lukhas/pull/325
- Release tag: guardian-safety-tags-v1 (@__________________)
- Image digest: __________________
- Flags at deploy: ENFORCE_ETHICS_DSL=____, LUKHAS_ADVANCED_TAGS=____, ENABLE_LLM_GUARDRAIL=____, LUKHAS_LANE=candidate
- Window: __________________ → __________________ (UTC)

## Summary
- Decision: ☐ Scale to 100% ☐ Scale to 50% ☐ Hold at 10% ☐ Rollback
- Executive score (0–10): ________
- Rationale (2–3 lines): _________________________________________________________________
  _____________________________________________________________________________________

## Metrics (candidate vs control)
| Signal                                | Target        | Observed | OK |
|---------------------------------------|---------------|----------|----|
| Warn+Block delta (15m ratio)          | ≤ +10%        | _____%   | ☐  |
| Ethics pipeline p95 overhead          | ≤ 1.05×       | ____×    | ☐  |
| Overrides p95 latency                 | < 5m          | ____ m   | ☐  |
| High/Critical band spike alerts       | none fired    | ____     | ☐  |
| Sev-2+ incidents                      | 0             | ____     | ☐  |

## Counterfactuals (dark-mode)
- would_action vs actual_action divergence: _____%
- Top rules causing divergence: _____________________________________________

## Governance & Hygiene
- Dual-approval verified: ☐ yes  ☐ no
- PII redaction audit (0.1% sample): ☐ pass  ☐ needs fix
- Ledger completeness (flags + overrides): ☐ pass  ☐ needs fix

## Residual-Risk Probes
- Locale formats (es-ES, pt-BR): ☐ pass
- Short-link exfil (bit.ly/t.co): ☐ pass
- Nested YAML → sudo chain: ☐ pass
- Model-hint entropy (≥2 hints): ☐ pass

## Incidents & Overrides
- Incidents: ___________________________________________________________________
- Overrides summary: _____ total, reasons top-3: _______________________________

## Decision & Sign-off
- Recommendation: ☐ SCALE  ☐ HOLD  ☐ ROLLBACK
- Owners: Ethics ☐  Platform ☐  On-call ☐
- Date/Time (UTC): ____________________

---
*T4 Executive Decision Record | Classification: Internal*