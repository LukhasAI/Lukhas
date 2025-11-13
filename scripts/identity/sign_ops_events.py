"""
Operational Event Signing Script

This script generates a signed artifact for an operational event, such as
release notes or a policy change, using the Quantum Resonance Glyph (QRG)
system. The signed artifact is a JSON file containing the original content,
signing metadata, and the QRG signature.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock

# --- Mocking for missing modules ---
# Per the instructions, mock lukhas.* modules if they are not available
# in the execution environment of this script.
try:
    from lukhas.products.security.qrg.qrg_core import (
        ConsciousnessContext,
        QIResonanceGlyph,
    )
except ImportError:
    print(
        "Warning: Could not import 'lukhas' modules. Using mock for QIResonanceGlyph.",
        file=sys.stderr,
    )

    # Define a mock class that simulates the necessary methods and outputs
    class MockQIGlyph:
        def to_dict(self):
            return {
                "glyph_id": "mock_glyph_id",
                "qi_signature": hashlib.sha256(b"mock_signature").hexdigest(),
                "consciousness_fingerprint": "mock_consciousness_fingerprint",
                "temporal_validity": (
                    datetime.now(timezone.utc).isoformat()
                ),
                "hidden_payload": None,
            }

    class MockQIResonanceGlyph:
        def generate_auth_glyph(self, user_identity, consciousness_context):
            return MockQIGlyph()

    QIResonanceGlyph = MockQIResonanceGlyph
    ConsciousnessContext = MagicMock()


def sign_event_file(file_path: str, user_identity: str) -> dict | None:
    """
    Signs the content of a file using the QRG system.

    Args:
        file_path: The path to the file to sign.
        user_identity: The symbolic identity of the signer.

    Returns:
        A dictionary representing the signed artifact, or None on failure.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {file_path}", file=sys.stderr)
        return None
    except IOError as e:
        print(f"Error: Could not read input file: {e}", file=sys.stderr)
        return None

    # Initialize the QRG system
    qrg_generator = QIResonanceGlyph()

    # Define a consciousness context for the signing event
    # This reflects a formal, operational context.
    context = ConsciousnessContext(
        emotional_state="focus",
        valence=0.2,
        arousal=0.7,
        current_context="operational_signing",
    )

    # Generate the QRG signature for the file content
    print(f"Generating QRG signature for '{file_path}' as user '{user_identity}'...")
    glyph = qrg_generator.generate_auth_glyph(
        user_identity=f"{user_identity}:{content}", consciousness_context=context
    )

    # Create the signed artifact
    signed_artifact = {
        "signer_identity": user_identity,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "signature_type": "QRG-v1",
        "signature": glyph.to_dict(),
        "original_content": content,
    }

    print("Signature generation complete.")
    return signed_artifact


def main():
    """Main function to parse arguments and run the signing process."""
    parser = argparse.ArgumentParser(
        description="Sign an operational event file with a Quantum Resonance Glyph."
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the input file to be signed (e.g., release_notes.md).",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to write the output JSON signed artifact.",
    )
    parser.add_argument(
        "--user-identity",
        required=True,
        help="The symbolic identity of the signer (e.g., 'ops-release-manager').",
    )

    args = parser.parse_args()

    artifact = sign_event_file(args.input_file, args.user_identity)

    if artifact is None:
        # The error message is already printed by sign_event_file
        sys.exit(1)

    try:
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)
        print(f"Successfully wrote signed artifact to '{args.output_file}'")
    except IOError as e:
        print(
            f"Error: Could not write output file at {args.output_file}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
