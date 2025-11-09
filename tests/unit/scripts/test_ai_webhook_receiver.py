import sys
from pathlib import Path
from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path to allow relative imports in the script
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bridge.queue.redis_queue import Task, TaskPriority, TaskType
from scripts.ai_webhook_receiver import app, map_status_to_priority, map_status_to_task_type


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_redis_queue():
    """Mock the RedisTaskQueue to prevent actual Redis calls."""
    with patch("scripts.ai_webhook_receiver.RedisTaskQueue", autospec=True) as mock_queue_class:
        mock_queue_instance = mock_queue_class.return_value
        # The mock for the async context manager
        mock_async_context = mock_queue_instance.__aenter__.return_value
        mock_async_context.enqueue = AsyncMock()
        mock_async_context.queue_size = AsyncMock(return_value=123)
        mock_async_context.peek = AsyncMock(return_value=[{"task_id": "1"}, {"task_id": "2"}])
        yield mock_async_context


# --- Tests for helper functions ---

@pytest.mark.parametrize("status, error, expected_priority", [
    ("error", "some import boundary violation", TaskPriority.CRITICAL),
    ("failed", "critical trinity architecture issue", TaskPriority.CRITICAL),
    ("error", "regular error", TaskPriority.HIGH),
    ("failed", None, TaskPriority.HIGH),
    ("waiting_for_user", None, TaskPriority.MEDIUM),
    ("completed", None, TaskPriority.LOW),
    ("info", None, TaskPriority.LOW),
    ("unknown_status", None, TaskPriority.LOW),
])
def test_map_status_to_priority(status, error, expected_priority):
    """Test the status to priority mapping logic."""
    assert map_status_to_priority(status, error) == expected_priority


@pytest.mark.parametrize("status, message, expected_task_type", [
    ("completed", "fixed a bug", TaskType.BUG_FIX),
    ("failed", "something failed", TaskType.BUG_FIX),
    ("completed", "refactored the code", TaskType.REFACTORING),
    ("completed", "added documentation", TaskType.DOCUMENTATION),
    ("completed", "created a new test", TaskType.TEST_CREATION),
    ("completed", "fixed an architecture violation", TaskType.ARCHITECTURAL_VIOLATION),
    ("completed", "some other message", TaskType.TODO_COMMENT),
    ("completed", None, TaskType.TODO_COMMENT),
])
def test_map_status_to_task_type(status, message, expected_task_type):
    """Test the status/message to task type mapping logic."""
    assert map_status_to_task_type(status, message) == expected_task_type


# --- Tests for /webhook/ai-status endpoint ---

def test_receive_ai_status_success(client, mock_redis_queue):
    """Test a successful webhook call."""
    payload = {
        "agent": "jules",
        "status": "completed",
        "message": "Plan executed successfully",
        "pr_number": 42,
    }
    response = client.post("/webhook/ai-status", json=payload)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["success"] is True
    assert "task_id" in json_response
    assert json_response["priority"] == "LOW"
    assert json_response["message"] == "Task enqueued successfully"

    mock_redis_queue.enqueue.assert_called_once_with(ANY)
    enqueued_task = mock_redis_queue.enqueue.call_args[0][0]
    assert isinstance(enqueued_task, Task)
    assert enqueued_task.pr_number == 42
    assert enqueued_task.agent == "jules"


def test_receive_ai_status_enqueue_failure(client, mock_redis_queue):
    """Test the webhook when enqueuing to Redis fails."""
    mock_redis_queue.enqueue.side_effect = Exception("Redis connection error")
    payload = {"agent": "jules", "status": "completed", "message": "A message"}
    response = client.post("/webhook/ai-status", json=payload)
    assert response.status_code == 500
    assert "Failed to enqueue task" in response.json()["detail"]


def test_invalid_payload(client, mock_redis_queue):
    """Test an invalid payload returns a 422 error."""
    payload = {"agent": "jules"}  # Missing 'status'
    response = client.post("/webhook/ai-status", json=payload)
    assert response.status_code == 422
    mock_redis_queue.enqueue.assert_not_called()


# --- Test for /health endpoint ---

def test_health_check_success(client, mock_redis_queue):
    """Test the health check endpoint successfully."""
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert json_response["redis_connected"] is True
    assert json_response["queue_size"] == 123


def test_health_check_redis_failure(client, mock_redis_queue):
    """Test the health check endpoint when Redis connection fails."""
    mock_redis_queue.queue_size.side_effect = Exception("Redis connection error")
    response = client.get("/health")
    assert response.status_code == 503
    json_response = response.json()
    assert json_response["status"] == "unhealthy"
    assert json_response["redis_connected"] is False
    assert "Redis connection error" in json_response["error"]


# --- Test for /queue/status endpoint ---

def test_queue_status_success(client, mock_redis_queue):
    """Test the queue status endpoint successfully."""
    response = client.get("/queue/status")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["queue_size"] == 123
    assert len(json_response["tasks"]) == 2
    assert json_response["tasks"] == [{"task_id": "1"}, {"task_id": "2"}]
    mock_redis_queue.peek.assert_called_once_with(count=20)


def test_queue_status_failure(client, mock_redis_queue):
    """Test the queue status endpoint when Redis fails."""
    mock_redis_queue.queue_size.side_effect = Exception("Redis error")
    response = client.get("/queue/status")
    assert response.status_code == 500
    assert "Redis error" in response.json()["detail"]
