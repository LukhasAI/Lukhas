"""Unit tests covering the lightweight encryption manager implementation."""

import pytest

from security.encryption_manager import (
    EncryptionError,
    EncryptionManager,
    KeyType,
    KeyUsage,
    create_encryption_manager,
)


@pytest.fixture()
def manager() -> EncryptionManager:
    return create_encryption_manager()


def test_generate_key_creates_active_key(manager: EncryptionManager) -> None:
    key_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

    assert key_id.startswith(KeyType.AES_256.value)
    assert key_id in manager.keys
    assert manager.keys[key_id].is_active


def test_encrypt_decrypt_roundtrip(manager: EncryptionManager) -> None:
    key_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)
    payload = "Sensitive test data"

    encrypted = manager.encrypt(payload, key_id)
    assert encrypted.encrypted_data

    decrypted = manager.decrypt(encrypted)
    assert decrypted.verified is True
    assert decrypted.decrypted_data.decode("utf-8") == payload


def test_rotate_key_marks_old_key_inactive(manager: EncryptionManager) -> None:
    original_key = manager.generate_key(KeyType.RSA_2048, KeyUsage.ENCRYPTION)

    new_key = manager.rotate_key(original_key)
    assert new_key != original_key
    assert manager.keys[new_key].is_active
    assert manager.keys[original_key].is_active is False


def test_verify_password_handles_invalid_key_state(manager: EncryptionManager) -> None:
    hashed = manager.hash_password("P@ssw0rd")
    assert manager.verify_password("P@ssw0rd", hashed) is True
    assert manager.verify_password("incorrect", hashed) is False


def test_encrypt_with_inactive_key_raises(manager: EncryptionManager) -> None:
    key_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)
    manager.keys[key_id].is_active = False

    with pytest.raises(EncryptionError):
        manager.encrypt("data", key_id)
