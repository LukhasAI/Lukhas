"""Bridge: orchestration.multi_ai_router (legacy alias of routers.multi)."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates

__all__, _exp = [], {}
for mod in (
    "lukhas_website.orchestration.multi_ai_router",
    "candidate.orchestration.multi_ai_router",
    "orchestration.multi_ai_router",
    "orchestration.routers.multi",  # fallback
):
    try:
        a, e = bridge_from_candidates(mod)
        if a:
            __all__ = list(a); _exp = e; break  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_orchestration_multi_ai_router___init___py_L16"}
    except Exception:
        continue
globals().update(_exp)
