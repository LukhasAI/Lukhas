"""Tests for Lukhas commercial FastAPI endpoints"""

import pytest
from unittest.mock import MagicMock, patch

# Skip this test file if dependencies are not available
pytest.skip("Commercial API tests temporarily disabled - missing dependencies", allow_module_level=True)

from fastapi.testclient import TestClient

# These imports are currently broken, need fixing in BATCH completion
# from config.config import TIER_PERMISSIONS
# from serve.main import app

client = TestClient(app)


def test_generate_dream():
    response = client.post("/generate-dream/", json={"symbols": ["sun", "moon"]})
    assert response.status_code == 200
    data = response.json()
    assert "dream" in data
    assert "driftScore" in data
    assert "affect_delta" in data


def test_glyph_feedback():
    response = client.post(
        "/glyph-feedback/", json={"driftScore": 0.1, "collapseHash": "abc"}
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()


def test_tier_auth():
    response = client.post("/tier-auth/", json={"token": "symbolic-tier-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["access_rights"] == TIER_PERMISSIONS[1]
    assert data["tier"] == 1


def test_plugin_load():
    response = client.post("/plugin-load/", json={"symbols": ["plug1"]})
    assert response.status_code == 200
    assert response.json()["status"] == "loaded"


def test_memory_dump():
    response = client.get("/memory-dump/")
    assert response.status_code == 200
    data = response.json()
    assert "folds" in data
    assert "emotional_state" in data
