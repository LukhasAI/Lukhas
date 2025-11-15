"""Bridge for governance.healthcare.decision_support"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "labs.governance.healthcare.decision_support",
    "candidate.governance.healthcare.decision_support",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure ClinicalDecisionSupport is available
if "ClinicalDecisionSupport" not in globals():
    class ClinicalDecisionSupport:
        """Stub ClinicalDecisionSupport class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["ClinicalDecisionSupport"] = ClinicalDecisionSupport
    if "ClinicalDecisionSupport" not in __all__:
        __all__.append("ClinicalDecisionSupport")

safe_guard(__name__, __all__)
