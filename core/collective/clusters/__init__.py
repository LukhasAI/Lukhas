"""Bridge for `core.collective.clusters`."""
from importlib import import_module

__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("labs.core.collective.clusters", "core.collective_clusters"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
