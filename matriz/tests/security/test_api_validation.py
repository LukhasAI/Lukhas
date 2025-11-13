
from unittest.mock import patch

import pytest

# --- Test Payloads ---
SQL_INJECTION_ATTEMPT = {"node_type": "math", "config": {"expression": "<>'\"&"}}
XSS_INJECTION_ATTEMPT = {"node_type": "validator", "config": {"rule": "<script>alert('XSS')</script>"}}
VALID_NODE_CONFIG = {"node_type": "math", "config": {"precision": 16}}
DEEPLY_NESTED_CONFIG = {"node_type": "math", "config": {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": "j"}}}}}}}}}}
# --- Tests ---

@pytest.mark.security
def test_oversized_request(test_client):
    with patch('matriz.interfaces.api_server.MAX_REQUEST_SIZE', 10):
        response = test_client.post("/query", json={"query": "a" * 20})
        assert response.status_code == 413

@pytest.mark.security
def test_injection_sanitization(test_client):
    headers = {"Authorization": "Bearer test"}
    response = test_client.post("/system/nodes", json=SQL_INJECTION_ATTEMPT, headers=headers)
    assert response.status_code == 400
    assert "empty after sanitization" in response.json()["detail"]

@pytest.mark.security
def test_xss_sanitization(test_client):
    headers = {"Authorization": "Bearer test"}
    response = test_client.post("/system/nodes", json=XSS_INJECTION_ATTEMPT, headers=headers)
    assert response.status_code == 400

@pytest.mark.security
def test_type_confusion_in_query(test_client):
    response = test_client.post("/query", json={"query": [1, 2, 3]})
    assert response.status_code == 422

@pytest.mark.security
def test_rate_limit_exceeded(test_client):
    with patch('matriz.interfaces.api_server.RATE_LIMIT_REQUESTS', 5):
        for _ in range(6):
            response = test_client.get("/health")
        assert response.status_code == 429

@pytest.mark.security
def test_unauthorized_access(test_client):
    response = test_client.get("/system/nodes")
    assert response.status_code == 401

@pytest.mark.security
def test_authorized_access(test_client):
    response = test_client.get("/system/nodes", headers={"Authorization": "Bearer test"})
    assert response.status_code == 200

@pytest.mark.security
def test_invalid_node_type(test_client):
    response = test_client.post("/system/nodes", json={"node_type": "foo", "config": {}}, headers={"Authorization": "Bearer test"})
    assert response.status_code == 422

@pytest.mark.security
def test_deeply_nested_config(test_client):
    response = test_client.post("/system/nodes", json=DEEPLY_NESTED_CONFIG, headers={"Authorization": "Bearer test"})
    assert response.status_code == 400

@pytest.mark.security
def test_malformed_json(test_client):
    response = test_client.post("/query", data="{", headers={"Content-Type": "application/json"})
    assert response.status_code == 422

@pytest.mark.security
def test_query_too_long(test_client):
    response = test_client.post("/query", json={"query": "a" * 10001})
    assert response.status_code == 422

@pytest.mark.security
def test_empty_query(test_client):
    response = test_client.post("/query", json={"query": ""})
    assert response.status_code == 422

@pytest.mark.security
def test_config_too_many_items(test_client):
    config = {f"k{i}": i for i in range(51)}
    response = test_client.post("/system/nodes", json={"node_type": "math", "config": config}, headers={"Authorization": "Bearer test"})
    assert response.status_code == 422

@pytest.mark.security
def test_invalid_node_name_pattern(test_client):
    response = test_client.post("/system/nodes", json={"node_type": "m@th", "config": {}}, headers={"Authorization": "Bearer test"})
    assert response.status_code == 422

@pytest.mark.security
def test_get_nonexistent_endpoint(test_client):
    response = test_client.get("/nonexistent")
    assert response.status_code == 404

@pytest.mark.security
def test_unsupported_method(test_client):
    response = test_client.get("/query")
    assert response.status_code == 405

@pytest.mark.security
def test_valid_node_creation(test_client):
    response = test_client.post("/system/nodes", json=VALID_NODE_CONFIG, headers={"Authorization": "Bearer test"})
    assert response.status_code == 201

@pytest.mark.security
def test_path_traversal_in_params(test_client):
    response = test_client.get("/system/nodes/../../etc/passwd", headers={"Authorization": "Bearer test"})
    assert response.status_code == 404

@pytest.mark.security
def test_unauthorized_node_creation(test_client):
    response = test_client.post("/system/nodes", json=VALID_NODE_CONFIG)
    assert response.status_code == 401

@pytest.mark.security
def test_valid_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200

@pytest.mark.security
def test_server_header_is_generic(test_client):
    response = test_client.get("/")
    assert "server" not in response.headers or "uvicorn" not in response.headers["server"]
