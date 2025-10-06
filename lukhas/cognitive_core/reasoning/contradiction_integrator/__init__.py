"""Bridge: contradiction_integrator -> real implementation."""
from __future__ import annotations

try:
    from lukhas_website.lukhas.cognitive_core.reasoning.contradiction_integrator import *  # noqa: F401, F403
    __all__ = [n for n in dir() if not n.startswith("_")]
except ImportError:
    try:
        from consciousness.cognitive.reasoning.contradiction_integrator import *  # noqa: F401, F403
        __all__ = [n for n in dir() if not n.startswith("_")]
    except ImportError:
        __all__ = []
