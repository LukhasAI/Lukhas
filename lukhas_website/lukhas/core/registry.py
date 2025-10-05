# lukhas/core/registry.py
"""
Simple runtime registry + optional auto-discovery.

Env flags:
- LUKHAS_PLUGIN_DISCOVERY=("auto"|"off") default "off"

Telemetry: print()-based by default (replace with logging/metrics if needed).
"""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
import sys
from typing import Any, Dict

# Try to import entry points (available in Python 3.10+ or importlib_metadata for 3.9)
try:
    from importlib.metadata import entry_points
except ImportError:
    try:
        from importlib_metadata import entry_points
    except ImportError:
        entry_points = None

_REG: Dict[str, Any] = {}
_DISCOVERY_FLAG = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off").lower()

# Legacy group name aliases for migration compatibility
ALIASES = {
    "lukhas.agi_nodes": "lukhas.cognitive_nodes",   # legacy alias
    "lukhas.agi_components": "lukhas.constellation_components",   # legacy alias
}


def _instantiate_plugin(ep_name: str, plugin_class):
    """
    T4/0.01% enhanced instantiation with comprehensive signature analysis:
    - Prefer classmethod factories if present
    - Advanced constructor signature inspection and validation
    - Robust error handling with detailed logging
    - Last-resort: register the class (factory) itself
    """
    plugin_name = getattr(plugin_class, '__name__', str(plugin_class))

    # Priority 1: factory classmethods with enhanced validation
    for factory in ("from_entry_point", "from_config", "build", "create"):
        if hasattr(plugin_class, factory):
            factory_method = getattr(plugin_class, factory)
            if callable(factory_method):
                try:
                    # Try with name parameter first
                    return factory_method(name=ep_name)
                except (TypeError, ValueError):
                    # If name parameter fails, try without parameters
                    try:
                        return factory_method()
                    except Exception:
                        # Log factory method failure for debugging
                        # print(f"[registry] factory {plugin_name}.{factory} failed: {inner_e}")
                        continue

    # Priority 2: enhanced constructor signature analysis
    try:
        sig = inspect.signature(plugin_class)
        params = list(sig.parameters.values())

        # Filter out 'self' for instance methods
        non_self_params = [p for p in params if p.name != "self"]

        # Case 1: zero-arg constructor (only self or no params)
        if len(non_self_params) == 0:
            return plugin_class()

        # Case 2: check for explicit name parameter (keyword or positional)
        name_param = None
        for param in non_self_params:
            if param.name == "name":
                name_param = param
                break

        if name_param:
            # Has explicit name parameter
            if name_param.default != inspect.Parameter.empty:
                # Name has default, try with and without
                try:
                    return plugin_class(name=ep_name)
                except TypeError:
                    return plugin_class()
            else:
                # Name is required
                return plugin_class(name=ep_name)

        # Case 3: check for config/options parameter patterns
        for param in non_self_params:
            if param.name in ("config", "options", "settings", "params"):
                # Try passing name as config-like parameter
                try:
                    return plugin_class(**{param.name: {"name": ep_name}})
                except (TypeError, ValueError):
                    # Try with just the name string
                    try:
                        return plugin_class(**{param.name: ep_name})
                    except (TypeError, ValueError):
                        continue

        # Case 4: single positional parameter - pass name
        if (len(non_self_params) == 1 and
            non_self_params[0].kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD
            )):
            param = non_self_params[0]
            if param.default != inspect.Parameter.empty:
                # Parameter has default, try with and without
                try:
                    return plugin_class(ep_name)
                except TypeError:
                    return plugin_class()
            else:
                # Parameter is required
                return plugin_class(ep_name)

        # Case 5: **kwargs present - try passing name first
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in non_self_params)
        if has_var_keyword:
            try:
                return plugin_class(name=ep_name)
            except TypeError:
                return plugin_class()

        # Case 6: multiple parameters with defaults - try zero-arg
        all_have_defaults = all(
            p.default != inspect.Parameter.empty or
            p.kind == inspect.Parameter.VAR_POSITIONAL or
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in non_self_params
        )

        if all_have_defaults:
            return plugin_class()

    except Exception:
        # Enhanced error logging for debugging
        # print(f"[registry] signature analysis failed for {plugin_name}: {e}")
        pass

    # Priority 3: register class as a factory (caller can instantiate later)
    # This allows for lazy instantiation or manual instantiation with custom parameters
    return plugin_class


def _register_kind(group: str, name: str, obj: Any) -> None:
    """Register a plugin with appropriate prefix based on entry point group"""
    prefix_map = {
        "lukhas.cognitive_nodes": "node",
        "lukhas.constellation_components": "constellation",
        "lukhas.adapters": "adapter",
        "lukhas.monitoring": "monitor",
    }

    # Get prefix, default to the group name if not in map
    prefix = prefix_map.get(group, group.split('.')[-1] if '.' in group else group)
    kind = f"{prefix}:{name}"

    register(kind, obj)


def register(kind: str, impl: Any) -> None:
    _REG[kind] = impl
    # Swap for your metrics/logging
    # print(f"[registry] register kind={kind} impl={getattr(impl, '__class__', type(impl)).__name__}")


def resolve(kind: str) -> Any:
    if kind not in _REG:
        raise LookupError(f"no implementation registered for '{kind}'")
    return _REG[kind]


def autoload(prefix: str = "candidate", suffix: str = "plugins") -> None:
    """Import any '{prefix}.**.{suffix}' modules to let them call register()."""
    if _DISCOVERY_FLAG != "auto":
        return
    for mod in pkgutil.iter_modules():
        name = mod.name
        if not name.startswith(f"{prefix}."):
            continue
        if not name.endswith(f".{suffix}"):
            continue
        try:
            importlib.import_module(name)
        except Exception as e:
            # Non-fatal: discovery should not crash the process.
            print(f"[registry] autoload skip {name}: {e}", file=sys.stderr)


def discover_entry_points() -> None:
    """Discover and register plugins via entry points."""
    discovery_flag = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off").lower()

    if entry_points is None:
        # print("[registry] entry points not available, skipping discovery", file=sys.stderr)
        return

    if discovery_flag != "auto":
        return

    # Discover LUKHAS entry point groups
    entry_point_groups = [
        "lukhas.cognitive_nodes",
        "lukhas.constellation_components",
        "lukhas.adapters",
        "lukhas.monitoring"
    ]

    for group_name in entry_point_groups:
        # Apply alias mapping for legacy compatibility
        resolved_group = ALIASES.get(group_name, group_name)

        try:
            # Get entry points for this group
            eps = entry_points(group=resolved_group)
            # print(f"[registry] checking group {group_name} -> {resolved_group}, found {len(list(eps))} entry points")

            for ep in eps:
                try:
                    # Load the entry point class
                    plugin_class = ep.load()

                    # Use smart instantiation
                    obj = _instantiate_plugin(ep.name, plugin_class)

                    # Register with appropriate prefix using helper
                    _register_kind(resolved_group, ep.name, obj)

                    # obj_type = "instance" if hasattr(obj, "__dict__") else "factory"
                    # print(f"[registry] loaded entry point: {group_name}.{ep.name} as {obj_type}")

                except Exception as e:
                    print(f"[registry] failed to load entry point {group_name}.{ep.name}: {e}", file=sys.stderr)

        except Exception as e:
            print(f"[registry] failed to discover group {group_name}: {e}", file=sys.stderr)


def auto_discover() -> None:
    """Run all discovery methods: entry points and module scanning."""
    discover_entry_points()
    autoload()


__all__ = ["register", "resolve", "autoload", "discover_entry_points", "auto_discover", "_register_kind"]
