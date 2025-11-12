"""
Integration tests for per-user data isolation (Task 1.3).

These tests verify that users can only access their own data:
- Feedback cards filtered by user_id
- Traces filtered by user_id
- Statistics scoped to user

Security: Prevents cross-user data access (OWASP A01 mitigation)
"""

import tempfile
from datetime import timedelta
from pathlib import Path

import pytest


# Feedback system tests
class TestFeedbackSystemIsolation:
    """Test feedback system enforces user_id filtering."""

    def setup_method(self):
        """Create temporary database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_feedback.db"

    def test_submit_feedback_requires_user_id(self):
        """Verify submit_feedback() requires user_id parameter."""
        from products.experience.feedback.core.feedback_cards import (
            FeedbackCardsManager,
            FeedbackCategory,
        )

        manager = FeedbackCardsManager(db_path=self.db_path)

        # Create a feedback card
        card = manager.create_rating_card(
            user_input="Test input",
            ai_response="Test response",
            category=FeedbackCategory.HELPFULNESS,
            session_id="test-session"
        )

        # Submit without user_id should raise ValueError
        with pytest.raises(ValueError, match="user_id is required"):
            manager.submit_feedback(
                card.card_id,
                user_id="",  # Empty user_id
                rating=5
            )

        # Submit with user_id should succeed
        result = manager.submit_feedback(
            card.card_id,
            user_id="user_a",
            rating=5
        )
        assert result is True

    def test_get_cards_for_training_filters_by_user(self):
        """Verify get_cards_for_training() only returns user's own cards."""
        from products.experience.feedback.core.feedback_cards import (
            FeedbackCardsManager,
            FeedbackCategory,
        )

        manager = FeedbackCardsManager(db_path=self.db_path)

        # User A submits feedback
        card_a = manager.create_rating_card(
            user_input="User A input",
            ai_response="Response A",
            category=FeedbackCategory.ACCURACY
        )
        manager.submit_feedback(card_a.card_id, user_id="user_a", rating=5)

        # User B submits feedback
        card_b = manager.create_rating_card(
            user_input="User B input",
            ai_response="Response B",
            category=FeedbackCategory.ACCURACY
        )
        manager.submit_feedback(card_b.card_id, user_id="user_b", rating=4)

        # User A should only see their own cards
        cards_a = manager.get_cards_for_training(user_id="user_a", min_impact=0.0)
        assert len(cards_a) == 1
        assert cards_a[0].card_id == card_a.card_id
        assert cards_a[0].user_id == "user_a"

        # User B should only see their own cards
        cards_b = manager.get_cards_for_training(user_id="user_b", min_impact=0.0)
        assert len(cards_b) == 1
        assert cards_b[0].card_id == card_b.card_id
        assert cards_b[0].user_id == "user_b"

    def test_get_statistics_scoped_to_user(self):
        """Verify get_statistics() only returns user's own statistics."""
        from products.experience.feedback.core.feedback_cards import (
            FeedbackCardsManager,
            FeedbackCategory,
        )

        manager = FeedbackCardsManager(db_path=self.db_path)

        # User A submits 3 feedback cards
        for i in range(3):
            card = manager.create_rating_card(
                user_input=f"User A input {i}",
                ai_response=f"Response {i}",
                category=FeedbackCategory.HELPFULNESS
            )
            manager.submit_feedback(card.card_id, user_id="user_a", rating=5)

        # User B submits 2 feedback cards
        for i in range(2):
            card = manager.create_rating_card(
                user_input=f"User B input {i}",
                ai_response=f"Response {i}",
                category=FeedbackCategory.HELPFULNESS
            )
            manager.submit_feedback(card.card_id, user_id="user_b", rating=3)

        # User A statistics should only show their 3 cards
        stats_a = manager.get_statistics(user_id="user_a")
        assert stats_a["total_cards"] == 3
        assert stats_a["average_rating"] == 5.0

        # User B statistics should only show their 2 cards
        stats_b = manager.get_statistics(user_id="user_b")
        assert stats_b["total_cards"] == 2
        assert stats_b["average_rating"] == 3.0

    def test_mark_as_applied_only_affects_own_cards(self):
        """Verify mark_as_applied() only marks user's own cards."""
        from products.experience.feedback.core.feedback_cards import (
            FeedbackCardsManager,
            FeedbackCategory,
        )

        manager = FeedbackCardsManager(db_path=self.db_path)

        # User A submits feedback
        card_a = manager.create_rating_card(
            user_input="User A input",
            ai_response="Response A",
            category=FeedbackCategory.ACCURACY
        )
        manager.submit_feedback(card_a.card_id, user_id="user_a", rating=5)

        # User B submits feedback
        card_b = manager.create_rating_card(
            user_input="User B input",
            ai_response="Response B",
            category=FeedbackCategory.ACCURACY
        )
        manager.submit_feedback(card_b.card_id, user_id="user_b", rating=4)

        # User A tries to mark User B's card as applied (should not work)
        manager.mark_as_applied(user_id="user_a", card_ids=[card_b.card_id])

        # User B's card should still be available for training (not marked as applied by User A)
        cards_b = manager.get_cards_for_training(user_id="user_b", min_impact=0.0)
        assert len(cards_b) == 1  # Card B still available

        # User A marks their own card as applied
        manager.mark_as_applied(user_id="user_a", card_ids=[card_a.card_id])

        # User A's card should no longer be available for training
        cards_a = manager.get_cards_for_training(user_id="user_a", min_impact=0.0)
        assert len(cards_a) == 0  # Card A marked as applied


# Trace system tests
class TestTraceSystemIsolation:
    """Test trace system enforces user_id filtering."""

    @pytest.mark.asyncio
    async def test_get_trace_by_id_filters_by_user(self):
        """Verify get_trace_by_id() only returns user's own traces."""
        import json
        import tempfile

        from serve.storage.trace_provider import FileTraceStorageProvider

        temp_dir = tempfile.mkdtemp()
        provider = FileTraceStorageProvider(storage_location=temp_dir)

        # Create mock traces in JSONL file
        traces_file = Path(temp_dir) / "all_traces.jsonl"
        trace_a_id = "trace-a-123"
        trace_b_id = "trace-b-456"

        with open(traces_file, "w") as f:
            # Trace A belongs to user_a
            trace_a = {
                "trace_id": trace_a_id,
                "user_id": "user_a",
                "timestamp": "2025-01-01T00:00:00Z",
                "unix_time": 1704067200.0,
                "level": 1,
                "level_name": "INFO",
                "message": "Trace for user A",
                "source_component": "test"
            }
            f.write(json.dumps(trace_a) + "\n")

            # Trace B belongs to user_b
            trace_b = {
                "trace_id": trace_b_id,
                "user_id": "user_b",
                "timestamp": "2025-01-01T00:00:00Z",
                "unix_time": 1704067200.0,
                "level": 1,
                "level_name": "INFO",
                "message": "Trace for user B",
                "source_component": "test"
            }
            f.write(json.dumps(trace_b) + "\n")

        # User A should only access their own trace
        trace_a_result = await provider.get_trace_by_id(trace_a_id, user_id="user_a")
        assert trace_a_result is not None
        assert trace_a_result["user_id"] == "user_a"

        # User A should NOT access User B's trace (returns None)
        trace_b_result = await provider.get_trace_by_id(trace_b_id, user_id="user_a")
        assert trace_b_result is None  # Access denied

    @pytest.mark.asyncio
    async def test_get_recent_traces_filters_by_user(self):
        """Verify get_recent_traces() only returns user's own traces."""
        import tempfile

        from serve.storage.trace_provider import FileTraceStorageProvider

        temp_dir = tempfile.mkdtemp()
        provider = FileTraceStorageProvider(storage_location=temp_dir)

        # Note: This test requires TraceMemoryLogger to be available
        # If not available, the test will skip via ImportError
        try:
            trace_logger = provider._get_trace_logger()

            # Add traces for different users
            trace_logger.recent_traces = [
                {"trace_id": "1", "user_id": "user_a", "message": "Trace 1"},
                {"trace_id": "2", "user_id": "user_b", "message": "Trace 2"},
                {"trace_id": "3", "user_id": "user_a", "message": "Trace 3"},
            ]

            # User A should only see their 2 traces
            traces_a = await provider.get_recent_traces(user_id="user_a", limit=10)
            assert len(traces_a) == 2
            assert all(t["user_id"] == "user_a" for t in traces_a)

            # User B should only see their 1 trace
            traces_b = await provider.get_recent_traces(user_id="user_b", limit=10)
            assert len(traces_b) == 1
            assert traces_b[0]["user_id"] == "user_b"

        except ImportError:
            pytest.skip("TraceMemoryLogger not available - skipping test")


# End-to-end isolation test
class TestCompleteUserIsolation:
    """End-to-end test verifying complete data isolation across systems."""

    def test_user_cannot_access_other_user_feedback(self):
        """Verify User A cannot access any of User B's feedback data."""
        import tempfile

        from products.experience.feedback.core.feedback_cards import (
            FeedbackCardsManager,
            FeedbackCategory,
        )

        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_isolation.db"
        manager = FeedbackCardsManager(db_path=db_path)

        # User B submits feedback
        card_b = manager.create_rating_card(
            user_input="User B private input",
            ai_response="Response B",
            category=FeedbackCategory.HELPFULNESS
        )
        manager.submit_feedback(card_b.card_id, user_id="user_b", rating=5)

        # User A should see empty results (no access to User B's data)
        cards_a = manager.get_cards_for_training(user_id="user_a", min_impact=0.0)
        assert len(cards_a) == 0  # User A sees nothing

        stats_a = manager.get_statistics(user_id="user_a")
        assert stats_a["total_cards"] == 0  # User A has no cards

        # User B should see their own data
        cards_b = manager.get_cards_for_training(user_id="user_b", min_impact=0.0)
        assert len(cards_b) == 1  # User B sees their card

        stats_b = manager.get_statistics(user_id="user_b")
        assert stats_b["total_cards"] == 1  # User B has 1 card

    @pytest.mark.asyncio
    async def test_legacy_traces_without_user_id_denied(self):
        """Verify legacy traces without user_id are denied for security."""
        import json
        import tempfile

        from serve.storage.trace_provider import FileTraceStorageProvider

        temp_dir = tempfile.mkdtemp()
        provider = FileTraceStorageProvider(storage_location=temp_dir)

        # Create legacy trace without user_id
        traces_file = Path(temp_dir) / "all_traces.jsonl"
        legacy_trace_id = "legacy-trace-123"

        with open(traces_file, "w") as f:
            legacy_trace = {
                "trace_id": legacy_trace_id,
                # NO user_id field (legacy trace)
                "timestamp": "2025-01-01T00:00:00Z",
                "unix_time": 1704067200.0,
                "level": 1,
                "level_name": "INFO",
                "message": "Legacy trace without user_id",
                "source_component": "test"
            }
            f.write(json.dumps(legacy_trace) + "\n")

        # Any user trying to access legacy trace should be denied
        result = await provider.get_trace_by_id(legacy_trace_id, user_id="user_a")
        assert result is None  # Legacy traces are denied for security
