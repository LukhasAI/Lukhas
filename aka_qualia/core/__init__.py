"""Bridge: aka_qualia.core — core subpackage facade."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.aka_qualia.core",
    "candidate.aka_qualia.core",
    "aka_qualia.core",
)
globals().update(_exp)

# Promote frequent symbols if present
try:
    mod = __import__("candidate.aka_qualia.core", fromlist=["*"])
    e = export_from(mod)
    for sym in ("QualiaEngine", "QualiaConfig", "QualiaInspector", "AkaQualia"):
        if sym in e and sym not in globals():
            globals()[sym] = e[sym]
            if "__all__" in globals():
                __all__.append(sym)
except Exception:
    pass

safe_guard(__name__, __all__)
