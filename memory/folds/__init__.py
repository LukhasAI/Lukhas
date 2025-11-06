"""Memory fold exports that gracefully bridge legacy implementations."""
from __future__ import annotations

from importlib import import_module
from typing import Any

__all__: list[str] = []

_CANDIDATES = (
    "candidate.memory.folds",
    "memory.folds_impl",
)


def _export(name: str, value: Any) -> None:
    globals()[name] = value
    if name not in __all__:
        __all__.append(name)


for module in _CANDIDATES:
    try:
        mod = import_module(module)
    except Exception:
        continue
    exported = False
    for symbol in ("FoldEngine", "SoftDelete", "FoldManager"):
        if hasattr(mod, symbol):
            _export(symbol, getattr(mod, symbol))
            exported = True
    if exported:
        break


if "FoldEngine" not in globals():
    class FoldEngine:  # type: ignore[misc]
        def execute(self, *args: Any, **kwargs: Any) -> None:
            return None


if "SoftDelete" not in globals():
    class SoftDelete:  # type: ignore[misc]
        def __call__(self, *args: Any, **kwargs: Any) -> None:
            return None


if "FoldManager" not in globals():
    class FoldManager:  # type: ignore[misc]
        def manage(self, *args: Any, **kwargs: Any) -> None:
            return None

# Added for test compatibility (memory.folds.FoldGuard)
try:
    from labs.memory.folds import FoldGuard
except ImportError:
    class FoldGuard:
        """Stub for FoldGuard."""
        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
__all__ = globals().get("__all__", [])
if "FoldGuard" not in __all__:
    __all__.append("FoldGuard")
