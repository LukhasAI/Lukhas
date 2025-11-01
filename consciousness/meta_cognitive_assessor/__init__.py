"""Bridge for `consciousness.meta_cognitive_assessor` (non-recursive).

Resolution order:
  1) lukhas_website.consciousness.meta_cognitive_assessor
  2) candidate.consciousness.meta_cognitive_assessor

If no backend is available, provide minimal stubs to satisfy imports in tests.
"""
from __future__ import annotations

from importlib import import_module
from typing import List
from enum import Enum
from dataclasses import dataclass

__all__: List[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order (avoid self to prevent recursion)
_CANDIDATES = (
    "lukhas_website.consciousness.meta_cognitive_assessor",
    "candidate.consciousness.meta_cognitive_assessor",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Provide minimal stubs if no backend found
if _SRC is None:
    class CognitiveLoadLevel(str, Enum):  # type: ignore[no-redef]
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    @dataclass
    class MetaCognitiveAssessment:  # type: ignore[no-redef]
        load_level: CognitiveLoadLevel = CognitiveLoadLevel.MEDIUM
        reasoning_depth: int = 0
        notes: str = ""

    __all__.extend([
        "CognitiveLoadLevel",
        "MetaCognitiveAssessment",
    ])

def __getattr__(name: str):
    """Lazy attribute access fallback to selected backend if available."""
    if _SRC is not None and hasattr(_SRC, name):
        return getattr(_SRC, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
