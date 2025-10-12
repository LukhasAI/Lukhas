"""Bridge for `candidate.core.matriz` with sane exports."""
from importlib import import_module

__all__ = []
_SRC = None

def _try(n: str):
    try: return import_module(n)
    except Exception: return None

for n in ("lukhas_website.lukhas.core.matriz", "core.matriz"):
    m = _try(n)
    if m:
        _SRC = m
        break

if _SRC:
    for k in ("MATRIZ", "MATRIZThoughtLoop", "MATRIZProcessingContext"):
        if hasattr(_SRC, k):
            globals()[k] = getattr(_SRC, k); __all__.append(k)
