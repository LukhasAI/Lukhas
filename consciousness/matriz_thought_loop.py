"""Bridge for consciousness.matriz_thought_loop -> lukhas.consciousness implementation."""
from __future__ import annotations

try:
    from lukhas.consciousness.matriz_thought_loop import MATRIZProcessingContext, MATRIZThoughtLoop
except Exception:
    try:
        from candidate.consciousness.core.matriz import MATRIZProcessingContext, MATRIZThoughtLoop
    except Exception:
        # Fallback minimal definitions
        class MATRIZProcessingContext:
            """MATRIZ processing context placeholder."""
            pass

        class MATRIZThoughtLoop:
            """MATRIZ thought loop placeholder."""
            pass

__all__ = ["MATRIZProcessingContext", "MATRIZThoughtLoop"]
