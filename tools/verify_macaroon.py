#!/usr/bin/env python3
"""
Macaroon Verification Tool

Standalone tool for verifying macaroons and extracting OPA input.
Integrates with existing ΛiD authentication system.
"""

import sys

from tier_macaroon_issuer import TierMacaroonVerifier


def main():
    """Verify macaroon and output OPA input JSON."""
    if len(sys.argv) != 2:
        print("Usage: verify_macaroon.py <macaroon_token>", file=sys.stderr)
        sys.exit(1)

    token = sys.argv[1]
    verifier = TierMacaroonVerifier()
    result = verifier.verify_capability(token)

    import json
    print(json.dumps(result, indent=2))

    # Exit with error code if verification failed
    if not result.get("valid", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
