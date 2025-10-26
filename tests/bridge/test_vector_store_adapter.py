"""Tests for VectorStoreAdapter high priority integration tasks."""

import asyncio
from types import SimpleNamespace

import pytest

from labs.bridge.llm_wrappers.openai_modulated_service import (
    VectorStoreAdapter,
    VectorStoreConfig,
    VectorStoreProvider,
)


class _StubPineconeClient:
    """Stub client emulating pinecone query interface."""

    def __init__(self, matches):
        self._matches = matches

    def query(self, **_kwargs):
        return SimpleNamespace(matches=self._matches)


@pytest.mark.unit
def test_vector_store_adapter_normalizes_pinecone_matches():
    """Ensure TODO-HIGH-BRIDGE-LLM-m7n8o9p0 normalization produces plain dicts."""

    match_objects = [
        SimpleNamespace(id="doc-1", score=0.12, metadata={"text": "alpha"}),
        SimpleNamespace(id="doc-2", score=0.34, metadata={"text": "beta"}),
    ]

    config = VectorStoreConfig(
        provider=VectorStoreProvider.PINECONE,
        endpoint="unused",
        api_key="test-key",
    )

    adapter = VectorStoreAdapter(config)
    adapter._client = _StubPineconeClient(match_objects)
    adapter._initialized = True

    results = asyncio.run(adapter.search([0.1, 0.2, 0.3], top_k=2))

    assert isinstance(results, list)
    assert results[0]["id"] == "doc-1"
    assert isinstance(results[0]["metadata"], dict)
    assert pytest.approx(results[1]["score"], rel=1e-6) == 0.34


@pytest.mark.unit
def test_vector_store_adapter_handles_dict_matches():
    """Dict matches remain stable after normalization."""

    match_dicts = [
        {"id": "doc-10", "score": 0.5, "metadata": {"topic": "guardian"}},
        {"id": "doc-11", "score": 0.7, "metadata": {"topic": "dream"}},
    ]

    config = VectorStoreConfig(
        provider=VectorStoreProvider.QDRANT,
        endpoint="unused",
    )

    adapter = VectorStoreAdapter(config)
    adapter._client = SimpleNamespace(
        search=lambda **_kwargs: [SimpleNamespace(id=match["id"], score=match["score"], payload=match["metadata"]) for match in match_dicts]
    )
    adapter._initialized = True

    results = asyncio.run(adapter.search([0.2, 0.1, 0.4], top_k=2))

    assert results[0]["metadata"]["topic"] == "guardian"
    assert results[1]["metadata"]["topic"] == "dream"
