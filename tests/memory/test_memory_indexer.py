"""
Test suite for LUKHAS memory indexer system.

Validates embedding generation, content extraction, deduplication,
and batch processing with T4/0.01% excellence standards.
"""

import asyncio

import numpy as np
import pytest

from lukhas.memory.indexer import (
    ContentExtractor,
    DocumentIndexer,
    OpenAIEmbeddingProvider,
    SentenceTransformersProvider,
)


class TestContentExtractor:
    """Test content extraction and analysis"""

    def setup_method(self):
        """Setup test environment"""
        self.extractor = ContentExtractor()

    def test_extract_basic_content(self):
        """Test basic content extraction"""
        content = "This is a test document with some words."

        result = self.extractor.extract_content(content)

        assert result["word_count"] == 9
        assert result["language"] == "en"
        assert result["content_type"] == "text"
        assert "features" in result
        assert result["features"]["char_count"] == len(content)

    def test_extract_empty_content(self):
        """Test extraction of empty content"""
        result = self.extractor.extract_content("")

        assert result["word_count"] == 0
        assert result["language"] is None
        assert result["entities"] == []

    def test_extract_entities(self):
        """Test entity extraction"""
        content = "Contact john.doe@example.com or visit https://example.com or call 555-123-4567"

        result = self.extractor.extract_content(content)

        entities = [entity[1] for entity in result["entities"]]
        assert "john.doe@example.com" in entities
        assert "https://example.com" in entities
        assert "555-123-4567" in entities

    def test_language_detection(self):
        """Test simple language detection"""
        english_text = "The quick brown fox jumps over the lazy dog"
        spanish_text = "El rápido zorro marrón salta sobre el perro perezoso"

        en_result = self.extractor.extract_content(english_text)
        es_result = self.extractor.extract_content(spanish_text)

        assert en_result["language"] == "en"
        assert es_result["language"] == "es"

    def test_content_features(self):
        """Test content feature extraction"""
        content = "Hello World! This is a TEST."

        result = self.extractor.extract_content(content)
        features = result["features"]

        assert features["sentence_count"] == 2
        assert features["uppercase_ratio"] > 0
        assert features["digit_ratio"] == 0
        assert features["whitespace_ratio"] > 0


class TestOpenAIEmbeddingProvider:
    """Test OpenAI embedding provider"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = OpenAIEmbeddingProvider(
            api_key="test-key",
            model="text-embedding-ada-002"
        )

    def test_provider_properties(self):
        """Test provider properties"""
        assert self.provider.dimension == 1536
        assert self.provider.model_name == "text-embedding-ada-002"

    @pytest.mark.asyncio
    async def test_embed_single_text(self):
        """Test single text embedding"""
        text = "This is a test document"

        embedding = await self.provider.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype == np.float32
        assert len(embedding) == 1536
        assert np.allclose(np.linalg.norm(embedding), 1.0, atol=1e-5)  # Should be normalized

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch embedding generation"""
        texts = ["First document", "Second document", "Third document"]

        embeddings = await self.provider.embed_batch(texts)

        assert len(embeddings) == 3
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.dtype == np.float32
            assert len(embedding) == 1536

    def test_deterministic_embeddings(self):
        """Test that embeddings are deterministic for same text"""
        # Note: The test implementation uses hash-based seeding for determinism
        text = "Same text for deterministic test"

        # Create two providers
        provider1 = OpenAIEmbeddingProvider(api_key="test", model="text-embedding-ada-002")
        provider2 = OpenAIEmbeddingProvider(api_key="test", model="text-embedding-ada-002")

        embedding1 = asyncio.run(provider1.embed_text(text))
        embedding2 = asyncio.run(provider2.embed_text(text))

        np.testing.assert_array_equal(embedding1, embedding2)

    def test_invalid_model(self):
        """Test initialization with invalid model"""
        with pytest.raises(ValueError, match="Unsupported OpenAI model"):
            OpenAIEmbeddingProvider(api_key="test", model="invalid-model")


class TestSentenceTransformersProvider:
    """Test SentenceTransformers provider"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = SentenceTransformersProvider(model_name="all-MiniLM-L6-v2")

    def test_provider_properties(self):
        """Test provider properties"""
        assert self.provider.dimension == 384
        assert self.provider.model_name == "all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_embed_text(self):
        """Test text embedding"""
        text = "Test document for sentence transformers"

        embedding = await self.provider.embed_text(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.dtype == np.float32
        assert len(embedding) == 384
        assert np.allclose(np.linalg.norm(embedding), 1.0, atol=1e-5)

    def test_invalid_model(self):
        """Test initialization with invalid model"""
        with pytest.raises(ValueError, match="Unsupported sentence-transformers model"):
            SentenceTransformersProvider(model_name="invalid-model")


class TestDocumentIndexer:
    """Test document indexer functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.provider = OpenAIEmbeddingProvider(api_key="test")
        self.extractor = ContentExtractor()
        self.indexer = DocumentIndexer(
            embedding_provider=self.provider,
            content_extractor=self.extractor,
            enable_deduplication=True
        )

    @pytest.mark.asyncio
    async def test_index_single_document(self):
        """Test indexing a single document"""
        result = await self.indexer.index_document(
            document_id="test-doc-1",
            content="This is a test document for indexing",
            metadata={"source": "test"},
            identity_id="test-identity",
            lane="candidate"
        )

        assert result.success is True
        assert result.error is None
        assert result.document is not None
        assert result.document.id == "test-doc-1"
        assert result.document.identity_id == "test-identity"
        assert result.document.lane == "candidate"
        assert result.word_count > 0
        assert result.processing_time_ms > 0
        assert "indexer" in result.document.metadata

    @pytest.mark.asyncio
    async def test_index_empty_content(self):
        """Test indexing empty content"""
        result = await self.indexer.index_document(
            document_id="empty-doc",
            content="",
            lane="candidate"
        )

        assert result.success is False
        assert "Empty or whitespace-only content" in result.error

    @pytest.mark.asyncio
    async def test_index_missing_id(self):
        """Test indexing without document ID"""
        result = await self.indexer.index_document(
            document_id="",
            content="Test content",
            lane="candidate"
        )

        assert result.success is False
        assert "Missing document ID" in result.error

    @pytest.mark.asyncio
    async def test_duplicate_detection(self):
        """Test content deduplication"""
        content = "This is duplicate content for testing"

        # Index first document
        result1 = await self.indexer.index_document(
            document_id="doc-1",
            content=content,
            lane="candidate"
        )
        assert result1.success is True

        # Index second document with same content
        result2 = await self.indexer.index_document(
            document_id="doc-2",
            content=content,
            lane="candidate"
        )
        assert result2.success is False
        assert result2.duplicate_of == "doc-1"
        assert "Duplicate content" in result2.error

    @pytest.mark.asyncio
    async def test_duplicate_detection_disabled(self):
        """Test indexing with deduplication disabled"""
        indexer = DocumentIndexer(
            embedding_provider=self.provider,
            enable_deduplication=False
        )

        content = "Duplicate content test"

        # Index same content twice
        result1 = await indexer.index_document("doc-1", content, lane="candidate")
        result2 = await indexer.index_document("doc-2", content, lane="candidate")

        assert result1.success is True
        assert result2.success is True
        assert result2.duplicate_of is None

    @pytest.mark.asyncio
    async def test_batch_indexing(self):
        """Test batch document indexing"""
        documents = [
            {
                "id": "batch-doc-1",
                "content": "First document in batch",
                "metadata": {"batch": True},
                "lane": "candidate"
            },
            {
                "id": "batch-doc-2",
                "content": "Second document in batch",
                "metadata": {"batch": True},
                "lane": "candidate"
            },
            {
                "id": "batch-doc-3",
                "content": "Third document in batch",
                "metadata": {"batch": True},
                "lane": "candidate"
            }
        ]

        results = await self.indexer.index_batch(documents)

        assert len(results) == 3
        for result in results:
            assert result.success is True
            assert result.document is not None
            assert result.document.metadata["batch"] is True

    @pytest.mark.asyncio
    async def test_batch_with_errors(self):
        """Test batch indexing with some errors"""
        documents = [
            {"id": "good-doc", "content": "Valid document", "lane": "candidate"},
            {"id": "", "content": "Missing ID", "lane": "candidate"},  # Error: missing ID
            {"id": "empty-content", "content": "", "lane": "candidate"},  # Error: empty content
        ]

        results = await self.indexer.index_batch(documents)

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is False

    @pytest.mark.asyncio
    async def test_content_analysis(self):
        """Test content analysis features"""
        content = "This is a comprehensive test document. Contact support@lukhas.ai for help!"

        result = await self.indexer.index_document(
            document_id="analysis-test",
            content=content,
            lane="candidate"
        )

        assert result.success is True
        assert result.word_count > 0
        assert result.language == "en"
        assert len(result.extracted_entities) > 0
        assert "support@lukhas.ai" in result.extracted_entities

    @pytest.mark.asyncio
    async def test_metadata_enrichment(self):
        """Test metadata enrichment during indexing"""
        result = await self.indexer.index_document(
            document_id="metadata-test",
            content="Test content for metadata enrichment",
            metadata={"original": "data"},
            identity_id="test-identity",
            fold_id="test-fold",
            tags=["test", "metadata"],
            lane="candidate"
        )

        assert result.success is True
        doc = result.document

        # Check original metadata preserved
        assert doc.metadata["original"] == "data"

        # Check indexer metadata added
        indexer_meta = doc.metadata["indexer"]
        assert indexer_meta["model"] == self.provider.model_name
        assert indexer_meta["dimension"] == self.provider.dimension
        assert "content_hash" in indexer_meta
        assert indexer_meta["word_count"] == result.word_count
        assert "indexed_at" in indexer_meta

    def test_content_hash_calculation(self):
        """Test content hash calculation for deduplication"""
        content1 = "This is test content"
        content2 = "This is test content"  # Same content
        content3 = "This is different content"

        hash1 = self.indexer._calculate_content_hash(content1)
        hash2 = self.indexer._calculate_content_hash(content2)
        hash3 = self.indexer._calculate_content_hash(content3)

        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA-256 hex length

    def test_statistics_tracking(self):
        """Test performance statistics tracking"""
        stats_before = self.indexer.get_statistics()

        # Run some indexing operations
        asyncio.run(self.indexer.index_document("stat-test-1", "Content 1", lane="candidate"))
        asyncio.run(self.indexer.index_document("stat-test-2", "Content 2", lane="candidate"))
        asyncio.run(self.indexer.index_document("stat-test-3", "Content 1", lane="candidate"))  # Duplicate

        stats_after = self.indexer.get_statistics()

        assert stats_after["documents_indexed"] > stats_before["documents_indexed"]
        assert stats_after["duplicates_detected"] > stats_before["duplicates_detected"]
        assert stats_after["avg_processing_time_ms"] > 0
        assert stats_after["duplicate_rate"] > 0
        assert stats_after["embedding_provider"] == self.provider.model_name

    def test_deduplication_cache_management(self):
        """Test deduplication cache management"""
        # Add some content to cache
        asyncio.run(self.indexer.index_document("cache-test", "Cache test content", lane="candidate"))

        assert len(self.indexer.content_hashes) == 1

        # Clear cache
        self.indexer.clear_deduplication_cache()

        assert len(self.indexer.content_hashes) == 0

    @pytest.mark.asyncio
    async def test_performance_targets(self):
        """Test performance targets compliance"""
        content = "Performance test document with moderate length content"

        start_time = asyncio.get_event_loop().time()
        result = await self.indexer.index_document(
            document_id="perf-test",
            content=content,
            lane="candidate"
        )
        end_time = asyncio.get_event_loop().time()

        duration_ms = (end_time - start_time) * 1000

        assert result.success is True
        # Target: <100ms p95 for document indexing
        # Note: This is a mock implementation, real performance may vary
        assert duration_ms < 1000  # Relaxed for test environment


@pytest.mark.asyncio
async def test_integration_indexer_with_backends():
    """Integration test with different embedding providers"""

    # Test with OpenAI provider
    openai_provider = OpenAIEmbeddingProvider(api_key="test")
    openai_indexer = DocumentIndexer(openai_provider)

    result = await openai_indexer.index_document(
        document_id="integration-openai",
        content="Integration test with OpenAI provider",
        lane="candidate"
    )

    assert result.success is True
    assert result.document.embedding.shape == (1536,)

    # Test with SentenceTransformers provider
    st_provider = SentenceTransformersProvider()
    st_indexer = DocumentIndexer(st_provider)

    result = await st_indexer.index_document(
        document_id="integration-st",
        content="Integration test with SentenceTransformers provider",
        lane="candidate"
    )

    assert result.success is True
    assert result.document.embedding.shape == (384,)


@pytest.mark.asyncio
async def test_concurrent_indexing():
    """Test concurrent indexing operations"""
    provider = OpenAIEmbeddingProvider(api_key="test")
    indexer = DocumentIndexer(provider)

    # Create concurrent indexing tasks
    tasks = []
    for i in range(10):
        task = indexer.index_document(
            document_id=f"concurrent-{i}",
            content=f"Concurrent test document {i}",
            lane="candidate"
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    assert len(results) == 10
    for result in results:
        assert result.success is True

    # Check statistics
    stats = indexer.get_statistics()
    assert stats["documents_indexed"] == 10


def test_indexer_configuration():
    """Test indexer configuration options"""
    provider = OpenAIEmbeddingProvider(api_key="test")

    # Test with custom configuration
    indexer = DocumentIndexer(
        embedding_provider=provider,
        enable_deduplication=False,
        dedup_threshold=0.8
    )

    assert indexer.enable_deduplication is False
    assert indexer.dedup_threshold == 0.8
    assert indexer.embedding_provider == provider


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
