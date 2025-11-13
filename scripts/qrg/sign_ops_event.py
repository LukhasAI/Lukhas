#!/usr/bin/env python3
"""
QRG Operational Event Signing Script

This script provides utilities for signing operational events with QRG
(Quantum Resilient Glyph) cryptographic signatures. It supports signing
release notes, policy changes, and other operational decisions requiring
tamper-evident provenance.

Usage:
    python sign_ops_event.py sign-release --version 1.0.0 --notes "Security fixes" --key path/to/key.pem
    python sign_ops_event.py sign-policy --policy-id drift_threshold --change "Increased to 0.20" --key path/to/key.pem
    python sign_ops_event.py verify --signature path/to/signature.json

Dependencies:
    - core.qrg.signing (QRG signature implementation)
    - core.qrg.model (QRGSignature data model)
"""

import argparse
import json

# Add project root to path if needed
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.qrg.model import QRGSignature
from core.qrg.signing import qrg_sign, qrg_verify


def sign_release_notes(
    version: str,
    notes: str,
    key_path: str,
    date: Optional[str] = None,
    author: Optional[str] = None,
    consent_hash: Optional[str] = None
) -> dict:
    """
    Sign software release notes with QRG signature.

    Args:
        version: Semantic version string (e.g., "1.0.0")
        notes: Release notes text describing changes
        key_path: Path to PEM-encoded private key file
        date: Release date (ISO 8601 format, defaults to now)
        author: Release author/team name (defaults to "LUKHAS AI Team")
        consent_hash: Optional hash linking to approval/consent document

    Returns:
        Dictionary containing payload and QRG signature with structure:
        {
            "payload": {
                "type": "release_notes",
                "version": "1.0.0",
                "date": "2025-11-12",
                "notes": "Release notes text",
                "author": "LUKHAS AI Team"
            },
            "qrg_signature": {
                "algo": "ecdsa-sha256",
                "pubkey_pem": "...",
                "sig_b64": "...",
                "ts": "2025-11-12T18:30:00.000Z",
                "payload_hash": "...",
                "consent_hash": null
            }
        }

    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If key file is invalid or signature generation fails
    """
    # Validate inputs
    if not version:
        raise ValueError("Version cannot be empty")
    if not notes:
        raise ValueError("Release notes cannot be empty")

    key_file = Path(key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Private key file not found: {key_path}")

    # Load private key
    try:
        with open(key_file, "rb") as f:
            priv_pem = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read private key: {e}") from e

    # Build payload
    payload = {
        "type": "release_notes",
        "version": version,
        "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
        "notes": notes,
        "author": author or "LUKHAS AI Team"
    }

    # Generate signature
    try:
        signature = qrg_sign(payload, priv_pem, consent_hash=consent_hash)
    except Exception as e:
        raise ValueError(f"Failed to generate QRG signature: {e}") from e

    # Return combined result
    return {
        "payload": payload,
        "qrg_signature": signature.to_dict() if isinstance(signature, QRGSignature) else signature
    }


def sign_policy_change(
    policy_id: str,
    change_desc: str,
    key_path: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    approved_by: Optional[str] = None,
    reason: Optional[str] = None,
    consent_hash: Optional[str] = None
) -> dict:
    """
    Sign Guardian policy change with QRG signature.

    Args:
        policy_id: Unique identifier for the policy being changed
        change_desc: Human-readable description of the change
        key_path: Path to PEM-encoded private key file
        old_value: Previous policy value (if applicable)
        new_value: New policy value (if applicable)
        approved_by: Entity/committee that approved the change
        reason: Justification for policy change
        consent_hash: Optional hash linking to approval document

    Returns:
        Dictionary containing payload and QRG signature with structure:
        {
            "payload": {
                "type": "policy_change",
                "policy_id": "guardian_drift_threshold",
                "change_desc": "Increased drift threshold",
                "old_value": "0.15",
                "new_value": "0.20",
                "approved_by": "governance_committee",
                "reason": "Reduce false positives",
                "timestamp": "2025-11-12T18:30:00.000Z"
            },
            "qrg_signature": {...}
        }

    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If key file is invalid or signature generation fails
    """
    # Validate inputs
    if not policy_id:
        raise ValueError("Policy ID cannot be empty")
    if not change_desc:
        raise ValueError("Change description cannot be empty")

    key_file = Path(key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Private key file not found: {key_path}")

    # Load private key
    try:
        with open(key_file, "rb") as f:
            priv_pem = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read private key: {e}") from e

    # Build payload
    payload = {
        "type": "policy_change",
        "policy_id": policy_id,
        "change_desc": change_desc,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Add optional fields if provided
    if old_value is not None:
        payload["old_value"] = old_value
    if new_value is not None:
        payload["new_value"] = new_value
    if approved_by:
        payload["approved_by"] = approved_by
    if reason:
        payload["reason"] = reason

    # Generate signature
    try:
        signature = qrg_sign(payload, priv_pem, consent_hash=consent_hash)
    except Exception as e:
        raise ValueError(f"Failed to generate QRG signature: {e}") from e

    # Return combined result
    return {
        "payload": payload,
        "qrg_signature": signature.to_dict() if isinstance(signature, QRGSignature) else signature
    }


def verify_signature(signature_data: dict) -> bool:
    """
    Verify a QRG signature against its payload.

    Args:
        signature_data: Dictionary containing "payload" and "qrg_signature" keys

    Returns:
        True if signature is valid, False otherwise

    Raises:
        ValueError: If signature_data is malformed
    """
    if "payload" not in signature_data:
        raise ValueError("Missing 'payload' field in signature data")
    if "qrg_signature" not in signature_data:
        raise ValueError("Missing 'qrg_signature' field in signature data")

    payload = signature_data["payload"]
    qrg = signature_data["qrg_signature"]

    try:
        return qrg_verify(payload, qrg)
    except Exception as e:
        print(f"Verification failed with error: {e}", file=sys.stderr)
        return False


def save_signature(signature_data: dict, output_path: str):
    """
    Save signed event to JSON file.

    Args:
        signature_data: Dictionary containing payload and signature
        output_path: Path to output JSON file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(signature_data, f, indent=2, sort_keys=True)

    print(f"Signature saved to: {output_file}")


def load_signature(signature_path: str) -> dict:
    """
    Load signed event from JSON file.

    Args:
        signature_path: Path to signature JSON file

    Returns:
        Dictionary containing payload and signature
    """
    signature_file = Path(signature_path)
    if not signature_file.exists():
        raise FileNotFoundError(f"Signature file not found: {signature_path}")

    with open(signature_file) as f:
        return json.load(f)


def main():
    """Command-line interface for QRG operational signing."""
    parser = argparse.ArgumentParser(
        description="Sign operational events with QRG cryptographic signatures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign release notes
  %(prog)s sign-release --version 1.0.0 --notes "Security fixes" --key release_key.pem -o release_1.0.0.json

  # Sign policy change
  %(prog)s sign-policy --policy-id drift_threshold --change "Increased to 0.20" \\
      --old-value 0.15 --new-value 0.20 --key policy_key.pem -o policy_change.json

  # Verify signature
  %(prog)s verify --signature release_1.0.0.json
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Sign release notes command
    release_parser = subparsers.add_parser("sign-release", help="Sign release notes")
    release_parser.add_argument("--version", required=True, help="Semantic version (e.g., 1.0.0)")
    release_parser.add_argument("--notes", required=True, help="Release notes text")
    release_parser.add_argument("--key", required=True, help="Path to private key PEM file")
    release_parser.add_argument("--date", help="Release date (ISO 8601, defaults to now)")
    release_parser.add_argument("--author", help="Release author (defaults to 'LUKHAS AI Team')")
    release_parser.add_argument("--consent-hash", help="Optional consent document hash")
    release_parser.add_argument("-o", "--output", help="Output JSON file path (defaults to stdout)")

    # Sign policy change command
    policy_parser = subparsers.add_parser("sign-policy", help="Sign policy change")
    policy_parser.add_argument("--policy-id", required=True, help="Policy identifier")
    policy_parser.add_argument("--change", required=True, dest="change_desc", help="Change description")
    policy_parser.add_argument("--key", required=True, help="Path to private key PEM file")
    policy_parser.add_argument("--old-value", help="Previous policy value")
    policy_parser.add_argument("--new-value", help="New policy value")
    policy_parser.add_argument("--approved-by", help="Approving entity/committee")
    policy_parser.add_argument("--reason", help="Justification for change")
    policy_parser.add_argument("--consent-hash", help="Optional consent document hash")
    policy_parser.add_argument("-o", "--output", help="Output JSON file path (defaults to stdout)")

    # Verify signature command
    verify_parser = subparsers.add_parser("verify", help="Verify QRG signature")
    verify_parser.add_argument("--signature", required=True, help="Path to signed JSON file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "sign-release":
            # Sign release notes
            signature_data = sign_release_notes(
                version=args.version,
                notes=args.notes,
                key_path=args.key,
                date=args.date,
                author=args.author,
                consent_hash=args.consent_hash
            )

            if args.output:
                save_signature(signature_data, args.output)
            else:
                print(json.dumps(signature_data, indent=2, sort_keys=True))

            print("✅ Release notes signed successfully", file=sys.stderr)

        elif args.command == "sign-policy":
            # Sign policy change
            signature_data = sign_policy_change(
                policy_id=args.policy_id,
                change_desc=args.change_desc,
                key_path=args.key,
                old_value=args.old_value,
                new_value=args.new_value,
                approved_by=args.approved_by,
                reason=args.reason,
                consent_hash=args.consent_hash
            )

            if args.output:
                save_signature(signature_data, args.output)
            else:
                print(json.dumps(signature_data, indent=2, sort_keys=True))

            print("✅ Policy change signed successfully", file=sys.stderr)

        elif args.command == "verify":
            # Verify signature
            signature_data = load_signature(args.signature)

            print(f"Verifying signature from: {args.signature}", file=sys.stderr)
            print(f"Payload type: {signature_data['payload'].get('type', 'unknown')}", file=sys.stderr)

            if verify_signature(signature_data):
                print("✅ Signature is VALID", file=sys.stderr)
                sys.exit(0)
            else:
                print("❌ Signature is INVALID", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
