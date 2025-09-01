# Tests for lukhas/bridge/llm_wrappers/unified_openai_client.py

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
import uuid
import os

from lukhas.bridge.llm_wrappers.unified_openai_client import (
    UnifiedOpenAIClient,
    ConversationMessage,
    ConversationState,
)


@pytest.fixture
def mock_openai_clients():
    with patch('lukhas.bridge.llm_wrappers.unified_openai_client.OpenAI') as mock_sync_client, \
         patch('lukhas.bridge.llm_wrappers.unified_openai_client.AsyncOpenAI') as mock_async_client:
        yield mock_sync_client, mock_async_client

@pytest.fixture
def client(mock_openai_clients):
    """Provides a UnifiedOpenAIClient instance with a mock API key."""
    return UnifiedOpenAIClient(api_key="test_api_key")


def test_client_initialization(client, mock_openai_clients):
    """Test that the client initializes correctly."""
    mock_sync_client, mock_async_client = mock_openai_clients
    assert client.api_key == "test_api_key"
    assert client.default_model == "gpt-4o-mini"
    mock_sync_client.assert_called_once_with(api_key="test_api_key", max_retries=3, timeout=60.0)
    mock_async_client.assert_called_once_with(api_key="test_api_key", max_retries=3, timeout=60.0)

def test_client_initialization_no_api_key():
    """Test that ValueError is raised if no API key is provided."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OpenAI API key must be provided"):
            UnifiedOpenAIClient()

def test_create_conversation(client):
    """Test creating a new conversation."""
    convo_id = client.create_conversation(system_prompt="You are a helpful assistant.")
    assert convo_id in client.conversations
    conversation_state = client.get_conversation(convo_id)
    assert isinstance(conversation_state, ConversationState)
    assert conversation_state.system_prompt == "You are a helpful assistant."

def test_get_conversation(client):
    """Test getting an existing conversation."""
    convo_id = client.create_conversation()
    retrieved_convo = client.get_conversation(convo_id)
    assert retrieved_convo is not None
    assert retrieved_convo.conversation_id == convo_id

def test_get_nonexistent_conversation(client):
    """Test getting a nonexistent conversation returns None."""
    assert client.get_conversation("nonexistent-id") is None

def test_clear_conversation(client):
    """Test clearing a conversation."""
    convo_id = client.create_conversation()
    assert convo_id in client.conversations
    result = client.clear_conversation(convo_id)
    assert result is True
    assert convo_id not in client.conversations

def test_clear_nonexistent_conversation(client):
    """Test clearing a nonexistent conversation."""
    result = client.clear_conversation("nonexistent-id")
    assert result is False

def test_add_message_to_conversation(client):
    """Test adding a message to a conversation."""
    convo_id = client.create_conversation()
    conversation = client.get_conversation(convo_id)
    message = conversation.add_message("user", "Hello, world!")
    assert len(conversation.messages) == 1
    assert message.role == "user"
    assert message.content == "Hello, world!"

def test_conversation_history_trimming(client):
    """Test that conversation history is trimmed correctly."""
    convo_id = client.create_conversation(max_history=2)
    conversation = client.get_conversation(convo_id)
    conversation.add_message("user", "message 1")
    conversation.add_message("assistant", "message 2")
    conversation.add_message("user", "message 3")
    assert len(conversation.messages) == 2
    assert conversation.messages[0].content == "message 2"
    assert conversation.messages[1].content == "message 3"

@pytest.mark.asyncio
async def test_chat_completion_string_message(client):
    """Test chat completion with a simple string message."""
    mock_response = MagicMock()
    mock_response.id = "chatcmpl-123"
    mock_response.object = "chat.completion"
    mock_response.created = 1677652288
    mock_response.model = "gpt-4o-mini"
    mock_choice = MagicMock()
    mock_choice.index = 0
    mock_choice.message.role = "assistant"
    mock_choice.message.content = "Hello there!"
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_response.usage = None
    client.async_client.chat.completions.create = AsyncMock(return_value=mock_response)

    response = await client.chat_completion("Hello")

    assert response["choices"][0]["message"]["content"] == "Hello there!"
    client.async_client.chat.completions.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_chat_completion_with_conversation(client):
    """Test chat completion within a conversation."""
    convo_id = client.create_conversation(system_prompt="You are a test assistant.")
    client.get_conversation(convo_id).add_message("user", "First message")

    mock_response = MagicMock()
    mock_response.id = "chatcmpl-123"
    mock_response.object = "chat.completion"
    mock_response.created = 1677652288
    mock_response.model = "gpt-4o-mini"
    mock_choice = MagicMock()
    mock_choice.index = 0
    mock_choice.message.role = "assistant"
    mock_choice.message.content = "This is a test response."
    mock_choice.finish_reason = "stop"
    mock_response.choices = [mock_choice]
    mock_response.usage = None
    client.async_client.chat.completions.create = AsyncMock(return_value=mock_response)

    await client.chat_completion("Second message", conversation_id=convo_id)

    conversation = client.get_conversation(convo_id)
    assert len(conversation.messages) == 3  # user, assistant, user
    assert conversation.messages[2].role == "assistant"
    assert conversation.messages[2].content == "This is a test response."

@pytest.mark.asyncio
async def test_chat_completion_streaming(client):
    """Test streaming chat completion."""
    async def mock_stream():
        for i in range(3):
            mock_chunk = MagicMock()
            mock_chunk.id = f"chatcmpl-123-{i}"
            mock_chunk.object = "chat.completion.chunk"
            mock_chunk.created = 1677652288
            mock_chunk.model = "gpt-4o-mini"
            mock_choice = MagicMock()
            mock_choice.index = 0
            mock_choice.delta.role = None
            mock_choice.delta.content = f"token {i} "
            mock_choice.finish_reason = None
            mock_chunk.choices = [mock_choice]
            yield mock_chunk

    client.async_client.chat.completions.create = AsyncMock(return_value=mock_stream())

    convo_id = client.create_conversation()
    response_iterator = await client.chat_completion("Stream test", conversation_id=convo_id, stream=True)

    full_response = ""
    async for chunk in response_iterator:
        full_response += chunk["choices"][0]["delta"]["content"]

    assert full_response == "token 0 token 1 token 2 "
    conversation = client.get_conversation(convo_id)
    assert conversation.messages[-1].content == "token 0 token 1 token 2 "

@pytest.mark.asyncio
async def test_embeddings(client):
    """Test the embeddings method."""
    mock_response = MagicMock()
    mock_response.object = "list"
    embedding_item = MagicMock()
    embedding_item.object = "embedding"
    embedding_item.index = 0
    embedding_item.embedding = [0.1, 0.2, 0.3]
    mock_response.data = [embedding_item]
    mock_response.model = "text-embedding-ada-002"
    mock_response.usage.prompt_tokens = 8
    mock_response.usage.total_tokens = 8
    client.async_client.embeddings.create = AsyncMock(return_value=mock_response)

    response = await client.embeddings("Test input")

    assert response["object"] == "list"
    assert len(response["data"]) == 1
    assert response["data"][0]["embedding"] == [0.1, 0.2, 0.3]
    client.async_client.embeddings.create.assert_awaited_once_with(
        model="text-embedding-ada-002",
        input="Test input"
    )
