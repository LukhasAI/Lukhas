"""
LUKHAS Branding - Canonical Public API
Bridge to candidate.branding (single source of truth)

Constellation Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic LUKHAS AI branding and symbolic identity
- 🧠 Consciousness: Brand awareness and consistent messaging
- 🛡️ Guardian: Approved terminology and compliance standards
"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "candidate.branding",
    "branding.terminology",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

try:
    from .initializer import initialize_branding  # noqa: F401
    __all__.append("initialize_branding")
except Exception:
    pass
