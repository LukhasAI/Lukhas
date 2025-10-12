"""Facade: candidate.matriz -> consciousness.matriz_thought_loop APIs."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

# Reuse final canonical MATRIZ classes from the consciousness bridge
_CANDIDATES = ("consciousness.matriz_thought_loop",)
__all__, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)
