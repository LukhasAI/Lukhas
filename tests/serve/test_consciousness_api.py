import pytest
from fastapi.testclient import TestClient

from serve.main import app

client = TestClient(app)


def test_query_consciousness():
    """
    Test the consciousness query endpoint.
    """
    response = client.post("/api/v1/consciousness/query")
    assert response.status_code == 200
    assert response.json() == {"response": "The current awareness level is high."}


def test_dream_consciousness():
    """
    Test the consciousness dream endpoint.
    """
    response = client.post("/api/v1/consciousness/dream")
    assert response.status_code == 200
    assert response.json() == {"dream_id": "dream-123", "status": "generating"}


def test_memory_consciousness():
    """
    Test the consciousness memory endpoint.
    """
    response = client.get("/api/v1/consciousness/memory")
    assert response.status_code == 200
    assert response.json() == {"memory_folds": 1024, "recall_accuracy": 0.98}
