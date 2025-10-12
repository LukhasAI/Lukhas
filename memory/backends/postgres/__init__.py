"""Bridge: memory.backends.postgres"""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.lukhas.memory.backends.postgres",
  "candidate.memory.backends.postgres",
  "memory.backends.postgres",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
