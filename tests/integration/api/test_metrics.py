from fastapi.testclient import TestClient
from serve.main import app

client = TestClient(app)

from prometheus_client.parser import text_string_to_metric_families

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200

    # Use the Prometheus client parser to validate the metrics
    metrics = {family.name: family for family in text_string_to_metric_families(response.text)}

    assert 'http_requests' in metrics
    assert 'http_request_duration_seconds' in metrics
    assert 'matriz_operations' in metrics
    assert 'matriz_operation_duration_milliseconds' in metrics
    assert 'matriz_active_thoughts' in metrics
    assert 'memory_entries' in metrics
    assert 'cache_hits_total' in metrics
    assert 'cache_misses_total' in metrics
    assert 'lukhas_system_info' in metrics
    assert 'lukhas_memory_bytes' in metrics

def test_metrics_are_updated():
    # Make a request to an endpoint to trigger the middleware
    client.get("/healthz")

    response = client.get("/metrics")
    assert response.status_code == 200

    metrics = {family.name: family for family in text_string_to_metric_families(response.text)}

    # Check that the http_requests_total metric has been incremented
    http_requests_metric = metrics['http_requests']
    found = False
    for sample in http_requests_metric.samples:
        if sample.labels == {'method': 'GET', 'endpoint': '/healthz', 'status': '200'}:
            assert sample.value == 1.0
            found = True
            break
    assert found
