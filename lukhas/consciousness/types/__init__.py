"""Consciousness type surface used by tests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from typing import Optional

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.types",
    "candidate.consciousness.types",
    "consciousness.types",
)

_backend = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)


if "ConsciousnessState" not in globals():

    class ConsciousnessState(Enum):
        IDLE = "idle"
        THINKING = "thinking"
        DREAMING = "dreaming"
        REFLECTING = "reflecting"

    __all__.append("ConsciousnessState")


if "ThoughtLoopContext" not in globals():

    @dataclass
    class ThoughtLoopContext:
        prompt: str
        iteration: int = 0
        safety_mode: Optional[str] = None

    __all__.append("ThoughtLoopContext")


if "MetaCognitiveContext" not in globals():

    @dataclass
    class MetaCognitiveContext:
        confidence: float = 0.0
        drift_score: float = 0.0

    __all__.append("MetaCognitiveContext")


if "DecisionContext" not in globals():

    @dataclass
    class DecisionContext:
        rationale: Optional[str] = None
        selected_action: Optional[str] = None

    __all__.append("DecisionContext")


if "SafetyMode" not in globals():

    class SafetyMode(Enum):
        NORMAL = "normal"
        RESTRICTED = "restricted"
        OFF = "off"

    __all__.append("SafetyMode")
