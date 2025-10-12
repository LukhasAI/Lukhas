"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Memory Component
File: trauma_lock.py
Path: core/memory/trauma_lock.py
Created: 2025-06-20
Author: lukhas AI Team

TAGS: [CRITICAL, KeyFile, Memory]
"""
import random
import streamlit as st

import logging

"""
lukhas AI System - Function Library
File: trauma_lock.py
Path: lukhas/core/memory/trauma_lock.py
Created: 2025-06-05 11:43:39
Author: lukhas AI Team
Version: 1.0

This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Advanced Cognitive Architecture for Cognitive Artificial Intelligence

Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""


# filepath:
# /Users/Gonz/Lukhas_Private/2025-05-21-prototypes-pre-integration/prot1/IDENTITY/trauma_lock.py
import base64
import hashlib
import json
import os
import time
from typing import Any, Optional

import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from lukhas.core.common import get_logger

logger = get_logger(__name__)


class TraumaLockSystem:
    """
    Implements memory vector encryption with trauma-locked access controls.

    This system ensures that sensitive memories are securely encrypted and
    can only be accessed under appropriate conditions, with environmental
    and contextual "keys" required for decryption.
    """

    def __init__(self, encryption_level: str = "medium"):
        self.encryption_level = encryption_level
        self.logger = logging.getLogger("TraumaLockSystem")

        # Generate system encryption key
        self.system_key = self._generate_system_key()

        # Memory access controls
        self.access_policies = self._initialize_access_policies()

        # Initialize secure vector space
        self.secure_memory_vectors = {}
        self.vector_dim = 64 if encryption_level == "low" else (128 if encryption_level == "medium" else 256)

        # Track access attempts
        self.access_log = []
        self.max_log_entries = 1000

        self.logger.info(f"Trauma Lock System initialized with {encryption_level} encryption level")

    def _generate_system_key(self) -> bytes:
        """Generate a secure system key for encryption"""
        # In production, would use a hardware security module or secure storage
        # For this implementation, we'll use an environment variable with a fallback
        env_key = os.environ.get("TRAUMA_LOCK_KEY")

        if env_key:
            # Use provided key (should be base64 encoded)
            try:
                return base64.urlsafe_b64decode(env_key.encode())
            except Exception as e:
                self.logger.warning(f"Invalid environment key, generating new key: {e}")

        # Generate a secure random key
        return Fernet.generate_key()

    def _initialize_access_policies(self) -> dict[str, dict[str, Any]]:
        """Initialize access policies for different security levels"""
        return {
            "standard": {
                "auth_required": False,
                "context_validation": False,
                "expiry_seconds": 604800,  # 7 days
            },
            "sensitive": {
                "auth_required": True,
                "context_validation": True,
                "context_match_threshold": 0.7,
                "expiry_seconds": 86400,  # 24 hours
            },
            "critical": {
                "auth_required": True,
                "context_validation": True,
                "context_match_threshold": 0.9,
                "expiry_seconds": 3600,  # 1 hour
                "multi_factor": True,
            },
        }

    def encrypt_memory(self, memory_data: dict[str, Any], access_level: str = "standard") -> dict[str, Any]:
        """
        Encrypt memory data with trauma-lock protection.

        Args:
            memory_data: The memory data to encrypt
            access_level: The security level to apply

        Returns:
            Encrypted memory data with metadata
        """
        # Verify access level is valid
        if access_level not in self.access_policies:
            self.logger.warning(f"Invalid access level: {access_level}, using standard")
            access_level = "standard"

        # Convert memory to JSON string for encryption
        memory_json = json.dumps(memory_data)

        # Generate encryption key specific to this memory
        memory_id = memory_data.get("id", f"mem_{int(time.time())")
        memory_key = self._derive_memory_key(memory_id)

        # Generate secure vector
        secure_vector = self._generate_secure_vector(memory_data)
        vector_id = f"vec_{hashlib.sha256(memory_id.encode()).hexdigest()}[:8]}"
        self.secure_memory_vectors[vector_id] = secure_vector

        # Encrypt the memory data
        encrypted_data = self._encrypt_data(memory_json.encode(), memory_key)

        # Build the wrapped encrypted memory
        encrypted_memory = {
            "encrypted_data": base64.urlsafe_b64encode(encrypted_data).decode(),
            "vector_id": vector_id,
            "access_level": access_level,
            "encryption_level": self.encryption_level,
            "creation_time": time.time(),
            "metadata": {
                # Include non-sensitive metadata for querying without decryption
                "memory_type": memory_data.get("memory_type", "general"),
                "encrypted": True,
            },
        }

        return encrypted_memory

    def decrypt_memory(
        self,
        encrypted_memory: dict[str, Any],
        access_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Decrypt and return memory data.

        Args:
            encrypted_memory: The encrypted memory data
            access_context: Context information for access control

        Returns:
            Decrypted memory data
        """
        if not encrypted_memory.get("encrypted_data"):
            raise ValueError("No encrypted data found in memory")

        # Get access level and policy
        access_level = encrypted_memory.get("access_level", "standard")
        policy = self.access_policies.get(access_level, self.access_policies["standard"])

        # Context validation if required
        if policy["context_validation"] and access_context:
            vector_id = encrypted_memory.get("vector_id")
            if not vector_id or vector_id not in self.secure_memory_vectors:
                raise ValueError("Security vector not found for memory")

            # Generate context vector
            context_vector = self._generate_context_vector(access_context)

            # Calculate similarity with stored vector
            stored_vector = self.secure_memory_vectors[vector_id]
            similarity = self._calculate_vector_similarity(stored_vector, context_vector)

            # Check if similarity meets threshold
            threshold = policy.get("context_match_threshold", 0.7)
            if similarity < threshold:
                self._log_access_attempt(vector_id, access_level, "context_mismatch", False)
                raise ValueError(f"Context validation failed: similarity {similarity:.2f} below threshold {threshold}")

        # Check expiry if applicable
        creation_time = encrypted_memory.get("creation_time", 0)
        expiry_seconds = policy.get("expiry_seconds")
        if expiry_seconds and (time.time() - creation_time > expiry_seconds):
            self._log_access_attempt(
                encrypted_memory.get("vector_id", "unknown"),
                access_level,
                "expired",
                False,
            )
            raise ValueError("Encrypted memory has expired")

        try:
            # Get the encrypted data
            encrypted_data = base64.urlsafe_b64decode(encrypted_memory["encrypted_data"].encode())

            # Re-derive the memory key
            memory_id = encrypted_memory.get("original_id", f"vec_{encrypted_memory.get('vector_id', '')}")
            memory_key = self._derive_memory_key(memory_id)

            # Decrypt the data
            decrypted_data = self._decrypt_data(encrypted_data, memory_key)

            # Parse JSON
            memory_data = json.loads(decrypted_data.decode())

            # Log successful access
            self._log_access_attempt(
                encrypted_memory.get("vector_id", "unknown"),
                access_level,
                "success",
                True,
            )

            return memory_data

        except Exception as e:
            # Log failed access
            self._log_access_attempt(
                encrypted_memory.get("vector_id", "unknown"),
                access_level,
                str(e),
                False,
            )
            raise ValueError(f"Memory decryption failed: {e}")

    def _derive_memory_key(self, memory_id: str) -> bytes:
        """Derive a unique key for a specific memory"""
        # Use PBKDF2 to derive a key from system key and memory ID
        salt = hashlib.sha256(memory_id.encode()).digest()[:16]

        iterations = 100000 if self.encryption_level == "high" else 10000

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits
            salt=salt,
            iterations=iterations,
        )

        return base64.urlsafe_b64encode(kdf.derive(self.system_key))

    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data with the provided key"""
        cipher = Fernet(key)
        return cipher.encrypt(data)

    def _decrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Decrypt data with the provided key"""
        cipher = Fernet(key)
        return cipher.decrypt(data)

    def _generate_secure_vector(self, memory_data: dict[str, Any]) -> np.ndarray:
        """
        Generate a secure vector representation of memory data.

        This vector encodes characteristics of the memory that can be
        used to validate access contexts without decrypting the memory.
        """
        # Create a deterministic but secure vector representation
        # In a real system, this would use sophisticated vector embedding

        # Use features from the memory to generate the vector
        vector = np.zeros(self.vector_dim)

        # Add content characteristics
        memory_json = json.dumps(memory_data)
        content_hash = hashlib.sha256(memory_json.encode()).digest()

        # Use the hash to seed a random number generator
        np.random.seed(int.from_bytes(content_hash[:4], byteorder="big"))
        vector += np.random.normal(0, 1, self.vector_dim)

        # Add time component
        time_component = np.sin(np.arange(self.vector_dim) * (time.time() % 1000) / 1000)
        vector += time_component * 0.05

        # Add memory type influence
        memory_type = memory_data.get("memory_type", "general")
        type_hash = int(hashlib.sha256(memory_type.encode()).hexdigest(), 16)
        np.random.seed(type_hash)
        type_vector = np.random.normal(0, 0.5, self.vector_dim)
        vector += type_vector

        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _generate_context_vector(self, context: dict[str, Any]) -> np.ndarray:
        """
        Generate a vector representation of an access context.

        This generates a vector that can be compared to the secure memory vector
        to determine if access should be granted.
        """
        vector = np.zeros(self.vector_dim)

        # Add access context characteristics
        context_json = json.dumps(context)
        context_hash = hashlib.sha256(context_json.encode()).digest()

        # Use the hash to seed a random number generator
        np.random.seed(int.from_bytes(context_hash[:4], byteorder="big"))
        vector += np.random.normal(0, 1, self.vector_dim)

        # Add time component
        time_component = np.sin(np.arange(self.vector_dim) * (time.time() % 1000) / 1000)
        vector += time_component * 0.05

        # Add context type influences
        if "access_reason" in context:
            reason = context["access_reason"]
            reason_hash = int(hashlib.sha256(reason.encode()).hexdigest(), 16)
            np.random.seed(reason_hash)
            reason_vector = np.random.normal(0, 0.5, self.vector_dim)
            vector += reason_vector

        # Normalize the vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _calculate_vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        similarity = dot_product / norm_product if norm_product > 0 else 0
        return (similarity + 1) / 2  # Scale from [-1, 1] to [0, 1]

    def _log_access_attempt(self, vector_id: str, access_level: str, reason: str, success: bool) -> None:
        """Log memory access attempts for security auditing"""
        entry = {
            "timestamp": time.time(),
            "vector_id": vector_id,
            "access_level": access_level,
            "reason": reason,
            "success": success,
        }

        self.access_log.append(entry)

        # Maintain maximum log size
        if len(self.access_log) > self.max_log_entries:
            self.access_log = self.access_log[-self.max_log_entries :]

        # Log suspicious activity
        if not success:
            self.logger.warning(f"Memory access denied: vector={vector_id}, level={access_level}, reason={reason}")

    def get_access_stats(self) -> dict[str, Any]:
        """Get statistics about memory access attempts"""
        if not self.access_log:
            return {"total_attempts": 0}

        total_attempts = len(self.access_log)
        successful = sum(1 for entry in self.access_log if entry["success"])

        # Get stats by access level
        by_level = {}
        for entry in self.access_log:
            level = entry["access_level"]
            if level not in by_level:
                by_level[level] = {"attempts": 0, "successful": 0}

            by_level[level]["attempts"] += 1
            if entry["success"]:
                by_level[level]["successful"] += 1

        # Calculate success rates
        for level_stats in by_level.values():
            level_stats["success_rate"] = (
                level_stats["successful"] / level_stats["attempts"] if level_stats["attempts"] > 0 else 0
            )

        return {
            "total_attempts": total_attempts,
            "successful": successful,
            "success_rate": successful / total_attempts if total_attempts > 0 else 0,
            "by_access_level": by_level,
            "encryption_level": self.encryption_level,
            "vector_dim": self.vector_dim,
            "secure_vectors_stored": len(self.secure_memory_vectors),
        }


# Last Updated: 2025-06-05 09:37:28
