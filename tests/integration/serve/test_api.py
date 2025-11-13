# tests/integration/serve/test_api.py
import os
from unittest.mock import MagicMock, patch


def test_healthz_endpoint(client_no_auth):
    """Test the /healthz endpoint."""
    response = client_no_auth.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_models_endpoint(client_no_auth):
    """Test the /v1/models endpoint."""
    response = client_no_auth.get("/v1/models")
    assert response.status_code == 200
    assert response.json()["object"] == "list"

@patch("serve.main.index_manager")
def test_create_embeddings_endpoint(mock_index_manager, client_no_auth):
    """Test the /v1/embeddings endpoint."""
    payload = {"input": "test"}
    response = client_no_auth.post("/v1/embeddings", json=payload)
    assert response.status_code == 200
    assert response.json()["object"] == "list"

def test_create_chat_completion_endpoint(client_no_auth):
    """Test the /v1/chat/completions endpoint."""
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Hello"}],
    }
    response = client_no_auth.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert response.json()["object"] == "chat.completion"

def test_dreams_endpoint(client_no_auth):
    """Test the /v1/dreams endpoint."""
    with patch.dict(os.environ, {"LUKHAS_API_KEY": "test-key"}):
        headers = {"X-API-Key": "test-key"}
        payload = {"seed": "test"}
        response = client_no_auth.post("/v1/dreams", headers=headers, json=payload)
        assert response.status_code == 200
        assert "id" in response.json()

@patch("serve.feedback_routes.feedback_system")
def test_capture_feedback_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/capture endpoint."""
    mock_feedback_system.capture_feedback.return_value = MagicMock(
        card_id="test_card", rating=MagicMock(value=5), timestamp=123.456
    )
    payload = {"action_id": "test_action", "rating": 5}
    response = client_no_auth.post("/feedback/capture", json=payload)
    assert response.status_code == 200
    assert "card_id" in response.json()

@patch("serve.feedback_routes.feedback_system")
def test_capture_batch_feedback_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/batch endpoint."""
    mock_feedback_system.capture_feedback.return_value = MagicMock(
        card_id="test_card", rating=MagicMock(value=5), timestamp=123.456
    )
    payload = [{"action_id": "test_action", "rating": 5}]
    response = client_no_auth.post("/feedback/batch", json=payload)
    assert response.status_code == 200
    assert len(response.json()) == 1

@patch("serve.feedback_routes.feedback_system")
def test_get_learning_report_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/report/{user_id} endpoint."""
    mock_feedback_system.explain_learning.return_value = MagicMock(
        user_id_hash="test_hash",
        total_feedback_cards=1,
        overall_satisfaction=5.0,
        improvement_trend=1.0,
        preferred_styles=["test"],
        recommended_adjustments={},
    )
    response = client_no_auth.get("/feedback/report/test_user")
    assert response.status_code == 200
    assert "user_id_hash" in response.json()

@patch("serve.feedback_routes.feedback_system")
def test_get_system_metrics_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/metrics endpoint."""
    mock_feedback_system.get_metrics.return_value = {
        "cards_captured": 1,
        "patterns_identified": 1,
        "policies_updated": 1,
        "validations_passed": 1,
        "validations_failed": 0,
        "total_cards": 1,
        "total_patterns": 1,
        "total_updates": 1,
    }
    response = client_no_auth.get("/feedback/metrics")
    assert response.status_code == 200
    assert "cards_captured" in response.json()

@patch("serve.feedback_routes.feedback_system")
def test_trigger_learning_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/trigger-learning endpoint."""
    mock_feedback_system.feedback_cards = [MagicMock()] * 10
    response = client_no_auth.post("/feedback/trigger-learning")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "triggered"

@patch("serve.feedback_routes.feedback_system")
def test_health_check_endpoint(mock_feedback_system, client_no_auth):
    """Test the /feedback/health endpoint."""
    mock_feedback_system.get_metrics.return_value = {"total_cards": 1}
    response = client_no_auth.get("/feedback/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"

@patch("serve.openai_routes.get_service")
def test_modulated_chat_endpoint(mock_get_service, client_no_auth):
    """Test the /openai/chat endpoint."""
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    mock_service.generate.return_value = {"response": "test"}
    payload = {"prompt": "test"}
    response = client_no_auth.post("/openai/chat", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()

@patch("serve.openai_routes.get_service")
def test_modulated_chat_stream_endpoint(mock_get_service, client_no_auth):
    """Test the /openai/chat/stream endpoint."""
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    async def mock_stream():
        yield "test"
    mock_service.generate_stream.return_value = mock_stream()
    payload = {"prompt": "test"}
    response = client_no_auth.post("/openai/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert response.text == "test"
