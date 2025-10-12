"""Bridge: deep_inference_engine -> lukhas_website implementation."""
from __future__ import annotations

try:
    from lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine import *  # noqa: F401, F403
    __all__ = [n for n in dir() if not n.startswith("_")]
except ImportError:
    __all__ = []

# Added for test compatibility (lukhas.cognitive_core.reasoning.deep_inference_engine.InferenceRequest)
try:
    from labs.cognitive_core.reasoning.deep_inference_engine import InferenceRequest  # noqa: F401
except ImportError:
    class InferenceRequest:
        """Stub for InferenceRequest."""
        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "InferenceRequest" not in __all__:
    __all__.append("InferenceRequest")
