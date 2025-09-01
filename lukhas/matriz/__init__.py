"""Compatibility shim: expose the top-level `matriz` package under `lukhas.matriz`.

This file allows tests and modules that import `lukhas.matriz` to find the
`matriz` implementation included at the repository root.
"""

try:
    # Prefer the installed/packaged matriz if available
    import matriz as _matriz  # type: ignore
except Exception:
    # Fallback: try to import from repository root
    import importlib

    _matriz = importlib.import_module("matriz")

# Re-export common symbols for convenience
from importlib import import_module as _import_module

__all__ = getattr(_matriz, "__all__", [])

for _name in __all__:
    globals()[_name] = getattr(_matriz, _name)
"""
LUKHAS AI MΛTRIZ Module
======================

Distributed consciousness architecture with cognitive DNA system.
Implements the MΛTRIZ cognitive framework for consciousness nodes.

Trinity Framework: ⚛️🧠🛡️
"""

import logging

logger = logging.getLogger(__name__)

# Import runtime components
try:
    from .runtime.policy import PolicyEngine
    from .runtime.supervisor import RuntimeSupervisor

    # Alias for backward compatibility
    MatrizNode = RuntimeSupervisor

except ImportError as e:
    logger.warning(f"Failed to import MΛTRIZ runtime components: {e}")
    RuntimeSupervisor = None
    PolicyEngine = None
    MatrizNode = None

__all__ = [
    "MatrizNode",  # Alias
    "PolicyEngine",
    "RuntimeSupervisor",
]

__version__ = "1.0.0"
