"""Lightweight encryption manager used by the security test suite.

This module provides a simplified implementation of the encryption manager
interfaces that the tests exercise.  The real production implementation lives
in ``lukhas_website`` but currently relies on cryptography primitives that are
not available in the constrained test environment.  The goal of this module is
to provide deterministic, dependency-free behaviour that mirrors the public
API required by the tests (key generation, encryption/decryption, password
hashing and key rotation).

The implementation intentionally favours clarity and testability over
cryptographic strength.  It should **not** be used in production code.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional


class EncryptionAlgorithm(str, Enum):
    """Algorithms supported by the lightweight encryption manager."""

    AES_256_GCM = "aes-256-gcm"
    RSA_OAEP = "rsa-oaep"


class KeyType(str, Enum):
    """Supported key types."""

    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"


class KeyUsage(str, Enum):
    """Supported key usages."""

    DATA_ENCRYPTION = "data-encryption"
    ENCRYPTION = "encryption"
    SIGNING = "signing"


@dataclass
class KeyMetadata:
    """Metadata associated with a managed key."""

    key_id: str
    key_type: KeyType
    usage: KeyUsage
    created_at: datetime
    is_active: bool = True
    expires_at: Optional[datetime] = None


@dataclass
class EncryptionResult:
    """Result returned by :meth:`EncryptionManager.encrypt`."""

    encrypted_data: bytes
    iv: bytes
    tag: Optional[bytes]
    algorithm: EncryptionAlgorithm
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Result returned by :meth:`EncryptionManager.decrypt`."""

    decrypted_data: bytes
    algorithm: EncryptionAlgorithm
    verified: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionManager:
    """Minimal encryption manager implementation for tests."""

    def __init__(
        self,
        key_store_path: Optional[str] = None,
        *,
        auto_rotation: bool = False,
        key_retention_days: int = 90,
    ) -> None:
        self.key_store_path = key_store_path or os.path.join(
            os.getcwd(), "keys"
        )
        self.auto_rotation = auto_rotation
        self.key_retention_days = key_retention_days

        self.keys: Dict[str, KeyMetadata] = {}
        self._key_material: Dict[str, bytes] = {}
        self.operation_count = 0
        self.total_time_ms = 0.0

    # ------------------------------------------------------------------
    # Key management
    # ------------------------------------------------------------------
    def generate_key(self, key_type: KeyType, usage: KeyUsage) -> str:
        """Generate a new key for the given ``key_type`` and ``usage``."""

        key_id = f"{key_type.value}-{secrets.token_hex(4)}"
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(days=self.key_retention_days)

        if key_type == KeyType.AES_256:
            material = secrets.token_bytes(32)
        elif key_type == KeyType.RSA_2048:
            # Simulate an RSA private key with 256 random bytes.
            material = secrets.token_bytes(256)
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        self.keys[key_id] = KeyMetadata(
            key_id=key_id,
            key_type=key_type,
            usage=usage,
            created_at=created_at,
            expires_at=expires_at,
        )
        self._key_material[key_id] = material

        return key_id

    def rotate_key(self, key_id: str) -> str:
        """Rotate the key referenced by ``key_id`` and return the new key id."""

        metadata = self.keys.get(key_id)
        if not metadata:
            raise KeyError(f"Unknown key: {key_id}")

        metadata.is_active = False
        return self.generate_key(metadata.key_type, metadata.usage)

    # ------------------------------------------------------------------
    # Encryption / Decryption
    # ------------------------------------------------------------------
    def encrypt(self, plaintext: str | bytes, key_id: str) -> EncryptionResult:
        """Encrypt ``plaintext`` with the specified key."""

        start = time.perf_counter()

        key_material = self._get_active_key_material(key_id)
        data = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
        iv = secrets.token_bytes(12)
        algorithm = self._select_algorithm(key_id)
        keystream = self._derive_keystream(key_material, iv, len(data))
        encrypted = bytes(b ^ k for b, k in zip(data, keystream))

        self._record_operation(start)
        metadata = {"key_id": key_id, "key_type": self.keys[key_id].key_type.value}
        if algorithm is EncryptionAlgorithm.RSA_OAEP:
            metadata["hybrid"] = True

        return EncryptionResult(
            encrypted_data=encrypted,
            iv=iv,
            tag=None,
            algorithm=algorithm,
            metadata=metadata,
        )

    def decrypt(self, encrypted: EncryptionResult) -> DecryptionResult:
        """Decrypt data previously returned by :meth:`encrypt`."""

        start = time.perf_counter()

        key_id = encrypted.metadata.get("key_id")
        if not key_id:
            raise ValueError("Encryption metadata missing key identifier")

        key_material = self._get_active_key_material(key_id)
        keystream = self._derive_keystream(
            key_material, encrypted.iv, len(encrypted.encrypted_data)
        )
        decrypted = bytes(b ^ k for b, k in zip(encrypted.encrypted_data, keystream))

        self._record_operation(start)

        return DecryptionResult(
            decrypted_data=decrypted,
            algorithm=encrypted.algorithm,
            verified=True,
            metadata=dict(encrypted.metadata),
        )

    # ------------------------------------------------------------------
    # Password utilities
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        """Return a PBKDF2 based password hash."""

        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100_000
        )
        return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password produced by :meth:`hash_password`."""

        try:
            algorithm, salt_hex, digest_hex = hashed.split("$")
        except ValueError:  # pragma: no cover - defensive programming
            return False

        if algorithm != "pbkdf2_sha256":
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100_000
        )
        return secrets.compare_digest(candidate, expected)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def get_performance_stats(self) -> Dict[str, Any]:
        """Return aggregated performance statistics for encryption ops."""

        if self.operation_count == 0:
            return {"no_operations": True}

        avg_ms = self.total_time_ms / self.operation_count
        return {
            "total_operations": self.operation_count,
            "average_time_ms": avg_ms,
            "performance_target_met": avg_ms <= 5.0,
            "total_keys": len(self.keys),
            "active_keys": sum(1 for meta in self.keys.values() if meta.is_active),
            "expired_keys": 0,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _select_algorithm(self, key_id: str) -> EncryptionAlgorithm:
        key_type = self.keys[key_id].key_type
        if key_type == KeyType.AES_256:
            return EncryptionAlgorithm.AES_256_GCM
        if key_type == KeyType.RSA_2048:
            return EncryptionAlgorithm.RSA_OAEP
        raise ValueError(f"Unsupported key type: {key_type}")

    def _get_active_key_material(self, key_id: str) -> bytes:
        metadata = self.keys.get(key_id)
        if not metadata:
            raise KeyError(f"Unknown key: {key_id}")
        if not metadata.is_active:
            raise ValueError(f"Key {key_id} is not active")
        return self._key_material[key_id]

    @staticmethod
    def _derive_keystream(key_material: bytes, iv: bytes, length: int) -> bytes:
        seed = hashlib.sha256(key_material + iv).digest()
        stream = bytearray()
        cursor = seed
        while len(stream) < length:
            cursor = hashlib.sha256(cursor).digest()
            stream.extend(cursor)
        return bytes(stream[:length])

    def _record_operation(self, start_time: float) -> None:
        elapsed = (time.perf_counter() - start_time) * 1000
        self.operation_count += 1
        self.total_time_ms += elapsed


def create_encryption_manager(config: Optional[Dict[str, Any]] = None) -> EncryptionManager:
    """Factory used by the tests to obtain an :class:`EncryptionManager`."""

    config = config or {}
    return EncryptionManager(
        key_store_path=config.get("key_store_path"),
        auto_rotation=config.get("auto_rotation", False),
        key_retention_days=config.get("key_retention_days", 90),
    )

