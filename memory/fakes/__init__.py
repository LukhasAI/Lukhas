"""Bridge: memory.fakes (test utilities)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.memory.fakes",
  "candidate.memory.fakes",
  "memory.fakes",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
