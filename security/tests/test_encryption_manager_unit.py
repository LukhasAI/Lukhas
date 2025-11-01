"""Unit tests for the lightweight :mod:`security.encryption_manager` module."""

from __future__ import annotations

import os
import tempfile

import pytest

from security.encryption_manager import (
    EncryptionAlgorithm,
    EncryptionManager,
    KeyType,
    KeyUsage,
    create_encryption_manager,
)


class TestEncryptionManager:
    """Exercise the behaviour required by the security test suite."""

    def setup_method(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["LUKHAS_KEYSTORE"] = self.temp_dir.name
        self.manager = create_encryption_manager()

    def teardown_method(self) -> None:
        self.temp_dir.cleanup()
        os.environ.pop("LUKHAS_KEYSTORE", None)

    def test_generate_key_registers_metadata(self) -> None:
        key_id = self.manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

        assert key_id.startswith(KeyType.AES_256.value)
        metadata = self.manager.keys[key_id]
        assert metadata.is_active
        assert metadata.algorithm is EncryptionAlgorithm.AES_256_GCM

    def test_encrypt_decrypt_round_trip_aes(self) -> None:
        key_id = self.manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)
        plaintext = "secret message"

        encrypted = self.manager.encrypt(plaintext, key_id)
        assert encrypted.algorithm is EncryptionAlgorithm.AES_256_GCM

        decrypted = self.manager.decrypt(encrypted)
        assert decrypted.decrypted_data.decode("utf-8") == plaintext
        assert decrypted.verified

    def test_encrypt_decrypt_round_trip_rsa(self) -> None:
        key_id = self.manager.generate_key(KeyType.RSA_2048, KeyUsage.ENCRYPTION)
        plaintext = "rsa secret"

        encrypted = self.manager.encrypt(plaintext, key_id)
        assert encrypted.algorithm is EncryptionAlgorithm.RSA_OAEP

        decrypted = self.manager.decrypt(encrypted)
        assert decrypted.decrypted_data.decode("utf-8") == plaintext

    def test_rotate_key_marks_old_key_inactive(self) -> None:
        key_id = self.manager.generate_key(KeyType.AES_256, KeyUsage.DATA_ENCRYPTION)

        new_key_id = self.manager.rotate_key(key_id)

        assert not self.manager.keys[key_id].is_active
        assert self.manager.keys[new_key_id].is_active
        assert new_key_id.startswith(KeyType.AES_256.value)

    def test_password_hash_round_trip(self) -> None:
        password = "Sup3rSecret!"
        hashed = self.manager.hash_password(password)

        assert hashed.startswith("pbkdf2$")
        assert self.manager.verify_password(password, hashed)
        assert not self.manager.verify_password("wrong", hashed)


@pytest.mark.parametrize(
    "key_type,expected_algorithm",
    [
        (KeyType.AES_256, EncryptionAlgorithm.AES_256_GCM),
        (KeyType.RSA_2048, EncryptionAlgorithm.RSA_OAEP),
    ],
)
def test_default_algorithm_selection(key_type: KeyType, expected_algorithm: EncryptionAlgorithm) -> None:
    manager = EncryptionManager()
    key_id = manager.generate_key(key_type, KeyUsage.DATA_ENCRYPTION)
    assert manager.keys[key_id].algorithm is expected_algorithm

