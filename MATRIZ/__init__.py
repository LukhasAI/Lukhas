"""Lowercase compatibility facade for the uppercase `MATRIZ` package.

Makes `matriz.<subpkg>` resolve to `MATRIZ.<subpkg>` so tests that import
`matriz.adapters.*` (and friends) can collect without moving files around.
"""
from __future__ import annotations

import importlib
import sys
from types import ModuleType

__all__: list[str] = []

def _alias(subpkg: str) -> ModuleType | None:
    """Map matriz.<subpkg> -> MATRIZ.<subpkg> if available, caching in sys.modules."""
    src_name = f"MATRIZ.{subpkg}"
    dst_name = f"{__name__}.{subpkg}"
    try:
        mod = importlib.import_module(src_name)
    except Exception:
        return None
    sys.modules[dst_name] = mod
    if subpkg not in __all__:
        __all__.append(subpkg)
    return mod

# Always expose the uppercase home for debugging/compat
try:
    MATRIZ = importlib.import_module("MATRIZ")
    __all__.append("MATRIZ")
except Exception:
    MATRIZ = None  # type: ignore[assignment]

# Canonical direct wires
if _alias("core") is None:
    # Leave core optional; some environments provide it elsewhere
    pass

# node_contract is a single module at top-level (MATRIZ/node_contract.py).
# Import it through the lowercase name to keep existing code stable.
try:
    node_contract = importlib.import_module("MATRIZ.node_contract")
    sys.modules[__name__ + ".node_contract"] = node_contract
    __all__.append("node_contract")
except Exception:
    pass

# High-value subpackages that tests import:
for _name in ("adapters", "runtime", "nodes", "utils", "visualization"):
    _alias(_name)

# Lazy fallback: if someone touches matriz.<anything>, try to load MATRIZ.<anything>
def __getattr__(name: str):
    mod = _alias(name)
    if mod is not None:
        return mod
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
