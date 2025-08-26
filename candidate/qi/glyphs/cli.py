# path: qi/glyphs/cli.py
"""
LUKHAS AI GLYPH CLI

Comprehensive command-line interface for creating, verifying, and managing
cryptographic seals for AI artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys

from .embed import auto_embed_seal, auto_extract_seal
from .seal import GlyphSigner, policy_fingerprint_from_files
from .verify import GlyphVerifier, verify_compact_seal


def hash_file(file_path: str) -> str:
    """Compute SHA3-512 hash of file content"""
    hasher = hashlib.sha3_512()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return f"sha3-512:{hasher.hexdigest()}"

def create_seal_command(args):
    """Create a new GLYPH seal"""
    try:
        # Compute content hash
        content_hash = hash_file(args.file)
        print(f"Content hash: {content_hash}")

        # Read content for actual sealing
        with open(args.file, 'rb') as f:
            content_bytes = f.read()

        # Determine media type
        import mimetypes
        media_type, _ = mimetypes.guess_type(args.file)
        if not media_type:
            media_type = "application/octet-stream"

        # Generate policy fingerprint if not provided
        policy_fp = args.policy_fingerprint
        if not policy_fp:
            if not args.policy_root:
                print("Error: --policy-root required when policy fingerprint not provided")
                return 1
            policy_fp = policy_fingerprint_from_files(args.policy_root, args.overlays)
            print(f"Policy fingerprint: {policy_fp}")

        # Create signer
        signer = GlyphSigner(key_id=args.key_id or "cli-key-001")

        # Parse calibration reference if provided
        calib_ref = None
        if args.calib_ref:
            try:
                calib_ref = json.loads(args.calib_ref)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in --calib-ref: {args.calib_ref}")
                return 1

        # Create seal
        result = signer.create_seal(
            content_bytes=content_bytes,
            media_type=media_type,
            issuer=args.issuer,
            model_id=args.model_id,
            policy_fingerprint=policy_fp,
            jurisdiction=args.jurisdiction,
            proof_bundle=args.proof_bundle,
            ttl_days=args.ttl_days,
            calib_ref=calib_ref,
            prev=args.prev
        )

        # Save seal
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Seal saved to: {args.output}")
        else:
            print("Seal created:")
            print(json.dumps(result, indent=2))

        # Embed in file if requested
        if args.embed:
            output_file = auto_embed_seal(args.file, result, args.embed_output)
            print(f"Seal embedded in: {output_file}")

        # Generate QR code if requested
        if args.qr:
            try:
                import qrcode
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(result["compact"])
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                img.save(args.qr)
                print(f"QR code saved to: {args.qr}")
            except ImportError:
                print("Warning: qrcode library not available for QR generation")

        return 0

    except Exception as e:
        print(f"Seal creation failed: {e}")
        return 1

def verify_seal_command(args):
    """Verify a GLYPH seal"""
    try:
        # Read content
        with open(args.file, 'rb') as f:
            content_bytes = f.read()

        # Load JWKS if provided
        jwks = {}
        if args.jwks:
            with open(args.jwks) as f:
                jwks_data = json.load(f)
                # Convert JWKS to simple key_id -> public_key mapping
                for key in jwks_data.get("keys", []):
                    if "kid" in key and "x" in key:
                        jwks[key["kid"]] = key["x"]

        # Verify based on input type
        if args.compact:
            # Compact seal verification
            compact_seal = args.seal.strip()
            result = verify_compact_seal(compact_seal, content_bytes, jwks)
        else:
            # JSON seal file verification
            with open(args.seal) as f:
                seal_package = json.load(f)

            seal_data = seal_package.get("seal", {})
            signature_data = seal_package.get("signature", {})

            verifier = GlyphVerifier(jwks)
            result = verifier.verify_seal(content_bytes, seal_data, signature_data, args.online)

        # Display results
        print(f"Verification: {'✅ VALID' if result.valid else '❌ INVALID'}")
        print(f"Issuer: {result.issuer}")
        print(f"Model: {result.model_id}")
        print(f"Created: {result.created_at}")
        print(f"Jurisdiction: {result.jurisdiction}")
        print(f"Content Hash: {result.content_hash}")

        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                print(f"  • {error}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  • {warning}")

        if result.online_checked:
            print(f"\n🌐 Online Status: {result.revocation_status}")

        return 0 if result.valid else 1

    except Exception as e:
        print(f"Verification failed: {e}")
        return 1

def extract_seal_command(args):
    """Extract seal from embedded file"""
    try:
        seal_data, clean_path = auto_extract_seal(args.file)

        if seal_data:
            # Save extracted seal
            output_file = args.output or f"{args.file}.seal.json"
            with open(output_file, 'w') as f:
                json.dump(seal_data, f, indent=2)

            print(f"✅ Seal extracted: {output_file}")
            if clean_path:
                print(f"📄 Clean content: {clean_path}")

            # Show seal information
            seal = seal_data.get("seal", {})
            print("\n📋 Seal Information:")
            print(f"  Issuer: {seal.get('issuer')}")
            print(f"  Model: {seal.get('model_id')}")
            print(f"  Created: {seal.get('created_at')}")
            print(f"  Jurisdiction: {seal.get('jurisdiction')}")
            print(f"  Expiry: {seal.get('expiry')}")

            # Verify if requested
            if args.verify:
                print("\n🔍 Verifying extracted seal...")

                # Read original content
                if clean_path:
                    with open(clean_path, 'rb') as f:
                        content_bytes = f.read()
                else:
                    with open(args.file, 'rb') as f:
                        content_bytes = f.read()

                seal_data_inner = seal_data.get("seal", {})
                signature_data = seal_data.get("signature", {})

                verifier = GlyphVerifier()
                result = verifier.verify_seal(content_bytes, seal_data_inner, signature_data)

                print(f"  Result: {'✅ VALID' if result.valid else '❌ INVALID'}")
                if result.errors:
                    for error in result.errors:
                        print(f"  ❌ {error}")
        else:
            print("❌ No GLYPH seal found in file")
            return 1

        return 0

    except Exception as e:
        print(f"Extraction failed: {e}")
        return 1

def info_command(args):
    """Show information about GLYPH system"""
    print("🔒 LUKHAS AI GLYPH Cryptographic Seal System v0.1")
    print("   Portable, quantum-resistant attestations for AI artifacts")
    print()
    print("📋 Supported Operations:")
    print("  • create  - Create cryptographic seals")
    print("  • verify  - Verify seal authenticity")
    print("  • extract - Extract seals from embedded files")
    print("  • embed   - Embed seals into files")
    print()
    print("🔧 Supported File Types:")
    print("  • PNG     - Embedded in tEXt chunk")
    print("  • JPEG    - Embedded in EXIF UserComment")
    print("  • Text    - Embedded as HTML comment")
    print("  • PDF     - Embedded in metadata (TODO)")
    print()
    print("🔐 Cryptographic Algorithms:")
    print("  • Ed25519 - Development and testing")
    print("  • Dilithium3 - Production (quantum-resistant)")
    print()
    print("🌐 Verification:")
    print("  • Offline - Using JWKS public keys")
    print("  • Online  - With revocation checking")
    print()
    print("For more information: https://docs.lukhas.ai/glyph")

    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="glyph",
        description="LUKHAS AI GLYPH Cryptographic Seal System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a cryptographic seal")
    create_parser.add_argument("file", help="File to seal")
    create_parser.add_argument("--issuer", required=True, help="Issuer ID (lukhas://org/<tenant>)")
    create_parser.add_argument("--model-id", required=True, help="Model identifier")
    create_parser.add_argument("--proof-bundle", required=True, help="Proof bundle URL")
    create_parser.add_argument("--policy-root", help="Policy pack root directory")
    create_parser.add_argument("--policy-fingerprint", help="Pre-computed policy fingerprint")
    create_parser.add_argument("--overlays", help="Policy overlay directory")
    create_parser.add_argument("--jurisdiction", default="global", help="Jurisdiction")
    create_parser.add_argument("--ttl-days", type=int, default=365, help="Seal validity days")
    create_parser.add_argument("--calib-ref", help="Calibration reference JSON")
    create_parser.add_argument("--prev", help="Previous seal ID for chaining")
    create_parser.add_argument("--key-id", help="Signing key ID")
    create_parser.add_argument("--output", help="Output JSON file")
    create_parser.add_argument("--embed", action="store_true", help="Embed seal in original file")
    create_parser.add_argument("--embed-output", help="Output file for embedded version")
    create_parser.add_argument("--qr", help="Generate QR code PNG")
    create_parser.set_defaults(func=create_seal_command)

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a cryptographic seal")
    verify_parser.add_argument("file", help="Original content file")
    verify_parser.add_argument("seal", help="Seal JSON file or compact seal string")
    verify_parser.add_argument("--jwks", help="JWKS file for key verification")
    verify_parser.add_argument("--online", action="store_true", help="Perform online verification")
    verify_parser.add_argument("--compact", action="store_true", help="Seal is compact format")
    verify_parser.set_defaults(func=verify_seal_command)

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract seal from embedded file")
    extract_parser.add_argument("file", help="File with embedded seal")
    extract_parser.add_argument("--output", help="Output JSON file for extracted seal")
    extract_parser.add_argument("--verify", action="store_true", help="Verify extracted seal")
    extract_parser.set_defaults(func=extract_seal_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")
    info_parser.set_defaults(func=info_command)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
