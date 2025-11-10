import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from serve.feedback_routes import router as feedback_router
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from serve.main import HeadersMiddleware

# Create a mock auth middleware that bypasses authentication for most tests
class MockAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user_id = "test_user"
        response = await call_next(request)
        return response

# Main app for testing with authentication mocked
app = FastAPI()
app.include_router(feedback_router)
app.add_middleware(MockAuthMiddleware)
app.add_middleware(HeadersMiddleware)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def mock_feedback_system():
    """Auto-used fixture to mock the FeedbackCardSystem."""
    with patch('serve.feedback_routes.feedback_system', autospec=True) as mock_system:
        mock_system.capture_feedback.return_value = MagicMock(card_id="card_123", rating=MagicMock(value=5), timestamp=1730000000.0)
        mock_system.explain_learning.return_value = MagicMock(
            user_id_hash="hashed_user_id", total_feedback_cards=10, overall_satisfaction=4.5,
            improvement_trend=0.2, preferred_styles=["direct", "concise"], recommended_adjustments={"tone": "more formal"}
        )
        mock_system.get_metrics.return_value = {
            "cards_captured": 100, "patterns_identified": 20, "policies_updated": 5, "validations_passed": 5,
            "validations_failed": 0, "total_cards": 500, "total_patterns": 50, "total_updates": 10,
        }
        mock_system.feedback_cards = [MagicMock()] * 15
        yield mock_system

# Tests for POST /feedback/capture
def test_capture_feedback_success(client, mock_feedback_system):
    response = client.post("/feedback/capture", json={"action_id": "action_123", "rating": 5, "note": "Great!", "user_id": "user_abc"})
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["card_id"] == "card_123"
    assert json_response["rating"] == 5
    mock_feedback_system.capture_feedback.assert_called_once()

def test_capture_feedback_validation_error(client):
    response = client.post("/feedback/capture", json={"action_id": "action_123", "rating": 6})
    assert response.status_code == 422

def test_capture_feedback_server_error(client, mock_feedback_system):
    mock_feedback_system.capture_feedback.side_effect = Exception("Database error")
    response = client.post("/feedback/capture", json={"action_id": "action_123", "rating": 4, "user_id": "user_abc"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Database error"}

# Tests for POST /feedback/batch
def test_capture_batch_feedback_success(client, mock_feedback_system):
    response = client.post("/feedback/batch", json=[{"action_id": "action_1", "rating": 5}, {"action_id": "action_2", "rating": 4}])
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert mock_feedback_system.capture_feedback.call_count == 2

def test_capture_batch_feedback_with_errors(client, mock_feedback_system):
    mock_feedback_system.capture_feedback.side_effect = [MagicMock(card_id="card_1", rating=MagicMock(value=5), timestamp=1.0), Exception("Processing error")]
    response = client.post("/feedback/batch", json=[{"action_id": "action_1", "rating": 5}, {"action_id": "action_2", "rating": 3}])
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert mock_feedback_system.capture_feedback.call_count == 2

def test_capture_batch_feedback_empty_list(client, mock_feedback_system):
    response = client.post("/feedback/batch", json=[])
    assert response.status_code == 200
    assert response.json() == []
    mock_feedback_system.capture_feedback.assert_not_called()

# Tests for GET /feedback/report/{user_id}
def test_get_learning_report_success(client, mock_feedback_system):
    response = client.get("/feedback/report/user_xyz")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["user_id_hash"] == "hashed_user_id"
    mock_feedback_system.explain_learning.assert_called_once_with("user_xyz")

def test_get_learning_report_not_found(client, mock_feedback_system):
    mock_feedback_system.explain_learning.side_effect = ValueError("User not found")
    response = client.get("/feedback/report/unknown_user")
    assert response.status_code == 500
    assert response.json() == {"detail": "User not found"}

# Tests for GET /feedback/metrics
def test_get_system_metrics_success(client, mock_feedback_system):
    response = client.get("/feedback/metrics")
    assert response.status_code == 200
    assert response.json()["cards_captured"] == 100
    mock_feedback_system.get_metrics.assert_called_once()

# Tests for POST /feedback/trigger-learning
def test_trigger_learning_success(client, mock_feedback_system):
    mock_feedback_system.feedback_cards = [MagicMock()] * 20
    response = client.post("/feedback/trigger-learning")
    assert response.status_code == 200
    assert response.json()["status"] == "triggered"

def test_trigger_learning_not_enough_feedback(client, mock_feedback_system):
    mock_feedback_system.feedback_cards = [MagicMock()] * 5
    response = client.post("/feedback/trigger-learning")
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"

def test_trigger_learning_error(client, mock_feedback_system):
    cards_mock = MagicMock()
    cards_mock.__getitem__.side_effect = IndexError("Slicing failed")
    cards_mock.__len__.return_value = 20
    mock_feedback_system.feedback_cards = cards_mock
    response = client.post("/feedback/trigger-learning")
    assert response.status_code == 500
    assert response.json() == {"detail": "Slicing failed"}

# Tests for GET /feedback/health
def test_health_check_healthy(client, mock_feedback_system):
    response = client.get("/feedback/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check_unhealthy(client, mock_feedback_system):
    mock_feedback_system.get_metrics.side_effect = Exception("Storage disconnected")
    response = client.get("/feedback/health")
    assert response.status_code == 200
    assert response.json()["status"] == "unhealthy"

# Authentication and Rate Limiting Tests
def test_unauthenticated_request_on_protected_route():
    """Test that an unauthenticated request to a protected route is rejected."""
    from serve.main import app as main_app
    with patch('serve.middleware.strict_auth.get_auth_system') as mock_auth_system:
        # Simulate the JWT verification failing
        mock_auth_system.return_value.verify_jwt.return_value = None
        with TestClient(main_app) as unauth_client:
            # Target a known protected route (/v1/*) instead of the feedback route
            response = unauth_client.get("/v1/models", headers={"Authorization": "Bearer invalid-token"})
            assert response.status_code == 401

def test_rate_limit_headers_present(client):
    """Test that rate limit headers are present in the response."""
    response = client.get("/feedback/health")
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
