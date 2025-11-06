"""Bridge: aka_qualia.core - core subpackage facade."""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.aka_qualia.core",
    "candidate.aka_qualia.core",
    "aka_qualia.core",
)
globals().update(_exp)

if not isinstance(__all__, list):
    __all__ = list(__all__)

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

# Ensure GLYPHToken surface exists even if backend missing
if "GLYPHToken" not in globals():
    try:
        from core.common import GLYPHToken as _GLYPHToken  # type: ignore
    except Exception:
        class _GLYPHToken:  # type: ignore
            """Fallback GLYPHToken representation for tests."""

            def __init__(self, *args: object, **kwargs: object) -> None:
                self.args = args
                self.kwargs = kwargs

        globals()["GLYPHToken"] = _GLYPHToken
    else:
        globals()["GLYPHToken"] = _GLYPHToken

    if "GLYPHToken" not in __all__:
        __all__.append("GLYPHToken")


if "AkaQualia" not in globals():
    class AkaQualia:  # type: ignore
        """Fallback AkaQualia implementation placeholder."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

    if "AkaQualia" not in __all__:
        __all__.append("AkaQualia")

safe_guard(__name__, __all__)
