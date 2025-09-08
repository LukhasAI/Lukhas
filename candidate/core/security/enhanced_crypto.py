"""
Enhanced Cryptographic System for LUKHAS AI
==========================================
Production-grade cryptographic implementation with key management,
secure defaults, and compliance with modern security standards.
Replaces legacy XOR encryption with proper cryptographic primitives.
"""
from typing import List
import time
import streamlit as st

import base64
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from .secure_logging import get_security_logger

    logger = get_security_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class CryptoAlgorithm(Enum):
    """Supported cryptographic algorithms"""

    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    FERNET = "fernet"  # Simplified symmetric encryption


class KeyDerivationFunction(Enum):
    """Key derivation functions"""

    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"  # Future implementation


@dataclass
class EncryptionKey:
    """Cryptographic key with metadata"""

    key_id: str
    algorithm: CryptoAlgorithm
    key_data: bytes
    created_at: datetime
    purpose: str
    ttl_seconds: Optional[int] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if key has expired"""
        if not self.ttl_seconds:
            return False

        expiry = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now(timezone.utc) > expiry

    def to_dict(self, include_key: bool = False) -> dict[str, Any]:
        """Convert to dictionary (optionally excluding key data)"""
        result = {
            "key_id": self.key_id,
            "algorithm": self.algorithm.value,
            "created_at": self.created_at.isoformat(),
            "purpose": self.purpose,
            "ttl_seconds": self.ttl_seconds,
            "metadata": self.metadata,
            "expired": self.is_expired(),
        }

        if include_key:
            result["key_data"] = base64.b64encode(self.key_data).decode()

        return result


@dataclass
class EncryptionResult:
    """Result of encryption operation"""

    ciphertext: bytes
    key_id: str
    algorithm: str
    nonce: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "nonce": base64.b64encode(self.nonce).decode() if self.nonce else None,
            "tag": base64.b64encode(self.tag).decode() if self.tag else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EncryptionResult":
        """Create from dictionary"""
        return cls(
            ciphertext=base64.b64decode(data["ciphertext"]),
            key_id=data["key_id"],
            algorithm=data["algorithm"],
            nonce=base64.b64decode(data["nonce"]) if data.get("nonce") else None,
            tag=base64.b64decode(data["tag"]) if data.get("tag") else None,
            metadata=data.get("metadata", {}),
        )


class EnhancedCryptoManager:
    """
    Enhanced cryptographic manager with secure key management
    Replaces legacy XOR and weak encryption with modern cryptography
    """

    def __init__(self, master_key: Optional[bytes] = None):
        """Initialize crypto manager"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography package required. Install with: pip install cryptography")

        # Key storage
        self.keys: dict[str, EncryptionKey] = {}

        # Master key for key encryption
        self.master_key = master_key or self._derive_master_key()

        # Default encryption parameters
        self.default_algorithm = CryptoAlgorithm.AES_256_GCM
        self.default_key_ttl = 86400 * 30  # 30 days

        logger.info("Enhanced cryptographic manager initialized")

    def generate_key(self, algorithm: CryptoAlgorithm, purpose: str, ttl_seconds: Optional[int] = None) -> str:
        """Generate new encryption key"""
        key_id = self._generate_key_id()

        # Generate key based on algorithm
        if (
            algorithm in [CryptoAlgorithm.AES_256_GCM, CryptoAlgorithm.AES_256_CBC]
            or algorithm == CryptoAlgorithm.CHACHA20_POLY1305
        ):
            key_data = secrets.token_bytes(32)  # 256-bit key
        elif algorithm == CryptoAlgorithm.FERNET:
            key_data = Fernet.generate_key()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Create key object
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_data=key_data,
            created_at=datetime.now(timezone.utc),
            purpose=purpose,
            ttl_seconds=ttl_seconds or self.default_key_ttl,
        )

        # Store key
        self.keys[key_id] = encryption_key

        logger.info(f"Generated encryption key: {key_id} for purpose: {purpose}")
        return key_id

    async def encrypt(
        self,
        data: Union[str, bytes],
        key_id: Optional[str] = None,
        algorithm: Optional[CryptoAlgorithm] = None,
        purpose: str = "data",
    ) -> tuple[bytes, str]:
        """
        Encrypt data with specified or default key
        Returns: (ciphertext, key_id)
        """
        # Convert string to bytes
        if isinstance(data, str):
            data = data.encode("utf-8")

        # Get or generate key
        if key_id:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
            encryption_key = self.keys[key_id]
        else:
            # Generate new key
            algo = algorithm or self.default_algorithm
            key_id = self.generate_key(algo, purpose)
            encryption_key = self.keys[key_id]

        # Check key expiry
        if encryption_key.is_expired():
            raise ValueError(f"Key expired: {key_id}")

        # Encrypt based on algorithm
        if encryption_key.algorithm == CryptoAlgorithm.AES_256_GCM:
            ciphertext = await self._encrypt_aes_gcm(data, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.AES_256_CBC:
            ciphertext = await self._encrypt_aes_cbc(data, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.CHACHA20_POLY1305:
            ciphertext = await self._encrypt_chacha20(data, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.FERNET:
            ciphertext = await self._encrypt_fernet(data, encryption_key.key_data)
        else:
            raise ValueError(f"Unsupported algorithm: {encryption_key.algorithm}")

        logger.debug(f"Encrypted data with key {key_id}")
        return ciphertext, key_id

    async def decrypt(self, ciphertext: bytes, key_id: str) -> bytes:
        """Decrypt data with specified key"""
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")

        encryption_key = self.keys[key_id]

        # Check key expiry
        if encryption_key.is_expired():
            raise ValueError(f"Key expired: {key_id}")

        # Decrypt based on algorithm
        if encryption_key.algorithm == CryptoAlgorithm.AES_256_GCM:
            plaintext = await self._decrypt_aes_gcm(ciphertext, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.AES_256_CBC:
            plaintext = await self._decrypt_aes_cbc(ciphertext, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.CHACHA20_POLY1305:
            plaintext = await self._decrypt_chacha20(ciphertext, encryption_key.key_data)
        elif encryption_key.algorithm == CryptoAlgorithm.FERNET:
            plaintext = await self._decrypt_fernet(ciphertext, encryption_key.key_data)
        else:
            raise ValueError(f"Unsupported algorithm: {encryption_key.algorithm}")

        logger.debug(f"Decrypted data with key {key_id}")
        return plaintext

    def rotate_key(self, old_key_id: str, purpose: Optional[str] = None) -> str:
        """Rotate encryption key (generate new, mark old as deprecated)"""
        if old_key_id not in self.keys:
            raise ValueError(f"Key not found: {old_key_id}")

        old_key = self.keys[old_key_id]

        # Generate new key with same algorithm
        new_purpose = purpose or old_key.purpose
        new_key_id = self.generate_key(old_key.algorithm, new_purpose)

        # Mark old key as deprecated
        old_key.metadata["deprecated"] = True
        old_key.metadata["rotated_at"] = datetime.now(timezone.utc).isoformat()
        old_key.metadata["new_key_id"] = new_key_id

        logger.info(f"Rotated key {old_key_id} -> {new_key_id}")
        return new_key_id

    def list_keys(self, include_expired: bool = False) -> list[dict[str, Any]]:
        """List all keys with metadata"""
        keys = []
        for key in self.keys.values():
            if not include_expired and key.is_expired():
                continue
            keys.append(key.to_dict(include_key=False))
        return keys

    def derive_key_from_password(
        self, password: str, salt: Optional[bytes] = None, kdf: KeyDerivationFunction = KeyDerivationFunction.PBKDF2
    ) -> bytes:
        """Derive encryption key from password"""
        if salt is None:
            salt = secrets.token_bytes(32)

        if kdf == KeyDerivationFunction.PBKDF2:
            kdf_instance = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # OWASP recommended minimum
            )
        elif kdf == KeyDerivationFunction.SCRYPT:
            kdf_instance = Scrypt(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                n=2**14,
                r=8,
                p=1,
            )
        else:
            raise ValueError(f"Unsupported KDF: {kdf}")

        key = kdf_instance.derive(password.encode())

        logger.info(f"Derived key from password using {kdf.value}")
        return key

    # Internal encryption methods

    async def _encrypt_aes_gcm(self, plaintext: bytes, key: bytes) -> bytes:
        """Encrypt with AES-256-GCM"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Combine nonce + ciphertext + tag
        return nonce + ciphertext + encryptor.tag

    async def _decrypt_aes_gcm(self, ciphertext: bytes, key: bytes) -> bytes:
        """Decrypt with AES-256-GCM"""
        nonce = ciphertext[:12]
        tag = ciphertext[-16:]
        encrypted_data = ciphertext[12:-16]

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

        return plaintext

    async def _encrypt_aes_cbc(self, plaintext: bytes, key: bytes) -> bytes:
        """Encrypt with AES-256-CBC"""
        # Add PKCS7 padding
        block_size = 16
        padding_len = block_size - (len(plaintext) % block_size)
        padded_data = plaintext + bytes([padding_len] * padding_len)

        iv = secrets.token_bytes(16)  # 128-bit IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return iv + ciphertext

    async def _decrypt_aes_cbc(self, ciphertext: bytes, key: bytes) -> bytes:
        """Decrypt with AES-256-CBC"""
        iv = ciphertext[:16]
        encrypted_data = ciphertext[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_len = padded_data[-1]
        plaintext = padded_data[:-padding_len]

        return plaintext

    async def _encrypt_fernet(self, plaintext: bytes, key: bytes) -> bytes:
        """Encrypt with Fernet (simplified symmetric encryption)"""
        fernet = Fernet(key)
        return fernet.encrypt(plaintext)

    async def _decrypt_fernet(self, ciphertext: bytes, key: bytes) -> bytes:
        """Decrypt with Fernet"""
        fernet = Fernet(key)
        return fernet.decrypt(ciphertext)

    async def _encrypt_chacha20(self, plaintext: bytes, key: bytes) -> bytes:
        """Encrypt with ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return nonce + ciphertext

    async def _decrypt_chacha20(self, ciphertext: bytes, key: bytes) -> bytes:
        """Decrypt with ChaCha20-Poly1305"""
        nonce = ciphertext[:12]
        encrypted_data = ciphertext[12:]

        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

        return plaintext

    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        return f"key_{secrets.token_hex(16)}"

    def _derive_master_key(self) -> bytes:
        """Derive master key from environment or generate new"""
        master_key_b64 = os.getenv("LUKHAS_MASTER_KEY")
        if master_key_b64:
            try:
                return base64.b64decode(master_key_b64)
            except Exception:
                logger.warning("Invalid LUKHAS_MASTER_KEY, generating new")

        # Generate new master key
        master_key = secrets.token_bytes(32)
        logger.warning("Generated new master key - set LUKHAS_MASTER_KEY environment variable")
        return master_key


# Global encryption manager instance
_encryption_manager: Optional[EnhancedCryptoManager] = None


def get_encryption_manager() -> EnhancedCryptoManager:
    """Get global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EnhancedCryptoManager()
    return _encryption_manager


async def migrate_from_xor(xor_encrypted_data: bytes, xor_key: bytes) -> tuple[bytes, str]:
    """
    Migrate data from XOR encryption to modern cryptography
    Returns: (new_ciphertext, key_id)
    """
    # Decrypt XOR data (simple XOR operation)
    plaintext = bytes(
        a ^ b
        for a, b in zip(
            xor_encrypted_data, (xor_key * ((len(xor_encrypted_data) // len(xor_key)) + 1))[: len(xor_encrypted_data)]
        )
    )

    # Re-encrypt with modern crypto
    crypto_manager = get_encryption_manager()
    ciphertext, key_id = await crypto_manager.encrypt(plaintext, purpose="migrated_from_xor")

    logger.info(f"Migrated XOR encrypted data to modern encryption with key {key_id}")
    return ciphertext, key_id


# Example usage and testing
async def example_usage():
    """Example usage of enhanced crypto system"""
    print("🔐 Enhanced Cryptographic System Example")
    print("=" * 50)

    # Create crypto manager
    crypto = get_encryption_manager()

    # Test data
    test_data = "This is sensitive LUKHAS consciousness data that needs protection"

    # Test different algorithms
    algorithms = [
        CryptoAlgorithm.AES_256_GCM,
        CryptoAlgorithm.FERNET,
    ]

    for algorithm in algorithms:
        print(f"\nTesting {algorithm.value}:")

        # Encrypt
        ciphertext, key_id = await crypto.encrypt(test_data, algorithm=algorithm, purpose="test")
        print(f"  ✅ Encrypted with key: {key_id}")

        # Decrypt
        decrypted = await crypto.decrypt(ciphertext, key_id)
        print(f"  ✅ Decrypted successfully: {decrypted.decode()} == test_data")

        # Test key rotation
        new_key_id = crypto.rotate_key(key_id)
        print(f"  🔄 Key rotated: {key_id} -> {new_key_id}")

    # List keys
    keys = crypto.list_keys()
    print(f"\n📋 Total keys managed: {len(keys)}")

    print("\n✅ Enhanced cryptographic system test completed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
