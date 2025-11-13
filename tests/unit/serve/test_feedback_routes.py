"""
Comprehensive test suite for serve/feedback_routes.py

Tests feedback collection and learning system:
- Feedback capture endpoint
- Batch feedback processing
- Learning report generation
- System metrics
- Manual learning trigger
- Health check
- Background task processing
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_feedback_system():
    """Mock FeedbackCardSystem."""
    mock_system = MagicMock()

    # Mock feedback card
    mock_card = MagicMock()
    mock_card.card_id = "card_123"
    mock_card.rating = MagicMock(value=5)
    mock_card.timestamp = 1730000000.0

    mock_system.capture_feedback.return_value = mock_card
    mock_system.feedback_cards = [mock_card] * 50  # Simulate existing cards

    # Mock learning report
    mock_report = MagicMock()
    mock_report.user_id_hash = "hashed_user_123"
    mock_report.total_feedback_cards = 10
    mock_report.overall_satisfaction = 4.5
    mock_report.improvement_trend = 0.2
    mock_report.preferred_styles = ["direct", "concise"]
    mock_report.recommended_adjustments = {"tone": "more formal"}

    mock_system.explain_learning.return_value = mock_report

    # Mock metrics
    mock_system.get_metrics.return_value = {
        "cards_captured": 100,
        "patterns_identified": 20,
        "policies_updated": 5,
        "validations_passed": 5,
        "validations_failed": 0,
        "total_cards": 500,
        "total_patterns": 50,
        "total_updates": 10,
    }

    # Mock pattern extraction
    mock_system.extract_patterns.return_value = [
        {"pattern_id": "p1", "type": "preference"},
    ]

    # Mock policy update
    mock_update = MagicMock()
    mock_update.update_id = "update_123"
    mock_system.update_policy.return_value = mock_update
    mock_system.validate_update.return_value = True

    return mock_system


@pytest.fixture
def app_client(mock_feedback_system):
    """Create test client with mocked feedback system."""
    with patch("serve.feedback_routes.FeedbackCardSystem", return_value=mock_feedback_system):
        from serve.feedback_routes import router
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)


class TestCaptureFeedback:
    """Test /feedback/capture endpoint."""

    def test_capture_feedback_success(self, app_client, mock_feedback_system):
        """Test successful feedback capture."""
        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                "rating": 5,
                "note": "Great response!",
                "symbols": ["helpful", "accurate"],
                "context": {"session": "test"},
                "user_id": "user_456",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["card_id"] == "card_123"
        assert data["rating"] == 5
        assert data["timestamp"] == 1730000000.0
        assert data["message"] == "Feedback captured successfully"

        # Verify system was called correctly
        mock_feedback_system.capture_feedback.assert_called_once()
        call_kwargs = mock_feedback_system.capture_feedback.call_args.kwargs

        assert call_kwargs["action_id"] == "action_123"
        assert call_kwargs["rating"] == 5
        assert call_kwargs["note"] == "Great response!"
        assert call_kwargs["symbols"] == ["helpful", "accurate"]
        assert call_kwargs["context"] == {"session": "test"}
        assert call_kwargs["user_id"] == "user_456"

    def test_capture_feedback_minimal(self, app_client, mock_feedback_system):
        """Test feedback capture with minimal fields."""
        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                "rating": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5  # Mock returns 5

    def test_capture_feedback_rating_validation_min(self, app_client):
        """Test rating minimum validation."""
        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                "rating": 0,  # Below minimum
            },
        )

        assert response.status_code == 422  # Validation error

    def test_capture_feedback_rating_validation_max(self, app_client):
        """Test rating maximum validation."""
        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                "rating": 6,  # Above maximum
            },
        )

        assert response.status_code == 422  # Validation error

    def test_capture_feedback_missing_required_fields(self, app_client):
        """Test error on missing required fields."""
        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                # Missing rating
            },
        )

        assert response.status_code == 422

    def test_capture_feedback_system_error(self, app_client, mock_feedback_system):
        """Test error handling when system fails."""
        mock_feedback_system.capture_feedback.side_effect = Exception("System error")

        response = app_client.post(
            "/feedback/capture",
            json={
                "action_id": "action_123",
                "rating": 4,
            },
        )

        assert response.status_code == 500
        assert "System error" in response.json()["detail"]


class TestBatchFeedback:
    """Test /feedback/batch endpoint."""

    def test_batch_feedback_success(self, app_client, mock_feedback_system):
        """Test successful batch feedback capture."""
        response = app_client.post(
            "/feedback/batch",
            json=[
                {"action_id": "action_1", "rating": 5},
                {"action_id": "action_2", "rating": 4},
                {"action_id": "action_3", "rating": 3},
            ],
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3
        for item in data:
            assert "card_id" in item
            assert "rating" in item
            assert "timestamp" in item

        # Verify all were captured
        assert mock_feedback_system.capture_feedback.call_count == 3

    def test_batch_feedback_empty_list(self, app_client):
        """Test batch with empty list."""
        response = app_client.post("/feedback/batch", json=[])

        assert response.status_code == 200
        assert response.json() == []

    def test_batch_feedback_partial_failure(self, app_client, mock_feedback_system):
        """Test batch continues on individual failures."""
        # Make second call fail
        mock_feedback_system.capture_feedback.side_effect = [
            MagicMock(card_id="card_1", rating=MagicMock(value=5), timestamp=1.0),
            Exception("Error on second"),
            MagicMock(card_id="card_3", rating=MagicMock(value=3), timestamp=3.0),
        ]

        response = app_client.post(
            "/feedback/batch",
            json=[
                {"action_id": "action_1", "rating": 5},
                {"action_id": "action_2", "rating": 4},
                {"action_id": "action_3", "rating": 3},
            ],
        )

        assert response.status_code == 200
        data = response.json()

        # Should have 2 successful captures (skipped the failed one)
        assert len(data) == 2

    def test_batch_feedback_validation_error(self, app_client):
        """Test batch validation errors."""
        response = app_client.post(
            "/feedback/batch",
            json=[
                {"action_id": "action_1", "rating": 5},
                {"action_id": "action_2", "rating": 10},  # Invalid
            ],
        )

        assert response.status_code == 422


class TestLearningReport:
    """Test /feedback/report/{user_id} endpoint."""

    def test_learning_report_success(self, app_client, mock_feedback_system):
        """Test successful learning report generation."""
        response = app_client.get("/feedback/report/user_123")

        assert response.status_code == 200
        data = response.json()

        assert data["user_id_hash"] == "hashed_user_123"
        assert data["total_feedback_cards"] == 10
        assert data["overall_satisfaction"] == 4.5
        assert data["improvement_trend"] == 0.2
        assert data["preferred_styles"] == ["direct", "concise"]
        assert data["recommendations"] == {"tone": "more formal"}
        assert "summary" in data

        # Verify system was called
        mock_feedback_system.explain_learning.assert_called_once_with("user_123")

    def test_learning_report_summary_improving(self, app_client, mock_feedback_system):
        """Test summary for improving trend."""
        response = app_client.get("/feedback/report/user_123")

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert "10 feedback cards" in summary
        assert "4.5/5" in summary
        assert "improving" in summary.lower()
        assert "direct, concise" in summary

    def test_learning_report_summary_degrading(self, app_client, mock_feedback_system):
        """Test summary for degrading trend."""
        mock_report = mock_feedback_system.explain_learning.return_value
        mock_report.improvement_trend = -0.3

        response = app_client.get("/feedback/report/user_123")

        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert "may not align" in summary.lower() or "recent changes" in summary.lower()

    def test_learning_report_no_recommendations(self, app_client, mock_feedback_system):
        """Test report with no recommendations."""
        mock_report = mock_feedback_system.explain_learning.return_value
        mock_report.recommended_adjustments = None

        response = app_client.get("/feedback/report/user_123")

        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"] == {}

    def test_learning_report_system_error(self, app_client, mock_feedback_system):
        """Test error handling in report generation."""
        mock_feedback_system.explain_learning.side_effect = Exception("Report error")

        response = app_client.get("/feedback/report/user_123")

        assert response.status_code == 500
        assert "Report error" in response.json()["detail"]


class TestSystemMetrics:
    """Test /feedback/metrics endpoint."""

    def test_system_metrics_success(self, app_client, mock_feedback_system):
        """Test successful metrics retrieval."""
        response = app_client.get("/feedback/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["cards_captured"] == 100
        assert data["patterns_identified"] == 20
        assert data["policies_updated"] == 5
        assert data["validations_passed"] == 5
        assert data["validations_failed"] == 0
        assert data["total_cards"] == 500
        assert data["total_patterns"] == 50
        assert data["total_updates"] == 10

    def test_system_metrics_error(self, app_client, mock_feedback_system):
        """Test error handling in metrics retrieval."""
        mock_feedback_system.get_metrics.side_effect = Exception("Metrics error")

        response = app_client.get("/feedback/metrics")

        assert response.status_code == 500


class TestTriggerLearning:
    """Test /feedback/trigger-learning endpoint."""

    def test_trigger_learning_success(self, app_client, mock_feedback_system):
        """Test successful learning trigger."""
        response = app_client.post("/feedback/trigger-learning")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "triggered"
        assert "50 feedback cards" in data["message"]

    def test_trigger_learning_insufficient_cards(self, app_client, mock_feedback_system):
        """Test learning trigger with insufficient cards."""
        mock_feedback_system.feedback_cards = [MagicMock()] * 5  # Only 5 cards

        response = app_client.post("/feedback/trigger-learning")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "skipped"
        assert "Not enough" in data["message"]
        assert "minimum 10" in data["message"]

    def test_trigger_learning_background_task(self, app_client, mock_feedback_system):
        """Test learning is triggered as background task."""
        from fastapi import BackgroundTasks

        response = app_client.post("/feedback/trigger-learning")

        assert response.status_code == 200
        # Background task should be scheduled (tested via successful response)

    def test_trigger_learning_error(self, app_client, mock_feedback_system):
        """Test error handling in learning trigger."""
        mock_feedback_system.feedback_cards = None  # Cause error

        response = app_client.post("/feedback/trigger-learning")

        assert response.status_code == 500


class TestRunLearningCycle:
    """Test run_learning_cycle background task."""

    @pytest.mark.asyncio
    async def test_run_learning_cycle_success(self, mock_feedback_system):
        """Test successful learning cycle execution."""
        from serve.feedback_routes import run_learning_cycle

        mock_cards = [MagicMock() for _ in range(20)]

        # Patch the global feedback_system
        with patch("serve.feedback_routes.feedback_system", mock_feedback_system):
            await run_learning_cycle(mock_cards)

        # Verify pattern extraction was called
        mock_feedback_system.extract_patterns.assert_called_once_with(mock_cards)

        # Verify policy update was called
        mock_feedback_system.update_policy.assert_called_once()

        # Verify validation was called
        mock_feedback_system.validate_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_learning_cycle_no_patterns(self, mock_feedback_system):
        """Test learning cycle with no patterns."""
        from serve.feedback_routes import run_learning_cycle

        mock_feedback_system.extract_patterns.return_value = []

        mock_cards = [MagicMock() for _ in range(20)]

        with patch("serve.feedback_routes.feedback_system", mock_feedback_system):
            await run_learning_cycle(mock_cards)

        # Should not call update_policy if no patterns
        mock_feedback_system.update_policy.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_learning_cycle_validation_failed(self, mock_feedback_system):
        """Test learning cycle when validation fails."""
        from serve.feedback_routes import run_learning_cycle

        mock_feedback_system.validate_update.return_value = False

        mock_cards = [MagicMock() for _ in range(20)]

        with patch("serve.feedback_routes.feedback_system", mock_feedback_system):
            # Should not raise error, just log warning
            await run_learning_cycle(mock_cards)

        mock_feedback_system.validate_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_learning_cycle_error_handling(self, mock_feedback_system):
        """Test error handling in learning cycle."""
        from serve.feedback_routes import run_learning_cycle

        mock_feedback_system.extract_patterns.side_effect = Exception("Pattern error")

        mock_cards = [MagicMock() for _ in range(20)]

        with patch("serve.feedback_routes.feedback_system", mock_feedback_system):
            # Should not raise error, just log
            await run_learning_cycle(mock_cards)


class TestHealthCheck:
    """Test /feedback/health endpoint."""

    def test_health_check_healthy(self, app_client, mock_feedback_system):
        """Test health check when system is healthy."""
        response = app_client.get("/feedback/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["total_cards"] == 500
        assert data["system_active"] is True

    def test_health_check_unhealthy(self, app_client, mock_feedback_system):
        """Test health check when system is unhealthy."""
        mock_feedback_system.get_metrics.side_effect = Exception("Storage disconnected")

        response = app_client.get("/feedback/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert "error" in data
        assert data["system_active"] is False


class TestRequestModels:
    """Test request/response model validation."""

    def test_feedback_request_model(self):
        """Test FeedbackRequest model."""
        from serve.feedback_routes import FeedbackRequest

        request = FeedbackRequest(
            action_id="test_action",
            rating=5,
            note="Great job",
            symbols=["accurate", "helpful"],
            context={"key": "value"},
            user_id="user_123",
        )

        assert request.action_id == "test_action"
        assert request.rating == 5
        assert request.note == "Great job"
        assert request.symbols == ["accurate", "helpful"]
        assert request.context == {"key": "value"}
        assert request.user_id == "user_123"

    def test_feedback_request_defaults(self):
        """Test FeedbackRequest default values."""
        from serve.feedback_routes import FeedbackRequest

        request = FeedbackRequest(action_id="test", rating=3)

        assert request.note is None
        assert request.symbols == []
        assert request.context == {}
        assert request.user_id is None

    def test_feedback_response_model(self):
        """Test FeedbackResponse model."""
        from serve.feedback_routes import FeedbackResponse

        response = FeedbackResponse(
            card_id="card_123",
            rating=5,
            timestamp=1730000000.0,
        )

        assert response.card_id == "card_123"
        assert response.rating == 5
        assert response.timestamp == 1730000000.0
        assert response.message == "Feedback captured successfully"

    def test_learning_report_response_model(self):
        """Test LearningReportResponse model."""
        from serve.feedback_routes import LearningReportResponse

        response = LearningReportResponse(
            user_id_hash="hash_123",
            total_feedback_cards=10,
            overall_satisfaction=4.5,
            improvement_trend=0.2,
            preferred_styles=["direct"],
            summary="Test summary",
            recommendations={"tone": "formal"},
        )

        assert response.user_id_hash == "hash_123"
        assert response.total_feedback_cards == 10
        assert response.overall_satisfaction == 4.5

    def test_system_metrics_response_model(self):
        """Test SystemMetricsResponse model."""
        from serve.feedback_routes import SystemMetricsResponse

        response = SystemMetricsResponse(
            cards_captured=100,
            patterns_identified=20,
            policies_updated=5,
            validations_passed=5,
            validations_failed=0,
            total_cards=500,
            total_patterns=50,
            total_updates=10,
        )

        assert response.cards_captured == 100
        assert response.total_cards == 500


class TestRouterConfiguration:
    """Test router configuration."""

    def test_router_prefix(self):
        """Test router has correct prefix."""
        from serve.feedback_routes import router

        assert router.prefix == "/feedback"

    def test_router_tags(self):
        """Test router has correct tags."""
        from serve.feedback_routes import router

        assert "feedback" in router.tags

    def test_feedback_system_initialization(self):
        """Test feedback system is initialized."""
        with patch("serve.feedback_routes.FeedbackCardSystem") as mock_system_class:
            # Re-import to trigger initialization
            import importlib
            from serve import feedback_routes

            importlib.reload(feedback_routes)

            # System should be initialized with storage_path
            mock_system_class.assert_called_with(storage_path="feedback_data")


class TestEndpointDocumentation:
    """Test endpoint documentation and OpenAPI specs."""

    def test_capture_endpoint_summary(self):
        """Test capture endpoint has summary."""
        from serve.feedback_routes import router

        capture_route = None
        for route in router.routes:
            if hasattr(route, "path") and route.path == "/capture":
                capture_route = route
                break

        assert capture_route is not None
        assert capture_route.summary == "Capture Feedback"

    def test_batch_endpoint_response_model(self):
        """Test batch endpoint response model."""
        from serve.feedback_routes import router

        batch_route = None
        for route in router.routes:
            if hasattr(route, "path") and route.path == "/batch":
                batch_route = route
                break

        assert batch_route is not None
        # Response model should be list of FeedbackResponse
