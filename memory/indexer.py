from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from .backends.pgvector_store import PgVectorStore, VectorDoc


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
