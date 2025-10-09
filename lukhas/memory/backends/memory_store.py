"""Bridge for ``lukhas.memory.backends.memory_store``."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

__all__, _exports = bridge_from_candidates(
    "lukhas_website.lukhas.memory.backends.memory_store",
    "memory.backends.memory_store",
    "candidate.memory.backends.memory_store",
)
globals().update(_exports)

# ΛTAG: memory_bridge -- backend memory store adapter

