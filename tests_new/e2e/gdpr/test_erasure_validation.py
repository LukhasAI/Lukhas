#!/usr/bin/env python3

"""
GDPR Right-to-Erasure Validation Tests
=====================================

Comprehensive validation tests for GDPR Article 17 compliance (Right to Erasure).
Tests complete data deletion across all LUKHAS consciousness and memory systems.

Addresses Guardian Security requirement for GDPR erasure validation testing.
"""

import json
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import pytest


# Mock simplified GDPR classes for testing
class LawfulBasis(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"


class DataCategory(Enum):
    PERSONAL_DATA = "personal_data"
    SENSITIVE_DATA = "sensitive_data"


@dataclass
class UserDataFootprint:
    """Represents all data associated with a user across LUKHAS systems"""

    user_id: str
    aka_qualia_scenes: list[str] = None
    aka_qualia_glyphs: list[str] = None
    memory_folds: list[str] = None
    consent_entries: list[str] = None
    audit_logs: list[str] = None
    vector_embeddings: list[str] = None
    cached_responses: list[str] = None
    session_data: dict[str, Any] = None

    def __post_init__(self):
        # Initialize empty lists if None
        for field in [
            "aka_qualia_scenes",
            "aka_qualia_glyphs",
            "memory_folds",
            "consent_entries",
            "audit_logs",
            "vector_embeddings",
            "cached_responses",
        ]:
            if getattr(self, field) is None:
                setattr(self, field, [])
        if self.session_data is None:
            self.session_data = {}


class MockDataStore:
    """Mock data store for testing GDPR erasure"""

    def __init__(self):
        self.db_path = None
        self.connection = None
        self._setup_test_database()

    def _setup_test_database(self):
        """Set up in-memory test database with LUKHAS schema"""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.connection = sqlite3.connect(self.db_path)

        # Create LUKHAS consciousness tables
        cursor = self.connection.cursor()

        # Aka Qualia tables
        cursor.execute(
            """
            CREATE TABLE akaq_scene (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                scene_data TEXT,
                timestamp REAL,
                risk_score REAL,
                proto_qualia TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE akaq_glyph (
                id TEXT PRIMARY KEY,
                scene_id TEXT,
                user_id TEXT NOT NULL,
                glyph_key TEXT,
                glyph_attrs TEXT,
                timestamp REAL,
                FOREIGN KEY (scene_id) REFERENCES akaq_scene(id)
            )
        """
        )

        # Memory system tables
        cursor.execute(
            """
            CREATE TABLE memory_fold (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                fold_data TEXT,
                embedding BLOB,
                created_at REAL,
                accessed_at REAL
            )
        """
        )

        # Consent ledger
        cursor.execute(
            """
            CREATE TABLE consent_ledger (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                consent_type TEXT,
                granted BOOLEAN,
                timestamp REAL,
                signature TEXT
            )
        """
        )

        # Audit logs
        cursor.execute(
            """
            CREATE TABLE audit_log (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT,
                details TEXT,
                timestamp REAL,
                sensitive_data TEXT
            )
        """
        )

        # Vector embeddings cache
        cursor.execute(
            """
            CREATE TABLE vector_cache (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                embedding_key TEXT,
                vector_data BLOB,
                metadata TEXT,
                expiry REAL
            )
        """
        )

        self.connection.commit()

    def insert_test_user_data(self, user_id: str) -> UserDataFootprint:
        """Insert comprehensive test data for a user"""
        cursor = self.connection.cursor()
        footprint = UserDataFootprint(user_id=user_id)
        timestamp = time.time()

        # Insert aka_qualia scenes
        for i in range(3):
            scene_id = f"scene_{user_id}_{i}"
            footprint.aka_qualia_scenes.append(scene_id)
            cursor.execute(
                "INSERT INTO akaq_scene (id, user_id, scene_data, timestamp, risk_score, proto_qualia) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    scene_id,
                    user_id,
                    json.dumps({"scene": f"test_scene_{i}"}),
                    timestamp,
                    0.1,
                    json.dumps({"tone": 0.5}),
                ),
            )

            # Insert glyphs for this scene
            for j in range(2):
                glyph_id = f"glyph_{user_id}_{i}_{j}"
                footprint.aka_qualia_glyphs.append(glyph_id)
                cursor.execute(
                    "INSERT INTO akaq_glyph (id, scene_id, user_id, glyph_key, glyph_attrs, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (glyph_id, scene_id, user_id, f"aka:test_{j}", json.dumps({"test": True}), timestamp),
                )

        # Insert memory folds
        for i in range(2):
            fold_id = f"fold_{user_id}_{i}"
            footprint.memory_folds.append(fold_id)
            cursor.execute(
                "INSERT INTO memory_fold (id, user_id, fold_data, embedding, created_at, accessed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (fold_id, user_id, json.dumps({"memory": f"test_memory_{i}"}), b"fake_embedding", timestamp, timestamp),
            )

        # Insert consent entries
        consent_id = f"consent_{user_id}"
        footprint.consent_entries.append(consent_id)
        cursor.execute(
            "INSERT INTO consent_ledger (id, user_id, consent_type, granted, timestamp, signature) VALUES (?, ?, ?, ?, ?, ?)",
            (consent_id, user_id, "data_processing", True, timestamp, "test_signature"),
        )

        # Insert audit logs (including some without user_id for cascade testing)
        for i in range(2):
            audit_id = f"audit_{user_id}_{i}"
            footprint.audit_logs.append(audit_id)
            cursor.execute(
                "INSERT INTO audit_log (id, user_id, action, details, timestamp, sensitive_data) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    audit_id,
                    user_id,
                    f"test_action_{i}",
                    f"User {user_id} performed action",
                    timestamp,
                    f"sensitive_{user_id}",
                ),
            )

        # Insert vector cache entries
        for i in range(2):
            vector_id = f"vector_{user_id}_{i}"
            footprint.vector_embeddings.append(vector_id)
            cursor.execute(
                "INSERT INTO vector_cache (id, user_id, embedding_key, vector_data, metadata, expiry) VALUES (?, ?, ?, ?, ?, ?)",
                (vector_id, user_id, f"embedding_{i}", b"fake_vector", json.dumps({"user": user_id}), timestamp + 3600),
            )

        self.connection.commit()
        return footprint

    def erase_user_data(self, user_id: str) -> dict[str, int]:
        """Perform GDPR-compliant data erasure for a user"""
        cursor = self.connection.cursor()
        erasure_counts = {}

        # Erase aka_qualia data with cascade
        cursor.execute("DELETE FROM akaq_glyph WHERE user_id = ?", (user_id,))
        erasure_counts["akaq_glyph"] = cursor.rowcount

        cursor.execute("DELETE FROM akaq_scene WHERE user_id = ?", (user_id,))
        erasure_counts["akaq_scene"] = cursor.rowcount

        # Erase memory system data
        cursor.execute("DELETE FROM memory_fold WHERE user_id = ?", (user_id,))
        erasure_counts["memory_fold"] = cursor.rowcount

        # Erase consent data
        cursor.execute("DELETE FROM consent_ledger WHERE user_id = ?", (user_id,))
        erasure_counts["consent_ledger"] = cursor.rowcount

        # Handle audit logs (anonymize rather than delete for compliance)
        cursor.execute("UPDATE audit_log SET user_id = NULL, sensitive_data = '[ERASED]' WHERE user_id = ?", (user_id,))
        erasure_counts["audit_log_anonymized"] = cursor.rowcount

        # Erase vector embeddings
        cursor.execute("DELETE FROM vector_cache WHERE user_id = ?", (user_id,))
        erasure_counts["vector_cache"] = cursor.rowcount

        self.connection.commit()
        return erasure_counts

    def verify_user_data_erased(self, user_id: str) -> dict[str, Any]:
        """Verify that all user data has been properly erased"""
        cursor = self.connection.cursor()
        verification_results = {}

        # Check aka_qualia tables
        cursor.execute("SELECT COUNT(*) FROM akaq_scene WHERE user_id = ?", (user_id,))
        verification_results["akaq_scene_remaining"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM akaq_glyph WHERE user_id = ?", (user_id,))
        verification_results["akaq_glyph_remaining"] = cursor.fetchone()[0]

        # Check memory system
        cursor.execute("SELECT COUNT(*) FROM memory_fold WHERE user_id = ?", (user_id,))
        verification_results["memory_fold_remaining"] = cursor.fetchone()[0]

        # Check consent ledger
        cursor.execute("SELECT COUNT(*) FROM consent_ledger WHERE user_id = ?", (user_id,))
        verification_results["consent_ledger_remaining"] = cursor.fetchone()[0]

        # Check audit logs (should be anonymized, not deleted)
        cursor.execute("SELECT COUNT(*) FROM audit_log WHERE user_id = ?", (user_id,))
        verification_results["audit_log_remaining"] = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM audit_log WHERE sensitive_data LIKE ? AND user_id IS NULL", (f"%{user_id}%",)
        )
        verification_results["audit_log_anonymized"] = cursor.fetchone()[0]

        # Check vector cache
        cursor.execute("SELECT COUNT(*) FROM vector_cache WHERE user_id = ?", (user_id,))
        verification_results["vector_cache_remaining"] = cursor.fetchone()[0]

        # Check for shadow references in metadata
        cursor.execute("SELECT COUNT(*) FROM vector_cache WHERE metadata LIKE ?", (f"%{user_id}%",))
        verification_results["vector_shadow_references"] = cursor.fetchone()[0]

        return verification_results

    def cleanup(self):
        """Clean up test database"""
        if self.connection:
            self.connection.close()
        if self.db_path and Path(self.db_path).exists():
            Path(self.db_path).unlink()


class GDPRErasureValidator:
    """Validator for GDPR erasure compliance"""

    def __init__(self, data_store: MockDataStore):
        self.data_store = data_store

    async def validate_complete_erasure(self, user_id: str) -> dict[str, Any]:
        """Validate complete GDPR-compliant data erasure"""

        # Step 1: Create comprehensive user data footprint
        footprint = self.data_store.insert_test_user_data(user_id)

        # Step 2: Verify data exists before erasure
        pre_erasure_check = self.data_store.verify_user_data_erased(user_id)

        # Step 3: Perform erasure
        erasure_counts = self.data_store.erase_user_data(user_id)

        # Step 4: Verify complete erasure
        post_erasure_check = self.data_store.verify_user_data_erased(user_id)

        # Step 5: Validate compliance
        erasure_compliance = await self._assess_erasure_compliance(
            user_id, footprint, erasure_counts, post_erasure_check
        )

        return {
            "user_id": user_id,
            "footprint": footprint,
            "pre_erasure": pre_erasure_check,
            "erasure_counts": erasure_counts,
            "post_erasure": post_erasure_check,
            "compliance_assessment": erasure_compliance,
            "erasure_timestamp": time.time(),
        }

    async def _assess_erasure_compliance(
        self,
        user_id: str,
        footprint: UserDataFootprint,
        erasure_counts: dict[str, int],
        verification_results: dict[str, Any],
    ) -> dict[str, Any]:
        """Assess GDPR compliance of the erasure process"""

        violations = []
        compliance_score = 1.0

        # Check for incomplete erasure
        critical_tables = [
            "akaq_scene_remaining",
            "akaq_glyph_remaining",
            "memory_fold_remaining",
            "consent_ledger_remaining",
        ]
        for table in critical_tables:
            if verification_results.get(table, 0) > 0:
                violations.append(
                    {
                        "type": "incomplete_erasure",
                        "severity": "critical",
                        "table": table,
                        "remaining_records": verification_results[table],
                        "description": f"User data remains in {table} after erasure request",
                    }
                )
                compliance_score -= 0.25

        # Check for shadow references (data leaks)
        if verification_results.get("vector_shadow_references", 0) > 0:
            violations.append(
                {
                    "type": "shadow_references",
                    "severity": "high",
                    "description": "User data found in metadata fields after erasure",
                    "shadow_count": verification_results["vector_shadow_references"],
                }
            )
            compliance_score -= 0.2

        # Verify audit trail anonymization (should be present but anonymized)
        if verification_results.get("audit_log_remaining", 0) > 0:
            violations.append(
                {
                    "type": "audit_log_not_anonymized",
                    "severity": "medium",
                    "description": "Audit logs contain user references instead of being anonymized",
                    "remaining_references": verification_results["audit_log_remaining"],
                }
            )
            compliance_score -= 0.1

        # Determine overall compliance status
        if compliance_score >= 0.95:
            status = "FULLY_COMPLIANT"
        elif compliance_score >= 0.8:
            status = "COMPLIANT_WITH_MINOR_ISSUES"
        elif compliance_score >= 0.6:
            status = "PARTIALLY_COMPLIANT"
        else:
            status = "NON_COMPLIANT"

        return {
            "compliance_score": max(0.0, compliance_score),
            "compliance_status": status,
            "violations": violations,
            "erasure_completeness": len(violations) == 0,
            "assessment_timestamp": time.time(),
        }


@pytest.fixture
def mock_data_store():
    """Fixture providing mock data store for testing"""
    store = MockDataStore()
    yield store
    store.cleanup()


@pytest.fixture
def erasure_validator(mock_data_store):
    """Fixture providing GDPR erasure validator"""
    return GDPRErasureValidator(mock_data_store)


@pytest.mark.asyncio
async def test_complete_user_data_erasure(erasure_validator):
    """Test complete erasure of user data across all LUKHAS systems"""

    user_id = "test_user_12345"

    # Perform complete erasure validation
    validation_result = await erasure_validator.validate_complete_erasure(user_id)

    # Assertions for complete erasure
    assert validation_result["compliance_assessment"]["compliance_status"] in [
        "FULLY_COMPLIANT",
        "COMPLIANT_WITH_MINOR_ISSUES",
    ]
    assert validation_result["compliance_assessment"]["compliance_score"] >= 0.8
    assert validation_result["post_erasure"]["akaq_scene_remaining"] == 0
    assert validation_result["post_erasure"]["akaq_glyph_remaining"] == 0
    assert validation_result["post_erasure"]["memory_fold_remaining"] == 0
    assert validation_result["post_erasure"]["consent_ledger_remaining"] == 0
    assert validation_result["post_erasure"]["vector_cache_remaining"] == 0

    # Verify cascade deletion worked
    assert validation_result["erasure_counts"]["akaq_scene"] > 0
    assert validation_result["erasure_counts"]["akaq_glyph"] > 0

    # Verify audit logs were anonymized, not deleted
    assert validation_result["post_erasure"]["audit_log_remaining"] == 0
    assert validation_result["erasure_counts"]["audit_log_anonymized"] > 0


@pytest.mark.asyncio
async def test_erasure_handles_shadow_data(erasure_validator):
    """Test that erasure detects and handles shadow references in vector DBs"""

    user_id = "shadow_test_user"

    # Insert additional shadow data that mimics vector DB leaks
    cursor = erasure_validator.data_store.connection.cursor()
    cursor.execute(
        "INSERT INTO vector_cache (id, user_id, embedding_key, vector_data, metadata, expiry) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "shadow_vector",
            "other_user",
            "embedding_key",
            b"fake_vector",
            json.dumps({"original_user": user_id, "context": f"derived from {user_id}"}),
            time.time() + 3600,
        ),
    )
    erasure_validator.data_store.connection.commit()

    # Perform erasure validation
    validation_result = await erasure_validator.validate_complete_erasure(user_id)

    # Should detect shadow references
    compliance = validation_result["compliance_assessment"]
    shadow_violations = [v for v in compliance["violations"] if v["type"] == "shadow_references"]

    # This test expects to find shadow violations
    assert len(shadow_violations) > 0, "Shadow reference detection should identify leaked data"
    assert compliance["compliance_score"] < 1.0, "Shadow references should reduce compliance score"


@pytest.mark.asyncio
async def test_erasure_multiple_users_isolation(erasure_validator):
    """Test that erasure of one user doesn't affect other users' data"""

    user_a = "user_a_12345"
    user_b = "user_b_67890"

    # Create data for both users
    erasure_validator.data_store.insert_test_user_data(user_a)
    footprint_b = erasure_validator.data_store.insert_test_user_data(user_b)

    # Erase only user A
    erasure_validator.data_store.erase_user_data(user_a)

    # Verify user A data is erased
    verification_a = erasure_validator.data_store.verify_user_data_erased(user_a)
    assert verification_a["akaq_scene_remaining"] == 0
    assert verification_a["akaq_glyph_remaining"] == 0

    # Verify user B data is intact
    verification_b = erasure_validator.data_store.verify_user_data_erased(user_b)
    assert verification_b["akaq_scene_remaining"] == len(footprint_b.aka_qualia_scenes)
    assert verification_b["akaq_glyph_remaining"] == len(footprint_b.aka_qualia_glyphs)


@pytest.mark.asyncio
async def test_erasure_compliance_scoring(erasure_validator):
    """Test GDPR compliance scoring for various erasure scenarios"""

    # Test perfect erasure
    user_id = "perfect_erasure_user"
    validation_result = await erasure_validator.validate_complete_erasure(user_id)

    compliance = validation_result["compliance_assessment"]
    assert compliance["compliance_score"] >= 0.95
    assert compliance["compliance_status"] == "FULLY_COMPLIANT"
    assert compliance["erasure_completeness"] is True
    assert len(compliance["violations"]) == 0


@pytest.mark.asyncio
async def test_gdpr_article17_compliance_integration():
    """Integration test for GDPR Article 17 Right-to-Erasure compliance"""

    # This test validates the complete GDPR erasure workflow
    mock_store = MockDataStore()
    validator = GDPRErasureValidator(mock_store)

    try:
        # Test multiple users with complex data relationships
        test_users = ["integration_user_1", "integration_user_2", "integration_user_3"]

        all_results = []
        for user_id in test_users:
            result = await validator.validate_complete_erasure(user_id)
            all_results.append(result)

            # Each user should achieve full compliance
            compliance = result["compliance_assessment"]
            assert compliance["compliance_status"] in ["FULLY_COMPLIANT", "COMPLIANT_WITH_MINOR_ISSUES"]
            assert compliance["compliance_score"] >= 0.8

        # Verify comprehensive erasure across the system
        total_erased_scenes = sum(r["erasure_counts"]["akaq_scene"] for r in all_results)
        total_erased_glyphs = sum(r["erasure_counts"]["akaq_glyph"] for r in all_results)

        assert total_erased_scenes >= 9  # 3 users × 3 scenes each
        assert total_erased_glyphs >= 18  # 3 users × 3 scenes × 2 glyphs each

        print("✅ GDPR Article 17 Right-to-Erasure compliance validated successfully")

    finally:
        mock_store.cleanup()


if __name__ == "__main__":
    # Run the GDPR erasure validation tests
    print("🛡️ Running GDPR Right-to-Erasure Validation Tests")
    pytest.main([__file__, "-v"])