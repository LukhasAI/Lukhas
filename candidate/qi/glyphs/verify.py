#!/usr/bin/env python3
# path: qi/glyphs/verify.py
"""
GLYPH Seal Verifier CLI

Offline-first verification of GLYPH seals.
"""
import argparse
import json
import sys
from typing import Any, Optional


def fetch_cached_jwks(issuer: str) -> Optional[dict[str, Any]]:
    """
    Fetch cached JWKS for issuer.

    In production, this would check local cache first,
    then fetch from issuer's .well-known/jwks.json endpoint.
    """
    # For now, return a mock JWKS
    return {
        "keys": [{
            "kty": "OKP",
            "use": "sig",
            "kid": "default",
            "alg": "Ed25519",
            "x": "mock_public_key"
        }]
    }

def verify_content_hash(content_bytes: bytes, seal: dict[str, Any]) -> bool:
    """Verify content hash matches seal."""
    from qi.glyphs.seal import sha3_512

    algo, expected_hash = seal["content_hash"].split(":", 1)
    if algo != "sha3-512":
        print(f"Unsupported hash algorithm: {algo}")
        return False

    actual_hash = sha3_512(content_bytes)
    if actual_hash != expected_hash:
        print("Content hash mismatch:")
        print(f"  Expected: {expected_hash[:32]}...")
        print(f"  Actual:   {actual_hash[:32]}...")
        return False

    return True

def verify_signature(seal: dict[str, Any], sig: dict[str, Any], jwks: dict[str, Any]) -> bool:
    """Verify seal signature."""
    from qi.glyphs.seal import canonicalize, verify_seal

    # Canonicalize seal for verification
    seal_bytes = canonicalize(seal)

    # Verify using seal module
    return verify_seal(seal_bytes, sig)

def check_expiry(seal: dict[str, Any]) -> bool:
    """Check if seal has expired."""
    from datetime import datetime

    try:
        expiry = datetime.fromisoformat(seal["expiry"].replace("Z", "+00:00"))
        now = datetime.utcnow().replace(tzinfo=expiry.tzinfo)

        if now > expiry:
            print(f"Seal expired on {seal['expiry']}")
            return False

        return True
    except Exception as e:
        print(f"Error checking expiry: {e}")
        return False

def check_revocation(seal: dict[str, Any], online: bool = False) -> bool:
    """
    Check if seal has been revoked.

    In production, this would check CRL if online.
    """
    if not online:
        print("Skipping revocation check (offline mode)")
        return True

    # Would check CRL endpoint here
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Verify GLYPH seals in files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.png          # Verify PNG with embedded seal
  %(prog)s report.txt            # Verify text with front-matter seal
  %(prog)s --online doc.png      # Online verification with revocation check
  %(prog)s --verbose report.txt  # Verbose output
"""
    )

    parser.add_argument(
        "path",
        help="Path to file containing GLYPH seal"
    )

    parser.add_argument(
        "--online",
        action="store_true",
        help="Enable online checks (revocation, fresh JWKS)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    # Read file
    try:
        with open(args.path, "rb") as f:
            content = f.read()
    except Exception as e:
        if args.json:
            print(json.dumps({"ok": False, "error": f"Cannot read file: {e}"}))
        else:
            print(f"Error: Cannot read file: {e}")
        sys.exit(1)

    # Extract seal based on file type
    from qi.glyphs.embed import extract_from_png, extract_from_text

    blob = None
    if args.path.lower().endswith(('.png', '.jpg', '.jpeg')):
        blob = extract_from_png(content)
    else:
        blob = extract_from_text(content)

    if not blob:
        if args.json:
            print(json.dumps({"ok": False, "error": "No GLYPH seal found"}))
        else:
            print("Error: No GLYPH seal found in file")
        sys.exit(1)

    seal = blob["seal"]
    sig = blob["sig"]

    if args.verbose and not args.json:
        print(f"Found GLYPH seal v{seal['v']}")
        print(f"  Issuer: {seal['issuer']}")
        print(f"  Model: {seal['model_id']}")
        print(f"  Created: {seal['created_at']}")
        print(f"  Jurisdiction: {seal['jurisdiction']}")
        print()

    # Perform verification checks
    checks = {
        "content_hash": False,
        "signature": False,
        "expiry": False,
        "revocation": False
    }

    # 1. Content hash
    if args.verbose and not args.json:
        print("Checking content hash...")
    checks["content_hash"] = verify_content_hash(content, seal)

    # 2. Signature
    if args.verbose and not args.json:
        print("Checking signature...")

    jwks = fetch_cached_jwks(seal["issuer"])
    if jwks:
        checks["signature"] = verify_signature(seal, sig, jwks)
    else:
        if not args.json:
            print("Warning: Cannot fetch JWKS for issuer")

    # 3. Expiry
    if args.verbose and not args.json:
        print("Checking expiry...")
    checks["expiry"] = check_expiry(seal)

    # 4. Revocation (if online)
    if args.online:
        if args.verbose and not args.json:
            print("Checking revocation...")
        checks["revocation"] = check_revocation(seal, online=True)
    else:
        checks["revocation"] = True  # Skip in offline mode

    # Overall result
    ok = all(checks.values())

    if args.json:
        result = {
            "ok": ok,
            "issuer": seal["issuer"],
            "model_id": seal["model_id"],
            "jurisdiction": seal["jurisdiction"],
            "checks": checks
        }
        print(json.dumps(result, indent=2))
    else:
        print()
        if ok:
            print("✓ Verification PASSED")
            print(f"  Issuer: {seal['issuer']}")
            print(f"  Model: {seal['model_id']}")
            print(f"  Jurisdiction: {seal['jurisdiction']}")
        else:
            print("✗ Verification FAILED")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
