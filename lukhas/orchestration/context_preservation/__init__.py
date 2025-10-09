"""Bridge for context preservation utilities."""

from __future__ import annotations

from enum import Enum
from importlib import import_module
from typing import Any, Dict

__all__ = ["CompressionLevel", "ContextPreservationEngine", "ContextType"]

_CANDIDATES = (
    "lukhas_website.lukhas.orchestration.context_preservation",
    "candidate.orchestration.context_preservation",
    "orchestration.context_preservation",
)

_SRC = None
for _candidate in _CANDIDATES:
    try:
        _mod = import_module(_candidate)
    except Exception:
        continue
    _SRC = _mod
    globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
    break


if "CompressionLevel" not in globals():

    class CompressionLevel(Enum):  # type: ignore[misc]
        NONE = "none"
        FAST = "fast"
        BALANCED = "balanced"
        MAXIMUM = "maximum"


if "ContextType" not in globals():

    class ContextType(Enum):  # type: ignore[misc]
        MEMORY = "memory"
        CONSCIOUSNESS = "consciousness"
        OBSERVABILITY = "observability"


if "ContextPreservationEngine" not in globals():

    class ContextPreservationEngine:  # type: ignore[misc]
        def __init__(self, compression: CompressionLevel = CompressionLevel.BALANCED):
            self.compression = compression

        def preserve(self, payload: Dict[str, Any]) -> Dict[str, Any]:
            return {"compression": self.compression.value, "payload": payload}
