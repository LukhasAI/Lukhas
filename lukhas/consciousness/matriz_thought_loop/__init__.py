"""Bridge: lukhas.consciousness.matriz_thought_loop."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard, deprecate

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.consciousness.matriz_thought_loop",
    "candidate.consciousness.matriz_thought_loop",
    "consciousness.matriz_thought_loop",
)
globals().update(_exp)

# Ensure the two most-expected symbols exist (tests referenced these)
wanted = ("MATRIZThoughtLoop", "MATRIZProcessingContext")
for mod_name in (
    "candidate.consciousness.matriz_thought_loop",
    "consciousness.matriz_thought_loop",
    "consciousness.matriz.core",  # known alt
):
    try:
        mod = __import__(mod_name, fromlist=["*"])
        e = export_from(mod)
        for w in wanted:
            if w in e and w not in globals():
                globals()[w] = e[w]
                if "__all__" in globals():
                    __all__.append(w)
    except Exception:
        pass

safe_guard(__name__, __all__)
deprecate(__name__, "prefer `candidate.consciousness.matriz_thought_loop` directly")
