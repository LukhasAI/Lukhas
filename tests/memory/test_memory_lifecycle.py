"""
Test suite for LUKHAS memory lifecycle management.

Validates retention policies, GDPR compliance, archival operations,
and lifecycle automation with T4/0.01% excellence standards.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import numpy as np
import pytest

from memory.backends.base import AbstractVectorStore, VectorDocument
from memory.lifecycle import (
    AbstractArchivalBackend,
    AbstractTombstoneStore,
    ArchivalTier,
    GDPRTombstone,
    MemoryLifecycleManager,
    RetentionPolicy,
    RetentionRule,
)


class MockVectorStore(AbstractVectorStore):
    """Mock vector store for testing"""

    def __init__(self):
        self.documents = {}
        self.deleted_ids = set()

    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def add(self, document):
        self.documents[document.id] = document
        return True

    async def bulk_add(self, documents):
        results = []
        for doc in documents:
            results.append(await self.add(doc))
        return results

    async def get(self, document_id):
        if document_id in self.deleted_ids:
            raise DocumentNotFoundError(
                f"Document {document_id} not found"
            )  # noqa: F821  # TODO: DocumentNotFoundError
        return self.documents.get(document_id)

    async def update(self, document):
        if document.id in self.documents:
            self.documents[document.id] = document
            return True
        return False

    async def delete(self, document_id):
        if document_id in self.documents:
            del self.documents[document_id]
            self.deleted_ids.add(document_id)
            return True
        return False

    async def search(self, query_vector, k=10, filters=None, include_metadata=True):
        return []  # Not needed for lifecycle tests

    async def search_by_text(self, query_text, k=10, filters=None):
        return []  # Not needed for lifecycle tests

    async def cleanup_expired(self):
        return 0

    async def optimize_index(self):
        pass

    async def get_stats(self):
        from memory.backends.base import StorageStats

        return StorageStats(
            total_documents=len(self.documents),
            total_size_bytes=0,
            active_documents=len(self.documents),
            expired_documents=0,
            avg_search_latency_ms=0,
            avg_upsert_latency_ms=0,
            p95_search_latency_ms=0,
            p95_upsert_latency_ms=0,
            memory_usage_bytes=0,
            disk_usage_bytes=0,
            deduplication_rate=0,
            compression_ratio=1.0,
            documents_by_lane={},
            documents_by_fold={},
            avg_dimension=384,
        )

    async def health_check(self):
        return {"status": "healthy"}

    async def list_by_identity(self, identity_id, limit=100):
        results = []
        for doc in self.documents.values():
            if doc.identity_id == identity_id:
                results.append(doc)
                if len(results) >= limit:
                    break
        return results

    def list_expired_documents(self, cutoff_time, limit=1000):
        """Helper method for testing"""
        expired = []
        for doc in self.documents.values():
            if doc.expires_at and doc.expires_at <= cutoff_time:
                expired.append(doc)
                if len(expired) >= limit:
                    break
        return expired


class MockArchivalBackend(AbstractArchivalBackend):
    """Mock archival backend for testing"""

    def __init__(self):
        self.archived_documents = {}
        self.next_archive_id = 1

    async def store_archived_document(self, document, tier, compress=True):
        archive_id = f"archive_{self.next_archive_id}"
        self.next_archive_id += 1
        self.archived_documents[archive_id] = {
            "document": document,
            "tier": tier,
            "compressed": compress,
            "archived_at": datetime.now(timezone.utc),
        }
        return archive_id

    async def retrieve_archived_document(self, archive_id):
        if archive_id not in self.archived_documents:
            raise Exception(f"Archive {archive_id} not found")
        return self.archived_documents[archive_id]["document"]

    async def delete_archived_document(self, archive_id):
        if archive_id in self.archived_documents:
            del self.archived_documents[archive_id]
            return True
        return False


class MockTombstoneStore(AbstractTombstoneStore):
    """Mock tombstone store for testing"""

    def __init__(self):
        self.tombstones = {}

    async def create_tombstone(self, tombstone):
        self.tombstones[tombstone.document_id] = tombstone
        return True

    async def get_tombstone(self, document_id):
        return self.tombstones.get(document_id)

    async def list_tombstones_by_identity(self, identity_id, limit=100):
        results = []
        for tombstone in self.tombstones.values():
            if tombstone.identity_id == identity_id:
                results.append(tombstone)
                if len(results) >= limit:
                    break
        return results

    async def cleanup_old_tombstones(self, older_than):
        count = 0
        to_delete = []
        for doc_id, tombstone in self.tombstones.items():
            if tombstone.deleted_at < older_than:
                to_delete.append(doc_id)
                count += 1

        for doc_id in to_delete:
            del self.tombstones[doc_id]

        return count


class TestRetentionRule:
    """Test retention rule configuration"""

    def test_retention_rule_creation(self):
        """Test retention rule creation"""
        rule = RetentionRule(
            name="test_rule", policy=RetentionPolicy.SHORT_TERM, active_retention_days=30, archive_retention_days=90
        )

        assert rule.name == "test_rule"
        assert rule.policy == RetentionPolicy.SHORT_TERM
        assert rule.active_retention_days == 30
        assert rule.archive_retention_days == 90
        assert rule.archive_tier == ArchivalTier.COLD  # Default

    def test_gdpr_retention_rule(self):
        """Test GDPR-specific retention rule"""
        rule = RetentionRule(
            name="gdpr_personal",
            policy=RetentionPolicy.GDPR_COMPLIANT,
            conditions={"gdpr_category": "personal_data"},
            allow_anonymization=True,
            require_explicit_deletion=True,
        )

        assert rule.policy == RetentionPolicy.GDPR_COMPLIANT
        assert rule.allow_anonymization is True
        assert rule.require_explicit_deletion is True


class TestGDPRTombstone:
    """Test GDPR tombstone functionality"""

    def test_tombstone_creation(self):
        """Test tombstone creation"""
        tombstone = GDPRTombstone(
            document_id="test-doc",
            identity_id="test-identity",
            deleted_at=datetime.now(timezone.utc),
            deletion_reason="gdpr_request",
            original_created_at=datetime.now(timezone.utc) - timedelta(days=30),
            original_lane="labs",
            content_hash="abcdef123456",
            word_count=150,
        )

        assert tombstone.document_id == "test-doc"
        assert tombstone.deletion_reason == "gdpr_request"
        assert tombstone.word_count == 150

    def test_tombstone_serialization(self):
        """Test tombstone serialization"""
        now = datetime.now(timezone.utc)
        tombstone = GDPRTombstone(
            document_id="serial-test",
            identity_id="identity-1",
            deleted_at=now,
            deletion_reason="expiration",
            original_created_at=now - timedelta(days=10),
            original_lane="production",
            original_tags=["tag1", "tag2"],
        )

        # Convert to dict
        data = tombstone.to_dict()
        assert data["document_id"] == "serial-test"
        assert data["original_tags"] == ["tag1", "tag2"]

        # Recreate from dict
        reconstructed = GDPRTombstone.from_dict(data)
        assert reconstructed.document_id == tombstone.document_id
        assert reconstructed.identity_id == tombstone.identity_id
        assert reconstructed.original_tags == tombstone.original_tags


class TestMemoryLifecycleManager:
    """Test memory lifecycle manager"""

    def setup_method(self):
        """Setup test environment"""
        self.vector_store = MockVectorStore()
        self.archival_backend = MockArchivalBackend()
        self.tombstone_store = MockTombstoneStore()

        self.manager = MemoryLifecycleManager(
            vector_store=self.vector_store,
            archival_backend=self.archival_backend,
            tombstone_store=self.tombstone_store,
            enable_gdpr_compliance=True,
            default_retention_days=365,
        )

    def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.vector_store == self.vector_store
        assert self.manager.enable_gdpr_compliance is True
        assert len(self.manager.retention_rules) > 0  # Default rules

    def test_default_rules_setup(self):
        """Test default retention rules setup"""
        rules = self.manager.retention_rules

        # Should have default rules for different lanes
        candidate_rule = None
        production_rule = None

        for rule in rules.values():
            if rule.conditions.get("lane") == "labs":
                candidate_rule = rule
            elif rule.conditions.get("lane") == "production":
                production_rule = rule

        assert candidate_rule is not None
        assert production_rule is not None
        assert candidate_rule.active_retention_days < production_rule.active_retention_days

    def test_add_retention_rule(self):
        """Test adding retention rule"""
        new_rule = RetentionRule(
            name="custom_rule",
            policy=RetentionPolicy.MEDIUM_TERM,
            conditions={"fold_id": "special_fold"},
            active_retention_days=180,
        )

        self.manager.add_retention_rule(new_rule)
        assert "custom_rule" in self.manager.retention_rules

    def test_remove_retention_rule(self):
        """Test removing retention rule"""
        # Add a rule first
        test_rule = RetentionRule(name="to_remove", policy=RetentionPolicy.SHORT_TERM)
        self.manager.add_retention_rule(test_rule)
        assert "to_remove" in self.manager.retention_rules

        # Remove it
        result = self.manager.remove_retention_rule("to_remove")
        assert result is True
        assert "to_remove" not in self.manager.retention_rules

        # Try to remove non-existent rule
        result = self.manager.remove_retention_rule("non_existent")
        assert result is False

    def test_document_matches_conditions(self):
        """Test document condition matching"""
        document = VectorDocument(
            id="test-doc",
            content="Test content",
            embedding=np.random.random(384).astype(np.float32),
            lane="labs",
            identity_id="test-identity",
            tags=["test", "sample"],
        )

        # Test lane matching
        assert self.manager._document_matches_conditions(document, {"lane": "labs"}) is True
        assert self.manager._document_matches_conditions(document, {"lane": "production"}) is False

        # Test identity matching
        assert self.manager._document_matches_conditions(document, {"identity_id": "test-identity"}) is True

        # Test tag matching
        assert self.manager._document_matches_conditions(document, {"tags": ["test"]}) is True
        assert self.manager._document_matches_conditions(document, {"tags": ["nonexistent"]}) is False

    def test_evaluate_retention_rule(self):
        """Test retention rule evaluation"""
        document = VectorDocument(
            id="eval-test", content="Test content", embedding=np.random.random(384).astype(np.float32), lane="labs"
        )

        rule = self.manager._evaluate_retention_rule(document)
        assert rule is not None
        assert rule.conditions.get("lane") == "labs"

    @pytest.mark.asyncio
    async def test_delete_document_with_tombstone(self):
        """Test document deletion with tombstone creation"""
        document = VectorDocument(
            id="tombstone-test",
            content="Content to be deleted",
            embedding=np.random.random(384).astype(np.float32),
            identity_id="test-identity",
            metadata={"indexer": {"content_hash": "abcdef", "word_count": 5}},
        )

        # Add document to store
        await self.vector_store.add(document)

        # Delete with tombstone
        success = await self.manager._delete_document_with_tombstone(document, "gdpr_request", requested_by="user-123")

        assert success is True
        assert "tombstone-test" in self.vector_store.deleted_ids

        # Check tombstone created
        tombstone = await self.tombstone_store.get_tombstone("tombstone-test")
        assert tombstone is not None
        assert tombstone.deletion_reason == "gdpr_request"
        assert tombstone.requested_by == "user-123"

    @pytest.mark.asyncio
    async def test_process_gdpr_deletion_request(self):
        """Test GDPR deletion request processing"""
        # Create test documents
        documents = [
            VectorDocument(
                id=f"gdpr-doc-{i}",
                content=f"Personal data {i}",
                embedding=np.random.random(384).astype(np.float32),
                identity_id="gdpr-test-identity",
            )
            for i in range(3)
        ]

        # Add documents to store
        for doc in documents:
            await self.vector_store.add(doc)

        # Process GDPR request
        summary = await self.manager.process_gdpr_deletion_request(
            identity_id="gdpr-test-identity", requested_by="privacy-officer", legal_basis_removed="consent_withdrawn"
        )

        assert summary["identity_id"] == "gdpr-test-identity"
        assert summary["documents_deleted"] == 3
        assert summary["errors"] == []

        # Verify documents deleted
        for doc in documents:
            assert doc.id in self.vector_store.deleted_ids

        # Verify tombstones created
        tombstones = await self.tombstone_store.list_tombstones_by_identity("gdpr-test-identity")
        assert len(tombstones) == 3

    @pytest.mark.asyncio
    async def test_anonymize_document(self):
        """Test document anonymization"""
        document = VectorDocument(
            id="anonymize-test",
            content="Personal information to anonymize",
            embedding=np.random.random(384).astype(np.float32),
            identity_id="to-anonymize",
            metadata={"personal": True},
        )

        await self.vector_store.add(document)

        # Anonymize
        success = await self.manager._anonymize_document(document, "privacy-request")

        assert success is True

        # Verify document updated
        updated_doc = await self.vector_store.get("anonymize-test")
        assert updated_doc.identity_id is None
        assert updated_doc.content == "[CONTENT ANONYMIZED PER GDPR REQUEST]"
        assert updated_doc.metadata["anonymized"] is True

    @pytest.mark.asyncio
    async def test_archive_document(self):
        """Test document archival"""
        document = VectorDocument(
            id="archive-test", content="Content to archive", embedding=np.random.random(384).astype(np.float32)
        )

        await self.vector_store.add(document)

        rule = RetentionRule(
            name="archive_rule",
            policy=RetentionPolicy.LONG_TERM,
            archive_tier=ArchivalTier.COLD,
            compress_on_archive=True,
        )

        # Archive document
        archive_id = await self.manager._archive_document(document, rule)

        assert archive_id is not None
        assert archive_id.startswith("archive_")

        # Verify document removed from active storage
        assert "archive-test" in self.vector_store.deleted_ids

        # Verify document in archival storage
        archived_doc = await self.archival_backend.retrieve_archived_document(archive_id)
        assert archived_doc.id == "archive-test"

    def test_should_delete_by_default(self):
        """Test default deletion logic"""
        now = datetime.now(timezone.utc)

        # Document with explicit expiration
        expired_doc = VectorDocument(
            id="expired",
            content="Expired content",
            embedding=np.random.random(384).astype(np.float32),
            expires_at=now - timedelta(hours=1),
        )
        assert self.manager._should_delete_by_default(expired_doc, now) is True

        # Old document without expiration
        old_doc = VectorDocument(
            id="old",
            content="Old content",
            embedding=np.random.random(384).astype(np.float32),
            created_at=now - timedelta(days=400),  # Older than default 365 days
        )
        assert self.manager._should_delete_by_default(old_doc, now) is True

        # Recent document
        recent_doc = VectorDocument(
            id="recent",
            content="Recent content",
            embedding=np.random.random(384).astype(np.float32),
            created_at=now - timedelta(days=10),
        )
        assert self.manager._should_delete_by_default(recent_doc, now) is False

    @pytest.mark.asyncio
    async def test_background_tasks(self):
        """Test background task management"""
        # Start background tasks
        await self.manager.start_background_tasks(cleanup_interval_hours=1, archival_interval_hours=24)

        assert self.manager._cleanup_task is not None
        assert self.manager._archival_task is not None

        # Stop background tasks
        await self.manager.stop_background_tasks()

        # Tasks should be cancelled
        assert self.manager._cleanup_task.cancelled() or self.manager._cleanup_task.done()

    def test_statistics_collection(self):
        """Test lifecycle statistics collection"""
        stats = self.manager.get_statistics()

        assert "operations" in stats
        assert "performance" in stats
        assert "gdpr_compliance" in stats
        assert "policies" in stats
        assert "configuration" in stats

        assert stats["configuration"]["gdpr_compliance_enabled"] is True
        assert stats["configuration"]["has_archival_backend"] is True
        assert stats["configuration"]["has_tombstone_store"] is True


class TestLifecycleIntegration:
    """Integration tests for lifecycle management"""

    @pytest.mark.asyncio
    async def test_end_to_end_lifecycle(self):
        """Test complete lifecycle from creation to deletion"""
        vector_store = MockVectorStore()
        archival_backend = MockArchivalBackend()
        tombstone_store = MockTombstoneStore()

        manager = MemoryLifecycleManager(
            vector_store=vector_store, archival_backend=archival_backend, tombstone_store=tombstone_store
        )

        # Add custom rule for testing
        test_rule = RetentionRule(
            name="test_lifecycle",
            policy=RetentionPolicy.SHORT_TERM,
            conditions={"tags": ["test_lifecycle"]},
            active_retention_days=1,  # Very short for testing
            archive_retention_days=0,  # No archival, direct deletion
        )
        manager.add_retention_rule(test_rule)

        # Create test document
        document = VectorDocument(
            id="lifecycle-end-to-end",
            content="End to end lifecycle test",
            embedding=np.random.random(384).astype(np.float32),
            tags=["test_lifecycle"],
            created_at=datetime.now(timezone.utc) - timedelta(days=2),  # Old enough
        )

        await vector_store.add(document)

        # Simulate lifecycle cleanup
        rule = manager._evaluate_retention_rule(document)
        assert rule.name == "test_lifecycle"

        now = datetime.now(timezone.utc)
        action = await manager._apply_retention_rule(document, rule, now)

        assert action == "deleted"
        assert document.id in vector_store.deleted_ids

        # Verify tombstone created
        tombstone = await tombstone_store.get_tombstone(document.id)
        assert tombstone is not None

    @pytest.mark.asyncio
    async def test_mixed_retention_policies(self):
        """Test multiple retention policies working together"""
        vector_store = MockVectorStore()
        manager = MemoryLifecycleManager(vector_store=vector_store)

        # Create documents for different lanes
        candidate_doc = VectorDocument(
            id="candidate-doc",
            content="Candidate lane document",
            embedding=np.random.random(384).astype(np.float32),
            lane="labs",
        )

        production_doc = VectorDocument(
            id="production-doc",
            content="Production lane document",
            embedding=np.random.random(384).astype(np.float32),
            lane="production",
        )

        await vector_store.add(candidate_doc)
        await vector_store.add(production_doc)

        # Evaluate rules
        candidate_rule = manager._evaluate_retention_rule(candidate_doc)
        production_rule = manager._evaluate_retention_rule(production_doc)

        assert candidate_rule.conditions["lane"] == "labs"
        assert production_rule.conditions["lane"] == "production"
        assert candidate_rule.active_retention_days < production_rule.active_retention_days

    @pytest.mark.asyncio
    async def test_performance_requirements(self):
        """Test performance requirements for lifecycle operations"""
        vector_store = MockVectorStore()
        manager = MemoryLifecycleManager(vector_store=vector_store)

        # Create multiple documents
        documents = []
        for i in range(100):
            doc = VectorDocument(
                id=f"perf-test-{i}",
                content=f"Performance test document {i}",
                embedding=np.random.random(384).astype(np.float32),
                lane="labs",
            )
            documents.append(doc)
            await vector_store.add(doc)

        # Time the cleanup operation
        start_time = asyncio.get_event_loop().time()

        # Mock the list_expired_documents to return our test documents
        with patch.object(vector_store, "list_expired_documents", return_value=documents[:10]):
            await manager.cleanup_expired_documents(max_documents=10)

        end_time = asyncio.get_event_loop().time()
        duration_ms = (end_time - start_time) * 1000

        # Target: <5s for 10k documents (scaled for 10 documents)
        assert duration_ms < 1000  # Should be much faster for 10 documents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
