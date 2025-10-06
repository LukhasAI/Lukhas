"""Bridge: orchestration.contracts (protocol/DTO contracts)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, bridge_from_candidates as bcf
_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.contracts",
    "candidate.orchestration.contracts",
    "orchestration.contracts",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)

# ensure GLYPHToken if tests reference it via contracts
if "GLYPHToken" not in __all__:
    try:
        a2, e2 = bcf("core.common")
        if "GLYPHToken" in a2:
            globals()["GLYPHToken"] = e2["GLYPHToken"]; __all__.append("GLYPHToken")
    except Exception:
        pass
