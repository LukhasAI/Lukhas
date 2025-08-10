import asyncio
import json
import logging
import os
import sys
import time
from collections import defaultdict
from typing import List

import psutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.actor_system import (
    AIAgentActor,
    SupervisionStrategy,
    get_global_actor_system,
)
from core.distributed_tracing import get_global_tracer
from core.event_bus import get_global_event_bus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Colony:
    def __init__(self, name: str, actor_system):
        self.name = name
        self.actor_system = actor_system
        self.actors: List[str] = []

    async def start(self):
        pass

    async def stop(self):
        for actor_id in self.actors:
            await self.actor_system.stop_actor(actor_id)


class DataIngestionColony(Colony):
    async def start(self):
        for i in range(3):
            actor_id = f"{self.name}-ingestor-{i}"
            await self.actor_system.create_actor(AIAgentActor, actor_id)
            self.actors.append(actor_id)


class RealtimeAnalyticsColony(Colony):
    async def start(self):
        for i in range(5):
            actor_id = f"{self.name}-analyzer-{i}"
            await self.actor_system.create_actor(AIAgentActor, actor_id)
            self.actors.append(actor_id)


class ValidationMatrix:
    def __init__(self):
        self.scenarios = {
            "S01": self.run_high_message_volume,
            "S02": self.run_network_partition,
            "S03": self.run_actor_failure,
            "S04": self.run_resource_exhaustion,
            "S05": self.run_conflicting_goals,
            "S06": self.run_symbolic_drift,
        }
        self.results = {}

    async def run(self):
        for scenario_id, scenario_func in self.scenarios.items():
            logger.info(f"Running scenario: {scenario_id}")
            system = await get_global_actor_system()
            event_bus = await get_global_event_bus()
            tracer = get_global_tracer()
            collector = ObservabilityCollector()
            collector.start()

            colonies = [
                DataIngestionColony("data-ingestion", system),
                RealtimeAnalyticsColony("realtime-analytics", system),
            ]

            for colony in colonies:
                await colony.start()

            start_time = time.time()
            try:
                await scenario_func(system, event_bus, tracer, collector, colonies)
            except Exception as e:
                logger.error(f"Scenario {scenario_id} failed: {e}")
            end_time = time.time()

            self.results[scenario_id] = {
                "duration": end_time - start_time,
                "metrics": collector.get_metrics(),
            }

            for colony in colonies:
                await colony.stop()

            collector.stop()
            await system.stop()
            await event_bus.stop()
            from core import actor_system, event_bus

            actor_system._global_actor_system = None
            event_bus._global_event_bus = None

    async def run_high_message_volume(
        self, system, event_bus, tracer, collector, colonies
    ):
        with tracer.trace_operation("high_message_volume_scenario") as trace_context:
            logger.info("Simulating high message volume...")
            start_time = time.time()
            tasks = []
            for i in range(1000):
                tasks.append(kernel_bus.emit("some_event", {"i": i}))
            await asyncio.gather(*tasks)

            # Wait for all events to be processed
            while not event_bus._queue.empty():
                await asyncio.sleep(0.01)

            end_time = time.time()
            duration = end_time - start_time
            collector.record_metric("system", "high_message_volume_duration", duration)
            tracer.add_tag(trace_context, "duration", duration)

    async def run_network_partition(
        self, system, event_bus, tracer, collector, colonies
    ):
        logger.info("Simulating network partition...")
        # This is a simplified simulation. A real implementation would involve
        # manipulating network interfaces or using a network simulator.
        analytics_colony = next(c for c in colonies if c.name == "realtime-analytics")
        for actor_id in analytics_colony.actors:
            p2p_node = await system.get_p2p_node(actor_id)
            if p2p_node:
                await p2p_node.stop()

        await asyncio.sleep(5)

        for actor_id in analytics_colony.actors:
            p2p_node = await system.get_p2p_node(actor_id)
            if p2p_node:
                await p2p_node.start()

    async def run_actor_failure(self, system, event_bus, tracer, collector, colonies):
        with tracer.trace_operation("actor_failure_scenario") as trace_context:
            logger.info("Simulating actor failure...")
            analytics_colony = next(
                c for c in colonies if c.name == "realtime-analytics"
            )
            actor_to_fail_id = "failing-actor"

            class Supervisor(AIAgentActor):
                def supervision_strategy(self) -> SupervisionStrategy:
                    return SupervisionStrategy.RESTART

            supervisor_ref = await system.create_actor(Supervisor, "supervisor-temp")
            supervisor = system.get_actor("supervisor-temp")

            class FailingActor(AIAgentActor):
                async def pre_start(self):
                    await super().pre_start()
                    self.register_handler("fail", self._handle_fail)

                async def _handle_fail(self, message):
                    raise RuntimeError("I am a failing actor")

            child_ref = await supervisor.create_child(FailingActor, actor_to_fail_id)

            start_time = time.time()
            try:
                await child_ref.ask("fail", {})
            except RuntimeError:
                pass  # Expected

            # Wait for the actor to be restarted
            while system.get_actor(actor_to_fail_id) is None:
                await asyncio.sleep(0.01)

            end_time = time.time()
            duration = end_time - start_time
            collector.record_metric("system", "actor_failure_recovery_time", duration)
            tracer.add_tag(trace_context, "duration", duration)

    async def run_resource_exhaustion(
        self, system, event_bus, tracer, collector, colonies
    ):
        with tracer.trace_operation("resource_exhaustion_scenario") as trace_context:
            logger.info("Simulating resource exhaustion...")
            # This is a simplified simulation. A real implementation would involve
            # running the system in a container with limited resources.

            # Create a large number of actors
            tasks = []
            for i in range(1000):
                tasks.append(system.create_actor(AIAgentActor, f"exhaustion-actor-{i}"))
            await asyncio.gather(*tasks)

            # Record memory usage
            mem_before = psutil.virtual_memory().percent
            collector.record_metric("system", "memory_usage_before_stress", mem_before)
            tracer.add_tag(trace_context, "mem_before", mem_before)

            # Stress the system
            tasks = []
            for i in range(10000):
                tasks.append(kernel_bus.emit("some_event", {"i": i}))
            await asyncio.gather(*tasks)

            # Record memory usage after stress
            mem_after = psutil.virtual_memory().percent
            collector.record_metric("system", "memory_usage_after_stress", mem_after)
            tracer.add_tag(trace_context, "mem_after", mem_after)

    async def run_conflicting_goals(
        self, system, event_bus, tracer, collector, colonies
    ):
        with tracer.trace_operation("conflicting_goals_scenario") as trace_context:
            logger.info("Simulating conflicting goals...")

            class GoalActor(AIAgentActor):
                async def pre_start(self):
                    await super().pre_start()
                    self.register_handler("set_goal", self._handle_set_goal)

                async def _handle_set_goal(self, message):
                    self.memory["goal"] = message.payload["goal"]

            actor1_id = colonies[0].actors[0]
            actor2_id = colonies[1].actors[0]

            await system.stop_actor(actor1_id)
            await system.stop_actor(actor2_id)

            actor1_ref = await system.create_actor(GoalActor, actor1_id)
            actor2_ref = await system.create_actor(GoalActor, actor2_id)

            if actor1_ref and actor2_ref:
                await actor1_ref.tell("set_goal", {"goal": "A"})
                await actor2_ref.tell("set_goal", {"goal": "B"})
            await asyncio.sleep(1)

    async def run_symbolic_drift(self, system, event_bus, tracer, collector, colonies):
        with tracer.trace_operation("symbolic_drift_scenario") as trace_context:
            logger.info("Simulating symbolic drift...")
            # This is a simplified simulation. A real implementation would involve
            # changing the meaning of a symbol in the system.
            await kernel_bus.emit(
                "symbol_update", {"symbol": "X", "meaning": "new_meaning"}
            )
            await asyncio.sleep(1)

    def generate_report(self):
        with open("colony_validation_report.md", "w") as f:
            f.write("# Colony Validation Report\n\n")
            for scenario_id, result in self.results.items():
                f.write(f"## Scenario: {scenario_id}\n\n")
                f.write(f"Duration: {result['duration']:.2f}s\n\n")
                f.write("### Metrics\n\n")
                f.write("```json\n")
                f.write(json.dumps(result["metrics"], indent=2))
                f.write("\n```\n\n")


async def main():
    matrix = ValidationMatrix()
    await matrix.run()
    matrix.generate_report()


if __name__ == "__main__":
    # The full implementation of ObservabilityCollector is not available
    # so we will mock it for now.
    class ObservabilityCollector:
        def __init__(self):
            self.metrics = defaultdict(list)

        def start(self):
            pass

        def stop(self):
            pass

        def get_metrics(self):
            return self.metrics

        def record_metric(self, actor_id, metric_name, value):
            self.metrics[metric_name].append(
                {"actor_id": actor_id, "value": value, "timestamp": time.time()}
            )

    from core.observability import collector

    collector.ObservabilityCollector = ObservabilityCollector

    asyncio.run(main())
