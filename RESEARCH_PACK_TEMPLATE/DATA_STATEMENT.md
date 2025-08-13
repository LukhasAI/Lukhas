# Data Statement — LUKHAS Research Package

## Summary
This research package uses **synthetic** inputs to evaluate system behavior under boundary conditions. No real-world sensitive or personal data is included.

## Generation
- Synthetic prompts are designed to induce behavioral responses (refusal/deferral/clarification) without requesting disallowed content.
- Test fixtures created programmatically with controlled parameters.
- No human-generated sensitive data incorporated.

## Use
- For research and testing only. 
- Not intended to train production systems without additional review.
- All test data clearly marked as synthetic.

## Governance
- Dataset versions, fingerprints, and metadata are recorded in `test_results/`.
- Compliance references are informational only and not legal advice.
- Data retention: Test results preserved for reproducibility (30 days minimum).

## Privacy & Ethics
- No PII collected or processed.
- No biometric or health data.
- Synthetic data designed to avoid harmful stereotypes.

## Access
- Public research package under specified license.
- Test data included in `data/` directory.
- Results available in `test_results/` after execution.

## Updates
- Data generation procedures documented in `tests/README.md`.
- Version control via git tags.
- Fingerprints updated with each test run.

---
*Updated: 2025-08-13*
*Version: 1.0.0*