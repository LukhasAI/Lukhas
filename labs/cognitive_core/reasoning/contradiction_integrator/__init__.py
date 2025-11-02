"""Bridge: candidate.cognitive_core.reasoning.contradiction_integrator."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

# This submodule is known to live under consciousness.cognitive.* in older trees
_CANDIDATES = (
    "consciousness.cognitive.reasoning.contradiction_integrator",
    "lukhas_website.consciousness.cognitive.reasoning.contradiction_integrator",
    "labs.consciousness.cognitive.reasoning.contradiction_integrator",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
