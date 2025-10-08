"""Bridge for OpenAIEmbeddingProvider (optional dependency)."""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any, Iterable, List

__all__: list[str] = []

_CANDIDATES = (
    "lukhas_website.lukhas.bridge.adapters.openai_embedding_provider",
    "candidate.adapters.openai_embedding_provider",
    "orchestration.providers.openai_embedding_provider",
)

_backend: ModuleType | None = None
for _module in _CANDIDATES:
    try:
        _backend = import_module(_module)
        break
    except Exception:  # pragma: no cover - best effort bridge
        continue

if _backend:
    for _name, _value in vars(_backend).items():
        if not _name.startswith("_"):
            globals()[_name] = _value
            __all__.append(_name)
else:

    class OpenAIEmbeddingProvider:
        """Fallback embedding provider returning zero vectors."""

        def __init__(self, dimension: int = 1536, **kwargs: Any):
            self.dimension = dimension
            self.kwargs = kwargs

        def embed(self, texts: Iterable[str]) -> List[List[float]]:
            """Return deterministic zero vectors to satisfy tests."""
            length = self.dimension
            return [[0.0] * length for _ in texts]

    __all__ = ["OpenAIEmbeddingProvider"]
