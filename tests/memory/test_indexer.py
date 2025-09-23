"""Unit tests for memory Indexer."""

import pytest
from unittest.mock import Mock, MagicMock
from memory.indexer import Indexer, Embeddings, _fingerprint
from memory.backends.pgvector_store import VectorDoc

def test_fingerprint():
    text1 = "hello world"
    text2 = "hello world  "  # trailing spaces
    text3 = "hello world!"

    fp1 = _fingerprint(text1)
    fp2 = _fingerprint(text2)
    fp3 = _fingerprint(text3)

    assert fp1 == fp2  # spaces are stripped
    assert fp1 != fp3  # different content
    assert len(fp1) == 64  # SHA256 hex length

def test_embeddings_placeholder():
    embeddings = Embeddings()
    result = embeddings.embed("test text")
    assert len(result) == 1536
    assert all(x == 0.0 for x in result)

@pytest.fixture
def mock_store():
    store = Mock()
    store.add.return_value = "doc-id-123"
    store.search.return_value = [("doc-id-123", 0.85)]
    return store

@pytest.fixture
def indexer(mock_store):
    return Indexer(mock_store)

def test_indexer_initialization(mock_store):
    indexer = Indexer(mock_store)
    assert indexer.store == mock_store
    assert isinstance(indexer.emb, Embeddings)

    # Test with custom embeddings
    custom_emb = Mock()
    indexer2 = Indexer(mock_store, custom_emb)
    assert indexer2.emb == custom_emb

def test_indexer_upsert(indexer, mock_store):
    text = "test memory"
    meta = {"lane": "candidate", "timestamp": 1234567890}

    result = indexer.upsert(text, meta)

    assert result == "doc-id-123"
    mock_store.add.assert_called_once()

    # Verify VectorDoc was created correctly
    call_args = mock_store.add.call_args[0][0]
    assert isinstance(call_args, VectorDoc)
    assert call_args.text == text
    assert call_args.meta == meta
    assert len(call_args.embedding) == 1536
    assert call_args.id == _fingerprint(text)

def test_indexer_search_text(indexer, mock_store):
    query = "search query"
    k = 5
    filters = {"lane": "candidate"}

    result = indexer.search_text(query, k=k, filters=filters)

    assert result == [("doc-id-123", 0.85)]
    mock_store.search.assert_called_once()

    # Verify search was called with embedding and parameters
    call_args = mock_store.search.call_args
    assert len(call_args[0][0]) == 1536  # embedding vector
    assert call_args[1]["k"] == k
    assert call_args[1]["filters"] == filters