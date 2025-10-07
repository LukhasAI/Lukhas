"""Bridge: governance.guardian_system — guardian orchestration layer."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

# Primary: website → candidate → ab_safety_guard (where Guardian often lives)
__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.governance.guardian_system",
    "candidate.core.ethics.ab_safety_guard",
    "governance.guardian_system",
)
globals().update(_exp)

# Canonical surface - promote from ab_safety_guard
try:
    mod = __import__("candidate.core.ethics.ab_safety_guard", fromlist=["*"])
    e = export_from(mod)
    for sym in ("SafetyGuard", "GuardConfig", "start"):
        if sym in e and sym not in globals():
            globals()[sym] = e[sym]
            __all__.append(sym)
except Exception:
    pass

# Lazily expose a `start()` no-op if tests call into it
if "start" not in globals():
    def start(*_, **__):  # type: ignore
        return None
    if "__all__" in globals():
        __all__.append("start")

safe_guard(__name__, __all__)
