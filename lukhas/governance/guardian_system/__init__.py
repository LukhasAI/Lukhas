"""Bridge shim for `lukhas.governance.guardian_system` with safe fallbacks."""
from __future__ import annotations

from importlib import import_module

_mod: object | None = None
_exports: dict[str, object] = {}
__all__ = []

# Try backends with graceful AttributeError handling
for _candidate in (
    "lukhas_website.lukhas.governance.guardian_system",
    "candidate.governance.guardian_system",
):
    try:
        _mod = import_module(_candidate)
        # Extract available symbols (don't fail if missing)
        for _name in ("Guardian", "GuardianSystem", "PolicyGuard", "PolicyResult", "ReplayDecision"):
            if hasattr(_mod, _name):
                globals()[_name] = getattr(_mod, _name)
                __all__.append(_name)
        if __all__:  # If we got anything, stop searching
            break
    except (ModuleNotFoundError, ImportError, AttributeError):
        continue

if not isinstance(__all__, list):
    __all__ = list(__all__)


def _ensure_symbol(name: str) -> None:
    if name in globals():
        return

    class _Stub:
        """Fallback stub for missing guardian system symbol."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

    _Stub.__name__ = name
    globals()[name] = _Stub
    __all__.append(name)


for _symbol in ("Guardian", "PolicyGuard", "PolicyResult", "ReplayDecision"):
    _ensure_symbol(_symbol)

del _symbol, _ensure_symbol, _mod, _exports
