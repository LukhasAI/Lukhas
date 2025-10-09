"""Bridge package for ``lukhas.identity`` consumers."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.identity",
    "identity",
    "candidate.identity",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# ΛTAG: identity_bridge -- expose canonical registry helpers safely
