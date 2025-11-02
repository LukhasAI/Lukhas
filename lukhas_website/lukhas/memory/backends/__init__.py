"""
T4/0.01% Excellence Memory Storage Backends

High-performance vector storage backends for LUKHAS memory system with
comprehensive observability and T4 performance guarantees.

Supported backends:
- PostgreSQL with pgvector extension
- FAISS (Facebook AI Similarity Search)
- In-memory store for development/testing

Performance targets:
- Upsert: <100ms p95 for single document
- Search: <50ms p95 for k≤10 results
- Bulk operations: <500ms p95 for 100 documents
"""

from .base import AbstractVectorStore, SearchResult, StorageStats, VectorDocument
from .faiss_store import FAISSStore
from .memory_store import InMemoryVectorStore
from .pgvector_store import PgVectorStore

__all__ = [
    "AbstractVectorStore",
    "VectorDocument",
    "SearchResult",
    "StorageStats",
    "PgVectorStore",
    "FAISSStore",
    "InMemoryVectorStore",
]
