import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from openai import AuthenticationError

from lukhas.bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService

class TestOpenAIModulatedService:

    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    def test_initialization(self, MockUnifiedClient):
        """Test that the service initializes the client correctly."""
        service = OpenAIModulatedService(api_key="test_key")
        MockUnifiedClient.assert_called_with(
            api_key="test_key",
            default_model="gpt-4o-mini",
            max_retries=3,
            timeout=60.0,
        )
        assert service.client == MockUnifiedClient.return_value

    @pytest.mark.asyncio
    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    async def test_generate_success(self, MockUnifiedClient):
        """Test successful response generation."""
        mock_client_instance = MockUnifiedClient.return_value
        mock_client_instance.chat_completion = AsyncMock()

        mock_response = {
            "choices": [{"message": {"content": "Hello"}, "finish_reason": "stop"}],
            "usage": {"total_tokens": 10},
            "id": "req-123"
        }
        mock_client_instance.chat_completion.return_value = mock_response

        service = OpenAIModulatedService()
        result = await service.generate("Hi")

        assert result["content"] == "Hello"
        assert not result.get("error")
        assert result["usage"]["total_tokens"] == 10
        mock_client_instance.chat_completion.assert_called_once()

    @pytest.mark.asyncio
    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    async def test_generate_error(self, MockUnifiedClient):
        """Test error handling during generation."""
        mock_client_instance = MockUnifiedClient.return_value
        mock_client_instance.chat_completion = AsyncMock(side_effect=AuthenticationError("Invalid API key", response=MagicMock(), body=None))

        service = OpenAIModulatedService()
        result = await service.generate("Hi")

        assert result["error"]
        assert result["error_type"] == "AuthenticationError"
        assert "Invalid API key" in result["content"]
        assert service.get_metrics()["total_errors"] == 1

    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    def test_build_messages(self, MockUnifiedClient):
        """Test message building logic."""
        service = OpenAIModulatedService(api_key="dummy")
        prompt = "User prompt"
        context = {"system_prompt": "System message"}
        messages = service._build_messages(prompt, context)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "System message"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "User prompt"

    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    def test_normalize_response(self, MockUnifiedClient):
        """Test response normalization."""
        service = OpenAIModulatedService(api_key="dummy")
        api_response = {
            "choices": [{"message": {"content": "Normalized"}, "finish_reason": "stop"}],
            "model": "gpt-4",
            "usage": {"total_tokens": 20},
            "id": "req-456"
        }
        normalized = service._normalize_response(api_response)

        assert normalized["content"] == "Normalized"
        assert normalized["model"] == "gpt-4"

    @patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient')
    def test_health_check_healthy(self, MockUnifiedClient):
        """Test health check when service is healthy."""
        service = OpenAIModulatedService()
        health = service.health_check()
        assert health["status"] == "healthy"

    def test_initialization_import_error(self):
        """Test that initialization fails if UnifiedOpenAIClient is not found."""
        with patch('lukhas.bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient', None):
            with pytest.raises(ImportError):
                OpenAIModulatedService()
