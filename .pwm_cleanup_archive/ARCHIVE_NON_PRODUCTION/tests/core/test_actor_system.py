import asyncio
import unittest
from unittest.mock import MagicMock

from core.actor_system import (
    Actor,
    ActorState,
    SupervisionStrategy,
    get_global_actor_system,
)


class TestActor(Actor):
    def __init__(self, actor_id, probe):
        super().__init__(actor_id)
        self.probe = probe
        self.state = "initial"
        self.register_handler("ping", self.handle_ping)
        self.register_handler("fail", self.handle_fail)
        self.register_handler("change_behavior", self.handle_change_behavior)

    async def handle_ping(self, message):
        self.probe.ping()
        return "pong"

    async def handle_fail(self, message):
        self.probe.fail()
        raise Exception("I am failing as requested")

    async def handle_change_behavior(self, message):
        self.probe.change_behavior()
        self.become({"ping": self.handle_ping_after_change})

    async def handle_ping_after_change(self, message):
        self.probe.ping_after_change()
        return "pong_after_change"

    async def pre_restart(self, reason):
        self.probe.pre_restart()

    async def post_stop(self):
        self.probe.post_stop()


class TestSupervisorActor(Actor):
    def __init__(self, actor_id, probe, strategy):
        super().__init__(actor_id)
        self.probe = probe
        self.supervision_strategy = strategy


class ActorSystemTests(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # Reset global actor system for each test
        from core import actor_system

        actor_system._global_actor_system = None
        self.system = self.loop.run_until_complete(get_global_actor_system())

    def tearDown(self):
        async def stop_system():
            if self.system._running:
                await self.system.stop()

        self.loop.run_until_complete(stop_system())
        self.loop.close()

    def test_actor_creation_and_messaging(self):
        async def run_test():
            probe = MagicMock()
            actor_ref = await self.system.create_actor(TestActor, "test_actor", probe)
            self.assertIsNotNone(actor_ref)

            response = await actor_ref.ask("ping", {})
            self.assertEqual(response, "pong")
            probe.ping.assert_called_once()

        self.loop.run_until_complete(run_test())

    def test_supervision_restart_strategy(self):
        async def run_test():
            probe = MagicMock()
            supervisor_ref = await self.system.create_actor(
                TestSupervisorActor, "supervisor", probe, SupervisionStrategy.RESTART
            )
            supervisor = self.system.get_actor("supervisor")
            child_ref = await supervisor.create_child(TestActor, "child", probe)

            # The child actor will fail, and the supervisor will restart it.
            await child_ref.tell("fail", {})

            # Give the system time to restart the actor
            await asyncio.sleep(0.1)

            probe.fail.assert_called_once()
            probe.pre_restart.assert_called_once()
            probe.post_stop.assert_called_once()

            # The actor should be in a running state after restart
            child = self.system.get_actor("child")
            self.assertIsNotNone(child)
            self.assertEqual(child.state, ActorState.RUNNING)

        self.loop.run_until_complete(run_test())

    def test_supervision_stop_strategy(self):
        async def run_test():
            probe = MagicMock()
            supervisor_ref = await self.system.create_actor(
                TestSupervisorActor, "supervisor", probe, SupervisionStrategy.STOP
            )
            supervisor = self.system.get_actor("supervisor")
            child_ref = await supervisor.create_child(TestActor, "child", probe)

            await child_ref.tell("fail", {})

            await asyncio.sleep(0.1)

            probe.fail.assert_called_once()
            probe.post_stop.assert_called_once()
            self.assertIsNone(self.system.get_actor("child"))

        self.loop.run_until_complete(run_test())

    def test_behavior_change(self):
        async def run_test():
            probe = MagicMock()
            actor_ref = await self.system.create_actor(TestActor, "test_actor", probe)

            response = await actor_ref.ask("ping", {})
            self.assertEqual(response, "pong")
            probe.ping.assert_called_once()

            await actor_ref.tell("change_behavior", {})
            await asyncio.sleep(0)  # Allow the message to be processed
            probe.change_behavior.assert_called_once()

            response = await actor_ref.ask("ping", {})
            self.assertEqual(response, "pong_after_change")
            probe.ping_after_change.assert_called_once()

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
