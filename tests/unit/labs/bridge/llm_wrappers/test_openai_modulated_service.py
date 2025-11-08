
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

from ._module_imports import load_openai_modulated_service

_REPO_ROOT = Path(__file__).resolve().parents[3]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

_openai_module = load_openai_modulated_service()
OpenAIModulatedService = _openai_module.OpenAIModulatedService
EmbeddingRequest = _openai_module.EmbeddingRequest
ModelTier = _openai_module.ModelTier
EmbeddingResult = _openai_module.EmbeddingResult
CompletionRequest = _openai_module.CompletionRequest
VectorSearchRequest = _openai_module.VectorSearchRequest
VectorStoreConfig = _openai_module.VectorStoreConfig
VectorStoreProvider = _openai_module.VectorStoreProvider

@pytest.fixture
def mock_openai_client(mocker):
    """Mocks the OpenAI and AsyncOpenAI clients."""
    mock_client = MagicMock()
    mock_async_client = MagicMock()
    mocker.patch(
        "labs.bridge.llm_wrappers.openai_modulated_service.OpenAI",
        return_value=mock_client,
    )
    mocker.patch(
        "labs.bridge.llm_wrappers.openai_modulated_service.AsyncOpenAI",
        return_value=mock_async_client,
    )
    return mock_client, mock_async_client


@pytest.fixture
def modulated_service(mock_openai_client):
    """Provides an instance of OpenAIModulatedService with mocked clients."""
    return OpenAIModulatedService(api_key="test_api_key")

@pytest.fixture
def modulated_service_with_vector_store(mock_openai_client, mocker):
    """Provides an instance of OpenAIModulatedService with a mocked VectorStoreAdapter."""
    vector_store_config = VectorStoreConfig(
        provider=VectorStoreProvider.FAISS, endpoint=""
    )
    service = OpenAIModulatedService(
        api_key="test_api_key", vector_store_config=vector_store_config
    )
    service.vector_store = AsyncMock()
    return service

@pytest.mark.asyncio
async def test_generate_embeddings_success(modulated_service, mock_openai_client):
    """Tests successful embedding generation."""
    _, mock_async_client = mock_openai_client
    request = EmbeddingRequest(
        text="test query", model=ModelTier.EMBEDDING_3_SMALL
    )

    # Mock the OpenAI API response
    mock_embedding_data = MagicMock()
    mock_embedding_data.embedding = [0.1, 0.2, 0.3]
    mock_response = MagicMock()
    mock_response.data = [mock_embedding_data]
    mock_response.model = "text-embedding-3-small"
    mock_response.usage.model_dump.return_value = {"total_tokens": 5}

    mock_async_client.embeddings.create = AsyncMock(return_value=mock_response)

    result = await modulated_service.generate_embeddings(request)

    assert isinstance(result, EmbeddingResult)
    assert result.embeddings == [[0.1, 0.2, 0.3]]
    assert result.model == "text-embedding-3-small"
    assert result.usage == {"total_tokens": 5}
    mock_async_client.embeddings.create.assert_called_once_with(
        model=ModelTier.EMBEDDING_3_SMALL.value, input=["test query"]
    )

@pytest.mark.asyncio
async def test_generate_embeddings_error(modulated_service, mock_openai_client):
    """Tests error handling for embedding generation."""
    _, mock_async_client = mock_openai_client
    request = EmbeddingRequest(text="test query")
    mock_async_client.embeddings.create.side_effect = Exception("API error")
    with pytest.raises(Exception, match="API error"):
        await modulated_service.generate_embeddings(request)

@pytest.mark.asyncio
async def test_chat_completion_non_streaming(modulated_service, mock_openai_client):
    """Tests a successful non-streaming chat completion."""
    _, mock_async_client = mock_openai_client
    request = CompletionRequest(
        messages=[{"role": "user", "content": "Hello"}],
        model=ModelTier.GPT35_TURBO,
    )

    mock_response = MagicMock()
    mock_response.usage.total_tokens = 10
    mock_async_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    result = await modulated_service.chat_completion(request)

    assert result is not None
    mock_async_client.chat.completions.create.assert_called_once_with(
        model=ModelTier.GPT35_TURBO.value,
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7,
        max_tokens=None,
        stream=False,
    )

@pytest.mark.asyncio
async def test_chat_completion_streaming(modulated_service, mock_openai_client):
    """Tests a successful streaming chat completion."""
    _, mock_async_client = mock_openai_client
    request = CompletionRequest(
        messages=[{"role": "user", "content": "Hello"}],
        model=ModelTier.GPT35_TURBO,
        stream=True,
    )

    mock_iterator = MagicMock()
    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_iterator)

    result = await modulated_service.chat_completion(request)

    assert result is mock_iterator
    mock_async_client.chat.completions.create.assert_called_once_with(
        model=ModelTier.GPT35_TURBO.value,
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7,
        max_tokens=None,
        stream=True,
    )

@pytest.mark.asyncio
async def test_chat_completion_error(modulated_service, mock_openai_client):
    """Tests error handling for chat completion."""
    _, mock_async_client = mock_openai_client
    request = CompletionRequest(messages=[{"role": "user", "content": "Hello"}])
    mock_async_client.chat.completions.create.side_effect = Exception("API error")
    with pytest.raises(Exception, match="API error"):
        await modulated_service.chat_completion(request)

@pytest.mark.asyncio
async def test_store_embeddings_no_vector_store(modulated_service):
    """Tests store_embeddings returns False when no vector store is configured."""
    result = await modulated_service.store_embeddings(
        texts=["test"], embeddings=[[0.1]]
    )
    assert not result

@pytest.mark.asyncio
async def test_search_similar_no_vector_store(modulated_service):
    """Tests search_similar returns empty result when no vector store is configured."""
    request = VectorSearchRequest(query="test")
    result = await modulated_service.search_similar(request)
    assert result.matches == []

@pytest.mark.asyncio
async def test_store_embeddings_with_vector_store(modulated_service_with_vector_store):
    """Tests that store_embeddings calls the vector store's upsert method."""
    service = modulated_service_with_vector_store
    await service.store_embeddings(
        texts=["test"], embeddings=[[0.1]], metadata=[{"key": "value"}]
    )
    service.vector_store.upsert_embeddings.assert_called_once()

@pytest.mark.asyncio
async def test_search_similar_with_vector_store(modulated_service_with_vector_store):
    """Tests that search_similar calls the vector store's search method."""
    service = modulated_service_with_vector_store

    mock_embedding_result = EmbeddingResult(
        embeddings=[[0.1, 0.2, 0.3]],
        model="text-embedding-3-small",
        usage={"total_tokens": 1},
    )
    service.generate_embeddings = AsyncMock(return_value=mock_embedding_result)

    request = VectorSearchRequest(query="test")
    await service.search_similar(request)
    service.vector_store.search.assert_called_once()

@pytest.mark.asyncio
async def test_chat_completion_with_memory_context(modulated_service_with_vector_store, mock_openai_client):
    """Tests that chat_completion with memory_context calls search_similar."""
    service = modulated_service_with_vector_store
    _, mock_async_client = mock_openai_client

    mock_search_result = MagicMock()
    mock_search_result.matches = [{"metadata": {"text": "some memory"}}]
    service.search_similar = AsyncMock(return_value=mock_search_result)

    mock_response = MagicMock()
    mock_response.usage.total_tokens = 10
    mock_async_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    request = CompletionRequest(
        messages=[{"role": "user", "content": "Hello"}],
        model=ModelTier.GPT35_TURBO,
        memory_context=["some context"],
    )

    await service.chat_completion(request)

    service.search_similar.assert_called_once()
    call_args = mock_async_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    assert messages[0]["role"] == "system"
    assert "some memory" in messages[0]["content"]

def test_check_rate_limit(modulated_service):
    """Tests that the rate limit check currently always passes."""
    assert modulated_service._check_rate_limit("test_id", "test_tier")
