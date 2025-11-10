# LUKHΛS Test Surgeon — LUKHAS module

**File:** `lukhas/governance/guardian.py`
**Goal:** 85%+ coverage, deterministic, no network.

Focus:
- WebAuthn / JWT flows (positive + negative)
- Feature flags CRUD & evaluation
- Privacy-preserving analytics (no PII leakage)

Constraints:
- No auth weakening; no snapshot test loosening
- Mock external backends
