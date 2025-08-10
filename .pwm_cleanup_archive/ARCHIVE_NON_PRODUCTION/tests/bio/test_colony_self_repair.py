import asyncio
import unittest

from bio.bio_utilities import simulate_colony_self_repair
from core.actor_system import Actor, get_global_actor_system
from core.supervision import SupervisorActor


class FailingUnit(Actor):
    async def pre_start(self):
        await super().pre_start()
        self.register_handler("fail", self._handle_fail)

    async def _handle_fail(self, message):
        raise RuntimeError("boom")


class TestColonySelfRepair(unittest.IsolatedAsyncioTestCase):
    async def test_simulation_positive_delta(self):
        result = await simulate_colony_self_repair({"repair_protein": 2})
        self.assertIn("health_delta", result)
        self.assertGreater(result["health_delta"], 0)

    async def test_supervisor_tracks_repair(self):
        system = await get_global_actor_system()
        supervisor_ref = await system.create_actor(
            SupervisorActor,
            "repair-supervisor",
            enable_self_repair=True,
        )
        supervisor = system.get_actor("repair-supervisor")
        child_ref = await supervisor.create_child(FailingUnit, "repair-child")

        with self.assertRaises(RuntimeError):
            await child_ref.ask("fail", {})
        await asyncio.sleep(0.1)
        stats = supervisor.get_supervision_stats()
        self.assertEqual(stats["health_metrics"]["attempts"], 1)
        await system.stop()
        from core import actor_system

        actor_system._global_actor_system = None


if __name__ == "__main__":
    unittest.main()
