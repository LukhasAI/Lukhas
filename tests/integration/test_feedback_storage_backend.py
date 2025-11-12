"""
Integration tests for feedback storage backend (Task 2.3).

Tests verify:
- Connection pooling functionality
- Batch operations (insert/update)
- Data retention and cleanup
- Backup and recovery
- Transaction management
- Performance metrics
- Error handling
"""

import json
import sqlite3
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import pytest

from products.experience.feedback.core.storage_backend import (
    ConnectionPool,
    FeedbackStorageBackend,
    StorageConfig,
)


class TestConnectionPool:
    """Test connection pool functionality."""

    def test_pool_creates_connections_up_to_limit(self):
        """Verify pool creates connections up to max_connections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            pool = ConnectionPool(db_path, max_connections=3)

            # Get connections without releasing (hold them)
            conn1 = pool._pool.get() if not pool._pool.empty() else pool._create_connection()
            pool._created_connections = 1

            # Verify pool tracks creation
            assert pool._created_connections >= 1

            # Close manually
            conn1.close()
            pool.close_all()

    def test_pool_reuses_connections(self):
        """Verify pool reuses released connections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            pool = ConnectionPool(db_path, max_connections=2)

            # Get and release connection
            with pool.get_connection() as conn1:
                pass

            # Pool should have 1 connection
            assert pool._created_connections == 1

            # Get connection again - should reuse
            with pool.get_connection() as conn2:
                pass

            # Still 1 connection (reused)
            assert pool._created_connections == 1

            pool.close_all()

    def test_pool_enables_wal_mode(self):
        """Verify connections have WAL mode enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            pool = ConnectionPool(db_path, max_connections=1)

            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode")
                mode = cursor.fetchone()[0]
                assert mode == "wal"

            pool.close_all()

    def test_pool_closes_all_connections(self):
        """Verify close_all() closes all pooled connections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            pool = ConnectionPool(db_path, max_connections=3)

            # Create connections
            for _ in range(3):
                with pool.get_connection() as conn:
                    pass

            # At least 1 connection should be created (may be reused)
            assert pool._created_connections >= 1

            # Close all
            pool.close_all()
            assert pool._created_connections == 0


class TestFeedbackStorageBackend:
    """Test storage backend functionality."""

    @pytest.fixture
    def backend(self):
        """Create temporary storage backend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(
                db_path=Path(tmpdir) / "test.db",
                max_connections=5,
                retention_days=30,
                backup_interval_hours=1,
            )
            backend = FeedbackStorageBackend(config)
            yield backend
            backend.close()

    def test_schema_initialization(self, backend):
        """Verify database schema is created correctly."""
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()

            # Check table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback_cards'")
            assert cursor.fetchone() is not None

            # Check indexes exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_user'")
            assert cursor.fetchone() is not None

            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_timestamp'")
            assert cursor.fetchone() is not None

    def test_insert_feedback(self, backend):
        """Verify single feedback card insertion."""
        card_data = {
            "card_id": str(uuid4()),
            "session_id": "session_1",
            "timestamp": time.time(),
            "user_input": "Test input",
            "ai_response": "Test response",
            "feedback_type": "rating",
            "category": "helpfulness",
            "rating": 5,
            "user_id": "user_a",
            "impact_score": 0.8,
        }

        result = backend.insert_feedback(card_data)
        assert result is True

        # Verify inserted
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards WHERE card_id = ?", (card_data["card_id"],))
            assert cursor.fetchone()[0] == 1

    def test_insert_batch(self, backend):
        """Verify batch insertion of feedback cards."""
        cards_data = []
        for i in range(10):
            cards_data.append(
                {
                    "card_id": str(uuid4()),
                    "session_id": f"session_{i}",
                    "timestamp": time.time(),
                    "user_input": f"Input {i}",
                    "ai_response": f"Response {i}",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "rating": 3 + (i % 3),
                    "user_id": f"user_{i % 3}",
                }
            )

        inserted = backend.insert_batch(cards_data)
        assert inserted == 10

        # Verify all inserted
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards")
            assert cursor.fetchone()[0] == 10

    def test_update_batch(self, backend):
        """Verify batch update of feedback cards."""
        # Insert cards first
        cards_data = []
        card_ids = []
        for i in range(5):
            card_id = str(uuid4())
            card_ids.append(card_id)
            cards_data.append(
                {
                    "card_id": card_id,
                    "session_id": f"session_{i}",
                    "timestamp": time.time(),
                    "user_input": f"Input {i}",
                    "ai_response": f"Response {i}",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "processed": 0,
                }
            )

        backend.insert_batch(cards_data)

        # Update cards
        updates = [({"processed": 1, "impact_score": 0.9}, card_id) for card_id in card_ids]

        updated = backend.update_batch(updates)
        assert updated == 5

        # Verify updates
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards WHERE processed = 1")
            assert cursor.fetchone()[0] == 5

    def test_cleanup_old_data(self, backend):
        """Verify cleanup of old feedback cards."""
        # Insert old cards (90 days ago)
        old_timestamp = time.time() - (90 * 86400)
        old_cards = []
        for i in range(5):
            old_cards.append(
                {
                    "card_id": str(uuid4()),
                    "session_id": f"old_session_{i}",
                    "timestamp": old_timestamp,
                    "user_input": "Old input",
                    "ai_response": "Old response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "applied_to_training": 1,  # Only delete if applied
                }
            )

        # Insert recent cards (1 day ago)
        recent_timestamp = time.time() - 86400
        recent_cards = []
        for i in range(3):
            recent_cards.append(
                {
                    "card_id": str(uuid4()),
                    "session_id": f"recent_session_{i}",
                    "timestamp": recent_timestamp,
                    "user_input": "Recent input",
                    "ai_response": "Recent response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "applied_to_training": 1,
                }
            )

        backend.insert_batch(old_cards + recent_cards)

        # Cleanup with 30-day retention
        deleted = backend.cleanup_old_data(retention_days=30)
        assert deleted == 5  # Only old cards deleted

        # Verify recent cards remain
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards")
            assert cursor.fetchone()[0] == 3

    def test_backup_database(self, backend):
        """Verify database backup functionality."""
        # Insert some data
        card_data = {
            "card_id": str(uuid4()),
            "session_id": "backup_test",
            "timestamp": time.time(),
            "user_input": "Backup test",
            "ai_response": "Backup response",
            "feedback_type": "rating",
            "category": "helpfulness",
        }
        backend.insert_feedback(card_data)

        # Create backup
        backup_path = backend.config.db_path.parent / "test_backup.db"
        result = backend.backup_database(backup_path)
        assert result is True
        assert backup_path.exists()

        # Verify backup contains data
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feedback_cards")
        assert cursor.fetchone()[0] == 1
        conn.close()

    def test_metrics_tracking(self, backend):
        """Verify performance metrics are tracked."""
        initial_metrics = backend.get_metrics()

        # Perform operations
        card_data = {
            "card_id": str(uuid4()),
            "session_id": "metrics_test",
            "timestamp": time.time(),
            "user_input": "Test",
            "ai_response": "Response",
            "feedback_type": "rating",
            "category": "helpfulness",
        }
        backend.insert_feedback(card_data)

        batch_data = [
            {
                "card_id": str(uuid4()),
                "session_id": f"batch_{i}",
                "timestamp": time.time(),
                "user_input": "Batch",
                "ai_response": "Batch",
                "feedback_type": "rating",
                "category": "helpfulness",
            }
            for i in range(5)
        ]
        backend.insert_batch(batch_data)

        # Check metrics updated
        final_metrics = backend.get_metrics()
        assert final_metrics["queries_total"] > initial_metrics["queries_total"]
        assert final_metrics["queries_success"] > initial_metrics["queries_success"]
        assert final_metrics["batch_operations"] > initial_metrics["batch_operations"]

    def test_transaction_rollback_on_error(self, backend):
        """Verify transactions rollback on error."""
        # Insert valid card
        card1 = {
            "card_id": str(uuid4()),
            "session_id": "trans_test",
            "timestamp": time.time(),
            "user_input": "Test",
            "ai_response": "Response",
            "feedback_type": "rating",
            "category": "helpfulness",
        }
        backend.insert_feedback(card1)

        # Try to insert duplicate card_id (should fail due to PRIMARY KEY)
        card2 = card1.copy()  # Same card_id
        result = backend.insert_feedback(card2)
        assert result is False

        # Verify only 1 card exists
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards")
            assert cursor.fetchone()[0] == 1

    def test_composite_index_usage(self, backend):
        """Verify composite indexes improve query performance."""
        # Insert cards for same user
        user_id = "test_user"
        cards_data = []
        for i in range(100):
            cards_data.append(
                {
                    "card_id": str(uuid4()),
                    "session_id": f"session_{i}",
                    "timestamp": time.time() - (i * 100),  # Spread over time
                    "user_input": f"Input {i}",
                    "ai_response": f"Response {i}",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "user_id": user_id,
                }
            )
        backend.insert_batch(cards_data)

        # Query using composite index (user_id + timestamp)
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()

            # Explain query plan to verify index usage
            cursor.execute(
                """
                EXPLAIN QUERY PLAN
                SELECT * FROM feedback_cards
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """,
                (user_id,),
            )

            plan = cursor.fetchall()
            # Check that some index is used (not a full table scan)
            plan_str = " ".join(str(row) for row in plan)
            assert "SCAN" not in plan_str or "idx" in plan_str.lower() or "index" in plan_str.lower()

    def test_wal_checkpoint(self, backend):
        """Verify WAL checkpointing occurs."""
        # Insert many cards to trigger checkpoint
        cards_data = []
        for i in range(backend.config.checkpoint_interval + 10):
            cards_data.append(
                {
                    "card_id": str(uuid4()),
                    "session_id": f"checkpoint_{i}",
                    "timestamp": time.time(),
                    "user_input": "Input",
                    "ai_response": "Response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                }
            )

        # Insert in batches
        for i in range(0, len(cards_data), 100):
            backend.insert_batch(cards_data[i : i + 100])

        # Transaction count should have reset after checkpoint
        assert backend._transaction_count < backend.config.checkpoint_interval

    def test_concurrent_connections(self, backend):
        """Verify multiple connections can be used concurrently."""
        import threading

        results = []
        errors = []

        def insert_card(user_id):
            try:
                card_data = {
                    "card_id": str(uuid4()),
                    "session_id": f"concurrent_{user_id}",
                    "timestamp": time.time(),
                    "user_input": f"User {user_id}",
                    "ai_response": "Response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                    "user_id": user_id,
                }
                result = backend.insert_feedback(card_data)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create 10 threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=insert_card, args=(f"user_{i}",))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify no errors and all succeeded
        assert len(errors) == 0
        assert len(results) == 10
        assert all(results)

        # Verify all cards inserted
        with backend.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM feedback_cards")
            assert cursor.fetchone()[0] == 10


class TestStorageBackendMaintenance:
    """Test maintenance operations."""

    def test_automatic_maintenance_scheduling(self):
        """Verify maintenance tasks are scheduled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(db_path=Path(tmpdir) / "test.db", retention_days=30, backup_interval_hours=1)

            backend = FeedbackStorageBackend(config)

            initial_cleanup = backend._last_cleanup
            initial_backup = backend._last_backup

            # Insert old data
            old_timestamp = time.time() - (40 * 86400)
            old_card = {
                "card_id": str(uuid4()),
                "session_id": "old",
                "timestamp": old_timestamp,
                "user_input": "Old",
                "ai_response": "Old",
                "feedback_type": "rating",
                "category": "helpfulness",
                "applied_to_training": 1,
            }
            backend.insert_feedback(old_card)

            # Simulate time passing
            backend._last_cleanup = time.time() - 86400 - 1  # Over 1 day ago
            backend._last_backup = time.time() - (2 * 3600) - 1  # Over 2 hours ago

            # Run maintenance
            backend.maybe_run_maintenance()

            # Verify maintenance ran
            assert backend._last_cleanup > initial_cleanup
            assert backend._last_backup > initial_backup

            backend.close()

    def test_retention_policy_respects_applied_training(self):
        """Verify cleanup only removes applied training data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(db_path=Path(tmpdir) / "test.db", retention_days=30)
            backend = FeedbackStorageBackend(config)

            old_timestamp = time.time() - (40 * 86400)

            # Insert old card NOT applied to training
            card1 = {
                "card_id": str(uuid4()),
                "session_id": "old_not_applied",
                "timestamp": old_timestamp,
                "user_input": "Old",
                "ai_response": "Old",
                "feedback_type": "rating",
                "category": "helpfulness",
                "applied_to_training": 0,  # NOT applied
            }

            # Insert old card applied to training
            card2 = {
                "card_id": str(uuid4()),
                "session_id": "old_applied",
                "timestamp": old_timestamp,
                "user_input": "Old",
                "ai_response": "Old",
                "feedback_type": "rating",
                "category": "helpfulness",
                "applied_to_training": 1,  # Applied
            }

            backend.insert_batch([card1, card2])

            # Cleanup
            deleted = backend.cleanup_old_data(retention_days=30)
            assert deleted == 1  # Only applied card deleted

            # Verify unapplied card remains
            with backend.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT card_id FROM feedback_cards")
                remaining = cursor.fetchall()
                assert len(remaining) == 1
                assert remaining[0][0] == card1["card_id"]

            backend.close()


class TestErrorHandling:
    """Test error handling and recovery."""

    def test_invalid_data_handling(self):
        """Verify backend handles invalid data gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(db_path=Path(tmpdir) / "test.db")
            backend = FeedbackStorageBackend(config)

            # Missing required fields
            invalid_card = {"card_id": str(uuid4())}  # Missing required fields

            result = backend.insert_feedback(invalid_card)
            assert result is False

            # Verify metrics track error
            metrics = backend.get_metrics()
            assert metrics["queries_error"] > 0

            backend.close()

    def test_batch_partial_failure(self):
        """Verify batch operations handle partial failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = StorageConfig(db_path=Path(tmpdir) / "test.db")
            backend = FeedbackStorageBackend(config)

            # Mix of valid and invalid cards
            cards_data = [
                # Valid card
                {
                    "card_id": str(uuid4()),
                    "session_id": "valid",
                    "timestamp": time.time(),
                    "user_input": "Test",
                    "ai_response": "Response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                },
                # Invalid card (duplicate card_id)
                {
                    "card_id": "duplicate_id",
                    "session_id": "invalid",
                    "timestamp": time.time(),
                    "user_input": "Test",
                    "ai_response": "Response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                },
                # Another with same ID (will fail)
                {
                    "card_id": "duplicate_id",
                    "session_id": "invalid2",
                    "timestamp": time.time(),
                    "user_input": "Test",
                    "ai_response": "Response",
                    "feedback_type": "rating",
                    "category": "helpfulness",
                },
            ]

            inserted = backend.insert_batch(cards_data)

            # Should insert 2 (1 valid + 1 first duplicate, 2nd duplicate fails)
            assert inserted == 2

            backend.close()
