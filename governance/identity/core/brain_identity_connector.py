"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: brain_identity_connector.py
Advanced: brain_identity_connector.py
Integration Date: 2025-05-31T07:55:28.094841
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                  LUCΛS :: Brain Identity Connector                          │
│                   Module: brain_identity_connector.py                       │
│                    Location: CORE/identity/                                 │
╰──────────────────────────────────────────────────────────────────────────────╯

📌 Description:
    This module connects the LUKHAS brain integration system with the identity
    management system (LUKHAS_ID), ensuring that memory operations respect
    appropriate access tiers and identity-based permissions.

    The connector enforces permissions for memory access, modification, and
    deletion based on the user's identity tier and consent levels.

📁 Integration Points:
    • LUKHAS_ID access tier enforcement
    • Memory operation authorization
    • Audit logging of sensitive memory access
    • Emotional context preservation during identity transitions
"""

from core.common import get_logger
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Set up logging
logger = logging.getLogger("brain_identity")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Try to import required modules
try:
    from .vault.lukhas_id import AccessTier, ConsentLevel, LucasID, LucasIDRegistry
    from .vault.memory_identity import MemoryAccessPolicy, MemoryOperation

    ID_IMPORTS_AVAILABLE = True
except ImportError:
    logger.warning(
        "Could not # import LUKHAS_ID  # External dependency components. Using placeholder implementations."
    )
    ID_IMPORTS_AVAILABLE = False

    # Create placeholder enums if imports fail
    class AccessTier(Enum):
        TIER_1 = 1
        TIER_2 = 2
        TIER_3 = 3
        TIER_4 = 4
        TIER_5 = 5

    class MemoryAccessPolicy(Enum):
        TIER_BASED = "tier_based"
        OWNER_ONLY = "owner_only"
        PUBLIC = "public"
        PRIVATE = "private"

    class MemoryOperation(Enum):
        READ = "read"
        WRITE = "write"
        DELETE = "delete"
        MODIFY = "modify"


class BrainIdentityConnector:
    """
    Connector between Brain Integration and LUKHAS_ID for enforcing
    identity-based access to memory operations.
    """

    def __init__(self, id_registry=None, brain_integration=None, config=None):
        """
        Initialize the brain identity connector.

        Args:
            id_registry: LUKHAS_ID registry for identity verification
            brain_integration: Brain integration module
            config: Optional configuration dictionary
        """
        self.id_registry = id_registry
        self.brain = brain_integration
        self.config = config or {}

        # Default tier requirements for memory operations
        self.default_tier_requirements = {
            MemoryOperation.READ: AccessTier.TIER_1,
            MemoryOperation.WRITE: AccessTier.TIER_2,
            MemoryOperation.MODIFY: AccessTier.TIER_3,
            MemoryOperation.DELETE: AccessTier.TIER_3,
        }

        # Memory type tier overrides
        self.memory_type_tiers = {
            "EPISODIC": {
                MemoryOperation.READ: AccessTier.TIER_2,
                MemoryOperation.WRITE: AccessTier.TIER_2,
            },
            "EMOTIONAL": {
                MemoryOperation.READ: AccessTier.TIER_2,
                MemoryOperation.WRITE: AccessTier.TIER_2,
                MemoryOperation.MODIFY: AccessTier.TIER_3,
            },
            "IDENTITY": {
                MemoryOperation.READ: AccessTier.TIER_3,
                MemoryOperation.WRITE: AccessTier.TIER_4,
                MemoryOperation.MODIFY: AccessTier.TIER_4,
                MemoryOperation.DELETE: AccessTier.TIER_5,
            },
            "SYSTEM": {
                MemoryOperation.READ: AccessTier.TIER_3,
                MemoryOperation.WRITE: AccessTier.TIER_4,
                MemoryOperation.MODIFY: AccessTier.TIER_4,
                MemoryOperation.DELETE: AccessTier.TIER_5,
            },
        }

        # Audit log for memory access
        self.access_log = []
        self.max_log_entries = self.config.get("max_log_entries", 1000)

        logger.info("Brain Identity Connector initialized")

    def connect_registry(self, id_registry):
        """
        Connect to an ID registry.

        Args:
            id_registry: LUKHAS_ID registry

        Returns:
            bool: Success status
        """
        self.id_registry = id_registry
        logger.info("Connected to LUKHAS_ID Registry")
        return True

    def connect_brain(self, brain_integration):
        """
        Connect to the brain integration module.

        Args:
            brain_integration: Brain integration module

        Returns:
            bool: Success status
        """
        self.brain = brain_integration
        logger.info("Connected to Brain Integration")
        return True

    def authorize_memory_operation(
        self,
        user_identity: Optional[LucasID],
        operation: Union[MemoryOperation, str],
        memory_key: str,
        memory_type: str = None,
        memory_owner: str = None,
        access_policy: Optional[MemoryAccessPolicy] = None,
    ) -> bool:
        """
        Authorize a memory operation based on identity access tier.

        Args:
            user_identity: User identity or None for system operations
            operation: Type of operation to authorize
            memory_key: Key of the memory to operate on
            memory_type: Type of the memory (EPISODIC, SEMANTIC, etc.)
            memory_owner: Owner of the memory
            access_policy: Access policy for the memory

        Returns:
            bool: True if operation is authorized, False otherwise
        """
        # System operations without user identity are limited to read operations
        if user_identity is None:
            if operation == MemoryOperation.READ or operation == "read":
                self._log_access(None, operation, memory_key, True)
                return True
            else:
                self._log_access(
                    None,
                    operation,
                    memory_key,
                    False,
                    "No identity for non-read operation",
                )
                return False

        # Convert string operation to enum if needed
        if isinstance(operation, str):
            try:
                operation = MemoryOperation(operation)
            except (ValueError, AttributeError):
                logger.error(f"Invalid operation: {operation}")
                self._log_access(
                    user_identity.get_user_id(),
                    operation,
                    memory_key,
                    False,
                    "Invalid operation",
                )
                return False

        # Check for memory ownership (owner has full access to their memories)
        if memory_owner and user_identity.get_user_id() == memory_owner:
            self._log_access(
                user_identity.get_user_id(), operation, memory_key, True, "Owner access"
            )
            return True

        # Get required tier based on operation and memory type
        required_tier = self._get_required_tier(operation, memory_type)

        # Check if user has the required tier
        if not user_identity.has_access_to_tier(required_tier):
            self._log_access(
                user_identity.get_user_id(),
                operation,
                memory_key,
                False,
                f"Insufficient tier: has {user_identity.tier.name}, needs {required_tier.name}",
            )
            return False

        # Check access policy if provided
        if access_policy:
            if (
                access_policy == MemoryAccessPolicy.OWNER_ONLY
                and user_identity.get_user_id() != memory_owner
            ):
                self._log_access(
                    user_identity.get_user_id(),
                    operation,
                    memory_key,
                    False,
                    "Owner-only access policy violation",
                )
                return False

            if access_policy == MemoryAccessPolicy.PRIVATE:
                # Private memories require higher tier than normal
                private_tier = AccessTier(
                    min(5, required_tier.value + 1)
                )  # One tier higher, max TIER_5
                if not user_identity.has_access_to_tier(private_tier):
                    self._log_access(
                        user_identity.get_user_id(),
                        operation,
                        memory_key,
                        False,
                        f"Private memory requires higher tier: {private_tier.name}",
                    )
                    return False

        # If we got here, operation is authorized
        self._log_access(user_identity.get_user_id(), operation, memory_key, True)
        return True

    def wrap_memory_function(self, func, operation_type, memory_type=None):
        """
        Wrap a memory function with authorization checks.

        Args:
            func: Function to wrap
            operation_type: Type of operation the function performs
            memory_type: Type of memory the function operates on

        Returns:
            function: Wrapped function that performs authorization
        """

        def wrapped_function(identity, *args, **kwargs):
            # Extract memory key from args or kwargs
            memory_key = kwargs.get("key") or (args[0] if args else None)
            if not memory_key:
                return {"status": "error", "error": "No memory key provided"}

            # Extract owner from kwargs if available
            memory_owner = kwargs.get("owner_id")

            # Authorize the operation
            if not self.authorize_memory_operation(
                user_identity=identity,
                operation=operation_type,
                memory_key=memory_key,
                memory_type=memory_type,
                memory_owner=memory_owner,
            ):
                return {
                    "status": "error",
                    "error": "Access denied",
                    "details": f"User does not have permission for {operation_type} on {memory_key}",
                }

            # If authorized, call the original function
            return func(*args, **kwargs)

        return wrapped_function

    def register_memory(
        self,
        memory_key: str,
        memory_owner: str,
        memory_type: str,
        access_policy: MemoryAccessPolicy = MemoryAccessPolicy.TIER_BASED,
        min_tier: AccessTier = AccessTier.TIER_1,
    ) -> bool:
        """
        Register a memory with identity system for access control.

        Args:
            memory_key: Unique key for the memory
            memory_owner: Owner of the memory
            memory_type: Type of memory
            access_policy: Policy for accessing the memory
            min_tier: Minimum tier required to access memory

        Returns:
            bool: Success status
        """
        # In a full implementation, this would store mappings in a database
        # For now, we'll just log the registration
        logger.info(
            f"Memory {memory_key} registered: owner={memory_owner}, "
            f"type={memory_type}, policy={access_policy}, tier={min_tier.name}"
        )
        return True

    def _get_required_tier(
        self, operation: MemoryOperation, memory_type: Optional[str]
    ) -> AccessTier:
        """
        Get the required access tier for a memory operation.

        Args:
            operation: Operation being performed
            memory_type: Type of memory being accessed

        Returns:
            AccessTier: Required access tier
        """
        # Get default tier for this operation
        default_tier = self.default_tier_requirements.get(operation)

        # If no memory type or not in overrides, return default
        if not memory_type or memory_type not in self.memory_type_tiers:
            return default_tier

        # Check for override for this memory type and operation
        type_tiers = self.memory_type_tiers[memory_type]
        return type_tiers.get(operation, default_tier)

    def _log_access(
        self,
        user_id: Optional[str],
        operation: Union[MemoryOperation, str],
        memory_key: str,
        authorized: bool,
        reason: Optional[str] = None,
    ):
        """
        Log a memory access event.

        Args:
            user_id: ID of the user performing the operation
            operation: Operation being performed
            memory_key: Key of the memory being accessed
            authorized: Whether access was authorized
            reason: Optional reason for authorization decision
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "operation": str(operation),
            "memory_key": memory_key,
            "authorized": authorized,
        }

        if reason:
            log_entry["reason"] = reason

        self.access_log.append(log_entry)

        # Trim log if it gets too large
        if len(self.access_log) > self.max_log_entries:
            self.access_log = self.access_log[-self.max_log_entries :]

        # Log to system logs for security auditing
        log_msg = (
            f"Memory {'access' if authorized else 'access denied'}: "
            f"user={user_id}, op={operation}, key={memory_key}"
        )
        if authorized:
            logger.debug(log_msg)
        else:
            logger.warning(f"{log_msg}, reason={reason}")

    def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent memory access logs.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List[Dict]: Recent access logs
        """
        return self.access_log[-limit:]


class MemoryIdentityIntegration:
    """
    Complete integration between memory systems and identity.

    This class provides a full integration layer between the memory
    management system and the identity system, enabling identity-aware
    memory operations with proper access control and encryption.
    """

    def __init__(self, id_registry, brain_integration):
        """
        Initialize the memory-identity integration.

        Args:
            id_registry: LUKHAS_ID registry
            brain_integration: Brain integration module
        """
        self.id_registry = id_registry
        self.brain = brain_integration
        self.connector = BrainIdentityConnector(id_registry, brain_integration)

        # Memory access metrics
        self.access_metrics = {
            "total_accesses": 0,
            "authorized_accesses": 0,
            "denied_accesses": 0,
            "operation_counts": {"read": 0, "write": 0, "modify": 0, "delete": 0},
        }

        logger.info("Memory Identity Integration initialized")

    def encrypt_memory_content(
        self, key: str, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Encrypt memory content for secure storage.

        Args:
            key: Memory key
            content: Memory content to encrypt

        Returns:
            Dict: Encrypted memory content
        """
        # In a real implementation, this would use actual encryption
        # For demo purposes, we just mark it as encrypted

        # Add metadata about encryption
        content["_meta"] = {
            "encrypted": True,
            "encryption_timestamp": datetime.now().isoformat(),
            "encryption_version": "1.0",
        }

        return content

    def decrypt_memory_content(
        self, key: str, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decrypt memory content for access.

        Args:
            key: Memory key
            content: Encrypted memory content

        Returns:
            Dict: Decrypted memory content
        """
        # In a real implementation, this would use actual decryption
        # For demo purposes, we just remove the encryption flag

        if "_meta" in content:
            meta = content["_meta"].copy()
            meta["encrypted"] = False
            meta["decryption_timestamp"] = datetime.now().isoformat()
            content["_meta"] = meta

        return content

    def register_memory(
        self,
        memory_key: str,
        memory_owner: str,
        memory_type: str,
        access_policy: MemoryAccessPolicy = MemoryAccessPolicy.TIER_BASED,
        min_tier: AccessTier = AccessTier.TIER_1,
    ) -> bool:
        """
        Register a memory with the identity system.

        Args:
            memory_key: Memory key
            memory_owner: Memory owner ID
            memory_type: Type of memory
            access_policy: Access policy for the memory
            min_tier: Minimum tier required to access

        Returns:
            bool: Success status
        """
        return self.connector.register_memory(
            memory_key, memory_owner, memory_type, access_policy, min_tier
        )

    def authorize_access(
        self,
        user_identity: LucasID,
        operation: MemoryOperation,
        memory_key: str,
        memory_type: str,
        memory_owner: str,
    ) -> bool:
        """
        Authorize memory access.

        Args:
            user_identity: User identity
            operation: Operation to authorize
            memory_key: Memory key
            memory_type: Memory type
            memory_owner: Memory owner

        Returns:
            bool: True if access is authorized
        """
        # Update metrics
        self.access_metrics["total_accesses"] += 1
        self.access_metrics["operation_counts"][operation.value] += 1

        # Check authorization
        authorized = self.connector.authorize_memory_operation(
            user_identity, operation, memory_key, memory_type, memory_owner
        )

        # Update metrics based on result
        if authorized:
            self.access_metrics["authorized_accesses"] += 1
        else:
            self.access_metrics["denied_accesses"] += 1

        return authorized

    def apply_secure_wrappers(self):
        """
        Apply secure wrappers to brain integration methods.

        This method wraps key memory operations with security checks.
        """
        if not self.brain:
            logger.error("Cannot apply wrappers: No brain integration available")
            return

        # Apply wrappers to key methods if they exist
        try:
            if hasattr(self.brain, "memory_manager"):
                mm = self.brain.memory_manager

                if hasattr(mm, "retrieve"):
                    mm.retrieve = self.connector.wrap_memory_function(
                        mm.retrieve, MemoryOperation.READ
                    )

                if hasattr(mm, "store"):
                    mm.store = self.connector.wrap_memory_function(
                        mm.store, MemoryOperation.WRITE
                    )

                if hasattr(mm, "update"):
                    mm.update = self.connector.wrap_memory_function(
                        mm.update, MemoryOperation.MODIFY
                    )

                if hasattr(mm, "forget") or hasattr(mm, "delete"):
                    forget_method = getattr(mm, "forget", None) or getattr(mm, "delete")
                    wrapped = self.connector.wrap_memory_function(
                        forget_method, MemoryOperation.DELETE
                    )

                    # Assign to whichever method exists
                    if hasattr(mm, "forget"):
                        mm.forget = wrapped
                    else:
                        mm.delete = wrapped

                logger.info("Applied secure wrappers to memory manager methods")

        except Exception as e:
            logger.error(f"Error applying memory security wrappers: {e}")

    def notify_memory_removal(self, memory_keys: List[str]) -> bool:
        """
        Notify the identity system of memory removal.

        Args:
            memory_keys: List of memory keys being removed

        Returns:
            bool: Success status
        """
        # In a full implementation, this would update the identity system's records
        for key in memory_keys:
            logger.info(f"Memory removal notification: {key}")

        return True

    def get_access_metrics(self) -> Dict[str, Any]:
        """
        Get memory access metrics.

        Returns:
            Dict: Memory access metrics
        """
        return self.access_metrics

    def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get memory access logs.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List[Dict]: Memory access logs
        """
        return self.connector.get_access_logs(limit)


# Basic test code
if __name__ == "__main__":
    print("Testing Brain Identity Connector")

    # Create mock registry and brain
    class MockRegistry:
        pass

    class MockBrain:
        pass

    registry = MockRegistry()
    brain = MockBrain()

    # Create connector
    connector = BrainIdentityConnector(registry, brain)
    print("Connector initialized")

    # Create full integration
    integration = MemoryIdentityIntegration(registry, brain)
    print("Integration initialized")
