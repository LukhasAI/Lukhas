"""
T4/0.01% Excellence Memory Backend Base Classes

Abstract base classes and data structures for vector storage backends
with comprehensive type safety and performance contracts.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from governance.schema_registry import get_lane_enum


class VectorDimension(Enum):
    """Standard vector dimensions for different embedding models"""
    OPENAI_1536 = 1536      # text-embedding-ada-002
    OPENAI_3072 = 3072      # text-embedding-3-large
    SENTENCE_384 = 384      # sentence-transformers small
    SENTENCE_768 = 768      # sentence-transformers base
    CUSTOM = -1             # Custom dimension


@dataclass
class VectorDocument:
    """
    Vector document with metadata and performance tracking.

    Core data structure for all vector storage operations.
    """
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)

    # LUKHAS-specific fields
    identity_id: Optional[str] = None
    lane: str = field(default_factory=lambda: get_lane_enum()[0])  # Use canonical lane enum
    fold_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Lifecycle fields
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    # Performance tracking
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def __post_init__(self):
        """Validate and normalize document"""
        if not isinstance(self.embedding, np.ndarray):
            self.embedding = np.array(self.embedding, dtype=np.float32)

        if self.embedding.dtype != np.float32:
            self.embedding = self.embedding.astype(np.float32)

        # Normalize vector for cosine similarity
        norm = np.linalg.norm(self.embedding)
        if norm > 0:
            self.embedding = self.embedding / norm

    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return len(self.embedding)

    @property
    def is_expired(self) -> bool:
        """Check if document has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def touch(self):
        """Update access tracking"""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding.tolist(),
            "metadata": self.metadata,
            "identity_id": self.identity_id,
            "lane": self.lane,
            "fold_id": self.fold_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorDocument':
        """Create from dictionary"""
        doc = cls(
            id=data["id"],
            content=data["content"],
            embedding=np.array(data["embedding"], dtype=np.float32),
            metadata=data.get("metadata", {}),
            identity_id=data.get("identity_id"),
            lane=data.get("lane", "candidate"),
            fold_id=data.get("fold_id"),
            tags=data.get("tags", []),
            access_count=data.get("access_count", 0)
        )

        # Parse datetimes
        if "created_at" in data and data["created_at"]:
            doc.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and data["updated_at"]:
            doc.updated_at = datetime.fromisoformat(data["updated_at"])
        if "expires_at" in data and data["expires_at"]:
            doc.expires_at = datetime.fromisoformat(data["expires_at"])
        if "last_accessed" in data and data["last_accessed"]:
            doc.last_accessed = datetime.fromisoformat(data["last_accessed"])

        return doc


@dataclass
class SearchResult:
    """
    Vector search result with relevance and performance metrics.
    """
    document: VectorDocument
    score: float  # Similarity score (0-1, higher = more similar)
    rank: int     # Result ranking (0-based)

    # Performance metadata
    search_latency_ms: Optional[float] = None
    retrieval_method: Optional[str] = None  # exact, approximate, cached


@dataclass
class StorageStats:
    """
    Storage backend performance and capacity statistics.
    """
    total_documents: int
    total_size_bytes: int
    active_documents: int
    expired_documents: int

    # Performance metrics
    avg_search_latency_ms: float
    avg_upsert_latency_ms: float
    p95_search_latency_ms: float
    p95_upsert_latency_ms: float

    # Capacity metrics
    memory_usage_bytes: int
    disk_usage_bytes: int

    # Quality metrics
    deduplication_rate: float  # Percentage of duplicates detected
    compression_ratio: float   # Storage compression ratio

    # LUKHAS-specific metrics
    documents_by_lane: Dict[str, int]
    documents_by_fold: Dict[str, int]
    avg_dimension: float


class VectorStoreError(Exception):
    """Base exception for vector store operations"""
    pass


class DocumentNotFoundError(VectorStoreError):
    """Document not found in store"""
    pass


class DimensionMismatchError(VectorStoreError):
    """Vector dimension mismatch"""
    pass


class StorageCapacityError(VectorStoreError):
    """Storage capacity exceeded"""
    pass


class AbstractVectorStore(ABC):
    """
    Abstract base class for vector storage backends.

    Defines the contract for T4/0.01% excellence vector storage
    with performance guarantees and comprehensive observability.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the vector store"""
        pass

    # Core vector operations
    @abstractmethod
    async def add(self, document: VectorDocument) -> bool:
        """
        Add single document to the store.

        Performance target: <100ms p95

        Args:
            document: Vector document to add

        Returns:
            True if successful

        Raises:
            DimensionMismatchError: If vector dimension doesn't match
            StorageCapacityError: If storage capacity exceeded
        """
        pass

    @abstractmethod
    async def bulk_add(self, documents: List[VectorDocument]) -> List[bool]:
        """
        Add multiple documents in batch.

        Performance target: <500ms p95 for 100 documents

        Args:
            documents: List of documents to add

        Returns:
            List of success flags for each document
        """
        pass

    @abstractmethod
    async def get(self, document_id: str) -> VectorDocument:
        """
        Get document by ID.

        Performance target: <10ms p95

        Args:
            document_id: Document identifier

        Returns:
            Vector document

        Raises:
            DocumentNotFoundError: If document not found
        """
        pass

    @abstractmethod
    async def update(self, document: VectorDocument) -> bool:
        """
        Update existing document.

        Performance target: <100ms p95

        Args:
            document: Updated document

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, document_id: str) -> bool:
        """
        Delete document by ID.

        Performance target: <50ms p95

        Args:
            document_id: Document identifier

        Returns:
            True if document was deleted
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """
        Vector similarity search.

        Performance target: <50ms p95 for k≤10

        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            filters: Optional metadata filters
            include_metadata: Whether to include document metadata

        Returns:
            List of search results ordered by similarity
        """
        pass

    @abstractmethod
    async def search_by_text(
        self,
        query_text: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Text-based similarity search (requires embedding model).

        Args:
            query_text: Query text to search for
            k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of search results ordered by similarity
        """
        pass

    # Maintenance operations
    @abstractmethod
    async def list_expired_documents(
        self,
        as_of: datetime,
        batch_size: int = 1000
    ) -> List[VectorDocument]:
        """
        List expired documents for lifecycle processing.

        Args:
            as_of: Timestamp to check expiration against
            batch_size: Maximum number of documents to return

        Returns:
            List of expired documents
        """
        pass

    @abstractmethod
    async def list_by_identity(
        self,
        identity_id: str,
        limit: int = 1000
    ) -> List[VectorDocument]:
        """
        List all documents for a specific identity (for GDPR compliance).

        Args:
            identity_id: Identity ID to filter by
            limit: Maximum number of documents to return

        Returns:
            List of documents for the identity
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Remove expired documents.

        Returns:
            Number of documents removed
        """
        pass

    @abstractmethod
    async def optimize_index(self) -> None:
        """
        Optimize vector index for better performance.

        Performance target: Complete within 30s for 100k documents
        """
        pass

    # Statistics and monitoring
    @abstractmethod
    async def get_stats(self) -> StorageStats:
        """
        Get comprehensive storage statistics.

        Returns:
            Storage statistics and performance metrics
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for monitoring systems.

        Returns:
            Health status and key metrics
        """
        pass

    # LUKHAS-specific operations
    async def list_by_fold(self, fold_id: str, limit: int = 100) -> List[VectorDocument]:
        """
        List documents by fold ID.

        Args:
            fold_id: Fold identifier
            limit: Maximum number of documents to return

        Returns:
            List of documents in the fold
        """
        filters = {"fold_id": fold_id}
        # Default implementation using search - backends can optimize
        dummy_vector = np.zeros(1536, dtype=np.float32)  # Will be filtered out
        results = await self.search(dummy_vector, k=limit, filters=filters)
        return [result.document for result in results]

    async def list_by_identity(self, identity_id: str, limit: int = 100) -> List[VectorDocument]:
        """
        List documents by identity ID.

        Args:
            identity_id: Identity identifier
            limit: Maximum number of documents to return

        Returns:
            List of documents for the identity
        """
        filters = {"identity_id": identity_id}
        dummy_vector = np.zeros(1536, dtype=np.float32)
        results = await self.search(dummy_vector, k=limit, filters=filters)
        return [result.document for result in results]

    async def list_by_lane(self, lane: str, limit: int = 100) -> List[VectorDocument]:
        """
        List documents by lane.

        Args:
            lane: Lane identifier (candidate, integration, production)
            limit: Maximum number of documents to return

        Returns:
            List of documents in the lane
        """
        filters = {"lane": lane}
        dummy_vector = np.zeros(1536, dtype=np.float32)
        results = await self.search(dummy_vector, k=limit, filters=filters)
        return [result.document for result in results]

    # Performance utilities
    def _measure_latency(func):
        """Decorator to measure operation latency"""
        async def wrapper(self, *args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(self, *args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                self._record_latency(func.__name__, duration_ms, success=True)
                return result
            except Exception:
                duration_ms = (time.perf_counter() - start_time) * 1000
                self._record_latency(func.__name__, duration_ms, success=False)
                raise
        return wrapper

    def _record_latency(self, operation: str, duration_ms: float, success: bool):
        """Record operation latency for observability"""
        # Implementation will be provided by concrete backends
        pass

    def _validate_dimension(self, vector: np.ndarray, expected_dim: Optional[int] = None):
        """Validate vector dimension"""
        if expected_dim is not None and len(vector) != expected_dim:
            raise DimensionMismatchError(
                f"Vector dimension {len(vector)} doesn't match expected {expected_dim}"
            )

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector for cosine similarity"""
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)

        if vector.dtype != np.float32:
            vector = vector.astype(np.float32)

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector
