"""
Test suite for LUKHAS memory backend implementations.

Validates vector storage backends (PgVector, FAISS, InMemory) with
T4/0.01% excellence standards and performance contracts.
"""

import pytest
import asyncio
import tempfile
import shutil
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
import numpy as np

from lukhas.memory.backends.base import (
    VectorDocument,
    SearchResult,
    StorageStats,
    DocumentNotFoundError,
    DimensionMismatchError
)
from lukhas.memory.backends.memory_store import InMemoryVectorStore
from lukhas.memory.backends.faiss_store import FAISSVectorStore
from lukhas.memory.backends.pgvector_store import PgVectorStore


class TestVectorDocument:
    """Test VectorDocument data structure"""

    def test_document_creation(self):
        """Test basic document creation"""
        embedding = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)

        doc = VectorDocument(
            id="test-doc",
            content="Test content",
            embedding=embedding,
            metadata={"test": True},
            identity_id="user-123",
            lane="candidate"
        )

        assert doc.id == "test-doc"
        assert doc.content == "Test content"
        assert doc.dimension == 4
        assert doc.lane == "candidate"
        assert doc.identity_id == "user-123"

    def test_document_normalization(self):
        """Test embedding normalization during creation"""
        # Create unnormalized embedding
        embedding = np.array([3.0, 4.0], dtype=np.float32)  # Magnitude = 5.0

        doc = VectorDocument(
            id="norm-test",
            content="Normalization test",
            embedding=embedding
        )

        # Should be normalized to unit length
        assert np.allclose(np.linalg.norm(doc.embedding), 1.0, atol=1e-6)
        assert np.allclose(doc.embedding, [0.6, 0.8], atol=1e-6)

    def test_document_expiration(self):
        """Test document expiration logic"""
        now = datetime.now(timezone.utc)

        # Non-expiring document
        doc1 = VectorDocument(
            id="no-expire",
            content="Never expires",
            embedding=np.array([1.0], dtype=np.float32)
        )
        assert doc1.is_expired is False

        # Future expiration
        doc2 = VectorDocument(
            id="future-expire",
            content="Expires in future",
            embedding=np.array([1.0], dtype=np.float32),
            expires_at=now + timedelta(hours=1)
        )
        assert doc2.is_expired is False

        # Past expiration
        doc3 = VectorDocument(
            id="past-expire",
            content="Already expired",
            embedding=np.array([1.0], dtype=np.float32),
            expires_at=now - timedelta(hours=1)
        )
        assert doc3.is_expired is True

    def test_document_access_tracking(self):
        """Test access tracking functionality"""
        doc = VectorDocument(
            id="access-test",
            content="Access tracking test",
            embedding=np.array([1.0], dtype=np.float32)
        )

        initial_count = doc.access_count
        initial_accessed = doc.last_accessed

        doc.touch()

        assert doc.access_count == initial_count + 1
        assert doc.last_accessed != initial_accessed
        assert doc.last_accessed is not None

    def test_document_serialization(self):
        """Test document serialization and deserialization"""
        now = datetime.now(timezone.utc)
        doc = VectorDocument(
            id="serial-test",
            content="Serialization test",
            embedding=np.array([0.5, 0.5], dtype=np.float32),
            metadata={"serialized": True},
            identity_id="user-456",
            lane="production",
            fold_id="fold-789",
            tags=["test", "serialization"],
            expires_at=now + timedelta(days=1)
        )

        # Convert to dict
        doc_dict = doc.to_dict()
        assert doc_dict["id"] == "serial-test"
        assert doc_dict["metadata"]["serialized"] is True
        assert len(doc_dict["embedding"]) == 2

        # Recreate from dict
        reconstructed = VectorDocument.from_dict(doc_dict)
        assert reconstructed.id == doc.id
        assert reconstructed.content == doc.content
        assert np.array_equal(reconstructed.embedding, doc.embedding)
        assert reconstructed.metadata == doc.metadata
        assert reconstructed.identity_id == doc.identity_id

    def test_document_validation(self):
        """Test document validation and type conversion"""
        # Test with list embedding (should convert to numpy array)
        doc = VectorDocument(
            id="validation-test",
            content="Type validation",
            embedding=[0.1, 0.2, 0.3]  # List instead of numpy array
        )

        assert isinstance(doc.embedding, np.ndarray)
        assert doc.embedding.dtype == np.float32

        # Test with wrong dtype (should convert)
        doc2 = VectorDocument(
            id="dtype-test",
            content="Dtype conversion",
            embedding=np.array([0.1, 0.2], dtype=np.float64)  # float64 -> float32
        )

        assert doc2.embedding.dtype == np.float32


class TestInMemoryVectorStore:
    """Test in-memory vector store implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.store = InMemoryVectorStore(dimension=384)

    @pytest.mark.asyncio
    async def test_store_initialization(self):
        """Test store initialization"""
        await self.store.initialize()
        assert self.store.dimension == 384
        assert len(self.store.documents) == 0

        await self.store.shutdown()

    @pytest.mark.asyncio
    async def test_add_document(self):
        """Test adding single document"""
        await self.store.initialize()

        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="add-test",
            content="Add test document",
            embedding=embedding
        )

        success = await self.store.add(doc)
        assert success is True
        assert "add-test" in self.store.documents

    @pytest.mark.asyncio
    async def test_add_dimension_mismatch(self):
        """Test adding document with wrong dimension"""
        await self.store.initialize()

        # Wrong dimension (384 expected, 256 provided)
        embedding = np.random.random(256).astype(np.float32)
        doc = VectorDocument(
            id="dim-mismatch",
            content="Dimension mismatch test",
            embedding=embedding
        )

        with pytest.raises(DimensionMismatchError):
            await self.store.add(doc)

    @pytest.mark.asyncio
    async def test_bulk_add(self):
        """Test bulk document addition"""
        await self.store.initialize()

        documents = []
        for i in range(5):
            embedding = np.random.random(384).astype(np.float32)
            doc = VectorDocument(
                id=f"bulk-{i}",
                content=f"Bulk test document {i}",
                embedding=embedding
            )
            documents.append(doc)

        results = await self.store.bulk_add(documents)
        assert len(results) == 5
        assert all(results)
        assert len(self.store.documents) == 5

    @pytest.mark.asyncio
    async def test_get_document(self):
        """Test document retrieval"""
        await self.store.initialize()

        # Add document
        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="get-test",
            content="Get test document",
            embedding=embedding,
            metadata={"test": "get"}
        )
        await self.store.add(doc)

        # Retrieve document
        retrieved = await self.store.get("get-test")
        assert retrieved.id == "get-test"
        assert retrieved.content == "Get test document"
        assert retrieved.metadata["test"] == "get"

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self):
        """Test retrieving non-existent document"""
        await self.store.initialize()

        with pytest.raises(DocumentNotFoundError):
            await self.store.get("nonexistent")

    @pytest.mark.asyncio
    async def test_update_document(self):
        """Test document update"""
        await self.store.initialize()

        # Add original document
        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="update-test",
            content="Original content",
            embedding=embedding
        )
        await self.store.add(doc)

        # Update document
        updated_doc = VectorDocument(
            id="update-test",
            content="Updated content",
            embedding=embedding,
            metadata={"updated": True}
        )

        success = await self.store.update(updated_doc)
        assert success is True

        # Verify update
        retrieved = await self.store.get("update-test")
        assert retrieved.content == "Updated content"
        assert retrieved.metadata.get("updated") is True

    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test document deletion"""
        await self.store.initialize()

        # Add document
        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="delete-test",
            content="Delete test document",
            embedding=embedding
        )
        await self.store.add(doc)

        # Delete document
        success = await self.store.delete("delete-test")
        assert success is True

        # Verify deletion
        with pytest.raises(DocumentNotFoundError):
            await self.store.get("delete-test")

    @pytest.mark.asyncio
    async def test_vector_search(self):
        """Test vector similarity search"""
        await self.store.initialize()

        # Add test documents
        documents = []
        for i in range(10):
            # Create embeddings with some pattern
            embedding = np.random.random(384).astype(np.float32)
            # Make first document similar to query
            if i == 0:
                embedding[0] = 1.0
                embedding[1:] = 0.1

            doc = VectorDocument(
                id=f"search-{i}",
                content=f"Search test document {i}",
                embedding=embedding,
                metadata={"index": i}
            )
            documents.append(doc)

        await self.store.bulk_add(documents)

        # Create query similar to first document
        query = np.zeros(384, dtype=np.float32)
        query[0] = 1.0
        query[1:] = 0.1
        query = query / np.linalg.norm(query)

        # Perform search
        results = await self.store.search(query, k=5)

        assert len(results) <= 5
        assert all(isinstance(r, SearchResult) for r in results)
        # First result should be most similar (document 0)
        assert results[0].document.id == "search-0"
        assert results[0].score >= results[1].score  # Scores descending

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with metadata filters"""
        await self.store.initialize()

        # Add documents with different metadata
        for i in range(5):
            embedding = np.random.random(384).astype(np.float32)
            doc = VectorDocument(
                id=f"filter-{i}",
                content=f"Filter test {i}",
                embedding=embedding,
                lane="candidate" if i < 3 else "production",
                tags=["even" if i % 2 == 0 else "odd"]
            )
            await self.store.add(doc)

        query = np.random.random(384).astype(np.float32)

        # Search with lane filter
        results = await self.store.search(
            query,
            k=10,
            filters={"lane": "candidate"}
        )

        assert len(results) == 3
        assert all(r.document.lane == "candidate" for r in results)

        # Search with tag filter
        results = await self.store.search(
            query,
            k=10,
            filters={"tags": ["even"]}
        )

        # Should return documents with even indices
        even_indices = [int(r.document.id.split("-")[1]) for r in results]
        assert all(i % 2 == 0 for i in even_indices)

    @pytest.mark.asyncio
    async def test_search_by_text(self):
        """Test text-based search (requires embedding generation)"""
        await self.store.initialize()

        # Mock embedding generation for text search
        with patch.object(self.store, '_generate_embedding') as mock_embed:
            mock_embed.return_value = np.random.random(384).astype(np.float32)

            # Add a document first
            embedding = np.random.random(384).astype(np.float32)
            doc = VectorDocument(
                id="text-search",
                content="Text search test",
                embedding=embedding
            )
            await self.store.add(doc)

            # Perform text search
            results = await self.store.search_by_text("search query", k=5)

            assert len(results) <= 5
            mock_embed.assert_called_once_with("search query")

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """Test expired document cleanup"""
        await self.store.initialize()

        now = datetime.now(timezone.utc)

        # Add expired and non-expired documents
        expired_doc = VectorDocument(
            id="expired",
            content="Expired document",
            embedding=np.random.random(384).astype(np.float32),
            expires_at=now - timedelta(hours=1)
        )

        valid_doc = VectorDocument(
            id="valid",
            content="Valid document",
            embedding=np.random.random(384).astype(np.float32),
            expires_at=now + timedelta(hours=1)
        )

        await self.store.add(expired_doc)
        await self.store.add(valid_doc)

        # Cleanup expired
        removed_count = await self.store.cleanup_expired()

        assert removed_count == 1
        # Valid document should remain
        await self.store.get("valid")
        # Expired document should be gone
        with pytest.raises(DocumentNotFoundError):
            await self.store.get("expired")

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test storage statistics"""
        await self.store.initialize()

        # Add some documents
        for i in range(3):
            doc = VectorDocument(
                id=f"stats-{i}",
                content=f"Stats document {i}",
                embedding=np.random.random(384).astype(np.float32),
                lane="candidate" if i < 2 else "production"
            )
            await self.store.add(doc)

        stats = await self.store.get_stats()

        assert isinstance(stats, StorageStats)
        assert stats.total_documents == 3
        assert stats.active_documents == 3
        assert stats.documents_by_lane["candidate"] == 2
        assert stats.documents_by_lane["production"] == 1

    @pytest.mark.asyncio
    async def test_performance_targets(self):
        """Test performance targets compliance"""
        await self.store.initialize()

        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="perf-test",
            content="Performance test",
            embedding=embedding
        )

        # Test add performance (<100ms p95)
        start_time = asyncio.get_event_loop().time()
        await self.store.add(doc)
        add_time = (asyncio.get_event_loop().time() - start_time) * 1000
        assert add_time < 100  # ms

        # Test get performance (<10ms p95)
        start_time = asyncio.get_event_loop().time()
        await self.store.get("perf-test")
        get_time = (asyncio.get_event_loop().time() - start_time) * 1000
        assert get_time < 10  # ms

        # Test search performance (<50ms p95)
        query = np.random.random(384).astype(np.float32)
        start_time = asyncio.get_event_loop().time()
        await self.store.search(query, k=10)
        search_time = (asyncio.get_event_loop().time() - start_time) * 1000
        assert search_time < 50  # ms

    @pytest.mark.asyncio
    async def test_list_by_identity(self):
        """Test listing documents by identity"""
        await self.store.initialize()

        # Add documents for different identities
        for i in range(3):
            doc = VectorDocument(
                id=f"identity-{i}",
                content=f"Identity test {i}",
                embedding=np.random.random(384).astype(np.float32),
                identity_id="user-123" if i < 2 else "user-456"
            )
            await self.store.add(doc)

        # List by identity
        user_123_docs = await self.store.list_by_identity("user-123", limit=10)
        user_456_docs = await self.store.list_by_identity("user-456", limit=10)

        assert len(user_123_docs) == 2
        assert len(user_456_docs) == 1
        assert all(doc.identity_id == "user-123" for doc in user_123_docs)


class TestFAISSVectorStore:
    """Test FAISS vector store implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = FAISSVectorStore(
            dimension=384,
            index_type="flat",
            storage_path=self.temp_dir
        )

    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_faiss_initialization(self):
        """Test FAISS store initialization"""
        await self.store.initialize()
        assert self.store.index is not None
        assert self.store.dimension == 384
        await self.store.shutdown()

    @pytest.mark.asyncio
    async def test_faiss_add_and_search(self):
        """Test FAISS add and search operations"""
        await self.store.initialize()

        # Add documents
        documents = []
        for i in range(10):
            embedding = np.random.random(384).astype(np.float32)
            doc = VectorDocument(
                id=f"faiss-{i}",
                content=f"FAISS test document {i}",
                embedding=embedding,
                metadata={"index": i}
            )
            documents.append(doc)

        results = await self.store.bulk_add(documents)
        assert all(results)

        # Perform search
        query = np.random.random(384).astype(np.float32)
        search_results = await self.store.search(query, k=5)

        assert len(search_results) <= 5
        assert all(isinstance(r, SearchResult) for r in search_results)

    @pytest.mark.asyncio
    async def test_faiss_persistence(self):
        """Test FAISS index persistence"""
        await self.store.initialize()

        # Add document
        embedding = np.random.random(384).astype(np.float32)
        doc = VectorDocument(
            id="persistence-test",
            content="Persistence test",
            embedding=embedding
        )
        await self.store.add(doc)

        # Save index
        await self.store.save_index()
        await self.store.shutdown()

        # Create new store and load index
        new_store = FAISSVectorStore(
            dimension=384,
            index_type="flat",
            storage_path=self.temp_dir
        )
        await new_store.initialize()
        await new_store.load_index()

        # Document should be retrievable
        retrieved = await new_store.get("persistence-test")
        assert retrieved.id == "persistence-test"

        await new_store.shutdown()


@pytest.mark.skipif(
    not os.getenv("POSTGRES_TEST_URL"),
    reason="PostgreSQL test database not configured"
)
class TestPgVectorStore:
    """Test PostgreSQL vector store implementation"""

    def setup_method(self):
        """Setup test environment"""
        self.db_url = os.getenv("POSTGRES_TEST_URL")
        self.store = PgVectorStore(
            connection_string=self.db_url,
            dimension=384,
            table_name="test_vectors"
        )

    @pytest.mark.asyncio
    async def test_pgvector_initialization(self):
        """Test PgVector store initialization"""
        await self.store.initialize()
        assert self.store.connection_pool is not None
        await self.store.shutdown()

    @pytest.mark.asyncio
    async def test_pgvector_crud_operations(self):
        """Test PgVector CRUD operations"""
        await self.store.initialize()

        try:
            # Add document
            embedding = np.random.random(384).astype(np.float32)
            doc = VectorDocument(
                id="pg-test",
                content="PostgreSQL test",
                embedding=embedding,
                metadata={"db": "postgresql"}
            )

            success = await self.store.add(doc)
            assert success is True

            # Retrieve document
            retrieved = await self.store.get("pg-test")
            assert retrieved.id == "pg-test"
            assert retrieved.metadata["db"] == "postgresql"

            # Update document
            doc.content = "Updated PostgreSQL test"
            success = await self.store.update(doc)
            assert success is True

            # Verify update
            retrieved = await self.store.get("pg-test")
            assert retrieved.content == "Updated PostgreSQL test"

            # Delete document
            success = await self.store.delete("pg-test")
            assert success is True

            # Verify deletion
            with pytest.raises(DocumentNotFoundError):
                await self.store.get("pg-test")

        finally:
            await self.store.shutdown()

    @pytest.mark.asyncio
    async def test_pgvector_search_performance(self):
        """Test PgVector search performance with indexes"""
        await self.store.initialize()

        try:
            # Add multiple documents for performance testing
            documents = []
            for i in range(100):
                embedding = np.random.random(384).astype(np.float32)
                doc = VectorDocument(
                    id=f"perf-{i}",
                    content=f"Performance test {i}",
                    embedding=embedding
                )
                documents.append(doc)

            await self.store.bulk_add(documents)

            # Test search performance
            query = np.random.random(384).astype(np.float32)
            start_time = asyncio.get_event_loop().time()
            results = await self.store.search(query, k=10)
            search_time = (asyncio.get_event_loop().time() - start_time) * 1000

            assert len(results) == 10
            # Performance target: <50ms p95
            assert search_time < 200  # Relaxed for test environment

        finally:
            await self.store.shutdown()


class TestVectorStoreComparison:
    """Comparative tests across vector store implementations"""

    @pytest.mark.asyncio
    async def test_consistency_across_stores(self):
        """Test that all stores behave consistently"""
        stores = [
            InMemoryVectorStore(dimension=128),
            FAISSVectorStore(dimension=128, index_type="flat")
        ]

        for store in stores:
            await store.initialize()

            try:
                # Test same operations on each store
                embedding = np.random.random(128).astype(np.float32)
                doc = VectorDocument(
                    id="consistency-test",
                    content="Consistency test",
                    embedding=embedding,
                    metadata={"store": store.__class__.__name__}
                )

                # Add document
                success = await store.add(doc)
                assert success is True

                # Retrieve document
                retrieved = await store.get("consistency-test")
                assert retrieved.id == "consistency-test"
                assert retrieved.content == "Consistency test"

                # Search for document
                results = await store.search(embedding, k=1)
                assert len(results) == 1
                assert results[0].document.id == "consistency-test"

            finally:
                await store.shutdown()

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test consistent error handling across stores"""
        stores = [
            InMemoryVectorStore(dimension=256),
            FAISSVectorStore(dimension=256, index_type="flat")
        ]

        for store in stores:
            await store.initialize()

            try:
                # Test dimension mismatch error
                wrong_embedding = np.random.random(128).astype(np.float32)
                doc = VectorDocument(
                    id="error-test",
                    content="Error test",
                    embedding=wrong_embedding
                )

                with pytest.raises(DimensionMismatchError):
                    await store.add(doc)

                # Test document not found error
                with pytest.raises(DocumentNotFoundError):
                    await store.get("nonexistent")

            finally:
                await store.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])