"""Bridge shim for `bridge.api.analysis` with explicit fallback symbols."""
from __future__ import annotations

from _bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

try:
    _mod, _exports, __all__ = bridge(
        candidates=(
            "lukhas_website.bridge.api.analysis",
            "candidate.bridge.api.analysis",
        ),
        names=("analysis_routes",),
    )
    globals().update(_exports)
except ModuleNotFoundError:
    __all__ = []

if not isinstance(__all__, list):
    __all__ = list(__all__)


if "analysis_routes" not in globals():
    def analysis_routes(*_args: object, **_kwargs: object) -> list[object]:
        """Fallback analysis_routes stub returning an empty payload."""

        return []

    __all__.append("analysis_routes")

del _mod, _exports
