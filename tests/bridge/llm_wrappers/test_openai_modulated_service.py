
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../lukhas_website/lukhas')))
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bridge.llm_wrappers.openai_modulated_service import (
    OpenAIModulatedService,  #, run_modulated_completion
)
from orchestration.signals.homeostasis import ModulationParams


@pytest.fixture
def mock_dependencies():
    """Mocks all external dependencies for the service."""
    with patch('bridge.llm_wrappers.openai_modulated_service.get_signal_bus', return_value=MagicMock()) as mock_bus, \
         patch('bridge.llm_wrappers.openai_modulated_service.HomeostasisController') as mock_homeo_class, \
         patch('bridge.llm_wrappers.openai_modulated_service.PromptModulator') as mock_modulator_class, \
         patch('bridge.llm_wrappers.openai_modulated_service.UnifiedOpenAIClient') as mock_client_class, \
         patch('bridge.llm_wrappers.openai_modulated_service.bridged_execute_tool', new_callable=AsyncMock) as mock_execute, \
         patch('bridge.llm_wrappers.openai_modulated_service.get_analytics') as mock_analytics_class, \
         patch('bridge.llm_wrappers.openai_modulated_service.get_metrics_collector') as mock_metrics_class, \
         patch('governance.guardian_sentinel.get_guardian_sentinel') as mock_guardian_class:

        mock_homeo = mock_homeo_class.return_value
        mock_modulator = mock_modulator_class.return_value
        mock_client = mock_client_class.return_value
        mock_analytics = mock_analytics_class.return_value
        mock_metrics = mock_metrics_class.return_value
        mock_guardian = mock_guardian_class.return_value

        mock_homeo.process_event = AsyncMock(return_value=ModulationParams())

        modulation_mock = MagicMock()
        modulation_mock.to_api_format.return_value = {
            'messages': [{'role': 'user', 'content': 'test prompt'}],
            'max_tokens': 100,
            'temperature': 0.7,
            'metadata': {}
        }
        modulation_mock.moderation_preset = "default"
        modulation_mock.style.value = "default"
        modulation_mock.api_params.to_dict.return_value = {}
        modulation_mock.metadata = {}
        mock_modulator.modulate.return_value = modulation_mock

        yield {
            "bus": mock_bus,
            "homeo": mock_homeo,
            "modulator": mock_modulator,
            "client": mock_client,
            "execute_tool": mock_execute,
            "analytics": mock_analytics,
            "metrics": mock_metrics,
            "guardian": mock_guardian
        }

@pytest.mark.asyncio
async def test_successful_response_generation(mock_dependencies):
    """Tests a successful response generation without streaming."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion = AsyncMock(return_value={
        'choices': [{'message': {'content': 'test response'}}]
    })

    result = await service.generate('test prompt')

    assert 'test response' in result['content']
    mock_dependencies['client'].chat_completion.assert_called_once()

@pytest.mark.asyncio
async def test_streaming_response_generation(mock_dependencies):
    """Tests a successful response generation with streaming."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    async def mock_stream():
        yield {'choices': [{'delta': {'content': 'test '}}]}
        yield {'choices': [{'delta': {'content': 'response'}}]}

    mock_dependencies['client'].chat_completion = AsyncMock(return_value=mock_stream())

    stream = await service.generate_stream('test prompt')

    result = ''
    async for chunk in stream:
        result += chunk

    assert 'test response' in result
    mock_dependencies['client'].chat_completion.assert_called_once()

# ... (keep other tests from the previous block) ...

@pytest.mark.asyncio
async def test_tool_execution_loop(mock_dependencies):
    """Tests the tool execution loop with a single tool call."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion.side_effect = [
        {
            'choices': [{'message': {'tool_calls': [{'id': '1', 'function': {'name': 'test_tool', 'arguments': '{}'}}]}}]
        },
        {
            'choices': [{'message': {'content': 'tool response'}}]
        }
    ]

    mock_dependencies['execute_tool'].return_value = 'tool result'

    params = ModulationParams(tool_allowlist=['test_tool'])
    result = await service.generate('test prompt with tool', params=params)

    assert 'tool response' in result['content']
    assert mock_dependencies['client'].chat_completion.call_count == 2
    mock_dependencies['execute_tool'].assert_called_once_with('test_tool', '{}')

@pytest.mark.asyncio
async def test_moderation_hooks(mock_dependencies):
    """Tests that moderation hooks are called."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion = AsyncMock(return_value={
        'choices': [{'message': {'content': 'test response'}}]
    })

    with patch.object(service, '_pre_moderation_check', wraps=service._pre_moderation_check) as pre_mock, \
         patch.object(service, '_post_moderation_check', wraps=service._post_moderation_check) as post_mock:

        mock_dependencies['guardian'].assess_threat.return_value = (True, "OK", {})

        await service.generate('test prompt')

        pre_mock.assert_called_once()
        post_mock.assert_called_once()

@pytest.mark.asyncio
async def test_context_retrieval(mock_dependencies):
    """Tests that context retrieval is called when enabled."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion = AsyncMock(return_value={
        'choices': [{'message': {'content': 'test response'}}]
    })

    params = ModulationParams(retrieval_k=3, tool_allowlist=['retrieval'])

    with patch.object(service, '_retrieve_context', new_callable=AsyncMock) as retrieval_mock:
        retrieval_mock.return_value = ['retrieved context']

        await service.generate('test prompt', params=params)

        retrieval_mock.assert_called_once()

@pytest.mark.asyncio
async def test_disallowed_tool_call(mock_dependencies):
    """Tests that a disallowed tool call is blocked."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion.side_effect = [
        {
            'choices': [{'message': {'tool_calls': [{'id': '1', 'function': {'name': 'disallowed_tool', 'arguments': '{}'}}]}}]
        },
        {
            'choices': [{'message': {'content': 'final response'}}]
        }
    ]

    params = ModulationParams(tool_allowlist=['allowed_tool'])
    result = await service.generate('prompt', params=params)

    assert result['content'] == 'final response'
    assert mock_dependencies['execute_tool'].call_count == 0
    # Check that a system message about the blocked tool was added
    last_call_messages = mock_dependencies['client'].chat_completion.call_args_list[1].kwargs['messages']
    assert any("Blocked tool 'disallowed_tool'" in msg['content'] for msg in last_call_messages if msg['role'] == 'system')


@pytest.mark.asyncio
async def test_tool_execution_error(mock_dependencies):
    """Tests handling of an error during tool execution."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion.side_effect = [
        {
            'choices': [{'message': {'tool_calls': [{'id': '1', 'function': {'name': 'error_tool', 'arguments': '{}'}}]}}]
        },
        {
            'choices': [{'message': {'content': 'final response'}}]
        }
    ]

    mock_dependencies['execute_tool'].side_effect = Exception("Tool failed")

    params = ModulationParams(tool_allowlist=['error_tool'])
    result = await service.generate('prompt', params=params)

    assert result['content'] == 'final response'
    last_call_messages = mock_dependencies['client'].chat_completion.call_args_list[1].kwargs['messages']
    assert any("Tool execution failed: Tool failed" in msg['content'] for msg in last_call_messages if msg['role'] == 'tool')


@pytest.mark.asyncio
async def test_max_tool_steps_reached(mock_dependencies):
    """Tests that the tool loop exits after MAX_STEPS."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    tool_call_response = {'choices': [{'message': {'tool_calls': [{'id': '1', 'function': {'name': 'test_tool', 'arguments': '{}'}}]}}]}
    # The loop should run MAX_STEPS (6) times and then stop.
    mock_dependencies['client'].chat_completion.side_effect = [tool_call_response] * 7

    params = ModulationParams(tool_allowlist=['test_tool'])
    # Expect the loop to break, so the result might be from the last tool call attempt
    await service.generate('prompt', params=params)

    assert mock_dependencies['client'].chat_completion.call_count == 6


@pytest.mark.asyncio
async def test_homeostasis_integration(mock_dependencies):
    """Tests that homeostasis is called when signals/params are not provided."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])
    mock_dependencies['client'].chat_completion = AsyncMock(return_value={'choices': [{'message': {'content': 'response'}}]})

    await service.generate('prompt')

    mock_dependencies['homeo'].process_event.assert_called_once()

@pytest.mark.asyncio
async def test_pre_moderation_block(mock_dependencies):
    """Tests that a pre-moderation block raises PermissionError."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['guardian'].assess_threat.return_value = (False, "Blocked", {})

    with pytest.raises(PermissionError, match="Pre-moderation blocked: Blocked"):
        await service.generate('violating prompt')

@pytest.mark.asyncio
async def test_post_moderation_block(mock_dependencies):
    """Tests that a post-moderation block raises PermissionError."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    mock_dependencies['client'].chat_completion = AsyncMock(return_value={'choices': [{'message': {'content': 'violating response'}}]})

    mock_dependencies['guardian'].assess_threat.side_effect = [
        (True, "OK", {}),
        (False, "Blocked", {})
    ]

    with pytest.raises(PermissionError, match="Post-moderation blocked: Blocked"):
        await service.generate('prompt')

@pytest.mark.asyncio
async def test_fallback_retrieval_on_import_error(mock_dependencies):
    """Tests fallback retrieval when vector store is unavailable."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])
    mock_dependencies['client'].chat_completion = AsyncMock(return_value={'choices': [{'message': {'content': 'response'}}]})

    params = ModulationParams(retrieval_k=3, tool_allowlist=['retrieval'])

    with patch('bridge.llm_wrappers.openai_modulated_service.get_vector_store', side_effect=ImportError):
        with patch.object(service, '_fallback_retrieval', new_callable=AsyncMock) as fallback_mock:
            fallback_mock.return_value = ['fallback context']
            await service.generate('prompt', params=params)
            fallback_mock.assert_called_once()

# @pytest.mark.xfail(reason="Circular dependency or other issue with run_modulated_completion import")
# @pytest.mark.asyncio
# async def test_run_modulated_completion_helper(mock_dependencies):
#     """Tests the run_modulated_completion helper function."""

#     # Mock the client for the helper
#     mock_client = MagicMock()
#     mock_client.chat.completions.create.return_value = MagicMock(
#         choices=[MagicMock(message=MagicMock(content="helper response"))]
#     )

#     # We patch the service inside the helper's scope
#     with patch('bridge.llm_wrappers.openai_modulated_service.OpenAIModulatedService') as mock_service_class:
#         mock_service_instance = mock_service_class.return_value
#         mock_service_instance.generate = AsyncMock(return_value={'content': 'helper response', 'raw': {}})

#         result = run_modulated_completion(mock_client, 'user message')

#         assert result.choices[0].message.content == 'helper response'
#         mock_service_instance.generate.assert_called_once()

@pytest.mark.asyncio
async def test_streaming_with_post_moderation_block(mock_dependencies):
    """Tests streaming where the final content gets blocked by post-moderation."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])

    async def mock_stream():
        yield {'choices': [{'delta': {'content': 'violating '}}]}
        yield {'choices': [{'delta': {'content': 'content'}}]}

    mock_dependencies['client'].chat_completion = AsyncMock(return_value=mock_stream())

    # Pre-moderation allows, post-moderation blocks
    mock_dependencies['guardian'].assess_threat.side_effect = [
        (True, "OK", {}), # pre-moderation
        (False, "Blocked", {}) # post-moderation
    ]

    stream_generator = await service.generate_stream('prompt')

    # Consume the stream
    async for _ in stream_generator:
        pass

    # Check if the moderation block was recorded
    assert service.metrics['moderation_blocks'] == 1

@pytest.mark.asyncio
async def test_no_tool_calls_in_response(mock_dependencies):
    """Test the case where no tool calls are present in the response."""
    service = OpenAIModulatedService(client=mock_dependencies['client'])
    mock_dependencies['client'].chat_completion = AsyncMock(return_value={
        'choices': [{'message': {'content': 'No tools needed'}}]
    })

    params = ModulationParams(tool_allowlist=['some_tool'])
    result = await service.generate('prompt', params=params)

    assert result['content'] == 'No tools needed'
    assert not result['tool_analytics']['tools_used']
    mock_dependencies['client'].chat_completion.assert_called_once()
    mock_dependencies['execute_tool'].assert_not_called()
