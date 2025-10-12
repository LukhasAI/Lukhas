"""Bridge for `candidate.rl.coordination`."""
from importlib import import_module

__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("lukhas_website.lukhas.rl.coordination", "rl.coordination"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
