"""Unified registry entry point.

This package exposes the new plugin registry interface while preserving
the legacy module-level helpers (``register``/``resolve``/``autoload``)
that the wider codebase still depends on.  Without this shim, importing
``lukhas.core.registry`` would surface only the plugin classes and break
the simpler runtime registry utilities.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional

from .plugin_registry import (
    LUKHASPlugin,
    PluginBase,
    PluginInfo,
    PluginRegistry,
    get_plugin_registry,
    register_plugin,
)


def _load_legacy_registry() -> Optional[ModuleType]:
    """Load the legacy ``lukhas.core.registry`` module if it still exists."""

    legacy_path = Path(__file__).resolve().parent.parent / "registry.py"
    if not legacy_path.exists():  # pragma: no cover - legacy file might be removed later
        return None

    module_name = "lukhas.core._registry_legacy"
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_legacy_module = _load_legacy_registry()


def _get_attr(name: str, fallback: Optional[Callable[[], Any]] = None) -> Any:
    if _legacy_module and hasattr(_legacy_module, name):
        return getattr(_legacy_module, name)
    if fallback is not None:
        return fallback()
    raise AttributeError(f"Legacy registry export '{name}' is not available")


# Legacy runtime registry exports (kept for backwards compatibility)
register: Callable[..., None] = _get_attr("register")
resolve: Callable[..., Any] = _get_attr("resolve")
autoload: Callable[..., None] = _get_attr("autoload")
discover_entry_points: Callable[..., None] = _get_attr("discover_entry_points")
auto_discover: Callable[..., None] = _get_attr("auto_discover")
_register_kind: Callable[..., None] = _get_attr("_register_kind")
_instantiate_plugin: Callable[..., Any] = _get_attr("_instantiate_plugin")
_REG_value = _get_attr("_REG", fallback=dict)
if not isinstance(_REG_value, dict):  # pragma: no cover - defensive
    _REG_value = dict(_REG_value)
_REG: dict[str, Any] = _REG_value


__all__ = [
    "PluginRegistry",
    "PluginBase",
    "PluginInfo",
    "LUKHASPlugin",
    "get_plugin_registry",
    "register_plugin",
    # Legacy runtime helpers
    "register",
    "resolve",
    "autoload",
    "discover_entry_points",
    "auto_discover",
    "_register_kind",
    "_instantiate_plugin",
    "_REG",
]

__version__ = "1.0.0"
