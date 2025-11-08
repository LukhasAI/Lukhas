#!/usr/bin/env python3
"""
Generate comprehensive claims registry from branding content.

Scans all branding/websites/**/*.md files, extracts claims, validates
evidence_links exist, and generates master registry.

Usage:
    python3 tools/generate_claims_registry.py
    python3 tools/generate_claims_registry.py --output branding/governance/claims_registry.json

Requirements:
    pip install pyyaml
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml

# Claim patterns to extract
CLAIM_PATTERNS = [
    (r'(\d+(?:\.\d+)?%)', 'percentage'),  # Percentages: 99.7%, 87.5%
    (r'<(\d+)ms', 'latency'),  # Latencies: <250ms, <100ms
    (r'(\d+(?:,\d{3})*(?:\.\d+)?(?:K|M|B)?)\+?\s+(?:users|interactions|operations)', 'count'),  # Counts
    (r'(\d+(?:\.\d+)?x)\s+(?:faster|slower|improvement)', 'multiplier'),  # Multipliers
    (r'deployment-ready|validated\s+production', 'operational'),  # Operational claims
]

def extract_front_matter(file_path: Path) -> Dict[str, Any]:
    """Extract YAML front-matter from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return {}

    # Extract front-matter between --- markers
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        print(f"Warning: YAML parse error in {file_path}: {e}")
        return {}

def extract_claims(file_path: Path) -> List[Dict[str, Any]]:
    """Extract all claims from a markdown file."""
    claims = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"Warning: Could not read {file_path} (encoding issue)")
        return claims

    for i, line in enumerate(lines, 1):
        for pattern, claim_type in CLAIM_PATTERNS:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                # Normalize match
                claim_text = match if isinstance(match, str) else match[0] if isinstance(match, tuple) else str(match)

                claims.append({
                    'claim': claim_text,
                    'claim_type': claim_type,
                    'context': line.strip()[:200],
                    'file': str(file_path),
                    'line': i
                })

    return claims

def validate_evidence(file_path: Path, front_matter: Dict) -> Dict[str, Any]:
    """Validate evidence_links exist for claims."""
    evidence_links = front_matter.get('evidence_links', [])

    # Handle both list and empty list cases
    if not isinstance(evidence_links, list):
        evidence_links = []

    status = {
        'has_evidence_links': len(evidence_links) > 0,
        'evidence_links': evidence_links,
        'claims_approval': front_matter.get('claims_approval', False),
        'verified_by': front_matter.get('claims_verified_by', []),
        'verified_date': front_matter.get('claims_verified_date'),
        'missing_evidence': []
    }

    # Check if evidence files exist
    for evidence_link in evidence_links:
        # Handle both full paths and just filenames
        if isinstance(evidence_link, str):
            # Try multiple potential locations
            potential_paths = [
                Path(evidence_link),  # As-is
                Path('release_artifacts') / Path(evidence_link).name,  # Just filename in release_artifacts
                Path(evidence_link.replace('release_artifacts/', ''))  # Remove prefix if present
            ]

            found = False
            for potential_path in potential_paths:
                if potential_path.exists():
                    found = True
                    break

            if not found:
                status['missing_evidence'].append(evidence_link)

    return status

def generate_registry(output_path: Path):
    """Generate complete claims registry."""
    registry = {
        'version': '1.0',
        'generated_at': datetime.now().isoformat(),
        'evidence_artifacts_pr': '#1102',
        'claims': [],
        'summary': {
            'total_files_scanned': 0,
            'total_claims': 0,
            'verified': 0,
            'missing_evidence': 0,
            'not_approved': 0,
            'by_type': {}
        }
    }

    # Scan all branding files
    branding_path = Path('branding/websites')
    if not branding_path.exists():
        print(f"Error: {branding_path} not found")
        return

    branding_files = list(branding_path.rglob('*.md'))
    registry['summary']['total_files_scanned'] = len(branding_files)

    print(f"Scanning {len(branding_files)} files in branding/websites...")

    for file_path in branding_files:
        front_matter = extract_front_matter(file_path)
        claims = extract_claims(file_path)
        evidence_status = validate_evidence(file_path, front_matter)

        for claim_data in claims:
            claim_type = claim_data.get('claim_type', 'unknown')

            claim_entry = {
                **claim_data,
                **evidence_status,
                'status': 'verified' if (
                    evidence_status['claims_approval'] and
                    not evidence_status['missing_evidence'] and
                    evidence_status['has_evidence_links']
                ) else 'missing_evidence' if evidence_status['missing_evidence'] or not evidence_status['has_evidence_links'] else 'not_approved'
            }

            registry['claims'].append(claim_entry)
            registry['summary']['total_claims'] += 1

            # Track by type
            if claim_type not in registry['summary']['by_type']:
                registry['summary']['by_type'][claim_type] = 0
            registry['summary']['by_type'][claim_type] += 1

            # Track by status
            if claim_entry['status'] == 'verified':
                registry['summary']['verified'] += 1
            elif 'missing_evidence' in claim_entry['status']:
                registry['summary']['missing_evidence'] += 1
            else:
                registry['summary']['not_approved'] += 1

    # Save registry
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Claims registry generated: {output_path}")
    print(f"\n📊 Summary:")
    print(f"   Total files scanned: {registry['summary']['total_files_scanned']}")
    print(f"   Total claims: {registry['summary']['total_claims']}")
    print(f"   ✅ Verified: {registry['summary']['verified']}")
    print(f"   ⚠️  Missing evidence: {registry['summary']['missing_evidence']}")
    print(f"   ❌ Not approved: {registry['summary']['not_approved']}")
    print(f"\n📈 By Type:")
    for claim_type, count in sorted(registry['summary']['by_type'].items()):
        print(f"   {claim_type}: {count}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate claims registry from branding content')
    parser.add_argument('--output', default='branding/governance/claims_registry.json', help='Output JSON path')
    args = parser.parse_args()

    generate_registry(Path(args.output))
