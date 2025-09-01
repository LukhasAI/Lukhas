"""Compatibility shim: expose the top-level `matriz` package under ``lukhas.matriz``.

This module prefers an installed ``matriz`` package, otherwise falls back to
the local repository copy. It also re-exports a small set of runtime symbols
when available.
"""

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


try:
    # Prefer the installed/packaged matriz if available
    import matriz as _matriz  # type: ignore
except Exception:
    # Fallback: try to import from repository root
    _matriz = importlib.import_module("matriz")


# Re-export common symbols if present in the upstream package
__all__ = getattr(_matriz, "__all__", [])
for _name in __all__:
    globals()[_name] = getattr(_matriz, _name)


# Attempt to import local runtime helpers (optional)
try:
    from .runtime.policy import PolicyEngine  # type: ignore
    from .runtime.supervisor import RuntimeSupervisor  # type: ignore

    # Alias for backward compatibility
    MatrizNode = RuntimeSupervisor
except Exception as e:  # pragma: no cover - best-effort import
    logger.info(f"MΛTRIZ runtime components not available: {e}")
    RuntimeSupervisor = None  # type: ignore
    PolicyEngine = None  # type: ignore
    MatrizNode = None  # type: ignore


__all__ += [
    "MatrizNode",
    "PolicyEngine",
    "RuntimeSupervisor",
]

__version__ = "1.0.0"
