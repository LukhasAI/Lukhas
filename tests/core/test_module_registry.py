"""
Comprehensive Test Suite for Module Registry System
=================================================

Tests the central registry for all LUKHAS modules with tier-based access control.
This is a critical core component that manages module discovery, access control,
and tier-based gating across the entire LUKHAS system.

Test Coverage Areas:
- Module registration and discovery mechanisms
- Tier-based access control integration (levels 0-5)
- Automatic tier validation on module access
- Audit logging for all module operations
- Module health monitoring and dependency resolution
- Security and authentication integration
- Performance and scalability testing
"""
import pytest
import logging
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from dataclasses import dataclass

from core.module_registry import (
    ModuleRegistry,
    ModuleInfo,
    TierLevel,
    ModuleAccessError,
    TierValidationError,
    ModuleDependencyError,
    RegistryHealthMonitor,
    ModuleAuditLogger,
    ModuleMetrics,
)


class TestModuleRegistry:
    """Comprehensive test suite for the Module Registry system."""

    @pytest.fixture
    def registry(self):
        """Create a test registry instance."""
        return ModuleRegistry(
            enable_tier_validation=True,
            enable_audit_logging=True,
            health_check_interval=1.0,
            max_modules=1000
        )

    @pytest.fixture
    def sample_module_info(self):
        """Create sample module information."""
        return ModuleInfo(
            name="test_module",
            version="1.0.0",
            description="Test module for registry testing",
            tier_requirements=TierLevel.TIER_2,
            dependencies=["core", "common"],
            capabilities=["consciousness", "memory"],
            health_endpoint="/health",
            status="active"
        )

    @pytest.fixture
    def multiple_modules(self):
        """Create multiple test modules."""
        modules = []
        for i in range(5):
            module_info = ModuleInfo(
                name=f"test_module_{i}",
                version=f"1.{i}.0",
                description=f"Test module {i}",
                tier_requirements=TierLevel(i % 6),  # Tier 0-5 cycling
                dependencies=["core"] if i > 0 else [],
                capabilities=[f"capability_{i}"],
                health_endpoint=f"/health/{i}",
                status="active"
            )
            modules.append(module_info)
        return modules

    @pytest.fixture
    def mock_identity_service(self):
        """Mock identity service for tier validation."""
        mock_service = Mock()
        mock_service.get_user_tier.return_value = TierLevel.TIER_3
        mock_service.validate_tier_access.return_value = True
        return mock_service

    # Basic Registry Functionality Tests
    def test_registry_initialization(self, registry):
        """Test registry initializes with correct settings."""
        assert registry.enable_tier_validation is True
        assert registry.enable_audit_logging is True
        assert registry.health_check_interval == 1.0
        assert registry.max_modules == 1000
        assert registry.module_count == 0
        assert isinstance(registry.health_monitor, RegistryHealthMonitor)
        assert isinstance(registry.audit_logger, ModuleAuditLogger)

    def test_module_registration(self, registry, sample_module_info):
        """Test basic module registration."""
        # Register module
        registration_id = registry.register_module(sample_module_info)
        
        # Verify registration
        assert registration_id is not None
        assert registry.module_count == 1
        assert registry.is_module_registered("test_module") is True
        
        # Retrieve module info
        retrieved_info = registry.get_module_info("test_module")
        assert retrieved_info.name == sample_module_info.name
        assert retrieved_info.version == sample_module_info.version

    def test_module_deregistration(self, registry, sample_module_info):
        """Test module deregistration."""
        # Register and then deregister
        registration_id = registry.register_module(sample_module_info)
        assert registry.is_module_registered("test_module") is True
        
        # Deregister
        success = registry.deregister_module("test_module")
        assert success is True
        assert registry.is_module_registered("test_module") is False
        assert registry.module_count == 0

    def test_duplicate_registration_prevention(self, registry, sample_module_info):
        """Test prevention of duplicate module registration."""
        # Register module
        first_id = registry.register_module(sample_module_info)
        assert first_id is not None
        
        # Attempt duplicate registration
        with pytest.raises(ValueError, match="already registered"):
            registry.register_module(sample_module_info)

    def test_module_discovery(self, registry, multiple_modules):
        """Test module discovery functionality."""
        # Register multiple modules
        for module_info in multiple_modules:
            registry.register_module(module_info)
        
        # Test discovery by capability
        consciousness_modules = registry.discover_modules_by_capability("capability_0")
        assert len(consciousness_modules) == 1
        assert consciousness_modules[0].name == "test_module_0"
        
        # Test discovery by tier
        tier_2_modules = registry.discover_modules_by_tier(TierLevel.TIER_2)
        expected_count = sum(1 for m in multiple_modules if m.tier_requirements == TierLevel.TIER_2)
        assert len(tier_2_modules) == expected_count

    def test_module_search(self, registry, multiple_modules):
        """Test module search functionality."""
        # Register modules
        for module_info in multiple_modules:
            registry.register_module(module_info)
        
        # Search by name pattern
        test_modules = registry.search_modules("test_module_*")
        assert len(test_modules) == len(multiple_modules)
        
        # Search by description
        specific_modules = registry.search_modules("Test module 1")
        assert len(specific_modules) == 1
        assert specific_modules[0].name == "test_module_1"

    # Tier-Based Access Control Tests
    def test_tier_validation_enabled(self, registry, sample_module_info, mock_identity_service):
        """Test tier validation when enabled."""
        with patch('core.module_registry.get_identity_service', return_value=mock_identity_service):
            # Set module to require Tier 2
            sample_module_info.tier_requirements = TierLevel.TIER_2
            registry.register_module(sample_module_info)
            
            # Test access with sufficient tier (Tier 3 > Tier 2)
            access_granted = registry.validate_module_access("test_module", user_id="test_user")
            assert access_granted is True
            
            # Test access with insufficient tier
            mock_identity_service.get_user_tier.return_value = TierLevel.TIER_1
            access_granted = registry.validate_module_access("test_module", user_id="test_user")
            assert access_granted is False

    def test_tier_validation_disabled(self, sample_module_info):
        """Test behavior when tier validation is disabled."""
        registry = ModuleRegistry(enable_tier_validation=False)
        registry.register_module(sample_module_info)
        
        # Access should be granted regardless of tier
        access_granted = registry.validate_module_access("test_module", user_id="test_user")
        assert access_granted is True

    def test_tier_elevation_support(self, registry, sample_module_info, mock_identity_service):
        """Test temporary tier elevation support."""
        with patch('core.module_registry.get_identity_service', return_value=mock_identity_service):
            # Set high tier requirement
            sample_module_info.tier_requirements = TierLevel.TIER_5
            registry.register_module(sample_module_info)
            
            # Set user to low tier
            mock_identity_service.get_user_tier.return_value = TierLevel.TIER_1
            
            # Test normal access (should fail)
            access_granted = registry.validate_module_access("test_module", user_id="test_user")
            assert access_granted is False
            
            # Test with tier elevation
            mock_identity_service.validate_tier_elevation.return_value = True
            access_granted = registry.validate_module_access(
                "test_module", 
                user_id="test_user",
                temporary_elevation=TierLevel.TIER_5,
                elevation_reason="emergency_access"
            )
            assert access_granted is True

    def test_tier_validation_error_handling(self, registry, sample_module_info):
        """Test tier validation error handling."""
        registry.register_module(sample_module_info)
        
        # Test with invalid user
        with pytest.raises(TierValidationError):
            registry.validate_module_access("test_module", user_id="nonexistent_user")
        
        # Test with nonexistent module
        with pytest.raises(ModuleAccessError):
            registry.validate_module_access("nonexistent_module", user_id="test_user")

    # Audit Logging Tests
    def test_audit_logging_enabled(self, registry, sample_module_info):
        """Test audit logging when enabled."""
        with patch.object(registry.audit_logger, 'log_module_access') as mock_log:
            registry.register_module(sample_module_info)
            
            # Access module
            registry.validate_module_access("test_module", user_id="test_user")
            
            # Verify audit log was called
            mock_log.assert_called_once()
            call_args = mock_log.call_args[0]
            assert call_args[0] == "test_module"
            assert call_args[1] == "test_user"

    def test_audit_logging_disabled(self, sample_module_info):
        """Test behavior when audit logging is disabled."""
        registry = ModuleRegistry(enable_audit_logging=False)
        
        with patch.object(registry.audit_logger, 'log_module_access') as mock_log:
            registry.register_module(sample_module_info)
            registry.validate_module_access("test_module", user_id="test_user")
            
            # Verify audit log was not called
            mock_log.assert_not_called()

    def test_comprehensive_audit_trail(self, registry, sample_module_info):
        """Test comprehensive audit trail functionality."""
        audit_events = []
        
        def capture_audit_event(module_name, user_id, action, result, **kwargs):
            audit_events.append({
                'module': module_name,
                'user': user_id,
                'action': action,
                'result': result,
                'timestamp': datetime.now(timezone.utc),
                **kwargs
            })
        
        with patch.object(registry.audit_logger, 'log_module_access', side_effect=capture_audit_event):
            # Register module
            registry.register_module(sample_module_info)
            
            # Multiple access attempts
            registry.validate_module_access("test_module", user_id="user1")
            registry.validate_module_access("test_module", user_id="user2")
            
            # Verify audit trail
            assert len(audit_events) == 2
            assert audit_events[0]['user'] == "user1"
            assert audit_events[1]['user'] == "user2"

    # Module Health Monitoring Tests
    def test_health_monitoring(self, registry, sample_module_info):
        """Test module health monitoring."""
        registry.register_module(sample_module_info)
        
        # Test health check
        health_status = registry.check_module_health("test_module")
        assert health_status is not None
        assert health_status.get('status') in ['healthy', 'unhealthy', 'unknown']

    def test_health_monitoring_with_endpoint(self, registry, sample_module_info):
        """Test health monitoring with custom endpoint."""
        # Mock HTTP response for health check
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'status': 'healthy', 'uptime': 3600}
            mock_get.return_value = mock_response
            
            registry.register_module(sample_module_info)
            health_status = registry.check_module_health("test_module")
            
            assert health_status['status'] == 'healthy'
            assert health_status['uptime'] == 3600

    def test_unhealthy_module_detection(self, registry, sample_module_info):
        """Test detection of unhealthy modules."""
        with patch('requests.get') as mock_get:
            # Simulate failed health check
            mock_get.side_effect = Exception("Connection failed")
            
            registry.register_module(sample_module_info)
            health_status = registry.check_module_health("test_module")
            
            assert health_status['status'] == 'unhealthy'

    def test_periodic_health_monitoring(self, registry, sample_module_info):
        """Test periodic health monitoring."""
        registry.register_module(sample_module_info)
        
        # Start health monitoring
        registry.start_health_monitoring()
        
        # Wait for at least one health check cycle
        time.sleep(1.5)
        
        # Stop monitoring
        registry.stop_health_monitoring()
        
        # Verify health monitoring occurred
        health_history = registry.get_health_history("test_module")
        assert len(health_history) > 0

    # Dependency Resolution Tests
    def test_dependency_resolution(self, registry):
        """Test module dependency resolution."""
        # Create modules with dependencies
        core_module = ModuleInfo(
            name="core",
            version="1.0.0",
            description="Core module",
            tier_requirements=TierLevel.TIER_0,
            dependencies=[],
            capabilities=["foundation"],
            health_endpoint="/health",
            status="active"
        )
        
        dependent_module = ModuleInfo(
            name="dependent",
            version="1.0.0",
            description="Dependent module",
            tier_requirements=TierLevel.TIER_1,
            dependencies=["core"],
            capabilities=["advanced"],
            health_endpoint="/health",
            status="active"
        )
        
        # Register core module first
        registry.register_module(core_module)
        
        # Register dependent module
        registry.register_module(dependent_module)
        
        # Test dependency resolution
        dependencies = registry.resolve_dependencies("dependent")
        assert "core" in dependencies
        assert len(dependencies) == 1

    def test_circular_dependency_detection(self, registry):
        """Test circular dependency detection."""
        module_a = ModuleInfo(
            name="module_a",
            version="1.0.0",
            description="Module A",
            tier_requirements=TierLevel.TIER_0,
            dependencies=["module_b"],
            capabilities=["a"],
            health_endpoint="/health",
            status="active"
        )
        
        module_b = ModuleInfo(
            name="module_b",
            version="1.0.0",
            description="Module B",
            tier_requirements=TierLevel.TIER_0,
            dependencies=["module_a"],
            capabilities=["b"],
            health_endpoint="/health",
            status="active"
        )
        
        # Register first module
        registry.register_module(module_a)
        
        # Attempt to register second module with circular dependency
        with pytest.raises(ModuleDependencyError, match="circular dependency"):
            registry.register_module(module_b)

    def test_missing_dependency_detection(self, registry):
        """Test missing dependency detection."""
        dependent_module = ModuleInfo(
            name="dependent",
            version="1.0.0",
            description="Dependent module",
            tier_requirements=TierLevel.TIER_1,
            dependencies=["nonexistent_module"],
            capabilities=["advanced"],
            health_endpoint="/health",
            status="active"
        )
        
        # Attempt to register module with missing dependency
        with pytest.raises(ModuleDependencyError, match="missing dependency"):
            registry.register_module(dependent_module)

    # Performance and Scalability Tests
    def test_large_scale_registration(self, registry):
        """Test registration performance with many modules."""
        start_time = time.time()
        
        # Register many modules
        for i in range(100):
            module_info = ModuleInfo(
                name=f"module_{i}",
                version="1.0.0",
                description=f"Module {i}",
                tier_requirements=TierLevel.TIER_0,
                dependencies=[],
                capabilities=[f"capability_{i}"],
                health_endpoint=f"/health/{i}",
                status="active"
            )
            registry.register_module(module_info)
        
        registration_time = time.time() - start_time
        
        # Verify performance
        assert registry.module_count == 100
        assert registration_time < 5.0  # Should complete in reasonable time

    def test_concurrent_access(self, registry, multiple_modules):
        """Test concurrent registry access."""
        registration_results = []
        access_results = []
        
        def register_modules():
            for module_info in multiple_modules:
                try:
                    reg_id = registry.register_module(module_info)
                    registration_results.append(reg_id)
                except Exception as e:
                    registration_results.append(None)
        
        def access_modules():
            for _ in range(10):
                for module_info in multiple_modules:
                    try:
                        access_granted = registry.validate_module_access(
                            module_info.name, 
                            user_id="test_user"
                        )
                        access_results.append(access_granted)
                    except Exception:
                        access_results.append(False)
        
        # Start concurrent operations
        register_thread = threading.Thread(target=register_modules)
        access_thread = threading.Thread(target=access_modules)
        
        register_thread.start()
        access_thread.start()
        
        register_thread.join()
        access_thread.join()
        
        # Verify concurrent operations completed
        assert len(registration_results) == len(multiple_modules)
        assert len(access_results) > 0

    def test_memory_usage_monitoring(self, registry, multiple_modules):
        """Test memory usage monitoring."""
        # Register modules
        for module_info in multiple_modules:
            registry.register_module(module_info)
        
        # Get memory metrics
        memory_stats = registry.get_memory_statistics()
        
        assert memory_stats['module_count'] == len(multiple_modules)
        assert memory_stats['memory_usage_bytes'] > 0

    # Configuration and Customization Tests
    def test_custom_tier_validation(self, registry):
        """Test custom tier validation logic."""
        custom_validation_called = False
        
        def custom_tier_validator(module_name, user_id, required_tier):
            nonlocal custom_validation_called
            custom_validation_called = True
            return user_id == "admin"  # Only admin has access
        
        registry.set_custom_tier_validator(custom_tier_validator)
        
        sample_module = ModuleInfo(
            name="custom_module",
            version="1.0.0",
            description="Custom module",
            tier_requirements=TierLevel.TIER_5,
            dependencies=[],
            capabilities=["custom"],
            health_endpoint="/health",
            status="active"
        )
        
        registry.register_module(sample_module)
        
        # Test custom validation
        admin_access = registry.validate_module_access("custom_module", user_id="admin")
        user_access = registry.validate_module_access("custom_module", user_id="user")
        
        assert custom_validation_called is True
        assert admin_access is True
        assert user_access is False

    def test_registry_configuration_validation(self):
        """Test registry configuration validation."""
        # Test invalid configuration
        with pytest.raises(ValueError):
            ModuleRegistry(
                max_modules=-1,  # Invalid negative value
                health_check_interval=0.0,  # Invalid zero interval
            )

    def test_module_info_validation(self, registry):
        """Test module information validation."""
        # Test invalid module info
        invalid_module = ModuleInfo(
            name="",  # Invalid empty name
            version="invalid-version",  # Invalid version format
            description="Test module",
            tier_requirements=TierLevel.TIER_0,
            dependencies=[],
            capabilities=[],
            health_endpoint="invalid-endpoint",  # Invalid endpoint format
            status="invalid_status"  # Invalid status
        )
        
        with pytest.raises(ValueError):
            registry.register_module(invalid_module)

    # Integration Tests
    def test_identity_service_integration(self, registry, sample_module_info):
        """Test integration with identity service."""
        with patch('core.module_registry.get_identity_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_user_tier.return_value = TierLevel.TIER_3
            mock_service.validate_tier_access.return_value = True
            mock_get_service.return_value = mock_service
            
            registry.register_module(sample_module_info)
            
            # Test integration
            access_granted = registry.validate_module_access("test_module", user_id="test_user")
            assert access_granted is True
            
            # Verify identity service was called
            mock_service.get_user_tier.assert_called_with("test_user")

    def test_metrics_integration(self, registry, sample_module_info):
        """Test integration with metrics system."""
        with patch('core.module_registry.get_metrics_client') as mock_get_metrics:
            mock_metrics = Mock()
            mock_get_metrics.return_value = mock_metrics
            
            registry.register_module(sample_module_info)
            registry.validate_module_access("test_module", user_id="test_user")
            
            # Verify metrics were recorded
            mock_metrics.increment.assert_called()

    def test_full_system_integration(self, registry, multiple_modules, mock_identity_service):
        """Test full system integration scenario."""
        with patch('core.module_registry.get_identity_service', return_value=mock_identity_service):
            # Register all modules
            for module_info in multiple_modules:
                registry.register_module(module_info)
            
            # Start health monitoring
            registry.start_health_monitoring()
            
            # Simulate various operations
            operations_results = []
            
            # Test discovery
            tier_0_modules = registry.discover_modules_by_tier(TierLevel.TIER_0)
            operations_results.append(len(tier_0_modules))
            
            # Test access validation
            for module_info in multiple_modules:
                access_granted = registry.validate_module_access(
                    module_info.name, 
                    user_id="test_user"
                )
                operations_results.append(access_granted)
            
            # Test dependency resolution
            for module_info in multiple_modules:
                if module_info.dependencies:
                    deps = registry.resolve_dependencies(module_info.name)
                    operations_results.append(len(deps))
            
            # Stop health monitoring
            registry.stop_health_monitoring()
            
            # Verify comprehensive integration
            assert len(operations_results) > 0
            assert registry.module_count == len(multiple_modules)

    # Error Handling and Recovery Tests
    def test_registry_error_recovery(self, registry, sample_module_info):
        """Test registry error recovery mechanisms."""
        # Simulate registry corruption
        registry._modules = None
        
        # Test recovery
        registry.recover_from_corruption()
        
        # Verify recovery
        assert registry._modules is not None
        
        # Test module registration after recovery
        registration_id = registry.register_module(sample_module_info)
        assert registration_id is not None

    def test_graceful_shutdown(self, registry, sample_module_info):
        """Test graceful registry shutdown."""
        # Set up registry with active operations
        registry.register_module(sample_module_info)
        registry.start_health_monitoring()
        
        # Test graceful shutdown
        registry.shutdown(graceful=True, timeout=5.0)
        
        # Verify shutdown
        assert registry.is_running is False

    # Cleanup and Resource Management Tests
    def test_registry_cleanup(self, registry, multiple_modules):
        """Test registry resource cleanup."""
        # Register modules and start monitoring
        for module_info in multiple_modules:
            registry.register_module(module_info)
        
        registry.start_health_monitoring()
        
        # Test cleanup
        registry.cleanup()
        
        # Verify cleanup
        assert registry.module_count == 0
        assert registry.is_running is False

    def test_memory_leak_prevention(self, registry):
        """Test memory leak prevention."""
        initial_memory = registry.get_memory_statistics()['memory_usage_bytes']
        
        # Register and deregister many modules
        for i in range(100):
            module_info = ModuleInfo(
                name=f"temp_module_{i}",
                version="1.0.0",
                description=f"Temporary module {i}",
                tier_requirements=TierLevel.TIER_0,
                dependencies=[],
                capabilities=[f"temp_{i}"],
                health_endpoint=f"/health/{i}",
                status="active"
            )
            
            registry.register_module(module_info)
            registry.deregister_module(f"temp_module_{i}")
        
        final_memory = registry.get_memory_statistics()['memory_usage_bytes']
        
        # Verify no significant memory increase
        memory_increase = final_memory - initial_memory
        assert memory_increase < 1024 * 1024  # Less than 1MB increase