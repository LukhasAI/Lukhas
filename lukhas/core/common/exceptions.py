"""
Bridge for `lukhas.core.common.exceptions`.
Prefers richer backends, falls back to minimal stubs.
"""
from __future__ import annotations
from importlib import import_module
from typing import Optional, List

__all__: List[str] = []

def _bind_from(modname: str) -> bool:
    try:
        src = import_module(modname)
    except Exception:
        return False
    # Re-export public names explicitly
    exports = [n for n in dir(src) if not n.startswith("_")]
    for n in exports:
        globals()[n] = getattr(src, n)
    globals()["__all__"] = exports
    return True

# Richest → leanest backends
for _m in (
    "candidate.core.common.exceptions",
    "core.common.exceptions",
    "lukhas_website.lukhas.core.common.exceptions",
):
    if _bind_from(_m):
        break
else:
    # Minimal, test-friendly fallbacks
    class LUKHASError(Exception): ...
    class ConfigError(LUKHASError): ...
    class DependencyError(LUKHASError): ...
    class InvariantViolation(LUKHASError): ...
    class NotReadyError(LUKHASError): ...
    __all__ = [
        "LUKHASError",
        "ConfigError",
        "DependencyError",
        "InvariantViolation",
        "NotReadyError",
    ]
