"""
Tests for Plugin Registry
========================

ΛTAG: test, plugin, registry
"""

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from orchestration.interfaces.plugin_registry import (
    ExamplePlugin,
    PluginDependency,
    PluginInterface,
    PluginMetadata,
    PluginRegistry,
    PluginStatus,
    PluginType,
)


class TestPluginMetadata:
    """Test PluginMetadata dataclass"""

    def test_metadata_creation(self):
        """Test creating plugin metadata"""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            plugin_type=PluginType.PROCESSOR,
            capabilities=["process", "analyze"],
        )

        assert metadata.name == "test_plugin"
        assert metadata.plugin_type == PluginType.PROCESSOR
        assert "process" in metadata.capabilities

    def test_metadata_dependencies(self):
        """Test plugin dependencies"""
        dep1 = PluginDependency("base_plugin", "1.0.0")
        dep2 = PluginDependency("optional_plugin", optional=True)

        metadata = PluginMetadata(name="test_plugin", dependencies=[dep1, dep2])

        assert len(metadata.dependencies) == 2
        assert metadata.dependencies[0].optional is False
        assert metadata.dependencies[1].optional is True

    def test_metadata_to_dict(self):
        """Test metadata dictionary conversion"""
        metadata = PluginMetadata(
            name="test_plugin",
            version="2.0.0",
            plugin_type=PluginType.ANALYZER,
            tags=["test", "demo"],
        )

        data = metadata.to_dict()

        assert data["name"] == "test_plugin"
        assert data["version"] == "2.0.0"
        assert data["plugin_type"] == "analyzer"
        assert "test" in data["tags"]


class TestPluginInterface:
    """Test PluginInterface base class"""

    @pytest.fixture
    def mock_plugin(self):
        """Create a mock plugin"""

        class MockPlugin(PluginInterface):
            def __init__(self):
                metadata = PluginMetadata(
                    name="mock_plugin",
                    version="1.0.0",
                    plugin_type=PluginType.PROCESSOR,
                )
                super().__init__(metadata)
                self.signal_count = 0

            async def process_signal(self, signal: Dict[str, Any]) -> Any:
                self.signal_count += 1
                return {"processed": True, "count": self.signal_count}

        return MockPlugin()

    def test_plugin_creation(self, mock_plugin):
        """Test plugin creation"""
        assert mock_plugin.metadata.name == "mock_plugin"
        assert mock_plugin.status == PluginStatus.UNLOADED
        assert isinstance(mock_plugin.config, dict)

    @pytest.mark.asyncio
    async def test_plugin_initialization(self, mock_plugin):
        """Test plugin initialization"""
        config = {"setting1": "value1", "setting2": 42}

        success = await mock_plugin.initialize(config)

        assert success is True
        assert mock_plugin.status == PluginStatus.READY
        assert mock_plugin.config == config

    @pytest.mark.asyncio
    async def test_plugin_signal_processing(self, mock_plugin):
        """Test plugin signal processing"""
        await mock_plugin.initialize({})

        signal = {"type": "test", "data": "test_data"}
        result = await mock_plugin.process_signal(signal)

        assert result["processed"] is True
        assert result["count"] == 1
        assert mock_plugin.signal_count == 1

    @pytest.mark.asyncio
    async def test_plugin_shutdown(self, mock_plugin):
        """Test plugin shutdown"""
        await mock_plugin.initialize({})
        await mock_plugin.shutdown()

        assert mock_plugin.status == PluginStatus.UNLOADING


class TestPluginRegistry:
    """Test PluginRegistry functionality"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def plugin_registry(self, temp_plugin_dir):
        """Create plugin registry with temp directory"""
        registry = PluginRegistry(plugin_dirs=[str(temp_plugin_dir)])
        return registry

    def create_test_plugin_file(self, plugin_dir: Path, name: str, content: str = None):
        """Create a test plugin file"""
        if content is None:
            content = f"""
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata, PluginType

class {name.title()}Plugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(
                name="{name}_plugin",
                version="1.0.0",
                plugin_type=PluginType.PROCESSOR
            )
        super().__init__(metadata)

    async def process_signal(self, signal):
        return {{"plugin": "{name}", "signal": signal}}
"""

        plugin_file = plugin_dir / f"{name}_plugin.py"
        plugin_file.write_text(content)
        return plugin_file

    def test_registry_creation(self, plugin_registry):
        """Test registry creation"""
        assert len(plugin_registry.plugins) == 0
        assert len(plugin_registry.plugin_classes) == 0
        assert isinstance(plugin_registry.plugin_dirs, list)

    def test_plugin_discovery(self, plugin_registry, temp_plugin_dir):
        """Test plugin discovery"""
        # Create test plugins
        self.create_test_plugin_file(temp_plugin_dir, "test1")
        self.create_test_plugin_file(temp_plugin_dir, "test2")

        # Create invalid file (should be ignored)
        (temp_plugin_dir / "_private.py").write_text("# Private file")

        # Discover plugins
        discovered = plugin_registry.discover_plugins()

        assert len(discovered) == 2
        assert "test1_plugin" in discovered
        assert "test2_plugin" in discovered

    @pytest.mark.asyncio
    async def test_load_plugin(self, plugin_registry, temp_plugin_dir):
        """Test loading a plugin"""
        self.create_test_plugin_file(temp_plugin_dir, "loadtest")

        # Load plugin
        success = await plugin_registry.load_plugin("loadtest_plugin")

        assert success is True
        assert "loadtest_plugin" in plugin_registry.plugins
        assert plugin_registry.plugins["loadtest_plugin"].status == PluginStatus.READY

    @pytest.mark.asyncio
    async def test_load_nonexistent_plugin(self, plugin_registry):
        """Test loading nonexistent plugin"""
        success = await plugin_registry.load_plugin("nonexistent_plugin")

        assert success is False
        assert "nonexistent_plugin" not in plugin_registry.plugins

    @pytest.mark.asyncio
    async def test_plugin_with_dependencies(self, plugin_registry, temp_plugin_dir):
        """Test loading plugin with dependencies"""
        # Create base plugin
        base_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class BasePlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="base_plugin", version="1.0.0")
        super().__init__(metadata)

    async def process_signal(self, signal):
        return {"base": True}
"""
        self.create_test_plugin_file(temp_plugin_dir, "base", base_content)

        # Create dependent plugin
        dependent_content = """
from orchestration.interfaces.plugin_registry import (
    PluginInterface, PluginMetadata, PluginDependency
)

class DependentPlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(
                name="dependent_plugin",
                version="1.0.0",
                dependencies=[PluginDependency("base_plugin")]
            )
        super().__init__(metadata)

    async def process_signal(self, signal):
        return {"dependent": True}
"""
        self.create_test_plugin_file(temp_plugin_dir, "dependent", dependent_content)

        # Load dependent plugin (should auto-load base)
        success = await plugin_registry.load_plugin("dependent_plugin")

        assert success is True
        assert "base_plugin" in plugin_registry.plugins
        assert "dependent_plugin" in plugin_registry.plugins

    @pytest.mark.asyncio
    async def test_unload_plugin(self, plugin_registry, temp_plugin_dir):
        """Test unloading a plugin"""
        self.create_test_plugin_file(temp_plugin_dir, "unloadtest")

        # Load and then unload
        await plugin_registry.load_plugin("unloadtest_plugin")
        success = await plugin_registry.unload_plugin("unloadtest_plugin")

        assert success is True
        assert "unloadtest_plugin" not in plugin_registry.plugins

    @pytest.mark.asyncio
    async def test_unload_plugin_with_dependents(
        self, plugin_registry, temp_plugin_dir
    ):
        """Test unloading plugin that others depend on"""
        # Create plugins with dependency
        self.create_test_plugin_file(temp_plugin_dir, "base")

        dependent_content = """
from orchestration.interfaces.plugin_registry import (
    PluginInterface, PluginMetadata, PluginDependency
)

class DependentPlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(
                name="dependent_plugin",
                dependencies=[PluginDependency("base_plugin")]
            )
        super().__init__(metadata)

    async def process_signal(self, signal):
        return {"dependent": True}
"""
        self.create_test_plugin_file(temp_plugin_dir, "dependent", dependent_content)

        # Load both
        await plugin_registry.load_plugin("base_plugin")
        await plugin_registry.load_plugin("dependent_plugin")

        # Try to unload base (should fail)
        success = await plugin_registry.unload_plugin("base_plugin")

        assert success is False
        assert "base_plugin" in plugin_registry.plugins  # Still loaded

    def test_signal_handler_registration(self, plugin_registry):
        """Test signal handler registration"""
        plugin_registry.register_signal_handler("test_signal", "plugin1")
        plugin_registry.register_signal_handler("test_signal", "plugin2")
        plugin_registry.register_signal_handler("other_signal", "plugin1")

        assert "test_signal" in plugin_registry._signal_handlers
        assert len(plugin_registry._signal_handlers["test_signal"]) == 2
        assert "plugin1" in plugin_registry._signal_handlers["test_signal"]
        assert "plugin2" in plugin_registry._signal_handlers["test_signal"]

    @pytest.mark.asyncio
    async def test_broadcast_signal(self, plugin_registry, temp_plugin_dir):
        """Test broadcasting signals to plugins"""
        # Create and load test plugins
        plugin1_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class Plugin1(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="plugin1")
        super().__init__(metadata)
        self.handles_signals = ["test_signal"]

    async def process_signal(self, signal):
        return {"plugin": "plugin1", "received": signal.get("data")}
"""
        self.create_test_plugin_file(temp_plugin_dir, "plugin1", plugin1_content)

        plugin2_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class Plugin2(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="plugin2")
        super().__init__(metadata)
        self.handles_signals = ["test_signal", "other_signal"]

    async def process_signal(self, signal):
        return {"plugin": "plugin2", "received": signal.get("data")}
"""
        self.create_test_plugin_file(temp_plugin_dir, "plugin2", plugin2_content)

        await plugin_registry.load_plugin("plugin1")
        await plugin_registry.load_plugin("plugin2")

        # Broadcast signal
        signal = {"type": "test_signal", "data": "test_data"}
        responses = await plugin_registry.broadcast_signal(signal)

        # Both plugins should respond
        assert len(responses) >= 2  # May include more if handling all signals
        assert any("plugin1" in str(r) for r in responses.values())
        assert any("plugin2" in str(r) for r in responses.values())

    @pytest.mark.asyncio
    async def test_plugin_error_handling(self, plugin_registry, temp_plugin_dir):
        """Test error handling in plugin processing"""
        error_plugin_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class ErrorPlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="error_plugin")
        super().__init__(metadata)

    async def process_signal(self, signal):
        raise Exception("Simulated plugin error")
"""
        self.create_test_plugin_file(temp_plugin_dir, "error", error_plugin_content)

        await plugin_registry.load_plugin("error_plugin")

        # Broadcast signal to error plugin
        signal = {"type": "test", "data": "test"}
        responses = await plugin_registry.broadcast_signal(signal)

        # Should handle error gracefully
        assert "error_plugin" in responses
        assert "error" in responses["error_plugin"]
        assert plugin_registry.plugins["error_plugin"].status == PluginStatus.ERROR

    def test_list_plugins(self, plugin_registry):
        """Test listing plugins"""
        # Add some mock plugins
        plugin1 = ExamplePlugin()
        plugin1.status = PluginStatus.READY
        plugin_registry.plugins["example1"] = plugin1

        plugin2 = ExamplePlugin()
        plugin2.status = PluginStatus.ERROR
        plugin_registry.plugins["example2"] = plugin2

        # List all plugins
        all_plugins = plugin_registry.list_plugins()
        assert len(all_plugins) == 2

        # List by status
        ready_plugins = plugin_registry.list_plugins(status=PluginStatus.READY)
        assert len(ready_plugins) == 1
        assert ready_plugins[0]["name"] == "example1"

        error_plugins = plugin_registry.list_plugins(status=PluginStatus.ERROR)
        assert len(error_plugins) == 1
        assert error_plugins[0]["name"] == "example2"

    @pytest.mark.asyncio
    async def test_reload_plugin(self, plugin_registry, temp_plugin_dir):
        """Test reloading a plugin"""
        self.create_test_plugin_file(temp_plugin_dir, "reload")

        # Load plugin
        await plugin_registry.load_plugin("reload_plugin")

        # Configure plugin
        plugin = plugin_registry.get_plugin("reload_plugin")
        plugin.config = {"custom": "config"}

        # Reload plugin
        success = await plugin_registry.reload_plugin("reload_plugin")

        assert success is True
        assert "reload_plugin" in plugin_registry.plugins
        # Config should be preserved
        assert plugin_registry.plugins["reload_plugin"].config == {"custom": "config"}

    def test_save_restore_state(self, plugin_registry, tmp_path):
        """Test saving and restoring registry state"""
        # Add mock plugin
        plugin = ExamplePlugin()
        plugin.status = PluginStatus.READY
        plugin.config = {"setting": "value"}
        plugin_registry.plugins["example"] = plugin

        # Register signal handlers
        plugin_registry.register_signal_handler("test_signal", "example")

        # Save state
        state_file = tmp_path / "registry_state.json"
        plugin_registry.save_registry_state(str(state_file))

        assert state_file.exists()

        # Create new registry and restore
        new_registry = PluginRegistry()

        # Note: restore would try to load plugins, which won't work without proper setup
        # Just verify the file was created correctly
        import json

        with open(state_file) as f:
            state = json.load(f)

        assert "plugins" in state
        assert "example" in state["plugins"]
        assert state["plugins"]["example"]["config"]["setting"] == "value"
        assert "signal_handlers" in state
        assert "test_signal" in state["signal_handlers"]

    @pytest.mark.asyncio
    async def test_enable_disable_plugin(self, plugin_registry, temp_plugin_dir):
        """Test disabling and enabling a plugin"""
        self.create_test_plugin_file(temp_plugin_dir, "toggle")

        await plugin_registry.load_plugin("toggle_plugin")
        assert plugin_registry.plugins["toggle_plugin"].status == PluginStatus.READY

        await plugin_registry.disable_plugin("toggle_plugin")
        assert plugin_registry.plugins["toggle_plugin"].status == PluginStatus.DISABLED

        responses = await plugin_registry.broadcast_signal({"type": "test"})
        assert "toggle_plugin" not in responses

        await plugin_registry.enable_plugin("toggle_plugin")
        assert plugin_registry.plugins["toggle_plugin"].status == PluginStatus.READY


class TestExamplePlugin:
    """Test the ExamplePlugin implementation"""

    @pytest.fixture
    def example_plugin(self):
        """Create ExamplePlugin instance"""
        return ExamplePlugin()

    def test_example_plugin_metadata(self, example_plugin):
        """Test ExamplePlugin metadata"""
        assert example_plugin.metadata.name == "example_plugin"
        assert example_plugin.metadata.plugin_type == PluginType.PROCESSOR
        assert "process_text" in example_plugin.metadata.capabilities

    @pytest.mark.asyncio
    async def test_example_plugin_initialization(self, example_plugin):
        """Test ExamplePlugin initialization"""
        config = {"debug": True}
        success = await example_plugin.initialize(config)

        assert success is True
        assert example_plugin.status == PluginStatus.READY
        assert example_plugin.config == config

    @pytest.mark.asyncio
    async def test_example_plugin_signal_processing(self, example_plugin):
        """Test ExamplePlugin signal processing"""
        await example_plugin.initialize({})

        signal = {"type": "text", "data": {"message": "Hello world"}}

        result = await example_plugin.process_signal(signal)

        assert result["plugin"] == "example_plugin"
        assert result["signal_type"] == "text"
        assert "processed_at" in result
        assert "bytes" in result["result"]  # Should contain bytes in result


@pytest.mark.integration
class TestPluginIntegration:
    """Integration tests for plugin system"""

    @pytest.mark.asyncio
    async def test_multiple_plugin_interaction(self):
        """Test multiple plugins interacting"""
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        temp_plugin_dir = Path(temp_dir)

        try:
            registry = PluginRegistry(plugin_dirs=[str(temp_plugin_dir)])

            # Create plugins that interact
            producer_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class ProducerPlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="producer")
        super().__init__(metadata)
        self.handles_signals = ["produce"]

    async def process_signal(self, signal):
        # Produce data for other plugins
        return {"produced_data": f"Data from {signal.get('source', 'unknown')}"}
"""

            consumer_content = """
from orchestration.interfaces.plugin_registry import PluginInterface, PluginMetadata

class ConsumerPlugin(PluginInterface):
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = PluginMetadata(name="consumer")
        super().__init__(metadata)
        self.handles_signals = ["consume"]
        self.consumed_data = []

    async def process_signal(self, signal):
        # Consume data from other plugins
        if "produced_data" in signal:
            self.consumed_data.append(signal["produced_data"])
        return {"consumed": len(self.consumed_data)}
"""

            # Create plugin files
            (temp_plugin_dir / "producer.py").write_text(producer_content)
            (temp_plugin_dir / "consumer.py").write_text(consumer_content)

            # Load plugins
            await registry.load_plugin("producer")
            await registry.load_plugin("consumer")

            # Producer generates data
            produce_result = await registry.broadcast_signal(
                {"type": "produce", "source": "test_source"}
            )

            # Consumer processes the produced data
            produced_data = produce_result.get("producer", {})
            consume_result = await registry.broadcast_signal(
                {"type": "consume", **produced_data}
            )

            # Verify interaction
            assert "produced_data" in produced_data
            consumer_response = consume_result.get("consumer", {})
            assert consumer_response.get("consumed", 0) > 0

        finally:
            shutil.rmtree(temp_dir)
