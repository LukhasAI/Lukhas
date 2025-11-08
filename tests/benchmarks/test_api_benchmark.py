"""Benchmarks for the API endpoints."""

import pytest
from fastapi.testclient import TestClient
from serve.main import app


@pytest.fixture
def client():
    """Provides a TestClient for the FastAPI app."""
    return TestClient(app)

def test_models_endpoint_benchmark(benchmark, client):
    """Benchmark the /v1/models endpoint."""
    benchmark(client.get, "/v1/models")

def test_embeddings_endpoint_benchmark(benchmark, client):
    """Benchmark the /v1/embeddings endpoint."""
    benchmark(client.post, "/v1/embeddings", json={"input": "test"})

def test_chat_completions_endpoint_benchmark(benchmark, client):
    """Benchmark the /v1/chat/completions endpoint."""
    benchmark(client.post, "/v1/chat/completions", json={"messages": [{"role": "user", "content": "test"}]})
