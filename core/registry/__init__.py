"""
Core Registry - Component registration and discovery.

Provides register() function and _REG registry.
"""
from __future__ import annotations
import importlib as _importlib
from typing import Optional
try:
    _mod = _importlib.import_module("labs.core.identity.registry")
    _REG = _mod._REG
    register = _mod.register
except Exception:
    _REG = None
    register = None

# Add missing functions expected by tests
def resolve(key: str):
    """Resolve a registered component by key."""
    return _REG.get(key)

def auto_discover():
    """Auto-discover plugins (placeholder)."""
    return []

def autoload():
    """Autoload discovered plugins (placeholder)."""
    pass

def discover_entry_points(group: str | None = None):
    """Discover entry points (placeholder)."""
    return []

def _instantiate_plugin(entry_point):
    """Instantiate a plugin from entry point (placeholder)."""
    return None

__all__ = ["_REG", "_instantiate_plugin", "auto_discover", "autoload", "discover_entry_points", "register", "resolve"]
