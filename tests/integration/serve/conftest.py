# tests/integration/serve/conftest.py
import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

@pytest.fixture
def client_no_auth():
    with patch.dict(os.environ, {'LUKHAS_DEV_MODE': 'true'}):
        from serve.main import app
        return TestClient(app)
