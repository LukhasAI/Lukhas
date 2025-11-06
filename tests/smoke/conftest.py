import os

import pytest
from serve.main import app
from starlette.testclient import TestClient


@pytest.fixture
def app():
    from serve.dreams_api import router as dreams_router
    from serve.main import app
    app.include_router(dreams_router)
    return app

@pytest.fixture
def client(app):
    """Create test client with auth."""
    os.environ["LUKHAS_API_KEY"] = "test_api_key"
    return TestClient(app)
