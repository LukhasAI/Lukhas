"""
Unit tests for OpenAIModulatedService and VectorStoreAdapter

TaskID: TODO-HIGH-BRIDGE-LLM-m7n8o9p0
"""
import sys
import types

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Provide a lightweight chromadb stub so tests do not require the real dependency.

from labs.bridge.llm_wrappers.openai_modulated_service import (
    OpenAIModulatedService,
    VectorStoreAdapter,
    VectorStoreConfig,
    VectorStoreProvider,
    EmbeddingRequest,
    VectorSearchRequest,
    CompletionRequest,
    ModelTier,
)

@pytest.fixture(autouse=True)
def stub_chromadb(monkeypatch):
    """Ensure chromadb imports succeed without the real package."""
    chromadb_module = types.ModuleType("chromadb")
    chromadb_module.Client = MagicMock(name="ChromadbClient")
    chromadb_module.PersistentClient = MagicMock(name="ChromadbPersistentClient")
    chromadb_module.EphemeralClient = MagicMock(name="ChromadbEphemeralClient")

    config_module = types.ModuleType("chromadb.config")

    class DummySettings:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    config_module.Settings = DummySettings

    monkeypatch.setitem(sys.modules, "chromadb", chromadb_module)
    monkeypatch.setitem(sys.modules, "chromadb.config", config_module)
    yield chromadb_module, config_module
    monkeypatch.delitem(sys.modules, "chromadb", raising=False)
    monkeypatch.delitem(sys.modules, "chromadb.config", raising=False)

@pytest.fixture
def vector_store_config():
    """Fixture for a ChromaDB VectorStoreConfig."""
    return VectorStoreConfig(
        provider=VectorStoreProvider.CHROMA,
        endpoint="http://localhost:8000",
        index_name="test-index",
    )

@pytest.fixture
def openai_modulated_service(vector_store_config):
    """Fixture for an OpenAIModulatedService instance."""
    # Patch the availability flag to bypass the real import check in the constructor.
    with patch('labs.bridge.llm_wrappers.openai_modulated_service.OPENAI_AVAILABLE', True):
        # Patch the OpenAI clients to avoid actual API calls.
        with patch('openai.AsyncOpenAI', new_callable=AsyncMock) as mock_async_openai, \
             patch('openai.OpenAI') as mock_openai:

            service = OpenAIModulatedService(
                api_key="test-key",
                vector_store_config=vector_store_config,
            )
            # Ensure the service uses the mocked clients
            service.async_client = mock_async_openai.return_value
            service.client = mock_openai.return_value
            return service

@pytest.mark.asyncio
async def test_vector_store_adapter_initialization(vector_store_config, stub_chromadb):
    """Test that the VectorStoreAdapter initializes correctly for ChromaDB."""
    adapter = VectorStoreAdapter(vector_store_config)
    # Patch the ChromaDB client to avoid a real connection.
    with patch('chromadb.Client') as mock_chroma_client:
        mock_collection = MagicMock()
        mock_chroma_client.return_value.get_or_create_collection.return_value = mock_collection

        await adapter.initialize()

        call_args = mock_chroma_client.call_args
        settings = call_args.args[0]
        assert settings.kwargs["chroma_server_host"] == "localhost"
        assert settings.kwargs["chroma_server_http_port"] == 8000

        mock_chroma_client.return_value.get_or_create_collection.assert_called_with(
            name="test-index",
            metadata={"hnsw:space": "cosine"}
        )
    assert adapter._initialized

@pytest.mark.asyncio
async def test_generate_embeddings(openai_modulated_service):
    """Test embedding generation."""
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_embedding_response.model = "text-embedding-3-small"
    # The usage object needs a 'model_dump' method
    mock_usage = MagicMock()
    mock_usage.model_dump.return_value = {"total_tokens": 10}
    mock_embedding_response.usage = mock_usage

    openai_modulated_service.async_client.embeddings.create.return_value = mock_embedding_response

    request = EmbeddingRequest(text="test query")
    result = await openai_modulated_service.generate_embeddings(request)

    assert result.embeddings == [[0.1, 0.2, 0.3]]
    assert result.model == "text-embedding-3-small"
    assert result.usage == {"total_tokens": 10}

@pytest.mark.asyncio
async def test_store_embeddings(openai_modulated_service):
    """Test storing embeddings."""
    # Mock the adapter's method directly
    openai_modulated_service.vector_store.upsert_embeddings = AsyncMock(return_value=True)

    result = await openai_modulated_service.store_embeddings(
        texts=["test text"],
        embeddings=[[0.1, 0.2, 0.3]],
    )

    assert result is True
    openai_modulated_service.vector_store.upsert_embeddings.assert_called_once()

@pytest.mark.asyncio
async def test_search_similar(openai_modulated_service):
    """Test semantic search."""
    # Mock embedding generation for the search query
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock(embedding=[0.4, 0.5, 0.6])]
    mock_embedding_response.model = "text-embedding-3-small"
    mock_usage = MagicMock()
    mock_usage.model_dump.return_value = {"total_tokens": 5}
    mock_embedding_response.usage = mock_usage
    openai_modulated_service.async_client.embeddings.create.return_value = mock_embedding_response

    # Mock vector store search result
    mock_search_result = [{"id": "1", "score": 0.9, "metadata": {"text": "similar text"}}]
    openai_modulated_service.vector_store.search = AsyncMock(return_value=mock_search_result)

    request = VectorSearchRequest(query="test query")
    result = await openai_modulated_service.search_similar(request)

    assert len(result.matches) == 1
    assert result.matches[0]["metadata"]["text"] == "similar text"
    openai_modulated_service.vector_store.search.assert_called_with(
        query_embedding=[0.4, 0.5, 0.6],
        top_k=10,
        filter_metadata=None,
        namespace=None,
    )

@pytest.mark.asyncio
async def test_chat_completion_with_memory(openai_modulated_service):
    """Test chat completion with context retrieval from vector store."""
    # Mock search result from search_similar
    mock_search_result = MagicMock()
    mock_search_result.matches = [{"id": "1", "score": 0.9, "metadata": {"text": "retrieved memory"}}]
    openai_modulated_service.search_similar = AsyncMock(return_value=mock_search_result)

    # Mock chat completion response
    mock_completion_response = MagicMock()
    mock_usage = MagicMock()
    mock_usage.total_tokens = 50
    mock_completion_response.usage = mock_usage
    openai_modulated_service.async_client.chat.completions.create.return_value = mock_completion_response

    request = CompletionRequest(
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        memory_context=["some context"] # This enables the memory retrieval logic
    )
    await openai_modulated_service.chat_completion(request)

    # Verify that the search was called
    openai_modulated_service.search_similar.assert_called_once()

    # Verify that the retrieved memory was added to the messages for the completion call
    openai_modulated_service.async_client.chat.completions.create.assert_called_once()
    call_args = openai_modulated_service.async_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    assert messages[0]['role'] == 'system'
    assert "retrieved memory" in messages[0]['content']
