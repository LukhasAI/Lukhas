"""Bridge for `lukhas.bridge.adapters.service_adapter_base`."""
from importlib import import_module

__all__ = []

def _try(n: str):
    try: return import_module(n)
    except Exception: return None

for n in (
    "bridge.adapters.service_adapter_base",
    "candidate.bridge.adapters.service_adapter_base",
    "lukhas_website.lukhas.bridge.adapters.service_adapter_base",
):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break
