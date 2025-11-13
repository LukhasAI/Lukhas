"""
Unit tests for QRG operational event signing.

Tests cover:
- Release notes signing and verification
- Policy change signing and verification
- Signature tampering detection
- Key management error handling
- Edge cases and validation
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from core.qrg.signing import (
    canonical_payload_hash,
    generate_private_key,
    private_key_to_pem,
    qrg_sign,
    qrg_verify,
)
from scripts.qrg.sign_ops_event import (
    sign_policy_change,
    sign_release_notes,
    verify_signature,
)


@pytest.fixture
def temp_key_file():
    """Generate temporary private key file for testing."""
    priv_key = generate_private_key()
    priv_pem = private_key_to_pem(priv_key)

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pem") as f:
        f.write(priv_pem)
        key_path = f.name

    yield key_path

    # Cleanup
    try:
        os.unlink(key_path)
    except Exception:
        pass


@pytest.fixture
def sample_release_payload():
    """Sample release notes payload for testing."""
    return {
        "version": "1.0.0",
        "notes": "Security fixes for Guardian system",
        "date": "2025-11-12",
        "author": "LUKHAS AI Team",
    }


@pytest.fixture
def sample_policy_payload():
    """Sample policy change payload for testing."""
    return {
        "policy_id": "guardian_drift_threshold",
        "old_value": "0.15",
        "new_value": "0.20",
        "reason": "Reduce false positive drift detections",
        "approved_by": "governance_committee",
    }


# =============================================================================
# RELEASE NOTES SIGNING TESTS
# =============================================================================


def test_sign_release_notes_basic(temp_key_file):
    """Test basic release notes signing."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Verify structure
    assert "payload" in result
    assert "qrg_signature" in result

    # Verify payload fields
    payload = result["payload"]
    assert payload["type"] == "release_notes"
    assert payload["version"] == "1.0.0"
    assert payload["notes"] == "Security fixes"
    assert payload["author"] == "LUKHAS AI Team"
    assert "date" in payload

    # Verify signature fields
    sig = result["qrg_signature"]
    assert sig["algo"] == "ecdsa-sha256"
    assert "pubkey_pem" in sig
    assert "sig_b64" in sig
    assert "ts" in sig
    assert "payload_hash" in sig


def test_sign_release_notes_custom_author(temp_key_file):
    """Test release notes signing with custom author."""
    result = sign_release_notes(
        version="2.0.0",
        notes="Major update",
        key_path=temp_key_file,
        author="Custom Team",
    )

    assert result["payload"]["author"] == "Custom Team"


def test_sign_release_notes_with_consent(temp_key_file):
    """Test release notes signing with consent hash."""
    consent_hash = "abc123def456"

    result = sign_release_notes(
        version="1.0.0",
        notes="Release notes",
        key_path=temp_key_file,
        consent_hash=consent_hash,
    )

    assert result["qrg_signature"]["consent_hash"] == consent_hash


def test_sign_release_notes_empty_version(temp_key_file):
    """Test that empty version raises error."""
    with pytest.raises(ValueError, match="Version cannot be empty"):
        sign_release_notes(
            version="",
            notes="Release notes",
            key_path=temp_key_file,
        )


def test_sign_release_notes_empty_notes(temp_key_file):
    """Test that empty notes raise error."""
    with pytest.raises(ValueError, match="Release notes cannot be empty"):
        sign_release_notes(
            version="1.0.0",
            notes="",
            key_path=temp_key_file,
        )


def test_sign_release_notes_missing_key():
    """Test that missing key file raises error."""
    with pytest.raises(FileNotFoundError, match="Private key file not found"):
        sign_release_notes(
            version="1.0.0",
            notes="Release notes",
            key_path="/nonexistent/key.pem",
        )


# =============================================================================
# POLICY CHANGE SIGNING TESTS
# =============================================================================


def test_sign_policy_change_basic(temp_key_file):
    """Test basic policy change signing."""
    result = sign_policy_change(
        policy_id="drift_threshold",
        change_desc="Increased threshold",
        key_path=temp_key_file,
    )

    # Verify structure
    assert "payload" in result
    assert "qrg_signature" in result

    # Verify payload fields
    payload = result["payload"]
    assert payload["type"] == "policy_change"
    assert payload["policy_id"] == "drift_threshold"
    assert payload["change_desc"] == "Increased threshold"
    assert "timestamp" in payload

    # Verify signature
    sig = result["qrg_signature"]
    assert sig["algo"] == "ecdsa-sha256"


def test_sign_policy_change_with_values(temp_key_file):
    """Test policy change signing with old/new values."""
    result = sign_policy_change(
        policy_id="drift_threshold",
        change_desc="Increased threshold",
        key_path=temp_key_file,
        old_value="0.15",
        new_value="0.20",
    )

    payload = result["payload"]
    assert payload["old_value"] == "0.15"
    assert payload["new_value"] == "0.20"


def test_sign_policy_change_with_approval(temp_key_file):
    """Test policy change signing with approval metadata."""
    result = sign_policy_change(
        policy_id="drift_threshold",
        change_desc="Increased threshold",
        key_path=temp_key_file,
        approved_by="governance_committee",
        reason="Reduce false positives",
    )

    payload = result["payload"]
    assert payload["approved_by"] == "governance_committee"
    assert payload["reason"] == "Reduce false positives"


def test_sign_policy_change_empty_policy_id(temp_key_file):
    """Test that empty policy ID raises error."""
    with pytest.raises(ValueError, match="Policy ID cannot be empty"):
        sign_policy_change(
            policy_id="",
            change_desc="Change description",
            key_path=temp_key_file,
        )


def test_sign_policy_change_empty_description(temp_key_file):
    """Test that empty change description raises error."""
    with pytest.raises(ValueError, match="Change description cannot be empty"):
        sign_policy_change(
            policy_id="drift_threshold",
            change_desc="",
            key_path=temp_key_file,
        )


# =============================================================================
# SIGNATURE VERIFICATION TESTS
# =============================================================================


def test_verify_valid_release_signature(temp_key_file):
    """Test verification of valid release notes signature."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Verify signature
    assert verify_signature(result) is True


def test_verify_valid_policy_signature(temp_key_file):
    """Test verification of valid policy change signature."""
    result = sign_policy_change(
        policy_id="drift_threshold",
        change_desc="Increased threshold",
        key_path=temp_key_file,
    )

    # Verify signature
    assert verify_signature(result) is True


def test_verify_tampered_payload(temp_key_file):
    """Test that tampered payload fails verification."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Original notes",
        key_path=temp_key_file,
    )

    # Tamper with payload
    result["payload"]["notes"] = "Tampered notes"

    # Verification should fail
    assert verify_signature(result) is False


def test_verify_tampered_version(temp_key_file):
    """Test that tampered version fails verification."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Tamper with version
    result["payload"]["version"] = "2.0.0"

    # Verification should fail
    assert verify_signature(result) is False


def test_verify_tampered_signature(temp_key_file):
    """Test that tampered signature bytes fail verification."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Tamper with signature
    original_sig = result["qrg_signature"]["sig_b64"]
    result["qrg_signature"]["sig_b64"] = original_sig[:-5] + "XXXXX"

    # Verification should fail
    assert verify_signature(result) is False


def test_verify_missing_payload_field():
    """Test that missing payload field raises error."""
    with pytest.raises(ValueError, match="Missing 'payload' field"):
        verify_signature({"qrg_signature": {}})


def test_verify_missing_signature_field():
    """Test that missing signature field raises error."""
    with pytest.raises(ValueError, match="Missing 'qrg_signature' field"):
        verify_signature({"payload": {}})


# =============================================================================
# PAYLOAD HASH CONSISTENCY TESTS
# =============================================================================


def test_payload_hash_deterministic():
    """Test that payload hashing is deterministic."""
    payload = {
        "version": "1.0.0",
        "notes": "Release notes",
        "date": "2025-11-12",
    }

    hash1 = canonical_payload_hash(payload)
    hash2 = canonical_payload_hash(payload)

    assert hash1 == hash2


def test_payload_hash_key_order_independence():
    """Test that key order doesn't affect hash."""
    payload1 = {
        "version": "1.0.0",
        "notes": "Release notes",
        "date": "2025-11-12",
    }

    payload2 = {
        "date": "2025-11-12",
        "version": "1.0.0",
        "notes": "Release notes",
    }

    hash1 = canonical_payload_hash(payload1)
    hash2 = canonical_payload_hash(payload2)

    assert hash1 == hash2


def test_payload_hash_sensitivity():
    """Test that payload hash is sensitive to changes."""
    payload1 = {"version": "1.0.0"}
    payload2 = {"version": "1.0.1"}

    hash1 = canonical_payload_hash(payload1)
    hash2 = canonical_payload_hash(payload2)

    assert hash1 != hash2


# =============================================================================
# SIGNATURE ROUND-TRIP TESTS
# =============================================================================


def test_sign_and_verify_roundtrip(temp_key_file):
    """Test complete sign and verify workflow."""
    # Sign release notes
    signed_release = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Verify signature
    assert verify_signature(signed_release) is True

    # Sign policy change
    signed_policy = sign_policy_change(
        policy_id="drift_threshold",
        change_desc="Increased threshold",
        key_path=temp_key_file,
        old_value="0.15",
        new_value="0.20",
    )

    # Verify signature
    assert verify_signature(signed_policy) is True


def test_multiple_signatures_same_key(temp_key_file):
    """Test that multiple signatures with same key are all valid."""
    signatures = []

    for i in range(5):
        sig = sign_release_notes(
            version=f"1.0.{i}",
            notes=f"Release {i}",
            key_path=temp_key_file,
        )
        signatures.append(sig)

    # All signatures should verify
    for sig in signatures:
        assert verify_signature(sig) is True


# =============================================================================
# TIMESTAMP TESTS
# =============================================================================


def test_signature_timestamp_format(temp_key_file):
    """Test that signature timestamp is ISO 8601 with Z timezone."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    ts = result["qrg_signature"]["ts"]

    # Verify timestamp format
    assert ts.endswith("Z")
    # Should be parseable as ISO 8601
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)


def test_signature_timestamp_recent(temp_key_file):
    """Test that signature timestamp is recent."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    ts = result["qrg_signature"]["ts"]
    sig_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    now = datetime.now(tz=sig_time.tzinfo)

    # Timestamp should be within last minute
    age_seconds = (now - sig_time).total_seconds()
    assert age_seconds < 60


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


def test_save_and_load_signature(temp_key_file):
    """Test saving signature to file and loading it back."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(result, f, indent=2)
        sig_path = f.name

    try:
        # Load from file
        with open(sig_path) as f:
            loaded = json.load(f)

        # Verify loaded signature
        assert verify_signature(loaded) is True
    finally:
        os.unlink(sig_path)


def test_signature_json_serializable(temp_key_file):
    """Test that signature result is JSON-serializable."""
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Should serialize without errors
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Should deserialize back
    loaded = json.loads(json_str)
    assert verify_signature(loaded) is True


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_sign_with_invalid_key_file():
    """Test that invalid key file raises error."""
    # Create temporary file with invalid key data
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem") as f:
        f.write("INVALID KEY DATA")
        key_path = f.name

    try:
        with pytest.raises(ValueError, match="Failed to read private key"):
            sign_release_notes(
                version="1.0.0",
                notes="Security fixes",
                key_path=key_path,
            )
    finally:
        os.unlink(key_path)


def test_verify_with_wrong_key(temp_key_file):
    """Test that signature from different key fails verification."""
    # Generate first signature
    result = sign_release_notes(
        version="1.0.0",
        notes="Security fixes",
        key_path=temp_key_file,
    )

    # Generate different key
    other_key = generate_private_key()
    other_pem = private_key_to_pem(other_key)

    # Create temporary file for other key
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pem") as f:
        f.write(other_pem)
        other_key_path = f.name

    try:
        # Sign with different key
        other_result = sign_release_notes(
            version="1.0.0",
            notes="Security fixes",
            key_path=other_key_path,
        )

        # Replace payload from first signature with signature from second key
        result["qrg_signature"] = other_result["qrg_signature"]

        # Verification should fail (different key)
        assert verify_signature(result) is False
    finally:
        os.unlink(other_key_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
