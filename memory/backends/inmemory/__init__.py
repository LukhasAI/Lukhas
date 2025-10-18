"""Bridge: memory.backends.inmemory"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.memory.backends.inmemory",
  "candidate.memory.backends.inmemory",
  "memory.backends.inmemory",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
