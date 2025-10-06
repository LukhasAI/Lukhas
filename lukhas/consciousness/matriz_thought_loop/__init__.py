"""Bridge for consciousness.matriz_thought_loop -> candidate implementations."""
from __future__ import annotations

try:
    from candidate.consciousness.core.matriz import MATRIZProcessingContext, MATRIZThoughtLoop
except Exception:
    try:
        from lukhas.consciousness.matriz import MATRIZProcessingContext, MATRIZThoughtLoop
    except Exception:
        # Fallback minimal definitions
        class MATRIZProcessingContext:
            """MATRIZ processing context placeholder."""
            pass

        class MATRIZThoughtLoop:
            """MATRIZ thought loop placeholder."""
            pass

__all__ = ["MATRIZProcessingContext", "MATRIZThoughtLoop"]
