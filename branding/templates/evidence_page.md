---
evidence_id: "{{EVIDENCE_ID}}"                    # e.g., matriz-p95-latency-2025-q3
claim_type: "{{CLAIM_TYPE}}"                      # performance|security|compliance|usage|accuracy
claim_statement: "{{CLAIM_STATEMENT}}"            # Full claim text, e.g., "<250ms p95 reasoning latency in MATRIZ cognitive engine"
domains: ["{{DOMAIN}}"]                           # e.g., [lukhas.ai, lukhas.eu]
pages_using_claim:                                # Bidirectional links to pages using this claim
  - 'branding/websites/{{DOMAIN}}/homepage.md'
methodology:
  test_environment: "{{TEST_ENVIRONMENT}}"        # e.g., "Production-like staging with 50K concurrent users"
  data_collection: "{{DATA_COLLECTION}}"          # e.g., "7-day continuous monitoring Oct 15-22, 2025"
  tools: ["{{TOOL_1}}", "{{TOOL_2}}"]            # e.g., ["Prometheus", "Grafana", "custom latency instrumentation"]
  sample_size: "{{SAMPLE_SIZE}}"                  # e.g., "3,042,156 reasoning operations"
artifacts:
  - path: 'release_artifacts/{{ARTIFACT_FILE}}.json'
    type: json
    hash: sha256-{{ARTIFACT_HASH}}
  - path: 'release_artifacts/{{ARTIFACT_FILE}}.png'
    type: image
    hash: sha256-{{IMAGE_HASH}}
verified_by: ['@web-architect', '@qa-lead']
verified_date: "{{VERIFIED_DATE}}"                # e.g., "2025-10-23"
legal_approved: false                              # Set to true after legal review
legal_approved_by: '@legal'
legal_approved_date: "{{LEGAL_DATE}}"             # e.g., "2025-10-24"
next_review: "{{NEXT_REVIEW_DATE}}"               # e.g., "2026-01-15"
---

# Evidence: {{CLAIM_STATEMENT}}

## Claim Summary

- **Statement**: {{CLAIM_STATEMENT}}
- **Type**: {{CLAIM_TYPE}}
- **Domains**: {{DOMAINS_LIST}}
- **Status**: ⚠️ Draft | ✅ Verified | 🔴 Retracted

## Methodology

### Test Environment

{{TEST_ENVIRONMENT_DESCRIPTION}}

**Configuration**:
- Infrastructure: [Describe cloud provider, regions, instance types]
- Network: [Latency profiles, bandwidth limits]
- Load pattern: [Peak users, request rate, concurrency]
- Dataset: [Size, characteristics, representativeness]

### Data Collection

**Collection Period**: {{DATA_COLLECTION}}

**Sampling Approach**:
- Sample size: {{SAMPLE_SIZE}}
- Sampling method: [Continuous monitoring | Random sampling | Stratified sampling]
- Aggregation: [p50/p95/p99 calculations, outlier handling]
- Monitoring frequency: [Real-time | 1-minute intervals]

### Tools & Instrumentation

{{#TOOLS}}
- **{{TOOL_NAME}}**: {{TOOL_PURPOSE}}
  - Version: {{TOOL_VERSION}}
  - Configuration: {{TOOL_CONFIG}}
  - Data collected: {{DATA_TYPE}}
{{/TOOLS}}

## Results

### Key Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| p50 latency | {{P50_VALUE}} | {{P50_TARGET}} | {{P50_STATUS}} |
| p95 latency | {{P95_VALUE}} | {{P95_TARGET}} | {{P95_STATUS}} |
| p99 latency | {{P99_VALUE}} | {{P99_TARGET}} | {{P99_STATUS}} |
| Success rate | {{SUCCESS_RATE}} | {{SUCCESS_TARGET}} | {{SUCCESS_STATUS}} |

### Statistical Confidence

- **Sample size**: {{SAMPLE_SIZE}}
- **Confidence level**: 95%
- **Margin of error**: ±{{MARGIN_ERROR}}
- **Standard deviation**: {{STD_DEV}}
- **Outliers removed**: {{OUTLIER_COUNT}} ({{OUTLIER_CRITERIA}})

### Performance Distribution

```
Percentile Distribution ({{SAMPLE_SIZE}} samples):
p0  (min):     {{P0_VALUE}}
p25:           {{P25_VALUE}}
p50 (median):  {{P50_VALUE}}
p75:           {{P75_VALUE}}
p90:           {{P90_VALUE}}
p95:           {{P95_VALUE}}
p99:           {{P99_VALUE}}
p100 (max):    {{P100_VALUE}}
```

## Artifacts

### Primary Evidence

1. **{{ARTIFACT_1_NAME}}.json** - Raw performance data
   - Path: `release_artifacts/{{ARTIFACT_1_PATH}}`
   - Hash: `sha256-{{ARTIFACT_1_HASH}}`
   - Size: {{ARTIFACT_1_SIZE}}
   - Format: JSON with per-request timing data
   - [Download](../../release_artifacts/{{ARTIFACT_1_PATH}})

2. **{{ARTIFACT_2_NAME}}.png** - Performance dashboard screenshot
   - Path: `release_artifacts/{{ARTIFACT_2_PATH}}`
   - Hash: `sha256-{{ARTIFACT_2_HASH}}`
   - Size: {{ARTIFACT_2_SIZE}}
   - Resolution: {{IMAGE_RESOLUTION}}
   - [View](../../release_artifacts/{{ARTIFACT_2_PATH}})

3. **{{ARTIFACT_3_NAME}}.csv** - Statistical summary
   - Path: `release_artifacts/{{ARTIFACT_3_PATH}}`
   - Hash: `sha256-{{ARTIFACT_3_HASH}}`
   - Columns: timestamp, metric, value, percentile
   - [Download](../../release_artifacts/{{ARTIFACT_3_PATH}})

### Third-Party Validation

{{#THIRD_PARTY_AUDIT}}
- **Auditor**: {{AUDITOR_NAME}}
- **Report**: [{{REPORT_NAME}}]({{REPORT_PATH}})
- **Audit Date**: {{AUDIT_DATE}}
- **Findings**: {{AUDIT_FINDINGS}}
- **Certification**: {{CERTIFICATION_INFO}}
{{/THIRD_PARTY_AUDIT}}

{{^THIRD_PARTY_AUDIT}}
*No third-party validation required for this claim.*
{{/THIRD_PARTY_AUDIT}}

## Pages Using This Claim

{{#PAGES_USING_CLAIM}}
- [{{PAGE_NAME}}](../../{{PAGE_PATH}}#L{{LINE_NUMBER}}) - "{{CLAIM_EXCERPT}}"
{{/PAGES_USING_CLAIM}}

### Bidirectional Link Validation

All pages listed above include this evidence page in their `evidence_links` front-matter field.

**Validation Command**:
```bash
python3 tools/validate_evidence_pages.py --check-bidirectional
```

## Verification History

| Date | Verifier | Action | Notes |
|------|----------|--------|-------|
| {{INITIAL_VERIFICATION_DATE}} | {{INITIAL_VERIFIER}} | Initial verification | {{INITIAL_NOTES}} |
| {{LEGAL_APPROVAL_DATE}} | @legal | Legal approval | {{LEGAL_NOTES}} |
{{#ADDITIONAL_VERIFICATIONS}}
| {{DATE}} | {{VERIFIER}} | {{ACTION}} | {{NOTES}} |
{{/ADDITIONAL_VERIFICATIONS}}

## Limitations & Assumptions

### What This Claim Covers

- ✅ {{COVERAGE_ITEM_1}}
- ✅ {{COVERAGE_ITEM_2}}
- ✅ {{COVERAGE_ITEM_3}}

### What This Claim Does NOT Cover

- ❌ {{LIMITATION_1}}
- ❌ {{LIMITATION_2}}
- ❌ {{LIMITATION_3}}

### Known Caveats

1. **{{CAVEAT_1_TITLE}}**: {{CAVEAT_1_DESCRIPTION}}
2. **{{CAVEAT_2_TITLE}}**: {{CAVEAT_2_DESCRIPTION}}
3. **{{CAVEAT_3_TITLE}}**: {{CAVEAT_3_DESCRIPTION}}

### Expected Variation

- Normal variance: ±{{NORMAL_VARIANCE}}
- Degradation triggers: {{DEGRADATION_TRIGGERS}}
- Re-measurement needed if: {{REMEASUREMENT_TRIGGERS}}

## Next Review

- **Scheduled**: {{NEXT_REVIEW_DATE}}
- **Trigger Conditions**:
  - Major version update (e.g., MATRIZ v3.x → v4.x)
  - Performance regression detected in monitoring
  - Architecture changes affecting measured component
  - Quarterly review cycle
- **Review Owner**: {{REVIEW_OWNER}}
- **Notification**: {{NOTIFICATION_METHOD}}

## Reproducibility

### Reproduction Instructions

To reproduce these measurements:

1. **Environment Setup**:
   ```bash
   {{SETUP_COMMANDS}}
   ```

2. **Load Test Execution**:
   ```bash
   {{LOAD_TEST_COMMANDS}}
   ```

3. **Data Collection**:
   ```bash
   {{DATA_COLLECTION_COMMANDS}}
   ```

4. **Analysis**:
   ```bash
   {{ANALYSIS_COMMANDS}}
   ```

### Expected Reproduction Variance

Reproductions should yield results within {{REPRODUCTION_TOLERANCE}} of reported values. Deviations beyond this range require investigation.

---

## Usage Instructions

This template is used to create evidence pages that back up numeric or operational claims made in LUKHAS marketing materials.

### When to Create an Evidence Page

Create an evidence page for any claim that includes:
- **Performance metrics** (e.g., "p95 latency < 250ms")
- **Accuracy percentages** (e.g., "94% accuracy on benchmark X")
- **System capabilities** (e.g., "supports 1M requests/day")
- **Compliance statements** (e.g., "WCAG AAA compliant")
- **Security claims** (e.g., "AES-256 encryption")
- **Availability/uptime** (e.g., "99.9% uptime SLA")

### How to Use This Template

1. **Auto-generate stub** via `tools/generate_evidence_page.py` (recommended)
2. **Fill methodology sections** with precise test setup
3. **Link artifacts** with SHA256 hashes for verification
4. **Document limitations** honestly to build trust
5. **Get verification** from technical reviewer (@web-architect, @qa-lead)
6. **Get legal approval** if claim is customer-facing
7. **Sign artifacts** using `tools/build_audit_pack.py`
8. **Update page front-matter** to reference this evidence page

### Auto-Generation

Use `tools/generate_evidence_page.py` to automatically create evidence page stubs from the claims registry:

```bash
# Generate claims registry from all markdown files
python3 tools/generate_claims_registry.py

# Create evidence page stubs for all claims
python3 tools/generate_evidence_page.py

# Or use Makefile targets
make evidence-pages
make evidence-validate
```

### Validation

Evidence pages are validated by:
- `tools/validate_evidence_pages.py` - Ensures claims have evidence and bidirectional links
- `tools/front_matter_lint.py` - Validates YAML front-matter completeness
- `tools/branding_vocab_lint.py` - Checks vocabulary compliance
- CI workflows in `.github/workflows/content-lint.yml`

### Artifact Signing

Sign evidence artifacts to create audit trail:

```bash
# Sign individual artifact
python3 tools/build_audit_pack.py sign release_artifacts/matriz-perf-2025-q3.json

# Sign all artifacts for an evidence page
python3 tools/build_audit_pack.py sign-evidence matriz-p95-latency-2025-q3

# Verify signature
python3 tools/build_audit_pack.py verify release_artifacts/matriz-perf-2025-q3.json.sig
```

---

**Template Version**: 2.0
**Last Updated**: 2025-11-08
**Source**: T4 Strategic Audit deliverable (A1: Evidence Page Template System)
**Canonical Location**: `branding/templates/evidence_page.md`
**Related Documents**:
- [EVIDENCE_SYSTEM.md](../governance/tools/EVIDENCE_SYSTEM.md) - Complete implementation guide
- [GAPS_ANALYSIS.md](../governance/strategic/GAPS_ANALYSIS.md) - Strategic context (A1)
- [CONTENT_LINTING.md](../governance/tools/CONTENT_LINTING.md) - Validation tools
