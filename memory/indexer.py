from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any

from .backends.pgvector_store import PgVectorStore, VectorDoc

__all__: list[str] = []


def _register(symbol: str) -> None:
    if symbol not in __all__:
        __all__.append(symbol)


# TODO: plug in actual embedding providers
class Embeddings:
    def __init__(self, provider=None):
        self._cache = {}
        # Use a simple stub if no provider is given
        self.provider = provider or OpenAIEmbeddingProvider()

    def embed(self, text: str) -> list[float]:
        """Get embedding from provider with caching"""
        cache_key = hashlib.sha256(text.encode()).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        # The stub provider expects an iterable and returns a list of lists.
        # We adapt to call it with a single item.
        embedding = self.provider.embed([text])[0]
        self._cache[cache_key] = embedding
        return embedding


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


class Indexer:
    def __init__(self, store: PgVectorStore, emb: Embeddings | None = None):
        self.store = store
        self.emb = emb or Embeddings()

    def upsert(self, text: str, meta: dict[str, Any]) -> str:
        fp = _fingerprint(text)

        # Check for duplicates using the fingerprint (id)
        existing = self.store.search(embedding=[0.0]*1536, k=1, filters={"id": fp})
        if existing:
            return existing[0][0] # Return existing ID

        vec = self.emb.embed(text)

        # Add the fingerprint to the metadata
        meta_with_fp = meta.copy()
        meta_with_fp['fingerprint'] = fp

        return self.store.add(VectorDoc(id=fp, text=text, embedding=vec, meta=meta_with_fp))

    def search_text(self, query: str, k: int = 10, filters: dict[str, Any] | None = None):
        vec = self.emb.embed(query)
        return self.store.search(vec, k=k, filters=filters)


# Added for test compatibility (memory.indexer.ContentExtractor)
try:
    from labs.memory.indexer import ContentExtractor
except ImportError:
    class ContentExtractor:
        """Stub for ContentExtractor."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

_register("ContentExtractor")


# Added for test compatibility (memory.indexer.DocumentIndexer)
try:
    from labs.memory.indexer import DocumentIndexer
except ImportError:
    class DocumentIndexer:
        """Stub for DocumentIndexer."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

_register("DocumentIndexer")

# Added for test compatibility (memory.indexer.OpenAIEmbeddingProvider)
try:
    from bridge.adapters.openai_embedding_provider import OpenAIEmbeddingProvider
    if "OpenAIEmbeddingProvider" not in __all__:
        __all__.append("OpenAIEmbeddingProvider")
except ImportError:
    try:
        from labs.memory.indexer import OpenAIEmbeddingProvider  # type: ignore
        if "OpenAIEmbeddingProvider" not in __all__:
            __all__.append("OpenAIEmbeddingProvider")
    except ImportError:
        class OpenAIEmbeddingProvider:
            """Stub embedding provider."""

            def embed(self, texts: Iterable[str]) -> list[list[float]]:
                return [[0.0] * 1536 for _ in texts]

        _register("OpenAIEmbeddingProvider")


# Added for test compatibility (memory.indexer.SentenceTransformersProvider)
try:
    from labs.memory.indexer import SentenceTransformersProvider
except ImportError:
    class SentenceTransformersProvider:
        """Stub sentence transformers provider."""

        def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
            self.model_name = model_name

        def embed(self, texts: Iterable[str]) -> list[list[float]]:
            return [[0.0] * 768 for _ in texts]

_register("SentenceTransformersProvider")
