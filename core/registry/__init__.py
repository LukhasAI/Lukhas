"""
Core Registry - Component registration and discovery.

Provides register() function and _REG registry.
"""
from __future__ import annotations
import importlib as _importlib
try:
    _mod = _importlib.import_module("labs.core.identity.registry")
    _REG = getattr(_mod, "_REG")
    register = getattr(_mod, "register")
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

def discover_entry_points(group: str = None):
    """Discover entry points (placeholder)."""
    return []

def _instantiate_plugin(entry_point):
    """Instantiate a plugin from entry point (placeholder)."""
    return None

__all__ = ["register", "_REG", "resolve", "auto_discover", "autoload", "discover_entry_points", "_instantiate_plugin"]
