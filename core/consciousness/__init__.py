"""Bridge for `core.consciousness` to the richer candidate implementation."""
from importlib import import_module

__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("candidate.core.consciousness", "core_core.consciousness"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
