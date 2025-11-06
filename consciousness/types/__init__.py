"""Bridge: consciousness.types (ConsciousnessState, enums)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

_CANDIDATES = (
  "lukhas_website.consciousness.types",
  "candidate.consciousness.types",
  "consciousness.types",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_consciousness_types___init___py_L11"}

# Ensure specific symbols if tests expect them explicitly
_required = ("ConsciousnessState", "CognitiveNodeBase")
for sym in _required:
    if sym not in __all__:
        try:
            from _bridgeutils import bridge_from_candidates as bcf
            a2, e2 = bcf("core.common")
            if sym in a2:
                globals()[sym] = e2[sym]
                __all__.append(sym)
        except Exception:
            pass
