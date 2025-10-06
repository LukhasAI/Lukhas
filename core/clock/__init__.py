"""Bridge: core.clock (time abstraction)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
_CANDIDATES = (
  "lukhas_website.lukhas.core.clock",
  "candidate.core.clock",
  "core.clock",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
