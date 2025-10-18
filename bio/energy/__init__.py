"""Bridge for `bio.energy`."""
from importlib import import_module

__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("bio.energy", "candidate.bio.energy", "lukhas_website.bio.energy"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
