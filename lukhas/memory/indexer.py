"""
T4/0.01% Excellence Memory Indexer

High-performance content indexing with embedding generation, SHA-256 deduplication,
and comprehensive metadata extraction for LUKHAS memory system.

Performance targets:
- Embedding generation: <500ms p95
- Document indexing: <100ms p95
- Duplicate detection: <50ms p95
- Content extraction: 99.9% accuracy
"""

import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import re

import numpy as np

from lukhas.memory.backends.base import VectorDocument
from lukhas.observability.metrics import get_metrics_collector
from lukhas.core.logging import get_logger


logger = get_logger(__name__)
metrics = get_metrics_collector()


@dataclass
class IndexingResult:
    """
    Result of document indexing operation.
    """
    document: Optional[VectorDocument] = None
    success: bool = False
    error: Optional[str] = None
    duplicate_of: Optional[str] = None
    processing_time_ms: float = 0.0
    metadata_extracted: Dict[str, Any] = field(default_factory=dict)

    # Content analysis results
    word_count: int = 0
    language: Optional[str] = None
    content_type: str = "text"
    extracted_entities: List[str] = field(default_factory=list)


class AbstractEmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    @abstractmethod
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier"""
        pass


class OpenAIEmbeddingProvider(AbstractEmbeddingProvider):
    """
    OpenAI embedding provider using text-embedding-ada-002 or text-embedding-3-large.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-ada-002",
        max_batch_size: int = 100,
        max_tokens_per_request: int = 8000
    ):
        self.api_key = api_key
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_tokens_per_request = max_tokens_per_request

        # Model dimensions
        self.model_dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }

        if model not in self.model_dimensions:
            raise ValueError(f"Unsupported OpenAI model: {model}")

    @property
    def dimension(self) -> int:
        return self.model_dimensions[self.model]

    @property
    def model_name(self) -> str:
        return self.model

    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        # This would integrate with OpenAI API
        # For now, return random embeddings for testing
        embeddings = []
        for text in texts:
            # Generate deterministic "embedding" based on text hash for testing
            text_hash = hashlib.md5(text.encode()).hexdigest()
            np.random.seed(int(text_hash[:8], 16))
            embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)

        return embeddings


class SentenceTransformersProvider(AbstractEmbeddingProvider):
    """
    Local sentence-transformers provider for development.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name_str = model_name
        self.model_dimensions = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "all-MiniLM-L12-v2": 384
        }

        if model_name not in self.model_dimensions:
            raise ValueError(f"Unsupported sentence-transformers model: {model_name}")

        # Initialize model (would require sentence-transformers library)
        self.model = None

    @property
    def dimension(self) -> int:
        return self.model_dimensions[self.model_name_str]

    @property
    def model_name(self) -> str:
        return self.model_name_str

    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        # Generate deterministic embedding for testing
        text_hash = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(text_hash[:8], 16))
        embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
        return embedding / np.linalg.norm(embedding)

    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings


class ContentExtractor:
    """
    Extract and analyze content from various sources.
    """

    def __init__(self):
        self.text_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'url': re.compile(r'https?://[^\s]+'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'date': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
        }

    def extract_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """
        Extract and analyze content features.

        Args:
            content: Raw content string
            content_type: Content type (text, markdown, html, etc.)

        Returns:
            Dictionary of extracted features
        """
        if not content or not content.strip():
            return {
                "word_count": 0,
                "language": None,
                "content_type": content_type,
                "entities": [],
                "features": {}
            }

        # Basic text statistics
        words = content.split()
        word_count = len(words)
        char_count = len(content)
        line_count = content.count('\n') + 1

        # Extract entities
        entities = []
        for entity_type, pattern in self.text_patterns.items():
            matches = pattern.findall(content)
            if matches:
                entities.extend([(entity_type, match) for match in matches])

        # Simple language detection (very basic)
        language = self._detect_language_simple(content)

        # Content features
        features = {
            "char_count": char_count,
            "line_count": line_count,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "sentence_count": content.count('.') + content.count('!') + content.count('?'),
            "uppercase_ratio": sum(1 for c in content if c.isupper()) / len(content) if content else 0,
            "digit_ratio": sum(1 for c in content if c.isdigit()) / len(content) if content else 0,
            "whitespace_ratio": sum(1 for c in content if c.isspace()) / len(content) if content else 0
        }

        return {
            "word_count": word_count,
            "language": language,
            "content_type": content_type,
            "entities": entities,
            "features": features
        }

    def _detect_language_simple(self, content: str) -> str:
        """
        Simple language detection based on common words.
        For production, use a proper language detection library.
        """
        content_lower = content.lower()

        # English indicators
        english_words = ['the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that']
        english_score = sum(1 for word in english_words if word in content_lower)

        # Spanish indicators
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'es', 'se', 'no', 'te']
        spanish_score = sum(1 for word in spanish_words if word in content_lower)

        # French indicators
        french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
        french_score = sum(1 for word in french_words if word in content_lower)

        scores = [
            ('en', english_score),
            ('es', spanish_score),
            ('fr', french_score)
        ]

        # Return language with highest score, or None if all scores are low
        max_lang, max_score = max(scores, key=lambda x: x[1])
        return max_lang if max_score > 2 else None


class DocumentIndexer:
    """
    High-level document indexer with embedding generation and deduplication.
    """

    def __init__(
        self,
        embedding_provider: AbstractEmbeddingProvider,
        content_extractor: Optional[ContentExtractor] = None,
        enable_deduplication: bool = True,
        dedup_threshold: float = 0.95
    ):
        self.embedding_provider = embedding_provider
        self.content_extractor = content_extractor or ContentExtractor()
        self.enable_deduplication = enable_deduplication
        self.dedup_threshold = dedup_threshold

        # Deduplication cache: content_hash -> document_id
        self.content_hashes: Dict[str, str] = {}

        # Performance tracking
        self.stats = {
            "documents_indexed": 0,
            "duplicates_detected": 0,
            "embedding_errors": 0,
            "total_processing_time_ms": 0.0
        }

    def _calculate_content_hash(self, content: str) -> str:
        """
        Calculate SHA-256 hash of normalized content for deduplication.

        Args:
            content: Document content

        Returns:
            SHA-256 hash as hexadecimal string
        """
        # Normalize content for hashing
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    async def index_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        identity_id: Optional[str] = None,
        lane: str = "candidate",
        fold_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None
    ) -> IndexingResult:
        """
        Index a single document with embedding generation and analysis.

        Args:
            document_id: Unique document identifier
            content: Document content to index
            metadata: Optional metadata dictionary
            identity_id: Associated identity ID
            lane: Processing lane (candidate, integration, production)
            fold_id: Associated fold ID
            tags: Document tags
            expires_at: Optional expiration timestamp

        Returns:
            IndexingResult with document and processing information
        """
        start_time = time.perf_counter()

        try:
            # Initialize result
            result = IndexingResult()

            # Validate inputs
            if not content or not content.strip():
                result.error = "Empty or whitespace-only content"
                return result

            if not document_id:
                result.error = "Missing document ID"
                return result

            # Check for duplicates if enabled
            content_hash = self._calculate_content_hash(content)
            if self.enable_deduplication and content_hash in self.content_hashes:
                result.duplicate_of = self.content_hashes[content_hash]
                result.error = f"Duplicate content (hash: {content_hash[:16]}...)"
                self.stats["duplicates_detected"] += 1
                metrics.increment_counter("indexer_duplicates_detected")
                return result

            # Extract content features
            content_analysis = self.content_extractor.extract_content(content)
            result.word_count = content_analysis["word_count"]
            result.language = content_analysis["language"]
            result.content_type = content_analysis["content_type"]
            result.extracted_entities = [entity[1] for entity in content_analysis["entities"]]
            result.metadata_extracted = content_analysis["features"]

            # Generate embedding
            try:
                embedding = await self.embedding_provider.embed_text(content)
            except Exception as e:
                result.error = f"Embedding generation failed: {e}"
                self.stats["embedding_errors"] += 1
                metrics.increment_counter("indexer_embedding_errors")
                return result

            # Create vector document
            now = datetime.now(timezone.utc)
            document = VectorDocument(
                id=document_id,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
                identity_id=identity_id,
                lane=lane,
                fold_id=fold_id,
                tags=tags or [],
                created_at=now,
                updated_at=now,
                expires_at=expires_at
            )

            # Add extracted metadata
            document.metadata.update({
                "indexer": {
                    "model": self.embedding_provider.model_name,
                    "dimension": self.embedding_provider.dimension,
                    "content_hash": content_hash,
                    "word_count": result.word_count,
                    "language": result.language,
                    "content_type": result.content_type,
                    "entities": result.extracted_entities,
                    "features": result.metadata_extracted,
                    "indexed_at": now.isoformat()
                }
            })

            # Register content hash for deduplication
            if self.enable_deduplication:
                self.content_hashes[content_hash] = document_id

            result.document = document
            result.success = True

            # Update statistics
            self.stats["documents_indexed"] += 1
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            result.processing_time_ms = processing_time_ms
            self.stats["total_processing_time_ms"] += processing_time_ms

            # Record metrics
            metrics.record_histogram("indexer_document_processing_duration_ms", processing_time_ms)
            metrics.increment_counter("indexer_documents_indexed")
            metrics.record_gauge("indexer_word_count", result.word_count)

            logger.debug(
                "Document indexed successfully",
                document_id=document_id,
                word_count=result.word_count,
                language=result.language,
                content_hash=content_hash[:16],
                processing_time_ms=processing_time_ms
            )

            return result

        except Exception as e:
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            result.processing_time_ms = processing_time_ms
            result.error = f"Indexing failed: {e}"

            logger.error(
                "Failed to index document",
                document_id=document_id,
                error=str(e),
                processing_time_ms=processing_time_ms
            )

            metrics.increment_counter("indexer_errors")
            return result

    async def index_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[IndexingResult]:
        """
        Index multiple documents in batch for better performance.

        Args:
            documents: List of document dictionaries with required fields

        Returns:
            List of IndexingResult objects
        """
        start_time = time.perf_counter()

        try:
            if not documents:
                return []

            # Extract content for batch embedding
            contents = []
            valid_docs = []
            results = []

            for i, doc_data in enumerate(documents):
                if not doc_data.get("content") or not doc_data.get("id"):
                    result = IndexingResult()
                    result.error = "Missing required fields (id, content)"
                    results.append(result)
                    continue

                contents.append(doc_data["content"])
                valid_docs.append((i, doc_data))

            # Generate embeddings in batch
            if contents:
                try:
                    embeddings = await self.embedding_provider.embed_batch(contents)
                except Exception as e:
                    # Fallback to individual processing
                    logger.warning(
                        "Batch embedding failed, falling back to individual processing",
                        error=str(e)
                    )
                    embeddings = []
                    for content in contents:
                        try:
                            emb = await self.embedding_provider.embed_text(content)
                            embeddings.append(emb)
                        except Exception:
                            embeddings.append(None)

                # Process each document
                embedding_idx = 0
                for original_idx, doc_data in valid_docs:
                    embedding = embeddings[embedding_idx] if embedding_idx < len(embeddings) else None
                    embedding_idx += 1

                    if embedding is None:
                        result = IndexingResult()
                        result.error = "Embedding generation failed"
                        results.insert(original_idx, result)
                        continue

                    # Create document using individual processing logic
                    result = await self.index_document(
                        document_id=doc_data["id"],
                        content=doc_data["content"],
                        metadata=doc_data.get("metadata"),
                        identity_id=doc_data.get("identity_id"),
                        lane=doc_data.get("lane", "candidate"),
                        fold_id=doc_data.get("fold_id"),
                        tags=doc_data.get("tags"),
                        expires_at=doc_data.get("expires_at")
                    )

                    # Override embedding with batch result
                    if result.document and embedding is not None:
                        result.document.embedding = embedding

                    results.insert(original_idx, result)

            # Fill in any missing results
            while len(results) < len(documents):
                result = IndexingResult()
                result.error = "Processing skipped"
                results.append(result)

            duration_ms = (time.perf_counter() - start_time) * 1000
            successful_count = sum(1 for r in results if r.success)

            metrics.record_histogram("indexer_batch_processing_duration_ms", duration_ms)
            metrics.increment_counter("indexer_batch_processed")
            metrics.record_gauge("indexer_batch_success_count", successful_count)

            logger.info(
                "Batch indexing completed",
                total_documents=len(documents),
                successful=successful_count,
                failed=len(documents) - successful_count,
                duration_ms=duration_ms
            )

            return results

        except Exception as e:
            logger.error(
                "Failed batch indexing",
                document_count=len(documents),
                error=str(e)
            )

            # Return error results for all documents
            return [
                IndexingResult(error=f"Batch processing failed: {e}")
                for _ in documents
            ]

    def clear_deduplication_cache(self):
        """Clear the deduplication cache"""
        cache_size = len(self.content_hashes)
        self.content_hashes.clear()

        logger.info(
            "Deduplication cache cleared",
            entries_removed=cache_size
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get indexer performance statistics.

        Returns:
            Dictionary of performance metrics and statistics
        """
        stats = self.stats.copy()

        # Calculate averages
        if stats["documents_indexed"] > 0:
            stats["avg_processing_time_ms"] = (
                stats["total_processing_time_ms"] / stats["documents_indexed"]
            )
            stats["duplicate_rate"] = (
                stats["duplicates_detected"] / stats["documents_indexed"]
            )
        else:
            stats["avg_processing_time_ms"] = 0.0
            stats["duplicate_rate"] = 0.0

        # Add configuration info
        stats.update({
            "embedding_provider": self.embedding_provider.model_name,
            "embedding_dimension": self.embedding_provider.dimension,
            "deduplication_enabled": self.enable_deduplication,
            "dedup_threshold": self.dedup_threshold,
            "cached_hashes": len(self.content_hashes)
        })

        return stats