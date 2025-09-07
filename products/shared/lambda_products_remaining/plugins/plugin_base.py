"""
LUKHAS Plugin System Base Classes
Universal plugin architecture for modular AI components integration

This provides the foundation for integrating Lambda Products and other modules
as plug-and-play components into LUKHAS  and other systems.
"""
import streamlit as st
from datetime import timezone

import asyncio
import contextlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__, timezone)


class PluginStatus(Enum):
    """Plugin lifecycle states"""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    UPDATING = "updating"


class PluginPriority(Enum):
    """Plugin execution priority levels"""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class PluginManifest:
    """Plugin metadata and configuration schema"""

    id: str
    name: str
    version: str
    description: str
    author: str = "LUKHAS AI"
    dependencies: list[str] = field(default_factory=list)
    optional_dependencies: list[str] = field(default_factory=list)
    endpoints: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    priority: PluginPriority = PluginPriority.NORMAL
    auto_enable: bool = True
    tier_requirements: Optional[str] = None  # For Lambda Products tiers (T1/T2/T3)


@dataclass
class HealthStatus:
    """Plugin health monitoring data"""

    is_healthy: bool
    last_check: datetime
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time_ms: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    uptime_seconds: float = 0.0
    custom_metrics: dict[str, Any] = field(default_factory=dict)


class LukhasPlugin(ABC):
    """
    Abstract base class for all LUKHAS plugins

    This provides the standard interface that all plugins must implement
    to integrate with the LUKHAS ecosystem.
    """

    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.status = PluginStatus.UNINITIALIZED
        self.config: dict[str, Any] = {}
        self.health_status = HealthStatus(is_healthy=False, last_check=datetime.now(timezone.utc))
        self._start_time = datetime.now(timezone.utc)
        self._error_handlers: list[Callable] = []
        self._event_listeners: dict[str, list[Callable]] = {}

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration

        Args:
            config: Plugin-specific configuration

        Returns:
            bool: True if initialization successful
        """

    @abstractmethod
    async def start(self) -> bool:
        """
        Start the plugin services

        Returns:
            bool: True if started successfully
        """

    @abstractmethod
    async def stop(self) -> bool:
        """
        Stop the plugin services gracefully

        Returns:
            bool: True if stopped successfully
        """

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """
        Perform health check on the plugin

        Returns:
            HealthStatus: Current health status
        """

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        Main processing method for the plugin

        Args:
            input_data: Input to process

        Returns:
            Any: Processed output
        """

    def get_capabilities(self) -> list[str]:
        """Get list of plugin capabilities"""
        return self.manifest.capabilities

    def get_endpoints(self) -> list[str]:
        """Get API endpoints exposed by plugin"""
        return self.manifest.endpoints

    def register_error_handler(self, handler: Callable):
        """Register error handler callback"""
        self._error_handlers.append(handler)

    def register_event_listener(self, event: str, listener: Callable):
        """Register event listener"""
        if event not in self._event_listeners:
            self._event_listeners[event] = []
        self._event_listeners[event].append(listener)

    async def emit_event(self, event: str, data: Any = None):
        """Emit event to registered listeners"""
        if event in self._event_listeners:
            for listener in self._event_listeners[event]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(data)
                    else:
                        listener(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event}: {e}")

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate configuration against schema"""
        # Basic validation - can be overridden for complex validation
        required_keys = self.manifest.config_schema.get("required", [])
        return all(key in config for key in required_keys)

    def get_uptime(self) -> float:
        """Get plugin uptime in seconds"""
        return (datetime.now(timezone.utc) - self._start_time).total_seconds()


class PluginSystem:
    """
    Central plugin management system for LUKHAS

    Manages plugin lifecycle, health monitoring, and coordination
    """

    def __init__(self):
        self.plugins: dict[str, LukhasPlugin] = {}
        self.plugin_order: list[str] = []  # For dependency resolution
        self._health_check_interval = 30  # seconds
        self._health_check_task = None
        self._event_bus: dict[str, list[Callable]] = {}

    async def register_plugin(self, plugin: LukhasPlugin) -> bool:
        """
        Register a plugin with the system

        Args:
            plugin: Plugin instance to register

        Returns:
            bool: True if registration successful
        """
        try:
            plugin_id = plugin.manifest.id

            # Check dependencies
            if not self._check_dependencies(plugin.manifest.dependencies):
                logger.error(f"Missing dependencies for plugin {plugin_id}")
                return False

            # Store plugin
            self.plugins[plugin_id] = plugin

            # Update execution order based on dependencies
            self._update_plugin_order(plugin_id)

            # Register plugin events
            plugin.register_event_listener("error", self._handle_plugin_error)
            plugin.register_event_listener("status_change", self._handle_status_change)

            logger.info(f"Plugin {plugin_id} registered successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False

    async def initialize_plugin(self, plugin_id: str, config: dict[str, Any]) -> bool:
        """Initialize a specific plugin"""
        if plugin_id not in self.plugins:
            logger.error(f"Plugin {plugin_id} not found")
            return False

        plugin = self.plugins[plugin_id]

        try:
            # Validate configuration
            if not plugin.validate_config(config):
                logger.error(f"Invalid configuration for plugin {plugin_id}")
                return False

            # Initialize
            plugin.status = PluginStatus.INITIALIZING
            success = await plugin.initialize(config)

            if success:
                plugin.status = PluginStatus.READY
                plugin.config = config
                logger.info(f"Plugin {plugin_id} initialized successfully")
            else:
                plugin.status = PluginStatus.ERROR
                logger.error(f"Plugin {plugin_id} initialization failed")

            return success

        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_id}: {e}")
            plugin.status = PluginStatus.ERROR
            return False

    async def start_plugin(self, plugin_id: str) -> bool:
        """Start a specific plugin"""
        if plugin_id not in self.plugins:
            return False

        plugin = self.plugins[plugin_id]

        if plugin.status != PluginStatus.READY:
            logger.error(f"Plugin {plugin_id} not ready to start")
            return False

        try:
            success = await plugin.start()
            if success:
                plugin.status = PluginStatus.ACTIVE
                logger.info(f"Plugin {plugin_id} started successfully")
            return success

        except Exception as e:
            logger.error(f"Error starting plugin {plugin_id}: {e}")
            plugin.status = PluginStatus.ERROR
            return False

    async def stop_plugin(self, plugin_id: str) -> bool:
        """Stop a specific plugin"""
        if plugin_id not in self.plugins:
            return False

        plugin = self.plugins[plugin_id]

        try:
            success = await plugin.stop()
            if success:
                plugin.status = PluginStatus.DISABLED
                logger.info(f"Plugin {plugin_id} stopped successfully")
            return success

        except Exception as e:
            logger.error(f"Error stopping plugin {plugin_id}: {e}")
            return False

    async def get_plugin(self, plugin_id: str) -> Optional[LukhasPlugin]:
        """Get plugin instance if healthy"""
        if plugin_id not in self.plugins:
            return None

        plugin = self.plugins[plugin_id]

        # Check health before returning
        health = await plugin.health_check()
        if health.is_healthy and plugin.status == PluginStatus.ACTIVE:
            return plugin

        logger.warning(f"Plugin {plugin_id} not healthy or active")
        return None

    async def broadcast_event(self, event: str, data: Any = None):
        """Broadcast event to all active plugins"""
        for plugin in self.plugins.values():
            if plugin.status == PluginStatus.ACTIVE:
                await plugin.emit_event(event, data)

    async def start_health_monitoring(self):
        """Start background health monitoring"""
        if self._health_check_task:
            return

        self._health_check_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("Health monitoring started")

    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_check_task
            self._health_check_task = None
            logger.info("Health monitoring stopped")

    async def _health_monitor_loop(self):
        """Background health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)

                for plugin_id, plugin in self.plugins.items():
                    if plugin.status == PluginStatus.ACTIVE:
                        health = await plugin.health_check()
                        plugin.health_status = health

                        if not health.is_healthy:
                            logger.warning(f"Plugin {plugin_id} health check failed")
                            await self.emit_system_event(
                                "plugin_unhealthy",
                                {"plugin_id": plugin_id, "health": health},
                            )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")

    def _check_dependencies(self, dependencies: list[str]) -> bool:
        """Check if all dependencies are available"""
        return all(dep in self.plugins for dep in dependencies)

    def _update_plugin_order(self, plugin_id: str):
        """Update plugin execution order based on dependencies"""
        # Simple topological sort for dependency resolution
        if plugin_id not in self.plugin_order:
            plugin = self.plugins[plugin_id]

            # Add dependencies first
            for dep in plugin.manifest.dependencies:
                if dep in self.plugins and dep not in self.plugin_order:
                    self._update_plugin_order(dep)

            # Add this plugin
            self.plugin_order.append(plugin_id)

    async def _handle_plugin_error(self, error_data: dict[str, Any]):
        """Handle plugin error events"""
        logger.error(f"Plugin error: {error_data}")
        await self.emit_system_event("plugin_error", error_data)

    async def _handle_status_change(self, status_data: dict[str, Any]):
        """Handle plugin status change events"""
        logger.info(f"Plugin status change: {status_data}")
        await self.emit_system_event("plugin_status_change", status_data)

    async def emit_system_event(self, event: str, data: Any = None):
        """Emit system-level event"""
        if event in self._event_bus:
            for listener in self._event_bus[event]:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(data)
                    else:
                        listener(data)
                except Exception as e:
                    logger.error(f"Error in system event listener for {event}: {e}")

    def register_system_event_listener(self, event: str, listener: Callable):
        """Register system event listener"""
        if event not in self._event_bus:
            self._event_bus[event] = []
        self._event_bus[event].append(listener)

    def get_plugin_status_summary(self) -> dict[str, Any]:
        """Get summary of all plugin statuses"""
        return {
            plugin_id: {
                "status": plugin.status.value,
                "health": plugin.health_status.is_healthy,
                "uptime": plugin.get_uptime(),
                "version": plugin.manifest.version,
            }
            for plugin_id, plugin in self.plugins.items()
        }


# Export main classes
__all__ = [
    "HealthStatus",
    "LukhasPlugin",
    "PluginManifest",
    "PluginPriority",
    "PluginStatus",
    "PluginSystem",
]
