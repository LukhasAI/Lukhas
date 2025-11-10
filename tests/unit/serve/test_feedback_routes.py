"""
Comprehensive test suite for serve.feedback_routes module.

Tests all 6 endpoints (capture, batch, report, metrics, trigger-learning, health)
and 1 helper function (run_learning_cycle) with comprehensive coverage.

Following Test Surgeon canonical guidelines:
- Tests only (no production code changes)
- Deterministic (mocked time, dependencies, filesystem)
- Network-free (all external systems mocked)
- Comprehensive coverage (75%+ target)
"""
from typing import Any
from unittest import mock

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient


@pytest.fixture
def mock_feedback_card():
    """Create mock feedback card."""
    card = mock.MagicMock()
    card.card_id = "card_test_123"
    card.rating.value = 5
    card.timestamp = 1730000000.0
    return card


@pytest.fixture
def mock_feedback_system(mock_feedback_card):
    """
    Create mock FeedbackCardSystem with pre-configured responses.
    """
    system = mock.MagicMock()

    # Mock capture_feedback method
    system.capture_feedback.return_value = mock_feedback_card

    # Mock feedback_cards list for trigger_learning
    system.feedback_cards = [mock_feedback_card] * 50

    # Mock explain_learning method
    mock_report = mock.MagicMock()
    mock_report.user_id_hash = "hashed_user_123"
    mock_report.total_feedback_cards = 25
    mock_report.overall_satisfaction = 4.3
    mock_report.improvement_trend = 0.15
    mock_report.preferred_styles = ["direct", "concise"]
    mock_report.recommended_adjustments = {"tone": "more formal", "detail_level": "higher"}
    system.explain_learning.return_value = mock_report

    # Mock get_metrics method
    system.get_metrics.return_value = {
        "cards_captured": 100,
        "patterns_identified": 20,
        "policies_updated": 5,
        "validations_passed": 5,
        "validations_failed": 0,
        "total_cards": 500,
        "total_patterns": 50,
        "total_updates": 10,
    }

    # Mock extract_patterns method
    mock_pattern = mock.MagicMock()
    mock_pattern.pattern_id = "pattern_test"
    system.extract_patterns.return_value = [mock_pattern]

    # Mock update_policy method
    mock_update = mock.MagicMock()
    mock_update.update_id = "update_test"
    system.update_policy.return_value = mock_update

    # Mock validate_update method
    system.validate_update.return_value = True

    return system


@pytest.fixture
def feedback_routes_module(mock_feedback_system):
    """
    Import serve.feedback_routes with mocked FeedbackCardSystem.
    """
    with mock.patch("serve.feedback_routes.FeedbackCardSystem", return_value=mock_feedback_system):
        import importlib

        import serve.feedback_routes as routes_module
        importlib.reload(routes_module)
        # Replace the module-level feedback_system instance
        routes_module.feedback_system = mock_feedback_system
        yield routes_module


@pytest.fixture
def test_app(feedback_routes_module):
    """Create FastAPI test client with feedback routes."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(feedback_routes_module.router)
    return TestClient(app)


# ==============================================================================
# Endpoint Tests: POST /feedback/capture
# ==============================================================================

def test_capture_feedback_success(test_app, mock_feedback_system):
    """Test POST /feedback/capture with valid request."""
    payload = {
        "action_id": "action_123",
        "rating": 5,
        "note": "Great response!",
        "symbols": ["helpful", "accurate"],
        "context": {"session_id": "session_123"},
        "user_id": "user_abc",
    }

    response = test_app.post("/feedback/capture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["card_id"] == "card_test_123"
    assert data["rating"] == 5
    assert data["timestamp"] == 1730000000.0
    assert data["message"] == "Feedback captured successfully"

    # Verify feedback_system.capture_feedback was called correctly
    mock_feedback_system.capture_feedback.assert_called_once_with(
        action_id="action_123",
        rating=5,
        note="Great response!",
        symbols=["helpful", "accurate"],
        context={"session_id": "session_123"},
        user_id="user_abc",
    )


def test_capture_feedback_minimal(test_app, mock_feedback_system):
    """Test POST /feedback/capture with minimal required fields."""
    payload = {
        "action_id": "action_456",
        "rating": 3,
    }

    response = test_app.post("/feedback/capture", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["card_id"] == "card_test_123"
    assert data["rating"] == 5


def test_capture_feedback_rating_validation_low(test_app):
    """Test POST /feedback/capture rejects rating below 1."""
    payload = {
        "action_id": "action_789",
        "rating": 0,
    }

    response = test_app.post("/feedback/capture", json=payload)

    assert response.status_code == 422  # Validation error


def test_capture_feedback_rating_validation_high(test_app):
    """Test POST /feedback/capture rejects rating above 5."""
    payload = {
        "action_id": "action_789",
        "rating": 6,
    }

    response = test_app.post("/feedback/capture", json=payload)

    assert response.status_code == 422  # Validation error


def test_capture_feedback_system_error(test_app, mock_feedback_system):
    """Test POST /feedback/capture handles system errors gracefully."""
    mock_feedback_system.capture_feedback.side_effect = Exception("Database connection failed")

    payload = {
        "action_id": "action_error",
        "rating": 4,
    }

    response = test_app.post("/feedback/capture", json=payload)

    assert response.status_code == 500
    assert "Database connection failed" in response.json()["detail"]


# ==============================================================================
# Endpoint Tests: POST /feedback/batch
# ==============================================================================

def test_capture_batch_feedback_success(test_app, mock_feedback_system):
    """Test POST /feedback/batch with multiple valid requests."""
    payload = [
        {"action_id": "action_1", "rating": 5},
        {"action_id": "action_2", "rating": 4},
        {"action_id": "action_3", "rating": 3},
    ]

    response = test_app.post("/feedback/batch", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["card_id"] == "card_test_123" for item in data)
    assert all(item["rating"] == 5 for item in data)
    assert mock_feedback_system.capture_feedback.call_count == 3


def test_capture_batch_feedback_empty_list(test_app):
    """Test POST /feedback/batch with empty list."""
    payload = []

    response = test_app.post("/feedback/batch", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_capture_batch_feedback_partial_failure(test_app, mock_feedback_system):
    """Test POST /feedback/batch continues on individual failures."""
    # First call succeeds, second fails, third succeeds
    mock_feedback_system.capture_feedback.side_effect = [
        mock_feedback_system.capture_feedback.return_value,
        Exception("Transient error"),
        mock_feedback_system.capture_feedback.return_value,
    ]

    payload = [
        {"action_id": "action_1", "rating": 5},
        {"action_id": "action_2", "rating": 4},
        {"action_id": "action_3", "rating": 3},
    ]

    response = test_app.post("/feedback/batch", json=payload)

    assert response.status_code == 200
    data = response.json()
    # Should have 2 successful captures (1st and 3rd)
    assert len(data) == 2


def test_capture_batch_feedback_single_item(test_app, mock_feedback_system):
    """Test POST /feedback/batch with single item."""
    payload = [{"action_id": "action_solo", "rating": 5}]

    response = test_app.post("/feedback/batch", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# ==============================================================================
# Endpoint Tests: GET /feedback/report/{user_id}
# ==============================================================================

def test_get_learning_report_success(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} returns learning report."""
    response = test_app.get("/feedback/report/user_123")

    assert response.status_code == 200
    data = response.json()

    assert data["user_id_hash"] == "hashed_user_123"
    assert data["total_feedback_cards"] == 25
    assert data["overall_satisfaction"] == 4.3
    assert data["improvement_trend"] == 0.15
    assert data["preferred_styles"] == ["direct", "concise"]
    assert "summary" in data
    assert "25 feedback cards" in data["summary"]
    assert "4.3/5" in data["summary"]
    assert data["recommendations"] == {"tone": "more formal", "detail_level": "higher"}

    mock_feedback_system.explain_learning.assert_called_once_with("user_123")


def test_get_learning_report_positive_trend(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} with positive improvement trend."""
    mock_report = mock_feedback_system.explain_learning.return_value
    mock_report.improvement_trend = 0.25

    response = test_app.get("/feedback/report/user_positive")

    assert response.status_code == 200
    data = response.json()
    assert "improving" in data["summary"]


def test_get_learning_report_negative_trend(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} with negative improvement trend."""
    mock_report = mock_feedback_system.explain_learning.return_value
    mock_report.improvement_trend = -0.15

    response = test_app.get("/feedback/report/user_negative")

    assert response.status_code == 200
    data = response.json()
    assert "may not align" in data["summary"]


def test_get_learning_report_no_preferred_styles(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} with no preferred styles."""
    mock_report = mock_feedback_system.explain_learning.return_value
    mock_report.preferred_styles = []

    response = test_app.get("/feedback/report/user_no_prefs")

    assert response.status_code == 200
    data = response.json()
    # Summary should not mention preferred style
    assert data["preferred_styles"] == []


def test_get_learning_report_no_recommendations(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} with no recommendations."""
    mock_report = mock_feedback_system.explain_learning.return_value
    mock_report.recommended_adjustments = None

    response = test_app.get("/feedback/report/user_no_recs")

    assert response.status_code == 200
    data = response.json()
    assert data["recommendations"] == {}


def test_get_learning_report_system_error(test_app, mock_feedback_system):
    """Test GET /feedback/report/{user_id} handles system errors."""
    mock_feedback_system.explain_learning.side_effect = Exception("Analysis failed")

    response = test_app.get("/feedback/report/user_error")

    assert response.status_code == 500
    assert "Analysis failed" in response.json()["detail"]


# ==============================================================================
# Endpoint Tests: GET /feedback/metrics
# ==============================================================================

def test_get_system_metrics_success(test_app, mock_feedback_system):
    """Test GET /feedback/metrics returns system metrics."""
    response = test_app.get("/feedback/metrics")

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

    mock_feedback_system.get_metrics.assert_called_once()


def test_get_system_metrics_zero_values(test_app, mock_feedback_system):
    """Test GET /feedback/metrics with zero values."""
    mock_feedback_system.get_metrics.return_value = {
        "cards_captured": 0,
        "patterns_identified": 0,
        "policies_updated": 0,
        "validations_passed": 0,
        "validations_failed": 0,
        "total_cards": 0,
        "total_patterns": 0,
        "total_updates": 0,
    }

    response = test_app.get("/feedback/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_cards"] == 0


def test_get_system_metrics_error(test_app, mock_feedback_system):
    """Test GET /feedback/metrics handles system errors."""
    mock_feedback_system.get_metrics.side_effect = Exception("Metrics unavailable")

    response = test_app.get("/feedback/metrics")

    assert response.status_code == 500
    assert "Metrics unavailable" in response.json()["detail"]


# ==============================================================================
# Endpoint Tests: POST /feedback/trigger-learning
# ==============================================================================

def test_trigger_learning_success(test_app, mock_feedback_system):
    """Test POST /feedback/trigger-learning with sufficient cards."""
    # Ensure we have more than 10 cards
    mock_feedback_system.feedback_cards = [mock.MagicMock()] * 50

    response = test_app.post("/feedback/trigger-learning")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert "50 feedback cards" in data["message"]


def test_trigger_learning_insufficient_cards(test_app, mock_feedback_system):
    """Test POST /feedback/trigger-learning with insufficient cards."""
    # Set less than 10 cards
    mock_feedback_system.feedback_cards = [mock.MagicMock()] * 5

    response = test_app.post("/feedback/trigger-learning")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert "Not enough feedback cards" in data["message"]
    assert "minimum 10 required" in data["message"]


def test_trigger_learning_exactly_ten_cards(test_app, mock_feedback_system):
    """Test POST /feedback/trigger-learning with exactly 10 cards."""
    mock_feedback_system.feedback_cards = [mock.MagicMock()] * 10

    response = test_app.post("/feedback/trigger-learning")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"


def test_trigger_learning_more_than_hundred_cards(test_app, mock_feedback_system):
    """Test POST /feedback/trigger-learning caps at 100 cards."""
    # Set 200 cards, should only use last 100
    mock_feedback_system.feedback_cards = [mock.MagicMock()] * 200

    response = test_app.post("/feedback/trigger-learning")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert "100 feedback cards" in data["message"]


def test_trigger_learning_system_error(test_app, mock_feedback_system):
    """Test POST /feedback/trigger-learning handles system errors."""
    mock_feedback_system.feedback_cards = None  # Trigger error

    response = test_app.post("/feedback/trigger-learning")

    assert response.status_code == 500


# ==============================================================================
# Endpoint Tests: GET /feedback/health
# ==============================================================================

def test_health_check_healthy(test_app, mock_feedback_system):
    """Test GET /feedback/health when system is healthy."""
    response = test_app.get("/feedback/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_cards"] == 500
    assert data["system_active"] is True


def test_health_check_unhealthy(test_app, mock_feedback_system):
    """Test GET /feedback/health when system has errors."""
    mock_feedback_system.get_metrics.side_effect = Exception("Storage disconnected")

    response = test_app.get("/feedback/health")

    # Note: health endpoint returns 200 even when unhealthy
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["error"] == "Storage disconnected"
    assert data["system_active"] is False


def test_health_check_zero_cards(test_app, mock_feedback_system):
    """Test GET /feedback/health with zero cards."""
    mock_feedback_system.get_metrics.return_value = {
        "cards_captured": 0,
        "patterns_identified": 0,
        "policies_updated": 0,
        "validations_passed": 0,
        "validations_failed": 0,
        "total_cards": 0,
        "total_patterns": 0,
        "total_updates": 0,
    }

    response = test_app.get("/feedback/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_cards"] == 0


# ==============================================================================
# Helper Function Tests: run_learning_cycle
# ==============================================================================

@pytest.mark.asyncio
async def test_run_learning_cycle_success(feedback_routes_module, mock_feedback_system):
    """Test run_learning_cycle completes successfully."""
    mock_cards = [mock.MagicMock() for _ in range(20)]

    await feedback_routes_module.run_learning_cycle(mock_cards)

    # Verify pattern extraction was called
    mock_feedback_system.extract_patterns.assert_called_once_with(mock_cards)

    # Verify policy update was called
    mock_feedback_system.update_policy.assert_called_once()

    # Verify validation was called
    mock_feedback_system.validate_update.assert_called_once()


@pytest.mark.asyncio
async def test_run_learning_cycle_no_patterns(feedback_routes_module, mock_feedback_system):
    """Test run_learning_cycle when no patterns found."""
    mock_feedback_system.extract_patterns.return_value = []
    mock_cards = [mock.MagicMock() for _ in range(20)]

    await feedback_routes_module.run_learning_cycle(mock_cards)

    # Should extract patterns but not update policy
    mock_feedback_system.extract_patterns.assert_called_once()
    mock_feedback_system.update_policy.assert_not_called()


@pytest.mark.asyncio
async def test_run_learning_cycle_no_update(feedback_routes_module, mock_feedback_system):
    """Test run_learning_cycle when update_policy returns None."""
    mock_feedback_system.update_policy.return_value = None
    mock_cards = [mock.MagicMock() for _ in range(20)]

    await feedback_routes_module.run_learning_cycle(mock_cards)

    # Should not validate if no update
    mock_feedback_system.validate_update.assert_not_called()


@pytest.mark.asyncio
async def test_run_learning_cycle_validation_failure(feedback_routes_module, mock_feedback_system):
    """Test run_learning_cycle when validation fails."""
    mock_feedback_system.validate_update.return_value = False
    mock_cards = [mock.MagicMock() for _ in range(20)]

    # Should not raise exception, just log warning
    await feedback_routes_module.run_learning_cycle(mock_cards)

    mock_feedback_system.validate_update.assert_called_once()


@pytest.mark.asyncio
async def test_run_learning_cycle_extract_patterns_error(
    feedback_routes_module, mock_feedback_system
):
    """Test run_learning_cycle handles extract_patterns errors."""
    mock_feedback_system.extract_patterns.side_effect = Exception("Pattern extraction failed")
    mock_cards = [mock.MagicMock() for _ in range(20)]

    # Should not raise exception, errors are logged
    await feedback_routes_module.run_learning_cycle(mock_cards)


@pytest.mark.asyncio
async def test_run_learning_cycle_update_policy_error(
    feedback_routes_module, mock_feedback_system
):
    """Test run_learning_cycle handles update_policy errors."""
    mock_feedback_system.update_policy.side_effect = Exception("Update generation failed")
    mock_cards = [mock.MagicMock() for _ in range(20)]

    # Should not raise exception, errors are logged
    await feedback_routes_module.run_learning_cycle(mock_cards)


# ==============================================================================
# Integration Tests
# ==============================================================================

def test_router_exports(feedback_routes_module):
    """Test that feedback_routes module exports router correctly."""
    assert hasattr(feedback_routes_module, "router")
    assert feedback_routes_module.router is not None
    assert feedback_routes_module.router.prefix == "/feedback"
    assert "feedback" in feedback_routes_module.router.tags


def test_feedback_system_initialization(feedback_routes_module):
    """Test that feedback_system is initialized at module level."""
    assert hasattr(feedback_routes_module, "feedback_system")
    assert feedback_routes_module.feedback_system is not None


def test_request_model_validation():
    """Test FeedbackRequest model validation."""
    from serve.feedback_routes import FeedbackRequest

    # Valid request
    request = FeedbackRequest(action_id="test", rating=3)
    assert request.action_id == "test"
    assert request.rating == 3
    assert request.note is None
    assert request.symbols == []
    assert request.context == {}

    # Test rating bounds
    with pytest.raises(Exception):  # Pydantic ValidationError
        FeedbackRequest(action_id="test", rating=0)

    with pytest.raises(Exception):  # Pydantic ValidationError
        FeedbackRequest(action_id="test", rating=6)


def test_response_model_structure():
    """Test FeedbackResponse model structure."""
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


def test_learning_report_model_structure():
    """Test LearningReportResponse model structure."""
    from serve.feedback_routes import LearningReportResponse

    report = LearningReportResponse(
        user_id_hash="hash",
        total_feedback_cards=10,
        overall_satisfaction=4.5,
        improvement_trend=0.2,
        preferred_styles=["direct"],
        summary="Summary text",
        recommendations={"key": "value"},
    )

    assert report.user_id_hash == "hash"
    assert report.total_feedback_cards == 10


def test_system_metrics_model_structure():
    """Test SystemMetricsResponse model structure."""
    from serve.feedback_routes import SystemMetricsResponse

    metrics = SystemMetricsResponse(
        cards_captured=100,
        patterns_identified=20,
        policies_updated=5,
        validations_passed=5,
        validations_failed=0,
        total_cards=500,
        total_patterns=50,
        total_updates=10,
    )

    assert metrics.cards_captured == 100
    assert metrics.total_cards == 500
