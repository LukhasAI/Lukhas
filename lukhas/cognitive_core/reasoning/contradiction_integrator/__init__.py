"""Bridge: lukhas.cognitive_core.reasoning.contradiction_integrator -> canonical."""
from __future__ import annotations

try:
    from consciousness.cognitive.reasoning.contradiction_integrator import *  # noqa: F401, F403
    __all__ = [n for n in locals().keys() if not n.startswith("_")]
except Exception:
    __all__ = []
