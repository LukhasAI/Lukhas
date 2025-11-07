# tests/integration/serve/conftest.py
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_no_auth():
    with patch.dict(os.environ, {'LUKHAS_DEV_MODE': 'true'}):
        from serve.main import app
        return TestClient(app)
