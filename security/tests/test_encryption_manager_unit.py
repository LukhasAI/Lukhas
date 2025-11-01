"""Unit tests for the lightweight encryption manager factory."""

from __future__ import annotations

import os
import tempfile

import pytest

from security.encryption_manager import (
    EncryptionManager,
    EncryptionResult,
    KeyType,
    KeyUsage,
    create_encryption_manager,
)


@pytest.fixture
def keystore_dir():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["LUKHAS_KEYSTORE"] = tmp
        yield tmp
        os.environ.pop("LUKHAS_KEYSTORE", None)


def test_factory_returns_manager(keystore_dir):
    manager = create_encryption_manager()
    assert isinstance(manager, EncryptionManager)
    assert manager.key_store_path.exists()


def test_generate_and_store_keys(keystore_dir):
    manager = create_encryption_manager()
    key_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

    assert key_id.startswith(KeyType.AES_256.value)
    assert key_id in manager.keys
    assert manager.keys[key_id].is_active


def test_encrypt_and_decrypt_round_trip(keystore_dir):
    manager = create_encryption_manager()
    key_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

    message = "Encryption manager test payload"
    result = manager.encrypt(message, key_id)
    assert isinstance(result, EncryptionResult)
    assert result.encrypted_data

    decrypted = manager.decrypt(result)
    assert decrypted.decrypted_data.decode("utf-8") == message


def test_password_hash_and_verify(keystore_dir):
    manager = create_encryption_manager()

    password = "CorrectHorseBatteryStaple!"
    hashed = manager.hash_password(password)

    assert hashed != password
    assert manager.verify_password(password, hashed)
    assert not manager.verify_password("wrong", hashed)


def test_rotate_key_marks_old_inactive(keystore_dir):
    manager = create_encryption_manager()
    original_id = manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

    new_id = manager.rotate_key(original_id)

    assert original_id != new_id
    assert not manager.keys[original_id].is_active
    assert new_id in manager.keys

