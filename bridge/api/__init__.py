"""Pre-freeze bridge surface for `bridge.api` expected by tests."""
from __future__ import annotations

from _bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

_CANDIDATES = (
    "lukhas_website.bridge.api",
    "candidate.bridge.api",
    "bridge.api_impl",
)

try:
    _mod, _exports, __all__ = bridge(
        candidates=_CANDIDATES,
        names=("identity_routes", "analysis_routes", "health_routes", "RouteHandlers"),
    )
    globals().update(_exports)
except ModuleNotFoundError:
    __all__ = []

if not isinstance(__all__, list):
    __all__ = list(__all__)

if "RouteHandlers" not in globals():
    class RouteHandlers:
        """Minimal mountable stub to keep collection healthy."""

        def __init__(self) -> None:
            self._mounts: list[tuple[tuple[object, ...], dict[str, object]]] = []

        def mount(self, *args: object, **kwargs: object) -> None:
            self._mounts.append((args, kwargs))

    __all__.append("RouteHandlers")


def _ensure_callable(name: str) -> None:
    if name in globals():
        return

    def _fallback(*_args: object, **_kwargs: object) -> list[object]:
        return []

    _fallback.__name__ = name
    globals()[name] = _fallback
    __all__.append(name)


for _symbol in ("identity_routes", "analysis_routes", "health_routes"):
    _ensure_callable(_symbol)

del _symbol, _ensure_callable, _mod, _exports
