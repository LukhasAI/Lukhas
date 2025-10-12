"""Bridge for lukhas.governance.identity.core."""
from importlib import import_module

__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in ("candidate.governance.identity.core", "lukhas_website.lukhas.governance.identity.core", "governance.identity.core"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
