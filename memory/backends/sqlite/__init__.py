"""Bridge: memory.backends.sqlite"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.memory.backends.sqlite",
  "candidate.memory.backends.sqlite",
  "memory.backends.sqlite",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
