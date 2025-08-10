"""Basic tests for LUKHAS core module functionality."""

import os
from unittest.mock import Mock, patch

import pytest

from core.plugin_registry import Plugin, PluginRegistry, PluginType


class TestCoreBasics:
    """Test basic core module functionality."""

    def test_plugin_registry_initialization(self):
        """Test that plugin registry initializes correctly."""
        registry = PluginRegistry()
        assert registry is not None

        # Should have all plugin types initialized
        all_plugins = registry.list_plugins()
        assert isinstance(all_plugins, list)

        # Each plugin type should be available
        for plugin_type in PluginType:
            type_plugins = registry.list_plugins(plugin_type)
            assert isinstance(type_plugins, list)

    def test_plugin_types_enum(self):
        """Test that all required plugin types are defined."""
        expected_types = {
            "ETHICS_POLICY",
            "MEMORY_HOOK",
            "ORCHESTRATION_AGENT",
            "SYMBOLIC_PROCESSOR",
        }

        actual_types = {pt.name for pt in PluginType}
        assert expected_types.issubset(actual_types)

    def test_plugin_base_class(self):
        """Test that Plugin base class has required abstract methods."""

        class TestPlugin(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.SYMBOLIC_PROCESSOR

            def get_plugin_name(self) -> str:
                return "test_plugin"

            def get_version(self) -> str:
                return "1.0.0"

        plugin = TestPlugin()
        assert plugin.get_plugin_type() == PluginType.SYMBOLIC_PROCESSOR
        assert plugin.get_plugin_name() == "test_plugin"
        assert plugin.get_version() == "1.0.0"

    def test_plugin_abstract_methods(self):
        """Test that Plugin abstract methods raise NotImplementedError."""
        with pytest.raises(TypeError):
            # Should not be able to instantiate abstract class directly
            Plugin()

    def test_plugin_registry_error_handling(self):
        """Test that plugin registry handles errors gracefully."""
        registry = PluginRegistry()

        # Getting non-existent plugin should return None
        result = registry.get_plugin(PluginType.ETHICS_POLICY, "nonexistent")
        assert result is None


class TestCoreIntegration:
    """Test core module integration points."""

    def test_core_module_imports(self):
        """Test that core module can be imported without errors."""
        # These should not raise import errors
        from config import settings
        from core.plugin_registry import PluginRegistry, PluginType

        assert PluginRegistry is not None
        assert PluginType is not None
        assert settings is not None

    def test_core_with_config_integration(self):
        """Test that core works with config system."""
        from config import settings, validate_optional_config
        from core.plugin_registry import PluginRegistry

        # Should be able to create registry with config available
        registry = PluginRegistry()
        status = validate_optional_config(settings)

        assert registry is not None
        assert isinstance(status, dict)

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_core_debug_mode(self):
        """Test core functionality in debug mode."""
        from config import Settings
        from core.plugin_registry import PluginRegistry

        debug_settings = Settings()
        registry = PluginRegistry()

        assert debug_settings.DEBUG is True
        assert registry is not None


class TestCorePluginSystem:
    """Test the core plugin system specifically."""

    def test_plugin_registration_workflow(self):
        """Test complete plugin registration workflow."""
        registry = PluginRegistry()

        # Create a test plugin
        class TestEthicsPlugin(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.ETHICS_POLICY

            def get_plugin_name(self) -> str:
                return "test_ethics"

            def get_version(self) -> str:
                return "1.0.0"

        plugin = TestEthicsPlugin()

        # Register plugin
        registry.register_plugin(plugin)

        # Verify registration
        retrieved = registry.get_plugin(PluginType.ETHICS_POLICY, "test_ethics")
        assert retrieved is plugin

        # Verify it appears in listings
        ethics_plugins = registry.list_plugins(PluginType.ETHICS_POLICY)
        assert plugin in ethics_plugins

        all_plugins = registry.list_plugins()
        assert plugin in all_plugins

    def test_multiple_plugins_same_type(self):
        """Test registering multiple plugins of the same type."""
        registry = PluginRegistry()

        class Plugin1(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.MEMORY_HOOK

            def get_plugin_name(self) -> str:
                return "plugin1"

            def get_version(self) -> str:
                return "1.0.0"

        class Plugin2(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.MEMORY_HOOK

            def get_plugin_name(self) -> str:
                return "plugin2"

            def get_version(self) -> str:
                return "1.0.0"

        plugin1 = Plugin1()
        plugin2 = Plugin2()

        registry.register_plugin(plugin1)
        registry.register_plugin(plugin2)

        # Both should be retrievable
        assert registry.get_plugin(PluginType.MEMORY_HOOK, "plugin1") is plugin1
        assert registry.get_plugin(PluginType.MEMORY_HOOK, "plugin2") is plugin2

        # Both should appear in type listing
        memory_plugins = registry.list_plugins(PluginType.MEMORY_HOOK)
        assert plugin1 in memory_plugins
        assert plugin2 in memory_plugins
        assert len(memory_plugins) >= 2

    def test_plugin_override(self):
        """Test that registering a plugin with same name overrides previous."""
        registry = PluginRegistry()

        class OriginalPlugin(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.SYMBOLIC_PROCESSOR

            def get_plugin_name(self) -> str:
                return "processor"

            def get_version(self) -> str:
                return "1.0.0"

        class UpdatedPlugin(Plugin):
            def get_plugin_type(self) -> PluginType:
                return PluginType.SYMBOLIC_PROCESSOR

            def get_plugin_name(self) -> str:
                return "processor"

            def get_version(self) -> str:
                return "2.0.0"

        original = OriginalPlugin()
        updated = UpdatedPlugin()

        registry.register_plugin(original)
        registry.register_plugin(updated)

        # Should get the updated plugin
        retrieved = registry.get_plugin(PluginType.SYMBOLIC_PROCESSOR, "processor")
        assert retrieved is updated
        assert retrieved.get_version() == "2.0.0"

    @patch("lukhas.core.plugin_registry.importlib.metadata.entry_points")
    def test_entry_point_loading(self, mock_entry_points):
        """Test loading plugins from entry points."""
        # Mock entry points
        mock_ep = Mock()
        mock_ep.name = "test_plugin"
        mock_ep.load.return_value = Mock

        mock_group = Mock()
        mock_group.select.return_value = [mock_ep]

        mock_entry_points.return_value = mock_group

        # This should attempt to load entry points without error
        registry = PluginRegistry()
        assert registry is not None


class TestCoreErrorHandling:
    """Test error handling in core systems."""

    def test_plugin_load_error_handling(self):
        """Test that plugin loading errors are handled gracefully."""
        with patch(
            "lukhas.core.plugin_registry.importlib.metadata.entry_points"
        ) as mock_ep:
            mock_ep.side_effect = Exception("Failed to load entry points")

            # Should not raise exception
            registry = PluginRegistry()
            assert registry is not None

    def test_malformed_plugin_handling(self):
        """Test handling of malformed plugins."""
        registry = PluginRegistry()

        # Try to register a malformed plugin
        class MalformedPlugin:
            pass

        malformed = MalformedPlugin()

        # Should handle gracefully or raise appropriate error
        with pytest.raises(AttributeError):
            registry.register_plugin(malformed)
