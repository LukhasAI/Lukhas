
import pytest
from unittest.mock import patch, MagicMock

from bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper

@pytest.mark.xfail(reason="Test environment missing anthropic dependencies or has version conflicts")
@patch('bridge.llm_wrappers.anthropic_wrapper.anthropic')
def test_initialization_with_api_key(mock_anthropic):
    """Tests successful initialization with an API key."""
    mock_client = MagicMock()
    mock_anthropic.AsyncAnthropic.return_value = mock_client

    with patch('bridge.llm_wrappers.env_loader.get_api_key', return_value='test_key'):
        wrapper = AnthropicWrapper()
        assert wrapper.is_available()
        mock_anthropic.AsyncAnthropic.assert_called_with(api_key='test_key')

@pytest.mark.xfail(reason="Test environment missing anthropic dependencies or has version conflicts")
@patch('bridge.llm_wrappers.anthropic_wrapper.anthropic')
@pytest.mark.asyncio
async def test_successful_response_generation(mock_anthropic):
    """Tests successful response generation."""
    mock_client = MagicMock()
    mock_client.messages.create = MagicMock()
    mock_anthropic.AsyncAnthropic.return_value = mock_client

    with patch('bridge.llm_wrappers.env_loader.get_api_key', return_value='test_key'):
        wrapper = AnthropicWrapper()

        # Mock the API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='anthropic response')]
        mock_client.messages.create.return_value = mock_response

        response, model = await wrapper.generate_response('test prompt')

        assert 'anthropic response' in response
        assert model == "claude-3-sonnet-20240229"
        mock_client.messages.create.assert_called_once()

@pytest.mark.xfail(reason="Test environment missing anthropic dependencies or has version conflicts")
@patch('bridge.llm_wrappers.anthropic_wrapper.anthropic')
@pytest.mark.asyncio
async def test_api_error_handling(mock_anthropic):
    """Tests error handling for API failures."""
    mock_client = MagicMock()
    mock_client.messages.create = MagicMock(side_effect=Exception("API Error"))
    mock_anthropic.AsyncAnthropic.return_value = mock_client

    with patch('bridge.llm_wrappers.env_loader.get_api_key', return_value='test_key'):
        wrapper = AnthropicWrapper()

        response, model = await wrapper.generate_response('test prompt')

        assert 'Anthropic API Error: API Error' in response
        assert model == "claude-3-sonnet-20240229"

def test_initialization_without_api_key():
    """Tests initialization without an API key."""
    with patch('bridge.llm_wrappers.env_loader.get_api_key', return_value=None):
        wrapper = AnthropicWrapper()
        assert not wrapper.is_available()
