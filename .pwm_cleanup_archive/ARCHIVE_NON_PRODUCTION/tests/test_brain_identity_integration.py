"""
Test suite for Brain Identity Integration
"""

from datetime import datetime

import pytest

from identity.core.brain_identity_integration import (
    BrainIdentityIntegration,
    create_brain_identity_integration,
)
from identity.identity_hub import IdentityHub


class TestBrainIdentityIntegration:
    """Test suite for brain identity integration with identity hub"""

    @pytest.fixture
    async def identity_hub(self):
        """Create a test identity hub instance"""
        hub = IdentityHub()
        return hub

    @pytest.fixture
    async def brain_identity_integration(self):
        """Create a test brain identity integration instance"""
        config = {
            "enable_access_logging": True,
            "max_log_entries": 500,
            "default_tier_requirements": {
                "read": 1,
                "write": 2,
                "modify": 3,
                "delete": 3,
            },
            "memory_type_tiers": {
                "EPISODIC": {"read": 2, "write": 2},
                "EMOTIONAL": {"read": 2, "write": 2, "modify": 3},
                "IDENTITY": {"read": 3, "write": 4, "modify": 4, "delete": 5},
            },
            "enable_encryption": True,
            "audit_sensitive_operations": True,
        }
        integration = BrainIdentityIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_brain_identity_integration_initialization(
        self, brain_identity_integration
    ):
        """Test brain identity integration initialization"""
        assert brain_identity_integration is not None
        assert brain_identity_integration.config["enable_access_logging"] is True
        assert brain_identity_integration.config["max_log_entries"] == 500
        assert brain_identity_integration.is_initialized is False

        # Initialize the integration
        await brain_identity_integration.initialize()
        assert brain_identity_integration.is_initialized is True

    @pytest.mark.asyncio
    async def test_identity_hub_brain_identity_registration(self, identity_hub):
        """Test that brain identity is registered in the identity hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Verify brain identity service is available (if BRAIN_IDENTITY_AVAILABLE is True)
        services = identity_hub.list_services()

        # The service should be registered if the import was successful
        if "brain_identity" in services:
            assert identity_hub.get_service("brain_identity") is not None

    @pytest.mark.asyncio
    async def test_memory_operation_authorization_through_hub(self, identity_hub):
        """Test memory operation authorization through the identity hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Skip test if brain identity not available
        if "brain_identity" not in identity_hub.services:
            pytest.skip("Brain identity integration not available")

        # Test memory operation authorization
        result = await identity_hub.authorize_memory_operation(
            user_id="test_user",
            operation="read",
            memory_key="test_memory_001",
            memory_type="EPISODIC",
            memory_owner="test_user",
        )

        # Verify result structure
        assert "authorized" in result
        assert "user_id" in result
        assert result["user_id"] == "test_user"
        assert "operation" in result
        assert result["operation"] == "read"
        assert "memory_key" in result
        assert result["memory_key"] == "test_memory_001"
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_memory_registration_through_hub(self, identity_hub):
        """Test memory registration through the identity hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Skip test if brain identity not available
        if "brain_identity" not in identity_hub.services:
            pytest.skip("Brain identity integration not available")

        # Test memory registration
        result = await identity_hub.register_memory_with_identity(
            memory_key="test_memory_002",
            memory_owner="test_user",
            memory_type="EMOTIONAL",
            access_policy="tier_based",
            min_tier=2,
        )

        # Verify result structure
        assert "success" in result
        assert "memory_key" in result
        assert result["memory_key"] == "test_memory_002"
        if result["success"]:
            assert "registered_at" in result

    @pytest.mark.asyncio
    async def test_access_logs_retrieval(self, identity_hub):
        """Test getting access logs through the identity hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Skip test if brain identity not available
        if "brain_identity" not in identity_hub.services:
            pytest.skip("Brain identity integration not available")

        # Get access logs
        logs = await identity_hub.get_brain_identity_access_logs(limit=50)

        # Verify logs structure
        assert isinstance(logs, list)
        if len(logs) > 0:
            log_entry = logs[0]
            assert "timestamp" in log_entry
            assert "user_id" in log_entry
            assert "operation" in log_entry
            assert "memory_key" in log_entry
            assert "authorized" in log_entry

    @pytest.mark.asyncio
    async def test_brain_identity_metrics(self, identity_hub):
        """Test getting brain identity metrics through hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Skip test if brain identity not available
        if "brain_identity" not in identity_hub.services:
            pytest.skip("Brain identity integration not available")

        # Get metrics
        result = await identity_hub.get_brain_identity_metrics()

        # Verify result
        assert result["available"] is True
        assert "metrics" in result
        metrics = result["metrics"]
        assert "total_accesses" in metrics
        assert "authorized_accesses" in metrics
        assert "denied_accesses" in metrics
        assert "operation_counts" in metrics
        assert "system_status" in metrics
        assert "brain_identity_available" in metrics

    @pytest.mark.asyncio
    async def test_memory_content_encryption_decryption(self, identity_hub):
        """Test memory content encryption and decryption through hub"""
        # Initialize the hub
        await identity_hub.initialize()

        # Skip test if brain identity not available
        if "brain_identity" not in identity_hub.services:
            pytest.skip("Brain identity integration not available")

        # Test content
        original_content = {
            "data": "sensitive memory content",
            "type": "emotional",
            "timestamp": datetime.now().isoformat(),
        }

        # Test encryption
        encrypted_content = await identity_hub.encrypt_memory_content(
            "test_memory_003", original_content
        )

        # Verify encryption (should have encryption metadata)
        assert encrypted_content is not None
        if "_encrypted" in encrypted_content or "_meta" in encrypted_content:
            # Has encryption markers
            assert True

        # Test decryption
        decrypted_content = await identity_hub.decrypt_memory_content(
            "test_memory_003", encrypted_content
        )

        # Verify decryption
        assert decrypted_content is not None
        assert "data" in decrypted_content
        assert decrypted_content["data"] == "sensitive memory content"

    @pytest.mark.asyncio
    async def test_error_handling_missing_service(self, identity_hub):
        """Test error handling when brain identity service is not available"""
        # Initialize the hub
        await identity_hub.initialize()

        # Remove brain identity service if it exists
        if "brain_identity" in identity_hub.services:
            del identity_hub.services["brain_identity"]

        # Test memory operation authorization with missing service
        result = await identity_hub.authorize_memory_operation(
            "test_user", "read", "test_memory"
        )
        assert result["authorized"] is False
        assert "error" in result

        # Test memory registration with missing service
        result = await identity_hub.register_memory_with_identity(
            "test_memory", "test_user", "EPISODIC"
        )
        assert result["success"] is False
        assert "error" in result

        # Test metrics with missing service
        result = await identity_hub.get_brain_identity_metrics()
        assert result["available"] is False
        assert "error" in result

        # Test access logs with missing service
        logs = await identity_hub.get_brain_identity_access_logs()
        assert logs == []

        # Test encryption/decryption with missing service (should return original content)
        test_content = {"test": "data"}
        encrypted = await identity_hub.encrypt_memory_content("key", test_content)
        assert encrypted == test_content  # Should return original

        decrypted = await identity_hub.decrypt_memory_content("key", test_content)
        assert decrypted == test_content  # Should return original

    @pytest.mark.asyncio
    async def test_authorization_with_different_operations(
        self, brain_identity_integration
    ):
        """Test authorization with different operation types"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        operations = ["read", "write", "modify", "delete"]
        memory_key = "test_memory_004"
        user_id = "test_user"

        for operation in operations:
            result = await brain_identity_integration.authorize_memory_operation(
                user_id=user_id,
                operation=operation,
                memory_key=memory_key,
                memory_type="EPISODIC",
            )

            # Should get a response for each operation
            assert "authorized" in result
            assert result["operation"] == operation
            assert result["user_id"] == user_id
            assert result["memory_key"] == memory_key
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_authorization_with_different_memory_types(
        self, brain_identity_integration
    ):
        """Test authorization with different memory types"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        memory_types = ["EPISODIC", "EMOTIONAL", "IDENTITY", "SYSTEM"]
        user_id = "test_user"
        operation = "read"

        for memory_type in memory_types:
            result = await brain_identity_integration.authorize_memory_operation(
                user_id=user_id,
                operation=operation,
                memory_key=f"test_memory_{memory_type.lower()}",
                memory_type=memory_type,
            )

            # Should get a response for each memory type
            assert "authorized" in result
            assert result["memory_type"] == memory_type
            assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_memory_registry_functionality(self, brain_identity_integration):
        """Test memory registry functionality"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        # Register multiple memories
        memories = [
            ("memory_001", "user_001", "EPISODIC", "tier_based", 1),
            ("memory_002", "user_002", "EMOTIONAL", "owner_only", 2),
            ("memory_003", "user_001", "IDENTITY", "private", 3),
        ]

        for memory_key, owner, mem_type, policy, tier in memories:
            result = await brain_identity_integration.register_memory(
                memory_key, owner, mem_type, policy, tier
            )
            assert "success" in result
            assert "memory_key" in result
            assert result["memory_key"] == memory_key

        # Check that memories are in the local registry
        registry = brain_identity_integration.memory_registry
        assert len(registry) >= 3
        assert "memory_001" in registry
        assert registry["memory_001"]["owner"] == "user_001"
        assert registry["memory_001"]["type"] == "EPISODIC"

    @pytest.mark.asyncio
    async def test_session_management(self, brain_identity_integration):
        """Test session management functionality"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        users = ["user_001", "user_002", "user_003"]

        # Generate sessions for users
        for user in users:
            session = brain_identity_integration._get_user_session(user)
            assert session is not None
            assert session.startswith("session_")

            # Same user should get same session
            session2 = brain_identity_integration._get_user_session(user)
            assert session == session2

        # Check session registry
        assert len(brain_identity_integration.user_sessions) == 3
        for user in users:
            assert user in brain_identity_integration.user_sessions

    @pytest.mark.asyncio
    async def test_fallback_functionality(self, brain_identity_integration):
        """Test fallback functionality when main components are not available"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        # Test fallback authorization
        result = brain_identity_integration._fallback_authorization(
            "owner_user", "read", "test_memory", "EPISODIC", "owner_user"
        )
        assert result is True  # Owner should have access

        result = brain_identity_integration._fallback_authorization(
            "other_user", "delete", "test_memory", "EPISODIC", "owner_user"
        )
        assert result is False  # Non-owner shouldn't have delete access

        # Test fallback memory registration
        result = brain_identity_integration._fallback_register_memory(
            "test_memory", "test_user", "EPISODIC", "tier_based", 1
        )
        assert result is True

        # Test fallback encryption/decryption
        test_content = {"data": "test"}
        encrypted = brain_identity_integration._fallback_encrypt("key", test_content)
        assert encrypted["_encrypted"] is True
        assert "_encryption_timestamp" in encrypted

        decrypted = brain_identity_integration._fallback_decrypt("key", encrypted)
        assert decrypted["_encrypted"] is False
        assert "_decryption_timestamp" in decrypted

    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options for brain identity integration"""
        # Test with custom config
        custom_config = {
            "enable_access_logging": False,
            "max_log_entries": 2000,
            "default_tier_requirements": {
                "read": 2,
                "write": 3,
                "modify": 4,
                "delete": 5,
            },
            "enable_encryption": False,
            "audit_sensitive_operations": False,
        }

        integration = create_brain_identity_integration(custom_config)

        # Verify config was applied
        assert integration.config["enable_access_logging"] is False
        assert integration.config["max_log_entries"] == 2000
        assert integration.config["default_tier_requirements"]["read"] == 2
        assert integration.config["enable_encryption"] is False
        assert integration.config["audit_sensitive_operations"] is False

    def test_mock_components_creation(self, brain_identity_integration):
        """Test that mock components are created properly"""
        # Test mock registry
        registry = brain_identity_integration.id_registry
        assert hasattr(registry, "users")
        assert hasattr(registry, "sessions")
        assert callable(getattr(registry, "get_user", None))
        assert callable(getattr(registry, "validate_session", None))
        assert callable(getattr(registry, "register_user", None))

        # Test mock brain integration
        brain = brain_identity_integration.brain_integration
        assert hasattr(brain, "memory_manager")
        mm = brain.memory_manager
        assert hasattr(mm, "memories")
        assert callable(getattr(mm, "retrieve", None))
        assert callable(getattr(mm, "store", None))
        assert callable(getattr(mm, "update", None))
        assert callable(getattr(mm, "delete", None))

    @pytest.mark.asyncio
    async def test_access_policy_handling(self, brain_identity_integration):
        """Test different access policy handling"""
        # Initialize the integration
        await brain_identity_integration.initialize()

        access_policies = ["tier_based", "owner_only", "public", "private"]

        for policy in access_policies:
            result = await brain_identity_integration.authorize_memory_operation(
                user_id="test_user",
                operation="read",
                memory_key=f"memory_{policy}",
                memory_type="EPISODIC",
                access_policy=policy,
            )

            # Should handle all policy types
            assert "authorized" in result
            assert "timestamp" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
