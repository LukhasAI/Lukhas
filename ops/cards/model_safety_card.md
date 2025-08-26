# Model & Safety Card — LUKHAS-QI (v0.9.0)

**Generated:** 2025-08-16 03:40:12Z
**Jurisdictions:** global, eu, us
**Policy Fingerprint:** `fbc344a0ae258448…`

## Evaluation Summary
- Suite: `core_tasks`
- Eval ID: `5274ba1383f3`
- Weighted Mean: `0.872847`
- Failures: `2`

## Safety Mechanisms
- TEQ: Task-specific Enforcement Queue with require_* checks
- Consent: Signed ledger with freshness & field scopes
- Capabilities: Deny-by-default leases (fs/net/api) with audit
- Provenance: Signed Merkle receipts (W3C PROV-ish), Kafka/S3 sinks
- C-EVAL: Continuous evaluation & drift gates

## Intended Use
- Enterprise assistive workflows with auditable provenance.
- Research and analytics with privacy-preserving receipts.

## Prohibited Use
- High-stakes medical/financial advice without a qualified human in the loop.
- Surveillance or privacy-invasive profiling without explicit consent and legal basis.

## Limitations
- May underperform on out-of-distribution inputs.
- Relies on policy pack coverage; gaps reduce enforcement efficacy.
- In-process sandboxing is not a kernel boundary; combine with OS sandboxing for untrusted binaries.

## Contact
security@lukhas.example
