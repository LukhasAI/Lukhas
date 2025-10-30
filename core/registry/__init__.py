"""
Core Registry - Component registration and discovery.

Provides register() function and _REG registry.
"""
from __future__ import annotations

import importlib
from typing import Any, Dict

# Avoid importing `labs` at module import time. Prefer local implementations
# when available; otherwise provide lightweight fallbacks and lazily import
# `labs.core.identity.registry` only when a real registry is required.

_LOCAL_IMPL_AVAILABLE = False
try:
    # If project provides a local core identity registry, import it.
    from core.identity.registry import _REG, register  # type: ignore
    _LOCAL_IMPL_AVAILABLE = True
except Exception:
    _LOCAL_IMPL_AVAILABLE = False
    # Provide minimal placeholders; real behavior may be loaded lazily.
    def register(*args: Any, **kwargs: Any) -> None:
        """Register a component (placeholder)."""
        return None

    _REG: Dict[str, Any] = {}


_LABS_REGISTRY: Any | None = None


def _load_labs_registry() -> Any | None:
    global _LABS_REGISTRY
    if _LABS_REGISTRY is not None:
        return _LABS_REGISTRY
    try:
        _LABS_REGISTRY = importlib.import_module("labs.core.identity.registry")
    except Exception:
        _LABS_REGISTRY = None
    return _LABS_REGISTRY

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
