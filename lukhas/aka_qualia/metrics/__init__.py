from __future__ import annotations

from importlib import import_module

try:
    mod = None
    for _m in (
        "lukhas_website.lukhas.aka_qualia.metrics",
        "labs.aka_qualia.metrics",
        "aka_qualia.metrics",
    ):
        try:
            mod = import_module(_m)
            break
        except Exception:
            continue
except Exception:
    mod = None

if mod is not None:
    globals().update({k: getattr(mod, k) for k in dir(mod) if not k.startswith("_")})
    __all__ = [k for k in dir(mod) if not k.startswith("_")]
else:
    __all__ = []
