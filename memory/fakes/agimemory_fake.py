"""Bridge: memory.fakes.agimemory_fake - test fake for AGI memory."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.memory.fakes.agimemory_fake",
    "candidate.memory.fakes.agimemory_fake",
    "labs.memory.fakes.agimemory_fake",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
