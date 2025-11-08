#!/usr/bin/env python3
"""
Populate pages_using_claim in evidence pages based on claims registry.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Map claim texts to evidence IDs
CLAIM_TO_EVIDENCE = {
    "250": "matriz-p95-latency-250ms",
    "100": "api-response-100ms",
    "100%": "compliance-rate-100pct",
    "Deployment-Ready": "matriz-deployment-ready-q4-2025",
    "deployment-ready": "matriz-deployment-ready-production",
    "50": "memory-fold-retrieval-50ms",
    "200": "cloud-infrastructure-200ms",
    "99.7%": "guardian-compliance-997pct",
    "validated production": "validated-production-deployment-eu",
    "15": "constitutional-validation-15ms",
    "8": "constitutional-validation-8ms",
    "12": "constitutional-validation-12ms",
    "10": "lambda-id-token-validation-10ms",
    "5": "global-consciousness-sync-5ms",
    "30": "api-proxy-pattern-30ms",
    "95%": "experimental-design-95pct",
    "99.95%": "system-uptime-9995pct",
    "87%": "matriz-completion-87pct",
    "94%": "user-satisfaction-94pct",
    "99.9%": "privacy-compliance-999pct",
}


def main():
    """Populate pages_using_claim in evidence pages."""

    # Load claims registry
    registry_path = Path("branding/governance/claims_registry.json")
    with open(registry_path) as f:
        registry = json.load(f)

    # Build evidence -> pages mapping
    evidence_pages = defaultdict(list)

    for claim in registry['claims']:
        claim_text = claim['claim']
        claim_file = claim['file']
        claim_line = claim['line']

        # Get evidence ID for this claim
        evidence_id = CLAIM_TO_EVIDENCE.get(claim_text)

        if evidence_id:
            evidence_pages[evidence_id].append({
                'file': claim_file,
                'line': claim_line,
                'claim': claim_text,
                'context': claim['context'][:100]
            })

    # Update evidence pages
    evidence_dir = Path("release_artifacts/evidence")

    for evidence_id, pages in evidence_pages.items():
        evidence_file = evidence_dir / f"{evidence_id}.md"

        if not evidence_file.exists():
            print(f"⚠️  Evidence file not found: {evidence_file}")
            continue

        content = evidence_file.read_text(encoding='utf-8')

        # Find the pages_using_claim field and replace it
        def replace_pages_using_claim(match, pages=pages):
            new_section = "pages_using_claim:\n"
            for page in sorted(pages, key=lambda x: x['file']):
                # Use relative path from evidence page to branding page
                rel_path = f"../../{page['file']}"
                new_section += f"  - '{rel_path}'\n"
            return new_section.rstrip()

        # Replace empty pages_using_claim: []
        content = re.sub(
            r'pages_using_claim:\s*\[\]',
            replace_pages_using_claim,
            content
        )

        # Write back
        evidence_file.write_text(content, encoding='utf-8')
        print(f"✅ Updated {evidence_id}: {len(pages)} pages")

    print(f"\n✅ Updated {len(evidence_pages)} evidence pages with bidirectional links")


if __name__ == "__main__":
    main()
