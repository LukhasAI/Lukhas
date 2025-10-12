"""Bridge: lukhas.public_api (compat surface for external callers)."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.lukhas.public_api",
  "labs.public_api",
  "public_api",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
