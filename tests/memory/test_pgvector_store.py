"""Unit tests for PgVectorStore."""

import pytest
from memory.backends.pgvector_store import PgVectorStore, VectorDoc


class MockPgClient:
    """Mock database client for testing."""
    def __init__(self):
        self.data = {}
        self.call_log = []

    def execute(self, query, params=None):
        self.call_log.append((query, params))
        return {"affected_rows": 1}

@pytest.fixture
def mock_store():
    return PgVectorStore(MockPgClient(), table="test_table", dim=128)

def test_vector_doc_creation():
    doc = VectorDoc(
        id="test-123",
        text="Hello world",
        embedding=[0.1, 0.2, 0.3],
        meta={"source": "test"}
    )
    assert doc.id == "test-123"
    assert doc.text == "Hello world"
    assert len(doc.embedding) == 3
    assert doc.meta["source"] == "test"

def test_pgvector_store_init(mock_store):
    assert mock_store.table == "test_table"
    assert mock_store.dim == 128
    assert isinstance(mock_store.conn, MockPgClient)

def test_stats_method(mock_store):
    stats = mock_store.stats()
    assert stats["table"] == "test_table"
    assert stats["dim"] == 128
    assert stats["count"] is None  # TODO: implement actual count

def test_add_not_implemented(mock_store):
    doc = VectorDoc("id1", "text", [0.1] * 128, {})
    with pytest.raises(NotImplementedError):
        mock_store.add(doc)

def test_bulk_add_not_implemented(mock_store):
    docs = [VectorDoc("id1", "text", [0.1] * 128, {})]
    with pytest.raises(NotImplementedError):
        mock_store.bulk_add(docs)

def test_search_not_implemented(mock_store):
    with pytest.raises(NotImplementedError):
        mock_store.search([0.1] * 128, k=5)

def test_delete_not_implemented(mock_store):
    with pytest.raises(NotImplementedError):
        mock_store.delete(id="test-id")
