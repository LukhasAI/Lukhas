"""
Compatibility shim: top-level `dream` module → labs.consciousness.dream

This shim is temporary. It emits a DeprecationWarning to encourage imports
to move to `labs.consciousness.dream`.

The canonical dream implementation is in labs/consciousness/dream/.
This compatibility layer will be removed after 2 releases (est. Q2 2026).
"""
import importlib
import warnings

warnings.warn(
    "Top-level package 'dream' is deprecated; import 'labs.consciousness.dream' instead. "
    "This compatibility shim will be removed after 2 releases.",
    DeprecationWarning,
    stacklevel=2
)

# Dynamically load the canonical module
_canonical_module = importlib.import_module("labs.consciousness.dream")

# Re-export all public symbols
__all__ = getattr(_canonical_module, '__all__', [])

# Preserve module reference for backwards compatibility
dream_module = _canonical_module
