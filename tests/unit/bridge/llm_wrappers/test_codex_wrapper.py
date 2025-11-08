
import asyncio
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses
from pydantic import ValidationError

# Now we can import the module under test
from bridge.llm_wrappers.codex_wrapper import (
    CodexClient,
    CodexConfig,
    CodexResponse,
)


@pytest.fixture
def mock_aioresponse():
    """Fixture for mocking aiohttp requests."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture to clear OpenAI environment variables for test isolation."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


# --- Initialization and Configuration Tests ---

def test_init_with_direct_api_key(mock_env):
    """Tests that the client is configured correctly with a direct API key."""
    client = CodexClient(api_key="direct-key")
    assert client.config.api_key == "direct-key"
    assert client.config.model == "gpt-4"  # Default value


def test_init_with_env_variable(monkeypatch, mock_env):
    """Tests that the client falls back to the environment variable."""
    # Explicitly disable keychain for this test to isolate env var logic
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', False)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    client = CodexClient()
    assert client.config.api_key == "env-key"


def test_init_with_keychain(monkeypatch, mock_env):
    """Tests that the client uses the keychain if available."""
    # Use monkeypatch to simulate keychain availability and mock its behavior
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', True)

    mock_keychain_manager = MagicMock()
    mock_keychain_manager.get_key.return_value = "keychain-key"
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KeychainManager', mock_keychain_manager)

    client = CodexClient()
    assert client.config.api_key == "keychain-key"
    mock_keychain_manager.get_key.assert_called_once_with("OPENAI_API_KEY", fallback_to_env=False)


def test_init_no_api_key_raises_error(monkeypatch, mock_env):
    """Tests that a ValueError is raised if no API key can be found."""
    # Ensure keychain is not available for this test
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', False)
    with pytest.raises(ValueError, match="OpenAI API key required"):
        CodexClient()


def test_api_key_precedence(monkeypatch, mock_env):
    """Tests the correct precedence for API key resolution: direct > keychain > env."""
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")

    # Mock keychain to be available and return a key
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', True)
    mock_keychain_manager = MagicMock()
    mock_keychain_manager.get_key.return_value = "keychain-key"
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KeychainManager', mock_keychain_manager)

    # 1. Direct key should be used
    client = CodexClient(api_key="direct-key")
    assert client.config.api_key == "direct-key"
    mock_keychain_manager.get_key.assert_not_called()

    # 2. Keychain key should be used when no direct key is provided
    client = CodexClient()
    assert client.config.api_key == "keychain-key"
    mock_keychain_manager.get_key.assert_called_once()

    # 3. Env var should be used if keychain is unavailable
    mock_keychain_manager.get_key.reset_mock()
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', False)
    client = CodexClient()
    assert client.config.api_key == "env-key"
    mock_keychain_manager.get_key.assert_not_called()


def test_init_with_custom_config():
    """Tests that the client can be initialized with a custom CodexConfig object."""
    config = CodexConfig(
        api_key="custom-key",
        model="gpt-3.5-turbo",
        timeout=120,
        max_retries=5,
        temperature=0.8,
        max_tokens=1024
    )
    client = CodexClient(config=config)
    assert client.config == config


def test_codex_config_model():
    """Tests the Pydantic model for configuration."""
    config = CodexConfig(api_key="test-key")
    assert config.model == "gpt-4"
    assert config.timeout == 300

    with pytest.raises(ValidationError):
        CodexConfig()  # api_key is required


def test_codex_response_model():
    """Tests the Pydantic model for responses."""
    response = CodexResponse(
        content="Hello",
        model="gpt-4",
        tokens_used=10,
        finish_reason="stop"
    )
    assert response.content == "Hello"
    # Test that created_at is set by default
    assert isinstance(response.created_at, datetime)

    with pytest.raises(ValidationError):
        CodexResponse(model="gpt-4", tokens_used=10, finish_reason="stop") # content is required


# --- Async Context Manager Tests ---

@pytest.mark.asyncio
@patch('aiohttp.ClientSession')
async def test_async_context_manager_lifecycle(MockClientSession):
    """Tests that the aiohttp session is created and closed correctly."""
    client = CodexClient(api_key="test-key")
    assert client._session is None

    # Mock the session object and its close method
    mock_session_instance = AsyncMock()
    MockClientSession.return_value = mock_session_instance

    async with client as a_client:
        assert a_client is client
        assert client._session is mock_session_instance
        # Check that session was created with correct headers and timeout
        MockClientSession.assert_called_once()
        call_kwargs = MockClientSession.call_args.kwargs
        assert call_kwargs['headers']['Authorization'] == 'Bearer test-key'
        assert isinstance(call_kwargs['timeout'], aiohttp.ClientTimeout)
        assert call_kwargs['timeout'].total == 300

    # Session should be closed upon exit
    mock_session_instance.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_client_used_outside_context_raises_error():
    """Tests that a RuntimeError is raised if the client is used without the context manager."""
    client = CodexClient(api_key="test-key")
    with pytest.raises(RuntimeError, match="CodexClient not initialized"):
        await client._make_request(prompt="test")


# --- Request Logic and Error Handling Tests ---

@pytest.fixture
def mock_success_response():
    """Returns a standard successful API response payload."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4-test",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "This is a test."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
    }


@pytest.mark.asyncio
async def test_make_request_success(mock_aioresponse, mock_success_response):
    """Tests a single successful request to the API."""
    client = CodexClient(api_key="test-key")
    url = f"{client.config.base_url}/chat/completions"
    mock_aioresponse.post(url, payload=mock_success_response)

    async with client:
        response = await client._make_request(prompt="test prompt")

    assert isinstance(response, CodexResponse)
    assert response.content == "This is a test."
    assert response.model == "gpt-4-test"
    assert response.tokens_used == 21
    assert response.finish_reason == "stop"


@pytest.mark.asyncio
async def test_make_request_retries_on_server_error(mock_aioresponse, mock_success_response, monkeypatch):
    """Tests if the client retries on 500 errors and then succeeds."""
    # Patch asyncio.sleep to avoid waiting during tests
    monkeypatch.setattr(asyncio, 'sleep', AsyncMock())

    client = CodexClient(api_key="test-key", config=CodexConfig(api_key="test-key", max_retries=3))
    url = f"{client.config.base_url}/chat/completions"

    # Simulate two 500 errors, followed by a 200 OK
    mock_aioresponse.post(url, status=500, body="Server Error")
    mock_aioresponse.post(url, status=500, body="Server Error")
    mock_aioresponse.post(url, payload=mock_success_response)

    async with client:
        response = await client._make_request(prompt="test")

    assert response.content == "This is a test."
    assert asyncio.sleep.call_count == 2  # Should have slept twice before success


@pytest.mark.asyncio
async def test_make_request_fails_after_max_retries(mock_aioresponse, monkeypatch):
    """Tests that a RuntimeError is raised after exhausting all retries."""
    monkeypatch.setattr(asyncio, 'sleep', AsyncMock())

    client = CodexClient(api_key="test-key", config=CodexConfig(api_key="test-key", max_retries=3))
    url = f"{client.config.base_url}/chat/completions"
    mock_aioresponse.post(url, status=503, repeat=3)

    async with client:
        with pytest.raises(RuntimeError, match="Failed after 3 retries"):
            await client._make_request(prompt="test")

    assert asyncio.sleep.call_count == 2 # Sleeps after the 1st and 2nd failed attempts


@pytest.mark.asyncio
async def test_make_request_retries_on_timeout(mock_aioresponse, mock_success_response, monkeypatch):
    """Tests that the client retries on asyncio.TimeoutError."""
    monkeypatch.setattr(asyncio, 'sleep', AsyncMock())

    client = CodexClient(api_key="test-key", config=CodexConfig(api_key="test-key", max_retries=2))
    url = f"{client.config.base_url}/chat/completions"

    # Simulate one timeout, then a success
    mock_aioresponse.post(url, exception=asyncio.TimeoutError())
    mock_aioresponse.post(url, payload=mock_success_response)

    async with client:
        response = await client._make_request(prompt="test")

    assert response.content == "This is a test."
    assert asyncio.sleep.call_count == 1


@pytest.mark.asyncio
async def test_make_request_fails_on_non_retryable_error(mock_aioresponse):
    """Tests that a non-retryable error (e.g., 400) fails immediately."""
    client = CodexClient(api_key="test-key")
    url = f"{client.config.base_url}/chat/completions"
    mock_aioresponse.post(url, status=400, body="Bad Request")

    async with client:
        with pytest.raises(RuntimeError, match="OpenAI API request failed: 400 - Bad Request"):
            await client._make_request(prompt="test")


# --- Public Method Tests ---

@pytest.fixture
def mock_make_request(monkeypatch):
    """Mocks the internal _make_request method to inspect its inputs."""
    mock = AsyncMock(return_value=CodexResponse(
        content="mocked response",
        model="gpt-4-test",
        tokens_used=1,
        finish_reason="stop"
    ))
    monkeypatch.setattr(CodexClient, '_make_request', mock)
    return mock


@pytest.mark.asyncio
async def test_complete_method(mock_make_request):
    """Tests the complete() method's prompt construction."""
    client = CodexClient(api_key="test-key")
    await client.complete("create a function", temperature=0.9, max_tokens=500)

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert "Generate clean, efficient, well-documented code" in call_kwargs['system_prompt']
    assert call_kwargs['prompt'] == "create a function"
    assert call_kwargs['temperature'] == 0.9
    assert call_kwargs['max_tokens'] == 500


@pytest.mark.asyncio
async def test_fix_code_method(mock_make_request):
    """Tests the fix_code() method's prompt construction."""
    client = CodexClient(api_key="test-key")
    await client.fix_code(code="<code>", error="<error>", context="<context>")

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert "You are an expert debugger" in call_kwargs['system_prompt']
    assert "<code>" in call_kwargs['prompt']
    assert "<error>" in call_kwargs['prompt']
    assert "<context>" in call_kwargs['prompt']


@pytest.mark.asyncio
async def test_refactor_method(mock_make_request):
    """Tests the refactor() method's prompt construction."""
    client = CodexClient(api_key="test-key")
    await client.refactor(code="<code>", instructions="<instructions>")

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert "You are an expert at code refactoring" in call_kwargs['system_prompt']
    assert "<code>" in call_kwargs['prompt']
    assert "<instructions>" in call_kwargs['prompt']


@pytest.mark.asyncio
@pytest.mark.parametrize("detail_level, expected_text", [
    ("brief", "Provide a brief 1-2 sentence summary."),
    ("medium", "Explain the code's purpose, key logic, and important details."),
    ("detailed", "Provide a comprehensive explanation"),
    ("invalid", "Explain the code's purpose, key logic, and important details."), # a sane default
])
async def test_explain_method(mock_make_request, detail_level, expected_text):
    """Tests the explain() method's prompt construction with different detail levels."""
    client = CodexClient(api_key="test-key")
    await client.explain(code="<code>", detail_level=detail_level)

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert expected_text in call_kwargs['system_prompt']
    assert "<code>" in call_kwargs['prompt']


@pytest.mark.asyncio
@pytest.mark.parametrize("style", ["google", "numpy", "sphinx"])
async def test_document_method(mock_make_request, style):
    """Tests the document() method's prompt construction with different styles."""
    client = CodexClient(api_key="test-key")
    await client.document(code="<code>", style=style)

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert f"Add comprehensive docstrings in {style} style" in call_kwargs['system_prompt']
    assert "<code>" in call_kwargs['prompt']


# --- Coverage Tests ---


@pytest.mark.asyncio
async def test_fix_code_method_no_context(mock_make_request):
    """Tests the fix_code() method's prompt construction when context is None."""
    client = CodexClient(api_key="test-key")
    await client.fix_code(code="<code>", error="<error>", context=None)

    mock_make_request.assert_awaited_once()
    call_kwargs = mock_make_request.call_args.kwargs
    assert "You are an expert debugger" in call_kwargs['system_prompt']
    assert "<code>" in call_kwargs['prompt']
    assert "<error>" in call_kwargs['prompt']
    assert "Context:" not in call_kwargs['prompt']


def test_init_with_keychain_logs_debug_message(monkeypatch, mock_env, caplog):
    """Tests that a debug message is logged when using a key from the keychain."""
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', True)
    mock_keychain_manager = MagicMock()
    mock_keychain_manager.get_key.return_value = "keychain-key"
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KeychainManager', mock_keychain_manager)

    with caplog.at_level("DEBUG"):
        CodexClient()
    assert "Using OpenAI API key from macOS Keychain" in caplog.text


def test_init_with_env_variable_logs_debug_message(monkeypatch, mock_env, caplog):
    """Tests that a debug message is logged when using a key from the environment."""
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', False)
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    with caplog.at_level("DEBUG"):
        CodexClient()
    assert "Using OpenAI API key from environment variable" in caplog.text


def test_init_with_keychain_failing_gracefully(monkeypatch, mock_env, caplog):
    """Tests that the client gracefully handles a failing keychain and falls back to env vars."""
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KEYCHAIN_AVAILABLE', True)
    mock_keychain_manager = MagicMock()
    mock_keychain_manager.get_key.side_effect = Exception("Keychain exploded")
    monkeypatch.setattr('bridge.llm_wrappers.codex_wrapper.KeychainManager', mock_keychain_manager)

    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    with caplog.at_level("DEBUG"):
        client = CodexClient()
    assert client.config.api_key == "env-key"
    assert "Using OpenAI API key from environment variable" in caplog.text
