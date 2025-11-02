"""
T4/0.01% Excellence FAISS Vector Backend

High-performance FAISS backend for vector similarity search with advanced indexing
and optimized memory management for production workloads.

Performance targets:
- Single upsert: <50ms p95
- Vector search: <20ms p95 (k≤10)
- Index build: <60s (100k docs)
- Memory efficiency: <4GB for 1M vectors (1536d)
"""

import asyncio
import json
import pickle
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

import numpy as np

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


class FAISSStore(AbstractVectorStore):
    """
    FAISS-based vector store with advanced indexing and persistence.

    Features:
    - Multiple index types (IVF, HNSW, LSH)
    - GPU acceleration support
    - Persistent storage with compression
    - Advanced filtering capabilities
    - Automatic index optimization
    """

    def __init__(
        self,
        dimension: int = 1536,
        index_type: str = "IVF",
        index_params: Optional[Dict[str, Any]] = None,
        persistence_path: Optional[str] = None,
        use_gpu: bool = False,
        max_memory_gb: float = 8.0,
    ):
        if not FAISS_AVAILABLE:
            raise VectorStoreError("FAISS not available. Install with: pip install faiss-cpu or faiss-gpu")

        self.dimension = dimension
        self.index_type = index_type.upper()
        self.index_params = index_params or {}
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.use_gpu = use_gpu and faiss.get_num_gpus() > 0
        self.max_memory_gb = max_memory_gb

        # FAISS index and metadata
        self.index: Optional[faiss.Index] = None
        self.documents: Dict[str, VectorDocument] = {}
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: Dict[int, str] = {}
        self.next_idx = 0

        # Thread safety
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="faiss")

        # Performance tracking
        self._last_build_time = None
        self._build_count = 0
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize FAISS index"""
        if self._initialized:
            return

        try:
            with self._lock:
                # Create index based on type
                self.index = self._create_index()

                # Load persisted data if available
                if self.persistence_path and self.persistence_path.exists():
                    await self._load_from_disk()

                self._initialized = True
                logger.info(
                    "FAISS store initialized",
                    index_type=self.index_type,
                    dimension=self.dimension,
                    use_gpu=self.use_gpu,
                    documents_loaded=len(self.documents),
                )

        except Exception as e:
            logger.error("Failed to initialize FAISS store", error=str(e))
            raise VectorStoreError(f"Failed to initialize: {e}") from e

    async def shutdown(self) -> None:
        """Shutdown FAISS store"""
        try:
            # Save to disk if persistence enabled
            if self.persistence_path:
                await self._save_to_disk()

            # Cleanup resources
            if self.index:
                self.index.reset()
                self.index = None

            self._executor.shutdown(wait=True)
            self._initialized = False

            logger.info("FAISS store shutdown")

        except Exception as e:
            logger.error("Error during FAISS shutdown", error=str(e))

    def _create_index(self) -> faiss.Index:
        """Create FAISS index based on configuration"""
        if self.index_type == "FLAT":
            # Exact search (brute force)
            index = faiss.IndexFlatIP(self.dimension)

        elif self.index_type == "IVF":
            # Inverted file index
            ncentroids = self.index_params.get("ncentroids", 100)
            quantizer = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, ncentroids)
            index.nprobe = self.index_params.get("nprobe", 10)

        elif self.index_type == "HNSW":
            # Hierarchical Navigable Small World
            M = self.index_params.get("M", 32)
            index = faiss.IndexHNSWFlat(self.dimension, M)
            index.hnsw.efConstruction = self.index_params.get("efConstruction", 200)
            index.hnsw.efSearch = self.index_params.get("efSearch", 100)

        elif self.index_type == "LSH":
            # Locality Sensitive Hashing
            nbits = self.index_params.get("nbits", 1024)
            index = faiss.IndexLSH(self.dimension, nbits)

        elif self.index_type == "PQ":
            # Product Quantization
            m = self.index_params.get("m", 8)  # number of subquantizers
            nbits = self.index_params.get("nbits", 8)  # bits per subquantizer
            index = faiss.IndexPQ(self.dimension, m, nbits)

        else:
            raise VectorStoreError(f"Unsupported FAISS index type: {self.index_type}")

        # Move to GPU if requested and available
        if self.use_gpu:
            try:
                gpu_res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(gpu_res, 0, index)
                logger.info("FAISS index moved to GPU")
            except Exception as e:
                logger.warning("Failed to move FAISS index to GPU", error=str(e))

        return index

    async def add(self, document: VectorDocument) -> bool:
        """Add single document to FAISS index"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(document.embedding, self.dimension)
            document.embedding = self._normalize_vector(document.embedding)

            with self._lock:
                # Check if document already exists
                if document.id in self.id_to_idx:
                    # Update existing document
                    idx = self.id_to_idx[document.id]
                    self.documents[document.id] = document

                    # Update vector in index (requires rebuild for most FAISS indices)
                    await self._rebuild_index_if_needed()
                else:
                    # Add new document
                    idx = self.next_idx
                    self.id_to_idx[document.id] = idx
                    self.idx_to_id[idx] = document.id
                    self.documents[document.id] = document
                    self.next_idx += 1

                    # Add vector to index
                    vector = document.embedding.reshape(1, -1)

                    def add_to_index():
                        self.index.add(vector.astype(np.float32))

                    await asyncio.get_event_loop().run_in_executor(self._executor, add_to_index)

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_add_duration_ms", duration_ms)
            metrics.increment_counter("faiss_add_total")

            logger.debug(
                "Document added to FAISS",
                document_id=document.id,
                index_size=self.index.ntotal,
                duration_ms=duration_ms,
            )

            return True

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_add_errors")
            logger.error(
                "Failed to add document to FAISS", document_id=document.id, error=str(e), duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to add document: {e}") from e

    async def bulk_add(self, documents: List[VectorDocument]) -> List[bool]:
        """Add multiple documents in batch"""
        start_time = time.perf_counter()

        try:
            if not documents:
                return []

            # Validate all documents
            for doc in documents:
                self._validate_dimension(doc.embedding, self.dimension)
                doc.embedding = self._normalize_vector(doc.embedding)

            with self._lock:
                # Prepare vectors and metadata
                new_vectors = []
                results = []

                for doc in documents:
                    try:
                        if doc.id not in self.id_to_idx:
                            idx = self.next_idx
                            self.id_to_idx[doc.id] = idx
                            self.idx_to_id[idx] = doc.id
                            self.documents[doc.id] = doc
                            new_vectors.append(doc.embedding)
                            self.next_idx += 1
                            results.append(True)
                        else:
                            # Update existing
                            self.documents[doc.id] = doc
                            results.append(True)
                    except Exception as e:
                        logger.error("Failed to prepare document", document_id=doc.id, error=str(e))
                        results.append(False)

                # Add all new vectors to index
                if new_vectors:
                    vectors_array = np.vstack(new_vectors).astype(np.float32)

                    def bulk_add_to_index():
                        self.index.add(vectors_array)

                    await asyncio.get_event_loop().run_in_executor(self._executor, bulk_add_to_index)

            duration_ms = (time.perf_counter() - start_time) * 1000
            success_count = sum(results)

            metrics.record_histogram("faiss_bulk_add_duration_ms", duration_ms)
            metrics.increment_counter("faiss_bulk_add_total")
            metrics.record_gauge("faiss_bulk_add_success_count", success_count)

            logger.info(
                "Bulk add completed",
                total_documents=len(documents),
                successful=success_count,
                failed=len(documents) - success_count,
                index_size=self.index.ntotal,
                duration_ms=duration_ms,
            )

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_bulk_add_errors")
            logger.error(
                "Failed bulk add operation", document_count=len(documents), error=str(e), duration_ms=duration_ms
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
            metrics.record_histogram("faiss_get_duration_ms", duration_ms)
            metrics.increment_counter("faiss_get_total")

            return document

        except DocumentNotFoundError:
            raise
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_get_errors")
            logger.error(
                "Failed to get document from FAISS", document_id=document_id, error=str(e), duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to get document: {e}") from e

    async def update(self, document: VectorDocument) -> bool:
        """Update existing document (same as add for FAISS)"""
        return await self.add(document)

    async def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        start_time = time.perf_counter()

        try:
            with self._lock:
                if document_id not in self.documents:
                    return False

                # Remove from metadata
                idx = self.id_to_idx[document_id]
                del self.documents[document_id]
                del self.id_to_idx[document_id]
                del self.idx_to_id[idx]

                # FAISS doesn't support efficient deletion, so we mark for rebuild
                await self._rebuild_index_if_needed()

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_delete_duration_ms", duration_ms)
            metrics.increment_counter("faiss_delete_total")

            logger.debug("Document deleted from FAISS", document_id=document_id, duration_ms=duration_ms)

            return True

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_delete_errors")
            logger.error(
                "Failed to delete document from FAISS", document_id=document_id, error=str(e), duration_ms=duration_ms
            )
            raise VectorStoreError(f"Failed to delete document: {e}") from e

    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
    ) -> List[SearchResult]:
        """Vector similarity search using FAISS"""
        start_time = time.perf_counter()

        try:
            self._validate_dimension(query_vector, self.dimension)
            query_vector = self._normalize_vector(query_vector)

            # Perform FAISS search
            def faiss_search():
                query = query_vector.reshape(1, -1).astype(np.float32)
                scores, indices = self.index.search(query, k)
                return scores[0], indices[0]

            scores, indices = await asyncio.get_event_loop().run_in_executor(self._executor, faiss_search)

            results = []
            rank = 0

            with self._lock:
                for score, idx in zip(scores, indices):
                    if idx == -1:  # FAISS returns -1 for empty slots
                        break

                    if idx in self.idx_to_id:
                        doc_id = self.idx_to_id[idx]
                        if doc_id in self.documents:
                            document = self.documents[doc_id]

                            # Apply filters
                            if filters and not self._matches_filters(document, filters):
                                continue

                            # Skip expired documents
                            if document.is_expired:
                                continue

                            result = SearchResult(
                                document=document,
                                score=float(score),
                                rank=rank,
                                search_latency_ms=(time.perf_counter() - start_time) * 1000,
                                retrieval_method="faiss",
                            )
                            results.append(result)
                            rank += 1

                            if len(results) >= k:
                                break

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_search_duration_ms", duration_ms)
            metrics.increment_counter("faiss_search_total")
            metrics.record_gauge("faiss_search_results_count", len(results))

            logger.debug(
                "FAISS search completed", k=k, results_count=len(results), duration_ms=duration_ms, filters=filters
            )

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_search_errors")
            logger.error("Failed FAISS search", k=k, filters=filters, error=str(e), duration_ms=duration_ms)
            raise VectorStoreError(f"Failed FAISS search: {e}") from e

    async def search_by_text(
        self, query_text: str, k: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Text-based search using simple text matching"""
        start_time = time.perf_counter()

        try:
            results = []
            rank = 0

            with self._lock:
                for doc_id, document in self.documents.items():
                    # Skip expired documents
                    if document.is_expired:
                        continue

                    # Apply filters
                    if filters and not self._matches_filters(document, filters):
                        continue

                    # Simple text matching
                    if query_text.lower() in document.content.lower():
                        score = 1.0 - (rank * 0.1)  # Simple ranking
                        result = SearchResult(
                            document=document,
                            score=max(0.0, score),
                            rank=rank,
                            search_latency_ms=(time.perf_counter() - start_time) * 1000,
                            retrieval_method="text_search",
                        )
                        results.append(result)
                        rank += 1

                        if len(results) >= k:
                            break

            # Sort by score descending
            results.sort(key=lambda x: x.score, reverse=True)

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_text_search_duration_ms", duration_ms)
            metrics.increment_counter("faiss_text_search_total")

            return results

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_text_search_errors")
            logger.error("Failed text search in FAISS", query_text=query_text, error=str(e), duration_ms=duration_ms)
            raise VectorStoreError(f"Failed text search: {e}") from e

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
                    idx = self.id_to_idx[doc_id]
                    del self.documents[doc_id]
                    del self.id_to_idx[doc_id]
                    del self.idx_to_id[idx]
                    deleted_count += 1

                # Rebuild index if we removed documents
                if deleted_count > 0:
                    await self._rebuild_index_if_needed()

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_cleanup_duration_ms", duration_ms)
            metrics.increment_counter("faiss_cleanup_total")
            metrics.record_gauge("faiss_cleanup_deleted_count", deleted_count)

            logger.info("Expired documents cleaned up", deleted_count=deleted_count, duration_ms=duration_ms)

            return deleted_count

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_cleanup_errors")
            logger.error("Failed to cleanup expired documents", error=str(e), duration_ms=duration_ms)
            return 0

    async def optimize_index(self) -> None:
        """Optimize FAISS index"""
        start_time = time.perf_counter()

        try:
            if self.index_type == "IVF" and hasattr(self.index, "train"):
                # Re-train IVF index for better performance
                vectors = []
                with self._lock:
                    for document in self.documents.values():
                        vectors.append(document.embedding)

                if vectors:
                    vectors_array = np.vstack(vectors).astype(np.float32)

                    def train_index():
                        self.index.train(vectors_array)

                    await asyncio.get_event_loop().run_in_executor(self._executor, train_index)

            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_histogram("faiss_optimize_duration_ms", duration_ms)
            metrics.increment_counter("faiss_optimize_total")

            logger.info("FAISS index optimization completed", index_type=self.index_type, duration_ms=duration_ms)

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.increment_counter("faiss_optimize_errors")
            logger.error("Failed to optimize FAISS index", error=str(e), duration_ms=duration_ms)
            raise VectorStoreError(f"Failed to optimize index: {e}") from e

    async def _rebuild_index_if_needed(self) -> None:
        """Rebuild FAISS index if needed (for deletions/updates)"""
        # Only rebuild if we have significant changes or it's been a while
        if len(self.documents) > 1000 and len(self.documents) % 100 == 0:
            await self._rebuild_index()

    async def _rebuild_index(self) -> None:
        """Rebuild entire FAISS index"""
        start_time = time.perf_counter()

        try:
            # Create new index
            new_index = self._create_index()

            # Collect all vectors
            vectors = []
            id_mapping = {}

            idx = 0
            for doc_id, document in self.documents.items():
                if not document.is_expired:
                    vectors.append(document.embedding)
                    id_mapping[idx] = doc_id
                    idx += 1

            if vectors:
                vectors_array = np.vstack(vectors).astype(np.float32)

                # Train if needed (for IVF)
                if hasattr(new_index, "is_trained") and not new_index.is_trained:

                    def train_index():
                        new_index.train(vectors_array)

                    await asyncio.get_event_loop().run_in_executor(self._executor, train_index)

                # Add vectors
                def add_vectors():
                    new_index.add(vectors_array)

                await asyncio.get_event_loop().run_in_executor(self._executor, add_vectors)

            # Update mappings
            self.index = new_index
            self.idx_to_id = id_mapping
            self.id_to_idx = {doc_id: idx for idx, doc_id in id_mapping.items()}
            self.next_idx = len(id_mapping)

            duration_ms = (time.perf_counter() - start_time) * 1000
            self._last_build_time = time.time()
            self._build_count += 1

            logger.info(
                "FAISS index rebuilt",
                document_count=len(vectors),
                duration_ms=duration_ms,
                build_count=self._build_count,
            )

        except Exception as e:
            logger.error("Failed to rebuild FAISS index", error=str(e))
            raise VectorStoreError(f"Failed to rebuild index: {e}") from e

    async def _save_to_disk(self) -> None:
        """Save FAISS index and metadata to disk"""
        if not self.persistence_path:
            return

        try:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            index_path = self.persistence_path.with_suffix(".faiss")

            def save_index():
                if self.use_gpu:
                    # Move to CPU for saving
                    cpu_index = faiss.index_gpu_to_cpu(self.index)
                    faiss.write_index(cpu_index, str(index_path))
                else:
                    faiss.write_index(self.index, str(index_path))

            await asyncio.get_event_loop().run_in_executor(self._executor, save_index)

            # Save metadata
            metadata = {
                "documents": {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()},
                "id_to_idx": self.id_to_idx,
                "idx_to_id": self.idx_to_id,
                "next_idx": self.next_idx,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "index_params": self.index_params,
            }

            with open(self.persistence_path.with_suffix(".pkl"), "wb") as f:
                pickle.dump(metadata, f)

            logger.info("FAISS data saved to disk", index_path=str(index_path), document_count=len(self.documents))

        except Exception as e:
            logger.error("Failed to save FAISS data to disk", error=str(e))

    async def _load_from_disk(self) -> None:
        """Load FAISS index and metadata from disk"""
        if not self.persistence_path or not self.persistence_path.exists():
            return

        try:
            # Load index
            index_path = self.persistence_path.with_suffix(".faiss")
            if index_path.exists():

                def load_index():
                    index = faiss.read_index(str(index_path))
                    if self.use_gpu and faiss.get_num_gpus() > 0:
                        gpu_res = faiss.StandardGpuResources()
                        index = faiss.index_cpu_to_gpu(gpu_res, 0, index)
                    return index

                self.index = await asyncio.get_event_loop().run_in_executor(self._executor, load_index)

            # Load metadata
            metadata_path = self.persistence_path.with_suffix(".pkl")
            if metadata_path.exists():
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)

                self.documents = {
                    doc_id: VectorDocument.from_dict(doc_data) for doc_id, doc_data in metadata["documents"].items()
                }
                self.id_to_idx = metadata["id_to_idx"]
                self.idx_to_id = metadata["idx_to_id"]
                self.next_idx = metadata["next_idx"]

            logger.info(
                "FAISS data loaded from disk",
                document_count=len(self.documents),
                index_size=self.index.ntotal if self.index else 0,
            )

        except Exception as e:
            logger.error("Failed to load FAISS data from disk", error=str(e))

    async def get_stats(self) -> StorageStats:
        """Get comprehensive storage statistics"""
        try:
            with self._lock:
                total_docs = len(self.documents)
                active_docs = sum(1 for doc in self.documents.values() if not doc.is_expired)
                expired_docs = total_docs - active_docs

                # Calculate storage size estimate
                doc_size_bytes = sum(
                    len(doc.content.encode("utf-8"))
                    + doc.embedding.nbytes
                    + len(json.dumps(doc.metadata).encode("utf-8"))
                    for doc in self.documents.values()
                )

                # Index size estimate
                index_size_bytes = self.index.ntotal * self.dimension * 4  # 4 bytes per float32

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
                    total_size_bytes=doc_size_bytes + index_size_bytes,
                    active_documents=active_docs,
                    expired_documents=expired_docs,
                    avg_search_latency_ms=0.0,  # Would need metrics aggregation
                    avg_upsert_latency_ms=0.0,  # Would need metrics aggregation
                    p95_search_latency_ms=0.0,  # Would need metrics aggregation
                    p95_upsert_latency_ms=0.0,  # Would need metrics aggregation
                    memory_usage_bytes=index_size_bytes,
                    disk_usage_bytes=doc_size_bytes,
                    deduplication_rate=0.0,
                    compression_ratio=1.0,
                    documents_by_lane=documents_by_lane,
                    documents_by_fold=documents_by_fold,
                    avg_dimension=float(self.dimension),
                )

        except Exception as e:
            logger.error("Failed to get FAISS stats", error=str(e))
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
                avg_dimension=float(self.dimension),
            )

    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        try:
            with self._lock:
                return {
                    "status": "healthy",
                    "index_type": self.index_type,
                    "dimension": self.dimension,
                    "document_count": len(self.documents),
                    "index_size": self.index.ntotal if self.index else 0,
                    "use_gpu": self.use_gpu,
                    "build_count": self._build_count,
                    "last_build_time": self._last_build_time,
                    "memory_usage_mb": (self.index.ntotal * self.dimension * 4) / (1024 * 1024) if self.index else 0,
                }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}
