"""Bridge for lukhas.orchestration.multi_ai_router."""

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
    "lukhas_website.lukhas.orchestration.multi_ai_router",
    "candidate.orchestration.multi_ai_router",
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


if "AIProvider" not in globals():
    class AIProvider(Enum):
        """Fallback AI provider enum."""

        OPENAI = "openai"
        ANTHROPIC = "anthropic"
        LOCAL = "local"

    __all__.append("AIProvider")


if "AIModel" not in globals():
    class AIModel:
        """Fallback AI model wrapper."""

        def __init__(self, provider, model_name, **kwargs):
            self.provider = provider
            self.model_name = model_name
            for key, value in kwargs.items():
                setattr(self, key, value)

    __all__.append("AIModel")


if "ConsensusType" not in globals():
    class ConsensusType(Enum):
        """Fallback consensus type enum."""

        UNANIMOUS = "unanimous"
        MAJORITY = "majority"
        WEIGHTED = "weighted"

    __all__.append("ConsensusType")

if "AIResponse" not in globals():
    class AIResponse:
        """Fallback AI response DTO."""

        def __init__(self, **payload):
            for key, value in payload.items():
                setattr(self, key, value)

    __all__.append("AIResponse")


if "RoutingRequest" not in globals():
    class RoutingRequest:
        """Fallback routing request."""

        def __init__(self, query: str, **kwargs):
            self.query = query
            for key, value in kwargs.items():
                setattr(self, key, value)

    __all__.append("RoutingRequest")

if "get_multi_ai_router" not in globals():

    def get_multi_ai_router(*args, **kwargs):
        """Fallback multi-AI router returning a noop handler."""

        def _route(prompt: str, **route_kwargs):
            return {
                "provider": route_kwargs.get("default_provider", "noop"),
                "response": prompt,
            }

        return _route

    __all__.append("get_multi_ai_router")


if "ConsensusEngine" not in globals():

    class ConsensusEngine:
        """Fallback consensus engine."""

        def decide(self, votes):
            votes = list(votes)
            if not votes:
                return False
            return sum(bool(v) for v in votes) >= (len(votes) / 2.0)

    __all__.append("ConsensusEngine")


if "ModelSelector" not in globals():

    class ModelSelector:
        """Fallback model selector returning static provider."""

        def select(self, prompt, **kwargs):
            return {
                "provider": kwargs.get("default_provider", "noop"),
                "model": kwargs.get("default_model", "lukhas-noop-model"),
            }

    __all__.append("ModelSelector")


if "MultiAIRouter" not in globals():

    from typing import Optional

    class MultiAIRouter:
        """Fallback multi AI router facade."""

        def __init__(self, selector: Optional[ModelSelector] = None):
            self.selector = selector or ModelSelector()

        def route(self, prompt: str, **kwargs):
            return self.selector.select(prompt, **kwargs)

    __all__.append("MultiAIRouter")


def __getattr__(name: str):
    if _SRC:
        module_dict = getattr(_SRC, "__dict__", {})
        if name in module_dict:
            return module_dict[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
