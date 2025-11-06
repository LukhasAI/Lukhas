---
id: "{{CLAIM_ID}}"                  # unique id, e.g., matriz-p95-2025q3
title: "Evidence — {{SHORT_CLAIM}}" # short descriptive title
claim_text: "{{EXACT_CLAIM_TEXT}}"  # exact marketing copy that asserted the claim
domain: "lukhas.ai"
owner: "@web-architect"
last_verified: "YYYY-MM-DD"
verified_by:
  - "@web-architect"
status: "draft" # draft | verified | deprecated
artifact_links:
  - "release_artifacts/perf/2025-10-26-matriz-smoke.json"
signature: null   # filled after signing: {"method":"gpg","sig_file":"...","sig_hash":"..."}
metadata:
  created_at: "YYYY-MM-DD"
  generated_by: "generate_evidence_pages.py"
---

# Evidence: {{SHORT_CLAIM}}

**Claim:**
{{EXACT_CLAIM_TEXT}}

## Summary
Short 2–3 sentence explanation of what the claim means and the scope (environments, dataset, date).

## Methodology
Describe precisely how the measurement was made:
- Test harness (branch/commit)
- Workload description
- Input data / dataset names
- Number of runs, aggregation method (e.g., p95 across N runs)
- Environment (regions, hardware, network conditions)

## Artifacts
List of artifacts (linked, with short descriptions and sha256).
- `release_artifacts/perf/2025-10-26-matriz-smoke.json` — smoke test raw output. SHA256: `<sha256>`

## Limitations & assumptions
Short bullet list: what this claim does *not* cover, known caveats, expected variation.

## Approval & signature
- Verified by: `@web-architect` on `YYYY-MM-DD`
- Legal: `@legal` (if required)
- Signature: See `signature` field in front-matter (signed metadata / detached signature)

## Full artifacts
(If the artifact is too large, add pointer to internal blobstore or S3 path and the signed `metadata.json` below.)

---

## Usage Instructions

This template is used to create evidence pages that back up numeric or operational claims made in LUKHAS marketing materials.

### When to Create an Evidence Page

Create an evidence page for any claim that includes:
- Performance metrics (e.g., "p95 latency < 250ms")
- Accuracy percentages (e.g., "94% accuracy")
- System capabilities (e.g., "supports 1M requests/day")
- Compliance statements (e.g., "WCAG AAA compliant")

### How to Use This Template

1. **Copy this template** to `release_artifacts/evidence/<claim-id>.md`
2. **Replace all {{PLACEHOLDERS}}** with actual values
3. **Fill in all sections** with precise methodology and artifacts
4. **Link artifacts** with SHA256 hashes for verification
5. **Get approval** from web-architect and legal (if needed)
6. **Sign metadata** using `tools/build_audit_pack.py`
7. **Reference** from page front-matter via `evidence_links`

### Auto-Generation

Use `tools/generate_evidence_pages.py` to automatically create evidence page stubs from the claims registry:

```bash
python3 tools/generate_claims_registry.py   # Generate registry
python3 tools/generate_evidence_pages.py    # Create evidence stubs
```

### Validation

Evidence pages are validated by:
- `tools/evidence_check.py` - Ensures claims have evidence
- `tools/front_matter_lint.py` - Validates YAML front-matter
- CI workflows in `.github/workflows/content-lint.yml`

---

**Version**: 1.0
**Last Updated**: 2025-11-06
**Source**: T4 Strategic Audit deliverable (STRATEGY.md)
**Canonical Location**: `branding/templates/evidence_page.md`
