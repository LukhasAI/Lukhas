import pytest
from unittest.mock import AsyncMock

from labs.core.bridges.core_consciousness_bridge import CoreConsciousnessBridge

@pytest.mark.asyncio
async def test_core_to_consciousness_missing_system():
    bridge = CoreConsciousnessBridge()
    result = await bridge.core_to_consciousness({})
    assert result == {"status": "missing_consciousness"}

@pytest.mark.asyncio
async def test_consciousness_to_core_missing_system():
    bridge = CoreConsciousnessBridge()
    result = await bridge.consciousness_to_core({})
    assert result == {"status": "missing_core"}

@pytest.mark.asyncio
async def test_core_to_consciousness_with_system():
    mock_consciousness_system = AsyncMock()
    mock_consciousness_system.process.return_value = {"status": "processed"}
    bridge = CoreConsciousnessBridge(consciousness_system=mock_consciousness_system)

    data = {"test": "data"}
    result = await bridge.core_to_consciousness(data)

    mock_consciousness_system.process.assert_awaited_once_with(data)
    assert result == {"status": "processed"}

@pytest.mark.asyncio
async def test_consciousness_to_core_with_system():
    mock_core_system = AsyncMock()
    mock_core_system.process.return_value = {"status": "processed"}
    bridge = CoreConsciousnessBridge(core_system=mock_core_system)

    data = {"test": "data"}
    result = await bridge.consciousness_to_core(data)

    mock_core_system.process.assert_awaited_once_with(data)
    assert result == {"status": "processed"}

@pytest.mark.skip(reason="sync_state is not implemented yet.")
@pytest.mark.asyncio
async def test_sync_state():
    bridge = CoreConsciousnessBridge()
    await bridge.sync_state()

@pytest.mark.skip(reason="handle_event is not implemented yet.")
@pytest.mark.asyncio
async def test_handle_event():
    bridge = CoreConsciousnessBridge()
    await bridge.handle_event({})
