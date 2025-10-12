"""Bridge for `lukhas.memory.backends.faiss_store`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.lukhas.memory.backends.faiss_store
  2) candidate.lukhas.memory.backends.faiss_store
  3) memory.backends.faiss_store

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations

from importlib import import_module
from typing import List

__all__: List[str] = ["FAISSVectorStore"]


def _try(name: str):
    try:
        mod = import_module(name)
    except Exception:
        return None
    if mod.__name__ == __name__:
        return None
    return mod


_CANDIDATES = (
    "lukhas_website.lukhas.memory.backends.faiss_store",
    "candidate.memory.backends.faiss_store",
    "memory.backends.faiss_store",
)

_SRC = None
for _cand in _CANDIDATES:
    _mod = _try(_cand)
    if not _mod:
        continue
    _SRC = _mod
    for name in dir(_mod):
        if name.startswith("_"):
            continue
        globals()[name] = getattr(_mod, name)
        if name not in __all__:
            __all__.append(name)
    break


if "FAISSVectorStore" not in globals():

    class FAISSVectorStore:  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            self.vectors = {}

        def index(self, key: str, vector):
            self.vectors[key] = vector

        def search(self, vector, top_k: int = 5):
            return []
