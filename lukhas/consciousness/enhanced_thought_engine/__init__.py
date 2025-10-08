"""Bridge for enhanced thought engine surfaces with safe fallbacks."""
from __future__ import annotations

from importlib import import_module

from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.consciousness.enhanced_thought_engine",
    "candidate.consciousness.enhanced_thought_engine",
    "consciousness.enhanced_thought_engine_impl",
)
globals().update(_exports)

if not isinstance(__all__, list):
    __all__ = list(__all__)

try:
    backend = import_module("candidate.consciousness.enhanced_thought_engine")
except Exception:
    backend = None
else:
    symbols = export_from(backend)
    for name in ("EnhancedThoughtEngine", "EnhancedContext", "EnhancedConfig"):
        if name in symbols and name not in globals():
            globals()[name] = symbols[name]
            __all__.append(name)


def _ensure(name: str, factory: type | None = None) -> None:
    if name in globals():
        return

    class _Stub:
        """Fallback implementation when enhanced engine backend missing."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

    target = factory if factory is not None else _Stub
    globals()[name] = target
    __all__.append(name)


_ensure("EnhancedThoughtEngine")


class EnhancedContext:
    """Default context stub aggregated when backend unavailable."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs


_ensure("EnhancedContext", EnhancedContext)


class EnhancedConfig:
    """Configuration stub for enhanced thought engine."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs


_ensure("EnhancedConfig", EnhancedConfig)

safe_guard(__name__, __all__)

del _exports, backend, _ensure
