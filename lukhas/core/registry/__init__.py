"""
LUKHAS Core Registry Module

Plugin discovery and management system for enterprise-grade extensibility.
"""

from .plugin_registry import (
    PluginRegistry,
    PluginBase,
    PluginInfo,
    LUKHASPlugin,
    get_plugin_registry,
    register_plugin,
)

__all__ = [
    "PluginRegistry",
    "PluginBase",
    "PluginInfo",
    "LUKHASPlugin",
    "get_plugin_registry",
    "register_plugin",
]

__version__ = "1.0.0"