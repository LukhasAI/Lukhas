"""Bridge: memory.backends — unify backends under one surface."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.memory.backends",
    "candidate.memory.backends",
    # DON'T import "memory.backends" - that's us! (circular)
)
globals().update(_exp)

# Promote frequent backends if they exist
possible = [
    "InMemoryBackend",
    "SQLiteBackend",
    "PostgresBackend",
    "VectorBackend",
    "S3Backend",
    "NullBackend",
]
for mod_name in (
    "candidate.memory.backends",
    "candidate.memory",
    "memory",  # single-file fallbacks
):
    try:
        mod = __import__(mod_name, fromlist=["*"])
        e = export_from(mod)
        for sym in possible:
            if sym in e and sym not in globals():
                globals()[sym] = e[sym]
                if "__all__" in globals():
                    __all__.append(sym)
    except Exception:
        continue

safe_guard(__name__, __all__)
