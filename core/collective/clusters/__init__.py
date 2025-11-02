"""Bridge for `core.collective.clusters`."""

from importlib import import_module

__all__ = []


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:
        return None


for candidate in ("labs.core.collective.clusters", "core.collective_clusters"):
    module = _try(candidate)
    if module:
        for attr in dir(module):
            if not attr.startswith("_"):
                globals()[attr] = getattr(module, attr)
                __all__.append(attr)
        break
