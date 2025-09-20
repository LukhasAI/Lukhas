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
import pkgutil
from typing import Any, Dict

_REG: Dict[str, Any] = {}
_DISCOVERY_FLAG = os.getenv("LUKHAS_PLUGIN_DISCOVERY", "off").lower()


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


__all__ = ["register", "resolve", "autoload"]