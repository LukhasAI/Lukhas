"""Bridge exposing RL environments for compatibility."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.rl.environments",
    "lukhas_website.lukhas.rl.engine",
    "labs.rl.environments",
    "rl.environments",
)
globals().update(_exports)

# ΛTAG: rl_bridge -- ensure deterministic environment exports

