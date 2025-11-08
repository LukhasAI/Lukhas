import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.integration.nias_dream_bridge import NIASDreamBridge, get_nias_dream_bridge


@pytest.fixture
def bridge():
    # Reset singleton instance for each test
    from core.integration import nias_dream_bridge
    nias_dream_bridge._nias_dream_bridge_instance = None
    bridge_instance = get_nias_dream_bridge()
    # Ensure event mappings are set up for tests that bypass connect()
    bridge_instance.setup_event_mappings()
    return bridge_instance

@pytest.fixture
def mock_hubs(mocker):
    mock_nias_hub_module = MagicMock()
    mock_dream_hub_module = MagicMock()

    mock_nias_hub_module.get_nias_hub.return_value = AsyncMock()
    mock_dream_hub_module.get_dream_hub.return_value = AsyncMock()

    mocker.patch.dict(sys.modules, {
        'core.modules.nias.nias_hub': mock_nias_hub_module,
        'orchestration.dream.dream_hub': mock_dream_hub_module,
    })
    return mock_nias_hub_module, mock_dream_hub_module

@pytest.mark.asyncio
async def test_connect_successful(bridge, mock_hubs):
    mock_nias_hub_module, mock_dream_hub_module = mock_hubs

    result = await bridge.connect()

    assert result is True
    assert bridge.is_connected is True
    assert bridge.nias_hub is not None
    assert bridge.dream_hub is not None
    mock_nias_hub_module.get_nias_hub.assert_called_once()
    mock_dream_hub_module.get_dream_hub.assert_called_once()

@pytest.mark.asyncio
async def test_connect_failure(bridge, mocker):
    mock_nias_hub_module = MagicMock()
    mock_nias_hub_module.get_nias_hub.side_effect = Exception("NIAS Hub Error")

    mocker.patch.dict(sys.modules, {
        'core.modules.nias.nias_hub': mock_nias_hub_module,
        'orchestration.dream.dream_hub': MagicMock(),
    })

    result = await bridge.connect()

    assert result is False
    assert bridge.is_connected is False

@pytest.mark.asyncio
async def test_nias_to_dream_forwarding(bridge):
    bridge.is_connected = True
    bridge.dream_hub = AsyncMock()
    bridge.dream_hub.process_event.return_value = {"status": "processed"}

    event_type = "message_deferred"
    data = {"test": "data"}

    result = await bridge.nias_to_dream(event_type, data)

    mapped_event = bridge.event_mappings.get(event_type)
    bridge.dream_hub.process_event.assert_awaited_once()

    # Check that the data was transformed
    call_args = bridge.dream_hub.process_event.call_args
    assert call_args[0][0] == mapped_event
    assert call_args[0][1]['source_system'] == 'nias'
    assert call_args[0][1]['data'] == data

    assert result == {"status": "processed"}

@pytest.mark.asyncio
async def test_dream_to_nias_forwarding(bridge):
    bridge.is_connected = True
    bridge.nias_hub = AsyncMock()
    bridge.nias_hub.process_event.return_value = {"status": "processed_by_nias"}

    event_type = "dream_completion"
    data = {"dream_data": "value"}

    result = await bridge.dream_to_nias(event_type, data)

    mapped_event = bridge.event_mappings.get(event_type)
    bridge.nias_hub.process_event.assert_awaited_once()

    call_args = bridge.nias_hub.process_event.call_args
    assert call_args[0][0] == mapped_event
    assert call_args[0][1]['source_system'] == 'dream'
    assert call_args[0][1]['data'] == data

    assert result == {"status": "processed_by_nias"}

@pytest.mark.asyncio
async def test_handle_message_deferral(bridge):
    bridge.nias_to_dream = AsyncMock(return_value={"status": "deferred"})
    message_data = {
        "content": "test message",
        "user_context": {"user": "test"},
        "reason": "testing deferral",
        "priority": "high"
    }

    result = await bridge.handle_message_deferral(message_data)

    bridge.nias_to_dream.assert_awaited_once()
    call_args = bridge.nias_to_dream.call_args
    assert call_args[0][0] == "message_deferred"
    assert call_args[0][1]['message_content'] == "test message"

    assert result == {"status": "deferred"}

@pytest.mark.asyncio
async def test_handle_dream_completion(bridge):
    bridge.dream_to_nias = AsyncMock(return_value={"status": "completed"})
    dream_result = {
        "dream_id": "1234",
        "result": "dream result",
        "insights": ["insight1"]
    }

    result = await bridge.handle_dream_completion(dream_result)

    bridge.dream_to_nias.assert_awaited_once()
    call_args = bridge.dream_to_nias.call_args
    assert call_args[0][0] == "dream_completion"
    assert call_args[0][1]['processed_content'] == "dream result"

    assert result == {"status": "completed"}

@pytest.mark.asyncio
async def test_sync_symbolic_data_success(bridge):
    bridge.is_connected = True
    mock_symbolic_matcher = MagicMock()
    mock_symbolic_matcher.get_current_symbols.return_value = ["symbol1", "symbol2"]

    bridge.nias_hub = MagicMock()
    bridge.nias_hub.get_service.return_value = mock_symbolic_matcher
    bridge.nias_to_dream = AsyncMock()

    result = await bridge.sync_symbolic_data()

    assert result is True
    bridge.nias_hub.get_service.assert_called_once_with("symbolic_matcher")
    mock_symbolic_matcher.get_current_symbols.assert_called_once()
    bridge.nias_to_dream.assert_awaited_once_with("symbolic_match", {"symbols": ["symbol1", "symbol2"]})

@pytest.mark.asyncio
async def test_sync_symbolic_data_failure(bridge):
    bridge.is_connected = True
    bridge.nias_hub = MagicMock()
    bridge.nias_hub.get_service.side_effect = Exception("Sync Error")

    result = await bridge.sync_symbolic_data()

    assert result is False

@pytest.mark.asyncio
async def test_health_check(bridge):
    bridge.is_connected = True
    bridge.nias_hub = object()
    bridge.dream_hub = object()

    health = await bridge.health_check()

    assert health["bridge_status"] == "healthy"
    assert health["nias_hub_available"] is True
    assert health["dream_hub_available"] is True
    assert "timestamp" in health
