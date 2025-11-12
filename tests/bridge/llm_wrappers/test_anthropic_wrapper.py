
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
def test_anthropic_wrapper_initialization(mock_get_api_key, MockAsyncAnthropic):
    """Tests that the AnthropicWrapper initializes correctly when an API key is present."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value

    # Act
    wrapper = AnthropicWrapper()

    # Assert
    assert wrapper.is_available()
    mock_get_api_key.assert_called_once_with("anthropic")
    MockAsyncAnthropic.assert_called_once_with(api_key="test_api_key")

@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value=None)
def test_anthropic_wrapper_initialization_no_key(mock_get_api_key):
    """Tests that the AnthropicWrapper does not initialize a client when no API key is present."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Act
    wrapper = AnthropicWrapper()

    # Assert
    assert not wrapper.is_available()
    mock_get_api_key.assert_called_once_with("anthropic")

@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
async def test_generate_response_success(mock_get_api_key, MockAsyncAnthropic):
    """Tests a successful response generation."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello, Claude")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    wrapper = AnthropicWrapper()

    # Act
    response, model = await wrapper.generate_response("test prompt")

    # Assert
    assert response == "Hello, Claude"
    assert model == "claude-3-sonnet-20240229"
    mock_client.messages.create.assert_awaited_once()

@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
async def test_generate_response_api_error(mock_get_api_key, MockAsyncAnthropic):
    """Tests handling of an API error during response generation."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value
    mock_client.messages.create = AsyncMock(side_effect=Exception("API Failure"))

    wrapper = AnthropicWrapper()

    # Act
    response, model = await wrapper.generate_response("test prompt")

    # Assert
    assert "Anthropic API Error: API Failure" in response
    assert model == "claude-3-sonnet-20240229"

@pytest.mark.asyncio
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value=None)
async def test_generate_response_when_unavailable(mock_get_api_key):
    """Tests that generate_response returns a graceful message when the client is not available."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    wrapper = AnthropicWrapper()

    # Act
    response, model = await wrapper.generate_response("test prompt")

    # Assert
    assert "Anthropic client not initialized" in response

@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
async def test_generate_response_with_opus_model(mock_get_api_key, MockAsyncAnthropic):
    """Tests response generation with a different model."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello from Opus")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    wrapper = AnthropicWrapper()

    # Act
    response, model = await wrapper.generate_response("test prompt", model="claude-3-opus-20240229")

    # Assert
    assert response == "Hello from Opus"
    assert model == "claude-3-opus-20240229"

@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
async def test_generate_response_with_haiku_model(mock_get_api_key, MockAsyncAnthropic):
    """Tests response generation with a different model."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello from Haiku")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    wrapper = AnthropicWrapper()

    # Act
    response, model = await wrapper.generate_response("test prompt", model="claude-3-haiku-20240307")

    # Assert
    assert response == "Hello from Haiku"
    assert model == "claude-3-haiku-20240307"

@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
@patch('bridge.llm_wrappers.anthropic_wrapper.get_api_key', return_value="test_api_key")
async def test_generate_response_with_max_tokens(mock_get_api_key, MockAsyncAnthropic):
    """Tests response generation with max_tokens parameter."""
    from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
    # Arrange
    mock_client = MockAsyncAnthropic.return_value
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Limited response")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    wrapper = AnthropicWrapper()

    # Act
    await wrapper.generate_response("test prompt", max_tokens=10)

    # Assert
    mock_client.messages.create.assert_awaited_once_with(
        model="claude-3-sonnet-20240229",
        max_tokens=10,
        system= "When describing methods, prefer 'quantum-inspired' and 'bio-inspired'. Refer to the project as 'Lukhas AI'.",
        messages=[{'role': 'user', 'content': 'test prompt'}]
    )
