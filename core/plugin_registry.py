"""Bridge module for core.plugin_registry → labs.core.plugin_registry"""
from __future__ import annotations

from labs.core.plugin_registry import PluginRegistry, RegistryManager, create_registry

__all__ = ["PluginRegistry", "RegistryManager", "create_registry"]
