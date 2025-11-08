#!/usr/bin/env python3
"""
Centralized encryption management for LUKHAS.

This module provides a unified encryption interface for all LUKHAS components,
supporting multiple AEAD (Authenticated Encryption with Associated Data) algorithms
with secure key management and rotation capabilities.

Key Features:
- AEAD-only encryption (AES-256-GCM, ChaCha20-Poly1305)
- Cryptographically secure key generation
- Key rotation support
- Authenticated encryption with tamper detection
- Type-safe algorithm selection
- Zero key logging or exposure

Constellation Framework: 🛡️ Guardian Excellence - Encryption Manager

Related Issues:
- #613: Implement centralized EncryptionManager (P2 - Security Foundation)
- #614: Define EncryptionAlgorithm Enum (P2 - PREREQUISITE)

Security Guarantees:
- All algorithms provide authentication (AEAD)
- Constant-time operations where possible
- Tag verification prevents tampering
- Unique nonces for each encryption
- No key material in logs or error messages

Example Usage:
    >>> from core.security.encryption_manager import EncryptionManager
    >>> from core.security.encryption_types import EncryptionAlgorithm
    >>>
    >>> manager = EncryptionManager()
    >>>
    >>> # Generate key for AES-256-GCM
    >>> key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
    >>>
    >>> # Encrypt data
    >>> data = b"Sensitive information"
    >>> encrypted = manager.encrypt(data, EncryptionAlgorithm.AES_256_GCM, key)
    >>>
    >>> # Decrypt data
    >>> decrypted = manager.decrypt(encrypted, key)
    >>> assert decrypted == data
    >>>
    >>> # Key rotation
    >>> new_key_info = manager.rotate_key("key-001", EncryptionAlgorithm.CHACHA20_POLY1305)
"""

from __future__ import annotations

import secrets
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

from core.security.encryption_types import (
    EncryptionAlgorithm,
    get_algorithm_metadata,
    validate_algorithm_choice,
)


class EncryptionError(Exception):
    """Base exception for encryption operations."""
    pass


class DecryptionError(Exception):
    """Exception raised when decryption fails."""
    pass


class InvalidKeyError(Exception):
    """Exception raised when an invalid key is provided."""
    pass


class EncryptionManager:
    """
    Centralized encryption manager for LUKHAS security.

    Provides unified interface for AEAD encryption operations across all
    LUKHAS components with support for multiple algorithms, secure key
    generation, and key rotation.

    Supported Operations:
    - encrypt(): Encrypt data with AEAD algorithm
    - decrypt(): Decrypt and verify data
    - generate_key(): Generate cryptographically secure keys
    - rotate_key(): Rotate encryption keys

    Supported Algorithms:
    - AES-256-GCM (primary, hardware-accelerated)
    - ChaCha20-Poly1305 (alternative, software-optimized)

    Security Properties:
    - All operations use AEAD (authenticated encryption)
    - Unique nonces generated for each encryption
    - Tag verification prevents tampering
    - No key material in logs or exceptions
    - Cryptographically secure random generation

    Performance Targets:
    - Encryption: <5ms for 1KB data
    - Decryption: <5ms for 1KB data
    - Key generation: <1ms
    """

    def __init__(self) -> None:
        """Initialize the EncryptionManager."""
        self._cipher_cache: dict[str, Any] = {}

    def encrypt(
        self,
        data: bytes,
        algorithm: EncryptionAlgorithm,
        key: bytes | None = None,
        associated_data: bytes | None = None,
    ) -> dict[str, Any]:
        """
        Encrypt data using specified AEAD algorithm.

        Args:
            data: Raw bytes to encrypt
            algorithm: AEAD algorithm to use (must be AEAD-capable)
            key: Encryption key (if None, generates new key)
            associated_data: Optional additional authenticated data (AAD)

        Returns:
            Dictionary containing:
                - algorithm: str - Algorithm name
                - ciphertext: bytes - Encrypted data
                - nonce: bytes - Initialization vector/nonce
                - tag: bytes - Authentication tag
                - key_id: str - Key identifier (optional)

        Raises:
            EncryptionError: If encryption fails
            InvalidKeyError: If key is invalid for algorithm
            ValueError: If algorithm is not AEAD

        Example:
            >>> manager = EncryptionManager()
            >>> key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
            >>> encrypted = manager.encrypt(
            ...     b"secret data",
            ...     EncryptionAlgorithm.AES_256_GCM,
            ...     key
            ... )
            >>> print(encrypted.keys())
            dict_keys(['algorithm', 'ciphertext', 'nonce', 'tag'])
        """
        # Validate algorithm choice (require AEAD)
        valid, error = validate_algorithm_choice(algorithm, require_aead=True, allow_legacy=False)
        if not valid:
            raise ValueError(f"Invalid algorithm choice: {error}")

        # Get algorithm metadata
        metadata = get_algorithm_metadata(algorithm)

        # Generate key if not provided
        if key is None:
            key = self.generate_key(algorithm)

        # Validate key size
        expected_key_bytes = metadata.key_size // 8
        if len(key) != expected_key_bytes:
            raise InvalidKeyError(
                f"Invalid key size for {algorithm.value}: "
                f"expected {expected_key_bytes} bytes, got {len(key)} bytes"
            )

        # Generate unique nonce
        nonce = secrets.token_bytes(metadata.nonce_size)

        try:
            # Get cipher instance
            cipher = self._get_cipher(algorithm, key)

            # Encrypt with AEAD
            if associated_data:
                ciphertext = cipher.encrypt(nonce, data, associated_data)
            else:
                ciphertext = cipher.encrypt(nonce, data, None)

            # Extract tag (last tag_size bytes for AEAD)
            tag_size = metadata.tag_size
            tag = ciphertext[-tag_size:]
            ciphertext_only = ciphertext[:-tag_size]

            return {
                "algorithm": algorithm.value,
                "ciphertext": ciphertext_only,
                "nonce": nonce,
                "tag": tag,
            }

        except Exception as e:
            # Don't leak key material in error messages
            raise EncryptionError(f"Encryption failed for algorithm {algorithm.value}") from e

    def decrypt(
        self,
        encrypted_data: dict[str, Any],
        key: bytes,
        associated_data: bytes | None = None,
    ) -> bytes:
        """
        Decrypt and verify AEAD-encrypted data.

        Args:
            encrypted_data: Dictionary containing encrypted data components
                - algorithm: str - Algorithm name
                - ciphertext: bytes - Encrypted data
                - nonce: bytes - Initialization vector/nonce
                - tag: bytes - Authentication tag
            key: Decryption key
            associated_data: Optional additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext bytes

        Raises:
            DecryptionError: If decryption or tag verification fails
            InvalidKeyError: If key is invalid
            ValueError: If encrypted_data format is invalid

        Example:
            >>> manager = EncryptionManager()
            >>> key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
            >>> encrypted = manager.encrypt(b"secret", EncryptionAlgorithm.AES_256_GCM, key)
            >>> decrypted = manager.decrypt(encrypted, key)
            >>> assert decrypted == b"secret"
        """
        # Validate encrypted data structure
        required_fields = {"algorithm", "ciphertext", "nonce", "tag"}
        if not all(field in encrypted_data for field in required_fields):
            raise ValueError(
                f"Invalid encrypted data format: missing required fields. "
                f"Required: {required_fields}"
            )

        # Get algorithm
        try:
            algorithm = EncryptionAlgorithm(encrypted_data["algorithm"])
        except ValueError as e:
            raise ValueError(f"Unknown algorithm: {encrypted_data['algorithm']}") from e

        # Get algorithm metadata
        metadata = get_algorithm_metadata(algorithm)

        # Validate key size
        expected_key_bytes = metadata.key_size // 8
        if len(key) != expected_key_bytes:
            raise InvalidKeyError(
                f"Invalid key size for {algorithm.value}: "
                f"expected {expected_key_bytes} bytes, got {len(key)} bytes"
            )

        try:
            # Get cipher instance
            cipher = self._get_cipher(algorithm, key)

            # Reconstruct full ciphertext (ciphertext + tag)
            ciphertext = encrypted_data["ciphertext"] + encrypted_data["tag"]
            nonce = encrypted_data["nonce"]

            # Decrypt and verify
            plaintext: bytes
            if associated_data:
                plaintext = cipher.decrypt(nonce, ciphertext, associated_data)
            else:
                plaintext = cipher.decrypt(nonce, ciphertext, None)

            return plaintext

        except Exception as e:
            # Authentication failure or decryption error
            # Don't leak key material in error messages
            raise DecryptionError(
                f"Decryption failed for algorithm {algorithm.value}: "
                "invalid key, corrupted data, or authentication failure"
            ) from e

    def generate_key(self, algorithm: EncryptionAlgorithm) -> bytes:
        """
        Generate cryptographically secure key for specified algorithm.

        Uses secrets module for cryptographically secure random generation.
        Key size is determined by algorithm metadata.

        Args:
            algorithm: Algorithm to generate key for

        Returns:
            Cryptographically secure random key bytes

        Raises:
            ValueError: If algorithm is invalid

        Example:
            >>> manager = EncryptionManager()
            >>> key = manager.generate_key(EncryptionAlgorithm.AES_256_GCM)
            >>> len(key)
            32
            >>> key2 = manager.generate_key(EncryptionAlgorithm.CHACHA20_POLY1305)
            >>> len(key2)
            32
        """
        # Validate algorithm
        valid, error = validate_algorithm_choice(algorithm, require_aead=True, allow_legacy=False)
        if not valid:
            raise ValueError(f"Invalid algorithm choice: {error}")

        # Get key size from metadata
        metadata = get_algorithm_metadata(algorithm)
        key_bytes = metadata.key_size // 8

        # Generate cryptographically secure random key
        return secrets.token_bytes(key_bytes)

    def rotate_key(
        self,
        old_key_id: str,
        new_algorithm: EncryptionAlgorithm,
    ) -> dict[str, Any]:
        """
        Generate new key for key rotation.

        Creates new encryption key and returns metadata for tracking
        the rotation. Applications should re-encrypt data with the new key.

        Args:
            old_key_id: Identifier of the key being rotated
            new_algorithm: Algorithm for the new key

        Returns:
            Dictionary containing:
                - old_key_id: str - Previous key identifier
                - new_key_id: str - New key identifier
                - new_key: bytes - New encryption key
                - algorithm: str - Algorithm name

        Raises:
            ValueError: If algorithm is invalid

        Example:
            >>> manager = EncryptionManager()
            >>> rotation = manager.rotate_key("key-001", EncryptionAlgorithm.AES_256_GCM)
            >>> print(rotation.keys())
            dict_keys(['old_key_id', 'new_key_id', 'new_key', 'algorithm'])
        """
        # Validate algorithm
        valid, error = validate_algorithm_choice(new_algorithm, require_aead=True, allow_legacy=False)
        if not valid:
            raise ValueError(f"Invalid algorithm choice: {error}")

        # Generate new key
        new_key = self.generate_key(new_algorithm)

        # Generate new key ID (cryptographically secure)
        new_key_id = secrets.token_hex(16)

        return {
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "new_key": new_key,
            "algorithm": new_algorithm.value,
        }

    def _get_cipher(self, algorithm: EncryptionAlgorithm, key: bytes) -> Any:
        """
        Get cipher instance for specified algorithm.

        Caches cipher instances for performance. Uses cryptography library's
        AEAD implementations.

        Args:
            algorithm: Encryption algorithm
            key: Encryption key

        Returns:
            Cipher instance (AESGCM or ChaCha20Poly1305)

        Raises:
            ValueError: If algorithm is not supported
        """
        # Note: We don't cache by key for security reasons (key rotation)
        # Each encryption should use a fresh cipher instance

        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return AESGCM(key)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return ChaCha20Poly1305(key)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm.value}")


__all__ = [
    "DecryptionError",
    "EncryptionError",
    "EncryptionManager",
    "InvalidKeyError",
]
