import pytest
import sys
from unittest.mock import AsyncMock, patch, MagicMock, ANY

# Mock the hub modules before they are imported by the bridge
mock_consciousness_hub_module = MagicMock()
mock_qi_hub_module = MagicMock()
sys.modules['consciousness.reflection.consciousness_hub'] = mock_consciousness_hub_module
sys.modules['qi.qi_hub'] = mock_qi_hub_module

from labs.core.bridges.consciousness_qi_bridge import ConsciousnessQIBridge, get_consciousness_quantum_bridge

@pytest.fixture
def bridge():
    """Fixture to create a new bridge instance for each test."""
    # Reset the singleton for each test
    from labs.core.bridges import consciousness_qi_bridge
    consciousness_qi_bridge._consciousness_quantum_bridge_instance = None
    # Reset mocks for each test run
    mock_consciousness_hub_module.reset_mock()
    mock_qi_hub_module.reset_mock()
    b = get_consciousness_quantum_bridge()
    # Ensure event mappings are set for tests that don't call connect()
    b.setup_event_mappings()
    return b

@pytest.mark.asyncio
class TestConsciousnessQIBridge:
    async def test_connect_success(self, bridge):
        mock_consciousness_hub_module.get_consciousness_hub.return_value = AsyncMock()
        mock_qi_hub_module.get_quantum_hub.return_value = AsyncMock()

        result = await bridge.connect()

        assert result is True
        assert bridge.is_connected is True
        mock_consciousness_hub_module.get_consciousness_hub.assert_called_once()
        mock_qi_hub_module.get_quantum_hub.assert_called_once()
        assert bridge.consciousness_hub is not None
        assert bridge.qi_hub is not None

    async def test_connect_failure(self, bridge):
        mock_consciousness_hub_module.get_consciousness_hub.side_effect = Exception("Test Error")
        result = await bridge.connect()
        assert result is False
        assert bridge.is_connected is False

    async def test_consciousness_to_quantum_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.qi_hub = AsyncMock()
        bridge.qi_hub.process_event.return_value = {"status": "processed"}

        event_type = "consciousness_state_change"
        data = {"state": "aware"}

        result = await bridge.consciousness_to_quantum(event_type, data)

        bridge.qi_hub.process_event.assert_awaited_once_with("qi_state_sync", ANY)
        assert result == {"status": "processed"}

    async def test_qi_to_consciousness_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.consciousness_hub = AsyncMock()
        bridge.consciousness_hub.process_event.return_value = {"status": "processed"}

        event_type = "qi_state_change"
        data = {"state": "superposition"}

        result = await bridge.qi_to_consciousness(event_type, data)

        bridge.consciousness_hub.process_event.assert_awaited_once_with("consciousness_sync_request", ANY)
        assert result == {"status": "processed"}

    async def test_health_check(self, bridge):
        bridge.is_connected = True
        bridge.consciousness_hub = AsyncMock()
        bridge.qi_hub = AsyncMock()
        health = await bridge.health_check()
        assert health["bridge_status"] == "healthy"
        assert health["consciousness_hub_available"] is True
        assert health["qi_hub_available"] is True

    def test_singleton(self):
        from labs.core.bridges import consciousness_qi_bridge
        consciousness_qi_bridge._consciousness_quantum_bridge_instance = None
        instance1 = get_consciousness_quantum_bridge()
        instance2 = get_consciousness_quantum_bridge()
        assert instance1 is instance2

    async def test_sync_quantum_consciousness_states_success(self, bridge):
        bridge.is_connected = True
        bridge.consciousness_hub = AsyncMock()
        bridge.qi_hub = AsyncMock()
        bridge.consciousness_hub.get_service.return_value.get_current_state.return_value = {"state": "conscious"}
        bridge.qi_hub.get_service.return_value.get_current_state.return_value = {"state": "quantum"}

        result = await bridge.sync_quantum_consciousness_states()

        assert result is True
        bridge.consciousness_hub.get_service.assert_called_with("qi_consciousness_hub")
        bridge.qi_hub.get_service.assert_called_with("qi_processor")


    async def test_sync_quantum_consciousness_states_fail_on_exception(self, bridge):
        bridge.is_connected = True
        with patch.object(bridge, 'get_consciousness_state', side_effect=Exception("State Error")):
            result = await bridge.sync_quantum_consciousness_states()
            assert result is False

    async def test_handle_quantum_superposition(self, bridge):
        bridge.is_connected = True
        bridge.consciousness_hub = AsyncMock()
        bridge.consciousness_hub.process_event.return_value = {"status": "processed"}
        superposition_data = {"states": ["a", "b"], "coherence": 0.9}

        result = await bridge.handle_quantum_superposition(superposition_data)

        assert result == {"status": "processed"}
        bridge.consciousness_hub.process_event.assert_awaited_once()

    async def test_handle_consciousness_decision(self, bridge):
        bridge.is_connected = True
        bridge.qi_hub = AsyncMock()
        bridge.qi_hub.process_event.return_value = {"status": "processed"}
        decision_data = {"decision": "collapse", "confidence": 0.9}

        result = await bridge.handle_consciousness_decision(decision_data)

        assert result == {"status": "processed"}
        bridge.qi_hub.process_event.assert_awaited_once()
