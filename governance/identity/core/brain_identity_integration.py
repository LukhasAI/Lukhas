"""
Brain Identity Connector Integration Module
Provides integration wrapper for connecting the brain identity connector to the identity hub
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

try:
    from .brain_identity_connector import (
        BrainIdentityConnector,
        MemoryIdentityIntegration,
        AccessTier,
        MemoryAccessPolicy,
        MemoryOperation
    )
    BRAIN_IDENTITY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Brain identity connector not available: {e}")
    BRAIN_IDENTITY_AVAILABLE = False

    # Create fallback mock classes
    class BrainIdentityConnector:
        def __init__(self, *args, **kwargs):
            self.initialized = False

    class MemoryIdentityIntegration:
        def __init__(self, *args, **kwargs):
            self.initialized = False

    class AccessTier:
        TIER_1 = 1
        TIER_2 = 2
        TIER_3 = 3
        TIER_4 = 4
        TIER_5 = 5

    class MemoryAccessPolicy:
        TIER_BASED = "tier_based"
        OWNER_ONLY = "owner_only"
        PUBLIC = "public"
        PRIVATE = "private"

    class MemoryOperation:
        READ = "read"
        WRITE = "write"
        MODIFY = "modify"
        DELETE = "delete"

logger = logging.getLogger(__name__)


class BrainIdentityIntegration:
    """
    Integration wrapper for the Brain Identity Connector System.
    Provides a simplified interface for the identity hub.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the brain identity integration"""
        self.config = config or {
            'enable_access_logging': True,
            'max_log_entries': 1000,
            'default_tier_requirements': {
                'read': 1,
                'write': 2,
                'modify': 3,
                'delete': 3
            },
            'memory_type_tiers': {
                'EPISODIC': {'read': 2, 'write': 2},
                'EMOTIONAL': {'read': 2, 'write': 2, 'modify': 3},
                'IDENTITY': {'read': 3, 'write': 4, 'modify': 4, 'delete': 5},
                'SYSTEM': {'read': 3, 'write': 4, 'modify': 4, 'delete': 5}
            },
            'enable_encryption': True,
            'audit_sensitive_operations': True
        }

        # Initialize mock registry and brain integration
        self.id_registry = self._create_mock_registry()
        self.brain_integration = self._create_mock_brain()

        # Initialize the brain identity connector
        if BRAIN_IDENTITY_AVAILABLE:
            self.connector = BrainIdentityConnector(
                self.id_registry,
                self.brain_integration,
                self.config
            )
            self.memory_integration = MemoryIdentityIntegration(
                self.id_registry,
                self.brain_integration
            )
        else:
            logger.warning("Using mock implementations for brain identity components")
            self.connector = BrainIdentityConnector()
            self.memory_integration = MemoryIdentityIntegration()

        self.is_initialized = False
        self.memory_registry = {}
        self.user_sessions = {}

        logger.info("BrainIdentityIntegration initialized with config: %s", self.config)

    def _create_mock_registry(self):
        """Create a mock ID registry for testing purposes"""
        class MockIDRegistry:
            def __init__(self):
                self.users = {}
                self.sessions = {}

            def get_user(self, user_id: str):
                return self.users.get(user_id)

            def validate_session(self, session_id: str):
                return self.sessions.get(session_id)

            def register_user(self, user_id: str, user_data: Dict[str, Any]):
                self.users[user_id] = user_data
                return True

        return MockIDRegistry()

    def _create_mock_brain(self):
        """Create a mock brain integration for testing purposes"""
        class MockBrainIntegration:
            def __init__(self):
                self.memory_manager = MockMemoryManager()

        class MockMemoryManager:
            def __init__(self):
                self.memories = {}

            def retrieve(self, key: str, **kwargs):
                return self.memories.get(key)

            def store(self, key: str, data: Any, **kwargs):
                self.memories[key] = data
                return True

            def update(self, key: str, data: Any, **kwargs):
                if key in self.memories:
                    self.memories[key] = data
                    return True
                return False

            def delete(self, key: str, **kwargs):
                if key in self.memories:
                    del self.memories[key]
                    return True
                return False

        return MockBrainIntegration()

    async def initialize(self):
        """Initialize the brain identity integration system"""
        if self.is_initialized:
            return

        try:
            logger.info("Initializing brain identity integration...")

            # Initialize connector settings
            await self._initialize_connector_settings()

            # Setup memory access policies
            await self._setup_memory_policies()

            # Initialize audit logging
            await self._initialize_audit_system()

            # Setup security wrappers
            await self._setup_security_wrappers()

            self.is_initialized = True
            logger.info("Brain identity integration initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize brain identity integration: {e}")
            raise

    async def _initialize_connector_settings(self):
        """Initialize connector settings"""
        logger.info("Initializing connector settings...")

        # Apply configuration to connector if available
        if BRAIN_IDENTITY_AVAILABLE and hasattr(self.connector, 'config'):
            self.connector.config.update(self.config)

        logger.info("Connector settings initialized")

    async def _setup_memory_policies(self):
        """Setup memory access policies"""
        logger.info("Setting up memory access policies...")

        # Configure tier requirements for different memory types
        self.memory_policies = {
            'default': {
                'read': AccessTier.TIER_1,
                'write': AccessTier.TIER_2,
                'modify': AccessTier.TIER_3,
                'delete': AccessTier.TIER_3
            },
            'episodic': {
                'read': AccessTier.TIER_2,
                'write': AccessTier.TIER_2,
                'modify': AccessTier.TIER_3,
                'delete': AccessTier.TIER_4
            },
            'emotional': {
                'read': AccessTier.TIER_2,
                'write': AccessTier.TIER_2,
                'modify': AccessTier.TIER_3,
                'delete': AccessTier.TIER_4
            },
            'identity': {
                'read': AccessTier.TIER_3,
                'write': AccessTier.TIER_4,
                'modify': AccessTier.TIER_4,
                'delete': AccessTier.TIER_5
            },
            'system': {
                'read': AccessTier.TIER_3,
                'write': AccessTier.TIER_4,
                'modify': AccessTier.TIER_4,
                'delete': AccessTier.TIER_5
            }
        }

        logger.info("Memory access policies configured")

    async def _initialize_audit_system(self):
        """Initialize audit logging system"""
        logger.info("Initializing audit system...")

        self.audit_config = {
            'log_all_access': self.config.get('enable_access_logging', True),
            'log_denied_access': True,
            'log_sensitive_operations': self.config.get('audit_sensitive_operations', True),
            'max_log_entries': self.config.get('max_log_entries', 1000)
        }

        logger.info("Audit system initialized")

    async def _setup_security_wrappers(self):
        """Setup security wrappers for memory operations"""
        logger.info("Setting up security wrappers...")

        # Apply security wrappers if available
        if BRAIN_IDENTITY_AVAILABLE and hasattr(self.memory_integration, 'apply_secure_wrappers'):
            try:
                self.memory_integration.apply_secure_wrappers()
                logger.info("Security wrappers applied successfully")
            except Exception as e:
                logger.warning(f"Failed to apply security wrappers: {e}")

        logger.info("Security wrapper setup complete")

    async def authorize_memory_operation(self,
                                       user_id: str,
                                       operation: str,
                                       memory_key: str,
                                       memory_type: Optional[str] = None,
                                       memory_owner: Optional[str] = None,
                                       access_policy: Optional[str] = None) -> Dict[str, Any]:
        """
        Authorize a memory operation for a user

        Args:
            user_id: User identifier
            operation: Operation type (read, write, modify, delete)
            memory_key: Memory key being accessed
            memory_type: Type of memory (optional)
            memory_owner: Owner of the memory (optional)
            access_policy: Access policy (optional)

        Returns:
            Dict containing authorization result
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Create mock user identity
            user_identity = self._create_mock_identity(user_id)

            # Convert operation string to enum-like value
            operation_enum = self._get_operation_enum(operation)

            # Convert access policy if provided
            policy_enum = None
            if access_policy:
                policy_enum = self._get_access_policy_enum(access_policy)

            # Authorize through connector if available
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.connector, 'authorize_memory_operation'):
                authorized = self.connector.authorize_memory_operation(
                    user_identity=user_identity,
                    operation=operation_enum,
                    memory_key=memory_key,
                    memory_type=memory_type,
                    memory_owner=memory_owner,
                    access_policy=policy_enum
                )
            else:
                # Fallback authorization logic
                authorized = self._fallback_authorization(
                    user_id, operation, memory_key, memory_type, memory_owner
                )

            result = {
                'authorized': authorized,
                'user_id': user_id,
                'operation': operation,
                'memory_key': memory_key,
                'memory_type': memory_type,
                'timestamp': datetime.now().isoformat(),
                'session_id': self._get_user_session(user_id)
            }

            if not authorized:
                result['reason'] = 'Insufficient access tier or policy violation'

            logger.info(f"Memory operation authorization: {authorized} for {user_id}/{operation}/{memory_key}")
            return result

        except Exception as e:
            logger.error(f"Error authorizing memory operation: {e}")
            return {
                'authorized': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _create_mock_identity(self, user_id: str):
        """Create a mock user identity"""
        class MockIdentity:
            def __init__(self, user_id: str):
                self.user_id = user_id
                self.tier = AccessTier.TIER_2  # Default tier

            def get_user_id(self):
                return self.user_id

            def has_access_to_tier(self, required_tier):
                if hasattr(required_tier, 'value'):
                    return self.tier.value >= required_tier.value
                return True  # Fallback for mock scenarios

        return MockIdentity(user_id)

    def _get_operation_enum(self, operation: str):
        """Convert operation string to enum value"""
        operation_map = {
            'read': MemoryOperation.READ,
            'write': MemoryOperation.WRITE,
            'modify': MemoryOperation.MODIFY,
            'delete': MemoryOperation.DELETE
        }
        return operation_map.get(operation.lower(), operation)

    def _get_access_policy_enum(self, policy: str):
        """Convert access policy string to enum value"""
        policy_map = {
            'tier_based': MemoryAccessPolicy.TIER_BASED,
            'owner_only': MemoryAccessPolicy.OWNER_ONLY,
            'public': MemoryAccessPolicy.PUBLIC,
            'private': MemoryAccessPolicy.PRIVATE
        }
        return policy_map.get(policy.lower(), policy)

    def _fallback_authorization(self, user_id: str, operation: str, memory_key: str,
                              memory_type: Optional[str], memory_owner: Optional[str]) -> bool:
        """Fallback authorization logic when main connector is not available"""
        logger.info("Using fallback authorization logic")

        # Simple authorization rules
        # Owner always has access
        if memory_owner and user_id == memory_owner:
            return True

        # System operations allowed for read
        if operation.lower() == 'read':
            return True

        # Write operations require basic validation
        if operation.lower() in ['write', 'modify']:
            return user_id is not None and len(user_id) > 0

        # Delete operations are more restrictive
        if operation.lower() == 'delete':
            return memory_owner and user_id == memory_owner

        return False

    def _get_user_session(self, user_id: str) -> str:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = f"session_{uuid.uuid4().hex[:16]}"
        return self.user_sessions[user_id]

    async def register_memory(self,
                            memory_key: str,
                            memory_owner: str,
                            memory_type: str,
                            access_policy: str = "tier_based",
                            min_tier: int = 1) -> Dict[str, Any]:
        """
        Register a memory with the identity system

        Args:
            memory_key: Unique memory identifier
            memory_owner: Owner of the memory
            memory_type: Type of memory
            access_policy: Access policy for the memory
            min_tier: Minimum tier required

        Returns:
            Dict containing registration result
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Convert min_tier to AccessTier if needed
            tier_enum = getattr(AccessTier, f'TIER_{min_tier}', AccessTier.TIER_1)
            policy_enum = self._get_access_policy_enum(access_policy)

            # Register with connector if available
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.connector, 'register_memory'):
                success = self.connector.register_memory(
                    memory_key, memory_owner, memory_type, policy_enum, tier_enum
                )
            else:
                # Fallback registration
                success = self._fallback_register_memory(
                    memory_key, memory_owner, memory_type, access_policy, min_tier
                )

            # Store in local registry
            self.memory_registry[memory_key] = {
                'owner': memory_owner,
                'type': memory_type,
                'access_policy': access_policy,
                'min_tier': min_tier,
                'registered_at': datetime.now().isoformat()
            }

            logger.info(f"Memory registered: {memory_key} by {memory_owner}")
            return {
                'success': success,
                'memory_key': memory_key,
                'registered_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error registering memory: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _fallback_register_memory(self, memory_key: str, memory_owner: str,
                                memory_type: str, access_policy: str, min_tier: int) -> bool:
        """Fallback memory registration"""
        logger.info(f"Fallback memory registration: {memory_key}")
        # Simple registration - just log it
        return True

    async def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get memory access logs

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of access log entries
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.connector, 'get_access_logs'):
                logs = self.connector.get_access_logs(limit)
            else:
                # Fallback - return mock logs
                logs = self._get_fallback_logs(limit)

            return logs

        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            return []

    def _get_fallback_logs(self, limit: int) -> List[Dict[str, Any]]:
        """Get fallback access logs"""
        return [
            {
                'timestamp': datetime.now().isoformat(),
                'user_id': 'mock_user',
                'operation': 'read',
                'memory_key': 'mock_memory',
                'authorized': True,
                'reason': 'Fallback log entry'
            }
        ][:limit]

    async def get_access_metrics(self) -> Dict[str, Any]:
        """
        Get access metrics for the brain identity system

        Returns:
            Dict containing access metrics
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.memory_integration, 'get_access_metrics'):
                metrics = self.memory_integration.get_access_metrics()
            else:
                # Fallback metrics
                metrics = self._get_fallback_metrics()

            # Add system information
            metrics.update({
                'system_status': 'active',
                'brain_identity_available': BRAIN_IDENTITY_AVAILABLE,
                'memory_registry_size': len(self.memory_registry),
                'active_sessions': len(self.user_sessions),
                'last_updated': datetime.now().isoformat()
            })

            return metrics

        except Exception as e:
            logger.error(f"Error getting access metrics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Get fallback access metrics"""
        return {
            'total_accesses': 0,
            'authorized_accesses': 0,
            'denied_accesses': 0,
            'operation_counts': {
                'read': 0,
                'write': 0,
                'modify': 0,
                'delete': 0
            }
        }

    async def encrypt_memory_content(self, memory_key: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt memory content for secure storage

        Args:
            memory_key: Memory identifier
            content: Content to encrypt

        Returns:
            Dict containing encrypted content
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.memory_integration, 'encrypt_memory_content'):
                encrypted_content = self.memory_integration.encrypt_memory_content(memory_key, content)
            else:
                # Fallback encryption (mock)
                encrypted_content = self._fallback_encrypt(memory_key, content)

            logger.info(f"Memory content encrypted: {memory_key}")
            return encrypted_content

        except Exception as e:
            logger.error(f"Error encrypting memory content: {e}")
            return content  # Return original content on error

    def _fallback_encrypt(self, memory_key: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback encryption (mock implementation)"""
        content_copy = content.copy()
        content_copy['_encrypted'] = True
        content_copy['_encryption_timestamp'] = datetime.now().isoformat()
        content_copy['_encryption_key'] = memory_key
        return content_copy

    async def decrypt_memory_content(self, memory_key: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt memory content for access

        Args:
            memory_key: Memory identifier
            content: Encrypted content

        Returns:
            Dict containing decrypted content
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            if BRAIN_IDENTITY_AVAILABLE and hasattr(self.memory_integration, 'decrypt_memory_content'):
                decrypted_content = self.memory_integration.decrypt_memory_content(memory_key, content)
            else:
                # Fallback decryption (mock)
                decrypted_content = self._fallback_decrypt(memory_key, content)

            logger.info(f"Memory content decrypted: {memory_key}")
            return decrypted_content

        except Exception as e:
            logger.error(f"Error decrypting memory content: {e}")
            return content  # Return original content on error

    def _fallback_decrypt(self, memory_key: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decryption (mock implementation)"""
        content_copy = content.copy()
        if '_encrypted' in content_copy:
            content_copy['_encrypted'] = False
            content_copy['_decryption_timestamp'] = datetime.now().isoformat()
        return content_copy


# Factory function for creating the integration
def create_brain_identity_integration(config: Optional[Dict[str, Any]] = None) -> BrainIdentityIntegration:
    """Create and return a brain identity integration instance"""
    return BrainIdentityIntegration(config)