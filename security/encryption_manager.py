"""Encryption manager utilities for security tests.

This module provides a lightweight `EncryptionManager` implementation that
offers the subset of behaviour required by the security test-suite.  The
implementation focuses on determinism and testability rather than on providing
production-grade cryptography – the real production implementation lives in the
`lukhas_website` package.  The goal here is to supply enough behaviour for the
tests to exercise key management, encryption/decryption flows, and password
hashing without introducing heavyweight dependencies.

The API mirrors the high-level surface of the production manager so that tests
and future migrations can share the same call-sites:

* `generate_key` creates AES or RSA style keys with metadata tracking.
* `encrypt` / `decrypt` operate on UTF-8 strings using a deterministic stream
  cipher derived from the key material (suitable for tests).
* `hash_password` / `verify_password` use PBKDF2 for stable hashing.
* `rotate_key` issues a new key while marking the previous one inactive.

The manager keeps its state entirely in-memory and optionally persists a master
key to disk when a keystore path is supplied.  This mirrors the real component's
behaviour closely enough for the surrounding tests to exercise lifecycle
operations.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class KeyType(Enum):
    """Supported key types for the lightweight manager."""

    AES_256 = "aes-256"
    RSA_2048 = "rsa-2048"


class KeyUsage(Enum):
    """Supported key usage intents."""

    ENCRYPTION = "encryption"
    DATA_ENCRYPTION = "data_encryption"


class EncryptionAlgorithm(Enum):
    """Algorithms available in the simplified manager."""

    STREAM = "stream-cipher"


@dataclass
class KeyMetadata:
    """Metadata stored for generated keys."""

    key_id: str
    key_type: KeyType
    key_usage: KeyUsage
    created_at: float
    is_active: bool = True
    version: int = 1


@dataclass
class EncryptionResult:
    """Container for encryption outputs."""

    encrypted_data: bytes
    iv: bytes
    key_id: str
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.STREAM
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecryptionResult:
    """Container for decryption outputs."""

    decrypted_data: bytes
    key_id: str
    verified: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionManager:
    """Lightweight encryption manager used for tests."""

    def __init__(
        self,
        key_store_path: Optional[str] = None,
        *,
        auto_persist_master: bool = True,
    ) -> None:
        self.key_store_path = Path(key_store_path or os.getenv("LUKHAS_KEYSTORE", ""))
        self.auto_persist_master = auto_persist_master and bool(self.key_store_path)

        self.keys: Dict[str, KeyMetadata] = {}
        self._key_material: Dict[str, bytes] = {}

        if self.auto_persist_master:
            self.key_store_path.mkdir(parents=True, exist_ok=True)
            self._master_key_path = self.key_store_path / "master.key"
        else:
            self._master_key_path = None

        self._master_key = self._load_or_create_master_key()

    # ------------------------------------------------------------------
    # Key lifecycle helpers
    # ------------------------------------------------------------------
    def generate_key(self, key_type: KeyType, key_usage: KeyUsage) -> str:
        """Create a new key and store its metadata."""

        timestamp = int(time.time() * 1000)
        key_id = f"{key_type.value}-{timestamp}-{secrets.token_hex(4)}"

        if key_type is KeyType.AES_256:
            material = secrets.token_bytes(32)
        elif key_type is KeyType.RSA_2048:
            # For the lightweight manager we simply use a larger random blob.
            material = secrets.token_bytes(64)
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        self.keys[key_id] = KeyMetadata(
            key_id=key_id,
            key_type=key_type,
            key_usage=key_usage,
            created_at=time.time(),
        )
        self._key_material[key_id] = material
        return key_id

    def rotate_key(self, key_id: str) -> str:
        """Rotate a key, returning the identifier of the new key."""

        if key_id not in self.keys:
            raise KeyError(f"Key {key_id} not found")

        metadata = self.keys[key_id]
        metadata.is_active = False
        metadata.version += 1

        new_key_id = self.generate_key(metadata.key_type, metadata.key_usage)
        return new_key_id

    # ------------------------------------------------------------------
    # Encryption helpers
    # ------------------------------------------------------------------
    def encrypt(self, data: str, key_id: str) -> EncryptionResult:
        """Encrypt a UTF-8 string using the stored key material."""

        if key_id not in self._key_material:
            raise KeyError(f"Key {key_id} not found")

        raw_key = self._key_material[key_id]
        iv = secrets.token_bytes(16)
        plaintext = data.encode("utf-8")
        keystream = self._derive_stream(raw_key, iv, len(plaintext))
        ciphertext = bytes(b ^ k for b, k in zip(plaintext, keystream))

        return EncryptionResult(
            encrypted_data=ciphertext,
            iv=iv,
            key_id=key_id,
            metadata={"length": len(ciphertext)},
        )

    def decrypt(self, result: EncryptionResult) -> DecryptionResult:
        """Decrypt an :class:`EncryptionResult`."""

        if result.key_id not in self._key_material:
            raise KeyError(f"Key {result.key_id} not found")

        raw_key = self._key_material[result.key_id]
        keystream = self._derive_stream(raw_key, result.iv, len(result.encrypted_data))
        plaintext = bytes(b ^ k for b, k in zip(result.encrypted_data, keystream))

        return DecryptionResult(
            decrypted_data=plaintext,
            key_id=result.key_id,
            verified=True,
            metadata=result.metadata.copy(),
        )

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------
    def hash_password(self, password: str) -> str:
        """Hash a password using PBKDF2."""

        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return f"{base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password previously hashed with :meth:`hash_password`."""

        try:
            salt_b64, hash_b64 = hashed.split("$", 1)
        except ValueError:
            return False

        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return secrets.compare_digest(expected, derived)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _derive_stream(self, key: bytes, iv: bytes, length: int) -> bytes:
        stream = bytearray()
        counter = 0
        while len(stream) < length:
            counter_bytes = counter.to_bytes(4, "big")
            block = hashlib.sha256(key + iv + counter_bytes + self._master_key).digest()
            stream.extend(block)
            counter += 1
        return bytes(stream[:length])

    def _load_or_create_master_key(self) -> bytes:
        if not self.auto_persist_master or not self._master_key_path:
            return secrets.token_bytes(32)

        if self._master_key_path.exists():
            return self._master_key_path.read_bytes()

        master_key = secrets.token_bytes(32)
        self._master_key_path.write_bytes(master_key)
        os.chmod(self._master_key_path, 0o600)
        return master_key


def create_encryption_manager(config: Optional[Dict[str, Any]] = None) -> EncryptionManager:
    """Factory that builds an :class:`EncryptionManager` for tests.

    Parameters
    ----------
    config:
        Optional configuration dictionary.  When provided the function honours
        the ``keystore`` entry to decide where to persist the master key.
    """

    config = config or {}
    key_store_path = config.get("keystore") or os.getenv("LUKHAS_KEYSTORE")
    return EncryptionManager(key_store_path)


__all__ = [
    "EncryptionAlgorithm",
    "EncryptionManager",
    "EncryptionResult",
    "KeyMetadata",
    "KeyType",
    "KeyUsage",
    "DecryptionResult",
    "create_encryption_manager",
]

