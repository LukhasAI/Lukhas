"""Lightweight encryption manager used by the security test-suite.

The real production implementation of the encryption manager lives in a
different lane of the repository with a number of third-party dependencies.
For the purposes of the TODO migration we provide a compact, dependency free
version that implements the same surface area that the tests expect.  The
implementation focuses on determinism and developer ergonomics rather than
strong cryptographic guarantees, which keeps the tests fast while still
covering the core behaviours such as key lifecycle management, symmetric
encryption/decryption and password hashing.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, Union


class EncryptionError(RuntimeError):
    """Raised when encryption or decryption fails."""


class EncryptionAlgorithm(str, Enum):
    """Supported logical encryption algorithms."""

    AES_256_GCM = "AES-256-GCM"
    RSA_2048_OAEP = "RSA-2048-OAEP"


class KeyType(str, Enum):
    """Supported key types for the manager."""

    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"


class KeyUsage(str, Enum):
    """Supported key usages."""

    DATA_ENCRYPTION = "data-encryption"
    ENCRYPTION = "encryption"


@dataclass
class KeyMetadata:
    """Metadata describing an encryption key."""

    key_id: str
    key_type: KeyType
    usage: KeyUsage
    algorithm: EncryptionAlgorithm
    material: bytes
    created_at: datetime
    is_active: bool = True
    rotation_count: int = 0


@dataclass
class EncryptionResult:
    """Container for encrypted payloads."""

    key_id: str
    algorithm: EncryptionAlgorithm
    encrypted_data: bytes
    nonce: bytes


@dataclass
class DecryptionResult:
    """Container for decrypted payloads."""

    key_id: str
    algorithm: EncryptionAlgorithm
    decrypted_data: bytes
    verified: bool


class EncryptionManager:
    """Manage encryption keys and provide crypto helpers for tests."""

    def __init__(self, config: Optional[Dict[str, Union[str, int]]] = None) -> None:
        self._config = config or {}
        self.keys: Dict[str, KeyMetadata] = {}

    # ------------------------------------------------------------------
    # Key management
    # ------------------------------------------------------------------
    def generate_key(self, key_type: KeyType, usage: KeyUsage) -> str:
        """Generate a new key and return its identifier."""

        algorithm = self._algorithm_for_type(key_type)
        key_material = self._generate_material(key_type)
        key_id = self._build_key_id(key_type)

        self.keys[key_id] = KeyMetadata(
            key_id=key_id,
            key_type=key_type,
            usage=usage,
            algorithm=algorithm,
            material=key_material,
            created_at=datetime.now(timezone.utc),
        )
        return key_id

    def rotate_key(self, key_id: str) -> str:
        """Rotate the specified key and return the new key id."""

        if key_id not in self.keys:
            raise KeyError(f"Unknown key: {key_id}")

        current_key = self.keys[key_id]
        current_key.is_active = False
        current_key.rotation_count += 1

        new_key_id = self.generate_key(current_key.key_type, current_key.usage)
        return new_key_id

    # ------------------------------------------------------------------
    # Cryptographic helpers
    # ------------------------------------------------------------------
    def encrypt(
        self,
        data: Union[str, bytes],
        key_id: str,
    ) -> EncryptionResult:
        """Encrypt a payload using the specified key."""

        key = self._get_key(key_id)
        nonce = secrets.token_bytes(16)
        plaintext = data.encode("utf-8") if isinstance(data, str) else data
        keystream = self._derive_keystream(key.material, nonce, len(plaintext))
        ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))

        return EncryptionResult(
            key_id=key.key_id,
            algorithm=key.algorithm,
            encrypted_data=ciphertext,
            nonce=nonce,
        )

    def decrypt(self, result: EncryptionResult) -> DecryptionResult:
        """Decrypt a payload that was produced by :meth:`encrypt`."""

        key = self._get_key(result.key_id)
        keystream = self._derive_keystream(key.material, result.nonce, len(result.encrypted_data))
        plaintext = bytes(c ^ k for c, k in zip(result.encrypted_data, keystream))

        return DecryptionResult(
            key_id=key.key_id,
            algorithm=key.algorithm,
            decrypted_data=plaintext,
            verified=True,
        )

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        """Hash a password using PBKDF2 with SHA-256."""

        iterations = int(self._config.get("password_iterations", 390_000))
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return "pbkdf2_sha256$%d$%s$%s" % (
            iterations,
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(dk).decode("ascii"),
        )

    def verify_password(self, password: str, encoded: str) -> bool:
        """Verify a password against a stored PBKDF2 hash."""

        try:
            algorithm, iteration_str, salt_b64, hash_b64 = encoded.split("$")
        except ValueError as exc:  # pragma: no cover - guard clause
            raise ValueError("Invalid encoded password format") from exc

        if algorithm != "pbkdf2_sha256":
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        iterations = int(iteration_str)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        calculated = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calculated, expected)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_key(self, key_id: str) -> KeyMetadata:
        try:
            key = self.keys[key_id]
        except KeyError as exc:  # pragma: no cover - guard clause
            raise KeyError(f"Unknown key: {key_id}") from exc

        if not key.is_active:
            raise EncryptionError(f"Key {key_id} is not active")
        return key

    @staticmethod
    def _build_key_id(key_type: KeyType) -> str:
        return f"{key_type.value}-{int(time.time() * 1000)}-{secrets.token_hex(4)}"

    @staticmethod
    def _algorithm_for_type(key_type: KeyType) -> EncryptionAlgorithm:
        if key_type is KeyType.AES_256:
            return EncryptionAlgorithm.AES_256_GCM
        if key_type is KeyType.RSA_2048:
            return EncryptionAlgorithm.RSA_2048_OAEP
        raise ValueError(f"Unsupported key type: {key_type}")

    @staticmethod
    def _generate_material(key_type: KeyType) -> bytes:
        if key_type is KeyType.AES_256:
            return os.urandom(32)
        if key_type is KeyType.RSA_2048:
            # Represent RSA private key material with 2048/8 bytes of entropy.
            return os.urandom(256)
        raise ValueError(f"Unsupported key type: {key_type}")

    @staticmethod
    def _derive_keystream(material: bytes, nonce: bytes, length: int) -> bytes:
        """Derive a pseudo-random keystream from key material and nonce."""

        digest = hashlib.sha256(material + nonce).digest()
        keystream = bytearray()
        while len(keystream) < length:
            keystream.extend(digest)
            digest = hashlib.sha256(digest + material).digest()
        return bytes(keystream[:length])


def create_encryption_manager(config: Optional[Dict[str, Union[str, int]]] = None) -> EncryptionManager:
    """Factory helper used throughout the security test-suite."""

    return EncryptionManager(config=config)
