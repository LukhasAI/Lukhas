"""Bridge: core.consciousness_stream -> canonical implementations."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.core.consciousness_stream",
    "candidate.core.consciousness_stream",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Add stubs if no backend found
if not __all__:
    class ConsciousnessStream:
        """Stub for ConsciousnessStream."""
        def __init__(self, *a, **k):
            raise NotImplementedError("ConsciousnessStream not implemented")

    class StreamEvent:
        """Stub for StreamEvent."""
        pass

    __all__ = ["ConsciousnessStream", "StreamEvent"]
