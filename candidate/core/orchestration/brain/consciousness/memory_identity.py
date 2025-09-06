"""
lukhas AI System - Function Library
Path: lukhas/core/Lukhas_ID/vault/memory_identity.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""

"""
Memory-Identity Integration Module
Provides integration between memory system and ΛiD for identity-based access control
Provides integration between memory system and Lukhas_ID for identity-based access control
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from cryptography.fernet import Fernet

from .lukhas_lambda_id import AccessTier, IDRegistry
from .Λ_lambda_id import AccessTier, IDRegistry

logger = logging.getLogger("v1_AGI.identity.memory", timezone)


class MemoryAccessPolicy(Enum):
    """
    Different access policy types for memory access control
    """

    TIER_BASED = 1  # Standard tier-based access control
    CONSENT_BASED = 2  # Requires explicit consent (e.g. for sensitive memories)
    OWNER_ONLY = 3  # Only owner can access
    CUSTOM = 4  # Custom access rules


class MemoryIdentityIntegration:
    """
    Integration layer between memory management and identity systems.
    Handles identity verification, encryption, and access control for memories.
    """

    def __init__(self, id_registry: IDRegistry):
        """
        Initialize the memory-identity integration.

        Args:
            id_registry: The ΛiD registry for identity lookups
            id_registry: The Lukhas_ID registry for identity lookups
        """
        logger.info("Initializing Memory-Identity Integration...")

        self.id_registry = id_registry
        self.memory_permissions = {}  # memory_key -> permission details
        self.shared_memories = {}  # user_id -> set of shared memory keys
        self.encryption_keys = {}  # memory_key -> encryption key

        # Create base encryption key (in production, this would be securely stored)
        self._master_key = Fernet.generate_key()
        self._cipher = Fernet(self._master_key)

        logger.info("Memory-Identity Integration initialized")

    def register_memory(
        self,
        memory_key: str,
        owner_id: str,
        memory_type: str,
        access_policy: MemoryAccessPolicy,
        min_access_tier: AccessTier,
    ) -> bool:
        """
        Register a memory with identity-based access control.

        Args:
            memory_key: Key of the memory to register
            owner_id: ID of the memory owner
            memory_type: Type of the memory
            access_policy: Access policy for this memory
            min_access_tier: Minimum access tier required

        Returns:
            bool: Success status
        """
        if memory_key in self.memory_permissions:
            logger.warning(f"Memory {memory_key} already registered")
            return False

        # Generate memory-specific encryption key
        memory_encryption_key = Fernet.generate_key()
        self.encryption_keys[memory_key] = memory_encryption_key

        # Register permission details
        self.memory_permissions[memory_key] = {
            "owner_id": owner_id,
            "memory_type": memory_type,
            "access_policy": access_policy.value,
            "min_access_tier": min_access_tier.value,
            "shared_with": set(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_accessed": None,
        }

        logger.debug(f"Memory registered: {memory_key}")
        return True

    def verify_access_permission(
        self,
        memory_key: str,
        user_id: Optional[str],
        requesting_tier: AccessTier,
    ) -> bool:
        """
        Verify if a user has permission to access a memory.

        Args:
            memory_key: Key of the memory to check
            user_id: ID of the requesting user (None for system)
            requesting_tier: Access tier of the request

        Returns:
            bool: True if access is allowed, False otherwise
        """
        # Check if memory is registered
        if memory_key not in self.memory_permissions:
            # Unregistered memories follow standard access rules
            return True

        permission = self.memory_permissions[memory_key]
        owner_id = permission["owner_id"]

        # Owner always has access
        if user_id == owner_id:
            return True

        # Check access policy
        access_policy = MemoryAccessPolicy(permission["access_policy"])

        if access_policy == MemoryAccessPolicy.OWNER_ONLY:
            # Only owner can access
            return False

        elif access_policy == MemoryAccessPolicy.CONSENT_BASED:
            # Check if user has consent
            user = self.id_registry.get(user_id) if user_id else None
            if not user or not user.verify_consent():
                return False

            # Also check if it's shared or if tier is sufficient
            if user_id in permission["shared_with"]:
                return True

            # For consent-based memories, require one tier higher than min
            required_tier = permission["min_access_tier"] + 1
            return requesting_tier.value >= required_tier

        elif access_policy == MemoryAccessPolicy.TIER_BASED:
            # Check if shared directly
            if user_id in permission["shared_with"]:
                return True

            # Check tier requirement
            min_tier = permission["min_access_tier"]
            return requesting_tier.value >= min_tier

        elif access_policy == MemoryAccessPolicy.CUSTOM:
            # Custom policies require specific implementation
            # Default to requiring higher tier access
            min_tier = permission["min_access_tier"]
            return requesting_tier.value > min_tier

        return False

    def share_memory(self, memory_key: str, owner_id: str, target_user_id: str) -> bool:
        """
        Share a memory with another user.

        Args:
            memory_key: Key of the memory to share
            owner_id: ID of the memory owner
            target_user_id: ID of the user to share with

        Returns:
            bool: Success status
        """
        # Check if memory is registered
        if memory_key not in self.memory_permissions:
            logger.warning(f"Cannot share unregistered memory: {memory_key}")
            return False

        # Check owner
        permission = self.memory_permissions[memory_key]
        if permission["owner_id"] != owner_id:
            logger.warning(f"Cannot share memory {memory_key}: User {owner_id} is not the owner")
            return False

        # Check if target user exists
        if not self.id_registry.get(target_user_id):
            logger.warning(f"Cannot share memory: Target user {target_user_id} doesn't exist")
            return False

        # Add target user to shared list
        permission["shared_with"].add(target_user_id)

        # Add to target user's shared memories
        if target_user_id not in self.shared_memories:
            self.shared_memories[target_user_id] = set()
        self.shared_memories[target_user_id].add(memory_key)

        logger.debug(f"Memory {memory_key} shared with {target_user_id}")
        return True

    def revoke_memory_access(self, memory_key: str, owner_id: str, target_user_id: str) -> bool:
        """
        Revoke a user's access to a shared memory.

        Args:
            memory_key: Key of the memory
            owner_id: ID of the memory owner
            target_user_id: ID of the user to revoke access from

        Returns:
            bool: Success status
        """
        # Check if memory is registered
        if memory_key not in self.memory_permissions:
            return False

        # Check owner
        permission = self.memory_permissions[memory_key]
        if permission["owner_id"] != owner_id:
            return False

        # Remove target user from shared list
        if target_user_id in permission["shared_with"]:
            permission["shared_with"].remove(target_user_id)

        # Remove from target user's shared memories
        if target_user_id in self.shared_memories and memory_key in self.shared_memories[target_user_id]:
            self.shared_memories[target_user_id].remove(memory_key)

        logger.debug(f"Access to memory {memory_key} revoked from {target_user_id}")
        return True

    def get_shared_memories(self, user_id: str) -> list[str]:
        """
        Get keys of memories shared with a user.

        Args:
            user_id: User ID to get shared memories for

        Returns:
            List[str]: Keys of shared memories
        """
        return list(self.shared_memories.get(user_id, set()))

    def encrypt_memory_content(self, memory_key: str, memory_content: dict[str, Any]) -> dict[str, Any]:
        """
        Encrypt sensitive memory content.

        Args:
            memory_key: Key of the memory to encrypt
            memory_content: Memory content to encrypt

        Returns:
            Dict[str, Any]: Encrypted memory content
        """
        # Only encrypt if memory is registered with encryption key
        if memory_key not in self.encryption_keys:
            return memory_content

        try:
            # Create a deep copy to avoid modifying original
            encrypted_content = memory_content.copy()

            # Extract data to encrypt
            if "data" in encrypted_content:
                data = encrypted_content["data"]

                # Convert to JSON and encrypt
                data_str = json.dumps(data)
                encrypted_data = self._encrypt_data(memory_key, data_str)

                # Replace with encrypted version
                encrypted_content["data"] = None

                # Add metadata about encryption
                if "_meta" not in encrypted_content:
                    encrypted_content["_meta"] = {}

                encrypted_content["_meta"]["encrypted"] = True
                encrypted_content["_meta"]["encrypted_data"] = encrypted_data

            return encrypted_content

        except Exception as e:
            logger.error(f"Error encrypting memory content: {e!s}")
            return memory_content

    def decrypt_memory_content(self, memory_key: str, encrypted_memory: dict[str, Any]) -> dict[str, Any]:
        """
        Decrypt encrypted memory content.

        Args:
            memory_key: Key of the memory to decrypt
            encrypted_memory: Encrypted memory content

        Returns:
            Dict[str, Any]: Decrypted memory content
        """
        # Check if memory is actually encrypted
        if not encrypted_memory.get("_meta", {}).get("encrypted"):
            return encrypted_memory

        # Check if encryption key exists
        if memory_key not in self.encryption_keys:
            logger.warning(f"Cannot decrypt memory {memory_key}: Missing encryption key")
            return encrypted_memory

        try:
            # Create a deep copy to avoid modifying original
            decrypted_memory = encrypted_memory.copy()

            # Get encrypted data
            encrypted_data = encrypted_memory["_meta"]["encrypted_data"]

            # Decrypt data
            data_str = self._decrypt_data(memory_key, encrypted_data)
            data = json.loads(data_str)

            # Replace with decrypted version
            decrypted_memory["data"] = data

            # Update metadata
            if "_meta" in decrypted_memory:
                meta = decrypted_memory["_meta"].copy()
                meta["encrypted"] = False
                if "encrypted_data" in meta:
                    del meta["encrypted_data"]
                decrypted_memory["_meta"] = meta

            return decrypted_memory

        except Exception as e:
            logger.error(f"Error decrypting memory content: {e!s}")
            return encrypted_memory

    def _encrypt_data(self, memory_key: str, data_str: str) -> str:
        """
        Encrypt a string using the memory-specific encryption key.

        Args:
            memory_key: Key of the memory
            data_str: String data to encrypt

        Returns:
            str: Encrypted data as a base64 string
        """
        key = self.encryption_keys[memory_key]
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data_str.encode())
        return encrypted_data.decode()

    def _decrypt_data(self, memory_key: str, encrypted_data: str) -> str:
        """
        Decrypt a string using the memory-specific encryption key.

        Args:
            memory_key: Key of the memory
            encrypted_data: Encrypted data as a base64 string

        Returns:
            str: Decrypted data as a string
        """
        key = self.encryption_keys[memory_key]
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data.encode())
        return decrypted_data.decode()

    def cleanup(self, older_than_days: int = 30) -> int:
        """
        Archive old or orphaned permissions instead of removing them.
        Memories are immutable for security and EU compliance reasons.

        Args:
            older_than_days: Archive permissions older than this many days

        Returns:
            int: Number of items archived
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        cutoff_str = cutoff.isoformat()

        archived = 0

        # Find old permissions and archive them
        for key, permission in self.memory_permissions.items():
            created_at = permission["created_at"]
            if created_at < cutoff_str and not permission.get("archived", False):
                # Mark as archived instead of deleting
                permission["archived"] = True
                permission["archive_date"] = datetime.now(timezone.utc).isoformat()
                permission["archive_reason"] = "age"
                archived += 1

                # Remove from active shared memories
                for user_id in self.shared_memories:
                    if key in self.shared_memories[user_id]:
                        self.shared_memories[user_id].remove(key)

        logger.info(f"Archived {archived} old permissions")
        return archived

    def notify_memory_removal(self, memory_keys: list[str]) -> None:
        """
        Archive memory permissions when notified about memory removals.
        For EU compliance and security, we maintain an immutable record.

        Args:
            memory_keys: List of memory keys that have been marked for removal

        Returns:
            None
        """
        archived = 0

        for key in memory_keys:
            if key in self.memory_permissions and not self.memory_permissions[key].get("archived", False):
                # Mark the memory as archived rather than removing it
                self.memory_permissions[key]["archived"] = True
                self.memory_permissions[key]["archive_date"] = datetime.now(timezone.utc).isoformat()
                self.memory_permissions[key]["archive_reason"] = "removal_notification"

                # Remove from active shared memories while preserving the record
                for user_id in self.shared_memories:
                    if key in self.shared_memories[user_id]:
                        self.shared_memories[user_id].remove(key)

                archived += 1

        if archived > 0:
            logger.info(f"Archived {archived} memory permissions based on removal notification")

    def get_permission_status(self, memory_key: str) -> dict[str, Any]:
        """
        Get detailed status information about a memory's permissions.

        Args:
            memory_key: Key of the memory to check

        Returns:
            Dict: Permission details or empty dict if not found
        """
        if memory_key not in self.memory_permissions:
            return {}

        permission = self.memory_permissions[memory_key].copy()

        # Convert set to list for JSON serialization
        if "shared_with" in permission:
            permission["shared_with"] = list(permission["shared_with"])

        # Add encryption status
        permission["is_encrypted"] = memory_key in self.encryption_keys

        return permission


# Last Updated: 2025-06-05 09:37:28
