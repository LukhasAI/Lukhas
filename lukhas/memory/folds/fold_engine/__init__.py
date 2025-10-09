"""Bridge for lukhas.memory.folds.fold_engine."""

from __future__ import annotations

from enum import Enum
from importlib import import_module

_CANDIDATES = (
    "lukhas_website.lukhas.memory.folds.fold_engine",
    "candidate.memory.folds.fold_engine",
    "memory.folds.fold_engine",
)

for _candidate in _CANDIDATES:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


class MemoryPriority(Enum):  # type: ignore[misc]
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MemoryType(Enum):  # type: ignore[misc]
    FACT = "fact"
    EXPERIENCE = "experience"
    REFLECTION = "reflection"


class MemoryFold:  # type: ignore[misc]
    def __init__(self, content):
        self.content = content

    def __repr__(self) -> str:
        return f"MemoryFold(content={self.content!r})"


class FoldEngine:  # type: ignore[misc]
    def fold(self, memories):
        return MemoryFold(memories)
