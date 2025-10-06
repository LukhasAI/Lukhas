"""Bridge: aka_qualia.core - Minimal stub for test compatibility"""
from __future__ import annotations
from typing import Any, Optional

class AkaQualia:
    """Minimal AkaQualia stub for test compatibility."""

    def __init__(
        self,
        pls=None,
        teq_guardian=None,
        glyph_mapper=None,
        router=None,
        oneiric_hook=None,
        memory=None,
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize AkaQualia with pluggable components (stub)."""
        self.config = config or {}
        self.pls = pls
        self.teq_guardian = teq_guardian
        self.glyph_mapper = glyph_mapper
        self.router = router
        self.oneiric_hook = oneiric_hook
        self.memory = memory

__all__ = ["AkaQualia"]
