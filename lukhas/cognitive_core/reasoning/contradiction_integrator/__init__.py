"""Bridge: lukhas.cognitive_core.reasoning.contradiction_integrator (ContradictionIntegrator class)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates, safe_guard, deprecate

_CANDIDATES = (
    "lukhas_website.lukhas.cognitive_core.reasoning.contradiction_integrator",
    "candidate.cognitive_core.reasoning.contradiction_integrator",
    "consciousness.cognitive.reasoning.contradiction_integrator",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
safe_guard(__name__, __all__)
deprecate(__name__, "prefer candidate.cognitive_core.reasoning.contradiction_integrator")
