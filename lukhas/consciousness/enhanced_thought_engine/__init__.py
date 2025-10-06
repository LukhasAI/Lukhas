"""Bridge: lukhas.consciousness.enhanced_thought_engine."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.consciousness.enhanced_thought_engine",
    "candidate.consciousness.enhanced_thought_engine",
    "consciousness.enhanced_thought_engine",
)
globals().update(_exp)

# Common test surface
for mod_name in (
    "candidate.consciousness.enhanced_thought_engine",
    "consciousness.enhanced_thought_engine",
):
    try:
        mod = __import__(mod_name, fromlist=["*"])
        e = export_from(mod)
        for sym in ("EnhancedThoughtEngine", "EnhancedThoughtConfig"):
            if sym in e and sym not in globals():
                globals()[sym] = e[sym]
                if "__all__" in globals():
                    __all__.append(sym)
    except Exception:
        pass

safe_guard(__name__, __all__)
