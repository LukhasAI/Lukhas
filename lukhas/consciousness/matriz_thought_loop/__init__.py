"""Bridge: MATRIZ Thought Loop."""
from __future__ import annotations
from lukhas._bridgeutils import resolve_first, export_from, safe_guard

# Prefer website → candidate → legacy
_candidates = (
    "lukhas_website.lukhas.consciousness.matriz_thought_loop",
    "candidate.consciousness.matriz_thought_loop",
    "consciousness.matriz_thought_loop_impl",
)

try:
    _mod = resolve_first(_candidates)
    _exports = export_from(_mod, names=("MATRIZProcessingContext", "MATRIZThoughtLoop"))
    globals().update(_exports)
    __all__ = list(_exports.keys())
except ModuleNotFoundError:
    # No backend exists - provide stubs so imports succeed
    class _NotImplementedMixin:
        def __init__(self, *a, **k):
            raise NotImplementedError("MATRIZ Thought Loop not wired yet")

    class MATRIZProcessingContext(_NotImplementedMixin):
        pass

    class MATRIZThoughtLoop(_NotImplementedMixin):
        pass

    __all__ = ["MATRIZProcessingContext", "MATRIZThoughtLoop"]

safe_guard(__name__, __all__)
