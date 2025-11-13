import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY

from labs.core.bridges.core_safety_bridge import CoreSafetyBridge, get_core_safety_bridge

@pytest.fixture
def bridge():
    """Fixture to create a new bridge instance for each test."""
    from labs.core.bridges import core_safety_bridge
    core_safety_bridge._core_safety_bridge_instance = None
    b = get_core_safety_bridge()
    b.setup_event_mappings()
    return b

@pytest.mark.asyncio
class TestCoreSafetyBridge:
    async def test_connect_success(self, bridge):
        result = await bridge.connect()
        assert result is True
        assert bridge.is_connected is True

    async def test_core_to_safety_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.safety_hub = AsyncMock()
        bridge.safety_hub.process_event.return_value = {"status": "processed"}

        event_type = "core_state_change"
        data = {"state": "critical"}

        result = await bridge.core_to_safety(event_type, data)

        bridge.safety_hub.process_event.assert_awaited_once_with("safety_sync_request", ANY)
        assert result == {"status": "processed"}

    async def test_safety_to_core_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.core_hub = AsyncMock()
        bridge.core_hub.process_event.return_value = {"status": "processed"}

        event_type = "safety_state_change"
        data = {"state": "safe"}

        result = await bridge.safety_to_core(event_type, data)

        bridge.core_hub.process_event.assert_awaited_once_with("core_sync_request", ANY)
        assert result == {"status": "processed"}

    def test_compare_states_no_diff(self, bridge):
        state1 = {"identity": {"id": 1}, "consciousness": {"level": "aware"}, "guardian": {"mode": "on"}}
        state2 = state1.copy()
        diff = bridge.compare_states(state1, state2)
        assert len(diff) == 0

    def test_compare_states_with_diffs(self, bridge):
        state1 = {"identity": {"id": 1}, "consciousness": {"level": "aware"}, "guardian": {"mode": "on"}}
        state2 = {"identity": {"id": 2}, "consciousness": {"level": "dreaming"}, "guardian": {"mode": "off"}}
        diffs = bridge.compare_states(state1, state2)
        assert len(diffs) == 4
        assert any(d["component"] == "identity" for d in diffs)
        assert any(d["component"] == "consciousness" for d in diffs)
        assert any(d["component"] == "guardian" for d in diffs)
        assert any(d["component"] == "constellation_framework" for d in diffs)

    async def test_sync_state_with_diffs(self, bridge):
        bridge.is_connected = True
        bridge.resolve_differences = AsyncMock()
        state1 = {"identity": {"id": 1}}
        state2 = {"identity": {"id": 2}}

        with patch.object(bridge, 'get_core_state', return_value=state1), \
             patch.object(bridge, 'get_safety_state', return_value=state2):
            result = await bridge.sync_state()
            assert result is True
            bridge.resolve_differences.assert_awaited_once()

    async def test_sync_state_no_diffs(self, bridge):
        bridge.is_connected = True
        bridge.resolve_differences = AsyncMock()
        state = {"identity": {"id": 1}}

        with patch.object(bridge, 'get_core_state', return_value=state), \
             patch.object(bridge, 'get_safety_state', return_value=state):
            result = await bridge.sync_state()
            assert result is True
            bridge.resolve_differences.assert_not_awaited()

    def test_singleton(self):
        from labs.core.bridges import core_safety_bridge
        core_safety_bridge._core_safety_bridge_instance = None
        instance1 = get_core_safety_bridge()
        instance2 = get_core_safety_bridge()
        assert instance1 is instance2
