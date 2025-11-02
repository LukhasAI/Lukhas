"""Bridge: candidate.rl (kept minimal; promotes to canon when found)."""

from __future__ import annotations

from _bridgeutils import bridge_from_candidates

# Many trees keep RL under research/ or tools/. This keeps tests unblocked.
_CANDIDATES = (
    "lukhas_website.candidate.rl",
    "labs.reinforcement",
    "labs.rl",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
