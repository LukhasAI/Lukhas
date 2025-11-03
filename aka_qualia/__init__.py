"""Bridge: aka_qualia — canonical surface for qualia research components."""
from __future__ import annotations

from importlib import import_module

from _bridgeutils import bridge_from_candidates, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.aka_qualia",
    "candidate.aka_qualia",
    "aka_qualia",
)

globals().update(_exp)

if not isinstance(__all__, list):
    __all__ = list(__all__)


def _ensure_local_module(name: str) -> None:
    if name in globals():
        return
    try:
        module = import_module(f"{__name__}.{name}")
    except Exception:
        return
    globals()[name] = module
    if name not in __all__:
        __all__.append(name)


for _module_name in ("core", "memory", "metrics"):
    _ensure_local_module(_module_name)

safe_guard(__name__, __all__)
