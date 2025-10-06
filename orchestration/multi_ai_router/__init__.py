"""Bridge: orchestration.multi_ai_router (legacy alias of routers.multi)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

__all__, _exp = [], {}
for mod in (
    "lukhas_website.lukhas.orchestration.multi_ai_router",
    "candidate.orchestration.multi_ai_router",
    "orchestration.multi_ai_router",
    "orchestration.routers.multi",  # fallback
):
    try:
        a, e = bridge_from_candidates(mod)
        if a:
            __all__ = list(a); _exp = e; break
    except Exception:
        continue
globals().update(_exp)
