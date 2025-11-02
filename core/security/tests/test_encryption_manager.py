from __future__ import annotations

import os

import pytest

from core.security.encryption_manager import (
    DecryptionResult,
    EncryptionError,
    EncryptionManager,
    EncryptedPayload,
)
from core.security.encryption_types import EncryptionAlgorithm, get_algorithm_metadata


@pytest.fixture()
def manager() -> EncryptionManager:
    os.environ.pop("LUKHAS_KEYSTORE", None)  # ensure no external influence
    return EncryptionManager()


def test_generate_key_tracks_versions(manager: EncryptionManager) -> None:
    first_id = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    second_id = manager.rotate_key(EncryptionAlgorithm.AES_256_GCM)

    assert first_id != second_id
    assert first_id.endswith("-v1")
    assert second_id.endswith("-v2")


def test_encrypt_decrypt_round_trip_aes(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.AES_256_GCM)

    payload = manager.encrypt("classified", EncryptionAlgorithm.AES_256_GCM)
    result = manager.decrypt(payload, EncryptionAlgorithm.AES_256_GCM)

    assert isinstance(result, DecryptionResult)
    assert result.plaintext == b"classified"
    assert result.authenticated is True


def test_encrypt_decrypt_round_trip_chacha(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)

    payload = manager.encrypt(b"data", EncryptionAlgorithm.CHACHA20_POLY1305)
    result = manager.decrypt(payload, EncryptionAlgorithm.CHACHA20_POLY1305)

    assert result.plaintext == b"data"
    assert result.version == 1


def test_encrypt_requires_existing_key(manager: EncryptionManager) -> None:
    with pytest.raises(EncryptionError):
        manager.encrypt(b"data", EncryptionAlgorithm.AES_256_GCM)


def test_decrypt_rejects_unknown_key(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    payload = manager.encrypt(b"payload", EncryptionAlgorithm.AES_256_GCM)
    tampered = EncryptedPayload(
        algorithm=payload.algorithm,
        key_id="nonexistent",
        version=payload.version,
        nonce=payload.nonce,
        ciphertext=payload.ciphertext,
        tag=payload.tag,
    )

    with pytest.raises(EncryptionError):
        manager.decrypt(tampered, payload.algorithm)


def test_decrypt_rejects_version_mismatch(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    payload = manager.encrypt(b"payload", EncryptionAlgorithm.AES_256_GCM)
    tampered = EncryptedPayload(
        algorithm=payload.algorithm,
        key_id=payload.key_id,
        version=payload.version + 1,
        nonce=payload.nonce,
        ciphertext=payload.ciphertext,
        tag=payload.tag,
    )

    with pytest.raises(EncryptionError):
        manager.decrypt(tampered, payload.algorithm)


def test_decrypt_detects_modified_ciphertext(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)
    payload = manager.encrypt(b"payload", EncryptionAlgorithm.CHACHA20_POLY1305)

    corrupted = EncryptedPayload(
        algorithm=payload.algorithm,
        key_id=payload.key_id,
        version=payload.version,
        nonce=payload.nonce,
        ciphertext=payload.ciphertext[:-1] + bytes([payload.ciphertext[-1] ^ 0xFF]),
        tag=payload.tag,
    )

    with pytest.raises(EncryptionError):
        manager.decrypt(corrupted, payload.algorithm)


def test_decrypt_rejects_algorithm_mismatch(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    payload = manager.encrypt(b"payload", EncryptionAlgorithm.AES_256_GCM)

    with pytest.raises(EncryptionError):
        manager.decrypt(payload, EncryptionAlgorithm.CHACHA20_POLY1305)


def test_rotation_keeps_old_keys_valid(manager: EncryptionManager) -> None:
    manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    payload = manager.encrypt(b"payload", EncryptionAlgorithm.AES_256_GCM)

    # Rotate to a new version and ensure the existing payload can still be decrypted.
    manager.rotate_key(EncryptionAlgorithm.AES_256_GCM)

    result = manager.decrypt(payload, EncryptionAlgorithm.AES_256_GCM)
    assert result.plaintext == b"payload"
    assert result.version == 1


def test_rejects_non_aead_algorithm(manager: EncryptionManager) -> None:
    metadata = get_algorithm_metadata(EncryptionAlgorithm.AES_256_CBC)
    assert metadata.is_aead is False

    with pytest.raises(ValueError):
        manager.generate_key(EncryptionAlgorithm.AES_256_CBC)
