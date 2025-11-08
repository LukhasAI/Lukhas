import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

# --- Fixtures ---

@pytest.fixture
def mock_env_loader():
    """Mocks the env_loader.get_api_key function."""
    with patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key') as mock_get_key:
        mock_get_key.return_value = "sk-ant-test-key-1234567890"
        yield mock_get_key

@pytest.fixture
def mock_anthropic_client():
    """Mocks the anthropic.AsyncAnthropic client."""
    with patch('anthropic.AsyncAnthropic') as mock_async_anthropic:
        mock_client_instance = MagicMock()
        mock_client_instance.messages.create = AsyncMock()
        mock_async_anthropic.return_value = mock_client_instance
        yield mock_client_instance

@pytest.fixture
def mock_normalize_output():
    """Mocks the branding.terminology.normalize_output function."""
    with patch('bridge.llm_wrappers.anthropic_wrapper.normalize_output') as mock_normalize:
        # Passthrough implementation for testing
        mock_normalize.side_effect = lambda x: x
        yield mock_normalize

# --- __init__ Tests ---

def test_init_success_with_api_key(mock_env_loader, mock_anthropic_client, capsys):
    """Tests successful initialization with a valid API key."""
    wrapper = AnthropicWrapper()
    assert wrapper.is_available()
    assert wrapper.api_key == "sk-ant-test-key-1234567890"
    mock_env_loader.assert_called_once_with("anthropic")

    captured = capsys.readouterr()
    assert "✅ Anthropic initialized with key: sk-ant-test-key-1234" in captured.out

def test_init_no_api_key(mock_env_loader):
    """Tests initialization when no API key is found."""
    mock_env_loader.return_value = None
    wrapper = AnthropicWrapper()
    assert not wrapper.is_available()
    assert wrapper.api_key is None

def test_init_import_error(mock_env_loader, capsys):
    """Tests initialization when the anthropic package is not installed."""
    with patch.dict('sys.modules', {'anthropic': None}):
        wrapper = AnthropicWrapper()
        assert not wrapper.is_available()
        captured = capsys.readouterr()
        assert "Anthropic package not installed." in captured.out

# --- generate_response Tests ---

@pytest.mark.asyncio
async def test_generate_response_success(mock_env_loader, mock_anthropic_client, mock_normalize_output):
    """Tests a successful response from the Anthropic API."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test response")]
    mock_anthropic_client.messages.create.return_value = mock_response

    wrapper = AnthropicWrapper()
    text, model = await wrapper.generate_response("Test prompt", model="claude-3-opus-20240229")

    assert text == "Test response"
    assert model == "claude-3-opus-20240229"
    mock_anthropic_client.messages.create.assert_awaited_once()
    mock_normalize_output.assert_called_once_with("Test response")

@pytest.mark.asyncio
@pytest.mark.parametrize("error, error_message", [
    (Exception("API connection failed"), "API connection failed"),
    (ImportError("anthropic"), "anthropic"), # Simulating a delayed import error
])
async def test_generate_response_api_error(mock_env_loader, mock_anthropic_client, mock_normalize_output, error, error_message):
    """Tests handling of a generic API error."""
    mock_anthropic_client.messages.create.side_effect = error

    wrapper = AnthropicWrapper()
    text, model = await wrapper.generate_response("Test prompt")

    assert f"Anthropic API Error: {error_message}" in text
    assert model == "claude-3-sonnet-20240229"
    mock_normalize_output.assert_called_once()

@pytest.mark.asyncio
async def test_generate_response_not_initialized(mock_env_loader, mock_normalize_output):
    """Tests response when the client is not initialized."""
    mock_env_loader.return_value = None
    wrapper = AnthropicWrapper()
    text, model = await wrapper.generate_response("Test prompt")

    expected_msg = "Anthropic client not initialized. Please check API key and installation."
    assert text == expected_msg
    assert model == "claude-3-sonnet-20240229"
    mock_normalize_output.assert_called_once_with(expected_msg)

@pytest.mark.asyncio
async def test_generate_response_empty_content(mock_env_loader, mock_anthropic_client, mock_normalize_output):
    """Tests handling of a response with no content."""
    mock_response = MagicMock()
    mock_response.content = []
    mock_anthropic_client.messages.create.return_value = mock_response

    wrapper = AnthropicWrapper()
    text, model = await wrapper.generate_response("Test prompt")

    assert text == ""
    assert model == "claude-3-sonnet-20240229"

@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", [
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
])
async def test_generate_response_with_different_models(mock_env_loader, mock_anthropic_client, model_name):
    """Tests that different models can be specified."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Model test")]
    mock_anthropic_client.messages.create.return_value = mock_response

    wrapper = AnthropicWrapper()
    _, model = await wrapper.generate_response("Test prompt", model=model_name)

    assert model == model_name

    expected_guidance = (
        "When describing methods, prefer 'quantum-inspired' and 'bio-inspired'. "
        "Refer to the project as 'Lukhas AI'."
    )

    mock_anthropic_client.messages.create.assert_awaited_once_with(
        model=model_name,
        max_tokens=2000,
        system=expected_guidance,
        messages=[{"role": "user", "content": "Test prompt"}]
    )

@pytest.mark.asyncio
async def test_generate_response_kwargs_passthrough(mock_env_loader, mock_anthropic_client):
    """Tests that kwargs are passed through to the anthropic client."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="")]
    mock_anthropic_client.messages.create.return_value = mock_response

    wrapper = AnthropicWrapper()
    await wrapper.generate_response("Test prompt", max_tokens=123)

    mock_anthropic_client.messages.create.assert_awaited_once()
    call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
    assert call_kwargs['max_tokens'] == 123

# --- is_available Tests ---

def test_is_available_true(mock_env_loader, mock_anthropic_client):
    """Tests that is_available returns True when the client is initialized."""
    wrapper = AnthropicWrapper()
    assert wrapper.is_available() is True

def test_is_available_false_no_key(mock_env_loader):
    """Tests that is_available returns False when there is no API key."""
    mock_env_loader.return_value = None
    wrapper = AnthropicWrapper()
    assert wrapper.is_available() is False

def test_is_available_false_import_error(mock_env_loader):
    """Tests that is_available returns False when the anthropic package is not installed."""
    with patch.dict('sys.modules', {'anthropic': None}):
        wrapper = AnthropicWrapper()
        assert wrapper.is_available() is False
