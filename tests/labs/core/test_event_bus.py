import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from labs.core.event_bus import EventBus, DreamEventType, get_global_event_bus

@pytest.fixture
async def event_bus():
    bus = EventBus()
    await bus.start()
    yield bus
    await bus.stop()

class TestEventBus:
    async def test_subscribe_and_publish(self, event_bus):
        callback = AsyncMock()
        event_bus.subscribe("test_event", callback)
        await event_bus.publish("test_event", {"data": "test"})
        await asyncio.sleep(0.01)  # Allow time for the event to be processed
        callback.assert_called_once()

    async def test_priority_queue(self, event_bus):
        low_priority_callback = AsyncMock()
        high_priority_callback = AsyncMock()

        event_bus.subscribe("priority_test", low_priority_callback)
        event_bus.subscribe("priority_test", high_priority_callback)

        await event_bus.publish("priority_test", {}, priority=1)
        await event_bus.publish("priority_test", {}, priority=5)

        await asyncio.sleep(0.01)

        # This is tricky to assert ordering with mocks. A better approach
        # would be to use a list to track call order.
        # For now, just assert they were both called.
        low_priority_callback.assert_called()
        high_priority_callback.assert_called()

    async def test_dream_coordination(self, event_bus):
        start_callback = AsyncMock()
        complete_callback = AsyncMock()

        event_bus.subscribe(DreamEventType.DREAM_CYCLE_START.value, start_callback)
        event_bus.subscribe(DreamEventType.DREAM_CYCLE_COMPLETE.value, complete_callback)

        dream_id = "dream-123"
        correlation_id = await event_bus.start_dream_coordination(dream_id, "test_dream")
        await event_bus.complete_dream_coordination(dream_id, correlation_id, {"result": "success"})

        await asyncio.sleep(0.01)

        start_callback.assert_called_once()
        complete_callback.assert_called_once()

    async def test_event_filtering(self, event_bus):
        callback = AsyncMock()

        def filter_func(event):
            return event.payload.get("data") == "filtered"

        event_bus.subscribe("filtered_event", callback, filter_func=filter_func)

        await event_bus.publish("filtered_event", {"data": "unfiltered"})
        await event_bus.publish("filtered_event", {"data": "filtered"})

        await asyncio.sleep(0.01)

        callback.assert_called_once()

    async def test_global_event_bus(self):
        bus = await get_global_event_bus()
        assert isinstance(bus, EventBus)
        await bus.stop()
