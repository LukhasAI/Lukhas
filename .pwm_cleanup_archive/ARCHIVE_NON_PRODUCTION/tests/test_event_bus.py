import asyncio
import unittest

from orchestration.symbolic_kernel_bus import get_global_event_bus


class TestEventBus(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.bus = EventBus()
        self.loop.run_until_complete(self.bus.start())

    def tearDown(self):
        self.loop.run_until_complete(self.bus.stop())
        self.loop.close()

    def test_publish_subscribe(self):
        async def _test():
            received_events = []

            async def handler(event):
                received_events.append(event)

            self.bus.subscribe("test_event", handler)
            await self.bus.publish("test_event", {"data": "test"})
            await asyncio.sleep(0.01)  # Give the worker time to process the event

            self.assertEqual(len(received_events), 1)
            self.assertEqual(received_events[0].event_type, "test_event")
            self.assertEqual(received_events[0].payload["data"], "test")

        self.loop.run_until_complete(_test())

    def test_unsubscribe(self):
        async def _test():
            received_events = []

            async def handler(event):
                received_events.append(event)

            self.bus.subscribe("test_event", handler)
            self.bus.unsubscribe("test_event", handler)
            await self.bus.publish("test_event", {"data": "test"})
            await asyncio.sleep(0.01)

            self.assertEqual(len(received_events), 0)

        self.loop.run_until_complete(_test())

    def test_multiple_subscribers(self):
        async def _test():
            received_events_1 = []
            received_events_2 = []

            async def handler_1(event):
                received_events_1.append(event)

            async def handler_2(event):
                received_events_2.append(event)

            self.bus.subscribe("test_event", handler_1)
            self.bus.subscribe("test_event", handler_2)
            await self.bus.publish("test_event", {"data": "test"})
            await asyncio.sleep(0.01)

            self.assertEqual(len(received_events_1), 1)
            self.assertEqual(len(received_events_2), 1)

        self.loop.run_until_complete(_test())

    def test_get_global_event_bus(self):
        async def _test():
            bus1 = await get_global_event_bus()
            bus2 = await get_global_event_bus()
            self.assertIs(bus1, bus2)
            await bus1.stop()
            from core import event_bus

            event_bus._global_event_bus = None

        self.loop.run_until_complete(_test())


if __name__ == "__main__":
    unittest.main()
