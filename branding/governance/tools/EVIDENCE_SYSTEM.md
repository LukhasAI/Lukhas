# Evidence Page Template System

> **📊 Structured, Auditable Evidence for All Claims**

**Version**: 2.0
**Date**: 2025-11-08
**Status**: ✅ Production-Ready
**Owner**: @web-architect
**Deliverable**: T4 Strategic Audit Gap A1

---

## Executive Summary

The Evidence Page Template System provides a standardized framework for documenting, verifying, and maintaining evidence that backs up all numeric and operational claims in LUKHAS marketing materials.

### Why This Matters

- **Legal Protection**: Auditable evidence trail prevents liability from unsubstantiated claims
- **Trust Building**: Transparent methodology increases customer and enterprise confidence
- **Compliance**: Meets EU advertising standards and enterprise procurement requirements
- **Efficiency**: Automated generation and validation reduces manual overhead

### Key Features

✅ **Comprehensive Template**: Structured front-matter + body with methodology, artifacts, and verification
✅ **Automated Generation**: Python script creates evidence page stubs from claims registry
✅ **Bidirectional Linking**: Connects claims to evidence and evidence back to source pages
✅ **Validation Tools**: Automated checks for completeness, correctness, and link integrity
✅ **Legal Workflow**: Built-in approval tracking for customer-facing claims
✅ **Artifact Signing**: SHA256 hashing and GPG signatures for audit trail

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Evidence Page Template](#evidence-page-template)
3. [Generator Tool](#generator-tool)
4. [Validator Tool](#validator-tool)
5. [Workflow](#workflow)
6. [Artifact Management](#artifact-management)
7. [Legal Approval Process](#legal-approval-process)
8. [Bidirectional Linking](#bidirectional-linking)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Generate Evidence Pages

```bash
# Option A: Use Makefile target (recommended)
make evidence-pages

# Option B: Run script directly
python3 tools/generate_evidence_page.py
```

### 2. Fill In Methodology

Edit generated pages in `release_artifacts/evidence/*.md`:

1. Replace placeholders with actual test data
2. Document test environment and methodology
3. Link artifacts (JSON, CSV, images)
4. Add SHA256 hashes for artifacts
5. Document limitations and caveats

### 3. Validate Evidence Pages

```bash
# Basic validation
make evidence-validate

# Strict validation (warnings = errors)
make evidence-validate-strict
```

### 4. Get Legal Approval

For customer-facing claims (lukhas.ai, lukhas.eu, lukhas.com):

1. Submit evidence page to @legal for review
2. Update `legal_approved: true` after approval
3. Add `legal_approved_by` and `legal_approved_date`
4. Re-validate to confirm completeness

---

## Evidence Page Template

### Template Location

**Path**: `branding/templates/evidence_page.md`

### Front-Matter Structure

```yaml
---
evidence_id: "matriz-p95-latency-2025-q3"        # Unique identifier
claim_type: "performance"                         # performance|security|compliance|usage|accuracy
claim_statement: "<250ms p95 reasoning latency"   # Full claim text
domains: [lukhas.ai, lukhas.eu]                   # Domains using this claim
pages_using_claim:                                # Bidirectional links
  - 'branding/websites/lukhas.ai/homepage.md'
methodology:
  test_environment: "Production-like staging..."
  data_collection: "7-day continuous monitoring..."
  tools: ["Prometheus", "Grafana"]
  sample_size: "3,042,156 operations"
artifacts:
  - path: 'release_artifacts/perf/matriz-p95-2025-q3.json'
    type: json
    hash: sha256-abc123...
verified_by: ['@web-architect', '@qa-lead']
verified_date: "2025-10-23"
legal_approved: true
legal_approved_by: '@legal'
legal_approved_date: "2025-10-24"
next_review: "2026-01-15"
---
```

### Required Fields

All evidence pages MUST include:

- `evidence_id` - Unique identifier (slug format)
- `claim_type` - One of: performance, security, compliance, usage, accuracy, general
- `claim_statement` - Full text of the claim
- `domains` - List of domains where claim appears
- `verified_by` - List of technical reviewers
- `verified_date` - Date of verification (YYYY-MM-DD)

### Recommended Fields

Strongly recommended for completeness:

- `pages_using_claim` - Bidirectional links to content pages
- `methodology` - Test environment, data collection, tools, sample size
- `artifacts` - List of evidence artifacts with paths and hashes
- `legal_approved` - Legal approval status (required for customer-facing claims)
- `next_review` - Scheduled review date

### Body Structure

1. **Claim Summary** - Statement, type, domains, status
2. **Methodology** - Test environment, data collection, tools
3. **Results** - Key metrics, statistical confidence, distribution
4. **Artifacts** - Primary evidence files, third-party validation
5. **Pages Using This Claim** - Bidirectional links with excerpts
6. **Verification History** - Timeline of reviews and approvals
7. **Limitations & Assumptions** - What's covered, what's not, caveats
8. **Next Review** - Schedule and trigger conditions
9. **Reproducibility** - Instructions to reproduce measurements

---

## Generator Tool

### Overview

**Path**: `tools/generate_evidence_page.py`

The generator creates evidence page stubs from a claims registry (YAML or JSON) with:

- Auto-generated evidence IDs
- Prefilled front-matter from claim data
- Bidirectional links to source pages
- Skeleton methodology sections

### Usage

```bash
# Generate all evidence pages
python3 tools/generate_evidence_page.py

# Specify custom registry path
python3 tools/generate_evidence_page.py --registry branding/governance/claims_registry.json

# Force overwrite existing pages
python3 tools/generate_evidence_page.py --force
```

### Evidence ID Generation

Evidence IDs are generated from claim data:

**Format**: `{domain}-{claim-type}-{claim-snippet}-{quarter}`

**Example**: `lukhas-ai-performance-p95-latency-2025-q4`

The generator:
1. Extracts domain from claim
2. Infers claim type from claim text (performance, accuracy, security, etc.)
3. Creates snippet from key terms (percentages, latency, technical terms)
4. Adds current quarter (YYYY-qN)
5. Slugifies to URL-safe format (max 80 chars)

### Claim Type Inference

The generator automatically infers claim type from claim text:

- **performance**: Contains "latency", "throughput", "p95", "p99", "ms", "performance"
- **accuracy**: Contains "accuracy", "precision", "f1", "score", "correct"
- **security**: Contains "security", "encryption", "AES", "TLS", "secure"
- **compliance**: Contains "compliance", "GDPR", "WCAG", "ISO", "SOC2"
- **usage**: Contains "users", "requests", "operations", "capacity", "scale"
- **general**: Default if no patterns match

### Prefilled Placeholders

The generator prefills:

- Evidence ID, claim type, claim statement, domains
- Verification dates (today + offsets for legal approval, next review)
- Artifact paths using evidence ID
- Bidirectional links to source pages
- Methodology skeleton with placeholders

Placeholders marked `[Describe...]` or `[Specify...]` must be filled manually.

---

## Validator Tool

### Overview

**Path**: `tools/validate_evidence_pages.py`

The validator checks evidence pages for:

- Required front-matter fields
- Valid claim types and date formats
- Legal approval for customer-facing claims
- Artifact references and SHA256 hash format
- Bidirectional link integrity
- Unfilled placeholders in body text

### Usage

```bash
# Basic validation
python3 tools/validate_evidence_pages.py

# Check bidirectional links
python3 tools/validate_evidence_pages.py --check-bidirectional

# Strict mode (warnings = errors)
python3 tools/validate_evidence_pages.py --strict

# Custom evidence directory
python3 tools/validate_evidence_pages.py --evidence-dir release_artifacts/evidence
```

### Validation Checks

#### 1. Required Fields

Ensures all required front-matter fields are present:
- evidence_id, claim_type, claim_statement, domains
- verified_by, verified_date

Missing fields → **ERROR**

#### 2. Recommended Fields

Checks for recommended fields:
- legal_approved, pages_using_claim, methodology, artifacts

Missing fields → **WARNING**

#### 3. Claim Type Validation

Ensures `claim_type` is one of:
- performance, security, compliance, usage, accuracy, general

Invalid type → **ERROR**

#### 4. Date Format Validation

Checks date fields are formatted as `YYYY-MM-DD`:
- verified_date, legal_approved_date, next_review

Invalid format → **ERROR**
Past next_review → **WARNING**

#### 5. Legal Approval

For customer-facing domains (lukhas.ai, lukhas.eu, lukhas.com):
- `legal_approved: true` → checks for legal_approved_by and legal_approved_date
- `legal_approved: false` or missing → **WARNING**

Missing approval fields → **WARNING**

#### 6. Artifact Validation

For each artifact:
- Checks for `path`, `type`, `hash` fields
- Validates SHA256 hash format: `sha256-[64 hex chars]`
- Checks if artifact file exists (INFO if missing)

Invalid hash format → **WARNING**
Missing artifact file → **INFO**

#### 7. Bidirectional Link Validation

(Only with `--check-bidirectional` flag)

For each page in `pages_using_claim`:
1. Checks if page file exists
2. Parses page front-matter
3. Verifies page references this evidence page in `evidence_links`

Missing reference → **WARNING**
Non-existent page → **ERROR**

#### 8. Placeholder Detection

Scans body text for unfilled placeholders: `{{PLACEHOLDER}}`

Unfilled placeholders → **WARNING**

### Exit Codes

- `0` - All checks pass (or warnings in non-strict mode)
- `1` - Errors found, or warnings in strict mode

---

## Workflow

### Evidence Page Lifecycle

```
1. Claim Created
   ↓
2. Auto-Generate Evidence Stub
   ↓
3. Fill Methodology & Results
   ↓
4. Link Artifacts
   ↓
5. Technical Verification
   ↓
6. Legal Approval (if customer-facing)
   ↓
7. Validation & CI Checks
   ↓
8. Quarterly Review
```

### Step-by-Step Process

#### Step 1: Create Claim in Content

Add claim to marketing page with front-matter:

```yaml
---
title: "LUKHAS AI - Homepage"
domain: lukhas.ai
evidence_links: []  # Will be filled after evidence page created
claims_approval: false
claims_verified_by: []
---

MATRIZ delivers **<250ms p95 reasoning latency** in production environments.
```

#### Step 2: Generate Claims Registry

```bash
# If generate_claims_registry.py exists
python3 tools/generate_claims_registry.py

# Output: release_artifacts/claims_registry.yaml or branding/governance/claims_registry.json
```

#### Step 3: Generate Evidence Page Stub

```bash
make evidence-pages
# Or: python3 tools/generate_evidence_page.py
```

Creates: `release_artifacts/evidence/lukhas-ai-performance-p95-latency-2025-q4.md`

#### Step 4: Fill Methodology

Edit the generated evidence page:

1. **Test Environment**: Describe infrastructure, load, dataset
2. **Data Collection**: Specify period, sample size, monitoring approach
3. **Tools & Instrumentation**: List tools, versions, configurations
4. **Results**: Add actual measurements (p50, p95, p99, etc.)
5. **Statistical Confidence**: Calculate margin of error, std dev
6. **Artifacts**: Link JSON/CSV/PNG files, calculate SHA256 hashes

#### Step 5: Link Artifacts

Store test results in `release_artifacts/perf/`:

```bash
# Generate SHA256 hash
sha256sum release_artifacts/perf/matriz-p95-2025-q3.json

# Add to front-matter
artifacts:
  - path: 'release_artifacts/perf/matriz-p95-2025-q3.json'
    type: json
    hash: sha256-abc123def456...
```

#### Step 6: Technical Verification

Assigned reviewer (@web-architect, @qa-lead):

1. Reviews methodology for correctness
2. Validates measurements match artifacts
3. Checks limitations are documented
4. Updates `verified_by` and `verified_date`
5. Sets status to "Verified"

#### Step 7: Legal Approval

For customer-facing claims:

1. Submit evidence page to @legal
2. Legal reviews claim statement, methodology, limitations
3. Legal approves or requests changes
4. Update front-matter:
   ```yaml
   legal_approved: true
   legal_approved_by: '@legal'
   legal_approved_date: '2025-10-24'
   ```

#### Step 8: Update Content Page

Add bidirectional link in content page front-matter:

```yaml
evidence_links:
  - 'release_artifacts/evidence/lukhas-ai-performance-p95-latency-2025-q4.md'
claims_approval: true
claims_verified_by: ['@web-architect', '@legal']
```

#### Step 9: Validate & CI

```bash
# Validate evidence pages
make evidence-validate-strict

# Validate content front-matter
python3 tools/front_matter_lint.py

# Validate vocabulary
make branding-vocab-lint
```

#### Step 10: Quarterly Review

Every 90 days or on trigger (version update, regression):

1. Re-run measurements
2. Update artifacts and results
3. Update verification date
4. Set new next_review date
5. Re-validate

---

## Artifact Management

### Artifact Storage

Evidence artifacts are stored in `release_artifacts/`:

```
release_artifacts/
├── evidence/                 # Evidence page markdown files
│   ├── matriz-p95-latency-2025-q3.md
│   └── lukhas-accuracy-benchmark-2025-q4.md
├── perf/                    # Performance test results
│   ├── matriz-p95-2025-q3.json
│   ├── matriz-p95-2025-q3.png
│   └── matriz-p95-2025-q3.csv
├── security/                # Security audit reports
├── compliance/              # Compliance certifications
└── benchmarks/              # Accuracy benchmarks
```

### Artifact Naming Convention

**Format**: `{component}-{metric}-{date}.{ext}`

Examples:
- `matriz-p95-latency-2025-q3.json`
- `lukhas-accuracy-gsm8k-2025-10-15.csv`
- `guardian-wcag-audit-2025-q4.pdf`

### SHA256 Hash Generation

```bash
# Generate SHA256 hash
sha256sum release_artifacts/perf/matriz-p95-2025-q3.json
# Output: abc123def456... matriz-p95-2025-q3.json

# Add to front-matter
artifacts:
  - path: 'release_artifacts/perf/matriz-p95-2025-q3.json'
    type: json
    hash: sha256-abc123def456...
```

### Artifact Signing (Optional)

For high-assurance claims, use GPG signing:

```bash
# Sign artifact
gpg --detach-sign --armor release_artifacts/perf/matriz-p95-2025-q3.json
# Creates: matriz-p95-2025-q3.json.asc

# Verify signature
gpg --verify release_artifacts/perf/matriz-p95-2025-q3.json.asc

# Add signature to front-matter
artifacts:
  - path: 'release_artifacts/perf/matriz-p95-2025-q3.json'
    type: json
    hash: sha256-abc123...
    signature:
      method: gpg
      sig_file: 'release_artifacts/perf/matriz-p95-2025-q3.json.asc'
      signer: '@web-architect'
```

---

## Legal Approval Process

### When Legal Approval is Required

Legal approval is **REQUIRED** for:

- ✅ Claims on customer-facing domains (lukhas.ai, lukhas.eu, lukhas.com)
- ✅ Performance claims (latency, throughput, accuracy percentages)
- ✅ Security claims (encryption, compliance certifications)
- ✅ Capacity claims (users, requests, operations)

Legal approval is **NOT REQUIRED** for:

- ❌ Internal documentation (lukhas.dev, lukhas.io)
- ❌ Developer-facing claims with clear caveats
- ❌ Open-source documentation

### Legal Review Checklist

@legal reviews:

1. **Claim Statement**: Is it accurate and not misleading?
2. **Methodology**: Is test environment representative of production?
3. **Limitations**: Are caveats clearly documented?
4. **Timeframe**: Is claim time-bound or evergreen?
5. **Compliance**: Does claim meet advertising standards (FTC, EU, ASA)?

### Approval Workflow

```yaml
# Before legal approval
legal_approved: false
legal_approved_by: '@legal'
legal_approved_date: null

# Submit to legal
# → Email evidence page to legal@lukhas.com
# → Include link to content pages using claim

# After legal approval
legal_approved: true
legal_approved_by: '@legal'
legal_approved_date: '2025-10-24'
```

### Legal Rejection

If legal rejects claim:

1. Update `legal_approved: false`
2. Add rejection reason to verification history
3. Update claim statement or methodology
4. Re-submit for review

---

## Bidirectional Linking

### Why Bidirectional Links Matter

Bidirectional links connect claims to evidence and evidence back to claims:

- **Forward Link**: Content page → Evidence page (via `evidence_links`)
- **Backward Link**: Evidence page → Content pages (via `pages_using_claim`)

This ensures:
- Claims can't be orphaned (always linked to evidence)
- Evidence can't be unused (always linked to claims)
- Changes to evidence trigger updates to all dependent pages

### Setting Up Forward Links

In content page front-matter:

```yaml
---
title: "LUKHAS AI - Homepage"
evidence_links:
  - 'release_artifacts/evidence/matriz-p95-latency-2025-q3.md'
  - 'release_artifacts/evidence/lukhas-accuracy-benchmark-2025-q4.md'
---
```

### Setting Up Backward Links

In evidence page front-matter:

```yaml
---
evidence_id: "matriz-p95-latency-2025-q3"
pages_using_claim:
  - 'branding/websites/lukhas.ai/homepage.md#L42'
  - 'branding/websites/lukhas.eu/homepage_matriz_ready.md#L67'
---
```

### Validating Bidirectional Links

```bash
# Check bidirectional link integrity
python3 tools/validate_evidence_pages.py --check-bidirectional
```

The validator checks:
1. Each page in `pages_using_claim` exists
2. Each page references this evidence page in `evidence_links`
3. Links are not broken or outdated

---

## Best Practices

### Methodology Documentation

✅ **DO**:
- Document exact test environment (regions, instance types, dataset)
- Specify data collection period and sample size
- List all tools with versions and configurations
- Include statistical measures (confidence level, margin of error)
- Document outlier removal criteria

❌ **DON'T**:
- Use vague terms like "production-like" without details
- Omit sample size or collection period
- Skip statistical analysis
- Hide negative results or outliers

### Limitation Documentation

✅ **DO**:
- Clearly state what claim does NOT cover
- Document known caveats and assumptions
- Specify expected variance and degradation triggers
- Define when re-measurement is needed

❌ **DON'T**:
- Overgeneralize results
- Omit important caveats
- Claim results apply to all scenarios

### Artifact Management

✅ **DO**:
- Store artifacts in version control for small files (<1MB)
- Use artifact signing for high-assurance claims
- Calculate and verify SHA256 hashes
- Include artifact metadata (size, format, columns)

❌ **DON'T**:
- Commit large binary files to git (use git-lfs or external storage)
- Link to external URLs that may disappear
- Skip hash verification

### Review Schedule

✅ **DO**:
- Set next_review to 90 days for stable claims
- Set next_review to 30 days for rapidly evolving claims
- Re-measure on major version updates
- Re-measure on performance regressions

❌ **DON'T**:
- Let evidence go stale (>6 months)
- Skip quarterly reviews
- Ignore regression alerts

---

## Troubleshooting

### Generator Issues

**Problem**: No claims registry found

```
❌ No claims registry found.
   Checked: release_artifacts/claims_registry.yaml
   Checked: branding/governance/claims_registry.json
```

**Solution**: Generate claims registry first:

```bash
python3 tools/generate_claims_registry.py
```

---

**Problem**: Evidence page already exists

```
⏭️  Skipping (exists): release_artifacts/evidence/matriz-p95-latency-2025-q3.md
```

**Solution**: Use `--force` to overwrite:

```bash
python3 tools/generate_evidence_page.py --force
```

---

### Validator Issues

**Problem**: Missing required fields

```
❌ matriz-p95-latency-2025-q3.md: Missing required fields: verified_by, verified_date
```

**Solution**: Add missing fields to front-matter:

```yaml
verified_by: ['@web-architect', '@qa-lead']
verified_date: '2025-10-23'
```

---

**Problem**: Invalid claim type

```
❌ lukhas-feature.md: Invalid claim_type 'general_performance'.
    Must be one of: performance, security, compliance, usage, accuracy, general
```

**Solution**: Use valid claim type:

```yaml
claim_type: "performance"  # Not "general_performance"
```

---

**Problem**: Unfilled placeholders

```
⚠️  matriz-p95-latency-2025-q3.md: Contains unfilled placeholders:
    TEST_ENVIRONMENT, DATA_COLLECTION, SAMPLE_SIZE ...
```

**Solution**: Replace placeholders with actual data:

```yaml
methodology:
  test_environment: "AWS us-east-1, m5.xlarge instances, 50K concurrent users"
  data_collection: "7-day continuous monitoring Oct 15-22, 2025"
  sample_size: "3,042,156 reasoning operations"
```

---

**Problem**: Bidirectional link broken

```
⚠️  matriz-p95-latency-2025-q3.md: Page branding/websites/lukhas.ai/homepage.md
    does not reference this evidence page in evidence_links
```

**Solution**: Add evidence link to content page:

```yaml
# In branding/websites/lukhas.ai/homepage.md
evidence_links:
  - 'release_artifacts/evidence/matriz-p95-latency-2025-q3.md'
```

---

## Related Documents

- **Template**: [evidence_page.md](../../templates/evidence_page.md) - Evidence page template
- **Generator**: [generate_evidence_page.py](../../../tools/generate_evidence_page.py) - Generator script
- **Validator**: [validate_evidence_pages.py](../../../tools/validate_evidence_pages.py) - Validator script
- **Gaps Analysis**: [GAPS_ANALYSIS.md](../strategic/GAPS_ANALYSIS.md) - Strategic context (A1)
- **Content Linting**: [CONTENT_LINTING.md](./CONTENT_LINTING.md) - Validation tools
- **Branding Policy**: [BRAND_POLICY.md](../../BRAND_POLICY.md) - Overall branding standards

---

**Document Version**: 2.0
**Last Updated**: 2025-11-08
**Review Cycle**: Quarterly
**Owner**: @web-architect
**Reviewers**: @content-lead, @legal
