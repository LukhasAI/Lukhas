"""Shim for MATRIZ.adapters -> matriz.adapters"""
import importlib
try:
    mod = importlib.import_module('matriz.adapters')
    __path__ = getattr(mod, '__path__', __path__)
    for _name in dir(mod):
        if not _name.startswith('__'):
            try:
                globals()[_name] = getattr(mod, _name)
            except Exception:
                pass
except Exception:
    pass
