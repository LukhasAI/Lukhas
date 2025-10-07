"""Bridge shim for `lukhas.governance.guardian_system` with safe fallbacks."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

try:
    _mod, _exports, __all__ = bridge(
        candidates=(
            "lukhas_website.lukhas.governance.guardian_system",
            "candidate.governance.guardian_system",
        ),
        names=("Guardian", "PolicyGuard", "PolicyResult", "ReplayDecision"),
    )
    globals().update(_exports)
except ModuleNotFoundError:
    __all__ = []

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
