import asyncio
import unittest

from core.actor_system import (
    Actor,
    AIAgentActor,
    SupervisionStrategy,
    get_global_actor_system,
)


class SupervisorActor(AIAgentActor):
    def __init__(self, actor_id: str, strategy: SupervisionStrategy):
        super().__init__(actor_id)
        self._strategy = strategy

    def supervision_strategy(self) -> SupervisionStrategy:
        return self._strategy


class FailingActor(Actor):
    async def pre_start(self):
        await super().pre_start()
        self.register_handler("fail", self._handle_fail)

    async def _handle_fail(self, message):
        raise RuntimeError("I am a failing actor")


class TestActorSupervision(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.system = self.loop.run_until_complete(get_global_actor_system())

    def tearDown(self):
        async def _tear_down():
            await self.system.stop()
            # Reset global actor system for subsequent tests
            from core import actor_system

            actor_system._global_actor_system = None

        self.loop.run_until_complete(_tear_down())
        self.loop.close()

    def test_restart_strategy(self):
        async def _test():
            supervisor_ref = await self.system.create_actor(
                SupervisorActor, "supervisor-1", strategy=SupervisionStrategy.RESTART
            )
            supervisor = self.system.get_actor("supervisor-1")
            child_ref = await supervisor.create_child(FailingActor, "child-1")
            child_actor_pre_failure = self.system.get_actor("child-1")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisor time to react
            await asyncio.sleep(0.1)

            # Check if the child was restarted
            new_child_actor = self.system.get_actor("child-1")
            self.assertIsNotNone(new_child_actor)
            self.assertNotEqual(id(child_actor_pre_failure), id(new_child_actor))

        self.loop.run_until_complete(_test())

    def test_stop_strategy(self):
        async def _test():
            supervisor_ref = await self.system.create_actor(
                SupervisorActor, "supervisor-2", strategy=SupervisionStrategy.STOP
            )
            supervisor = self.system.get_actor("supervisor-2")
            child_ref = await supervisor.create_child(FailingActor, "child-2")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisor time to react
            await asyncio.sleep(0.1)

            # Check if the child was stopped
            stopped_child_ref = self.system.get_actor_ref("child-2")
            self.assertIsNone(stopped_child_ref)

        self.loop.run_until_complete(_test())

    def test_escalate_strategy(self):
        async def _test():
            grand_supervisor_ref = await self.system.create_actor(
                SupervisorActor,
                "grand-supervisor-1",
                strategy=SupervisionStrategy.STOP,
            )
            grand_supervisor = self.system.get_actor("grand-supervisor-1")

            supervisor_ref = await grand_supervisor.create_child(
                SupervisorActor, "supervisor-3", strategy=SupervisionStrategy.ESCALATE
            )
            supervisor = self.system.get_actor("supervisor-3")

            child_ref = await supervisor.create_child(FailingActor, "child-3")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisors time to react
            await asyncio.sleep(0.1)

            # Check if the failure was escalated and the supervisor was stopped
            stopped_supervisor_ref = self.system.get_actor_ref("supervisor-3")
            self.assertIsNone(stopped_supervisor_ref)

        self.loop.run_until_complete(_test())

        async def _test():
            supervisor_ref = await self.system.create_actor(
                SupervisorActor, "supervisor-1", strategy=SupervisionStrategy.RESTART
            )
            supervisor = self.system.get_actor("supervisor-1")
            child_ref = await supervisor.create_child(FailingActor, "child-1")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisor time to react
            await asyncio.sleep(0.1)

            # Check if the child was restarted
            new_child_ref = self.system.get_actor_ref("child-1")
            self.assertIsNotNone(new_child_ref)
            self.assertNotEqual(child_ref, new_child_ref)

        self.loop.run_until_complete(_test())

    def test_stop_strategy(self):
        async def _test():
            supervisor_ref = await self.system.create_actor(
                SupervisorActor, "supervisor-2", strategy=SupervisionStrategy.STOP
            )
            supervisor = self.system.get_actor("supervisor-2")
            child_ref = await supervisor.create_child(FailingActor, "child-2")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisor time to react
            await asyncio.sleep(0.1)

            # Check if the child was stopped
            stopped_child_ref = self.system.get_actor_ref("child-2")
            self.assertIsNone(stopped_child_ref)

        self.loop.run_until_complete(_test())

    def test_escalate_strategy(self):
        async def _test():
            grand_supervisor_ref = await self.system.create_actor(
                SupervisorActor,
                "grand-supervisor-1",
                strategy=SupervisionStrategy.STOP,
            )
            grand_supervisor = self.system.get_actor("grand-supervisor-1")

            supervisor_ref = await grand_supervisor.create_child(
                SupervisorActor, "supervisor-3", strategy=SupervisionStrategy.ESCALATE
            )
            supervisor = self.system.get_actor("supervisor-3")

            child_ref = await supervisor.create_child(FailingActor, "child-3")

            # Make the child fail
            with self.assertRaises(RuntimeError):
                await child_ref.ask("fail", {})

            # Give the supervisors time to react
            await asyncio.sleep(0.1)

            # Check if the failure was escalated and the supervisor was stopped
            stopped_supervisor_ref = self.system.get_actor_ref("supervisor-3")
            self.assertIsNone(stopped_supervisor_ref)

        self.loop.run_until_complete(_test())


if __name__ == "__main__":
    unittest.main()
