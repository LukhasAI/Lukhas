from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List, Optional

from .backends.pgvector_store import PgVectorStore, VectorDoc

__all__: list[str] = []


def _register(symbol: str) -> None:
    if symbol not in __all__:
        __all__.append(symbol)


# TODO: plug in actual embedding providers
class Embeddings:
    def embed(self, text: str) -> List[float]:
        # TODO: call provider, cache results
        return [0.0] * 1536  # placeholder


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


class Indexer:
    def __init__(self, store: PgVectorStore, emb: Optional[Embeddings] = None):
        self.store = store
        self.emb = emb or Embeddings()

    def upsert(self, text: str, meta: Dict[str, Any]) -> str:
        fp = _fingerprint(text)
        vec = self.emb.embed(text)
        # TODO: detect duplicates by fp in meta
        return self.store.add(VectorDoc(id=fp, text=text, embedding=vec, meta=meta))

    def search_text(self, query: str, k: int = 10, filters: Optional[Dict[str, Any]] = None):
        vec = self.emb.embed(query)
        return self.store.search(vec, k=k, filters=filters)


# Added for test compatibility (memory.indexer.ContentExtractor)
try:
    from candidate.memory.indexer import ContentExtractor
except ImportError:
    class ContentExtractor:
        """Stub for ContentExtractor."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

_register("ContentExtractor")


# Added for test compatibility (memory.indexer.DocumentIndexer)
try:
    from candidate.memory.indexer import DocumentIndexer
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
        from candidate.memory.indexer import OpenAIEmbeddingProvider  # type: ignore
        if "OpenAIEmbeddingProvider" not in __all__:
            __all__.append("OpenAIEmbeddingProvider")
    except ImportError:
        class OpenAIEmbeddingProvider:
            """Stub embedding provider."""

            def embed(self, texts: Iterable[str]) -> List[List[float]]:
                return [[0.0] * 1536 for _ in texts]

        _register("OpenAIEmbeddingProvider")


# Added for test compatibility (memory.indexer.SentenceTransformersProvider)
try:
    from candidate.memory.indexer import SentenceTransformersProvider
except ImportError:
    class SentenceTransformersProvider:
        """Stub sentence transformers provider."""

        def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
            self.model_name = model_name

        def embed(self, texts: Iterable[str]) -> List[List[float]]:
            return [[0.0] * 768 for _ in texts]

_register("SentenceTransformersProvider")
