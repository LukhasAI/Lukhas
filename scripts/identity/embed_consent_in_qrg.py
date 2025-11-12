"""
Embed Consent Hash in Quantum Resonance Glyph (QRG) Claims

This script generates a consent hash from identity and consent data and embeds
it into the signed payload of a Quantum Resonance Glyph (QRG). It demonstrates
the integration of LUKHAS consent management with the QRG authentication system,
adhering to the LUKHAS lane architecture.

This script is designed to run in an environment where `lukhas` is a top-level
package. It uses mocked implementations of the consent manager and QRG core
for demonstration purposes, as per the task requirements.
"""

import hashlib
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from unittest.mock import MagicMock

# --- Mocked LUKHAS Modules ---
# As per the task instructions, we mock missing modules to adhere to the
# `lukhas.*` import structure. In a real environment, these would be direct
# imports from the LUKHAS platform's packages.

# Mock for lukhas.governance.consent.consent_manager
mock_consent_manager = MagicMock()

@dataclass
class MockConsentRecord:
    """A mock representation of a ConsentRecord for hashing."""
    consent_id: str
    user_id: str
    purpose_id: str
    granted_at: datetime
    method: str
    consent_text: str

mock_consent_manager.ConsentRecord = MockConsentRecord

# Mock for lukhas.products.security.qrg.qrg_core
mock_qrg_core = MagicMock()

@dataclass
class MockQIGlyph:
    """A mock representation of a QIGlyph."""
    glyph_id: str
    hidden_payload: Optional[dict[str, Any]] = None

class MockQIResonanceGlyph:
    """A mock QIResonanceGlyph generator."""
    def generate_auth_glyph(self, user_identity: str, **kwargs) -> MockQIGlyph:
        """Generates a base glyph."""
        glyph_id = hashlib.sha256(f"glyph_{user_identity}".encode()).hexdigest()
        return MockQIGlyph(glyph_id=glyph_id)

    def embed_hidden_data(self, glyph: MockQIGlyph, hidden_payload: dict[str, Any], **kwargs) -> MockQIGlyph:
        """Embeds data into a glyph."""
        glyph.hidden_payload = hidden_payload
        glyph.glyph_id += "_embedded"
        return glyph

mock_qrg_core.QIResonanceGlyph = MockQIResonanceGlyph

# Apply mocks to sys.modules to allow `lukhas.*` imports
sys.modules['lukhas'] = MagicMock()
sys.modules['lukhas.governance'] = MagicMock()
sys.modules['lukhas.governance.consent'] = mock_consent_manager
sys.modules['lukhas.products'] = MagicMock()
sys.modules['lukhas.products.security'] = MagicMock()
sys.modules['lukhas.products.security.qrg'] = mock_qrg_core
# --- End Mocked LUKHAS Modules ---


# These imports will now work because of the mocks above
from lukhas.governance.consent import ConsentRecord
from lukhas.products.security.qrg import QIResonanceGlyph, QIGlyph


def generate_consent_hash(consent_record: ConsentRecord) -> str:
    """
    Generates an integrity hash for a consent record.

    This function mirrors the hashing logic from the AdvancedConsentManager
    to ensure consistency and verifiability.

    Args:
        consent_record: The consent record to hash.

    Returns:
        A SHA-256 hash of the core consent data.
    """
    # Ensure granted_at is in the expected ISO format with timezone info
    if consent_record.granted_at.tzinfo is None:
        granted_at_iso = consent_record.granted_at.isoformat() + "Z"
    else:
        granted_at_iso = consent_record.granted_at.isoformat()

    hash_data = {
        "consent_id": consent_record.consent_id,
        "user_id": consent_record.user_id,
        "purpose_id": consent_record.purpose_id,
        "granted_at": granted_at_iso,
        "method": consent_record.method,
        "consent_text": consent_record.consent_text,
    }

    # Sort keys for a consistent hash
    serialized_data = json.dumps(hash_data, sort_keys=True)

    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def embed_consent_in_qrg(user_identity: str, consent_record: ConsentRecord) -> QIGlyph:
    """
    Generates a QRG and embeds the consent hash into its hidden payload.

    Args:
        user_identity: The user's unique identifier.
        consent_record: The consent record to process.

    Returns:
        A new QIGlyph instance with the consent hash embedded.
    """
    print(f"Embedding consent for user '{user_identity}' into a new QRG...")

    # 1. Initialize the QRG generation engine
    qrg_generator = QIResonanceGlyph()

    # 2. Generate a base authentication glyph for the user
    base_glyph = qrg_generator.generate_auth_glyph(user_identity=user_identity)
    print(f"  - Generated base QRG with ID: {base_glyph.glyph_id}")

    # 3. Generate the consent hash from the provided record
    consent_hash = generate_consent_hash(consent_record)
    print(f"  - Generated consent hash: {consent_hash}")

    # 4. Prepare the hidden payload with the consent hash
    hidden_payload = {
        "iss": "lukhas.identity",
        "aud": "lukhas.qrg_verifier",
        "iat": datetime.now().isoformat(),
        "sub": user_identity,
        "claims": {
            "consent_hash": consent_hash,
            "consent_id": consent_record.consent_id,
            "purpose": consent_record.purpose_id
        }
    }
    print(f"  - Prepared hidden payload for embedding.")

    # 5. Embed the payload into the QRG
    embedded_glyph = qrg_generator.embed_hidden_data(
        glyph=base_glyph,
        hidden_payload=hidden_payload
    )
    print(f"  - Embedded payload into new QRG with ID: {embedded_glyph.glyph_id}")

    return embedded_glyph


if __name__ == "__main__":
    print("--- Running QRG Consent Embedding Demonstration ---")

    # Example Data
    USER_ID = "user_7c5b8e9f"
    CONSENT_ID = f"consent_{uuid.uuid4().hex[:12]}"
    PURPOSE_ID = "service_improvement"

    # 1. Create a sample consent record
    # In a real scenario, this would be retrieved from the ConsentManager
    sample_consent_record = MockConsentRecord(
        consent_id=CONSENT_ID,
        user_id=USER_ID,
        purpose_id=PURPOSE_ID,
        granted_at=datetime.now(),
        method="web_form",
        consent_text=f"I consent to data processing for {PURPOSE_ID}."
    )
    print(f"\n1. Created sample consent record: {sample_consent_record.consent_id}")

    # 2. Run the embedding process
    final_qrg = embed_consent_in_qrg(
        user_identity=USER_ID,
        consent_record=sample_consent_record
    )

    # 3. Verify the result
    print("\n3. Verification:")
    if final_qrg and final_qrg.hidden_payload:
        print("  - SUCCESS: QRG contains a hidden payload.")
        retrieved_hash = final_qrg.hidden_payload.get("claims", {}).get("consent_hash")

        # Re-generate hash to ensure it matches
        expected_hash = generate_consent_hash(sample_consent_record)

        if retrieved_hash == expected_hash:
            print(f"  - SUCCESS: Embedded consent hash matches expected hash.")
            print(f"    - Embedded:   {retrieved_hash}")
            print(f"    - Expected:   {expected_hash}")
        else:
            print(f"  - FAILURE: Embedded hash does not match expected hash.")
            print(f"    - Embedded:   {retrieved_hash}")
            print(f"    - Expected:   {expected_hash}")
    else:
        print("  - FAILURE: QRG does not contain a hidden payload.")

    print("\n--- Demonstration Complete ---")
