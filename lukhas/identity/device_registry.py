"""Bridge for ``lukhas.identity.device_registry``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.identity.device_registry",
    "identity.device_registry",
    "candidate.identity.device_registry",
)
globals().update(_exports)

# ΛTAG: identity_bridge -- deterministic device registry re-export

