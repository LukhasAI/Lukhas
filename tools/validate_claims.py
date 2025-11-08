#!/usr/bin/env python3
"""
Validate all branding claims have evidence.

Usage:
    python3 tools/validate_claims.py
    python3 tools/validate_claims.py --strict  # Exit 1 on any violations

Exit codes:
    0 - All claims validated (or warnings only in non-strict mode)
    1 - Claims missing evidence or not approved
"""

import argparse
import json
import sys
from pathlib import Path


def validate_claims(strict=False):
    """Validate all claims have evidence and approval."""
    registry_path = Path('branding/governance/claims_registry.json')

    if not registry_path.exists():
        print("❌ Claims registry not found. Run tools/generate_claims_registry.py first.")
        sys.exit(1)

    with open(registry_path, encoding='utf-8') as f:
        registry = json.load(f)

    summary = registry['summary']
    violations = []
    warnings = []

    # Check for violations
    for claim in registry['claims']:
        if claim['status'] != 'verified':
            # Categorize severity
            if not claim.get('has_evidence_links'):
                violations.append(('missing_evidence', claim))
            elif claim.get('missing_evidence'):
                violations.append(('broken_link', claim))
            elif not claim.get('claims_approval'):
                warnings.append(('not_approved', claim))

    # Report
    print("📊 Claims Validation Report")
    print("=" * 60)
    print(f"Total claims: {summary['total_claims']}")
    print(f"✅ Verified: {summary['verified']}")
    print(f"⚠️  Missing evidence: {summary['missing_evidence']}")
    print(f"❌ Not approved: {summary['not_approved']}")
    print(f"\nGenerated from: PR {registry.get('evidence_artifacts_pr', 'unknown')}")

    if violations:
        print(f"\n🔍 VIOLATIONS FOUND ({len(violations)}):")

        for violation_type, violation in violations[:10]:  # Show first 10
            print(f"\n   Type: {violation_type}")
            print(f"   Claim: {violation['claim']}")
            print(f"   File: {violation['file']}:{violation['line']}")
            if violation.get('missing_evidence'):
                print(f"   Missing: {', '.join(violation['missing_evidence'])}")

        if len(violations) > 10:
            print(f"\n   ... and {len(violations) - 10} more violations")

        print(f"\n❌ VALIDATION FAILED - {len(violations)} violations")
        sys.exit(1)

    elif warnings and strict:
        print(f"\n⚠️  WARNINGS ({len(warnings)}) - Strict mode enabled:")
        for warning_type, warning in warnings[:5]:
            print(f"\n   Claim: {warning['claim']}")
            print(f"   File: {warning['file']}:{warning['line']}")
            print(f"   Issue: {warning_type}")

        print(f"\n❌ VALIDATION FAILED IN STRICT MODE - {len(warnings)} warnings")
        sys.exit(1)

    elif warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}) - Not approved but has evidence:")
        for warning_type, warning in warnings[:5]:
            print(f"   {warning['file']}: {warning['claim']}")
        print("\n✅ PASSED (warnings in non-strict mode)")
        sys.exit(0)

    else:
        print("\n✅ ALL CLAIMS VALIDATED")
        print(f"   {summary['verified']} claims verified with evidence and approval")
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate branding claims')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    args = parser.parse_args()

    validate_claims(strict=args.strict)
