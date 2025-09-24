"""
PostgreSQL pgvector Vector Store Implementation
==============================================

High-performance vector store using PostgreSQL with pgvector extension.
Optimized for T4/0.01% excellence with <50ms p95 search latency.

Features:
- Native SQL vector operations with pgvector
- HNSW and IVFFlat index support
- Connection pooling and prepared statements
- Batch operations with COPY protocol
- Comprehensive error handling and monitoring
"""

import asyncio
import asyncpg
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import asdict
import numpy as np

from .vector_store_base import (
    VectorStoreBase,
    BatchVectorStoreBase,
    VectorDocument,
    VectorSearchQuery,
    VectorSearchResult,
    VectorSearchResponse,
    VectorStoreType,
    VectorStoreError,
    VectorStoreDimensionError,
    VectorStoreConnectionError,
    VectorStoreFactory
)

logger = logging.getLogger(__name__)


class PostgreSQLVectorStore(BatchVectorStoreBase):
    """
    PostgreSQL vector store implementation using pgvector extension.

    Configuration:
        host: PostgreSQL host
        port: PostgreSQL port
        database: Database name
        user: Username
        password: Password
        table_name: Vector table name (default: vector_documents)
        pool_size: Connection pool size (default: 10)
        vector_dimensions: Expected vector dimensions
        index_type: 'hnsw' or 'ivfflat' (default: hnsw)
        index_params: Index-specific parameters
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pool: Optional[asyncpg.Pool] = None
        self.table_name = config.get('table_name', 'vector_documents')
        self.vector_dimensions = config.get('vector_dimensions', 1536)
        self.index_type = config.get('index_type', 'hnsw')
        self.index_params = config.get('index_params', {'m': 16, 'ef_construction': 64})

        # Connection configuration
        self.db_config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 5432),
            'database': config.get('database', 'lukhas'),
            'user': config.get('user', 'postgres'),
            'password': config.get('password', ''),
            'min_size': config.get('pool_min_size', 5),
            'max_size': config.get('pool_size', 10),
            'command_timeout': config.get('command_timeout', 60),
        }

    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and create schema"""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(**self.db_config)

            # Setup schema and indexes
            async with self.pool.acquire() as conn:
                await self._create_schema(conn)
                await self._create_indexes(conn)

            logger.info(f"PostgreSQL vector store initialized: {self.table_name}")
            await self._update_stats()

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL vector store: {e}")
            raise VectorStoreConnectionError(f"Initialization failed: {e}")

    async def close(self) -> None:
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL vector store closed")

    async def health_check(self) -> bool:
        """Check PostgreSQL connection and pgvector extension"""
        if not self.pool:
            return False

        try:
            async with self.pool.acquire() as conn:
                # Test basic connectivity
                result = await conn.fetchval("SELECT 1")
                if result != 1:
                    return False

                # Test pgvector extension
                await conn.fetchval("SELECT '[1,2,3]'::vector")

                # Test table existence
                exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = $1)",
                    self.table_name
                )
                return bool(exists)

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def _create_schema(self, conn: asyncpg.Connection) -> None:
        """Create vector documents table and required extensions"""
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Create table with optimized schema
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id TEXT PRIMARY KEY,
            vector VECTOR({self.vector_dimensions}) NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{{}}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
        await conn.execute(create_table_sql)

        # Create updated_at trigger
        trigger_sql = f"""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        DROP TRIGGER IF EXISTS update_{self.table_name}_updated_at ON {self.table_name};
        CREATE TRIGGER update_{self.table_name}_updated_at
            BEFORE UPDATE ON {self.table_name}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        await conn.execute(trigger_sql)

        logger.info(f"Created schema for table: {self.table_name}")

    async def _create_indexes(self, conn: asyncpg.Connection) -> None:
        """Create vector similarity indexes"""
        # Vector similarity index
        if self.index_type.lower() == 'hnsw':
            # HNSW index for better query performance
            index_sql = f"""
            CREATE INDEX IF NOT EXISTS {self.table_name}_vector_hnsw_idx
            ON {self.table_name} USING hnsw (vector vector_cosine_ops)
            WITH (m = {self.index_params.get('m', 16)}, ef_construction = {self.index_params.get('ef_construction', 64)})
            """
        else:
            # IVFFlat index for balanced performance/memory
            lists = self.index_params.get('lists', 100)
            index_sql = f"""
            CREATE INDEX IF NOT EXISTS {self.table_name}_vector_ivf_idx
            ON {self.table_name} USING ivfflat (vector vector_cosine_ops)
            WITH (lists = {lists})
            """

        await conn.execute(index_sql)

        # Metadata GIN index for filtering
        metadata_index_sql = f"""
        CREATE INDEX IF NOT EXISTS {self.table_name}_metadata_idx
        ON {self.table_name} USING GIN (metadata)
        """
        await conn.execute(metadata_index_sql)

        # ID index (usually automatic, but ensure it exists)
        id_index_sql = f"""
        CREATE INDEX IF NOT EXISTS {self.table_name}_id_idx
        ON {self.table_name} (id)
        """
        await conn.execute(id_index_sql)

        logger.info(f"Created indexes for table: {self.table_name}")

    async def upsert_documents(self, documents: List[VectorDocument]) -> Dict[str, Any]:
        """Insert or update documents with vectors using efficient UPSERT"""
        if not documents:
            return {'inserted': 0, 'updated': 0, 'failed': 0, 'duration_ms': 0}

        start_time = time.perf_counter()

        # Validate vector dimensions
        vectors = [doc.vector for doc in documents]
        await self._validate_vector_dimensions(vectors)

        try:
            async with self.pool.acquire() as conn:
                # Use COPY for bulk inserts when possible
                if len(documents) > 100:
                    return await self._bulk_upsert(conn, documents, start_time)
                else:
                    return await self._batch_upsert_prepared(conn, documents, start_time)

        except Exception as e:
            logger.error(f"Upsert failed: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            return {
                'inserted': 0,
                'updated': 0,
                'failed': len(documents),
                'duration_ms': duration_ms,
                'error': str(e)
            }

    async def _batch_upsert_prepared(self, conn: asyncpg.Connection,
                                   documents: List[VectorDocument],
                                   start_time: float) -> Dict[str, Any]:
        """Efficient batch upsert using prepared statements"""
        upsert_sql = f"""
        INSERT INTO {self.table_name} (id, vector, content, metadata, created_at, updated_at)
        VALUES ($1, $2, $3, $4, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET
            vector = EXCLUDED.vector,
            content = EXCLUDED.content,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        """

        inserted = 0
        updated = 0
        failed = 0

        async with conn.transaction():
            for doc in documents:
                try:
                    # Check if document exists
                    exists = await conn.fetchval(
                        f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE id = $1)",
                        doc.id
                    )

                    # Execute upsert
                    await conn.execute(
                        upsert_sql,
                        doc.id,
                        doc.vector,
                        doc.content,
                        json.dumps(doc.metadata)
                    )

                    if exists:
                        updated += 1
                    else:
                        inserted += 1

                except Exception as e:
                    logger.error(f"Failed to upsert document {doc.id}: {e}")
                    failed += 1

        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            'inserted': inserted,
            'updated': updated,
            'failed': failed,
            'duration_ms': duration_ms
        }

    async def _bulk_upsert(self, conn: asyncpg.Connection,
                          documents: List[VectorDocument],
                          start_time: float) -> Dict[str, Any]:
        """High-performance bulk upsert using COPY protocol"""
        # For very large batches, use COPY to temporary table then UPSERT
        temp_table = f"temp_{self.table_name}_{int(time.time())}"

        try:
            async with conn.transaction():
                # Create temporary table
                await conn.execute(f"""
                CREATE TEMPORARY TABLE {temp_table} (
                    LIKE {self.table_name} INCLUDING DEFAULTS
                ) ON COMMIT DROP
                """)

                # Bulk insert to temp table using COPY
                copy_data = []
                for doc in documents:
                    copy_data.append((
                        doc.id,
                        doc.vector,
                        doc.content,
                        json.dumps(doc.metadata)
                    ))

                await conn.copy_records_to_table(
                    temp_table,
                    records=copy_data,
                    columns=['id', 'vector', 'content', 'metadata']
                )

                # Perform bulk upsert from temp table
                upsert_result = await conn.fetch(f"""
                INSERT INTO {self.table_name} (id, vector, content, metadata, created_at, updated_at)
                SELECT id, vector, content, metadata::jsonb, NOW(), NOW()
                FROM {temp_table}
                ON CONFLICT (id) DO UPDATE SET
                    vector = EXCLUDED.vector,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted
                """)

                # Count inserts vs updates
                inserted = sum(1 for row in upsert_result if row['inserted'])
                updated = len(upsert_result) - inserted

        except Exception as e:
            logger.error(f"Bulk upsert failed: {e}")
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        return {
            'inserted': inserted,
            'updated': updated,
            'failed': 0,
            'duration_ms': duration_ms
        }

    async def search_vectors(self, query: VectorSearchQuery) -> VectorSearchResponse:
        """Perform vector similarity search with T4/0.01% excellence"""
        start_time = time.perf_counter()

        try:
            async with self.pool.acquire() as conn:
                # Build search query with optional metadata filtering
                where_clause = ""
                params = [query.vector, query.top_k]
                param_idx = 3

                if query.metadata_filter:
                    filter_conditions = []
                    for key, value in query.metadata_filter.items():
                        if isinstance(value, (list, tuple)):
                            # IN clause for lists
                            placeholders = ','.join(f'${i}' for i in range(param_idx, param_idx + len(value)))
                            filter_conditions.append(f"metadata->>'{key}' IN ({placeholders})")
                            params.extend(value)
                            param_idx += len(value)
                        else:
                            # Equality for single values
                            filter_conditions.append(f"metadata->>'{key}' = ${param_idx}")
                            params.append(str(value))
                            param_idx += 1

                    if filter_conditions:
                        where_clause = "WHERE " + " AND ".join(filter_conditions)

                # Build base query
                select_fields = ["id", "content", "metadata", "created_at"]
                if query.include_vectors:
                    select_fields.append("vector")

                search_sql = f"""
                SELECT {', '.join(select_fields)},
                       1 - (vector <=> $1::vector) AS similarity_score
                FROM {self.table_name}
                {where_clause}
                ORDER BY vector <=> $1::vector
                LIMIT $2
                """

                # Apply score threshold if specified
                if query.score_threshold is not None:
                    threshold_clause = f"HAVING 1 - (vector <=> $1::vector) >= ${param_idx}"
                    search_sql = search_sql.replace("ORDER BY", f"{threshold_clause} ORDER BY")
                    params.append(query.score_threshold)

                # Execute search
                rows = await conn.fetch(search_sql, *params)

                # Build results
                results = []
                for rank, row in enumerate(rows):
                    doc = VectorDocument(
                        id=row['id'],
                        content=row['content'],
                        vector=list(row['vector']) if query.include_vectors else [],
                        metadata=row['metadata'] if query.include_metadata else {},
                        timestamp=row['created_at'].timestamp()
                    )

                    result = VectorSearchResult(
                        document=doc,
                        score=float(row['similarity_score']),
                        rank=rank + 1
                    )
                    results.append(result)

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}")

        duration_ms = (time.perf_counter() - start_time) * 1000
        self._record_query_time(duration_ms)

        # Count total documents for response metadata
        total_docs = await self.count_documents(query.metadata_filter)

        return VectorSearchResponse(
            results=results,
            query_time_ms=duration_ms,
            total_documents=total_docs,
            query_vector_dim=len(query.vector)
        )

    async def delete_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """Delete documents by IDs"""
        if not document_ids:
            return {'deleted': 0, 'not_found': 0, 'failed': 0, 'duration_ms': 0}

        start_time = time.perf_counter()

        try:
            async with self.pool.acquire() as conn:
                # Delete in batches for better performance
                batch_size = 1000
                total_deleted = 0

                for i in range(0, len(document_ids), batch_size):
                    batch = document_ids[i:i + batch_size]
                    placeholders = ','.join(f'${j+1}' for j in range(len(batch)))

                    delete_sql = f"DELETE FROM {self.table_name} WHERE id IN ({placeholders})"
                    result = await conn.execute(delete_sql, *batch)

                    # Extract number of deleted rows from result
                    deleted_count = int(result.split()[-1]) if result.startswith('DELETE') else 0
                    total_deleted += deleted_count

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            duration_ms = (time.perf_counter() - start_time) * 1000
            return {
                'deleted': 0,
                'not_found': 0,
                'failed': len(document_ids),
                'duration_ms': duration_ms,
                'error': str(e)
            }

        duration_ms = (time.perf_counter() - start_time) * 1000
        not_found = len(document_ids) - total_deleted

        return {
            'deleted': total_deleted,
            'not_found': not_found,
            'failed': 0,
            'duration_ms': duration_ms
        }

    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """Retrieve a single document by ID"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    f"SELECT id, vector, content, metadata, created_at FROM {self.table_name} WHERE id = $1",
                    document_id
                )

                if not row:
                    return None

                return VectorDocument(
                    id=row['id'],
                    vector=list(row['vector']),
                    content=row['content'],
                    metadata=row['metadata'],
                    timestamp=row['created_at'].timestamp()
                )

        except Exception as e:
            logger.error(f"Get document failed: {e}")
            raise VectorStoreError(f"Get document failed: {e}")

    async def count_documents(self, metadata_filter: Optional[Dict[str, Any]] = None) -> int:
        """Count documents with optional metadata filter"""
        try:
            async with self.pool.acquire() as conn:
                if not metadata_filter:
                    return await conn.fetchval(f"SELECT COUNT(*) FROM {self.table_name}")

                # Build filter conditions
                where_conditions = []
                params = []
                param_idx = 1

                for key, value in metadata_filter.items():
                    if isinstance(value, (list, tuple)):
                        placeholders = ','.join(f'${i}' for i in range(param_idx, param_idx + len(value)))
                        where_conditions.append(f"metadata->>'{key}' IN ({placeholders})")
                        params.extend(value)
                        param_idx += len(value)
                    else:
                        where_conditions.append(f"metadata->>'{key}' = ${param_idx}")
                        params.append(str(value))
                        param_idx += 1

                where_clause = " AND ".join(where_conditions)
                count_sql = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"

                return await conn.fetchval(count_sql, *params)

        except Exception as e:
            logger.error(f"Count documents failed: {e}")
            return 0

    async def create_index(self, index_params: Dict[str, Any]) -> None:
        """Create or rebuild vector index"""
        try:
            async with self.pool.acquire() as conn:
                # Drop existing index
                await conn.execute(f"DROP INDEX IF EXISTS {self.table_name}_vector_idx")

                # Create new index based on parameters
                index_type = index_params.get('type', self.index_type)
                if index_type.lower() == 'hnsw':
                    m = index_params.get('m', 16)
                    ef_construction = index_params.get('ef_construction', 64)
                    index_sql = f"""
                    CREATE INDEX {self.table_name}_vector_idx
                    ON {self.table_name} USING hnsw (vector vector_cosine_ops)
                    WITH (m = {m}, ef_construction = {ef_construction})
                    """
                else:
                    lists = index_params.get('lists', 100)
                    index_sql = f"""
                    CREATE INDEX {self.table_name}_vector_idx
                    ON {self.table_name} USING ivfflat (vector vector_cosine_ops)
                    WITH (lists = {lists})
                    """

                await conn.execute(index_sql)
                logger.info(f"Created {index_type} index for {self.table_name}")

        except Exception as e:
            logger.error(f"Create index failed: {e}")
            raise VectorStoreError(f"Create index failed: {e}")

    async def batch_upsert(self,
                          documents: List[VectorDocument],
                          batch_size: int = 100,
                          parallel_batches: int = 4) -> Dict[str, Any]:
        """Parallel batch upsert for high throughput"""
        if not documents:
            return {'inserted': 0, 'updated': 0, 'failed': 0, 'duration_ms': 0}

        start_time = time.perf_counter()

        # Split into batches
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]

        # Process batches in parallel
        semaphore = asyncio.Semaphore(parallel_batches)
        tasks = []

        async def process_batch(batch):
            async with semaphore:
                return await self.upsert_documents(batch)

        tasks = [process_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        total_inserted = 0
        total_updated = 0
        total_failed = 0

        for result in results:
            if isinstance(result, Exception):
                total_failed += len(batch)  # Assume all in batch failed
                logger.error(f"Batch failed: {result}")
            else:
                total_inserted += result.get('inserted', 0)
                total_updated += result.get('updated', 0)
                total_failed += result.get('failed', 0)

        duration_ms = (time.perf_counter() - start_time) * 1000

        return {
            'inserted': total_inserted,
            'updated': total_updated,
            'failed': total_failed,
            'duration_ms': duration_ms,
            'batches_processed': len(batches)
        }

    async def batch_search(self,
                          queries: List[VectorSearchQuery],
                          parallel_queries: int = 8) -> List[VectorSearchResponse]:
        """Execute multiple searches in parallel"""
        if not queries:
            return []

        semaphore = asyncio.Semaphore(parallel_queries)

        async def search_with_semaphore(query):
            async with semaphore:
                return await self.search_vectors(query)

        tasks = [search_with_semaphore(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Search {i} failed: {result}")
                # Return empty response for failed searches
                responses.append(VectorSearchResponse(
                    results=[],
                    query_time_ms=0,
                    total_documents=0,
                    query_vector_dim=len(queries[i].vector)
                ))
            else:
                responses.append(result)

        return responses

    async def _update_stats(self) -> None:
        """Update vector store statistics"""
        await super()._update_stats()

        try:
            async with self.pool.acquire() as conn:
                # Get document count
                self.stats.total_documents = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {self.table_name}"
                )

                # Get table size
                size_result = await conn.fetchrow(
                    """SELECT pg_total_relation_size($1) as size""",
                    self.table_name
                )
                self.stats.index_size_bytes = size_result['size'] if size_result else 0

                self.stats.vector_dimensions = self.vector_dimensions

        except Exception as e:
            logger.error(f"Failed to update stats: {e}")


# Register the PostgreSQL vector store
VectorStoreFactory.register(VectorStoreType.POSTGRESQL, PostgreSQLVectorStore)