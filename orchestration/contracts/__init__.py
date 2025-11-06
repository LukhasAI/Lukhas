"""Bridge: orchestration.contracts (protocol/DTO contracts)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, bridge_from_candidates as bcf

_CANDIDATES = (
    "lukhas_website.orchestration.contracts",
    "candidate.orchestration.contracts",
    "orchestration.contracts",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_orchestration_contracts___init___py_L11"}

# ensure GLYPHToken if tests reference it via contracts
if "GLYPHToken" not in __all__:
    try:
        a2, e2 = bcf("core.common")
        if "GLYPHToken" in a2:
            globals()["GLYPHToken"] = e2["GLYPHToken"]; __all__.append("GLYPHToken")  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_orchestration_contracts___init___py_L18"}
    except Exception:
        pass
