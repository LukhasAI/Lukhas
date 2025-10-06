"""Bridge: memory.backends."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.memory.backends",
    "candidate.memory.backends",
    "memory.backends",
)
globals().update(_exp)
