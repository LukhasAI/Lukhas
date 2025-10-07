"""Bridge: lukhas.consciousness.enhanced_thought_engine."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.consciousness.enhanced_thought_engine",
    "candidate.consciousness.enhanced_thought_engine",
    "consciousness.enhanced_thought_engine",
)
globals().update(_exp)

# Promote conventional symbols if present
try:
    mod = __import__("candidate.consciousness.enhanced_thought_engine", fromlist=["*"])
    e = export_from(mod)
    for sym in ("EnhancedThoughtEngine", "EnhancedContext", "EnhancedConfig"):
        if sym in e and sym not in globals():
            globals()[sym] = e[sym]
            __all__.append(sym)
except Exception:
    pass

safe_guard(__name__, __all__)
