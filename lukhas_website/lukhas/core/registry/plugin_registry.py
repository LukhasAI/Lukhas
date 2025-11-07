#!/usr/bin/env python3
"""
LUKHAS Plugin Registry System

Enterprise-grade plugin discovery and management for T4/0.01% performance targets.
Provides automatic plugin discovery, instantiation, and lifecycle management.
"""

import importlib
import importlib.util
import inspect
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Type

from observability.opentelemetry_tracing import LUKHASTracer
from observability.prometheus_metrics import LUKHASMetrics


class LUKHASPlugin(Protocol):
    """Protocol defining the interface for LUKHAS plugins."""

    def initialize(self) -> None:
        """Initialize the plugin."""
        ...

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        ...

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the plugin."""
        ...

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        ...


@dataclass
class PluginInfo:
    """Plugin metadata and configuration."""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]
    config_schema: Optional[Dict[str, Any]] = None
    performance_profile: Optional[Dict[str, Any]] = None


class PluginBase(ABC):
    """Base class for LUKHAS plugins."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.initialized = False
        self.metrics = LUKHASMetrics()
        self.tracer = LUKHASTracer()

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        pass

    def initialize(self) -> None:
        """Initialize the plugin."""
        if self.initialized:
            return

        with self.tracer.trace_operation(f"plugin_init_{self.name}"):
            self._initialize()
            self.initialized = True

        self.metrics.record_plugin_operation(
            "initialization",
            plugin_name=self.name,
            success=True
        )

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        if not self.initialized:
            return

        with self.tracer.trace_operation(f"plugin_shutdown_{self.name}"):
            self._shutdown()
            self.initialized = False

        self.metrics.record_plugin_operation(
            "shutdown",
            plugin_name=self.name,
            success=True
        )

    @abstractmethod
    def _initialize(self) -> None:
        """Plugin-specific initialization logic."""
        pass

    def _shutdown(self) -> None:
        """Plugin-specific shutdown logic."""
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the plugin."""
        pass


class PluginRegistry:
    """
    Enterprise plugin registry with automatic discovery and management.

    Features:
    - Automatic plugin discovery from filesystem
    - Smart instantiation with dependency resolution
    - Performance monitoring and health checks
    - Plugin lifecycle management
    """

    def __init__(
        self,
        search_paths: Optional[List[str]] = None,
        metrics: Optional[LUKHASMetrics] = None,
        tracer: Optional[LUKHASTracer] = None,
    ):
        """
        Initialize plugin registry.

        Args:
            search_paths: Directories to search for plugins
            metrics: Metrics collector instance
            tracer: Distributed tracer instance
        """
        self.search_paths = search_paths or [
            "lukhas/core/plugins",
            "lukhas/memory/plugins",
            "lukhas/consciousness/plugins",
            "candidate/core/plugins",
            "plugins"
        ]

        self.metrics = metrics or LUKHASMetrics()
        self.tracer = tracer or LUKHASTracer()

        self.discovered_plugins: Dict[str, Type[PluginBase]] = {}
        self.instantiated_plugins: Dict[str, PluginBase] = {}
        self.plugin_metadata: Dict[str, PluginInfo] = {}

        self._last_discovery = 0
        self._discovery_cache_duration = 300  # 5 minutes

    def discover_plugins(self, force_refresh: bool = False) -> Dict[str, Type[PluginBase]]:
        """
        Discover plugins from configured search paths.

        Args:
            force_refresh: Force rediscovery even if cache is valid

        Returns:
            Dictionary mapping plugin names to plugin classes
        """
        current_time = time.time()

        # Use cache if valid and not forcing refresh
        if (not force_refresh and
            self.discovered_plugins and
            current_time - self._last_discovery < self._discovery_cache_duration):
            return self.discovered_plugins

        with self.tracer.trace_operation("plugin_discovery") as span:
            span.set_attribute("force_refresh", force_refresh)
            span.set_attribute("search_paths", len(self.search_paths))

            discovered_count = 0

            for search_path in self.search_paths:
                try:
                    discovered_count += self._discover_in_path(search_path)
                except Exception as e:
                    self.metrics.record_plugin_operation(
                        "discovery",
                        success=False,
                        error=str(e)
                    )
                    # Continue discovery in other paths

            span.set_attribute("plugins_discovered", discovered_count)

        self._last_discovery = current_time

        self.metrics.record_plugin_operation(
            "discovery",
            success=True
        )

        return self.discovered_plugins

    def _discover_in_path(self, search_path: str) -> int:
        """Discover plugins in a specific path."""
        if not os.path.exists(search_path):
            return 0

        discovered_count = 0

        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if (file.endswith('_plugin.py') or
                    file.endswith('_adapter.py') or
                    (file.endswith('.py') and 'plugin' in file.lower())):

                    file_path = os.path.join(root, file)
                    try:
                        plugin_class = self._load_plugin_from_file(file_path)
                        if plugin_class:
                            self.discovered_plugins[plugin_class.__name__] = plugin_class
                            discovered_count += 1
                    except Exception as e:
                        # Log but continue discovery
                        print(f"Warning: Failed to load plugin from {file_path}: {e}")

        return discovered_count

    def _load_plugin_from_file(self, file_path: str) -> Optional[Type[PluginBase]]:
        """Load a plugin class from a Python file."""
        try:
            # Create module spec
            module_name = f"plugin_{hash(file_path)}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)

            if spec is None or spec.loader is None:
                return None

            # Load module
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes
            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginBase) and
                    obj != PluginBase and
                    not obj.__name__.startswith('_')):
                    return obj

        except Exception as e:
            raise RuntimeError(f"Failed to load plugin from {file_path}: {e}")

        return None

    def instantiate_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> PluginBase:
        """
        Instantiate a plugin by name.

        Args:
            plugin_name: Name of the plugin to instantiate
            config: Optional configuration for the plugin

        Returns:
            Instantiated plugin instance

        Raises:
            ValueError: If plugin not found or instantiation fails
        """
        if plugin_name in self.instantiated_plugins:
            return self.instantiated_plugins[plugin_name]

        if plugin_name not in self.discovered_plugins:
            # Try discovery first
            self.discover_plugins()

            if plugin_name not in self.discovered_plugins:
                raise ValueError(f"Plugin '{plugin_name}' not found in registry")

        plugin_class = self.discovered_plugins[plugin_name]

        with self.tracer.trace_operation(f"plugin_instantiation_{plugin_name}") as span:
            try:
                # Instantiate plugin
                plugin_instance = plugin_class(config=config) if config else plugin_class()

                # Initialize plugin
                plugin_instance.initialize()

                # Store instance
                self.instantiated_plugins[plugin_name] = plugin_instance

                # Store metadata
                self.plugin_metadata[plugin_name] = plugin_instance.get_info()

                span.set_attribute("success", True)

                self.metrics.record_plugin_operation(
                    "instantiation",
                    plugin_name=plugin_name,
                    success=True
                )

                return plugin_instance

            except Exception as e:
                span.set_attribute("success", False)
                span.set_attribute("error", str(e))

                self.metrics.record_plugin_operation(
                    "instantiation",
                    plugin_name=plugin_name,
                    success=False,
                    error=str(e)
                )

                raise ValueError(f"Failed to instantiate plugin '{plugin_name}': {e}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get an instantiated plugin by name."""
        return self.instantiated_plugins.get(plugin_name)

    def list_plugins(self) -> Dict[str, PluginInfo]:
        """List all available plugins with their metadata."""
        # Ensure discovery is up to date
        self.discover_plugins()

        plugin_list = {}

        for name, _plugin_class in self.discovered_plugins.items():
            if name in self.plugin_metadata:
                plugin_list[name] = self.plugin_metadata[name]
            else:
                # Create basic metadata
                plugin_list[name] = PluginInfo(
                    name=name,
                    version="unknown",
                    description="Plugin discovered but not instantiated",
                    author="unknown",
                    category="unknown",
                    dependencies=[]
                )

        return plugin_list

    def shutdown_all_plugins(self) -> None:
        """Shutdown all instantiated plugins."""
        with self.tracer.trace_operation("plugin_registry_shutdown"):
            for plugin_name, plugin_instance in self.instantiated_plugins.items():
                try:
                    plugin_instance.shutdown()
                except Exception as e:
                    print(f"Warning: Failed to shutdown plugin {plugin_name}: {e}")

            self.instantiated_plugins.clear()

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on plugin registry and all plugins."""
        health_data = {
            "registry_healthy": True,
            "discovered_plugins": len(self.discovered_plugins),
            "instantiated_plugins": len(self.instantiated_plugins),
            "plugins": {},
            "last_discovery": self._last_discovery,
            "cache_valid": time.time() - self._last_discovery < self._discovery_cache_duration
        }

        # Check each instantiated plugin
        for plugin_name, plugin_instance in self.instantiated_plugins.items():
            plugin_health = {
                "initialized": plugin_instance.initialized,
                "healthy": True
            }

            try:
                # Basic health check
                if hasattr(plugin_instance, 'health_check'):
                    plugin_health.update(plugin_instance.health_check())
            except Exception as e:
                plugin_health["healthy"] = False
                plugin_health["error"] = str(e)

            health_data["plugins"][plugin_name] = plugin_health

        return health_data


# Global plugin registry instance
_plugin_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create the global plugin registry."""
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry


def register_plugin(plugin_class: Type[PluginBase]) -> None:
    """Register a plugin class with the global registry."""
    registry = get_plugin_registry()
    registry.discovered_plugins[plugin_class.__name__] = plugin_class
