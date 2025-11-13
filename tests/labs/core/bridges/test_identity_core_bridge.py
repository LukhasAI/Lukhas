import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY

from labs.core.bridges.identity_core_bridge import IdentityCoreBridge, get_identity_core_bridge

@pytest.fixture
def bridge():
    """Fixture to create a new bridge instance for each test."""
    from labs.core.bridges import identity_core_bridge
    identity_core_bridge._identity_core_bridge_instance = None
    b = get_identity_core_bridge()
    b.setup_event_mappings()
    return b

@pytest.mark.asyncio
class TestIdentityCoreBridge:
    async def test_connect_success(self, bridge):
        result = await bridge.connect()
        assert result is True
        assert bridge.is_connected is True

    async def test_connect_failure(self, bridge):
        with patch('labs.core.bridges.identity_core_bridge.IdentityCoreBridge.setup_event_mappings', side_effect=Exception("Setup failed")):
            result = await bridge.connect()
            assert result is False
            assert bridge.is_connected is False

    async def test_identity_to_core_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.core_hub = AsyncMock()
        bridge.core_hub.process_event.return_value = {"status": "processed"}

        event_type = "identity_state_change"
        data = {"state": "authenticated"}

        result = await bridge.identity_to_core(event_type, data)

        bridge.core_hub.process_event.assert_awaited_once_with("core_sync_request", ANY)
        assert result == {"status": "processed"}

    async def test_core_to_identity_forwarding(self, bridge):
        bridge.is_connected = True
        bridge.identity_hub = AsyncMock()
        bridge.identity_hub.process_event.return_value = {"status": "processed"}

        event_type = "core_state_change"
        data = {"state": "updated"}

        result = await bridge.core_to_identity(event_type, data)

        bridge.identity_hub.process_event.assert_awaited_once_with("identity_sync_request", ANY)
        assert result == {"status": "processed"}

    async def test_identity_to_core_no_hub(self, bridge):
        bridge.is_connected = True
        bridge.core_hub = None
        result = await bridge.identity_to_core("any_event", {})
        assert result == {"error": "core hub not available"}

    async def test_core_to_identity_no_hub(self, bridge):
        bridge.is_connected = True
        bridge.identity_hub = None
        result = await bridge.core_to_identity("any_event", {})
        assert result == {"error": "identity hub not available"}

    async def test_sync_state_not_connected(self, bridge):
        bridge.is_connected = False
        result = await bridge.sync_state()
        assert result is False

    async def test_sync_state_connected(self, bridge):
        bridge.is_connected = True
        with patch.object(bridge, 'get_identity_state', return_value={}) as mock_get_identity, \
             patch.object(bridge, 'get_core_state', return_value={}) as mock_get_core, \
             patch.object(bridge, 'resolve_differences', new_callable=AsyncMock) as mock_resolve:

            result = await bridge.sync_state()
            assert result is True
            mock_get_identity.assert_awaited_once()
            mock_get_core.assert_awaited_once()
            mock_resolve.assert_not_awaited()

    async def test_get_identity_state_with_hub(self, bridge):
        bridge.identity_hub = MagicMock()
        state = await bridge.get_identity_state()
        assert state == {"system": "identity", "state": "active"}

    async def test_get_core_state_with_hub(self, bridge):
        bridge.core_hub = MagicMock()
        state = await bridge.get_core_state()
        assert state == {"system": "core", "state": "active"}

    @pytest.mark.skip(reason="compare_states is not implemented yet.")
    def test_compare_states_placeholder(self, bridge):
        diffs = bridge.compare_states({}, {})
        assert diffs == []

    def test_singleton(self):
        from labs.core.bridges import identity_core_bridge
        identity_core_bridge._identity_core_bridge_instance = None
        instance1 = get_identity_core_bridge()
        instance2 = get_identity_core_bridge()
        assert instance1 is instance2
