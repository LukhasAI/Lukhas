"""Bridge: deep_inference_engine -> lukhas_website implementation."""
from __future__ import annotations

try:
    from lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine import *  # noqa: F401, F403
    __all__ = [n for n in dir() if not n.startswith("_")]
except ImportError:
    __all__ = []
