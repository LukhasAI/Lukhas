"""Bridge: lukhas.tiers (enum of lanes/tiers)."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates
__all__, _exp = [], {}
for mod in (
    "lukhas_website.lukhas.tiers",
    "candidate.tiers",
    "products.tiers",
):
    try:
        a, e = bridge_from_candidates(mod)
        if a:
            __all__ = list(a); _exp = e; break
    except Exception:
        continue
if not __all__:
    from enum import Enum
    class Tier(Enum):
        L0="L0"; L1="L1"; L2="L2"; L3="L3"; L4="L4"; L5="L5"
    __all__=["Tier"]
    globals().update({"Tier": Tier})
else:
    globals().update(_exp)
