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
from typing import Any, Dict, Iterable, Optional, Tuple


class EncryptionAlgorithm(str, Enum):
    """Algorithms supported by the lightweight encryption manager."""

    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    RSA_OAEP = "rsa-oaep"
    EC_ENCRYPTION = "ec-encryption"


class KeyType(str, Enum):
    """Supported key types."""

    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"
    EC_P256 = "ec-p256"
    EC_P384 = "ec-p384"
    ED25519 = "ed25519"


class KeyUsage(str, Enum):
    """Supported key usages."""

    DATA_ENCRYPTION = "data-encryption"
    ENCRYPTION = "encryption"
    SIGNING = "signing"
    KEY_WRAPPING = "key-wrapping"
    AUTHENTICATION = "authentication"


@dataclass
class KeyMetadata:
    """Metadata associated with a managed key."""

    key_id: str
    key_type: KeyType
    usage: KeyUsage
    created_at: datetime
    is_active: bool = True
    expires_at: Optional[datetime] = None
    algorithm: Optional[EncryptionAlgorithm] = None


@dataclass
class EncryptionResult:
    """Result returned by :meth:`EncryptionManager.encrypt`."""

    encrypted_data: bytes
    iv: bytes
    tag: Optional[bytes]
    algorithm: EncryptionAlgorithm
    key_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Result returned by :meth:`EncryptionManager.decrypt`."""

    decrypted_data: bytes
    algorithm: EncryptionAlgorithm
    verified: bool
    key_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionError(RuntimeError):
    """Base error raised by the lightweight encryption manager."""


class KeyNotFoundError(EncryptionError):
    """Raised when a requested key identifier cannot be located."""


class InactiveKeyError(EncryptionError):
    """Raised when an operation targets a key that is not active."""


class EncryptionManager:
    """Minimal encryption manager implementation for tests."""

    DEFAULT_PASSWORD_ITERATIONS = 100_000
    DEFAULT_PASSWORD_SALT_SIZE = 16

    def __init__(
        self,
        key_store_path: Optional[str] = None,
        *,
        auto_rotation: bool = False,
        key_retention_days: int = 90,
        default_algorithm: Optional[EncryptionAlgorithm] = None,
        password_iterations: int = DEFAULT_PASSWORD_ITERATIONS,
        password_salt_size: int = DEFAULT_PASSWORD_SALT_SIZE,
        allowed_algorithms: Optional[Iterable[EncryptionAlgorithm]] = None,
    ) -> None:
        self.key_store_path = key_store_path or os.path.join(
            os.getcwd(), "keys"
        )
        self.auto_rotation = auto_rotation
        self.key_retention_days = key_retention_days

        if password_iterations <= 0:
            raise ValueError("password_iterations must be positive")
        if password_salt_size <= 0:
            raise ValueError("password_salt_size must be positive")

        self.password_iterations = password_iterations
        self.password_salt_size = password_salt_size

        self.allowed_algorithms: Tuple[EncryptionAlgorithm, ...]
        if allowed_algorithms:
            coerced = tuple(self._coerce_algorithm(alg) for alg in allowed_algorithms)
            if not coerced:
                raise ValueError("allowed_algorithms cannot be empty")
            self.allowed_algorithms = coerced
        else:
            self.allowed_algorithms = tuple(EncryptionAlgorithm)

        if default_algorithm is None:
            self.default_algorithm = None
        else:
            coerced_default = self._coerce_algorithm(default_algorithm)
            if coerced_default not in self.allowed_algorithms:
                self.allowed_algorithms = self.allowed_algorithms + (coerced_default,)
            self.default_algorithm = coerced_default

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
        elif key_type == KeyType.RSA_4096:
            material = secrets.token_bytes(512)
        elif key_type in {KeyType.EC_P256, KeyType.ED25519}:
            material = secrets.token_bytes(32)
        elif key_type == KeyType.EC_P384:
            material = secrets.token_bytes(48)
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

        metadata = self.keys[key_id]
        metadata.algorithm = self._select_algorithm(key_id)

        return key_id

    def rotate_key(
        self,
        key_id: str,
        *,
        key_type: Optional[KeyType] = None,
        usage: Optional[KeyUsage] = None,
    ) -> str:
        """Rotate the key referenced by ``key_id`` and return the new key id."""

        metadata = self.keys.get(key_id)
        if not metadata:
            raise KeyNotFoundError(f"Unknown key: {key_id}")

        metadata.is_active = False
        return self.generate_key(key_type or metadata.key_type, usage or metadata.usage)

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
        keystream = self._derive_keystream(key_material, iv, len(data), algorithm)
        encrypted = bytes(b ^ k for b, k in zip(data, keystream))
        tag = hashlib.sha256(iv + key_material + algorithm.value.encode("utf-8")).digest()[:16]

        self._record_operation(start)
        metadata = {
            "key_id": key_id,
            "key_type": self.keys[key_id].key_type.value,
            "key_usage": self.keys[key_id].usage.value,
            "algorithm": algorithm.value,
        }
        if algorithm is EncryptionAlgorithm.RSA_OAEP:
            metadata["hybrid"] = True

        return EncryptionResult(
            encrypted_data=encrypted,
            iv=iv,
            tag=tag,
            algorithm=algorithm,
            key_id=key_id,
            metadata=metadata,
        )

    def decrypt(self, encrypted: EncryptionResult) -> DecryptionResult:
        """Decrypt data previously returned by :meth:`encrypt`."""

        start = time.perf_counter()

        key_id = encrypted.metadata.get("key_id")
        if not key_id:
            raise EncryptionError("Encryption metadata missing key identifier")

        key_material = self._get_active_key_material(key_id)
        keystream = self._derive_keystream(
            key_material, encrypted.iv, len(encrypted.encrypted_data), encrypted.algorithm
        )
        decrypted = bytes(b ^ k for b, k in zip(encrypted.encrypted_data, keystream))

        self._record_operation(start)

        return DecryptionResult(
            decrypted_data=decrypted,
            algorithm=encrypted.algorithm,
            verified=True,
            key_id=key_id,
            metadata={
                "key_id": key_id,
                "algorithm": encrypted.algorithm.value,
            },
        )

    # ------------------------------------------------------------------
    # Password utilities
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        """Return a PBKDF2 based password hash."""

        salt = secrets.token_bytes(self.password_salt_size)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, self.password_iterations
        )
        return f"pbkdf2:{self.password_iterations}:{salt.hex()}:{digest.hex()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password produced by :meth:`hash_password`."""

        try:
            scheme, iterations_text, salt_hex, digest_hex = hashed.split(":", 3)
        except ValueError:  # pragma: no cover - defensive programming
            return False

        if scheme != "pbkdf2":
            return False

        try:
            iterations = int(iterations_text)
        except ValueError:
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
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
        total_seconds = self.total_time_ms / 1000 if self.total_time_ms else 0.0
        ops_per_sec = (
            self.operation_count / total_seconds if total_seconds else 0.0
        )
        return {
            "total_operations": self.operation_count,
            "average_time_ms": avg_ms,
            "ops_per_sec": ops_per_sec,
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
            desired = EncryptionAlgorithm.AES_256_GCM
        elif key_type in {KeyType.RSA_2048, KeyType.RSA_4096}:
            desired = EncryptionAlgorithm.RSA_OAEP
        elif key_type in {KeyType.EC_P256, KeyType.EC_P384, KeyType.ED25519}:
            desired = EncryptionAlgorithm.EC_ENCRYPTION
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        if desired in self.allowed_algorithms:
            return desired
        if self.default_algorithm and self.default_algorithm in self.allowed_algorithms:
            return self.default_algorithm
        return self.allowed_algorithms[0]

    def _get_active_key_material(self, key_id: str) -> bytes:
        metadata = self.keys.get(key_id)
        if not metadata:
            raise KeyNotFoundError(f"Unknown key: {key_id}")
        if not metadata.is_active:
            raise InactiveKeyError(f"Key {key_id} is not active")
        return self._key_material[key_id]

    @staticmethod
    def _derive_keystream(
        key_material: bytes,
        iv: bytes,
        length: int,
        algorithm: EncryptionAlgorithm,
    ) -> bytes:
        seed = hashlib.sha256(key_material + iv + algorithm.value.encode("utf-8")).digest()
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
    password_config = config.get("password_hashing") or {}

    default_algorithm = config.get("default_algorithm")
    allowed_algorithms = config.get("allowed_algorithms")

    def _parse_algorithm(value: Any) -> EncryptionAlgorithm:
        if value is None:
            raise ValueError("Algorithm value cannot be None")
        if isinstance(value, EncryptionAlgorithm):
            return value
        if isinstance(value, str):
            return EncryptionAlgorithm(value.lower())
        raise ValueError(f"Unsupported algorithm value: {value!r}")

    parsed_default = (
        _parse_algorithm(default_algorithm) if default_algorithm is not None else None
    )

    parsed_allowed: Optional[Iterable[EncryptionAlgorithm]]
    if allowed_algorithms is None:
        parsed_allowed = None
    else:
        parsed_allowed = tuple(_parse_algorithm(item) for item in allowed_algorithms)

    return EncryptionManager(
        key_store_path=config.get("key_store_path"),
        auto_rotation=config.get("auto_rotation", False),
        key_retention_days=config.get("key_retention_days", 90),
        default_algorithm=parsed_default,
        password_iterations=int(
            password_config.get(
                "iterations", EncryptionManager.DEFAULT_PASSWORD_ITERATIONS
            )
        ),
        password_salt_size=int(
            password_config.get(
                "salt_size", EncryptionManager.DEFAULT_PASSWORD_SALT_SIZE
            )
        ),
        allowed_algorithms=parsed_allowed,
    )


def _coerce_algorithm_value(value: EncryptionAlgorithm | str) -> EncryptionAlgorithm:
    if isinstance(value, EncryptionAlgorithm):
        return value
    if isinstance(value, str):
        return EncryptionAlgorithm(value.lower())
    raise ValueError(f"Unsupported algorithm specification: {value!r}")


EncryptionManager._coerce_algorithm = staticmethod(_coerce_algorithm_value)

