"""Bridge: memory.backends — unify backends under one surface."""
from __future__ import annotations
from importlib import import_module

__all__ = []

# Make "import memory.backends" not explode even if specific backends are missing
for name in ("sqlite", "redis", "inmemory", "postgres", "filesystem", "s3"):
    try:
        m = import_module(f"memory.backends.{name}")
        globals()[name] = m
        __all__.append(name)
    except Exception:
        pass
