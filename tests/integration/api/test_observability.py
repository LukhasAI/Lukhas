from fastapi.testclient import TestClient
from serve.main import app

client = TestClient(app)

def test_metrics_endpoint():
    # Make a request to a health check endpoint to generate some metrics
    client.get("/healthz")

    # Now, get the metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert 'method="GET"' in response.text
    assert 'endpoint="/healthz"' in response.text
    assert 'status_code="200"' in response.text
