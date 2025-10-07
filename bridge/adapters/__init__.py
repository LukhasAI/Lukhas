"""Pre-freeze bridge surface for `bridge.adapters` expected by tests."""
from __future__ import annotations

from lukhas._bridgeutils import bridge

_mod: object | None = None
_exports: dict[str, object] = {}

try:
    _mod, _exports, __all__ = bridge(
        candidates=(
            "lukhas_website.lukhas.bridge.adapters",
            "candidate.bridge.adapters",
        ),
        names=("OpenAIAdapter", "AnthropicAdapter", "BedrockAdapter", "BridgeTraceLogger"),
    )
    globals().update(_exports)
except ModuleNotFoundError:
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
    target = factory if factory is not None else _FallbackAdapter
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
