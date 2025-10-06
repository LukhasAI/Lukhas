"""Bridge: memory.backends (vector stores)."""
from __future__ import annotations

# Direct exports from local implementation (lukhas_website has import errors)
from memory.backends.pgvector_store import PgVectorStore, VectorDoc

__all__ = ["PgVectorStore", "VectorDoc"]

# Try to import additional components if available
try:
    from lukhas_website.lukhas.memory.backends import (
        AbstractVectorStore,
        SearchResult,
        StorageStats,
        FAISSStore,
        InMemoryVectorStore,
    )
    __all__.extend([
        "AbstractVectorStore",
        "SearchResult",
        "StorageStats",
        "FAISSStore",
        "InMemoryVectorStore",
    ])
except (ImportError, ModuleNotFoundError):
    # Fallback: these aren't critical for basic functionality
    pass
