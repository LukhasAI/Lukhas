import sys
from typing import Any, Dict
from unittest.mock import MagicMock

from pydantic import BaseModel


# Create a fake Pydantic model to satisfy the router's type hint
class FakeHealthStatus(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    components: Dict[str, Any]

# Mock the problematic import before it's accessed
# This allows the test to run without the 'interfaces' module being present.
models_mock = MagicMock()
models_mock.HealthStatus = FakeHealthStatus

sys.modules['interfaces'] = MagicMock()
sys.modules['interfaces.api'] = MagicMock()
sys.modules['interfaces.api.v1'] = MagicMock()
sys.modules['interfaces.api.v1.rest'] = MagicMock()
sys.modules['interfaces.api.v1.rest.models'] = models_mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Now that the mock is in place, we can import the router
from matriz.matriz_health_router import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_get_health():
    """
    Tests the health check endpoint.
    Verifies that the endpoint returns a 200 status code and the correct
    JSON payload structure.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], float)
    assert data["components"] == {"core": True}
