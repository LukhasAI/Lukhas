"""Bridge for lukhas.governance.identity.core."""
from importlib import import_module

__all__ = []


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:
        return None


for candidate in (
    "labs.governance.identity.core",
    "lukhas_website.lukhas.governance.identity.core",
    "lukhas.governance.identity.core",
):
    module = _try(candidate)
    if module:
        for attr in dir(module):
            if not attr.startswith("_"):
                globals()[attr] = getattr(module, attr)
                __all__.append(attr)
        break
