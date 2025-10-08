"""Bridge for lukhas.consciousness.meta_cognitive_assessor."""

from __future__ import annotations

from enum import Enum
from importlib import import_module
from typing import List

__all__: List[str] = []


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:  # pragma: no cover - best effort bridge
        return None


_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.meta_cognitive_assessor",
    "candidate.consciousness.meta_cognitive_assessor",
)

_SRC = None
for _candidate in _CANDIDATES:
    module = _try(_candidate)
    if module:
        _SRC = module
        for name in dir(module):
            if not name.startswith("_"):
                globals()[name] = getattr(module, name)
                __all__.append(name)
        break


if "CognitiveLoadLevel" not in globals():
    class CognitiveLoadLevel(Enum):
        """Fallback cognitive load enum."""

        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    __all__.append("CognitiveLoadLevel")

if "MetaCognitiveContext" not in globals():
    try:
        from lukhas.consciousness.meta_cognitive_context import MetaCognitiveContext  # noqa: F401
    except Exception:
        class MetaCognitiveContext(dict):
            """Fallback meta cognitive context."""

    __all__.append("MetaCognitiveContext")


if "MetaCognitiveAssessment" not in globals():
    class MetaCognitiveAssessment(dict):
        """Fallback assessment payload."""

    __all__.append("MetaCognitiveAssessment")


def __getattr__(name: str):
    if _SRC:
        module_dict = getattr(_SRC, "__dict__", {})
        if name in module_dict:
            return module_dict[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
