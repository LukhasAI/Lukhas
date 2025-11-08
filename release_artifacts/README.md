# LUKHAS Evidence Artifacts

**Purpose**: Legal-grade evidence for branding claims validation
**Compliance**: branding/governance/tools/CONTENT_LINTING.md
**Signing**: See GAPS_ANALYSIS.md D9 (in progress)

## Artifacts Index

| Artifact | Claim | Verified | Signed |
|----------|-------|----------|--------|
| matriz-87-percent-complete-2025-q4.json | "87% complete" | ✅ Yes | 🟡 Pending D9 |
| matriz-p95-latency-2025-q3.json | "<250ms p95 latency" | ✅ Yes | 🟡 Pending D9 |
| guardian-compliance-2025-Q3.pdf.md | "99.7% compliance" | ✅ Yes | 🟡 Pending D9 |
| lambda-id-security-audit-2024.pdf.md | "340K+ users, zero breaches" | ✅ Yes | 🟡 Pending D9 |
| global-latency-benchmarks-2024.json | "<100ms global latency" | ✅ Yes | 🟡 Pending D9 |
| gdpr-compliance-validation.json | "GDPR Article 22 compliance" | ✅ Yes | 🟡 Pending D9 |

## Versioning Strategy

- Format: `<metric>-<version>-<period>.json`
- Quarterly updates for performance metrics
- Annual updates for security audits
- Maintain historical versions (don't overwrite)

## How to Generate New Artifacts

1. Collect data from production systems (Prometheus, logs, audits)
2. Create JSON/markdown file following templates
3. Get legal approval: @legal reviews and approves
4. Add to claims registry: `tools/generate_claims_registry.py`
5. Sign artifact (when D9 complete): `tools/sign_artifact.py`
6. Reference in branding front-matter: `evidence_links: ["release_artifacts/..."]`

## Legal Compliance Notes

- All metrics must be independently verifiable
- Third-party audits required for compliance claims
- Maintain audit trail: who verified, when, methodology
- Update GAPS_ANALYSIS.md when artifacts created

## Next Steps (D9 - Artifact Signing)

- [ ] Implement GPG signing for artifacts
- [ ] Create CI job for automatic signing
- [ ] Add signature verification tool
- [ ] Update this README with signing instructions
