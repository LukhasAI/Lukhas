"""
Memory Read API Service
======================

High-performance read-only memory operations with T4/0.01% excellence:
- Search operations (semantic, keyword, hybrid)
- Top-K retrieval with relevance ranking
- Memory fold access and filtering
- Performance target: p95 <100ms, p99 <150ms

Features:
- Async/await for high concurrency
- Circuit breaker protection
- Prometheus metrics
- Backpressure handling
- Query optimization
"""

import asyncio
import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from lukhas.memory.consciousness_memory_integration import ConsciousnessMemoryIntegrator, MemoryFoldType
from lukhas.memory.fold_system import MemoryFold

from .adapters.vector_store_base import VectorStoreAdapter
from .backpressure import BackpressureManager

# Import services components
from .circuit_breaker import MemoryCircuitBreaker
from .metrics import MemoryMetrics

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """Search operation types"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    EXACT_MATCH = "exact_match"


class SortOrder(Enum):
    """Result sorting options"""
    RELEVANCE_DESC = "relevance_desc"
    TIMESTAMP_DESC = "timestamp_desc"
    TIMESTAMP_ASC = "timestamp_asc"
    PRIORITY_DESC = "priority_desc"


@dataclass
class SearchQuery:
    """Search query with parameters"""
    query_text: str
    search_type: SearchType = SearchType.HYBRID
    max_results: int = 10
    min_similarity: float = 0.7
    fold_types: Optional[Set[MemoryFoldType]] = None
    tags: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    sort_order: SortOrder = SortOrder.RELEVANCE_DESC
    include_metadata: bool = True
    query_id: str = field(default_factory=lambda: f"q_{uuid.uuid4().hex[:8]}")


@dataclass
class SearchResult:
    """Search result with metadata"""
    fold_id: str
    fold_type: MemoryFoldType
    content: str
    similarity_score: float
    timestamp: datetime
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResponse:
    """Complete search response"""
    query_id: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    query: SearchQuery
    processing_stats: Dict[str, Any] = field(default_factory=dict)


class MemoryReadService:
    """
    High-performance memory read service with T4/0.01% excellence.

    Provides semantic search, top-K retrieval, and memory fold access
    with strict performance SLOs and reliability guarantees.
    """

    def __init__(self,
                 vector_store: VectorStoreAdapter,
                 consciousness_integrator: Optional[ConsciousnessMemoryIntegrator] = None,
                 max_concurrent_queries: int = 50,
                 query_timeout_ms: int = 2000):
        """Initialize memory read service"""
        self.vector_store = vector_store
        self.consciousness_integrator = consciousness_integrator
        self.max_concurrent_queries = max_concurrent_queries
        self.query_timeout_ms = query_timeout_ms

        # Service components
        self.circuit_breaker = MemoryCircuitBreaker(
            failure_threshold=5,
            recovery_timeout_ms=30000
        )
        self.backpressure = BackpressureManager(
            max_tokens=max_concurrent_queries,
            refill_rate=10.0  # tokens per second
        )
        self.metrics = MemoryMetrics()

        # Query optimization
        self.query_cache: Dict[str, Tuple[SearchResponse, float]] = {}
        self.cache_ttl_seconds = 300  # 5 minutes

        # Connection pool
        self._query_semaphore = asyncio.Semaphore(max_concurrent_queries)

        logger.info(f"MemoryReadService initialized with max_concurrent_queries={max_concurrent_queries}")

    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Execute search query with performance monitoring.
        Target: p95 <100ms, p99 <150ms
        """
        start_time = time.perf_counter()

        # Validate query
        self._validate_search_query(query)

        # Check backpressure
        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            # Check cache first
            cached_result = self._get_cached_result(query)
            if cached_result:
                self.metrics.record_cache_hit(query.search_type.value)
                return cached_result

            # Execute search with circuit breaker protection
            async with self._query_semaphore:
                response = await self.circuit_breaker.call(
                    self._execute_search_query, query
                )

            # Cache result
            self._cache_result(query, response)

            # Record metrics
            search_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_search_latency(
                search_time_ms, query.search_type.value, len(response.results)
            )

            # Update response timing
            response.search_time_ms = search_time_ms

            logger.debug(f"Search completed: {query.query_id} in {search_time_ms:.2f}ms")
            return response

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_search_error(query.search_type.value, str(e))
            logger.error(f"Search failed: {query.query_id} after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def get_top_k(self,
                       embedding: List[float],
                       k: int = 10,
                       fold_types: Optional[Set[MemoryFoldType]] = None,
                       min_similarity: float = 0.0) -> List[SearchResult]:
        """
        Get top-K most similar memory folds by embedding.
        Target: p95 <100ms
        """
        start_time = time.perf_counter()

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            async with self._query_semaphore:
                results = await self.circuit_breaker.call(
                    self._execute_top_k_query,
                    embedding, k, fold_types, min_similarity
                )

            # Record metrics
            retrieval_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_retrieval_latency(retrieval_time_ms, k, len(results))

            logger.debug(f"Top-K retrieval completed in {retrieval_time_ms:.2f}ms: {len(results)} results")
            return results

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_retrieval_error(str(e))
            logger.error(f"Top-K retrieval failed after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def get_memory_fold(self, fold_id: str) -> Optional[MemoryFold]:
        """Get specific memory fold by ID"""
        start_time = time.perf_counter()

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            async with self._query_semaphore:
                fold = await self.circuit_breaker.call(
                    self._get_fold_by_id, fold_id
                )

            # Record metrics
            retrieval_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_fold_access_latency(retrieval_time_ms, fold is not None)

            return fold

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_fold_access_error(fold_id, str(e))
            logger.error(f"Fold access failed: {fold_id} after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def list_memory_folds(self,
                              fold_types: Optional[Set[MemoryFoldType]] = None,
                              tags: Optional[List[str]] = None,
                              limit: int = 100,
                              offset: int = 0) -> List[SearchResult]:
        """List memory folds with filtering and pagination"""
        start_time = time.perf_counter()

        if not await self.backpressure.acquire_token():
            raise Exception("Service overloaded - backpressure active")

        try:
            async with self._query_semaphore:
                results = await self.circuit_breaker.call(
                    self._list_folds,
                    fold_types, tags, limit, offset
                )

            # Record metrics
            list_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_list_latency(list_time_ms, len(results))

            return results

        except Exception as e:
            error_time_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.record_list_error(str(e))
            logger.error(f"List folds failed after {error_time_ms:.2f}ms - {e}")
            raise
        finally:
            self.backpressure.release_token()

    async def _execute_search_query(self, query: SearchQuery) -> SearchResponse:
        """Execute the actual search query"""
        try:
            # Convert query to vector store format
            if query.search_type == SearchType.SEMANTIC:
                # Generate embedding for semantic search
                embedding = await self._generate_query_embedding(query.query_text)
                raw_results = await self.vector_store.semantic_search(
                    embedding=embedding,
                    limit=query.max_results,
                    min_similarity=query.min_similarity,
                    filters=self._build_filters(query)
                )
            elif query.search_type == SearchType.KEYWORD:
                raw_results = await self.vector_store.keyword_search(
                    query=query.query_text,
                    limit=query.max_results,
                    filters=self._build_filters(query)
                )
            elif query.search_type == SearchType.HYBRID:
                raw_results = await self.vector_store.hybrid_search(
                    query=query.query_text,
                    limit=query.max_results,
                    min_similarity=query.min_similarity,
                    filters=self._build_filters(query)
                )
            else:
                raw_results = await self.vector_store.exact_match(
                    query=query.query_text,
                    limit=query.max_results,
                    filters=self._build_filters(query)
                )

            # Convert results to SearchResult objects
            results = []
            for raw_result in raw_results:
                search_result = SearchResult(
                    fold_id=raw_result['fold_id'],
                    fold_type=MemoryFoldType(raw_result.get('fold_type', 'episodic')),
                    content=raw_result['content'],
                    similarity_score=raw_result.get('score', 0.0),
                    timestamp=raw_result.get('timestamp', datetime.now(timezone.utc)),
                    tags=raw_result.get('tags', []),
                    metadata=raw_result.get('metadata', {}),
                    embedding=raw_result.get('embedding') if query.include_metadata else None
                )
                results.append(search_result)

            # Apply sorting
            results = self._sort_results(results, query.sort_order)

            return SearchResponse(
                query_id=query.query_id,
                results=results,
                total_results=len(results),
                search_time_ms=0,  # Will be set by caller
                query=query,
                processing_stats={
                    'vector_store_results': len(raw_results),
                    'filtered_results': len(results),
                    'search_type': query.search_type.value
                }
            )

        except Exception as e:
            logger.error(f"Search execution failed for query {query.query_id}: {e}")
            raise

    async def _execute_top_k_query(self,
                                  embedding: List[float],
                                  k: int,
                                  fold_types: Optional[Set[MemoryFoldType]],
                                  min_similarity: float) -> List[SearchResult]:
        """Execute top-K similarity search"""
        filters = {}
        if fold_types:
            filters['fold_types'] = [ft.value for ft in fold_types]

        raw_results = await self.vector_store.semantic_search(
            embedding=embedding,
            limit=k,
            min_similarity=min_similarity,
            filters=filters
        )

        results = []
        for raw_result in raw_results:
            search_result = SearchResult(
                fold_id=raw_result['fold_id'],
                fold_type=MemoryFoldType(raw_result.get('fold_type', 'episodic')),
                content=raw_result['content'],
                similarity_score=raw_result.get('score', 0.0),
                timestamp=raw_result.get('timestamp', datetime.now(timezone.utc)),
                tags=raw_result.get('tags', []),
                metadata=raw_result.get('metadata', {})
            )
            results.append(search_result)

        return results

    async def _get_fold_by_id(self, fold_id: str) -> Optional[MemoryFold]:
        """Get memory fold by ID"""
        raw_fold = await self.vector_store.get_by_id(fold_id)
        if not raw_fold:
            return None

        # Convert to MemoryFold object
        # This would need to be implemented based on the actual MemoryFold structure
        return MemoryFold(
            fold_id=raw_fold['fold_id'],
            content=raw_fold['content'],
            fold_type=MemoryFoldType(raw_fold.get('fold_type', 'episodic')),
            timestamp=raw_fold.get('timestamp', datetime.now(timezone.utc)),
            tags=raw_fold.get('tags', []),
            metadata=raw_fold.get('metadata', {}),
            embedding=raw_fold.get('embedding', [])
        )

    async def _list_folds(self,
                         fold_types: Optional[Set[MemoryFoldType]],
                         tags: Optional[List[str]],
                         limit: int,
                         offset: int) -> List[SearchResult]:
        """List memory folds with filtering"""
        filters = {}
        if fold_types:
            filters['fold_types'] = [ft.value for ft in fold_types]
        if tags:
            filters['tags'] = tags

        raw_results = await self.vector_store.list_documents(
            limit=limit,
            offset=offset,
            filters=filters
        )

        results = []
        for raw_result in raw_results:
            search_result = SearchResult(
                fold_id=raw_result['fold_id'],
                fold_type=MemoryFoldType(raw_result.get('fold_type', 'episodic')),
                content=raw_result['content'],
                similarity_score=1.0,  # No similarity for list operations
                timestamp=raw_result.get('timestamp', datetime.now(timezone.utc)),
                tags=raw_result.get('tags', []),
                metadata=raw_result.get('metadata', {})
            )
            results.append(search_result)

        return results

    async def _generate_query_embedding(self, query_text: str) -> List[float]:
        """Generate embedding for query text"""
        # This would use the consciousness integrator or a dedicated embedding service
        if self.consciousness_integrator:
            return await self.consciousness_integrator.generate_embedding(query_text)
        else:
            # Fallback embedding (would need actual implementation)
            return [0.0] * 768  # Placeholder

    def _build_filters(self, query: SearchQuery) -> Dict[str, Any]:
        """Build filter dictionary from search query"""
        filters = {}

        if query.fold_types:
            filters['fold_types'] = [ft.value for ft in query.fold_types]

        if query.tags:
            filters['tags'] = query.tags

        if query.date_range:
            filters['timestamp_range'] = {
                'start': query.date_range[0],
                'end': query.date_range[1]
            }

        return filters

    def _sort_results(self, results: List[SearchResult], sort_order: SortOrder) -> List[SearchResult]:
        """Sort search results by specified order"""
        if sort_order == SortOrder.RELEVANCE_DESC:
            return sorted(results, key=lambda r: r.similarity_score, reverse=True)
        elif sort_order == SortOrder.TIMESTAMP_DESC:
            return sorted(results, key=lambda r: r.timestamp, reverse=True)
        elif sort_order == SortOrder.TIMESTAMP_ASC:
            return sorted(results, key=lambda r: r.timestamp)
        else:  # PRIORITY_DESC - would need priority field
            return results

    def _validate_search_query(self, query: SearchQuery):
        """Validate search query parameters"""
        if not query.query_text or len(query.query_text.strip()) == 0:
            raise ValueError("Query text cannot be empty")

        if query.max_results <= 0 or query.max_results > 1000:
            raise ValueError("max_results must be between 1 and 1000")

        if query.min_similarity < 0.0 or query.min_similarity > 1.0:
            raise ValueError("min_similarity must be between 0.0 and 1.0")

    def _get_cached_result(self, query: SearchQuery) -> Optional[SearchResponse]:
        """Get cached search result if available and fresh"""
        cache_key = self._generate_cache_key(query)
        if cache_key in self.query_cache:
            cached_response, cache_time = self.query_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl_seconds:
                return cached_response
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        return None

    def _cache_result(self, query: SearchQuery, response: SearchResponse):
        """Cache search result"""
        cache_key = self._generate_cache_key(query)
        self.query_cache[cache_key] = (response, time.time())

        # Limit cache size
        if len(self.query_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.query_cache.keys(),
                key=lambda k: self.query_cache[k][1]
            )[:100]
            for key in oldest_keys:
                del self.query_cache[key]

    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key from search query"""
        # Create deterministic hash of query parameters
        key_parts = [
            query.query_text,
            query.search_type.value,
            str(query.max_results),
            str(query.min_similarity),
            str(sorted(query.fold_types) if query.fold_types else ""),
            str(sorted(query.tags) if query.tags else ""),
            str(query.date_range),
            query.sort_order.value
        ]
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()[:16]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        return {
            **self.metrics.get_metrics(),
            'circuit_breaker_state': self.circuit_breaker.get_state(),
            'backpressure_tokens_available': self.backpressure.get_available_tokens(),
            'active_queries': self.max_concurrent_queries - self._query_semaphore._value,
            'cache_size': len(self.query_cache)
        }

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            # Test vector store connection
            await self.vector_store.health_check()

            return {
                'status': 'healthy',
                'service': 'memory_read',
                'performance_metrics': self.get_performance_metrics(),
                'vector_store_healthy': True,
                'circuit_breaker_open': self.circuit_breaker.is_open(),
                'backpressure_active': self.backpressure.is_limiting()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': 'memory_read',
                'error': str(e),
                'circuit_breaker_open': self.circuit_breaker.is_open(),
                'backpressure_active': self.backpressure.is_limiting()
            }
