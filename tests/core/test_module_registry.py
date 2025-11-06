from unittest.mock import Mock, patch

import pytest

from core.module_registry import ModuleInfo, ModuleRegistry, TierLevel


class TestModuleRegistry:
    @pytest.fixture
    def registry(self):
        """Create a test registry instance."""
        return ModuleRegistry()
    def test_initialization(self):
        """Registry initializes with empty state"""
        registry = ModuleRegistry()
        assert len(registry.modules) == 0

    def test_register_module(self, registry):
        """Can register a module with metadata"""
        module_info = ModuleInfo(
            module_id="test_module",
            name="Test Module",
            version="1.0.0",
            path="test.module",
            instance=Mock(),
            min_tier=TierLevel.GUEST,
        )
        registry.register_module(
            module_id="test_module",
            module_instance=module_info.instance,
            name=module_info.name,
            version=module_info.version,
            path=module_info.path,
            min_tier=module_info.min_tier,
        )
        assert "test_module" in registry.modules

    def test_duplicate_registration_raises(self, registry):
        """Registering same module twice raises error"""
        module_info = ModuleInfo(
            module_id="test_module",
            name="Test Module",
            version="1.0.0",
            path="test.module",
            instance=Mock(),
            min_tier=TierLevel.GUEST,
        )
        registry.register_module(
            module_id="test_module",
            module_instance=module_info.instance,
            name=module_info.name,
            version=module_info.version,
            path=module_info.path,
            min_tier=module_info.min_tier,
        )
        with pytest.raises(ValueError):
            registry.register_module(
                module_id="test_module",
                module_instance=module_info.instance,
                name=module_info.name,
                version=module_info.version,
                path=module_info.path,
                min_tier=module_info.min_tier,
            )

    @patch('core.module_registry.TIER_SYSTEM_AVAILABLE', True)
    def test_get_module_success(self, registry):
        """Can get a module instance with sufficient tier."""
        registry.identity_client = Mock()
        registry.identity_client.verify_user_access.return_value = True
        module_instance = Mock()
        registry.register_module(
            module_id="test_module",
            module_instance=module_instance,
            name="Test Module",
            version="1.0.0",
            path="test.module",
            min_tier=TierLevel.GUEST,
        )
        module = registry.get_module("test_module", "test_user")
        assert module == module_instance
        registry.identity_client.verify_user_access.assert_called_once()

    @patch('core.module_registry.TIER_SYSTEM_AVAILABLE', True)
    def test_get_module_tier_denied(self, registry):
        """Access is denied if user tier is too low."""
        registry.identity_client = Mock()
        registry.identity_client.verify_user_access.return_value = False
        registry.register_module(
            module_id="test_module",
            module_instance=Mock(),
            name="Test Module",
            version="1.0.0",
            path="test.module",
            min_tier=TierLevel.TRUSTED,
        )
        module = registry.get_module("test_module", "test_user")
        assert module is None

    @patch('core.module_registry.TIER_SYSTEM_AVAILABLE', True)
    def test_list_modules(self, registry):
        """Can list modules, filtering by tier."""
        registry.identity_client = Mock()
        registry.register_module("module1", Mock(), "Module 1", "1.0", "mod1", min_tier=TierLevel.GUEST)
        registry.register_module("module2", Mock(), "Module 2", "1.0", "mod2", min_tier=TierLevel.TRUSTED)

        # User with low tier
        registry.identity_client.verify_user_access.side_effect = lambda user, tier: tier == f"LAMBDA_TIER_{TierLevel.GUEST}"
        modules = registry.list_modules("low_tier_user")
        assert len(modules) == 1
        assert modules[0]["module_id"] == "module1"

        # User with high tier
        registry.identity_client.verify_user_access.side_effect = lambda user, tier: True
        modules = registry.list_modules("high_tier_user")
        assert len(modules) == 2

    def test_get_module_health(self, registry):
        """Can get module health status."""
        registry.register_module("test_module", Mock(), "Test Module", "1.0", "test.path")
        health = registry.get_module_health("test_module")
        assert health["health_status"] == "healthy"
        assert health["module_id"] == "test_module"

    def test_shutdown(self, registry):
        """Shutdown clears modules and logs audit."""
        registry.register_module("test_module", Mock(), "Test Module", "1.0", "test.path")
        registry.shutdown()
        assert len(registry.modules) == 0
        assert registry.audit_log[-1]["action"] == "registry_shutdown"
