import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Module under test
from lukhas.bridge.llm_wrappers import anthropic_wrapper

class TestAnthropicWrapper:

    @patch('candidate.bridge.llm_wrappers.anthropic_wrapper.AnthropicWrapper')
    def test_lazy_loading_success(self, MockCandidateWrapper):
        """Verify that the real wrapper is loaded and instantiated on first access."""
        # Arrange
        mock_instance = MockCandidateWrapper.return_value

        # Act
        # Re-import to ensure the lazy loading mechanism is triggered
        from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
        wrapper = AnthropicWrapper(api_key="test_key")

        # Assert
        MockCandidateWrapper.assert_called_once_with(api_key="test_key")
        assert wrapper is mock_instance

    @patch.dict('sys.modules', {'candidate.bridge.llm_wrappers.anthropic_wrapper': None})
    def test_lazy_loading_import_error_fallback(self):
        """Verify that a fallback is used if the candidate module is not found."""
        # Arrange
        # Force the lazy loader to run again by clearing its cache
        anthropic_wrapper._anthropic_wrapper_class = None

        # Act
        from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
        wrapper = AnthropicWrapper()

        # Assert
        assert "FallbackWrapper" in str(type(wrapper))
        assert not wrapper.is_available()

    @pytest.mark.asyncio
    @patch('lukhas.bridge.llm_wrappers.anthropic_wrapper._get_anthropic_wrapper_class')
    async def test_method_delegation(self, mock_get_class):
        """Verify that methods called on the facade are delegated to the real instance."""
        # Arrange
        MockCandidateWrapper = MagicMock()
        mock_instance = MockCandidateWrapper.return_value
        mock_instance.generate_response = AsyncMock(return_value=("response", "model"))
        mock_instance.is_available = MagicMock(return_value=True)
        mock_get_class.return_value = MockCandidateWrapper

        from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
        # Force re-evaluation of the lazy loader
        anthropic_wrapper._anthropic_wrapper_class = None
        wrapper = AnthropicWrapper() # This will now use the mock

        # Act
        response, model = await wrapper.generate_response("prompt", model='claude-3-sonnet-20240229')
        available = wrapper.is_available()

        # Assert
        mock_instance.generate_response.assert_called_once_with("prompt", model='claude-3-sonnet-20240229')
        mock_instance.is_available.assert_called_once()
        assert response == "response"
        assert model == "model"
        assert available is True

    def test_new_method_instantiates_correctly(self):
        """Test the __new__ method directly."""
        with patch('lukhas.bridge.llm_wrappers.anthropic_wrapper._get_anthropic_wrapper_class') as mock_get_class:
            MockActualClass = MagicMock()
            mock_get_class.return_value = MockActualClass

            from lukhas.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
            instance = AnthropicWrapper(foo="bar")

            mock_get_class.assert_called_once()
            MockActualClass.assert_called_once_with(foo="bar")
            assert instance == MockActualClass.return_value
