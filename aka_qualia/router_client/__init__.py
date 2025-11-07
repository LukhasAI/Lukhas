"""Bridge for `aka_qualia.router_client`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.aka_qualia.router_client
  2) candidate.aka_qualia.router_client
  3) aka_qualia.router_client

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: list[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.aka_qualia.router_client",
    "candidate.aka_qualia.router_client",
    "aka_qualia.router_client",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
# No pre-defined stubs

# Add expected symbols as stubs if not found
if "RouterClient" not in globals():

    class RouterClient:
        pass


if "compute_routing_priority" not in globals():

    def compute_routing_priority(scene):
        return 0.5


if "create_router_client" not in globals():

    def create_router_client(router_type, router_config):
        return RouterClient()
