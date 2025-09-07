#!/usr/bin/env python3

"""
Guardian Crypto Spine for LUKHAS Memory Systems
==============================================

Implements cryptographic signatures and verification for all memory operations
to ensure integrity, authenticity, and non-repudiation of memory data.

This module addresses the Guardian Security requirement for integrating the Guardian
crypto spine into the C4 memory schema, providing cryptographic protection for all
memory operations including storage, retrieval, and modification.
"""
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

import streamlit as st
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class MemoryOperationType(Enum):
    """Types of memory operations that require cryptographic protection"""

    STORE = "store"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    DELETE = "delete"
    FOLD_CREATE = "fold_create"
    FOLD_ACCESS = "fold_access"
    CASCADE_DELETE = "cascade_delete"
    INTEGRITY_CHECK = "integrity_check"


@dataclass
class GuardianSignature:
    """Cryptographic signature for memory operations"""

    operation_type: MemoryOperationType
    timestamp: float
    signature: bytes
    public_key_hash: str
    nonce: Optional[bytes] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert signature to dictionary for storage"""
        return {
            "operation_type": self.operation_type.value,
            "timestamp": self.timestamp,
            "signature": self.signature.hex(),
            "public_key_hash": self.public_key_hash,
            "nonce": self.nonce.hex() if self.nonce else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GuardianSignature":
        """Create signature from dictionary"""
        return cls(
            operation_type=MemoryOperationType(data["operation_type"]),
            timestamp=data["timestamp"],
            signature=bytes.fromhex(data["signature"]),
            public_key_hash=data["public_key_hash"],
            nonce=bytes.fromhex(data["nonce"]) if data.get("nonce") else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class MemorySecurityContext:
    """Security context for memory operations"""

    user_id: Optional[str]
    session_id: str
    security_level: int  # 1-5 (T1-T5 tiered authentication)
    permissions: list[str]
    cfg_version: str = "guardian@1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for hashing"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "security_level": self.security_level,
            "permissions": sorted(self.permissions),
            "cfg_version": self.cfg_version,
        }


class GuardianCryptoSpine:
    """
    Guardian Security cryptographic spine for memory systems.

    Provides cryptographic signatures, verification, and encryption for all
    memory operations to ensure integrity and authenticity of consciousness data.
    """

    def __init__(self, private_key: Optional[rsa.RSAPrivateKey] = None):
        """
        Initialize Guardian crypto spine.

        Args:
            private_key: RSA private key for signing (generates new if None)
        """
        if private_key is None:
            self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        else:
            self.private_key = private_key

        self.public_key = self.private_key.public_key()
        self.public_key_hash = self._compute_public_key_hash()

        # AES-GCM for symmetric encryption of memory data
        self.aes_key = AESGCM.generate_key(bit_length=256)
        self.aes_gcm = AESGCM(self.aes_key)

        # Memory operation counters for audit trails
        self.operation_counters = {op_type: 0 for op_type in MemoryOperationType}
        self.signature_cache = {}  # Cache recent signatures

    def _compute_public_key_hash(self) -> str:
        """Compute SHA256 hash of public key for identification"""
        public_key_der = self.public_key.public_der()
        return hashlib.sha256(public_key_der).hexdigest()

    def sign_memory_operation(
        self,
        operation_type: MemoryOperationType,
        memory_data: Any,
        security_context: MemorySecurityContext,
        metadata: Optional[dict[str, Any]] = None,
    ) -> GuardianSignature:
        """
        Create cryptographic signature for memory operation.

        Args:
            operation_type: Type of memory operation
            memory_data: Data being operated on
            security_context: Security context for the operation
            metadata: Additional metadata for the signature

        Returns:
            GuardianSignature containing the cryptographic signature
        """
        timestamp = time.time()
        nonce = hashlib.sha256(str(timestamp).encode()).digest()[:16]

        # Create canonical representation for signing
        operation_payload = {
            "operation_type": operation_type.value,
            "timestamp": timestamp,
            "memory_data_hash": self._hash_memory_data(memory_data),
            "security_context": security_context.to_dict(),
            "nonce": nonce.hex(),
            "public_key_hash": self.public_key_hash,
            "metadata": metadata or {},
        }

        # Serialize payload for signing
        payload_bytes = json.dumps(operation_payload, sort_keys=True).encode("utf-8")

        # Create RSA-PSS signature
        signature = self.private_key.sign(
            payload_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        # Update operation counter
        self.operation_counters[operation_type] += 1

        guardian_signature = GuardianSignature(
            operation_type=operation_type,
            timestamp=timestamp,
            signature=signature,
            public_key_hash=self.public_key_hash,
            nonce=nonce,
            metadata={
                **(metadata or {}),
                "operation_count": self.operation_counters[operation_type],
                "security_level": security_context.security_level,
                "cfg_version": security_context.cfg_version,
            },
        )

        # Cache signature for recent operations
        cache_key = f"{operation_type.value}_{timestamp}"
        self.signature_cache[cache_key] = guardian_signature

        return guardian_signature

    def verify_memory_signature(
        self,
        guardian_signature: GuardianSignature,
        memory_data: Any,
        security_context: MemorySecurityContext,
        public_key: Optional[rsa.RSAPublicKey] = None,
    ) -> bool:
        """
        Verify cryptographic signature for memory operation.

        Args:
            guardian_signature: Guardian signature to verify
            memory_data: Original memory data
            security_context: Security context used for signing
            public_key: Public key for verification (uses own if None)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Use provided public key or default to own
            verify_key = public_key or self.public_key

            # Recreate the operation payload
            operation_payload = {
                "operation_type": guardian_signature.operation_type.value,
                "timestamp": guardian_signature.timestamp,
                "memory_data_hash": self._hash_memory_data(memory_data),
                "security_context": security_context.to_dict(),
                "nonce": (guardian_signature.nonce.hex() if guardian_signature.nonce else None),
                "public_key_hash": guardian_signature.public_key_hash,
                "metadata": {
                    k: v
                    for k, v in guardian_signature.metadata.items()
                    if k not in ["operation_count", "security_level", "cfg_version"]
                },
            }

            # Serialize payload
            payload_bytes = json.dumps(operation_payload, sort_keys=True).encode("utf-8")

            # Verify RSA-PSS signature
            verify_key.verify(
                guardian_signature.signature,
                payload_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Additional integrity checks
            return self._perform_integrity_checks(guardian_signature, security_context)

        except Exception:
            # Signature verification failed
            return False

    def encrypt_memory_data(self, memory_data: bytes, associated_data: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Encrypt memory data using AES-GCM.

        Args:
            memory_data: Data to encrypt
            associated_data: Additional authenticated data

        Returns:
            Tuple of (nonce, encrypted_data)
        """
        nonce = hashlib.sha256(str(time.time()).encode()).digest()[:12]  # 96-bit nonce for GCM
        encrypted_data = self.aes_gcm.encrypt(nonce, memory_data, associated_data)
        return nonce, encrypted_data

    def decrypt_memory_data(
        self,
        nonce: bytes,
        encrypted_data: bytes,
        associated_data: Optional[bytes] = None,
    ) -> bytes:
        """
        Decrypt memory data using AES-GCM.

        Args:
            nonce: Nonce used for encryption
            encrypted_data: Encrypted data
            associated_data: Additional authenticated data

        Returns:
            Decrypted data
        """
        return self.aes_gcm.decrypt(nonce, encrypted_data, associated_data)

    def create_memory_integrity_hash(self, memory_data: Any, security_context: MemorySecurityContext) -> str:
        """
        Create integrity hash for memory data.

        Args:
            memory_data: Memory data to hash
            security_context: Security context

        Returns:
            SHA256 hash of memory data with security context
        """
        memory_hash = self._hash_memory_data(memory_data)
        context_hash = hashlib.sha256(json.dumps(security_context.to_dict(), sort_keys=True).encode()).hexdigest()

        combined_hash = hashlib.sha256((memory_hash + context_hash).encode()).hexdigest()
        return combined_hash

    def verify_memory_integrity(
        self,
        memory_data: Any,
        security_context: MemorySecurityContext,
        expected_hash: str,
    ) -> bool:
        """
        Verify integrity of memory data.

        Args:
            memory_data: Memory data to verify
            security_context: Security context
            expected_hash: Expected integrity hash

        Returns:
            True if integrity is valid, False otherwise
        """
        computed_hash = self.create_memory_integrity_hash(memory_data, security_context)
        return hmac.compare_digest(computed_hash, expected_hash)

    def _hash_memory_data(self, memory_data: Any) -> str:
        """Hash memory data consistently"""
        if isinstance(memory_data, (dict, list)):
            data_str = json.dumps(memory_data, sort_keys=True)
        elif isinstance(memory_data, bytes):
            data_str = memory_data.hex()
        else:
            data_str = str(memory_data)

        return hashlib.sha256(data_str.encode()).hexdigest()

    def _perform_integrity_checks(
        self,
        guardian_signature: GuardianSignature,
        security_context: MemorySecurityContext,
    ) -> bool:
        """Perform additional integrity checks on signature"""

        # Check timestamp validity (not too old)
        current_time = time.time()
        max_age = 3600  # 1 hour max age for signatures
        if current_time - guardian_signature.timestamp > max_age:
            return False

        # Check security level consistency
        expected_security_level = security_context.security_level
        signature_security_level = guardian_signature.metadata.get("security_level")
        if signature_security_level and signature_security_level != expected_security_level:
            return False

        # Check cfg_version consistency
        expected_cfg_version = security_context.cfg_version
        signature_cfg_version = guardian_signature.metadata.get("cfg_version")
        return not (signature_cfg_version and signature_cfg_version != expected_cfg_version)

    def get_security_metrics(self) -> dict[str, Any]:
        """Get security metrics for monitoring"""
        return {
            "public_key_hash": self.public_key_hash,
            "operation_counters": dict(self.operation_counters),
            "total_operations": sum(self.operation_counters.values()),
            "cached_signatures": len(self.signature_cache),
            "key_strength": "RSA-2048",
            "encryption_algorithm": "AES-256-GCM",
            "signature_algorithm": "RSA-PSS-SHA256",
        }

    def export_public_key(self) -> bytes:
        """Export public key in PEM format"""
        return self.public_key.public_pem()

    def cleanup_signature_cache(self, max_age: int = 3600):
        """Clean up old signatures from cache"""
        current_time = time.time()
        expired_keys = []

        for cache_key, signature in self.signature_cache.items():
            if current_time - signature.timestamp > max_age:
                expired_keys.append(cache_key)

        for key in expired_keys:
            del self.signature_cache[key]


class C4MemoryGuardianAdapter:
    """
    Adapter to integrate Guardian crypto spine with C4 memory operations.

    This class provides the integration layer between the Guardian cryptographic
    security system and the existing LUKHAS memory architecture.
    """

    def __init__(self, guardian_spine: GuardianCryptoSpine):
        """
        Initialize C4 memory Guardian adapter.

        Args:
            guardian_spine: Guardian crypto spine instance
        """
        self.guardian_spine = guardian_spine
        self.protected_operations = set(MemoryOperationType)

    def secure_memory_store(
        self,
        memory_key: str,
        memory_data: Any,
        security_context: MemorySecurityContext,
        encrypt_data: bool = True,
    ) -> dict[str, Any]:
        """
        Securely store memory data with cryptographic protection.

        Args:
            memory_key: Unique key for the memory data
            memory_data: Data to store
            security_context: Security context for the operation
            encrypt_data: Whether to encrypt the data

        Returns:
            Dictionary containing the secured memory record
        """
        # Create signature for store operation
        signature = self.guardian_spine.sign_memory_operation(
            MemoryOperationType.STORE,
            memory_data,
            security_context,
            {"memory_key": memory_key},
        )

        # Optionally encrypt memory data
        stored_data = memory_data
        encryption_info = None

        if encrypt_data and isinstance(memory_data, (str, dict, list)):
            # Convert to bytes for encryption
            if isinstance(memory_data, str):
                data_bytes = memory_data.encode("utf-8")
            else:
                data_bytes = json.dumps(memory_data).encode("utf-8")

            # Encrypt with associated data
            associated_data = f"{memory_key}:{security_context.session_id}".encode()
            nonce, encrypted_data = self.guardian_spine.encrypt_memory_data(data_bytes, associated_data)

            stored_data = {
                "encrypted": True,
                "data": encrypted_data.hex(),
                "data_type": type(memory_data).__name__,
            }
            encryption_info = {
                "nonce": nonce.hex(),
                "associated_data": associated_data.hex(),
                "algorithm": "AES-256-GCM",
            }

        # Create integrity hash
        integrity_hash = self.guardian_spine.create_memory_integrity_hash(memory_data, security_context)

        # Create secured memory record
        secured_record = {
            "memory_key": memory_key,
            "stored_data": stored_data,
            "guardian_signature": signature.to_dict(),
            "integrity_hash": integrity_hash,
            "encryption_info": encryption_info,
            "security_level": security_context.security_level,
            "created_timestamp": signature.timestamp,
            "cfg_version": security_context.cfg_version,
        }

        return secured_record

    def secure_memory_retrieve(
        self, secured_record: dict[str, Any], security_context: MemorySecurityContext
    ) -> tuple[Any, bool]:
        """
        Securely retrieve memory data with cryptographic verification.

        Args:
            secured_record: Secured memory record
            security_context: Security context for verification

        Returns:
            Tuple of (memory_data, verification_success)
        """
        try:
            # Reconstruct Guardian signature
            signature = GuardianSignature.from_dict(secured_record["guardian_signature"])

            # Extract stored data
            stored_data = secured_record["stored_data"]

            # Decrypt data if necessary
            if isinstance(stored_data, dict) and stored_data.get("encrypted"):
                encryption_info = secured_record["encryption_info"]
                nonce = bytes.fromhex(encryption_info["nonce"])
                associated_data = bytes.fromhex(encryption_info["associated_data"])
                encrypted_data = bytes.fromhex(stored_data["data"])

                # Decrypt
                decrypted_bytes = self.guardian_spine.decrypt_memory_data(nonce, encrypted_data, associated_data)

                # Convert back to original type
                if stored_data["data_type"] == "str":
                    memory_data = decrypted_bytes.decode("utf-8")
                else:
                    memory_data = json.loads(decrypted_bytes.decode("utf-8"))
            else:
                memory_data = stored_data

            # Verify signature
            signature_valid = self.guardian_spine.verify_memory_signature(signature, memory_data, security_context)

            # Verify integrity hash
            integrity_valid = self.guardian_spine.verify_memory_integrity(
                memory_data, security_context, secured_record["integrity_hash"]
            )

            # Create retrieve signature
            self.guardian_spine.sign_memory_operation(
                MemoryOperationType.RETRIEVE,
                memory_data,
                security_context,
                {"memory_key": secured_record["memory_key"]},
            )

            verification_success = signature_valid and integrity_valid

            return memory_data, verification_success

        except Exception:
            # Return None data with failed verification
            return None, False

    def get_guardian_metrics(self) -> dict[str, Any]:
        """Get Guardian security metrics for memory operations"""
        base_metrics = self.guardian_spine.get_security_metrics()

        return {
            **base_metrics,
            "adapter_version": "1.0.0",
            "protected_operations": [op.value for op in self.protected_operations],
            "c4_integration_status": "active",
        }


# Integration helper functions
def create_guardian_memory_context(
    user_id: Optional[str] = None,
    session_id: str = "default",
    security_level: int = 3,
    permissions: Optional[list[str]] = None,
) -> MemorySecurityContext:
    """Create a Guardian memory security context"""
    if permissions is None:
        permissions = ["memory:read", "memory:write"]

    return MemorySecurityContext(
        user_id=user_id,
        session_id=session_id,
        security_level=security_level,
        permissions=permissions,
    )


def initialize_guardian_memory_system() -> tuple[GuardianCryptoSpine, C4MemoryGuardianAdapter]:
    """Initialize complete Guardian memory security system"""
    guardian_spine = GuardianCryptoSpine()
    memory_adapter = C4MemoryGuardianAdapter(guardian_spine)

    return guardian_spine, memory_adapter
