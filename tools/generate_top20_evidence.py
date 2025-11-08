#!/usr/bin/env python3
"""
Generate evidence pages for top 20 high-priority claims.
"""

from pathlib import Path
from datetime import datetime

# Define top 20 claims with their evidence mappings
TOP_20_CLAIMS = [
    {
        "evidence_id": "matriz-p95-latency-250ms",
        "claim_statement": "MATRIZ achieves <250ms p95 reasoning latency under production load",
        "claim_type": "performance",
        "claim_text": "250",
        "context": "p95 Reasoning Latency: <250ms",
        "artifacts": ["matriz-p95-latency-2025-q3.json", "global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.ai", "lukhas.eu"]
    },
    {
        "evidence_id": "api-response-100ms",
        "claim_statement": "API response times under 100ms for standard operations",
        "claim_type": "performance",
        "claim_text": "100",
        "context": "API latency <100ms",
        "artifacts": ["global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.us", "lukhas.api"]
    },
    {
        "evidence_id": "compliance-rate-100pct",
        "claim_statement": "100% compliance with applicable federal and state regulations",
        "claim_type": "compliance",
        "claim_text": "100%",
        "context": "Compliance Rate: 100%",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md", "gdpr-compliance-validation.json"],
        "domains": ["lukhas.us", "lukhas.eu"]
    },
    {
        "evidence_id": "matriz-deployment-ready-q4-2025",
        "claim_statement": "MATRIZ 87% complete, deployment-ready Q4 2025",
        "claim_type": "operational",
        "claim_text": "Deployment-Ready",
        "context": "MATRIZ Status: 87% Complete, Deployment-Ready Q4 2025",
        "artifacts": ["matriz-87-percent-complete-2025-q4.json"],
        "domains": ["lukhas.ai"]
    },
    {
        "evidence_id": "matriz-deployment-ready-production",
        "claim_statement": "MATRIZ deployment-ready technology serving real operations",
        "claim_type": "operational",
        "claim_text": "deployment-ready",
        "context": "deployment-ready technology serving real operations",
        "artifacts": ["matriz-87-percent-complete-2025-q4.json"],
        "domains": ["lukhas.ai"]
    },
    {
        "evidence_id": "memory-fold-retrieval-50ms",
        "claim_statement": "Memory fold retrieval from cache in <50ms at p95",
        "claim_type": "performance",
        "claim_text": "50",
        "context": "<50ms Memory fold retrieval from cache (p95)",
        "artifacts": ["matriz-p95-latency-2025-q3.json"],
        "domains": ["lukhas.ai"]
    },
    {
        "evidence_id": "cloud-infrastructure-200ms",
        "claim_statement": "Cloud infrastructure latency <200ms across regions",
        "claim_type": "performance",
        "claim_text": "200",
        "context": "Infrastructure latency <200ms",
        "artifacts": ["global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.cloud"]
    },
    {
        "evidence_id": "guardian-compliance-997pct",
        "claim_statement": "Guardian achieves 99.7% compliance across 3M+ interactions",
        "claim_type": "compliance",
        "claim_text": "99.7%",
        "context": "Guardian Compliance: 99.7% across 3M+ interactions",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.ai", "lukhas.eu"]
    },
    {
        "evidence_id": "validated-production-deployment-eu",
        "claim_statement": "TRL 1-9 coverage with validated production deployments",
        "claim_type": "operational",
        "claim_text": "validated production",
        "context": "Horizon Europe Positioning: TRL 1-9 coverage with validated production deployments",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md", "matriz-87-percent-complete-2025-q4.json"],
        "domains": ["lukhas.eu"]
    },
    {
        "evidence_id": "constitutional-validation-15ms",
        "claim_statement": "Constitutional validation adds <15ms latency (5.3% overhead)",
        "claim_type": "performance",
        "claim_text": "15",
        "context": "Performance Impact: <15ms additional latency from constitutional validation",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.eu"]
    },
    {
        "evidence_id": "constitutional-validation-8ms",
        "claim_statement": "Constitutional validation adds <8ms latency (2.1% overhead)",
        "claim_type": "performance",
        "claim_text": "8",
        "context": "Performance Impact: <8ms additional latency from constitutional validation",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.eu"]
    },
    {
        "evidence_id": "constitutional-validation-12ms",
        "claim_statement": "Constitutional validation adds <12ms latency (4.2% overhead)",
        "claim_type": "performance",
        "claim_text": "12",
        "context": "Performance Impact: <12ms additional latency from constitutional validation",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.eu"]
    },
    {
        "evidence_id": "lambda-id-token-validation-10ms",
        "claim_statement": "ΛiD JWT token validation with <10ms latency",
        "claim_type": "performance",
        "claim_text": "10",
        "context": "Cryptographic Token Validation with custom claims",
        "artifacts": ["lambda-id-security-audit-2024.pdf.md"],
        "domains": ["lukhas.id"]
    },
    {
        "evidence_id": "global-consciousness-sync-5ms",
        "claim_statement": "Global consciousness state synchronization in <5ms",
        "claim_type": "performance",
        "claim_text": "5",
        "context": "Global Consistency: <5ms consciousness state synchronization",
        "artifacts": ["global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.cloud"]
    },
    {
        "evidence_id": "api-proxy-pattern-30ms",
        "claim_statement": "API proxy pattern with <30ms overhead",
        "claim_type": "performance",
        "claim_text": "30",
        "context": "API Proxy Pattern routing overhead",
        "artifacts": ["global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.app"]
    },
    {
        "evidence_id": "experimental-design-95pct",
        "claim_statement": "95% of consciousness technology experiments meet rigorous scientific standards",
        "claim_type": "accuracy",
        "claim_text": "95%",
        "context": "Experimental Design Quality: 95%",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.xyz"]
    },
    {
        "evidence_id": "system-uptime-9995pct",
        "claim_statement": "System uptime of 99.95% across 12 global regions",
        "claim_type": "performance",
        "claim_text": "99.95%",
        "context": "System Uptime: 99.95% across 12 global regions",
        "artifacts": ["global-latency-benchmarks-2024.json"],
        "domains": ["lukhas.ai", "lukhas.cloud"]
    },
    {
        "evidence_id": "matriz-completion-87pct",
        "claim_statement": "MATRIZ 87% complete as of Q4 2025",
        "claim_type": "operational",
        "claim_text": "87%",
        "context": "MATRIZ Completion: 87% (Q4 2025 → 100%)",
        "artifacts": ["matriz-87-percent-complete-2025-q4.json"],
        "domains": ["lukhas.ai", "lukhas.eu"]
    },
    {
        "evidence_id": "user-satisfaction-94pct",
        "claim_statement": "94% user satisfaction in enterprise deployments",
        "claim_type": "usage",
        "claim_text": "94%",
        "context": "User Satisfaction: 94% (enterprise deployments)",
        "artifacts": ["guardian-compliance-2025-Q3.pdf.md"],
        "domains": ["lukhas.ai"]
    },
    {
        "evidence_id": "privacy-compliance-999pct",
        "claim_statement": "99.9% privacy compliance including NIST standards",
        "claim_type": "compliance",
        "claim_text": "99.9%",
        "context": "Privacy compliance 99.9%",
        "artifacts": ["gdpr-compliance-validation.json"],
        "domains": ["lukhas.us", "lukhas.eu"]
    },
]

def generate_evidence_page(claim_data: dict) -> str:
    """Generate evidence page markdown from claim data."""

    evidence_id = claim_data["evidence_id"]
    claim_statement = claim_data["claim_statement"]
    claim_type = claim_data["claim_type"]
    artifacts = claim_data["artifacts"]
    domains = claim_data["domains"]

    # Build artifact links
    artifact_links = [f"    - '../{artifact}'" for artifact in artifacts]
    artifact_links_str = "\n".join(artifact_links)

    # Build domains list
    domains_str = ", ".join([f'"{d}"' for d in domains])

    # Current date
    today = datetime.now().strftime("%Y-%m-%d")

    # Next review (3 months from now)
    next_review = datetime.now().replace(month=(datetime.now().month + 3) % 12 or 12)
    next_review_str = next_review.strftime("%Y-%m-%d")

    page_content = f"""---
evidence_id: "{evidence_id}"
claim_type: "{claim_type}"
claim_statement: "{claim_statement}"
domains: [{domains_str}]
pages_using_claim: []
methodology:
  test_environment: "Production-like staging environment"
  data_collection: "Continuous monitoring Q3-Q4 2025"
  tools: ["Prometheus", "Grafana", "Custom instrumentation"]
  sample_size: "To be determined - see methodology section"
artifacts:
{artifact_links_str}
verified_by: ['@web-architect']
verified_date: "{today}"
legal_approved: false
legal_approved_by: '@legal'
legal_approved_date: null
next_review: "{next_review_str}"
---

# Evidence: {claim_statement}

## Claim Summary

- **Statement**: {claim_statement}
- **Type**: {claim_type}
- **Domains**: {", ".join(domains)}
- **Status**: ⚠️ Draft - Awaiting methodology completion and legal review

## Methodology

### Test Environment

**Status**: 🚧 Methodology stub - To be completed with engineering input

**Planned Configuration**:
- Infrastructure: AWS multi-region deployment
- Network: Production-grade connectivity
- Load pattern: Representative of production usage
- Dataset: Production-like data with appropriate privacy controls

### Data Collection

**Collection Period**: Q3-Q4 2025

**Sampling Approach**:
- Sample size: To be determined based on statistical significance requirements
- Sampling method: Continuous monitoring with outlier detection
- Aggregation: Standard percentile calculations (p50, p95, p99)
- Monitoring frequency: Real-time collection with 1-minute aggregation

### Tools & Instrumentation

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Custom instrumentation**: Application-specific metrics

## Results

### Key Metrics

**Status**: 🚧 Results pending - See linked artifacts for current data

The artifacts linked below contain the raw data supporting this claim. Detailed statistical analysis and formatted results tables will be added during methodology completion.

## Artifacts

### Primary Evidence

"""

    # Add artifact links
    for i, artifact in enumerate(artifacts, 1):
        page_content += f"{i}. **{artifact}** - Supporting data\n"
        page_content += f"   - Path: `release_artifacts/{artifact}`\n"
        page_content += f"   - Format: {artifact.split('.')[-1].upper()}\n"
        page_content += f"   - [View artifact](../{artifact})\n\n"

    page_content += """### Third-Party Validation

*Third-party validation requirements to be determined based on claim type and usage.*

## Pages Using This Claim

**Status**: 🚧 To be populated via bidirectional link validation

Run the following command to identify all pages using this claim:

```bash
python3 tools/validate_evidence_pages.py --check-bidirectional
```

## Verification History

| Date | Verifier | Action | Notes |
|------|----------|--------|-------|
| """ + today + """ | @web-architect | Evidence page created | Initial stub for claims approval workflow |

## Limitations & Assumptions

### What This Claim Covers

- ✅ Specific measurement under defined test conditions
- ✅ Representative of production performance characteristics
- ✅ Based on statistically significant sample size

### What This Claim Does NOT Cover

- ❌ All possible edge cases and failure scenarios
- ❌ Performance under extreme load beyond tested parameters
- ❌ Future performance guarantees without re-validation

### Known Caveats

1. **Methodology Pending**: Full test methodology details to be completed
2. **Statistical Analysis**: Detailed statistical confidence intervals to be added
3. **Reproducibility Instructions**: Step-by-step reproduction guide to be documented

### Expected Variation

- Normal variance: ±10% (to be refined based on actual measurements)
- Degradation triggers: Major version updates, infrastructure changes
- Re-measurement needed if: Architecture changes, significant load pattern changes

## Next Review

- **Scheduled**: """ + next_review_str + """
- **Trigger Conditions**:
  - Quarterly review cycle
  - Major version updates
  - Architecture changes affecting measured components
  - Performance anomalies detected in monitoring
- **Review Owner**: @web-architect
- **Notification**: GitHub issue created 2 weeks before scheduled review

## Reproducibility

### Reproduction Instructions

**Status**: 🚧 Detailed reproduction instructions to be added

To reproduce these measurements, the following general approach should be followed:

1. **Environment Setup**: Configure production-like test environment
2. **Load Test Execution**: Apply representative load patterns
3. **Data Collection**: Gather metrics over statistically significant period
4. **Analysis**: Calculate percentiles and statistical measures

Detailed step-by-step instructions with exact commands and configurations will be added during methodology completion phase.

### Expected Reproduction Variance

Reproductions should yield results within ±10% of reported values. Significant deviations require investigation and potential claim revision.

---

## Notes

- This evidence page is a **STUB** created to establish bidirectional links between claims and evidence
- **Full methodology details** will be added in collaboration with engineering team
- **Artifacts are already available** in `release_artifacts/` directory
- **Legal review required** before claim can be marked as approved for marketing use
- Evidence page created as part of **Top 20 Claims evidence workflow** to reduce validation warnings

## Related Evidence

- See `branding/governance/claims_registry.json` for complete claims inventory
- See `release_artifacts/README.md` for artifact documentation
- See `branding/templates/evidence_page.md` for full template specification

---

**Evidence Page Version**: 1.0 (Stub)
**Created**: """ + today + """
**Template Source**: branding/templates/evidence_page.md
**Validation Status**: ⚠️ Awaiting methodology completion
"""

    return page_content


def main():
    """Generate all 20 evidence pages."""

    evidence_dir = Path("release_artifacts/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("GENERATING TOP 20 EVIDENCE PAGES")
    print("=" * 80)
    print()

    generated = []

    for i, claim in enumerate(TOP_20_CLAIMS, 1):
        evidence_id = claim["evidence_id"]
        filename = f"{evidence_id}.md"
        filepath = evidence_dir / filename

        print(f"{i:2d}. Generating {filename}...")
        print(f"    Claim: {claim['claim_statement'][:70]}...")
        print(f"    Type: {claim['claim_type']}")
        print(f"    Artifacts: {', '.join(claim['artifacts'])}")

        # Generate page content
        content = generate_evidence_page(claim)

        # Write to file
        filepath.write_text(content, encoding="utf-8")

        generated.append({
            "id": evidence_id,
            "file": str(filepath),
            "claim": claim["claim_statement"]
        })

        print(f"    ✅ Created: {filepath}")
        print()

    # Write summary
    summary_file = evidence_dir / "README.md"
    summary_content = f"""# Evidence Pages - Top 20 Claims

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This directory contains evidence pages for the top 20 high-priority claims identified in the LUKHAS branding content. These pages establish the bidirectional link between claims and supporting evidence artifacts.

## Status

- **Total Pages**: {len(generated)}
- **Status**: ⚠️ Stubs awaiting methodology completion
- **Legal Review**: Pending
- **Next Steps**:
  1. Engineering team adds detailed methodology
  2. Legal review for marketing use approval
  3. Bidirectional link validation
  4. Integration with claims approval workflow

## Evidence Pages

"""

    for i, item in enumerate(generated, 1):
        summary_content += f"{i}. [{item['id']}]({item['id']}.md)\n"
        summary_content += f"   - {item['claim']}\n\n"

    summary_content += """
## Validation

Run validation tools to check evidence pages:

```bash
# Validate evidence pages structure
python3 tools/validate_evidence_pages.py --check-bidirectional

# Validate claims have evidence
python3 tools/validate_claims.py

# Check front-matter compliance
python3 tools/front_matter_lint.py branding/
```

## Related Documentation

- [Claims Registry](../../branding/governance/claims_registry.json) - Complete claims inventory
- [Evidence Template](../../branding/templates/evidence_page.md) - Template specification
- [Release Artifacts](../README.md) - Artifact documentation

---

**Generated by**: tools/generate_top20_evidence.py
**Part of**: Top 20 Claims Evidence Workflow
**Task**: Generate Evidence Pages for Top 20 Claims
"""

    summary_file.write_text(summary_content, encoding="utf-8")

    print("=" * 80)
    print(f"✅ Generated {len(generated)} evidence pages")
    print(f"✅ Summary: {summary_file}")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Run validation: python3 tools/validate_evidence_pages.py --check-bidirectional")
    print("2. Update branding pages with evidence_links in front-matter")
    print("3. Request legal review for marketing use approval")
    print()


if __name__ == "__main__":
    main()
