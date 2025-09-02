"""Central plugin registry for the LUKHAS system.

ΛTAG: plugin_registry
"""

from __future__ import annotations

import importlib.metadata
import logging
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Supported plugin categories."""

    ETHICS_POLICY = "ethics_policy"
    MEMORY_HOOK = "memory_hook"
    ORCHESTRATION_AGENT = "orchestration_agent"
    SYMBOLIC_PROCESSOR = "symbolic_processor"


class Plugin(ABC):
    """Base class for all plugins."""

    @abstractmethod
    def get_plugin_type(self) -> PluginType:
        """Return the plugin type."""
        raise NotImplementedError

    @abstractmethod
    def get_plugin_name(self) -> str:
        """Return the plugin name."""
        raise NotImplementedError

    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version."""
        raise NotImplementedError


class PluginRegistry:
    """Registry handling plugin discovery and access."""

    def __init__(self) -> None:
        self._plugins: dict[PluginType, dict[str, Plugin]] = {pt: {} for pt in PluginType}
        self._load_entry_points()

    def _load_entry_points(self) -> None:
        """Load plugins defined via package entry points."""
        try:
            eps = importlib.metadata.entry_points()
            # Handle Python 3.9 vs 3.10+ compatibility
            if hasattr(eps, "select"):  # Python 3.10+
                group = eps.select(group="lukhas.plugins")
            elif isinstance(eps, dict) and "lukhas.plugins" in eps:  # Python 3.9
                group = eps["lukhas.plugins"]
            else:
                group = []
            for ep in group:
                try:
                    plugin_cls = ep.load()
                    plugin = plugin_cls()
                    self.register_plugin(plugin)
                except Exception as exc:
                    logger.error("Failed to load plugin %s: %s", ep.name, exc)
        except Exception as exc:
            logger.error("Entry point discovery failed: %s", exc)

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin instance."""
        ptype = plugin.get_plugin_type()
        pname = plugin.get_plugin_name()
        self._plugins[ptype][pname] = plugin

    def get_plugin(self, plugin_type: PluginType, name: str) -> Plugin | None:
        """Retrieve a plugin by type and name."""
        return self._plugins[plugin_type].get(name)

    def list_plugins(self, plugin_type: PluginType | None = None) -> list[Plugin]:
        """List registered plugins by type or all."""
        if plugin_type:
            return list(self._plugins[plugin_type].values())
        all_plugins: list[Plugin] = []
        for plugins in self._plugins.values():
            all_plugins.extend(plugins.values())
        return all_plugins
