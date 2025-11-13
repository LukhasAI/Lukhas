# Ethics Assessment Template

**Module / Component:**  
**Owner:** @  
**Date:**  
**Is model-facing?** [Yes/No]

---

## 1. Summary
Short description of the component and intended behavior.

## 2. Scope & Stakeholders
- Affected users / groups:
- External systems/APIs:
- Data types (PII / sensitive / public):

## 3. Data provenance & quality
- Data sources and authorship:
- Licensing and consent:
- Coverage, biases, and known gaps:

## 4. Threat model & failure modes
- List realistic threats and failure modes (e.g., hallucination, privacy leakage, incorrect safety filtering).
- For each failure: probability estimate and impact severity.

## 5. Mitigations & controls
- Rate-limiting, content filters, safety layers.
- Data minimization and retention policy.
- Input validation and sanitization.
- Human-in-loop gating (where applicable).
- Fallback behaviors & safe defaults.

## 6. Testing & Validation
- Unit tests & integration tests (list).
- Adversarial tests performed (list).
- Metrics and acceptance thresholds (e.g., false positive/negative rates).

## 7. Monitoring & Alerting
- Key signals to track (latency, error rates, safety filter triggers).
- Dashboards and alerts (locations).
- Canary/Canary metric thresholds and roll-back triggers.

## 8. Privacy & Compliance
- GDPR / CCPA considerations.
- Data retention and deletion policy.
- Access control & least privilege info.

## 9. Governance & Sign-off
- Risk classification: [LOW | MEDIUM | HIGH]
- Residual risks and recommended mitigations.
- Owner signature:
- Ethics reviewer signature:
- Security reviewer signature:
- Date of sign-off:

---

## Appendix
- Links to datasets
- Links to tests / CI artifacts
- Threat-model diagram (optional)
