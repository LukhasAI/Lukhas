"""Tests for the Prometheus configuration and metrics endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Mock modules that are not needed for these tests
import sys
sys.modules['async_lru'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()
sys.modules['streamlit'] = MagicMock()
sys.modules['serve.utils.cache_manager'] = MagicMock()

# A mock middleware that just passes the request through
class PassthroughMiddleware:
    def __init__(self, app, *args, **kwargs):  # Accept any args
        self.app = app
    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)

sys.modules['serve.middleware.prometheus'] = MagicMock(PrometheusMiddleware=PassthroughMiddleware)
sys.modules['serve.middleware.cache_middleware'] = MagicMock(CacheMiddleware=PassthroughMiddleware)

# Mock the deep import path for StrictAuthMiddleware
sys.modules['lukhas_website'] = MagicMock()
sys.modules['lukhas_website.lukhas'] = MagicMock()
sys.modules['lukhas_website.lukhas.api'] = MagicMock()
sys.modules['lukhas_website.lukhas.api.middleware'] = MagicMock()
sys.modules['lukhas_website.lukhas.api.middleware.strict_auth'] = MagicMock(StrictAuthMiddleware=PassthroughMiddleware)

from serve.main import app
from lukhas.observability.prometheus_config import (
    REQUEST_DURATION_SECONDS,
    REQUESTS_TOTAL,
    ERRORS_TOTAL,
)


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


def test_metrics_are_registered():
    """Verify that the Prometheus metrics are created."""
    assert REQUEST_DURATION_SECONDS is not None
    assert REQUESTS_TOTAL is not None
    assert ERRORS_TOTAL is not None


def test_metrics_endpoint(client):
    """Test the /metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('text/plain')

    content = response.content.decode('utf-8')
    assert 'request_duration_seconds' in content
    assert 'requests_total' in content
    assert 'errors_total' in content
