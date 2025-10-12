"""Bridge: candidate.cognitive_core.reasoning.contradiction_integrator."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

# This submodule is known to live under consciousness.cognitive.* in older trees
_CANDIDATES = (
    "consciousness.cognitive.reasoning.contradiction_integrator",
    "lukhas_website.lukhas.consciousness.cognitive.reasoning.contradiction_integrator",
    "candidate.consciousness.cognitive.reasoning.contradiction_integrator",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
