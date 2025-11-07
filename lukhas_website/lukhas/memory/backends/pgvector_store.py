"""
T4/0.01% Excellence PostgreSQL pgvector Backend

High-performance PostgreSQL backend with pgvector extension for vector similarity search.
Provides production-ready vector storage with ACID guarantees and advanced indexing.

Performance targets:
- Single upsert: <100ms p95
- Vector search: <50ms p95 (k≤10)
- Bulk upsert: <500ms p95 (100 docs)
- Index optimization: <30s (100k docs)
"""

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import asyncpg
import numpy as np
from asyncpg.pool import Pool

from core.common.logger import get_logger
from observability.service_metrics import get_metrics_collector

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


class PgVectorStore(AbstractVectorStore):
    """
    PostgreSQL backend with pgvector extension for vector similarity search.

    Features:
    - ACID transactions for data consistency
    - Advanced indexing (IVFFlat, HNSW)
    - Typed metadata with JSONB
    - Comprehensive performance monitoring
    - Automatic index optimization
    """

    def __init__(
        self,
        connection_string: str,
        table_name: str = "vector_documents",
        dimension: int = 1536,
        index_type: str = "hnsw",  # hnsw, ivfflat
        index_params: Optional[Dict[str, Any]] = None,
        pool_size: int = 10,
        max_pool_size: int = 20
    ):
        self.connection_string = connection_string
        self.table_name = table_name
        self.dimension = dimension
        self.index_type = index_type.lower()
        self.index_params = index_params or {}
        self.pool_size = pool_size
        self.max_pool_size = max_pool_size

        self.pool: Optional[Pool] = None
        self._initialized = False

        # Default index parameters
        if self.index_type == "hnsw":
            self.index_params.setdefault("m", 16)
            self.index_params.setdefault("ef_construction", 64)
        elif self.index_type == "ivfflat":
            self.index_params.setdefault("lists", 100)

    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and create tables"""
        if self._initialized:
            return

        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=self.pool_size,
                max_size=self.max_pool_size,
                command_timeout=60
            )

            # Initialize database schema
            await self._create_tables()
            await self._create_indexes()

            self._initialized = True
            logger.info(
                "PgVector store initialized",
                table_name=self.table_name,
                dimension=self.dimension,
                index_type=self.index_type,
                pool_size=self.pool_size
            )

        except Exception as e:
            logger.error("Failed to initialize PgVector store", error=str(e))
            raise VectorStoreError(f"Failed to initialize: {e}") from e

    async def shutdown(self) -> None:
        """Shutdown connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self._initialized = False
            logger.info("PgVector store shutdown")

    async def _create_tables(self) -> None:
        """Create necessary database tables"""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create main documents table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({self.dimension}) NOT NULL,
                metadata JSONB DEFAULT '{{}}'::jsonb,

                -- LUKHAS-specific fields
                identity_id TEXT,
                lane TEXT DEFAULT 'candidate',
                fold_id TEXT,
                tags TEXT[] DEFAULT ARRAY[]::TEXT[],

                -- Lifecycle fields
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                expires_at TIMESTAMPTZ,

                -- Performance tracking
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMPTZ,

                -- Add constraints
                CONSTRAINT valid_lane CHECK (lane IN ('candidate', 'integration', 'production')),
                CONSTRAINT valid_expires_at CHECK (expires_at IS NULL OR expires_at > created_at)
            );
            """
            await conn.execute(create_table_sql)

            # Create indexes for performance
            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_identity_id
            ON {self.table_name}(identity_id) WHERE identity_id IS NOT NULL;
            """)

            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_lane
            ON {self.table_name}(lane);
            """)

            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_fold_id
            ON {self.table_name}(fold_id) WHERE fold_id IS NOT NULL;
            """)

            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_expires_at
            ON {self.table_name}(expires_at) WHERE expires_at IS NOT NULL;
            """)

            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_tags
            ON {self.table_name} USING GIN(tags);
            """)

            await conn.execute(f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_{self.table_name}_metadata
            ON {self.table_name} USING GIN(metadata);
            """)

    async def _create_indexes(self) -> None:
        """Create vector similarity indexes"""
        async with self.pool.acquire() as conn:
            index_name = f"idx_{self.table_name}_embedding_{self.index_type}"

            if self.index_type == "hnsw":
                m = self.index_params.get("m", 16)
                ef_construction = self.index_params.get("ef_construction", 64)

                index_sql = f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name}
                ON {self.table_name}
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = {m}, ef_construction = {ef_construction});
                """

            elif self.index_type == "ivfflat":
                lists = self.index_params.get("lists", 100)

                index_sql = f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name}
                ON {self.table_name}
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = {lists});
                """
            else:
                raise VectorStoreError(f"Unsupported index type: {self.index_type}")

            await conn.execute(index_sql)
            logger.info(
                "Vector index created",
                index_name=index_name,
                index_type=self.index_type,
                params=self.index_params
            )

    async def add(self, document: VectorDocument) -> bool:
        """Add single document to PostgreSQL"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(document.embedding, self.dimension)
            document.embedding = self._normalize_vector(document.embedding)

            async with self.pool.acquire() as conn:
                insert_sql = f"""
                INSERT INTO {self.table_name} (
                    id, content, embedding, metadata, identity_id, lane, fold_id, tags,
                    created_at, updated_at, expires_at, access_count, last_accessed
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
                ) ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    identity_id = EXCLUDED.identity_id,
                    lane = EXCLUDED.lane,
                    fold_id = EXCLUDED.fold_id,
                    tags = EXCLUDED.tags,
                    updated_at = NOW(),
                    expires_at = EXCLUDED.expires_at;
                """

                await conn.execute(
                    insert_sql,
                    document.id,
                    document.content,
                    document.embedding.tolist(),
                    json.dumps(document.metadata),
                    document.identity_id,
                    document.lane,
                    document.fold_id,
                    document.tags,
                    document.created_at,
                    document.updated_at,
                    document.expires_at,
                    document.access_count,
                    document.last_accessed
                )

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("pgvector_add_duration_ms", duration_ms)
            metrics.increment_counter("pgvector_add_total")

            logger.debug(
                "Document added to PgVector",
                document_id=document.id,
                dimension=len(document.embedding),
                lane=document.lane,
                duration_ms=duration_ms
            )

            return True

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_add_errors")
            logger.error(
                "Failed to add document to PgVector",
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

            async with self.pool.acquire() as conn, conn.transaction():
                insert_sql = f"""
                    INSERT INTO {self.table_name} (
                        id, content, embedding, metadata, identity_id, lane, fold_id, tags,
                        created_at, updated_at, expires_at, access_count, last_accessed
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
                    ) ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW();
                    """

                results = []
                for doc in documents:
                    try:
                        await conn.execute(
                            insert_sql,
                            doc.id,
                            doc.content,
                            doc.embedding.tolist(),
                            json.dumps(doc.metadata),
                            doc.identity_id,
                            doc.lane,
                            doc.fold_id,
                            doc.tags,
                            doc.created_at,
                            doc.updated_at,
                            doc.expires_at,
                            doc.access_count,
                            doc.last_accessed
                        )
                        results.append(True)
                    except Exception as e:
                        logger.error(
                            "Failed to insert document in batch",
                            document_id=doc.id,
                            error=str(e)
                        )
                        results.append(False)

            duration_ms = (time.perf_counter() - start_time) * 1000
            success_count = sum(results)

            metrics.record_histogram("pgvector_bulk_add_duration_ms", duration_ms)
            metrics.increment_counter("pgvector_bulk_add_total")
            metrics.record_gauge("pgvector_bulk_add_success_count", success_count)

            logger.info(
                "Bulk add completed",
                total_documents=len(documents),
                successful=success_count,
                failed=len(documents) - success_count,
                duration_ms=duration_ms
            )

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_bulk_add_errors")
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
            async with self.pool.acquire() as conn:
                select_sql = f"""
                SELECT id, content, embedding, metadata, identity_id, lane, fold_id, tags,
                       created_at, updated_at, expires_at, access_count, last_accessed
                FROM {self.table_name}
                WHERE id = $1;
                """

                row = await conn.fetchrow(select_sql, document_id)

                if not row:
                    raise DocumentNotFoundError(f"Document {document_id} not found")

                # Update access tracking
                await conn.execute(f"""
                UPDATE {self.table_name}
                SET access_count = access_count + 1, last_accessed = NOW()
                WHERE id = $1;
                """, document_id)

                # Create document from row
                document = VectorDocument(
                    id=row["id"],
                    content=row["content"],
                    embedding=np.array(row["embedding"], dtype=np.float32),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    identity_id=row["identity_id"],
                    lane=row["lane"],
                    fold_id=row["fold_id"],
                    tags=list(row["tags"]) if row["tags"] else [],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    expires_at=row["expires_at"],
                    access_count=row["access_count"] + 1,
                    last_accessed=datetime.now(timezone.utc)
                )

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_get_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_get_total")

                return document

        except DocumentNotFoundError:
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_get_errors")
            logger.error(
                "Failed to get document from PgVector",
                document_id=document_id,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to get document: {e}") from e

    async def update(self, document: VectorDocument) -> bool:
        """Update existing document"""
        # PgVector uses UPSERT, so update is the same as add
        return await self.add(document)

    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        start_time = time.perf_counter()

        try:
            async with self.pool.acquire() as conn:
                delete_sql = f"DELETE FROM {self.table_name} WHERE id = $1;"
                result = await conn.execute(delete_sql, document_id)

                deleted = result.endswith("1")  # "DELETE 1" means success

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_delete_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_delete_total")

                if deleted:
                    logger.debug(
                        "Document deleted from PgVector",
                        document_id=document_id,
                        duration_ms=duration_ms
                    )

                return deleted

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_delete_errors")
            logger.error(
                "Failed to delete document from PgVector",
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
        """Vector similarity search using cosine similarity"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(query_vector, self.dimension)
            query_vector = self._normalize_vector(query_vector)

            # Build WHERE clause from filters
            where_conditions = []
            params = [query_vector.tolist(), k]
            param_idx = 3

            if filters:
                for key, value in filters.items():
                    if key == "identity_id":
                        where_conditions.append(f"identity_id = ${param_idx}")
                    elif key == "lane":
                        where_conditions.append(f"lane = ${param_idx}")
                    elif key == "fold_id":
                        where_conditions.append(f"fold_id = ${param_idx}")
                    elif key == "tags":
                        if isinstance(value, list):
                            where_conditions.append(f"tags && ${param_idx}")
                        else:
                            where_conditions.append(f"${param_idx} = ANY(tags)")
                    elif key.startswith("metadata."):
                        # JSONB path query
                        path = key[9:]  # Remove "metadata." prefix
                        where_conditions.append(f"metadata->>'{path}' = ${param_idx}")
                    else:
                        continue  # Skip unknown filter

                    params.append(value)
                    param_idx += 1

            # Add expiration filter
            where_conditions.append("(expires_at IS NULL OR expires_at > NOW())")

            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            search_sql = f"""
            SELECT id, content, embedding, metadata, identity_id, lane, fold_id, tags,
                   created_at, updated_at, expires_at, access_count, last_accessed,
                   1 - (embedding <=> $1) AS similarity_score
            FROM {self.table_name}
            {where_clause}
            ORDER BY embedding <=> $1
            LIMIT $2;
            """

            async with self.pool.acquire() as conn:
                rows = await conn.fetch(search_sql, *params)

                results = []
                for rank, row in enumerate(rows):
                    document = VectorDocument(
                        id=row["id"],
                        content=row["content"],
                        embedding=np.array(row["embedding"], dtype=np.float32),
                        metadata=json.loads(row["metadata"]) if row["metadata"] and include_metadata else {},
                        identity_id=row["identity_id"],
                        lane=row["lane"],
                        fold_id=row["fold_id"],
                        tags=list(row["tags"]) if row["tags"] else [],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        expires_at=row["expires_at"],
                        access_count=row["access_count"],
                        last_accessed=row["last_accessed"]
                    )

                    result = SearchResult(
                        document=document,
                        score=float(row["similarity_score"]),
                        rank=rank,
                        search_latency_ms=(time.perf_counter() - start_time) * 1000,
                        retrieval_method="pgvector"
                    )
                    results.append(result)

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_search_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_search_total")
                metrics.record_gauge("pgvector_search_results_count", len(results))

                logger.debug(
                    "Vector search completed",
                    k=k,
                    results_count=len(results),
                    duration_ms=duration_ms,
                    filters=filters
                )

                return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_search_errors")
            logger.error(
                "Failed vector search in PgVector",
                k=k,
                filters=filters,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed vector search: {e}") from e

    async def search_by_text(
        self,
        query_text: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Text-based search (requires external embedding service)"""
        # This would require an embedding service integration
        # For now, we'll do a simple text search as fallback
        start_time = time.perf_counter()

        try:
            where_conditions = ["content ILIKE $1"]
            params = [f"%{query_text}%", k]
            param_idx = 3

            # Add filters similar to vector search
            if filters:
                for key, value in filters.items():
                    if key in ["identity_id", "lane", "fold_id"]:
                        where_conditions.append(f"{key} = ${param_idx}")
                        params.append(value)
                        param_idx += 1

            # Add expiration filter
            where_conditions.append("(expires_at IS NULL OR expires_at > NOW())")

            where_clause = "WHERE " + " AND ".join(where_conditions)

            search_sql = f"""
            SELECT id, content, embedding, metadata, identity_id, lane, fold_id, tags,
                   created_at, updated_at, expires_at, access_count, last_accessed
            FROM {self.table_name}
            {where_clause}
            ORDER BY created_at DESC
            LIMIT $2;
            """

            async with self.pool.acquire() as conn:
                rows = await conn.fetch(search_sql, *params)

                results = []
                for rank, row in enumerate(rows):
                    document = VectorDocument(
                        id=row["id"],
                        content=row["content"],
                        embedding=np.array(row["embedding"], dtype=np.float32),
                        metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                        identity_id=row["identity_id"],
                        lane=row["lane"],
                        fold_id=row["fold_id"],
                        tags=list(row["tags"]) if row["tags"] else [],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        expires_at=row["expires_at"],
                        access_count=row["access_count"],
                        last_accessed=row["last_accessed"]
                    )

                    # Score based on text match (simplified)
                    score = 1.0 - (rank * 0.1)  # Simple ranking score

                    result = SearchResult(
                        document=document,
                        score=max(0.0, score),
                        rank=rank,
                        search_latency_ms=(time.perf_counter() - start_time) * 1000,
                        retrieval_method="text_search"
                    )
                    results.append(result)

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_text_search_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_text_search_total")

                return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_text_search_errors")
            logger.error(
                "Failed text search in PgVector",
                query_text=query_text,
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed text search: {e}") from e

    async def cleanup_expired(self) -> int:
        """Remove expired documents"""
        start_time = time.perf_counter()

        try:
            async with self.pool.acquire() as conn:
                delete_sql = f"""
                DELETE FROM {self.table_name}
                WHERE expires_at IS NOT NULL AND expires_at <= NOW();
                """
                result = await conn.execute(delete_sql)

                # Extract deleted count from result string like "DELETE 5"
                deleted_count = int(result.split()[-1]) if result.split()[-1].isdigit() else 0

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_cleanup_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_cleanup_total")
                metrics.record_gauge("pgvector_cleanup_deleted_count", deleted_count)

                logger.info(
                    "Expired documents cleaned up",
                    deleted_count=deleted_count,
                    duration_ms=duration_ms
                )

                return deleted_count

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_cleanup_errors")
            logger.error(
                "Failed to cleanup expired documents",
                error=str(e),
                duration_ms=duration_ms
            )
            return 0

    async def optimize_index(self) -> None:
        """Optimize vector indexes"""
        start_time = time.perf_counter()

        try:
            async with self.pool.acquire() as conn:
                # Analyze table for better query planning
                await conn.execute(f"ANALYZE {self.table_name};")

                # Rebuild indexes if necessary (careful with this in production)
                # await conn.execute(f"REINDEX TABLE {self.table_name};")

                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_histogram("pgvector_optimize_duration_ms", duration_ms)
                metrics.increment_counter("pgvector_optimize_total")

                logger.info(
                    "Index optimization completed",
                    table_name=self.table_name,
                    duration_ms=duration_ms
                )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("pgvector_optimize_errors")
            logger.error(
                "Failed to optimize indexes",
                error=str(e),
                duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to optimize indexes: {e}") from e

    async def get_stats(self) -> StorageStats:
        """Get comprehensive storage statistics"""
        try:
            async with self.pool.acquire() as conn:
                # Basic counts
                stats_sql = f"""
                SELECT
                    COUNT(*) as total_documents,
                    COUNT(*) FILTER (WHERE expires_at IS NULL OR expires_at > NOW()) as active_documents,
                    COUNT(*) FILTER (WHERE expires_at IS NOT NULL AND expires_at <= NOW()) as expired_documents,
                    AVG(access_count)::float as avg_access_count,
                    pg_total_relation_size('{self.table_name}')::bigint as table_size_bytes
                FROM {self.table_name};
                """

                stats_row = await conn.fetchrow(stats_sql)

                # Lane distribution
                lane_stats_sql = f"""
                SELECT lane, COUNT(*) as count
                FROM {self.table_name}
                WHERE expires_at IS NULL OR expires_at > NOW()
                GROUP BY lane;
                """
                lane_rows = await conn.fetch(lane_stats_sql)
                documents_by_lane = {row["lane"]: row["count"] for row in lane_rows}

                # Fold distribution
                fold_stats_sql = f"""
                SELECT fold_id, COUNT(*) as count
                FROM {self.table_name}
                WHERE fold_id IS NOT NULL AND (expires_at IS NULL OR expires_at > NOW())
                GROUP BY fold_id;
                """
                fold_rows = await conn.fetch(fold_stats_sql)
                documents_by_fold = {row["fold_id"]: row["count"] for row in fold_rows}

                return StorageStats(
                    total_documents=stats_row["total_documents"],
                    total_size_bytes=stats_row["table_size_bytes"],
                    active_documents=stats_row["active_documents"],
                    expired_documents=stats_row["expired_documents"],
                    avg_search_latency_ms=0.0,  # Would need metrics aggregation
                    avg_upsert_latency_ms=0.0,  # Would need metrics aggregation
                    p95_search_latency_ms=0.0,  # Would need metrics aggregation
                    p95_upsert_latency_ms=0.0,  # Would need metrics aggregation
                    memory_usage_bytes=0,  # PostgreSQL manages memory internally
                    disk_usage_bytes=stats_row["table_size_bytes"],
                    deduplication_rate=0.0,  # Would need duplicate tracking
                    compression_ratio=1.0,  # PostgreSQL handles compression
                    documents_by_lane=documents_by_lane,
                    documents_by_fold=documents_by_fold,
                    avg_dimension=float(self.dimension)
                )

        except Exception as e:
            logger.error("Failed to get PgVector stats", error=str(e))
            # Return empty stats on error
            return StorageStats(
                total_documents=0,
                total_size_bytes=0,
                active_documents=0,
                expired_documents=0,
                avg_search_latency_ms=0.0,
                avg_upsert_latency_ms=0.0,
                p95_search_latency_ms=0.0,
                p95_upsert_latency_ms=0.0,
                memory_usage_bytes=0,
                disk_usage_bytes=0,
                deduplication_rate=0.0,
                compression_ratio=1.0,
                documents_by_lane={},
                documents_by_fold={},
                avg_dimension=float(self.dimension)
            )

    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        try:
            async with self.pool.acquire() as conn:
                # Simple connectivity and performance check
                start_time = time.perf_counter()
                await conn.fetchval("SELECT 1")
                ping_latency_ms = (time.perf_counter() - start_time) * 1000

                # Get basic stats
                stats = await conn.fetchrow(f"""
                SELECT COUNT(*) as doc_count,
                       pg_database_size(current_database()) as db_size
                FROM {self.table_name};
                """)

                return {
                    "status": "healthy",
                    "ping_latency_ms": ping_latency_ms,
                    "connection_pool_size": self.pool.get_size(),
                    "document_count": stats["doc_count"],
                    "database_size_bytes": stats["db_size"],
                    "index_type": self.index_type,
                    "dimension": self.dimension,
                    "table_name": self.table_name
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
