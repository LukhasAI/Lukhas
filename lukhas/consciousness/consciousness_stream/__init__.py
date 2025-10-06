"""Bridge for consciousness.consciousness_stream -> candidate implementations."""
from __future__ import annotations

try:
    from candidate.consciousness.stream import ConsciousnessStream
except Exception:
    try:
        from candidate.consciousness.streams import ConsciousnessStream
    except Exception:
        # Fallback minimal definition
        class ConsciousnessStream:
            """Consciousness stream placeholder."""
            pass

__all__ = ["ConsciousnessStream"]
