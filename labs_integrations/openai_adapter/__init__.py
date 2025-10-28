from __future__ import annotations
from typing import Any, Dict, List

# This module intentionally lives outside production lanes and may import
# `labs.*` modules. It is only loaded via the provider registry by config.
try:
    # Example labs-side client; adapt to the actual labs client in your repo.
    from labs.openai_client import OpenAIClient
except Exception:
    # Provide a very small fallback stub to avoid runtime crashes in tests.
    class OpenAIClient:
        def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
            return {"content": "stubbed response", "ok": True}


class _OpenAIProvider:
    def __init__(self):
        self._client = OpenAIClient()

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        return self._client.chat(messages, **kwargs)

    def embed(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        # Minimal stub; replace with real call to labs client if available.
        return [[0.0] * 8 for _ in texts]


def provide():
    return _OpenAIProvider()
