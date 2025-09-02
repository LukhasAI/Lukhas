"""Tests for the WebAuthn manager."""

import base64

from lukhas.identity.webauthn import WebAuthnManager

# ΛTAG: webauthn_test


def test_generate_registration_options_records_pending() -> None:
    """Ensure registration options generation stores pending state."""
    manager = WebAuthnManager()

    result = manager.generate_registration_options(
        user_id="user123",
        user_name="Alice",
        user_display_name="Alice A",
        user_tier=3,
    )

    assert result["success"] is True
    reg_id = result["registration_id"]
    assert reg_id in manager.pending_registrations

    stored = manager.pending_registrations[reg_id]
    assert stored["user_id"] == "user123"

    # Challenge should decode to 32 bytes
    challenge_b64 = result["options"]["challenge"]
    decoded = base64.urlsafe_b64decode(challenge_b64 + "==")
    assert len(decoded) == 32

    # Tier 3 requires direct attestation
    assert result["options"]["attestation"] == "direct"

