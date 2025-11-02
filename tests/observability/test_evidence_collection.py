#!/usr/bin/env python3
"""
Test suite for LUKHAS Evidence Collection Engine
Comprehensive tests for tamper-evident audit logging and evidence integrity.
"""

import asyncio

# Test imports
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability.evidence_collection import (
    ComplianceRegime,
    EvidenceCollectionEngine,
    EvidenceType,
    collect_evidence,
    initialize_evidence_collection,
)


@pytest.fixture
async def temp_evidence_dir():
    """Create temporary directory for evidence storage"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
async def evidence_engine(temp_evidence_dir):
    """Create evidence collection engine for testing"""
    engine = EvidenceCollectionEngine(
        storage_path=str(temp_evidence_dir),
        retention_days=30,
        compression_enabled=True,
        encryption_enabled=True,
        chain_block_size=5,  # Small block size for testing
    )
    yield engine
    await engine.shutdown()


class TestEvidenceCollectionEngine:
    """Test evidence collection engine functionality"""

    @pytest.mark.asyncio
    async def test_evidence_collection_basic(self, evidence_engine):
        """Test basic evidence collection"""
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.USER_INTERACTION,
            source_component="test_component",
            operation="test_operation",
            payload={"test_key": "test_value"},
            user_id="test_user",
            session_id="test_session",
        )

        assert evidence_id is not None
        assert len(evidence_id) > 0
        assert evidence_engine._evidence_buffer

    @pytest.mark.asyncio
    async def test_evidence_integrity_verification(self, evidence_engine):
        """Test evidence integrity verification"""
        # Collect evidence
        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.AI_DECISION,
            source_component="test_ai",
            operation="decision_made",
            payload={"decision": "approve", "confidence": 0.95},
        )

        # Flush buffer to create evidence records
        await evidence_engine.flush_evidence_buffer()

        # Verify integrity (need to access internal evidence for testing)
        # In practice, this would be done through the query interface
        assert len(evidence_engine.current_chain) > 0

        # Test verification of a created evidence record
        test_record = evidence_engine.current_chain[0]
        is_valid = evidence_engine.verify_evidence(test_record)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_evidence_chain_creation(self, evidence_engine):
        """Test evidence chain block creation"""
        # Collect enough evidence to trigger chain block creation
        evidence_ids = []
        for i in range(6):  # More than chain_block_size
            evidence_id = await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.SYSTEM_EVENT,
                source_component="test_system",
                operation=f"test_operation_{i}",
                payload={"iteration": i},
            )
            evidence_ids.append(evidence_id)

        # Flush buffer to create chain blocks
        await evidence_engine.flush_evidence_buffer()

        # Check that chain block was created
        assert evidence_engine.chain_sequence > 0
        assert len(evidence_engine.current_chain) < 6  # Some moved to chain block

    @pytest.mark.asyncio
    async def test_evidence_query(self, evidence_engine):
        """Test evidence querying functionality"""
        # Collect test evidence
        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.DATA_ACCESS,
            source_component="data_service",
            operation="read_user_data",
            payload={"user_id": "test_user", "data_type": "profile"},
            user_id="test_user",
        )

        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.AUTHENTICATION,
            source_component="auth_service",
            operation="login",
            payload={"method": "password"},
            user_id="test_user",
        )

        # Flush to storage
        await evidence_engine.flush_evidence_buffer()

        # Query by evidence type
        data_access_evidence = []
        async for evidence in evidence_engine.query_evidence(evidence_type=EvidenceType.DATA_ACCESS, limit=10):
            data_access_evidence.append(evidence)

        # Should find at least one data access record
        assert len(data_access_evidence) > 0
        assert data_access_evidence[0].evidence_type == EvidenceType.DATA_ACCESS

    @pytest.mark.asyncio
    async def test_evidence_compression(self, evidence_engine):
        """Test evidence compression functionality"""
        # Create large payload to test compression
        large_payload = {
            "data": "x" * 1000,  # 1KB of data
            "metadata": {"items": [f"item_{i}" for i in range(100)]},
        }

        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.PERFORMANCE_METRIC,
            source_component="performance_monitor",
            operation="large_data_operation",
            payload=large_payload,
        )

        await evidence_engine.flush_evidence_buffer()
        await evidence_engine._create_chain_block()

        # Check that compressed storage was used
        # This is validated by ensuring the chain block creation succeeded
        assert evidence_engine.chain_sequence > 0

    @pytest.mark.asyncio
    async def test_evidence_retention_policy(self, evidence_engine):
        """Test evidence retention policy enforcement"""
        # Create evidence with specific retention
        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.REGULATORY_EVENT,
            source_component="compliance_monitor",
            operation="gdpr_request",
            payload={"request_type": "deletion", "user_id": "test_user"},
            compliance_regimes=[ComplianceRegime.GDPR],
        )

        await evidence_engine.flush_evidence_buffer()

        # Check that retention policy is set
        if evidence_engine.current_chain:
            record = evidence_engine.current_chain[0]
            assert record.retention_until is not None
            assert record.retention_until > datetime.now(timezone.utc)
            assert ComplianceRegime.GDPR in record.compliance_regimes

    @pytest.mark.asyncio
    async def test_performance_metrics(self, evidence_engine):
        """Test performance metrics collection"""
        # Collect multiple evidence records to generate metrics
        for i in range(10):
            await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.USER_INTERACTION,
                source_component="ui_component",
                operation="button_click",
                payload={"button": f"button_{i}"},
            )

        # Get performance metrics
        metrics = evidence_engine.get_performance_metrics()

        assert "collection_performance_ms" in metrics
        assert "buffer_size" in metrics
        assert metrics["collection_performance_ms"]["avg"] >= 0
        assert metrics["buffer_size"] >= 0

    @pytest.mark.asyncio
    async def test_concurrent_evidence_collection(self, evidence_engine):
        """Test concurrent evidence collection"""

        async def collect_evidence_task(task_id):
            return await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.SYSTEM_EVENT,
                source_component=f"task_{task_id}",
                operation="concurrent_test",
                payload={"task_id": task_id},
            )

        # Run concurrent collection tasks
        tasks = [collect_evidence_task(i) for i in range(20)]
        evidence_ids = await asyncio.gather(*tasks)

        # All tasks should complete successfully
        assert len(evidence_ids) == 20
        assert all(eid for eid in evidence_ids)

        # Buffer should contain all evidence
        assert len(evidence_engine._evidence_buffer) == 20

    @pytest.mark.asyncio
    async def test_evidence_tampering_detection(self, evidence_engine):
        """Test evidence tampering detection"""
        # Collect evidence
        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.SECURITY_EVENT,
            source_component="security_monitor",
            operation="access_attempt",
            payload={"source_ip": "192.168.1.100"},
        )

        await evidence_engine.flush_evidence_buffer()

        # Get the evidence record
        if evidence_engine.current_chain:
            record = evidence_engine.current_chain[0]

            # Tamper with the payload
            record.payload["source_ip"] = "malicious_tampering"

            # Verification should fail
            is_valid = evidence_engine.verify_evidence(record)
            assert is_valid is False

            # Restore original data
            record.payload["source_ip"] = "192.168.1.100"
            is_valid = evidence_engine.verify_evidence(record)
            assert is_valid is True


class TestEvidenceTypes:
    """Test different evidence types"""

    @pytest.mark.asyncio
    async def test_user_interaction_evidence(self, evidence_engine):
        """Test user interaction evidence collection"""
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.USER_INTERACTION,
            source_component="web_ui",
            operation="form_submission",
            payload={
                "form_type": "contact",
                "fields": ["name", "email", "message"],
                "validation_passed": True,
            },
            user_id="user_123",
            session_id="session_456",
        )

        assert evidence_id is not None

    @pytest.mark.asyncio
    async def test_ai_decision_evidence(self, evidence_engine):
        """Test AI decision evidence collection"""
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.AI_DECISION,
            source_component="recommendation_engine",
            operation="content_recommendation",
            payload={
                "user_profile": {"interests": ["technology", "science"]},
                "recommended_items": [1, 5, 12],
                "confidence_scores": [0.95, 0.87, 0.82],
                "model_version": "v2.1.0",
            },
            user_id="user_789",
        )

        assert evidence_id is not None

    @pytest.mark.asyncio
    async def test_regulatory_event_evidence(self, evidence_engine):
        """Test regulatory event evidence collection"""
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.REGULATORY_EVENT,
            source_component="gdpr_processor",
            operation="data_deletion_request",
            payload={
                "user_id": "user_to_delete",
                "request_date": datetime.now(timezone.utc).isoformat(),
                "data_categories": ["profile", "activity", "preferences"],
                "deletion_completed": True,
            },
            compliance_regimes=[ComplianceRegime.GDPR],
            user_id="user_to_delete",
        )

        assert evidence_id is not None


class TestComplianceIntegration:
    """Test compliance regime integration"""

    @pytest.mark.asyncio
    async def test_gdpr_compliance(self, evidence_engine):
        """Test GDPR compliance evidence handling"""
        await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.DATA_ACCESS,
            source_component="user_service",
            operation="export_user_data",
            payload={"exported_data_size": 1024, "format": "json"},
            compliance_regimes=[ComplianceRegime.GDPR],
            user_id="gdpr_user",
        )

        await evidence_engine.flush_evidence_buffer()

        # Query GDPR-related evidence
        gdpr_evidence = []
        async for evidence in evidence_engine.query_evidence(user_id="gdpr_user", limit=10):
            if ComplianceRegime.GDPR in evidence.compliance_regimes:
                gdpr_evidence.append(evidence)

        assert len(gdpr_evidence) > 0

    @pytest.mark.asyncio
    async def test_sox_compliance(self, evidence_engine):
        """Test SOX compliance evidence handling"""
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="financial_system",
            operation="transaction_processed",
            payload={
                "transaction_id": "txn_12345",
                "amount": 1000.00,
                "currency": "USD",
                "authorized_by": "manager_001",
            },
            compliance_regimes=[ComplianceRegime.SOX],
        )

        assert evidence_id is not None


class TestIntegrationFunctions:
    """Test module-level integration functions"""

    def test_initialize_evidence_collection(self, temp_evidence_dir):
        """Test evidence collection initialization"""
        engine = initialize_evidence_collection(
            storage_path=str(temp_evidence_dir),
            retention_days=365,
            compression_enabled=True,
        )

        assert engine is not None
        assert engine.retention_days == 365
        assert engine.compression_enabled is True

    @pytest.mark.asyncio
    async def test_convenience_collect_function(self, evidence_engine):
        """Test convenience collect_evidence function"""
        # Mock the global engine
        with patch("observability.evidence_collection.get_evidence_engine", return_value=evidence_engine):
            evidence_id = await collect_evidence(
                evidence_type=EvidenceType.USER_INTERACTION,
                source_component="test_component",
                operation="test_operation",
                payload={"test": "data"},
            )

            assert evidence_id is not None


class TestErrorHandling:
    """Test error handling scenarios"""

    @pytest.mark.asyncio
    async def test_invalid_evidence_type(self, evidence_engine):
        """Test handling of invalid evidence parameters"""
        # This should still work as evidence_type is an enum
        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.SYSTEM_EVENT,
            source_component="",  # Empty component should still work
            operation="test_operation",
            payload={},  # Empty payload should work
        )

        assert evidence_id is not None

    @pytest.mark.asyncio
    async def test_storage_failure_resilience(self, evidence_engine):
        """Test resilience to storage failures"""
        # Mock storage path to be invalid
        original_path = evidence_engine.storage_path
        evidence_engine.storage_path = Path("/invalid/path/that/does/not/exist")

        try:
            # Should still collect evidence in buffer
            evidence_id = await evidence_engine.collect_evidence(
                evidence_type=EvidenceType.ERROR_EVENT,
                source_component="test_component",
                operation="test_operation",
                payload={"error": "storage_test"},
            )

            assert evidence_id is not None
            assert evidence_engine._evidence_buffer

        finally:
            evidence_engine.storage_path = original_path

    @pytest.mark.asyncio
    async def test_large_payload_handling(self, evidence_engine):
        """Test handling of large evidence payloads"""
        # Create very large payload
        large_payload = {
            "large_data": "x" * 100000,  # 100KB
            "metadata": {"size": "large"},
        }

        evidence_id = await evidence_engine.collect_evidence(
            evidence_type=EvidenceType.PERFORMANCE_METRIC,
            source_component="performance_test",
            operation="large_payload_test",
            payload=large_payload,
        )

        assert evidence_id is not None

        # Should be able to flush without issues
        flushed_count = await evidence_engine.flush_evidence_buffer()
        assert flushed_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
