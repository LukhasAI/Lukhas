"""Bridge for root-level observability.advanced_metrics."""
from importlib import import_module
__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("lukhas.observability.advanced_metrics", "candidate.observability.advanced_metrics"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
