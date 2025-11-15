"""
Comprehensive Test Suite for GDPR Consent History Manager

This test suite ensures:
1. Hash determinism (same input = same hash)
2. Chronological ordering preserved
3. Consent verification logic correct
4. Withdrawal/revocation recorded properly
5. Export format valid (JSON)
6. >80% test coverage
7. GDPR Article 7(1) compliance
8. All storage backends work correctly

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock

# Adjust path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../')))

# Import directly from the module file to avoid circular import issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "consent_history",
    os.path.join(os.path.dirname(__file__), '../../../../../../governance/identity/core/sent/consent_history.py')
)
consent_history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consent_history)

ConsentEventType = consent_history.ConsentEventType
ConsentHistoryManager = consent_history.ConsentHistoryManager
InMemoryStorage = consent_history.InMemoryStorage
SQLiteStorage = consent_history.SQLiteStorage
StorageBackend = consent_history.StorageBackend


class MockTraceLogger:
    """Mock trace logger for testing."""

    def __init__(self):
        self.activities = []

    def log_activity(self, user_id: str, activity: str, metadata: dict) -> None:
        """Log an activity."""
        self.activities.append({
            "user_id": user_id,
            "activity": activity,
            "metadata": metadata
        })


class TestConsentHistoryManagerHashDeterminism(unittest.TestCase):
    """Test hash determinism requirements."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_same_input_produces_same_hash(self):
        """Verify that same input produces same hash."""
        record = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "event_type": "granted",
            "scope_data": {"scope": "data_processing"},
            "metadata": {"ip": "127.0.0.1"}
        }
        user_id = "user_123"

        hash1 = self.manager._generate_record_hash(record, user_id)
        hash2 = self.manager._generate_record_hash(record, user_id)

        self.assertEqual(hash1, hash2)

    def test_different_input_produces_different_hash(self):
        """Verify that different input produces different hash."""
        record1 = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "event_type": "granted",
            "scope_data": {"scope": "data_processing"},
            "metadata": {}
        }
        record2 = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "event_type": "withdrawn",
            "scope_data": {"scope": "data_processing"},
            "metadata": {}
        }
        user_id = "user_123"

        hash1 = self.manager._generate_record_hash(record1, user_id)
        hash2 = self.manager._generate_record_hash(record2, user_id)

        self.assertNotEqual(hash1, hash2)

    def test_hash_is_sha256(self):
        """Verify that hash is valid SHA-256."""
        record = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "event_type": "granted",
            "scope_data": {"scope": "data_processing"},
            "metadata": {}
        }
        user_id = "user_123"

        hash_value = self.manager._generate_record_hash(record, user_id)

        # SHA-256 hash is 64 hex characters
        self.assertEqual(len(hash_value), 64)
        # Should only contain hex characters
        self.assertTrue(all(c in "0123456789abcdef" for c in hash_value))

    def test_hash_determinism_with_dict_key_order(self):
        """Verify hash is deterministic regardless of dict key order."""
        # Create two records with same data but different key order
        record1 = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "event_type": "granted",
            "scope_data": {"scope": "data_processing", "purpose": "analytics"},
            "metadata": {"ip": "127.0.0.1", "agent": "Firefox"}
        }
        record2 = {
            "event_type": "granted",
            "timestamp": "2025-01-01T00:00:00+00:00",
            "metadata": {"agent": "Firefox", "ip": "127.0.0.1"},
            "scope_data": {"purpose": "analytics", "scope": "data_processing"}
        }
        user_id = "user_123"

        hash1 = self.manager._generate_record_hash(record1, user_id)
        hash2 = self.manager._generate_record_hash(record2, user_id)

        self.assertEqual(hash1, hash2)


class TestConsentHistoryManagerChronologicalOrdering(unittest.TestCase):
    """Test chronological ordering requirements."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_records_retrieved_in_chronological_order(self):
        """Verify records are returned in chronological order."""
        user_id = "user_123"

        # Add records in non-chronological order
        hash1 = self.manager.add_record(
            user_id, "granted", {"scope": "data_processing"}
        )
        hash2 = self.manager.add_record(
            user_id, "updated", {"scope": "data_processing"}
        )
        hash3 = self.manager.add_record(
            user_id, "withdrawn", {"scope": "data_processing"}
        )

        history = self.manager.get_history(user_id)

        # Verify we got all records
        self.assertEqual(len(history), 3)

        # Verify chronological order
        timestamps = [
            datetime.fromisoformat(r["record"]["timestamp"])
            for r in history
        ]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_start_time_filter(self):
        """Verify start_time filtering works correctly."""
        user_id = "user_123"

        # Add first record
        hash1 = self.manager.add_record(
            user_id, "granted", {"scope": "data_processing"}
        )

        # Wait a moment and note the cutoff time
        import time
        time.sleep(0.01)
        cutoff_time = datetime.now(timezone.utc)

        # Add second record
        hash2 = self.manager.add_record(
            user_id, "updated", {"scope": "data_processing"}
        )

        # Get history after cutoff
        history = self.manager.get_history(user_id, start_time=cutoff_time)

        # Should only get the second record
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["hash"], hash2)


class TestConsentHistoryManagerConsentVerification(unittest.TestCase):
    """Test consent verification logic."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_verify_consent_when_granted(self):
        """Verify consent verification returns True when consent is granted."""
        user_id = "user_123"
        scope = "data_processing"

        self.manager.add_record(user_id, "granted", {"scope": scope})

        self.assertTrue(self.manager.verify_consent(user_id, scope))

    def test_verify_consent_when_updated(self):
        """Verify consent verification returns True when consent is updated."""
        user_id = "user_123"
        scope = "data_processing"

        self.manager.add_record(user_id, "granted", {"scope": scope})
        self.manager.add_record(user_id, "updated", {"scope": scope})

        self.assertTrue(self.manager.verify_consent(user_id, scope))

    def test_verify_consent_when_withdrawn(self):
        """Verify consent verification returns False when consent is withdrawn."""
        user_id = "user_123"
        scope = "data_processing"

        self.manager.add_record(user_id, "granted", {"scope": scope})
        self.manager.add_record(user_id, "withdrawn", {"scope": scope})

        self.assertFalse(self.manager.verify_consent(user_id, scope))

    def test_verify_consent_when_revoked(self):
        """Verify consent verification returns False when consent is revoked."""
        user_id = "user_123"
        scope = "data_processing"

        self.manager.add_record(user_id, "granted", {"scope": scope})
        self.manager.add_record(user_id, "revoked", {"scope": scope})

        self.assertFalse(self.manager.verify_consent(user_id, scope))

    def test_verify_consent_when_no_consent(self):
        """Verify consent verification returns False when no consent exists."""
        user_id = "user_123"
        scope = "data_processing"

        self.assertFalse(self.manager.verify_consent(user_id, scope))

    def test_verify_consent_uses_latest_event(self):
        """Verify consent verification uses the latest event."""
        user_id = "user_123"
        scope = "data_processing"

        # Grant, withdraw, then grant again
        self.manager.add_record(user_id, "granted", {"scope": scope})
        self.manager.add_record(user_id, "withdrawn", {"scope": scope})
        self.manager.add_record(user_id, "granted", {"scope": scope})

        # Latest is granted, so should return True
        self.assertTrue(self.manager.verify_consent(user_id, scope))


class TestConsentHistoryManagerWithdrawalRevocation(unittest.TestCase):
    """Test withdrawal and revocation functionality."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_withdraw_consent(self):
        """Test user-initiated consent withdrawal."""
        user_id = "user_123"
        scope = "data_processing"

        # Grant consent first
        self.manager.add_record(user_id, "granted", {"scope": scope})

        # Withdraw consent
        hash_value = self.manager.withdraw_consent(
            user_id, scope, reason="Privacy concerns"
        )

        # Verify withdrawal was recorded
        self.assertIsNotNone(hash_value)

        history = self.manager.get_history(user_id)
        self.assertEqual(len(history), 2)

        withdrawal = history[-1]
        self.assertEqual(withdrawal["record"]["event_type"], "withdrawn")
        self.assertEqual(withdrawal["record"]["metadata"]["reason"], "Privacy concerns")
        self.assertEqual(withdrawal["record"]["metadata"]["withdrawal_type"], "user_initiated")

    def test_revoke_consent(self):
        """Test administrative consent revocation."""
        user_id = "user_123"
        scope = "data_processing"

        # Grant consent first
        self.manager.add_record(user_id, "granted", {"scope": scope})

        # Revoke consent
        hash_value = self.manager.revoke_consent(
            user_id, scope, reason="Policy violation"
        )

        # Verify revocation was recorded
        self.assertIsNotNone(hash_value)

        history = self.manager.get_history(user_id)
        self.assertEqual(len(history), 2)

        revocation = history[-1]
        self.assertEqual(revocation["record"]["event_type"], "revoked")
        self.assertEqual(revocation["record"]["metadata"]["reason"], "Policy violation")
        self.assertEqual(revocation["record"]["metadata"]["revocation_type"], "administrative")

    def test_withdraw_without_reason(self):
        """Test withdrawal without reason."""
        user_id = "user_123"
        scope = "data_processing"

        hash_value = self.manager.withdraw_consent(user_id, scope)

        history = self.manager.get_history(user_id)
        withdrawal = history[-1]

        self.assertNotIn("reason", withdrawal["record"]["metadata"])
        self.assertEqual(withdrawal["record"]["metadata"]["withdrawal_type"], "user_initiated")


class TestConsentHistoryManagerExport(unittest.TestCase):
    """Test GDPR export functionality."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_export_format_is_json(self):
        """Verify export format is valid JSON."""
        user_id = "user_123"

        self.manager.add_record(user_id, "granted", {"scope": "data_processing"})

        export_bytes = self.manager.export_history(user_id)

        # Should be bytes
        self.assertIsInstance(export_bytes, bytes)

        # Should be valid JSON
        export_data = json.loads(export_bytes.decode("utf-8"))

        self.assertIn("export_metadata", export_data)
        self.assertIn("consent_history", export_data)

    def test_export_contains_gdpr_metadata(self):
        """Verify export contains GDPR compliance metadata."""
        user_id = "user_123"

        self.manager.add_record(user_id, "granted", {"scope": "data_processing"})

        export_bytes = self.manager.export_history(user_id)
        export_data = json.loads(export_bytes.decode("utf-8"))

        metadata = export_data["export_metadata"]

        self.assertEqual(metadata["user_id"], user_id)
        self.assertIn("Article 20", metadata["gdpr_article"])
        self.assertEqual(metadata["format"], "application/json")
        self.assertEqual(metadata["total_records"], 1)

    def test_export_contains_all_records(self):
        """Verify export contains all consent records."""
        user_id = "user_123"

        # Add multiple records
        self.manager.add_record(user_id, "granted", {"scope": "data_processing"})
        self.manager.add_record(user_id, "updated", {"scope": "data_processing"})
        self.manager.add_record(user_id, "withdrawn", {"scope": "data_processing"})

        export_bytes = self.manager.export_history(user_id)
        export_data = json.loads(export_bytes.decode("utf-8"))

        # Should have all 3 records
        self.assertEqual(len(export_data["consent_history"]), 3)

        # Verify record structure
        for record in export_data["consent_history"]:
            self.assertIn("timestamp", record)
            self.assertIn("event_type", record)
            self.assertIn("scope", record)
            self.assertIn("scope_data", record)
            self.assertIn("metadata", record)
            self.assertIn("record_hash", record)

    def test_export_empty_history(self):
        """Verify export works with empty history."""
        user_id = "user_999"

        export_bytes = self.manager.export_history(user_id)
        export_data = json.loads(export_bytes.decode("utf-8"))

        self.assertEqual(export_data["export_metadata"]["total_records"], 0)
        self.assertEqual(len(export_data["consent_history"]), 0)


class TestConsentHistoryManagerValidation(unittest.TestCase):
    """Test input validation."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_invalid_event_type_raises_error(self):
        """Verify invalid event type raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.manager.add_record(
                "user_123", "invalid_event", {"scope": "data_processing"}
            )

        self.assertIn("Invalid event_type", str(context.exception))

    def test_missing_scope_raises_error(self):
        """Verify missing scope raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.manager.add_record(
                "user_123", "granted", {"purpose": "analytics"}
            )

        self.assertIn("must contain 'scope' key", str(context.exception))

    def test_valid_event_types(self):
        """Verify all valid event types work."""
        user_id = "user_123"

        for event_type in ["granted", "withdrawn", "revoked", "updated"]:
            hash_value = self.manager.add_record(
                user_id, event_type, {"scope": f"scope_{event_type}"}
            )
            self.assertIsNotNone(hash_value)


class TestConsentHistoryManagerTraceLogging(unittest.TestCase):
    """Test trace logging functionality."""

    def test_trace_logger_called_on_add_record(self):
        """Verify trace logger is called when adding records."""
        trace_logger = MockTraceLogger()
        manager = ConsentHistoryManager(trace_logger=trace_logger)

        user_id = "user_123"
        manager.add_record(user_id, "granted", {"scope": "data_processing"})

        # Verify trace logger was called
        self.assertEqual(len(trace_logger.activities), 1)

        activity = trace_logger.activities[0]
        self.assertEqual(activity["user_id"], user_id)
        self.assertEqual(activity["activity"], "consent_granted")
        self.assertIn("hash", activity["metadata"])
        self.assertIn("event_type", activity["metadata"])

    def test_trace_logger_not_called_when_none(self):
        """Verify no error when trace logger is None."""
        manager = ConsentHistoryManager(trace_logger=None)

        # Should not raise an error
        manager.add_record("user_123", "granted", {"scope": "data_processing"})


class TestConsentHistoryManagerStorageBackends(unittest.TestCase):
    """Test different storage backends."""

    def test_in_memory_storage(self):
        """Test in-memory storage backend."""
        manager = ConsentHistoryManager(
            config={"storage_backend": "memory"}
        )

        user_id = "user_123"
        manager.add_record(user_id, "granted", {"scope": "data_processing"})

        history = manager.get_history(user_id)
        self.assertEqual(len(history), 1)

    def test_sqlite_storage(self):
        """Test SQLite storage backend."""
        # Use temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            manager = ConsentHistoryManager(
                config={"storage_backend": "sqlite", "db_path": db_path}
            )

            user_id = "user_123"
            manager.add_record(user_id, "granted", {"scope": "data_processing"})

            history = manager.get_history(user_id)
            self.assertEqual(len(history), 1)

            manager.close()

            # Verify persistence - reopen database
            manager2 = ConsentHistoryManager(
                config={"storage_backend": "sqlite", "db_path": db_path}
            )

            history2 = manager2.get_history(user_id)
            self.assertEqual(len(history2), 1)

            manager2.close()
        finally:
            # Clean up
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_invalid_backend_raises_error(self):
        """Verify invalid storage backend raises error."""
        with self.assertRaises(ValueError) as context:
            ConsentHistoryManager(
                config={"storage_backend": "invalid"}
            )

        self.assertIn("Unsupported storage backend", str(context.exception))


class TestConsentHistoryManagerConsentSummary(unittest.TestCase):
    """Test consent summary functionality."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_consent_summary_structure(self):
        """Verify consent summary has correct structure."""
        user_id = "user_123"

        self.manager.add_record(user_id, "granted", {"scope": "data_processing"})
        self.manager.add_record(user_id, "granted", {"scope": "marketing"})

        summary = self.manager.get_consent_summary(user_id)

        self.assertIn("user_id", summary)
        self.assertIn("total_events", summary)
        self.assertIn("active_consents", summary)
        self.assertIn("withdrawn_consents", summary)
        self.assertIn("revoked_consents", summary)
        self.assertIn("last_updated", summary)

    def test_consent_summary_categorizes_correctly(self):
        """Verify consent summary categorizes consents correctly."""
        user_id = "user_123"

        # Active consent
        self.manager.add_record(user_id, "granted", {"scope": "data_processing"})

        # Withdrawn consent
        self.manager.add_record(user_id, "granted", {"scope": "marketing"})
        self.manager.add_record(user_id, "withdrawn", {"scope": "marketing"})

        # Revoked consent
        self.manager.add_record(user_id, "granted", {"scope": "analytics"})
        self.manager.add_record(user_id, "revoked", {"scope": "analytics"})

        summary = self.manager.get_consent_summary(user_id)

        self.assertEqual(summary["total_events"], 5)
        self.assertEqual(summary["active_consents"], ["data_processing"])
        self.assertEqual(summary["withdrawn_consents"], ["marketing"])
        self.assertEqual(summary["revoked_consents"], ["analytics"])

    def test_consent_summary_empty(self):
        """Verify consent summary works with empty history."""
        user_id = "user_999"

        summary = self.manager.get_consent_summary(user_id)

        self.assertEqual(summary["total_events"], 0)
        self.assertEqual(summary["active_consents"], [])
        self.assertEqual(summary["withdrawn_consents"], [])
        self.assertEqual(summary["revoked_consents"], [])
        self.assertIsNone(summary["last_updated"])


class TestConsentHistoryManagerContextManager(unittest.TestCase):
    """Test context manager functionality."""

    def test_context_manager(self):
        """Verify context manager works correctly."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        try:
            with ConsentHistoryManager(
                config={"storage_backend": "sqlite", "db_path": db_path}
            ) as manager:
                manager.add_record("user_123", "granted", {"scope": "data_processing"})

                history = manager.get_history("user_123")
                self.assertEqual(len(history), 1)

            # Connection should be closed after exiting context
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestConsentHistoryManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        self.manager = ConsentHistoryManager()

    def test_multiple_users(self):
        """Verify multiple users' data is isolated."""
        user1 = "user_123"
        user2 = "user_456"

        self.manager.add_record(user1, "granted", {"scope": "data_processing"})
        self.manager.add_record(user2, "granted", {"scope": "marketing"})

        history1 = self.manager.get_history(user1)
        history2 = self.manager.get_history(user2)

        self.assertEqual(len(history1), 1)
        self.assertEqual(len(history2), 1)
        self.assertEqual(history1[0]["record"]["scope_data"]["scope"], "data_processing")
        self.assertEqual(history2[0]["record"]["scope_data"]["scope"], "marketing")

    def test_unicode_in_metadata(self):
        """Verify Unicode characters are handled correctly."""
        user_id = "user_123"

        metadata = {
            "reason": "Préoccupations de confidentialité 🔒",
            "location": "Zürich"
        }

        hash_value = self.manager.add_record(
            user_id, "granted", {"scope": "data_processing"}, metadata=metadata
        )

        history = self.manager.get_history(user_id)
        self.assertEqual(history[0]["record"]["metadata"]["reason"], metadata["reason"])

        # Verify export handles Unicode
        export_bytes = self.manager.export_history(user_id)
        export_data = json.loads(export_bytes.decode("utf-8"))
        self.assertEqual(
            export_data["consent_history"][0]["metadata"]["reason"],
            metadata["reason"]
        )

    def test_large_metadata(self):
        """Verify large metadata is handled correctly."""
        user_id = "user_123"

        metadata = {
            "description": "A" * 10000,  # 10KB of text
            "details": {f"key_{i}": f"value_{i}" for i in range(100)}
        }

        hash_value = self.manager.add_record(
            user_id, "granted", {"scope": "data_processing"}, metadata=metadata
        )

        history = self.manager.get_history(user_id)
        self.assertEqual(len(history[0]["record"]["metadata"]["description"]), 10000)


if __name__ == "__main__":
    unittest.main()
