"""Bridge: Consciousness Stream."""
from __future__ import annotations
from lukhas._bridgeutils import resolve_first, export_from, safe_guard

_candidates = (
    "lukhas_website.lukhas.consciousness.consciousness_stream",
    "candidate.consciousness.stream",
    "consciousness.stream",
    "core.consciousness_stream",
)

try:
    _mod = resolve_first(_candidates)
    _exports = export_from(_mod, names=("ConsciousnessStream", "StreamEvent"))
    globals().update(_exports)
    __all__ = list(_exports.keys())
except ModuleNotFoundError:
    # No backend - provide stubs
    class _NotImplementedMixin:
        def __init__(self, *a, **k):
            raise NotImplementedError("Consciousness Stream not wired yet")

    class ConsciousnessStream(_NotImplementedMixin):
        pass

    class StreamEvent:
        pass

    __all__ = ["ConsciousnessStream", "StreamEvent"]

safe_guard(__name__, __all__)
