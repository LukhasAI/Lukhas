#!/usr/bin/env python3
"""
Entry point discovery smoke tests.
Minimal testing that patches only the entry point list, not the classes.
Uses concrete sample classes, not mocks.
"""

import pytest
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lukhas.core.registry import _REG, discover_entry_points, _instantiate_plugin


class SampleNode:
    """Concrete sample node for testing."""

    def __init__(self, name=None):
        self.name = name or "sample"

    def process(self, context):
        return {"result": f"processed by {self.name}"}


class SampleAdapter:
    """Concrete sample adapter for testing."""

    def __init__(self, name=None):
        self.name = name or "sample_adapter"

    def connect(self):
        return f"connected to {self.name}"


class SampleMonitor:
    """Concrete sample monitor for testing."""

    def __init__(self, name=None):
        self.name = name or "sample_monitor"

    def collect(self):
        return f"monitoring {self.name}"


class SampleFactoryNode:
    """Sample node with factory method."""

    def __init__(self, name=None):
        self.name = name or "factory_default"

    @classmethod
    def from_entry_point(cls, name=None):
        return cls(name=f"factory_{name}")

    def process(self, context):
        return {"result": f"factory processed by {self.name}"}


class ConfigBasedNode:
    """Node that takes a config dictionary."""

    def __init__(self, config=None):
        self.config = config or {}
        self.name = self.config.get("name", "config_default")

    def process(self, context):
        return {"result": f"config processed by {self.name}"}


class RequiredArgNode:
    """Node that requires a mandatory argument."""

    def __init__(self, required_param):
        self.required_param = required_param
        self.name = f"required_{required_param}"

    def process(self, context):
        return {"result": f"required processed by {self.name}"}


class VarKwargsNode:
    """Node that accepts **kwargs."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.name = kwargs.get("name", "kwargs_default")

    def process(self, context):
        return {"result": f"kwargs processed by {self.name}"}


class MultipleDefaultsNode:
    """Node with multiple parameters that all have defaults."""

    def __init__(self, param1="default1", param2="default2", name="multi_default"):
        self.param1 = param1
        self.param2 = param2
        self.name = name

    def process(self, context):
        return {"result": f"multi processed by {self.name}"}


class NoInitNode:
    """Node without __init__ method."""

    name = "no_init_default"

    def process(self, context):
        return {"result": f"no_init processed by {self.name}"}


class CreateFactoryNode:
    """Node with 'create' factory method."""

    def __init__(self, identifier=None):
        self.identifier = identifier or "create_default"

    @classmethod
    def create(cls):
        return cls("created_instance")

    def process(self, context):
        return {"result": f"create processed by {self.identifier}"}


class FailingFactoryNode:
    """Node with factory method that fails."""

    def __init__(self, name=None):
        self.name = name or "failing_default"

    @classmethod
    def from_entry_point(cls, name=None):
        raise ValueError("Factory intentionally fails")

    @classmethod
    def build(cls):
        return cls("built_instance")

    def process(self, context):
        return {"result": f"failing processed by {self.name}"}


class _EP(SimpleNamespace):
    """Simple entry point object: .name, .load()"""

    def load(self):
        return self.target


class TestEntryPointsSmoke:
    """Smoke tests for entry point discovery."""

    def setup_method(self):
        """Clear registry before each test."""
        _REG.clear()

    def test_entry_point_discovery_smoke(self, monkeypatch):
        """Test basic entry point discovery with concrete nodes."""
        eps = [
            _EP(name="memory", target=SampleNode),
            _EP(name="thought", target=SampleNode),
        ]

        def fake_entry_points(group=None):
            return eps if group == "lukhas.cognitive_nodes" else []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                discover_entry_points()

        assert "node:memory" in _REG and "node:thought" in _REG
        assert isinstance(_REG["node:memory"], SampleNode)
        assert isinstance(_REG["node:thought"], SampleNode)
        assert _REG["node:memory"].name == "memory"
        assert _REG["node:thought"].name == "thought"

    def test_multiple_group_discovery(self, monkeypatch):
        """Test discovery across multiple entry point groups."""
        cognitive_eps = [_EP(name="memory", target=SampleNode)]
        adapter_eps = [_EP(name="gmail", target=SampleAdapter)]
        monitor_eps = [_EP(name="metrics", target=SampleMonitor)]

        def fake_entry_points(group=None):
            if group == "lukhas.cognitive_nodes":
                return cognitive_eps
            elif group == "lukhas.adapters":
                return adapter_eps
            elif group == "lukhas.monitoring":
                return monitor_eps
            return []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                discover_entry_points()

        # All should be registered with correct prefixes
        assert "node:memory" in _REG
        assert "adapter:gmail" in _REG
        assert "monitor:metrics" in _REG

        # Verify correct types and names
        assert isinstance(_REG["node:memory"], SampleNode)
        assert isinstance(_REG["adapter:gmail"], SampleAdapter)
        assert isinstance(_REG["monitor:metrics"], SampleMonitor)

        assert _REG["node:memory"].name == "memory"
        assert _REG["adapter:gmail"].name == "gmail"
        assert _REG["monitor:metrics"].name == "metrics"

    def test_factory_method_discovery(self, monkeypatch):
        """Test discovery with factory method nodes."""
        eps = [_EP(name="factory_test", target=SampleFactoryNode)]

        def fake_entry_points(group=None):
            return eps if group == "lukhas.cognitive_nodes" else []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                discover_entry_points()

        assert "node:factory_test" in _REG
        node = _REG["node:factory_test"]
        assert isinstance(node, SampleFactoryNode)
        assert node.name == "factory_factory_test"  # from_entry_point prefixes with "factory_"

    def test_legacy_alias_group_discovery(self, monkeypatch):
        """Test that legacy group names are properly aliased."""
        eps = [_EP(name="legacy_memory", target=SampleNode)]

        def fake_entry_points(group=None):
            # Only respond to the resolved group name
            return eps if group == "lukhas.cognitive_nodes" else []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                # Manually test the alias by calling discover with legacy groups
                from lukhas.core.registry import ALIASES
                # Verify alias exists
                assert "lukhas.agi_nodes" in ALIASES
                assert ALIASES["lukhas.agi_nodes"] == "lukhas.cognitive_nodes"
                discover_entry_points()

        # Should still register under the standard prefix
        assert "node:legacy_memory" in _REG
        assert isinstance(_REG["node:legacy_memory"], SampleNode)

    def test_discovery_disabled_by_default(self, monkeypatch):
        """Test that discovery is disabled by default."""
        eps = [_EP(name="should_not_load", target=SampleNode)]

        def fake_entry_points(group=None):
            return eps

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            # Don't set LUKHAS_PLUGIN_DISCOVERY - should default to "off"
            discover_entry_points()

        # Should not have loaded anything
        assert len(_REG) == 0

    def test_discovery_error_handling(self, monkeypatch):
        """Test that discovery errors are handled gracefully."""

        class FailingNode:
            def __init__(self, required_arg):  # Will fail without args
                self.required_arg = required_arg

        eps = [
            _EP(name="good", target=SampleNode),
            _EP(name="bad", target=FailingNode),
        ]

        def fake_entry_points(group=None):
            return eps if group == "lukhas.cognitive_nodes" else []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                # Should not raise exception despite failing node
                discover_entry_points()

        # Good node should be registered as instance, bad node now also instantiated
        assert "node:good" in _REG
        assert "node:bad" in _REG  # T4/0.01%: Enhanced instantiation handles this now
        assert isinstance(_REG["node:good"], SampleNode)
        # Enhanced instantiation now successfully creates instance with required param
        assert isinstance(_REG["node:bad"], FailingNode)

    def test_instantiate_plugin_directly(self):
        """Test the _instantiate_plugin function directly."""
        # Test with SampleNode (name parameter)
        obj1 = _instantiate_plugin("test1", SampleNode)
        assert isinstance(obj1, SampleNode)
        assert obj1.name == "test1"

        # Test with SampleFactoryNode (factory method)
        obj2 = _instantiate_plugin("test2", SampleFactoryNode)
        assert isinstance(obj2, SampleFactoryNode)
        assert obj2.name == "factory_test2"

        # Test with problematic class (should return class itself)
        class ProblematicClass:
            def __init__(self, required1, required2):
                pass

        obj3 = _instantiate_plugin("test3", ProblematicClass)
        assert obj3 is ProblematicClass

    def test_enhanced_instantiation_edge_cases(self):
        """Test enhanced _instantiate_plugin with comprehensive edge cases."""

        # Test 1: Config-based node
        config_obj = _instantiate_plugin("config_test", ConfigBasedNode)
        assert isinstance(config_obj, ConfigBasedNode)
        assert config_obj.name == "config_test"  # Should pass name in config

        # Test 2: Required argument node (should instantiate with name as required param)
        required_obj = _instantiate_plugin("required_test", RequiredArgNode)
        assert isinstance(required_obj, RequiredArgNode)
        assert required_obj.name == "required_required_test"  # Name passed as required param

        # Test 3: **kwargs node
        kwargs_obj = _instantiate_plugin("kwargs_test", VarKwargsNode)
        assert isinstance(kwargs_obj, VarKwargsNode)
        assert kwargs_obj.name == "kwargs_test"

        # Test 4: Multiple defaults node
        multi_obj = _instantiate_plugin("multi_test", MultipleDefaultsNode)
        assert isinstance(multi_obj, MultipleDefaultsNode)
        assert multi_obj.name == "multi_test"

        # Test 5: No __init__ method (should use default constructor)
        no_init_obj = _instantiate_plugin("no_init_test", NoInitNode)
        assert isinstance(no_init_obj, NoInitNode)
        assert no_init_obj.name == "no_init_default"

        # Test 6: Create factory method
        create_obj = _instantiate_plugin("create_test", CreateFactoryNode)
        assert isinstance(create_obj, CreateFactoryNode)
        assert create_obj.identifier == "created_instance"

        # Test 7: Failing factory method (should fallback to second factory)
        failing_obj = _instantiate_plugin("failing_test", FailingFactoryNode)
        assert isinstance(failing_obj, FailingFactoryNode)
        assert failing_obj.name == "built_instance"  # Used 'build' factory

    def test_enhanced_discovery_with_edge_cases(self, monkeypatch):
        """Test discovery with the enhanced instantiation edge cases."""
        eps = [
            _EP(name="config", target=ConfigBasedNode),
            _EP(name="kwargs", target=VarKwargsNode),
            _EP(name="multi", target=MultipleDefaultsNode),
            _EP(name="failing", target=FailingFactoryNode),
        ]

        def fake_entry_points(group=None):
            return eps if group == "lukhas.cognitive_nodes" else []

        with patch("lukhas.core.registry.entry_points", side_effect=fake_entry_points):
            with monkeypatch.context() as m:
                m.setenv("LUKHAS_PLUGIN_DISCOVERY", "auto")
                discover_entry_points()

        # Verify all plugins were registered with correct instantiation
        assert "node:config" in _REG
        assert "node:kwargs" in _REG
        assert "node:multi" in _REG
        assert "node:failing" in _REG

        # Verify correct instantiation happened
        config_instance = _REG["node:config"]
        assert isinstance(config_instance, ConfigBasedNode)
        assert config_instance.name == "config"

        kwargs_instance = _REG["node:kwargs"]
        assert isinstance(kwargs_instance, VarKwargsNode)
        assert kwargs_instance.name == "kwargs"

        multi_instance = _REG["node:multi"]
        assert isinstance(multi_instance, MultipleDefaultsNode)
        assert multi_instance.name == "multi"

        failing_instance = _REG["node:failing"]
        assert isinstance(failing_instance, FailingFactoryNode)
        assert failing_instance.name == "built_instance"  # Fallback factory used

    def test_registry_kind_helper(self):
        """Test the _register_kind helper function."""
        from lukhas.core.registry import _register_kind

        # Clear registry for clean test
        _REG.clear()

        # Test standard group mappings
        _register_kind("lukhas.cognitive_nodes", "test_node", SampleNode())
        assert "node:test_node" in _REG

        _register_kind("lukhas.constellation_components", "test_comp", SampleAdapter())
        assert "constellation:test_comp" in _REG

        _register_kind("lukhas.adapters", "test_adapter", SampleAdapter())
        assert "adapter:test_adapter" in _REG

        _register_kind("lukhas.monitoring", "test_monitor", SampleMonitor())
        assert "monitor:test_monitor" in _REG

        # Test unknown group (should use last part of group name)
        _register_kind("lukhas.unknown.custom", "test_custom", SampleNode())
        assert "custom:test_custom" in _REG

        # Test group without dots
        _register_kind("simple", "test_simple", SampleNode())
        assert "simple:test_simple" in _REG

    def test_constructor_signature_patterns(self):
        """Test specific constructor signature patterns handled by enhanced instantiation."""

        # Pattern 1: Options parameter
        class OptionsNode:
            def __init__(self, options=None):
                self.options = options or {}
                self.name = self.options.get("name", "options_default")

        options_obj = _instantiate_plugin("options_test", OptionsNode)
        assert isinstance(options_obj, OptionsNode)
        assert options_obj.name == "options_test"

        # Pattern 2: Settings parameter
        class SettingsNode:
            def __init__(self, settings=None):
                self.settings = settings or {}
                self.name = self.settings.get("name", "settings_default")

        settings_obj = _instantiate_plugin("settings_test", SettingsNode)
        assert isinstance(settings_obj, SettingsNode)
        assert settings_obj.name == "settings_test"

        # Pattern 3: Mixed args with defaults
        class MixedNode:
            def __init__(self, required, optional="default", name="mixed"):
                self.required = required
                self.optional = optional
                self.name = name

        mixed_obj = _instantiate_plugin("mixed_test", MixedNode)
        assert mixed_obj is MixedNode  # Can't instantiate due to required param without default

        # Pattern 4: Varargs and kwargs
        class VarNode:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
                self.name = kwargs.get("name", "var_default")

        var_obj = _instantiate_plugin("var_test", VarNode)
        assert isinstance(var_obj, VarNode)
        assert var_obj.name == "var_test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])