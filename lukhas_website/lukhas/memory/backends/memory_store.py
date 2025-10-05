"""
T4/0.01% Excellence In-Memory Vector Store

High-performance in-memory vector store for development, testing, and small-scale deployments.
Optimized for rapid prototyping with full feature parity to production backends.

Performance targets:
- Single upsert: <5ms p95
- Vector search: <10ms p95 (k≤10)
- Exact search: 100% precision/recall
- Memory efficient: <1GB for 100k vectors (1536d)
"""

import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.spatial.distance import cosine

from lukhas.core.common.logger import get_logger
from lukhas.observability.service_metrics import get_metrics_collector

from .base import (
    AbstractVectorStore,
    DocumentNotFoundError,
    SearchResult,
    StorageStats,
    VectorDocument,
    VectorStoreError,
)

logger = get_logger(__name__)
metrics = get_metrics_collector()


class InMemoryVectorStore(AbstractVectorStore):
    """
    In-memory vector store with exact similarity search.

    Features:
    - Exact cosine similarity search
    - Full filtering capabilities
    - Thread-safe operations
    - Comprehensive performance tracking
    - Memory-efficient storage
    - Development-friendly debugging
    """

    def __init__(
        self,
        dimension: int = 1536,
        similarity_metric: str = "cosine",
        max_documents: int = 1000000,
        enable_caching: bool = True
    ):
        self.dimension = dimension
        self.similarity_metric = similarity_metric.lower()
        self.max_documents = max_documents
        self.enable_caching = enable_caching

        # Document storage
        self.documents: Dict[str, VectorDocument] = {}
        self.embeddings: Dict[str, np.ndarray] = {}

        # Search cache for frequently used queries
        self.query_cache: Dict[str, List[SearchResult]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # Thread safety
        self._lock = threading.RLock()

        # Performance tracking
        self.operation_counts = {
            "add": 0,
            "get": 0,
            "delete": 0,
            "search": 0,
            "cleanup": 0
        }

        self.operation_times = {
            "add": [],
            "get": [],
            "delete": [],
            "search": [],
            "cleanup": []
        }

        self._initialized = False

        if self.similarity_metric not in ["cosine", "euclidean", "dot"]:
            raise VectorStoreError(f"Unsupported similarity metric: {similarity_metric}")

    async def initialize(self) -> None:
        """Initialize in-memory store"""
        if self._initialized:
            return

        try:
            with self._lock:
                # Clear any existing data
                self.documents.clear()
                self.embeddings.clear()
                self.query_cache.clear()

                # Reset counters
                self.cache_hits = 0
                self.cache_misses = 0
                for key in self.operation_counts:
                    self.operation_counts[key] = 0
                    self.operation_times[key].clear()

                self._initialized = True

                logger.info(
                    "In-memory vector store initialized",
                    dimension=self.dimension,
                    similarity_metric=self.similarity_metric,
                    max_documents=self.max_documents
                )

        except Exception as e:
            logger.error("Failed to initialize in-memory store", error=str(e))
            raise VectorStoreError(f"Failed to initialize: {e}") from e

    async def shutdown(self) -> None:
        """Shutdown in-memory store"""
        try:
            with self._lock:
                self.documents.clear()
                self.embeddings.clear()
                self.query_cache.clear()

                self._initialized = False

                logger.info(
                    "In-memory store shutdown",
                    final_document_count=len(self.documents)
                )

        except Exception as e:
            logger.error("Error during in-memory store shutdown", error=str(e))

    async def add(self, document: VectorDocument) -> bool:
        """Add single document to memory"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(document.embedding, self.dimension)
            document.embedding = self._normalize_vector(document.embedding)

            with self._lock:
                # Check capacity
                if len(self.documents) >= self.max_documents and document.id not in self.documents:
                    raise VectorStoreError(f"Maximum document limit reached: {self.max_documents}")

                # Store document and embedding
                self.documents[document.id] = document
                self.embeddings[document.id] = document.embedding.copy()

                # Clear cache if enabled (document change invalidates cache)
                if self.enable_caching:
                    self.query_cache.clear()

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._record_operation("add", duration_ms)

            logger.debug(
                "Document added to memory store",
                document_id=document.id,
                dimension=len(document.embedding),
                lane=document.lane,
                total_documents=len(self.documents),
                duration_ms=duration_ms
            )

            return True

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_add_errors")
            logger.error(
                "Failed to add document to memory store",
                document_id=document.id,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to add document: {e}") from e

    async def bulk_add(self, documents: List[VectorDocument]) -> List[bool]:
        """Add multiple documents in batch"""
        start_time = time.perf_counter()

        try:
            if not documents:
                return []

            # Validate all documents first
            for doc in documents:
                self._validate_dimension(doc.embedding, self.dimension)
                doc.embedding = self._normalize_vector(doc.embedding)

            results = []

            with self._lock:
                for doc in documents:
                    try:
                        # Check capacity
                        if len(self.documents) >= self.max_documents and doc.id not in self.documents:
                            results.append(False)
                            continue

                        # Store document
                        self.documents[doc.id] = doc
                        self.embeddings[doc.id] = doc.embedding.copy()
                        results.append(True)

                    except Exception as e:
                        logger.error("Failed to add document in bulk", document_id=doc.id, error=str(e))
                        results.append(False)

                # Clear cache
                if self.enable_caching:
                    self.query_cache.clear()

            duration_ms = (time.perf_counter() - start_time) * 1000
            success_count = sum(results)
            self._record_operation("add", duration_ms)

            logger.info(
                "Bulk add completed",
                total_documents=len(documents),
                successful=success_count,
                failed=len(documents) - success_count,
                total_stored=len(self.documents),
                duration_ms=duration_ms
            )

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_bulk_add_errors")
            logger.error(
                "Failed bulk add operation",
                document_count=len(documents),
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed bulk add: {e}") from e

    async def get(self, document_id: str) -> VectorDocument:
        """Get document by ID"""
        start_time = time.perf_counter()

        try:
            with self._lock:
                if document_id not in self.documents:
                    raise DocumentNotFoundError(f"Document {document_id} not found")

                document = self.documents[document_id]

                # Update access tracking
                document.touch()

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._record_operation("get", duration_ms)

            return document

        except DocumentNotFoundError:
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_get_errors")
            logger.error(
                "Failed to get document from memory store",
                document_id=document_id,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to get document: {e}") from e

    async def update(self, document: VectorDocument) -> bool:
        """Update existing document (same as add for in-memory)"""
        return await self.add(document)

    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        start_time = time.perf_counter()

        try:
            with self._lock:
                if document_id not in self.documents:
                    return False

                # Remove document and embedding
                del self.documents[document_id]
                del self.embeddings[document_id]

                # Clear cache
                if self.enable_caching:
                    self.query_cache.clear()

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._record_operation("delete", duration_ms)

            logger.debug(
                "Document deleted from memory store",
                document_id=document_id,
                remaining_documents=len(self.documents),
                duration_ms=duration_ms
            )

            return True

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_delete_errors")
            logger.error(
                "Failed to delete document from memory store",
                document_id=document_id,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to delete document: {e}") from e

    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Vector similarity search with exact computation"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(query_vector, self.dimension)
            query_vector = self._normalize_vector(query_vector)

            # Check cache if enabled
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(query_vector, k, filters)
                if cache_key in self.query_cache:
                    self.cache_hits += 1
                    return self.query_cache[cache_key]
                else:
                    self.cache_misses += 1

            candidates = []

            with self._lock:
                for doc_id, document in self.documents.items():
                    # Skip expired documents
                    if document.is_expired:
                        continue

                    # Apply filters
                    if filters and not self._matches_filters(document, filters):
                        continue

                    # Calculate similarity
                    embedding = self.embeddings[doc_id]
                    similarity = self._calculate_similarity(query_vector, embedding)

                    candidates.append((similarity, doc_id, document))

            # Sort by similarity (highest first) and take top k
            candidates.sort(key=lambda x: x[0], reverse=True)
            candidates = candidates[:k]

            # Create search results
            results = []
            for rank, (score, doc_id, document) in enumerate(candidates):
                result = SearchResult(
                    document=document,
                    score=score,
                    rank=rank,
                    search_latency_ms=(time.perf_counter() - start_time) * 1000,
                    retrieval_method="exact"
                )
                results.append(result)

            # Cache results if enabled
            if self.enable_caching and cache_key:
                self.query_cache[cache_key] = results
                # Limit cache size
                if len(self.query_cache) > 100:
                    # Remove oldest entry (simple FIFO)
                    oldest_key = next(iter(self.query_cache))
                    del self.query_cache[oldest_key]

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._record_operation("search", duration_ms)

            logger.debug(
                "Memory store search completed",
                k=k,
                candidates_evaluated=len(self.documents),
                results_count=len(results),
                duration_ms=duration_ms,
                cache_hit=cache_key in self.query_cache if cache_key else False,
                filters=filters
            )

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_search_errors")
            logger.error(
                "Failed search in memory store",
                k=k,
                filters=filters,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed search: {e}") from e

    async def search_by_text(
        self,
        query_text: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Text-based search using exact text matching"""
        start_time = time.perf_counter()

        try:
            query_lower = query_text.lower()
            candidates = []

            with self._lock:
                for doc_id, document in self.documents.items():
                    # Skip expired documents
                    if document.is_expired:
                        continue

                    # Apply filters
                    if filters and not self._matches_filters(document, filters):
                        continue

                    # Text matching
                    content_lower = document.content.lower()
                    if query_lower in content_lower:
                        # Simple scoring based on position and frequency
                        score = self._calculate_text_score(query_lower, content_lower)
                        candidates.append((score, doc_id, document))

            # Sort by score and take top k
            candidates.sort(key=lambda x: x[0], reverse=True)
            candidates = candidates[:k]

            # Create results
            results = []
            for rank, (score, doc_id, document) in enumerate(candidates):
                result = SearchResult(
                    document=document,
                    score=score,
                    rank=rank,
                    search_latency_ms=(time.perf_counter() - start_time) * 1000,
                    retrieval_method="text_search"
                )
                results.append(result)

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("memory_store_text_search_duration_ms", duration_ms)
            metrics.increment_counter("memory_store_text_search_total")

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_text_search_errors")
            logger.error(
                "Failed text search in memory store",
                query_text=query_text,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed text search: {e}") from e

    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between two vectors"""
        if self.similarity_metric == "cosine":
            # Using 1 - cosine distance for similarity (higher = more similar)
            return 1.0 - cosine(vec1, vec2)
        elif self.similarity_metric == "dot":
            # Dot product (assumes normalized vectors)
            return float(np.dot(vec1, vec2))
        elif self.similarity_metric == "euclidean":
            # Convert Euclidean distance to similarity
            distance = np.linalg.norm(vec1 - vec2)
            return 1.0 / (1.0 + distance)
        else:
            raise VectorStoreError(f"Unknown similarity metric: {self.similarity_metric}")

    def _calculate_text_score(self, query: str, content: str) -> float:
        """Calculate text similarity score"""
        # Simple scoring: frequency and early occurrence bonus
        frequency = content.count(query)
        first_position = content.find(query)

        if frequency == 0:
            return 0.0

        # Base score from frequency
        score = min(frequency * 0.1, 1.0)

        # Bonus for early occurrence
        if first_position < 100:
            score += 0.2 * (1.0 - first_position / 100.0)

        return min(score, 1.0)

    def _matches_filters(self, document: VectorDocument, filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        for key, value in filters.items():
            if key == "identity_id":
                if document.identity_id != value:
                    return False
            elif key == "lane":
                if document.lane != value:
                    return False
            elif key == "fold_id":
                if document.fold_id != value:
                    return False
            elif key == "tags":
                if isinstance(value, list):
                    if not any(tag in document.tags for tag in value):
                        return False
                else:
                    if value not in document.tags:
                        return False
            elif key.startswith("metadata."):
                path = key[9:]  # Remove "metadata." prefix
                if path not in document.metadata or document.metadata[path] != value:
                    return False

        return True

    def _generate_cache_key(self, query_vector: np.ndarray, k: int, filters: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query"""
        # Simple hash of query vector + parameters
        vector_hash = hash(query_vector.tobytes())
        filters_str = str(sorted(filters.items())) if filters else ""
        return f"{vector_hash}:{k}:{filters_str}"

    def _record_operation(self, operation: str, duration_ms: float):
        """Record operation for performance tracking"""
        self.operation_counts[operation] += 1
        self.operation_times[operation].append(duration_ms)

        # Keep only last 1000 times to prevent memory growth
        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]

        # Record metrics
        metrics.record_histogram(f"memory_store_{operation}_duration_ms", duration_ms)
        metrics.increment_counter(f"memory_store_{operation}_total")

    async def cleanup_expired(self) -> int:
        """Remove expired documents"""
        start_time = time.perf_counter()
        deleted_count = 0

        try:
            with self._lock:
                expired_ids = []
                for doc_id, document in self.documents.items():
                    if document.is_expired:
                        expired_ids.append(doc_id)

                # Remove expired documents
                for doc_id in expired_ids:
                    del self.documents[doc_id]
                    del self.embeddings[doc_id]
                    deleted_count += 1

                # Clear cache
                if self.enable_caching and deleted_count > 0:
                    self.query_cache.clear()

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._record_operation("cleanup", duration_ms)

            logger.info(
                "Expired documents cleaned up",
                deleted_count=deleted_count,
                remaining_documents=len(self.documents),
                duration_ms=duration_ms
            )

            return deleted_count

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("memory_store_cleanup_errors")
            logger.error(
                "Failed to cleanup expired documents",
                error=str(e),
                duration_ms=duration_ms
            )
            return 0

    async def optimize_index(self) -> None:
        """Optimize in-memory storage (mostly a no-op)"""
        start_time = time.perf_counter()

        try:
            with self._lock:
                # Clear query cache to free memory
                if self.enable_caching:
                    cache_size_before = len(self.query_cache)
                    self.query_cache.clear()
                    logger.info(
                        "Query cache cleared",
                        cache_entries_removed=cache_size_before
                    )

                # Cleanup operation time history
                for operation in self.operation_times:
                    if len(self.operation_times[operation]) > 100:
                        self.operation_times[operation] = self.operation_times[operation][-100:]

            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Memory store optimization completed",
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.error("Failed to optimize memory store", error=str(e))

    async def get_stats(self) -> StorageStats:
        """Get comprehensive storage statistics"""
        try:
            with self._lock:
                total_docs = len(self.documents)
                active_docs = sum(1 for doc in self.documents.values() if not doc.is_expired)
                expired_docs = total_docs - active_docs

                # Calculate memory usage
                doc_memory = sum(
                    len(doc.content.encode('utf-8')) + doc.embedding.nbytes
                    for doc in self.documents.values()
                )
                embedding_memory = sum(emb.nbytes for emb in self.embeddings.values())

                # Performance statistics
                def calc_avg_latency(operation: str) -> float:
                    times = self.operation_times.get(operation, [])
                    return sum(times) / len(times) if times else 0.0

                def calc_p95_latency(operation: str) -> float:
                    times = sorted(self.operation_times.get(operation, []))
                    if not times:
                        return 0.0
                    idx = int(len(times) * 0.95)
                    return times[min(idx, len(times) - 1)]

                # Lane distribution
                documents_by_lane = {}
                for doc in self.documents.values():
                    if not doc.is_expired:
                        documents_by_lane[doc.lane] = documents_by_lane.get(doc.lane, 0) + 1

                # Fold distribution
                documents_by_fold = {}
                for doc in self.documents.values():
                    if not doc.is_expired and doc.fold_id:
                        documents_by_fold[doc.fold_id] = documents_by_fold.get(doc.fold_id, 0) + 1

                return StorageStats(
                    total_documents=total_docs,
                    total_size_bytes=doc_memory + embedding_memory,
                    active_documents=active_docs,
                    expired_documents=expired_docs,
                    avg_search_latency_ms=calc_avg_latency("search"),
                    avg_upsert_latency_ms=calc_avg_latency("add"),
                    p95_search_latency_ms=calc_p95_latency("search"),
                    p95_upsert_latency_ms=calc_p95_latency("add"),
                    memory_usage_bytes=doc_memory + embedding_memory,
                    disk_usage_bytes=0,  # In-memory only
                    deduplication_rate=0.0,  # Not implemented
                    compression_ratio=1.0,   # No compression
                    documents_by_lane=documents_by_lane,
                    documents_by_fold=documents_by_fold,
                    avg_dimension=float(self.dimension)
                )

        except Exception as e:
            logger.error("Failed to get memory store stats", error=str(e))
            return StorageStats(
                total_documents=0, total_size_bytes=0, active_documents=0, expired_documents=0,
                avg_search_latency_ms=0.0, avg_upsert_latency_ms=0.0,
                p95_search_latency_ms=0.0, p95_upsert_latency_ms=0.0,
                memory_usage_bytes=0, disk_usage_bytes=0,
                deduplication_rate=0.0, compression_ratio=1.0,
                documents_by_lane={}, documents_by_fold={}, avg_dimension=float(self.dimension)
            )

    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        try:
            with self._lock:
                total_operations = sum(self.operation_counts.values())
                cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0

                return {
                    "status": "healthy",
                    "dimension": self.dimension,
                    "similarity_metric": self.similarity_metric,
                    "document_count": len(self.documents),
                    "max_documents": self.max_documents,
                    "total_operations": total_operations,
                    "operation_counts": self.operation_counts.copy(),
                    "cache_enabled": self.enable_caching,
                    "cache_hit_rate": cache_hit_rate,
                    "cache_size": len(self.query_cache),
                    "memory_usage_mb": sum(emb.nbytes for emb in self.embeddings.values()) / (1024 * 1024)
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
