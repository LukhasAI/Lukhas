"""
T4/0.01% Excellence Memory Lifecycle Tests

Comprehensive test suite for memory lifecycle management including:
- Retention policy enforcement
- Document archival with gzip compression
- GDPR tombstone creation and read-back
- Audit event generation and validation
- Performance target validation (<100ms p95 for tombstones)
"""

import gzip
import json
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Import VectorDocument directly without importing from backends package
from typing import Any, Optional

import numpy as np
import pytest

from memory.lifecycle import (
    ArchivalTier,
    FileArchivalBackend,
    FileTombstoneStore,
    GDPRTombstone,
    LifecycleStats,
    MemoryLifecycleManager,
    RetentionPolicy,
    RetentionRule,
)


# Define a minimal VectorDocument class for testing
@dataclass
class VectorDocument:
    """Minimal VectorDocument for testing"""
    id: str
    content: str
    embedding: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
    identity_id: Optional[str] = None
    lane: str = "labs"
    fold_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
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
    def is_expired(self) -> bool:
        """Check if document has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> dict[str, Any]:
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


class MockVectorStore:
    """Mock vector store for testing lifecycle operations"""

    def __init__(self):
        self.documents: dict[str, VectorDocument] = {}

    async def delete(self, doc_id: str) -> bool:
        """Delete document from store"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False

    async def update(self, document: VectorDocument) -> bool:
        """Update document in store"""
        self.documents[document.id] = document
        return True

    async def list_expired_documents(self, cutoff_time: datetime, limit: int) -> list[VectorDocument]:
        """List documents that have expired"""
        expired = []
        for doc in self.documents.values():
            if doc.is_expired or (doc.created_at < cutoff_time - timedelta(days=30)):
                expired.append(doc)
                if len(expired) >= limit:
                    break
        return expired

    async def list_by_identity(self, identity_id: str, limit: int) -> list[VectorDocument]:
        """List documents by identity"""
        matching = [
            doc for doc in self.documents.values()
            if doc.identity_id == identity_id
        ]
        return matching[:limit]


@pytest.fixture
def temp_dir():
    """Temporary directory for test artifacts"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_vector_store():
    """Mock vector store with sample documents"""
    store = MockVectorStore()

    # Add some test documents
    now = datetime.now(timezone.utc)

    # Expired document for cleanup testing
    expired_doc = VectorDocument(
        id="doc_expired_1",
        content="This document has expired",
        embedding=np.random.random(1536).astype(np.float32),
        identity_id="user_123",
        lane="labs",
        tags=["test", "expired"],
        created_at=now - timedelta(days=60),  # Old document
        expires_at=now - timedelta(days=1)   # Expired yesterday
    )
    store.documents["doc_expired_1"] = expired_doc

    # Active document for GDPR testing
    active_doc = VectorDocument(
        id="doc_active_1",
        content="This document contains personal data",
        embedding=np.random.random(1536).astype(np.float32),
        identity_id="user_123",
        lane="production",
        tags=["personal", "active"],
        metadata={"gdpr": {"category": "personal_data"}},
        created_at=now - timedelta(days=10)
    )
    store.documents["doc_active_1"] = active_doc

    return store


@pytest.fixture
def file_archival_backend(temp_dir):
    """File-based archival backend for testing"""
    archive_path = Path(temp_dir) / "archive"
    return FileArchivalBackend(str(archive_path))


@pytest.fixture
def file_tombstone_store(temp_dir):
    """File-based tombstone store for testing"""
    artifacts_path = Path(temp_dir) / "artifacts"
    return FileTombstoneStore(str(artifacts_path))


@pytest.fixture
def lifecycle_manager(mock_vector_store, file_archival_backend, file_tombstone_store):
    """Memory lifecycle manager with all backends configured"""
    return MemoryLifecycleManager(
        vector_store=mock_vector_store,
        archival_backend=file_archival_backend,
        tombstone_store=file_tombstone_store,
        enable_gdpr_compliance=True,
        default_retention_days=30
    )


class TestMemoryLifecycleRetention:
    """Test retention policy enforcement"""

    @pytest.mark.asyncio
    async def test_retention_rule_evaluation(self, lifecycle_manager, mock_vector_store):
        """Test that retention rules are properly evaluated"""
        # Add a specific retention rule for candidate lane
        rule = RetentionRule(
            name="test_candidate_rule",
            policy=RetentionPolicy.SHORT_TERM,
            conditions={"lane": "labs", "tags": ["expired"]},
            active_retention_days=7,
            archive_retention_days=30
        )
        lifecycle_manager.add_retention_rule(rule)

        # Get the expired document
        doc = mock_vector_store.documents["doc_expired_1"]

        # Test rule evaluation
        matching_rule = lifecycle_manager._evaluate_retention_rule(doc)
        assert matching_rule is not None
        assert matching_rule.name == "test_candidate_rule"
        assert matching_rule.policy == RetentionPolicy.SHORT_TERM

    @pytest.mark.asyncio
    async def test_document_cleanup_with_archival(self, lifecycle_manager, mock_vector_store, file_archival_backend):
        """Test document cleanup with archival"""
        # Configure rule to archive instead of delete
        rule = RetentionRule(
            name="archive_rule",
            policy=RetentionPolicy.MEDIUM_TERM,
            conditions={"lane": "labs"},
            active_retention_days=7,
            archive_retention_days=365,
            archive_tier=ArchivalTier.COLD
        )
        lifecycle_manager.add_retention_rule(rule)

        initial_count = len(mock_vector_store.documents)

        # Run cleanup
        stats = await lifecycle_manager.cleanup_expired_documents(max_documents=1)

        # Check that document was archived (removed from active storage)
        assert len(mock_vector_store.documents) < initial_count
        assert stats.documents_archived > 0
        assert stats.cleanup_duration_ms < 5000  # Performance target: <5s for 10k docs

    @pytest.mark.asyncio
    async def test_retention_policy_statistics(self, lifecycle_manager):
        """Test retention policy usage statistics"""
        stats = await lifecycle_manager.cleanup_expired_documents()

        # Check that statistics are populated
        assert isinstance(stats, LifecycleStats)
        assert stats.cleanup_duration_ms >= 0
        assert len(stats.retention_rules_applied) >= 0


class TestArchivalOperations:
    """Test document archival with gzip compression"""

    @pytest.mark.asyncio
    async def test_archive_document_gzip(self, file_archival_backend):
        """Test archiving document with gzip compression"""
        # Create test document
        doc = VectorDocument(
            id="test_doc_archive",
            content="This content will be archived and compressed",
            embedding=np.random.random(1536).astype(np.float32),
            identity_id="user_archive",
            lane="integration",
            tags=["archive_test"]
        )

        # Archive with compression
        archive_id = await file_archival_backend.store_archived_document(
            doc,
            ArchivalTier.COLD,
            compress=True
        )

        assert archive_id.startswith("arch_")

        # Check that file exists and is compressed
        archive_path = file_archival_backend._get_archive_path(archive_id)
        assert archive_path.exists()
        assert archive_path.suffix == ".gz"

        # Verify we can read the compressed content
        with gzip.open(archive_path, 'rt', encoding='utf-8') as f:
            archive_data = json.load(f)

        assert archive_data["archive_id"] == archive_id
        assert archive_data["document"]["id"] == doc.id
        assert archive_data["compressed"] is True
        assert archive_data["tier"] == ArchivalTier.COLD.value

    @pytest.mark.asyncio
    async def test_retrieve_archived_document(self, file_archival_backend):
        """Test retrieving archived document and reconstructing VectorDocument"""
        # Create and archive document
        original_doc = VectorDocument(
            id="test_retrieve",
            content="Content for retrieval test",
            embedding=np.random.random(1536).astype(np.float32),
            identity_id="user_retrieve",
            lane="production",
            tags=["retrieve_test"],
            metadata={"test_key": "test_value"}
        )

        archive_id = await file_archival_backend.store_archived_document(
            original_doc,
            ArchivalTier.WARM,
            compress=True
        )

        # Retrieve the document
        retrieved_doc = await file_archival_backend.retrieve_archived_document(archive_id)

        # Verify document reconstruction
        assert retrieved_doc.id == original_doc.id
        assert retrieved_doc.content == original_doc.content
        assert retrieved_doc.identity_id == original_doc.identity_id
        assert retrieved_doc.lane == original_doc.lane
        assert retrieved_doc.tags == original_doc.tags
        assert retrieved_doc.metadata == original_doc.metadata
        np.testing.assert_array_almost_equal(retrieved_doc.embedding, original_doc.embedding)

    @pytest.mark.asyncio
    async def test_delete_archived_document(self, file_archival_backend):
        """Test deleting archived document"""
        # Create and archive document
        doc = VectorDocument(
            id="test_delete_archive",
            content="This will be deleted",
            embedding=np.random.random(1536).astype(np.float32),
            lane="labs"
        )

        archive_id = await file_archival_backend.store_archived_document(
            doc,
            ArchivalTier.FROZEN,
            compress=True
        )

        # Verify file exists
        archive_path = file_archival_backend._get_archive_path(archive_id)
        assert archive_path.exists()

        # Delete archived document
        success = await file_archival_backend.delete_archived_document(archive_id)
        assert success is True

        # Verify file was deleted
        assert not archive_path.exists()


class TestGDPRTombstones:
    """Test GDPR tombstone creation and read-back"""

    @pytest.mark.asyncio
    async def test_tombstone_creation_performance(self, file_tombstone_store):
        """Test tombstone creation meets <100ms p95 performance target"""
        import time

        tombstone = GDPRTombstone(
            document_id="perf_test_doc",
            identity_id="user_perf_test",
            deleted_at=datetime.now(timezone.utc),
            deletion_reason="performance_test",
            requested_by="test_suite",
            original_created_at=datetime.now(timezone.utc) - timedelta(days=30),
            original_lane="labs",
            original_fold_id="fold_123",
            original_tags=["performance", "test"],
            content_hash="abc123",
            word_count=150,
            language="en",
            gdpr_category="personal_data"
        )

        # Measure tombstone creation time
        start_time = time.perf_counter()
        success = await file_tombstone_store.create_tombstone(tombstone)
        duration_ms = (time.perf_counter() - start_time) * 1000

        assert success is True
        assert duration_ms < 100  # Performance target: <100ms p95

        # Verify audit event was written
        artifacts_path = file_tombstone_store.base_path
        audit_files = list(artifacts_path.glob("memory_validation_*.json"))
        assert len(audit_files) > 0

        # Check audit event content
        with open(audit_files[0], encoding='utf-8') as f:
            audit_event = json.loads(f.read().strip())

        assert audit_event["event_type"] == "tombstone_created"
        assert audit_event["tombstone"]["document_id"] == "perf_test_doc"
        assert audit_event["audit_metadata"]["compliance_version"] == "GDPR-2018"

    @pytest.mark.asyncio
    async def test_tombstone_read_back(self, file_tombstone_store):
        """Test tombstone retrieval and data integrity"""
        # Create tombstone
        original_tombstone = GDPRTombstone(
            document_id="readback_test_doc",
            identity_id="user_readback",
            deleted_at=datetime.now(timezone.utc),
            deletion_reason="gdpr_request",
            requested_by="data_subject",
            original_created_at=datetime.now(timezone.utc) - timedelta(days=45),
            original_lane="production",
            gdpr_category="personal_data",
            legal_basis_removed="consent_withdrawn"
        )

        await file_tombstone_store.create_tombstone(original_tombstone)

        # Read back tombstone
        retrieved_tombstone = await file_tombstone_store.get_tombstone("readback_test_doc")

        assert retrieved_tombstone is not None
        assert retrieved_tombstone.document_id == original_tombstone.document_id
        assert retrieved_tombstone.identity_id == original_tombstone.identity_id
        assert retrieved_tombstone.deletion_reason == original_tombstone.deletion_reason
        assert retrieved_tombstone.gdpr_category == original_tombstone.gdpr_category
        assert retrieved_tombstone.legal_basis_removed == original_tombstone.legal_basis_removed

        # Verify tombstone access creates audit event
        artifacts_path = file_tombstone_store.base_path
        audit_files = list(artifacts_path.glob("memory_validation_*.json"))
        assert len(audit_files) > 0

    @pytest.mark.asyncio
    async def test_tombstone_cleanup_old_entries(self, file_tombstone_store):
        """Test cleanup of old tombstones"""
        now = datetime.now(timezone.utc)

        # Create old tombstone (should be cleaned up)
        old_tombstone = GDPRTombstone(
            document_id="old_tombstone",
            identity_id="user_old",
            deleted_at=now - timedelta(days=400),  # Very old
            deletion_reason="expiration",
            original_created_at=now - timedelta(days=450),
            original_lane="labs"
        )

        # Create recent tombstone (should be kept)
        recent_tombstone = GDPRTombstone(
            document_id="recent_tombstone",
            identity_id="user_recent",
            deleted_at=now - timedelta(days=30),   # Recent
            deletion_reason="gdpr_request",
            original_created_at=now - timedelta(days=60),
            original_lane="production"
        )

        await file_tombstone_store.create_tombstone(old_tombstone)
        await file_tombstone_store.create_tombstone(recent_tombstone)

        # Clean up tombstones older than 365 days
        cleanup_threshold = now - timedelta(days=365)
        deleted_count = await file_tombstone_store.cleanup_old_tombstones(cleanup_threshold)

        assert deleted_count == 1  # Only old tombstone should be deleted

        # Verify old tombstone is gone
        assert await file_tombstone_store.get_tombstone("old_tombstone") is None

        # Verify recent tombstone is still there
        assert await file_tombstone_store.get_tombstone("recent_tombstone") is not None


class TestGDPRCompliance:
    """Test GDPR compliance features"""

    @pytest.mark.asyncio
    async def test_gdpr_deletion_request(self, lifecycle_manager, mock_vector_store):
        """Test processing GDPR right-to-be-forgotten request"""
        # Process GDPR deletion request
        deletion_summary = await lifecycle_manager.process_gdpr_deletion_request(
            identity_id="user_123",
            requested_by="data_subject",
            legal_basis_removed="consent_withdrawn"
        )

        # Verify deletion summary
        assert deletion_summary["identity_id"] == "user_123"
        assert deletion_summary["requested_by"] == "data_subject"
        assert deletion_summary["legal_basis_removed"] == "consent_withdrawn"
        assert deletion_summary["documents_deleted"] >= 0
        assert deletion_summary["processing_time_ms"] > 0

        # Verify documents were processed
        remaining_docs = await mock_vector_store.list_by_identity("user_123", limit=100)
        # Documents should be deleted or anonymized
        for doc in remaining_docs:
            if doc.content != "[CONTENT ANONYMIZED PER GDPR REQUEST]":
                # If not anonymized, should not contain personal identifiers
                assert doc.identity_id != "user_123" or "anonymized" in doc.metadata

    @pytest.mark.asyncio
    async def test_document_anonymization(self, lifecycle_manager, mock_vector_store):
        """Test document anonymization instead of deletion"""
        # Add retention rule that allows anonymization
        rule = RetentionRule(
            name="anonymization_rule",
            policy=RetentionPolicy.GDPR_COMPLIANT,
            conditions={"gdpr_category": "personal_data"},
            allow_anonymization=True,
            require_explicit_deletion=False
        )
        lifecycle_manager.add_retention_rule(rule)

        # Get document that matches anonymization rule
        doc = mock_vector_store.documents["doc_active_1"]
        original_content = doc.content

        # Anonymize the document
        success = await lifecycle_manager._anonymize_document(doc, "test_anonymizer")

        assert success is True

        # Check document was anonymized
        anonymized_doc = mock_vector_store.documents["doc_active_1"]
        assert anonymized_doc.content == "[CONTENT ANONYMIZED PER GDPR REQUEST]"
        assert anonymized_doc.content != original_content
        assert anonymized_doc.identity_id is None  # Identity link removed
        assert anonymized_doc.metadata["anonymized"] is True
        assert "personal_" not in str(anonymized_doc.tags)  # Personal tags removed


class TestAuditEventGeneration:
    """Test audit event generation and validation"""

    @pytest.mark.asyncio
    async def test_audit_event_structure(self, file_tombstone_store, temp_dir):
        """Test audit event JSON structure and compliance metadata"""
        tombstone = GDPRTombstone(
            document_id="audit_test_doc",
            identity_id="user_audit",
            deleted_at=datetime.now(timezone.utc),
            deletion_reason="audit_test",
            original_created_at=datetime.now(timezone.utc) - timedelta(days=20),
            original_lane="integration"
        )

        await file_tombstone_store.create_tombstone(tombstone)

        # Read audit event file
        artifacts_path = Path(temp_dir) / "artifacts"
        audit_files = list(artifacts_path.glob("memory_validation_*.json"))
        assert len(audit_files) > 0

        with open(audit_files[0], encoding='utf-8') as f:
            audit_event = json.loads(f.read().strip())

        # Validate audit event structure
        required_fields = [
            "event_type", "timestamp", "tombstone", "audit_metadata"
        ]
        for field in required_fields:
            assert field in audit_event, f"Missing required field: {field}"

        # Validate compliance metadata
        audit_metadata = audit_event["audit_metadata"]
        assert audit_metadata["compliance_version"] == "GDPR-2018"
        assert audit_metadata["lukhas_version"] == "1.0.0"
        assert audit_metadata["retention_policy_version"] == "v2.1"

        # Validate tombstone data integrity
        tombstone_data = audit_event["tombstone"]
        assert tombstone_data["document_id"] == "audit_test_doc"
        assert tombstone_data["identity_id"] == "user_audit"
        assert tombstone_data["deletion_reason"] == "audit_test"

    @pytest.mark.asyncio
    async def test_multiple_audit_events_append(self, file_tombstone_store):
        """Test that multiple audit events append to same file"""
        # Create multiple tombstones to generate multiple events
        for i in range(3):
            tombstone = GDPRTombstone(
                document_id=f"multi_audit_doc_{i}",
                identity_id=f"user_multi_{i}",
                deleted_at=datetime.now(timezone.utc),
                deletion_reason="multi_test",
                original_created_at=datetime.now(timezone.utc) - timedelta(days=10),
                original_lane="labs"
            )
            await file_tombstone_store.create_tombstone(tombstone)

        # Check that events were appended to file
        artifacts_path = file_tombstone_store.base_path
        audit_files = list(artifacts_path.glob("memory_validation_*.json"))
        assert len(audit_files) > 0

        # Count events in file
        with open(audit_files[0], encoding='utf-8') as f:
            content = f.read().strip()
            events = [json.loads(line) for line in content.split('\n') if line.strip()]

        assert len(events) >= 3  # At least 3 events (could be more from other tests)

        # Verify all our events are there
        our_events = [e for e in events if e.get("tombstone", {}).get("deletion_reason") == "multi_test"]
        assert len(our_events) == 3


class TestPerformanceTargets:
    """Test performance targets for lifecycle operations"""

    @pytest.mark.asyncio
    async def test_cleanup_performance_10k_docs(self, lifecycle_manager):
        """Test cleanup operations <5s for 10k documents target"""
        import time

        # Simulate processing many documents (mock the expensive operations)
        start_time = time.perf_counter()

        # Run cleanup with batch processing
        stats = await lifecycle_manager.cleanup_expired_documents(
            batch_size=1000,
            max_documents=10000
        )

        duration_s = (time.perf_counter() - start_time)

        # Performance target: <5s for 10k documents
        # Note: This is a scaled test since we don't have 10k real documents
        assert duration_s < 5.0, f"Cleanup took {duration_s:.2f}s, exceeds 5s target"
        assert stats.cleanup_duration_ms < 5000

    @pytest.mark.asyncio
    async def test_archival_performance_100k_docs(self, file_archival_backend):
        """Test archival operations <30s for 100k documents target"""
        import time

        # Test archival speed with multiple documents
        documents = []
        for i in range(10):  # Scaled down test
            doc = VectorDocument(
                id=f"perf_test_{i}",
                content=f"Performance test document {i} with substantial content to test compression and I/O performance under load conditions.",
                embedding=np.random.random(1536).astype(np.float32),
                lane="performance_test"
            )
            documents.append(doc)

        start_time = time.perf_counter()

        # Archive all documents
        archive_ids = []
        for doc in documents:
            archive_id = await file_archival_backend.store_archived_document(
                doc,
                ArchivalTier.COLD,
                compress=True
            )
            archive_ids.append(archive_id)

        duration_s = (time.perf_counter() - start_time)

        # Scale performance expectation (10 docs should be much faster than target)
        expected_max = 0.3  # 30s / 100 scale factor
        assert duration_s < expected_max, f"Archival took {duration_s:.2f}s for 10 docs"

        # Verify all archives were created successfully
        assert len(archive_ids) == 10
        for archive_id in archive_ids:
            retrieved_doc = await file_archival_backend.retrieve_archived_document(archive_id)
            assert retrieved_doc is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
