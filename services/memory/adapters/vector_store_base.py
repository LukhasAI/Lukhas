"""
Vector Store Base Classes
========================

Abstract base classes defining the interface for vector store implementations.
Supports semantic search, metadata filtering, and T4/0.01% excellence SLOs.
"""

import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorStoreType(Enum):
    """Supported vector store implementations"""
    POSTGRESQL = "postgresql"
    FAISS = "faiss"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"


@dataclass
class VectorDocument:
    """Document with vector embedding and metadata"""
    id: str
    vector: list[float]
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class VectorSearchQuery:
    """Vector similarity search query"""
    vector: list[float]
    top_k: int = 10
    metadata_filter: Optional[dict[str, Any]] = None
    score_threshold: Optional[float] = None
    include_vectors: bool = False
    include_metadata: bool = True


@dataclass
class VectorSearchResult:
    """Single search result with score"""
    document: VectorDocument
    score: float
    rank: int


@dataclass
class VectorSearchResponse:
    """Complete search response with timing"""
    results: list[VectorSearchResult]
    query_time_ms: float
    total_documents: int
    query_vector_dim: int


@dataclass
class VectorStoreStats:
    """Vector store performance and health statistics"""
    total_documents: int
    vector_dimensions: int
    index_size_bytes: int
    last_updated: float
    average_query_time_ms: float
    p95_query_time_ms: float
    p99_query_time_ms: float
    error_rate: float


class VectorStoreError(Exception):
    """Base exception for vector store operations"""
    pass


class VectorStoreDimensionError(VectorStoreError):
    """Vector dimension mismatch error"""
    pass


class VectorStoreConnectionError(VectorStoreError):
    """Connection or availability error"""
    pass


class VectorStoreBase(ABC):
    """
    Abstract base class for vector store implementations.

    Provides unified interface for vector similarity search across
    different backends (PostgreSQL, FAISS, ChromaDB, etc.).

    T4/0.01% Excellence Requirements:
    - Search p95 <50ms, p99 <100ms
    - Upsert p95 <100ms, p99 <150ms
    - 99.9% availability SLO
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.stats = VectorStoreStats(
            total_documents=0,
            vector_dimensions=0,
            index_size_bytes=0,
            last_updated=time.time(),
            average_query_time_ms=0.0,
            p95_query_time_ms=0.0,
            p99_query_time_ms=0.0,
            error_rate=0.0
        )
        self._query_times: list[float] = []
        self._max_query_history = 1000

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector store connection and indexes"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources and close connections"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vector store is healthy and responsive"""
        pass

    @abstractmethod
    async def upsert_documents(self, documents: list[VectorDocument]) -> dict[str, Any]:
        """
        Insert or update documents with vectors.

        Returns:
            Dict with keys: 'inserted', 'updated', 'failed', 'duration_ms'
        """
        pass

    @abstractmethod
    async def search_vectors(self, query: VectorSearchQuery) -> VectorSearchResponse:
        """
        Perform vector similarity search.

        Must meet T4 SLO: p95 <50ms, p99 <100ms
        """
        pass

    @abstractmethod
    async def delete_documents(self, document_ids: list[str]) -> dict[str, Any]:
        """
        Delete documents by ID.

        Returns:
            Dict with keys: 'deleted', 'not_found', 'failed', 'duration_ms'
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve a single document by ID"""
        pass

    @abstractmethod
    async def count_documents(self, metadata_filter: Optional[dict[str, Any]] = None) -> int:
        """Count documents, optionally with metadata filter"""
        pass

    @abstractmethod
    async def create_index(self, index_params: dict[str, Any]) -> None:
        """Create or rebuild vector index with specified parameters"""
        pass

    async def get_stats(self) -> VectorStoreStats:
        """Get current performance statistics"""
        await self._update_stats()
        return self.stats

    async def _update_stats(self) -> None:
        """Update internal statistics"""
        if self._query_times:
            import statistics
            self.stats.average_query_time_ms = statistics.mean(self._query_times)

            if len(self._query_times) >= 20:  # Need sufficient samples
                try:
                    percentiles = statistics.quantiles(self._query_times, n=100)
                    self.stats.p95_query_time_ms = percentiles[94]  # 95th percentile
                    self.stats.p99_query_time_ms = percentiles[98]  # 99th percentile
                except statistics.StatisticsError:
                    # Fallback for insufficient data
                    sorted_times = sorted(self._query_times)
                    n = len(sorted_times)
                    self.stats.p95_query_time_ms = sorted_times[int(n * 0.95)]
                    self.stats.p99_query_time_ms = sorted_times[int(n * 0.99)]

        self.stats.last_updated = time.time()

    def _record_query_time(self, duration_ms: float) -> None:
        """Record a query time for statistics"""
        self._query_times.append(duration_ms)

        # Keep only recent query times
        if len(self._query_times) > self._max_query_history:
            self._query_times = self._query_times[-self._max_query_history:]

    async def _validate_vector_dimensions(self, vectors: list[list[float]]) -> None:
        """Validate that all vectors have consistent dimensions"""
        if not vectors:
            return

        expected_dim = len(vectors[0])
        if expected_dim == 0:
            raise VectorStoreDimensionError("Empty vectors not allowed")

        for i, vector in enumerate(vectors):
            if len(vector) != expected_dim:
                raise VectorStoreDimensionError(
                    f"Vector {i} has {len(vector)} dimensions, expected {expected_dim}"
                )

        # Update stats
        if self.stats.vector_dimensions == 0:
            self.stats.vector_dimensions = expected_dim
        elif self.stats.vector_dimensions != expected_dim:
            raise VectorStoreDimensionError(
                f"Vector dimension mismatch: {expected_dim} != {self.stats.vector_dimensions}"
            )


class BatchVectorStoreBase(VectorStoreBase):
    """
    Extended base class for vector stores supporting efficient batch operations.

    Provides batch processing optimizations for high-throughput scenarios.
    """

    @abstractmethod
    async def batch_upsert(self,
                          documents: list[VectorDocument],
                          batch_size: int = 100,
                          parallel_batches: int = 4) -> dict[str, Any]:
        """
        Efficient batch upsert with parallel processing.

        Args:
            documents: List of documents to upsert
            batch_size: Documents per batch
            parallel_batches: Number of concurrent batches

        Returns:
            Aggregated results from all batches
        """
        pass

    @abstractmethod
    async def batch_search(self,
                          queries: list[VectorSearchQuery],
                          parallel_queries: int = 8) -> list[VectorSearchResponse]:
        """
        Execute multiple searches in parallel.

        Optimizes resource utilization for bulk search operations.
        """
        pass


class VectorStoreFactory:
    """Factory for creating vector store instances"""

    _stores: dict[VectorStoreType, type] = {}  # TODO[T4-ISSUE]: {"code":"RUF012","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Mutable class attribute needs ClassVar annotation for type safety","estimate":"15m","priority":"medium","dependencies":"typing imports","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_services_memory_adapters_vector_store_base_py_L282"}

    @classmethod
    def register(cls, store_type: VectorStoreType, store_class: type):
        """Register a vector store implementation"""
        cls._stores[store_type] = store_class

    @classmethod
    def create(cls, store_type: VectorStoreType, config: dict[str, Any]) -> VectorStoreBase:
        """Create a vector store instance"""
        if store_type not in cls._stores:
            raise ValueError(f"Unsupported vector store type: {store_type}")

        store_class = cls._stores[store_type]
        return store_class(config)

    @classmethod
    def list_available(cls) -> list[VectorStoreType]:
        """List all registered vector store types"""
        return list(cls._stores.keys())


# Performance monitoring utilities
class VectorStoreMonitor:
    """Monitor vector store performance and SLO compliance"""

    def __init__(self, store: VectorStoreBase):
        self.store = store
        self.slo_violations = 0
        self.total_operations = 0

    async def monitor_search(self, query: VectorSearchQuery) -> VectorSearchResponse:
        """Monitor a search operation for SLO compliance"""
        start_time = time.perf_counter()

        try:
            response = await self.store.search_vectors(query)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Check T4 SLO: p95 <50ms
            if duration_ms > 50:
                self.slo_violations += 1
                logger.warning(f"Search SLO violation: {duration_ms:.2f}ms > 50ms")

            self.total_operations += 1
            return response

        except Exception as e:
            self.slo_violations += 1
            self.total_operations += 1
            logger.error(f"Search operation failed: {e}")
            raise

    def get_slo_compliance(self) -> float:
        """Get current SLO compliance rate"""
        if self.total_operations == 0:
            return 1.0
        return 1.0 - (self.slo_violations / self.total_operations)
