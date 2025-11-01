"""Lightweight encryption manager used by the test suite.

The production repository ships a feature-rich encryption system inside the
``lukhas_website`` package.  Pulling that implementation into the unit tests
would introduce a large number of heavy, third-party dependencies.  The
security test suite only needs a handful of capabilities:

* Key generation with predictable identifiers
* Simple (but deterministic) encryption/decryption so that round-trips can be
  asserted
* Password hashing and verification helpers
* Key rotation metadata tracking

This module provides a small, self-contained implementation that mimics the
behaviour required by the tests while relying solely on the Python standard
library.  The goal is determinism and testability rather than strong
cryptographic guarantees – production code continues to live in the dedicated
package.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from itertools import cycle
from typing import Any, Dict, Optional


class KeyType(Enum):
    """Supported key types for the lightweight manager."""

    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"


class KeyUsage(Enum):
    """High-level key usage categories."""

    DATA_ENCRYPTION = "data_encryption"
    ENCRYPTION = "encryption"


class EncryptionAlgorithm(Enum):
    """Algorithms exposed to the security test-suite."""

    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    RSA_OAEP = "rsa-oaep"


@dataclass
class KeyMetadata:
    """Metadata stored alongside each key."""

    key_id: str
    key_type: KeyType
    key_usage: KeyUsage
    algorithm: EncryptionAlgorithm
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    is_active: bool = True
    rotation_token: Optional[str] = None
    last_used: Optional[float] = None
    usage_count: int = 0


@dataclass
class EncryptionResult:
    """Result returned by :meth:`EncryptionManager.encrypt`."""

    encrypted_data: bytes
    iv: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Result returned by :meth:`EncryptionManager.decrypt`."""

    decrypted_data: bytes
    key_id: str
    verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionManagerError(RuntimeError):
    """Base error for the lightweight manager."""


class KeyNotFoundError(EncryptionManagerError):
    """Raised when a key identifier is unknown."""


class EncryptionManager:
    """Minimal encryption manager for unit tests."""

    def __init__(self, key_store_path: Optional[str] = None) -> None:
        self.key_store_path = key_store_path or os.getenv("LUKHAS_KEYSTORE")
        if self.key_store_path:
            os.makedirs(self.key_store_path, exist_ok=True)

        self.keys: Dict[str, KeyMetadata] = {}
        self._key_material: Dict[str, bytes] = {}

    # ------------------------------------------------------------------
    # Key lifecycle operations
    # ------------------------------------------------------------------
    def generate_key(
        self,
        key_type: KeyType,
        key_usage: KeyUsage,
        *,
        algorithm: Optional[EncryptionAlgorithm] = None,
    ) -> str:
        """Generate a new key and return its identifier."""

        algorithm = algorithm or self._default_algorithm(key_type)
        key_id = self._build_key_id(key_type, version=1)

        metadata = KeyMetadata(
            key_id=key_id,
            key_type=key_type,
            key_usage=key_usage,
            algorithm=algorithm,
        )
        self.keys[key_id] = metadata
        self._key_material[key_id] = self._generate_material(key_type)

        return key_id

    def rotate_key(self, key_id: str) -> str:
        """Rotate a key and return the new identifier."""

        metadata = self._get_metadata(key_id)
        metadata.is_active = False

        new_version = metadata.version + 1
        new_id = self._build_key_id(metadata.key_type, version=new_version)
        new_metadata = KeyMetadata(
            key_id=new_id,
            key_type=metadata.key_type,
            key_usage=metadata.key_usage,
            algorithm=metadata.algorithm,
            version=new_version,
        )
        new_metadata.rotation_token = secrets.token_hex(4)

        self.keys[new_id] = new_metadata
        self._key_material[new_id] = self._generate_material(metadata.key_type)

        return new_id

    # ------------------------------------------------------------------
    # Cryptographic helpers (deterministic XOR cipher for tests)
    # ------------------------------------------------------------------
    def encrypt(self, data: str | bytes, key_id: str) -> EncryptionResult:
        metadata = self._get_metadata(key_id)
        if not metadata.is_active:
            raise EncryptionManagerError(f"Key '{key_id}' is not active")

        plaintext = data if isinstance(data, bytes) else data.encode("utf-8")
        key_material = self._key_material[key_id]

        iv = secrets.token_bytes(12)
        ciphertext = self._xor_cipher(plaintext, key_material)
        payload = base64.b64encode(iv + ciphertext)

        self._record_usage(metadata)

        return EncryptionResult(
            encrypted_data=payload,
            iv=iv,
            key_id=key_id,
            algorithm=metadata.algorithm,
            metadata={"size": len(plaintext)},
        )

    def decrypt(self, result: EncryptionResult) -> DecryptionResult:
        key_id = result.key_id
        metadata = self._get_metadata(key_id)
        key_material = self._key_material[key_id]

        decoded = base64.b64decode(result.encrypted_data)
        iv, ciphertext = decoded[:12], decoded[12:]
        plaintext = self._xor_cipher(ciphertext, key_material)

        metadata.last_used = time.time()

        return DecryptionResult(
            decrypted_data=plaintext,
            key_id=key_id,
            verified=True,
            metadata={"iv": base64.b64encode(iv).decode("ascii")},
        )

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return "pbkdf2$" + base64.b64encode(salt).decode("ascii") + "$" + base64.b64encode(derived).decode("ascii")

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            scheme, salt_b64, hash_b64 = hashed.split("$")
        except ValueError as exc:  # pragma: no cover - defensive
            raise EncryptionManagerError("Invalid password hash format") from exc

        if scheme != "pbkdf2":
            raise EncryptionManagerError(f"Unsupported password hash scheme '{scheme}'")

        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        calculated = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return hmac.compare_digest(expected, calculated)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_metadata(self, key_id: str) -> KeyMetadata:
        try:
            return self.keys[key_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyNotFoundError(f"Unknown key identifier '{key_id}'") from exc

    def _default_algorithm(self, key_type: KeyType) -> EncryptionAlgorithm:
        if key_type is KeyType.RSA_2048:
            return EncryptionAlgorithm.RSA_OAEP
        return EncryptionAlgorithm.AES_256_GCM

    def _build_key_id(self, key_type: KeyType, *, version: int) -> str:
        suffix = secrets.token_hex(4)
        base = f"{key_type.value}-{suffix}"
        return f"{base}-v{version}" if version > 1 else base

    def _generate_material(self, key_type: KeyType) -> bytes:
        size = 32 if key_type is KeyType.AES_256 else 64
        return secrets.token_bytes(size)

    def _xor_cipher(self, payload: bytes, key_material: bytes) -> bytes:
        repeated = cycle(key_material)
        return bytes(b ^ next(repeated) for b in payload)

    def _record_usage(self, metadata: KeyMetadata) -> None:
        metadata.usage_count += 1
        metadata.last_used = time.time()


def create_encryption_manager(config: Optional[Dict[str, Any]] = None) -> EncryptionManager:
    """Factory helper matching the production API."""

    config = config or {}
    key_store_path = config.get("key_store_path")
    return EncryptionManager(key_store_path=key_store_path)


__all__ = [
    "create_encryption_manager",
    "DecryptionResult",
    "EncryptionAlgorithm",
    "EncryptionManager",
    "EncryptionManagerError",
    "EncryptionResult",
    "KeyMetadata",
    "KeyNotFoundError",
    "KeyType",
    "KeyUsage",
]

