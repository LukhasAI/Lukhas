"""Core security encryption manager implementation.

This module provides a lightweight key management facility that supports
authenticated encryption using approved algorithms.  It is intentionally
opinionated: only AEAD algorithms defined in :mod:`core.security.encryption_types`
are permitted.  The manager keeps track of key versions, allowing secure key
rotation without losing the ability to decrypt previously produced ciphertexts.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from .encryption_types import (
    EncryptionAlgorithm,
    get_algorithm_metadata,
    validate_algorithm_choice,
)


class EncryptionError(RuntimeError):
    """Raised for errors during encryption or decryption operations."""


@dataclass(frozen=True)
class KeyRecord:
    """Metadata describing a managed encryption key."""

    key_id: str
    algorithm: EncryptionAlgorithm
    version: int
    material: bytes
    created_at: datetime
    active: bool


@dataclass(frozen=True)
class EncryptedPayload:
    """Container for encrypted data produced by :class:`EncryptionManager`."""

    algorithm: EncryptionAlgorithm
    key_id: str
    version: int
    nonce: bytes
    ciphertext: bytes
    tag: bytes


@dataclass(frozen=True)
class DecryptionResult:
    """Result returned by :meth:`EncryptionManager.decrypt`."""

    plaintext: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    version: int
    authenticated: bool


class EncryptionManager:
    """Manage authenticated encryption keys and operations."""

    def __init__(self) -> None:
        self._keys: Dict[str, KeyRecord] = {}
        self._latest_key: Dict[EncryptionAlgorithm, str] = {}
        self._versions: Dict[EncryptionAlgorithm, int] = {}

    # ------------------------------------------------------------------
    # Key lifecycle operations
    # ------------------------------------------------------------------
    def generate_key(self, algorithm: EncryptionAlgorithm | str) -> str:
        """Generate a new key for ``algorithm`` and return its identifier."""

        normalized = validate_algorithm_choice(algorithm, require_aead=True)
        metadata = get_algorithm_metadata(normalized)
        version = self._versions.get(normalized, 0) + 1
        key_id = f"{normalized.value}-v{version}"

        key_material = os.urandom(metadata.key_size)
        created_at = datetime.now(timezone.utc)

        if normalized in self._latest_key:
            # Mark the previous key as inactive but keep it for decryption.
            previous_id = self._latest_key[normalized]
            previous_record = self._keys[previous_id]
            self._keys[previous_id] = KeyRecord(
                key_id=previous_record.key_id,
                algorithm=previous_record.algorithm,
                version=previous_record.version,
                material=previous_record.material,
                created_at=previous_record.created_at,
                active=False,
            )

        record = KeyRecord(
            key_id=key_id,
            algorithm=normalized,
            version=version,
            material=key_material,
            created_at=created_at,
            active=True,
        )
        self._keys[key_id] = record
        self._latest_key[normalized] = key_id
        self._versions[normalized] = version
        return key_id

    def rotate_key(self, algorithm: EncryptionAlgorithm | str) -> str:
        """Rotate the active key for ``algorithm`` and return the new key id."""

        return self.generate_key(algorithm)

    # ------------------------------------------------------------------
    # Encryption / Decryption
    # ------------------------------------------------------------------
    def encrypt(
        self,
        data: bytes | str,
        algorithm: EncryptionAlgorithm | str,
        *,
        associated_data: Optional[bytes] = None,
    ) -> EncryptedPayload:
        """Encrypt ``data`` using the active key for ``algorithm``."""

        normalized = validate_algorithm_choice(algorithm, require_aead=True)
        key_id = self._latest_key.get(normalized)
        if key_id is None:
            raise EncryptionError(
                f"No key material available for algorithm {normalized.value}."
            )

        record = self._keys[key_id]
        metadata = get_algorithm_metadata(normalized)
        nonce = os.urandom(metadata.nonce_size)

        payload = data.encode("utf-8") if isinstance(data, str) else data
        cipher = self._cipher_for(record.material, normalized)
        ciphertext_with_tag = cipher.encrypt(nonce, payload, associated_data)
        ciphertext = ciphertext_with_tag[:-metadata.tag_size]
        tag = ciphertext_with_tag[-metadata.tag_size :]

        return EncryptedPayload(
            algorithm=normalized,
            key_id=record.key_id,
            version=record.version,
            nonce=nonce,
            ciphertext=ciphertext,
            tag=tag,
        )

    def decrypt(
        self,
        payload: EncryptedPayload,
        algorithm: EncryptionAlgorithm | str,
        *,
        associated_data: Optional[bytes] = None,
    ) -> DecryptionResult:
        """Decrypt ``payload`` verifying the authentication tag."""

        normalized = validate_algorithm_choice(algorithm, require_aead=True)
        if payload.algorithm != normalized:
            raise EncryptionError(
                "Payload algorithm does not match the requested algorithm."
            )

        record = self._keys.get(payload.key_id)
        if record is None:
            raise EncryptionError("Unknown key identifier referenced by payload.")

        if record.version != payload.version:
            # Guard against tampered payload metadata.
            raise EncryptionError("Payload key version does not match record.")

        cipher = self._cipher_for(record.material, normalized)
        combined = payload.ciphertext + payload.tag

        try:
            plaintext = cipher.decrypt(payload.nonce, combined, associated_data)
        except InvalidTag as exc:  # pragma: no cover - cryptography specific
            raise EncryptionError("Ciphertext failed authentication.") from exc

        return DecryptionResult(
            plaintext=plaintext,
            algorithm=normalized,
            key_id=record.key_id,
            version=record.version,
            authenticated=True,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _cipher_for(key: bytes, algorithm: EncryptionAlgorithm) -> AESGCM | ChaCha20Poly1305:
        if algorithm is EncryptionAlgorithm.AES_256_GCM:
            return AESGCM(key)
        if algorithm is EncryptionAlgorithm.CHACHA20_POLY1305:
            return ChaCha20Poly1305(key)
        raise EncryptionError(f"Unsupported algorithm {algorithm.value} for cipher creation.")


__all__ = [
    "EncryptionManager",
    "EncryptionError",
    "EncryptedPayload",
    "DecryptionResult",
]
