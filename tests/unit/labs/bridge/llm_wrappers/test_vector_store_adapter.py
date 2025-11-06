
import pytest
import sys
from unittest.mock import MagicMock, AsyncMock

from labs.bridge.llm_wrappers.openai_modulated_service import (
    VectorStoreAdapter,
    VectorStoreConfig,
    VectorStoreProvider,
)

# Test data
TEST_EMBEDDING = [0.1, 0.2, 0.3]
TEST_METADATA = {"key": "value"}

@pytest.mark.asyncio
async def test_faiss_adapter(mocker):
    """Integration test for the FAISS VectorStoreAdapter."""
    mock_faiss = MagicMock()
    mock_numpy = MagicMock()
    mocker.patch.dict(sys.modules, {"faiss": mock_faiss, "numpy": mock_numpy})

    config = VectorStoreConfig(provider=VectorStoreProvider.FAISS, endpoint="", dimension=3)
    adapter = VectorStoreAdapter(config)

    mock_index = MagicMock()
    mock_faiss.IndexFlatL2.return_value = mock_index
    mock_numpy.array.return_value.astype.return_value = "mock_array"

    await adapter.initialize()
    mock_faiss.IndexFlatL2.assert_called_once_with(3)

    await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    mock_index.add.assert_called_once()

    mock_index.search.return_value = ([[0.5]], [[0]])
    adapter._metadata = [TEST_METADATA]
    results = await adapter.search(TEST_EMBEDDING, top_k=1)
    mock_index.search.assert_called_once()
    assert len(results) == 1
    assert results[0]['metadata'] == TEST_METADATA

@pytest.mark.asyncio
async def test_pinecone_adapter(mocker):
    """Integration test for the Pinecone VectorStoreAdapter."""
    mock_pinecone = MagicMock()
    mocker.patch.dict(sys.modules, {"pinecone": mock_pinecone})

    config = VectorStoreConfig(provider=VectorStoreProvider.PINECONE, api_key="test", endpoint="test")
    adapter = VectorStoreAdapter(config)

    mock_index = MagicMock()
    mock_pinecone.Index.return_value = mock_index

    await adapter.initialize()
    mock_pinecone.init.assert_called_once()

    await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    mock_index.upsert.assert_called_once()

    mock_match = MagicMock()
    mock_match.to_dict.return_value = {"id": "1", "score": 0.9, "metadata": TEST_METADATA}
    mock_index.query.return_value.matches = [mock_match]
    results = await adapter.search(TEST_EMBEDDING, top_k=1)
    mock_index.query.assert_called_once()
    assert len(results) == 1
    assert results[0]['metadata'] == TEST_METADATA

@pytest.mark.asyncio
async def test_weaviate_adapter(mocker):
    """Integration test for the Weaviate VectorStoreAdapter."""
    mock_weaviate = MagicMock()
    mocker.patch.dict(sys.modules, {"weaviate": mock_weaviate})

    config = VectorStoreConfig(provider=VectorStoreProvider.WEAVIATE, api_key="test", endpoint="test")
    adapter = VectorStoreAdapter(config)

    mock_client = MagicMock()
    mock_weaviate.Client.return_value = mock_client
    mock_weaviate.AuthApiKey.return_value = "mock_auth"

    await adapter.initialize()
    mock_weaviate.Client.assert_called_once()

    mock_batch = MagicMock()
    mock_client.batch.__enter__.return_value = mock_batch
    await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    mock_batch.add_data_object.assert_called_once()

    mock_query = MagicMock()
    mock_client.query.get.return_value.with_near_vector.return_value.with_limit.return_value.with_where.return_value = mock_query
    mock_query.do.return_value = {"data": {"Get": {config.index_name: [{"metadata": TEST_METADATA}]}}}
    results = await adapter.search(TEST_EMBEDDING, top_k=1, filter_metadata={"key": "value"})
    assert len(results) == 1
    assert results[0]['metadata'] == TEST_METADATA

@pytest.mark.asyncio
async def test_chroma_adapter(mocker):
    """Integration test for the Chroma VectorStoreAdapter."""
    mock_chromadb = MagicMock()
    mocker.patch.dict(sys.modules, {"chromadb": mock_chromadb})

    config = VectorStoreConfig(provider=VectorStoreProvider.CHROMA, endpoint="test")
    adapter = VectorStoreAdapter(config)

    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_chromadb.Client.return_value = mock_client
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client.get_collection.return_value = mock_collection


    await adapter.initialize()
    mock_chromadb.Client.assert_called_once()

    await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    mock_collection.upsert.assert_called_once()

    mock_collection.query.return_value = {
        "ids": [["1"]], "distances": [[0.5]], "metadatas": [[TEST_METADATA]]
    }
    results = await adapter.search(TEST_EMBEDDING, top_k=1)
    assert len(results) == 1
    assert results[0]['metadata'] == TEST_METADATA

@pytest.mark.asyncio
async def test_qdrant_adapter(mocker):
    """Integration test for the Qdrant VectorStoreAdapter."""
    mock_qdrant_client = MagicMock()
    mock_qdrant_models = MagicMock()
    mocker.patch.dict(sys.modules, {
        "qdrant_client": mock_qdrant_client,
        "qdrant_client.models": mock_qdrant_models,
    })

    config = VectorStoreConfig(provider=VectorStoreProvider.QDRANT, api_key="test", endpoint="test")
    adapter = VectorStoreAdapter(config)

    mock_client = MagicMock()
    mock_qdrant_client.QdrantClient.return_value = mock_client

    await adapter.initialize()
    mock_qdrant_client.QdrantClient.assert_called_once()

    await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    mock_client.upsert.assert_called_once()

    mock_hit = MagicMock(id="1", score=0.9, payload=TEST_METADATA)
    mock_client.search.return_value = [mock_hit]
    results = await adapter.search(TEST_EMBEDDING, top_k=1)
    assert len(results) == 1
    assert results[0]['metadata'] == TEST_METADATA

@pytest.mark.asyncio
async def test_adapter_import_error(mocker):
    """Tests that initialization raises an exception when a provider is not installed."""
    mocker.patch.dict(sys.modules, {"pinecone": None})
    config = VectorStoreConfig(provider=VectorStoreProvider.PINECONE, api_key="test", endpoint="test")
    adapter = VectorStoreAdapter(config)
    with pytest.raises(Exception):
        await adapter.initialize()

@pytest.mark.asyncio
async def test_unsupported_provider():
    """Tests that an unsupported provider raises a ValueError."""
    config = VectorStoreConfig(provider=VectorStoreProvider.MILVUS, endpoint="test")
    adapter = VectorStoreAdapter(config)
    with pytest.raises(ValueError):
        await adapter.initialize()

@pytest.mark.asyncio
async def test_upsert_and_search_failure(mocker):
    """Tests that upsert and search handle exceptions gracefully."""
    mock_pinecone = MagicMock()
    mocker.patch.dict(sys.modules, {"pinecone": mock_pinecone})

    config = VectorStoreConfig(provider=VectorStoreProvider.PINECONE, api_key="test", endpoint="test")
    adapter = VectorStoreAdapter(config)

    mock_index = MagicMock()
    mock_pinecone.Index.return_value = mock_index

    await adapter.initialize()

    mock_index.upsert.side_effect = Exception("test error")
    result = await adapter.upsert_embeddings([TEST_EMBEDDING], ["1"], [TEST_METADATA])
    assert not result

    mock_index.query.side_effect = Exception("test error")
    results = await adapter.search(TEST_EMBEDDING, top_k=1)
    assert results == []
