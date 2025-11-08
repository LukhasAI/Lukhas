#!/usr/bin/env python3
"""
Add evidence_links to branding pages for top 20 claims.
"""

import json
from pathlib import Path
from collections import defaultdict

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


def load_claims_registry():
    """Load the claims registry."""
    registry_path = Path("branding/governance/claims_registry.json")
    with open(registry_path, 'r') as f:
        return json.load(f)


def get_evidence_for_claim(claim_text):
    """Get evidence ID for a claim text."""
    return CLAIM_TO_EVIDENCE.get(claim_text)


def add_evidence_links_to_file(filepath, evidence_links):
    """Add evidence_links to a markdown file's front-matter."""

    content = filepath.read_text(encoding="utf-8")

    # Check if file has front-matter
    if not content.startswith('---'):
        print(f"  ⚠️  No front-matter found, skipping")
        return False

    # Split front-matter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print(f"  ⚠️  Invalid front-matter format, skipping")
        return False

    front_matter = parts[1]
    body = parts[2]

    # Check if evidence_links already exists
    if 'evidence_links:' in front_matter:
        # Update existing evidence_links
        # Find the evidence_links section
        lines = front_matter.split('\n')
        new_lines = []
        in_evidence_links = False
        evidence_links_added = False

        for line in lines:
            if line.strip().startswith('evidence_links:'):
                in_evidence_links = True
                new_lines.append('evidence_links:')
                # Add all evidence links
                for link in sorted(set(evidence_links)):
                    new_lines.append(f"  - 'release_artifacts/evidence/{link}.md'")
                evidence_links_added = True
            elif in_evidence_links and line.strip().startswith('-'):
                # Skip existing evidence links
                continue
            elif in_evidence_links and line and not line[0].isspace():
                # End of evidence_links section
                in_evidence_links = False
                new_lines.append(line)
            else:
                new_lines.append(line)

        front_matter = '\n'.join(new_lines)
    else:
        # Add evidence_links after title or at the end of front-matter
        lines = front_matter.split('\n')
        new_lines = []
        added = False

        for i, line in enumerate(lines):
            new_lines.append(line)
            # Add after title field
            if line.strip().startswith('title:') and not added:
                new_lines.append('evidence_links:')
                for link in sorted(set(evidence_links)):
                    new_lines.append(f"  - 'release_artifacts/evidence/{link}.md'")
                added = True

        # If not added after title, add at the end
        if not added:
            new_lines.append('evidence_links:')
            for link in sorted(set(evidence_links)):
                new_lines.append(f"  - 'release_artifacts/evidence/{link}.md'")

        front_matter = '\n'.join(new_lines)

    # Reconstruct file
    new_content = f"---{front_matter}---{body}"

    # Write back
    filepath.write_text(new_content, encoding="utf-8")
    return True


def main():
    """Add evidence links to branding pages."""

    print("=" * 80)
    print("ADDING EVIDENCE LINKS TO BRANDING PAGES")
    print("=" * 80)
    print()

    # Load claims registry
    print("Loading claims registry...")
    registry = load_claims_registry()

    # Build file -> evidence_links mapping
    file_evidence = defaultdict(set)

    for claim in registry['claims']:
        claim_text = claim['claim']
        claim_file = claim['file']

        # Get evidence ID for this claim
        evidence_id = get_evidence_for_claim(claim_text)

        if evidence_id:
            file_evidence[claim_file].add(evidence_id)

    # Show summary
    print(f"Found {len(file_evidence)} files with top 20 claims")
    print()

    # Update files
    updated_count = 0
    skipped_count = 0

    for filepath_str, evidence_ids in sorted(file_evidence.items()):
        filepath = Path(filepath_str)

        if not filepath.exists():
            print(f"⚠️  File not found: {filepath}")
            skipped_count += 1
            continue

        print(f"Updating: {filepath}")
        print(f"  Adding {len(evidence_ids)} evidence links:")
        for eid in sorted(evidence_ids):
            print(f"    - {eid}")

        if add_evidence_links_to_file(filepath, evidence_ids):
            print(f"  ✅ Updated")
            updated_count += 1
        else:
            print(f"  ❌ Failed")
            skipped_count += 1
        print()

    print("=" * 80)
    print(f"✅ Updated {updated_count} files")
    print(f"⚠️  Skipped {skipped_count} files")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review changes with: git diff branding/")
    print("2. Run validation: python3 tools/validate_evidence_pages.py --check-bidirectional")
    print("3. Run claims validation: python3 tools/validate_claims.py")
    print()


if __name__ == "__main__":
    main()
