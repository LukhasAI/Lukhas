from __future__ import annotations
from typing import Protocol, Any, Dict, List


class OpenAIProvider(Protocol):
    """Minimal protocol for OpenAI-like providers used by production code.

    Keep this file dependency-free and lane-safe (no `labs` imports).
    """

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        ...

    def embed(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        ...
