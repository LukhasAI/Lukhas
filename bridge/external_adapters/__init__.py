"""Pre-freeze bridge surface for `bridge.external_adapters`."""
from __future__ import annotations

from _bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

try:
    _mod, _exports, __all__ = bridge(
        candidates=(
            "lukhas_website.bridge.external_adapters",
            "candidate.bridge.external_adapters",
        ),
        names=("InferenceRequest", "InferenceResponse"),
    )
    globals().update(_exports)
except ModuleNotFoundError:
    __all__ = []

if not isinstance(__all__, list):
    __all__ = list(__all__)


class _Stub:
    """Generic container used when inference adapters are not wired."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs


for _symbol in ("InferenceRequest", "InferenceResponse"):
    if _symbol not in globals():
        globals()[_symbol] = _Stub
        __all__.append(_symbol)

del _mod, _exports, _Stub, _symbol
