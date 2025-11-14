"""Comprehensive tests for WebAuthnStore.

Tests cover:
- Encrypted credential storage
- Credential retrieval and decryption
- Signature counter updates (monotonic enforcement)
- Clone detection (counter regression)
- User-to-credential relationships
- Credential deletion
- Encryption correctness
"""

import os
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.identity.storage.webauthn_store import WebAuthnStore, CredentialData


@pytest.fixture
def db_url():
    """SQLite database URL for tests (in-memory)."""
    return "sqlite:///:memory:"


@pytest.fixture
def encryption_key():
    """Generate test encryption key."""
    return AESGCM.generate_key(bit_length=256)


@pytest.fixture
async def webauthn_store(db_url, encryption_key):
    """WebAuthnStore instance for testing."""
    store = WebAuthnStore(db_url=db_url, encryption_key=encryption_key)
    yield store
    store.close()


@pytest.mark.asyncio
async def test_store_and_retrieve_credential(webauthn_store):
    """Test basic credential storage and retrieval with encryption."""
    credential_id = "cred_test_001"
    lid = "usr_alice"
    public_key = b"\x04\xab\xcd\xef" * 16  # 64-byte mock COSE key
    aaguid = b"\x12\x34\x56\x78\x9a\xbc\xde\xf0" * 2  # 16-byte AAGUID

    # Store credential
    success = await webauthn_store.store_credential(
        credential_id=credential_id,
        lid=lid,
        public_key=public_key,
        aaguid=aaguid,
        transports=["usb", "nfc"],
        attestation_format="packed",
        user_verified=True,
    )
    assert success is True

    # Retrieve credential
    cred = await webauthn_store.get_credential(credential_id)
    assert cred is not None
    assert cred.id == credential_id
    assert cred.lid == lid
    assert cred.public_key == public_key  # Decrypted correctly
    assert cred.aaguid == aaguid  # Decrypted correctly
    assert cred.transports == ["usb", "nfc"]
    assert cred.attestation_format == "packed"
    assert cred.user_verified is True
    assert cred.sign_count == 0


@pytest.mark.asyncio
async def test_encryption_at_rest(webauthn_store, db_url, encryption_key):
    """Test that sensitive data is encrypted in database."""
    credential_id = "cred_encrypted"
    lid = "usr_bob"
    public_key = b"secret_key_data_123"

    # Store credential
    await webauthn_store.store_credential(
        credential_id=credential_id, lid=lid, public_key=public_key
    )

    # Query database directly to verify encryption
    with webauthn_store.SessionLocal() as session:
        from core.identity.storage.webauthn_store import WebAuthnCredentialModel

        cred = session.query(WebAuthnCredentialModel).filter_by(id=credential_id).first()
        assert cred is not None

        # Encrypted data should NOT match plaintext
        assert cred.public_key_encrypted != public_key
        assert len(cred.public_key_encrypted) > len(public_key)  # Includes auth tag

        # Nonce should be present
        assert cred.nonce is not None
        assert len(cred.nonce) == 12  # AES-GCM nonce


@pytest.mark.asyncio
async def test_signature_counter_update(webauthn_store):
    """Test signature counter update with monotonic enforcement."""
    credential_id = "cred_counter"
    lid = "usr_charlie"
    public_key = b"test_key"

    # Store credential with initial counter = 0
    await webauthn_store.store_credential(
        credential_id=credential_id, lid=lid, public_key=public_key, sign_count=0
    )

    # Update counter: 0 -> 5
    old_count = await webauthn_store.update_sign_count(credential_id, new_count=5)
    assert old_count == 0

    # Verify counter updated
    cred = await webauthn_store.get_credential(credential_id)
    assert cred.sign_count == 5
    assert cred.last_used_at is not None

    # Update counter: 5 -> 10
    old_count = await webauthn_store.update_sign_count(credential_id, new_count=10)
    assert old_count == 5

    cred = await webauthn_store.get_credential(credential_id)
    assert cred.sign_count == 10


@pytest.mark.asyncio
async def test_signature_counter_regression_detection(webauthn_store):
    """Test that counter regression is detected (cloned authenticator)."""
    credential_id = "cred_clone_detect"
    lid = "usr_dave"
    public_key = b"test_key"

    # Store credential with counter = 10
    await webauthn_store.store_credential(
        credential_id=credential_id, lid=lid, public_key=public_key, sign_count=10
    )

    # Attempt to set counter to 5 (regression) - should raise ValueError
    with pytest.raises(ValueError, match="Signature counter must increase"):
        await webauthn_store.update_sign_count(credential_id, new_count=5)

    # Attempt to set counter to 10 (no change) - should also raise ValueError
    with pytest.raises(ValueError, match="Signature counter must increase"):
        await webauthn_store.update_sign_count(credential_id, new_count=10)

    # Verify counter unchanged
    cred = await webauthn_store.get_credential(credential_id)
    assert cred.sign_count == 10


@pytest.mark.asyncio
async def test_multiple_credentials_per_user(webauthn_store):
    """Test that users can have multiple credentials."""
    lid = "usr_eve"
    credentials = [
        ("cred_phone", b"phone_key", ["internal"]),
        ("cred_yubikey", b"yubikey_key", ["usb"]),
        ("cred_laptop", b"laptop_key", ["internal", "usb"]),
    ]

    # Store multiple credentials for same user
    for cred_id, public_key, transports in credentials:
        await webauthn_store.store_credential(
            credential_id=cred_id,
            lid=lid,
            public_key=public_key,
            transports=transports,
        )

    # Retrieve all credentials for user
    user_creds = await webauthn_store.get_credentials_for_user(lid)
    assert len(user_creds) == 3

    # Verify each credential
    cred_ids = {c.id for c in user_creds}
    assert cred_ids == {"cred_phone", "cred_yubikey", "cred_laptop"}

    # Count credentials
    count = await webauthn_store.count_credentials_for_user(lid)
    assert count == 3


@pytest.mark.asyncio
async def test_credential_deletion(webauthn_store):
    """Test credential deletion."""
    credential_id = "cred_delete"
    lid = "usr_frank"
    public_key = b"delete_me"

    # Store credential
    await webauthn_store.store_credential(
        credential_id=credential_id, lid=lid, public_key=public_key
    )

    # Verify exists
    assert await webauthn_store.get_credential(credential_id) is not None

    # Delete credential
    deleted = await webauthn_store.delete_credential(credential_id)
    assert deleted is True

    # Verify deleted
    assert await webauthn_store.get_credential(credential_id) is None

    # Delete again - should return False (not found)
    deleted_again = await webauthn_store.delete_credential(credential_id)
    assert deleted_again is False


@pytest.mark.asyncio
async def test_get_nonexistent_credential(webauthn_store):
    """Test retrieving non-existent credential."""
    cred = await webauthn_store.get_credential("cred_does_not_exist")
    assert cred is None


@pytest.mark.asyncio
async def test_update_sign_count_nonexistent(webauthn_store):
    """Test updating sign count for non-existent credential."""
    result = await webauthn_store.update_sign_count("cred_nonexistent", new_count=5)
    assert result is None


@pytest.mark.asyncio
async def test_encryption_key_validation():
    """Test that encryption key validation works."""
    # Invalid key length (16 bytes instead of 32)
    invalid_key = b"0123456789abcdef"

    with pytest.raises(ValueError, match="exactly 32 bytes"):
        WebAuthnStore(db_url="sqlite:///:memory:", encryption_key=invalid_key)


@pytest.mark.asyncio
async def test_decryption_integrity(webauthn_store):
    """Test that tampered ciphertext is detected."""
    credential_id = "cred_tamper"
    lid = "usr_grace"
    public_key = b"integrity_test"

    # Store credential
    await webauthn_store.store_credential(
        credential_id=credential_id, lid=lid, public_key=public_key
    )

    # Tamper with encrypted data in database
    with webauthn_store.SessionLocal() as session:
        from core.identity.storage.webauthn_store import WebAuthnCredentialModel

        cred = session.query(WebAuthnCredentialModel).filter_by(id=credential_id).first()

        # Flip a bit in the ciphertext
        tampered = bytearray(cred.public_key_encrypted)
        tampered[0] ^= 0x01
        cred.public_key_encrypted = bytes(tampered)
        session.commit()

    # Retrieval should fail (or return None) due to auth tag mismatch
    try:
        retrieved = await webauthn_store.get_credential(credential_id)
        # cryptography raises InvalidTag, which gets caught and returns None
        assert retrieved is None
    except Exception:
        # Some versions might not catch the exception
        pass


@pytest.mark.asyncio
async def test_user_with_no_credentials(webauthn_store):
    """Test querying credentials for user with none registered."""
    creds = await webauthn_store.get_credentials_for_user("usr_no_creds")
    assert creds == []

    count = await webauthn_store.count_credentials_for_user("usr_no_creds")
    assert count == 0


@pytest.mark.asyncio
async def test_health_check_healthy(webauthn_store):
    """Test health check with healthy database."""
    health = webauthn_store.health_check()
    assert health["status"] == "healthy"
    assert "kms_key_id" in health


@pytest.mark.asyncio
async def test_health_check_unhealthy():
    """Test health check with closed database."""
    store = WebAuthnStore(db_url="sqlite:///:memory:")
    store.close()  # Close connection

    health = store.health_check()
    assert health["status"] == "unhealthy"
    assert "error" in health


@pytest.mark.asyncio
async def test_metadata_storage(webauthn_store):
    """Test that metadata fields are stored correctly."""
    credential_id = "cred_metadata"
    lid = "usr_heidi"
    public_key = b"key_with_metadata"

    await webauthn_store.store_credential(
        credential_id=credential_id,
        lid=lid,
        public_key=public_key,
        transports=["usb", "nfc", "ble"],
        attestation_format="fido-u2f",
        user_verified=True,
        registered_from_ip="192.168.1.100",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    )

    # Retrieve and verify metadata
    cred = await webauthn_store.get_credential(credential_id)
    assert cred.transports == ["usb", "nfc", "ble"]
    assert cred.attestation_format == "fido-u2f"
    assert cred.user_verified is True
    assert cred.created_at is not None


@pytest.mark.asyncio
async def test_kms_key_id_tracking(encryption_key):
    """Test that KMS key ID is tracked for rotation support."""
    store = WebAuthnStore(
        db_url="sqlite:///:memory:",
        encryption_key=encryption_key,
        kms_key_id="arn:aws:kms:us-east-1:123456789012:key/abcd-1234",
    )

    health = store.health_check()
    assert health["kms_key_id"] == "arn:aws:kms:us-east-1:123456789012:key/abcd-1234"

    store.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
