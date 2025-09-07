"""
LUKHAS Plugin Registry
=====================

Centralized plugin management system for the LUKHAS orchestration framework.
Provides dynamic plugin loading, dependency resolution, and lifecycle management.

ΛTAG: plugin, registry, orchestration
"""
from typing import List
from typing import Dict
import streamlit as st
from datetime import timezone

import asyncio
import importlib
import importlib.util
import inspect
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported by the system"""

    PROCESSOR = "processor"
    ANALYZER = "analyzer"
    TRANSFORMER = "transformer"
    MONITOR = "monitor"
    INTEGRATION = "integration"
    CUSTOM = "custom"


class PluginStatus(Enum):
    """Plugin lifecycle states"""

    UNLOADED = auto()
    LOADING = auto()
    LOADED = auto()
    INITIALIZING = auto()
    READY = auto()
    ACTIVE = auto()
    ERROR = auto()
    DISABLED = auto()
    UNLOADING = auto()


@dataclass
class PluginDependency:
    """Represents a plugin dependency"""

    name: str
    version: Optional[str] = None
    optional: bool = False

    def __str__(self):
        version_str = f">={self.version}" if self.version else ""
        optional_str = " (optional)" if self.optional else ""
        return f"{self.name}{version_str}{optional_str}"


@dataclass
class PluginMetadata:
    """Metadata for a plugin"""

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "LUKHAS Team"
    plugin_type: PluginType = PluginType.CUSTOM
    dependencies: list[PluginDependency] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "dependencies": [str(dep) for dep in self.dependencies],
            "capabilities": self.capabilities,
            "config_schema": self.config_schema,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


class PluginInterface:
    """
    Base interface that all plugins must implement.

    This provides the contract for plugin interaction with the registry.
    """

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.status = PluginStatus.UNLOADED
        self.config: dict[str, Any] = {}
        self._logger = logging.getLogger(f"Plugin.{metadata.name}")

    async def initialize(self, config: dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration

        Returns:
            bool: True if initialization successful
        """
        self.config = config
        self.status = PluginStatus.READY
        return True

    async def process_signal(self, signal: dict[str, Any]) -> Any:
        """
        Process a signal from the orchestrator.

        Args:
            signal: Signal data

        Returns:
            Processing result
        """
        raise NotImplementedError("Plugins must implement process_signal")

    async def shutdown(self) -> None:
        """Gracefully shutdown the plugin"""
        self.status = PluginStatus.UNLOADING

    def get_status(self) -> PluginStatus:
        """Get current plugin status"""
        return self.status

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return self.metadata


class PluginRegistry:
    """
    Central registry for managing plugins in the LUKHAS system.

    Handles:
    - Dynamic plugin loading/unloading
    - Dependency resolution
    - Plugin lifecycle management
    - Signal routing
    - Error handling and recovery
    """

    def __init__(self, plugin_dirs: Optional[list[str]] = None):
        """
        Initialize the plugin registry.

        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or [
            "lukhas/plugins",
            "core/plugins",
            "plugins",
        ]
        self.plugins: dict[str, PluginInterface] = {}
        self.plugin_classes: dict[str, type[PluginInterface]] = {}
        self.dependency_graph: dict[str, set[str]] = {}
        self._signal_handlers: dict[str, list[str]] = {}  # signal_type -> [plugin_names]
        self._logger = logger

    def discover_plugins(self) -> dict[str, PluginMetadata]:
        """
        Discover all available plugins in configured directories.

        Returns:
            Dict mapping plugin names to their metadata
        """
        discovered = {}

        for plugin_dir in self.plugin_dirs:
            path = Path(plugin_dir)
            if not path.exists():
                self._logger.debug(f"Plugin directory not found: {plugin_dir}")
                continue

            self._logger.info(f"Scanning plugin directory: {plugin_dir}")

            # Look for Python files
            for file_path in path.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue

                try:
                    metadata = self._extract_plugin_metadata(file_path)
                    if metadata:
                        discovered[metadata.name] = metadata
                        self._logger.info(f"Discovered plugin: {metadata.name} v{metadata.version}")
                except Exception as e:
                    self._logger.error(f"Error discovering plugin from {file_path}: {e}")

        return discovered

    def _extract_plugin_metadata(self, file_path: Path) -> Optional[PluginMetadata]:
        """Extract metadata from a plugin file without fully loading it"""
        try:
            # Load the module spec
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if not spec or not spec.loader:
                return None

            # Create module
            module = importlib.util.module_from_spec(spec)

            # Execute module
            spec.loader.exec_module(module)

            # Look for plugin class or metadata
            if hasattr(module, "PLUGIN_METADATA"):
                metadata = module.PLUGIN_METADATA
                metadata.name = file_path.stem
                return metadata

            # Look for plugin class
            if hasattr(module, "plugin"):
                plugin_class = module.plugin
                if hasattr(plugin_class, "metadata"):
                    md = plugin_class.metadata
                    md.name = file_path.stem
                    return md

                return PluginMetadata(
                    name=file_path.stem,
                    description=(
                        getattr(plugin_class, "__doc__", "").strip() if hasattr(plugin_class, "__doc__") else ""
                    ),
                )

            # Look for classes that inherit from PluginInterface
            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, PluginInterface) and obj != PluginInterface:
                    if hasattr(obj, "metadata"):
                        md = obj.metadata
                        md.name = file_path.stem
                        return md
                    return PluginMetadata(name=file_path.stem)

        except Exception as e:
            self._logger.debug(f"Could not extract metadata from {file_path}: {e}")

        return None

    async def load_plugin(self, plugin_name: str, config: Optional[dict[str, Any]] = None) -> bool:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Name of the plugin to load
            config: Optional configuration for the plugin

        Returns:
            bool: True if plugin loaded successfully
        """
        try:
            if plugin_name in self.plugins:
                self._logger.warning(f"Plugin {plugin_name} already loaded")
                return True

            # Find plugin file
            plugin_file = self._find_plugin_file(plugin_name)
            if not plugin_file:
                self._logger.error(f"Plugin {plugin_name} not found")
                return False

            # Load plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if not spec or not spec.loader:
                self._logger.error(f"Could not load plugin spec for {plugin_name}")
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Find and instantiate plugin class
            plugin_class = None

            if hasattr(module, "plugin"):
                plugin_class = module.plugin
            else:
                # Look for PluginInterface subclass
                for _name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, PluginInterface) and obj != PluginInterface:
                        plugin_class = obj
                        break

            if not plugin_class:
                self._logger.error(f"No plugin class found in {plugin_name}")
                return False

            # Create plugin instance
            if inspect.isclass(plugin_class):
                if hasattr(plugin_class, "metadata"):
                    metadata = plugin_class.metadata
                    plugin_instance = plugin_class(metadata)
                else:
                    # Let the plugin construct its own metadata
                    plugin_instance = plugin_class()
                    metadata = plugin_instance.metadata
            else:
                # Handle function-based plugins
                metadata = PluginMetadata(name=plugin_name)
                plugin_instance = self._create_function_plugin_wrapper(plugin_class, metadata)

            # Check dependencies using the instantiated metadata
            if not await self._check_dependencies(metadata):
                self._logger.error(f"Dependencies not satisfied for {plugin_name}")
                return False

            # Initialize plugin
            plugin_instance.status = PluginStatus.INITIALIZING
            success = await plugin_instance.initialize(config or {})

            if success:
                self.plugins[plugin_name] = plugin_instance
                self.plugin_classes[plugin_name] = plugin_class
                plugin_instance.status = PluginStatus.READY
                self._logger.info(f"Successfully loaded plugin: {plugin_name}")

                # Register signal handlers if plugin has them
                if hasattr(plugin_instance, "handles_signals"):
                    for signal_type in plugin_instance.handles_signals:
                        self.register_signal_handler(signal_type, plugin_name)

                return True
            else:
                self._logger.error(f"Plugin {plugin_name} initialization failed")
                return False

        except Exception as e:
            self._logger.error(f"Error loading plugin {plugin_name}: {e}", exc_info=True)
            return False

    def _find_plugin_file(self, plugin_name: str) -> Optional[Path]:
        """Find plugin file in configured directories"""
        for plugin_dir in self.plugin_dirs:
            path = Path(plugin_dir)

            candidates = [
                f"{plugin_name}.py",
                f"{plugin_name.replace('-', '_')}.py",
                f"{plugin_name}_plugin.py",
            ]

            for candidate in candidates:
                plugin_file = path / candidate
                if plugin_file.exists():
                    return plugin_file

        return None

    def _create_function_plugin_wrapper(self, func: Callable, metadata: PluginMetadata) -> PluginInterface:
        """Create a PluginInterface wrapper for function-based plugins"""

        class FunctionPlugin(PluginInterface):
            def __init__(self, metadata: PluginMetadata):
                super().__init__(metadata)
                self.func = func

            async def process_signal(self, signal: dict[str, Any]) -> Any:
                if asyncio.iscoroutinefunction(self.func):
                    return await self.func(signal)
                else:
                    return self.func(signal)

        return FunctionPlugin(metadata)

    async def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """Check if plugin dependencies are satisfied"""
        for dep in metadata.dependencies:
            if not dep.optional and dep.name not in self.plugins:
                # Try to load dependency
                if not await self.load_plugin(dep.name):
                    return False
        return True

    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            bool: True if successfully unloaded
        """
        try:
            if plugin_name not in self.plugins:
                self._logger.warning(f"Plugin {plugin_name} not loaded")
                return True

            plugin = self.plugins[plugin_name]

            # Check if other plugins depend on this one
            dependents = self._get_dependent_plugins(plugin_name)
            if dependents:
                self._logger.error(f"Cannot unload {plugin_name}, required by: {dependents}")
                return False

            # Shutdown plugin
            await plugin.shutdown()

            # Remove from registry
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_classes:
                del self.plugin_classes[plugin_name]

            # Remove from signal handlers
            for handlers in self._signal_handlers.values():
                if plugin_name in handlers:
                    handlers.remove(plugin_name)

            self._logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            self._logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a loaded plugin without unloading it."""
        if plugin_name not in self.plugins:
            self._logger.warning(f"Plugin {plugin_name} not loaded")
            return False

        plugin = self.plugins[plugin_name]
        if plugin.status == PluginStatus.DISABLED:
            return True

        plugin.status = PluginStatus.DISABLED
        self._logger.info(f"Disabled plugin: {plugin_name}")
        return True

    async def enable_plugin(self, plugin_name: str) -> bool:
        """Re-enable a previously disabled plugin."""
        if plugin_name not in self.plugins:
            self._logger.warning(f"Plugin {plugin_name} not loaded")
            return False

        plugin = self.plugins[plugin_name]
        if plugin.status != PluginStatus.DISABLED:
            return True

        plugin.status = PluginStatus.READY
        self._logger.info(f"Enabled plugin: {plugin_name}")
        return True

    def _get_dependent_plugins(self, plugin_name: str) -> list[str]:
        """Get list of plugins that depend on the given plugin"""
        dependents = []
        for name, plugin in self.plugins.items():
            if name == plugin_name:
                continue
            for dep in plugin.metadata.dependencies:
                if dep.name == plugin_name and not dep.optional:
                    dependents.append(name)
        return dependents

    def register_signal_handler(self, signal_type: str, plugin_name: str) -> None:
        """Register a plugin to handle a specific signal type"""
        if signal_type not in self._signal_handlers:
            self._signal_handlers[signal_type] = []
        if plugin_name not in self._signal_handlers[signal_type]:
            self._signal_handlers[signal_type].append(plugin_name)
            self._logger.debug(f"Registered {plugin_name} for signal type: {signal_type}")

    async def broadcast_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        """
        Broadcast a signal to all relevant plugins.

        Args:
            signal: Signal to broadcast

        Returns:
            Dict mapping plugin names to their responses
        """
        signal_type = signal.get("type", "generic")
        responses = {}

        # Get handlers for this signal type
        handlers = self._signal_handlers.get(signal_type, [])

        # Also include plugins that handle all signals
        all_handlers = self._signal_handlers.get("*", [])
        handlers = list(set(handlers + all_handlers))

        # If no specific handlers, broadcast to all active plugins
        if not handlers:
            handlers = [name for name, plugin in self.plugins.items() if plugin.status == PluginStatus.READY]

        # Process signal with each handler
        for plugin_name in handlers:
            if plugin_name not in self.plugins:
                continue

            plugin = self.plugins[plugin_name]
            if plugin.status != PluginStatus.READY:
                continue

            try:
                plugin.status = PluginStatus.ACTIVE
                response = await plugin.process_signal(signal)
                responses[plugin_name] = response
                plugin.status = PluginStatus.READY
            except Exception as e:
                self._logger.error(f"Error in plugin {plugin_name} processing signal: {e}")
                plugin.status = PluginStatus.ERROR
                responses[plugin_name] = {"error": str(e)}

        return responses

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a loaded plugin by name"""
        return self.plugins.get(plugin_name)

    def list_plugins(self, status: Optional[PluginStatus] = None) -> list[dict[str, Any]]:
        """
        List all loaded plugins.

        Args:
            status: Optional filter by status

        Returns:
            List of plugin information dictionaries
        """
        plugin_list = []

        for name, plugin in self.plugins.items():
            if status and plugin.status != status:
                continue

            plugin_info = {
                "name": name,
                "status": plugin.status.name,
                "metadata": plugin.metadata.to_dict(),
            }
            plugin_list.append(plugin_info)

        return plugin_list

    async def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (unload and load again).

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            bool: True if successfully reloaded
        """
        # Save current config
        config = None
        if plugin_name in self.plugins:
            config = self.plugins[plugin_name].config

        # Unload
        if not await self.unload_plugin(plugin_name):
            return False

        # Load again
        return await self.load_plugin(plugin_name, config)

    def save_registry_state(self, file_path: str) -> None:
        """Save current registry state to file"""
        state = {
            "plugins": {
                name: {
                    "metadata": plugin.metadata.to_dict(),
                    "status": plugin.status.name,
                    "config": plugin.config,
                }
                for name, plugin in self.plugins.items()
            },
            "signal_handlers": self._signal_handlers,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(state, f, indent=2)

        self._logger.info(f"Saved registry state to {file_path}")

    async def restore_registry_state(self, file_path: str) -> bool:
        """Restore registry state from file"""
        try:
            with open(file_path) as f:
                state = json.load(f)

            # Load plugins
            for plugin_name, plugin_data in state.get("plugins", {}).items():
                config = plugin_data.get("config", {})
                await self.load_plugin(plugin_name, config)

            # Restore signal handlers
            self._signal_handlers = state.get("signal_handlers", {})

            self._logger.info(f"Restored registry state from {file_path}")
            return True

        except Exception as e:
            self._logger.error(f"Error restoring registry state: {e}")
            return False


# Example plugin implementation


class ExamplePlugin(PluginInterface):
    """Example plugin demonstrating the plugin interface"""

    metadata = PluginMetadata(
        name="example_plugin",
        version="1.0.0",
        description="Example plugin for demonstration",
        plugin_type=PluginType.PROCESSOR,
        capabilities=["process_text", "analyze_data"],
        dependencies=[PluginDependency("base_processor", optional=True)],
    )

    def __init__(self):
        super().__init__(self.metadata)
        self.handles_signals = ["text", "data", "example"]

    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the example plugin"""
        await super().initialize(config)
        self._logger.info("Example plugin initialized")
        return True

    async def process_signal(self, signal: dict[str, Any]) -> Any:
        """Process incoming signals"""
        signal_type = signal.get("type", "unknown")
        data = signal.get("data", {})

        self._logger.debug(f"Processing {signal_type} signal")

        # Example processing
        result = {
            "plugin": self.metadata.name,
            "signal_type": signal_type,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "result": f"Processed {len(str(data)} bytes of data",
        }

        return result
