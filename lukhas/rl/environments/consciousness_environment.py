"""Bridge for ``lukhas.rl.environments.consciousness_environment``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.rl.environments.consciousness_environment",
    "lukhas_website.lukhas.rl.engine.consciousness_environment",
    "candidate.rl.environments.consciousness_environment",
    "rl.engine.consciousness_environment",
)
globals().update(_exports)

# ΛTAG: rl_bridge -- consciousness environment shim

