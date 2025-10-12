"""Bridge for `lukhas.aka_qualia.monitoring_dashboard`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.lukhas.aka_qualia.monitoring_dashboard
  2) candidate.lukhas.aka_qualia.monitoring_dashboard
  3) aka_qualia.monitoring_dashboard

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = ["MonitoringDashboard"]


def _try(name: str):
    try:
        mod = import_module(name)
    except Exception:
        return None
    if mod.__name__ == __name__:
        return None
    return mod


_CANDIDATES = (
    "lukhas_website.lukhas.aka_qualia.monitoring_dashboard",
    "candidate.aka_qualia.monitoring_dashboard",
    "aka_qualia.monitoring_dashboard",
)

_SRC = None
for _cand in _CANDIDATES:
    _mod = _try(_cand)
    if not _mod:
        continue
    _SRC = _mod
    for name in dir(_mod):
        if name.startswith("_"):
            continue
        globals()[name] = getattr(_mod, name)
        if name not in __all__:
            __all__.append(name)
    break


if "MonitoringDashboard" not in globals():

    class MonitoringDashboard:  # type: ignore[misc]
        def render(self):
            return "Dashboard unavailable"
