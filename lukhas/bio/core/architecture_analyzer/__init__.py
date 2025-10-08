"""Bridge for `lukhas.bio.core.architecture_analyzer`."""
from importlib import import_module
__all__ = []
def _try(n: str):
    try: return import_module(n)
    except Exception: return None
for n in (
    "candidate.bio.core.architecture_analyzer",
    "lukhas_website.lukhas.bio.core.architecture_analyzer",
    "bio.core.architecture_analyzer",
):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
