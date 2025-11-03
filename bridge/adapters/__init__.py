"""Pre-freeze bridge surface for `bridge.adapters` expected by tests."""
from __future__ import annotations

from _bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

_CANDIDATE_PATHS = (
    "lukhas_website.bridge.adapters",
    "candidate.bridge.adapters",
    "labs.bridge.adapters",
)

_names = ("OpenAIAdapter", "AnthropicAdapter", "BedrockAdapter", "BridgeTraceLogger")

__all__: list[str] = []
for _candidate in _CANDIDATE_PATHS:
    try:
        _mod, _exports, _resolved = bridge(candidates=(_candidate,), names=_names)
    except (ModuleNotFoundError, AttributeError):
        continue
    else:
        __all__ = list(_resolved)
        globals().update(_exports)
        break
else:
    __all__ = []

if not isinstance(__all__, list):
    __all__ = list(__all__)


class _FallbackAdapter:
    """No-op adapter stub for environments without concrete adapters."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs

    def run(self, *args: object, **kwargs: object) -> None:
        return None


def _ensure(name: str, factory: type | None = None) -> None:
    if name in globals():
        return
    target = factory if factory is not None else _FallbackAdapter  # noqa: F821  # TODO: _FallbackAdapter
    globals()[name] = target
    __all__.append(name)


_ensure("OpenAIAdapter")
_ensure("AnthropicAdapter")
_ensure("BedrockAdapter")


class _BridgeTraceLogger:
    """Minimal trace logger that collects entries in memory."""

    def __init__(self) -> None:
        self.entries: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def log(self, *args: object, **kwargs: object) -> None:
        self.entries.append((args, kwargs))


_ensure("BridgeTraceLogger", _BridgeTraceLogger)

del _mod, _exports, _ensure, _FallbackAdapter, _BridgeTraceLogger
