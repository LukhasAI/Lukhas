"""Bridge for ``lukhas.identity.oidc_provider``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.identity.oidc_provider",
    "identity.oidc_provider",
    "candidate.identity.oidc_provider",
)
globals().update(_exports)

# ΛTAG: identity_bridge -- unified OIDC provider facade

