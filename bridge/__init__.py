"""Compatibility shim for the historic ``bridge`` package.

The production implementation of the bridge surface now lives in
``lukhas_website.lukhas.bridge`` with development variants in ``labs.bridge``.
Smoke tests – especially the legacy branding and wrapper checks – still
import symbols directly from ``bridge``.  The goal of this module is to bridge
those imports to the backed implementations while keeping the test matrix
healthy even when the real backends are unavailable.
"""

from __future__ import annotations

from typing import Any, Mapping

from _bridgeutils import bridge, resolve_first

_BACKEND_CANDIDATES = (
    "lukhas_website.lukhas.bridge",
    "labs.bridge",
)

_mod: object | None = None
_exports: Mapping[str, Any] | None = None

try:
    _mod, _exports, __all__ = bridge(
        candidates=_BACKEND_CANDIDATES,
        names=(
            "BRIDGE_ACTIVE",
            "BRIDGE_DRY_RUN",
            "MODULE_VERSION",
            "APIBridge",
            "BridgeWrapper",
            "MultiModelOrchestrator",
            "get_bridge_status",
            "get_bridge_wrapper",
        ),
    )
except ModuleNotFoundError:
    __all__ = []
else:
    globals().update(_exports)

if not isinstance(__all__, list):
    __all__ = list(__all__)


def _register(name: str, value: Any) -> None:
    globals()[name] = value
    if name not in __all__:
        __all__.append(name)


if "MODULE_VERSION" in globals():
    _register("__version__", globals()["MODULE_VERSION"])
    _register("VERSION", globals()["MODULE_VERSION"])


if "BridgeWrapper" not in globals():

    class BridgeWrapper:  # pragma: no cover - smoke-test stub
        """Fallback BridgeWrapper that exposes a minimal interface."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

    _register("BridgeWrapper", BridgeWrapper)


if "get_bridge_wrapper" not in globals():

    def get_bridge_wrapper() -> BridgeWrapper | None:  # pragma: no cover - stub
        return None

    _register("get_bridge_wrapper", get_bridge_wrapper)


if "MultiModelOrchestrator" not in globals():

    class MultiModelOrchestrator:  # pragma: no cover - smoke-test stub
        """Placeholder orchestrator used when backends are absent."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

    _register("MultiModelOrchestrator", MultiModelOrchestrator)


_BRANDING_BACKENDS = (
    "lukhas_website.lukhas.branding_bridge",
    "labs.branding_bridge",
    "brain",
)

_branding = None
for _candidate in _BRANDING_BACKENDS:
    try:
        _branding = resolve_first((_candidate,))
    except ModuleNotFoundError:
        continue
    else:
        break

if _branding is not None:
    for _symbol in ("BrandContext", "get_brand_voice", "build_context"):
        if hasattr(_branding, _symbol):
            _register(_symbol, getattr(_branding, _symbol))

    if hasattr(_branding, "BRANDING_AVAILABLE"):
        _register("BRIDGE_BRANDING_AVAILABLE", getattr(_branding, "BRANDING_AVAILABLE"))
else:

    class BrandContext:  # pragma: no cover - smoke-test stub
        """Minimal brand context used when branding bridge is missing."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

    def _noop(*_args: Any, **_kwargs: Any) -> Any:  # pragma: no cover - stub helper
        return {
            "valid": False,
            "issues": ["branding backend unavailable"],
        }

    _register("BrandContext", BrandContext)
    _register("get_brand_voice", _noop)
    _register("build_context", _noop)
    _register("BRIDGE_BRANDING_AVAILABLE", False)


del _mod, _exports, _candidate, _branding, _BRANDING_BACKENDS, _BACKEND_CANDIDATES, _register
if "_noop" in globals():
    del _noop
