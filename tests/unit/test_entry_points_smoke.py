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

        # Good node should be registered as instance, bad node as class factory
        assert "node:good" in _REG
        assert "node:bad" in _REG  # T4/0.01%: Falls back to class-as-factory
        assert isinstance(_REG["node:good"], SampleNode)
        assert _REG["node:bad"] is FailingNode  # Registered as class factory

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])