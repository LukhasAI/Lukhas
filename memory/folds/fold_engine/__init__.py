"""Bridge: memory.folds.fold_engine"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.memory.folds.fold_engine",
    "candidate.memory.folds.fold_engine",
    "labs.memory.folds.fold_engine",
    "memory.fold_engine",  # historical
)
globals().update(_exp)

# Ensure commonly expected symbols are available
if "MemoryType" not in globals():
    from enum import Enum
    class MemoryType(Enum):
        """Stub MemoryType enum."""
        EPISODIC = "episodic"
        SEMANTIC = "semantic"
        PROCEDURAL = "procedural"
    globals()["MemoryType"] = MemoryType
    if "MemoryType" not in __all__:
        __all__.append("MemoryType")

if "MemoryPriority" not in globals():
    from enum import Enum
    class MemoryPriority(Enum):
        """Stub MemoryPriority enum."""
        LOW = 1
        MEDIUM = 2
        HIGH = 3
    globals()["MemoryPriority"] = MemoryPriority
    if "MemoryPriority" not in __all__:
        __all__.append("MemoryPriority")

if "MemoryFold" not in globals():
    class MemoryFold:
        """Stub MemoryFold class."""
        def __init__(self, *args, **kwargs):
            pass
    globals()["MemoryFold"] = MemoryFold
    if "MemoryFold" not in __all__:
        __all__.append("MemoryFold")

safe_guard(__name__, __all__)
