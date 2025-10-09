"""Bridge for ``lukhas.governance.guardian_serializers``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.governance.guardian_serializers",
    "governance.guardian_serializers",
    "candidate.governance.guardian_serializers",
)
globals().update(_exports)

# ΛTAG: governance_bridge -- guardian serializer façade
