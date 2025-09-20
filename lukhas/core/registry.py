# lukhas/core/registry.py
"""
Simple runtime registry + optional auto-discovery.

Env flags:
- LUKHAS_PLUGIN_DISCOVERY=("auto"|"off") default "off"

Telemetry: print()-based by default (replace with logging/metrics if needed).
"""

from __future__ import annotations
import os
import sys
import importlib
import inspect
import pkgutil
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
    T4/0.01% instantiation:
    - Prefer classmethod factories if present
    - Else inspect __init__ to decide whether to pass name
    - Else last-resort: register the class (factory) itself
    """
    # Priority 1: factory classmethods
    for factory in ("from_entry_point", "from_config", "build"):
        if hasattr(plugin_class, factory) and callable(getattr(plugin_class, factory)):
            try:
                return getattr(plugin_class, factory)(name=ep_name)
            except TypeError:
                try:
                    return getattr(plugin_class, factory)()
                except Exception:
                    continue

    # Priority 2: constructor signature
    try:
        sig = inspect.signature(plugin_class)
        params = list(sig.parameters.values())

        # zero-arg constructor
        if len(params) == 0 or (len(params) == 1 and params[0].name == "self"):
            return plugin_class()

        # constructor accepts a name (positional or kw)
        names = [p.name for p in params if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)]
        if "name" in names:
            return plugin_class(name=ep_name)

        # one positional arg after self → pass name
        if len(params) >= 2 and params[1].kind in (params[1].POSITIONAL_ONLY, params[1].POSITIONAL_OR_KEYWORD):
            return plugin_class(ep_name)

    except Exception:
        pass

    # Priority 3: register class as a factory (caller can instantiate later)
    return plugin_class


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

                    # Register with appropriate prefix
                    if resolved_group == "lukhas.cognitive_nodes":
                        register(f"node:{ep.name}", obj)
                    elif resolved_group == "lukhas.constellation_components":
                        register(f"constellation:{ep.name}", obj)
                    elif resolved_group == "lukhas.adapters":
                        register(f"adapter:{ep.name}", obj)
                    elif resolved_group == "lukhas.monitoring":
                        register(f"monitor:{ep.name}", obj)

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


__all__ = ["register", "resolve", "autoload", "discover_entry_points", "auto_discover"]