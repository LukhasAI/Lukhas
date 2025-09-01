"""
Consciousness-Colony Integration Module
Enables distributed consciousness processing through colony architecture
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

import numpy as np
from consciousness.systems.engine import (
    LUKHASConsciousnessEngine,
)

from candidate.bridge.shared_state import SharedStateManager
from candidate.core.colonies.creativity_colony import CreativityColony
from candidate.core.colonies.memory_colony import MemoryColony
from candidate.core.colonies.reasoning_colony import ReasoningColony
from candidate.core.common import get_logger
from candidate.core.swarm import SwarmHub

logger = get_logger(__name__)


class DistributedConsciousnessEngine(LUKHASConsciousnessEngine):
    """
    Extended consciousness engine that leverages colony architecture
    for distributed processing of consciousness tasks.
    """

    def __init__(
        self,
        user_id_context: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """Initialize distributed consciousness engine with colony support."""
        super().__init__(user_id_context, config)

        self.logger = logging.getLogger(f"{__name__}.{user_id_context or 'system'}")
        self.logger.info("Initializing DistributedConsciousnessEngine with colony integration")

        # Initialize consciousness colonies
        self.reasoning_colony = ReasoningColony("consciousness-reasoning")
        self.memory_colony = MemoryColony("consciousness-memory")
        self.creativity_colony = CreativityColony("consciousness-creativity")

        # Swarm hub for colony coordination
        self.swarm_hub = SwarmHub()

        # Event bus for inter-colony communication
        self.event_bus = EventBus()

        # Shared state manager
        self.shared_state = SharedStateManager()

        # Colony processing metrics
        self.colony_metrics = {
            "reasoning": {"tasks": 0, "success_rate": 1.0},
            "memory": {"tasks": 0, "success_rate": 1.0},
            "creativity": {"tasks": 0, "success_rate": 1.0},
        }

        self._running = False
        self._colony_tasks = []

    async def start(self):
        """Start the distributed consciousness engine and all colonies."""
        if self._running:
            return

        self.logger.info("Starting distributed consciousness engine with colonies...")
        self._running = True

        # Start all consciousness colonies
        try:
            await self.reasoning_colony.start()
            await self.memory_colony.start()
            await self.creativity_colony.start()

            # Register colonies with swarm hub
            self.swarm_hub.register_colony(self.reasoning_colony)
            self.swarm_hub.register_colony(self.memory_colony)
            self.swarm_hub.register_colony(self.creativity_colony)

            # Subscribe to colony events
            self.kernel_bus.subscribe("colony.reasoning.complete", self._handle_reasoning_complete)
            self.kernel_bus.subscribe("colony.memory.stored", self._handle_memory_stored)
            self.kernel_bus.subscribe("colony.creativity.insight", self._handle_creative_insight)

            self.logger.info("Distributed consciousness engine started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start distributed consciousness engine: {e}")
            self._running = False
            raise

    async def stop(self):
        """Stop the distributed consciousness engine and all colonies."""
        if not self._running:
            return

        self.logger.info("Stopping distributed consciousness engine...")
        self._running = False

        # Cancel any pending colony tasks
        for task in self._colony_tasks:
            if not task.done():
                task.cancel()

        # Stop all colonies
        await self.reasoning_colony.stop()
        await self.memory_colony.stop()
        await self.creativity_colony.stop()

        self.logger.info("Distributed consciousness engine stopped")

    async def process_consciousness_task(self, task_type: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process consciousness tasks using distributed colony architecture.

        Args:
            task_type: Type of consciousness task (reflection, integration, awareness)
            task_data: Task-specific data

        Returns:
            Processed result from colony collaboration
        """
        self.logger.info(f"Processing distributed consciousness task: {task_type}")

        task_id = f"{task_type}-{datetime.now().timestamp()}"

        try:
            if task_type == "reflection":
                result = await self._process_reflection_distributed(task_id, task_data)
            elif task_type == "integration":
                result = await self._process_integration_distributed(task_id, task_data)
            elif task_type == "awareness":
                result = await self._process_awareness_distributed(task_id, task_data)
            else:
                # Default to reasoning colony for unknown types
                result = await self.reasoning_colony.execute_task(task_id, task_data)

            # Update metrics
            self._update_colony_metrics(task_type, True)

            return result

        except Exception as e:
            self.logger.error(f"Error in distributed consciousness processing: {e}")
            self._update_colony_metrics(task_type, False)
            raise

    async def _process_reflection_distributed(self, task_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process reflection using multiple colonies in parallel."""
        self.logger.debug(f"Distributing reflection task {task_id} across colonies")

        # Create parallel tasks for each colony
        tasks = []

        # Reasoning colony analyzes logical patterns
        reasoning_task = {
            "type": "analyze_patterns",
            "experience": data.get("experience", {}),
            "context": data.get("context", {}),
        }
        tasks.append(self.reasoning_colony.execute_task(f"{task_id}-reasoning", reasoning_task))

        # Memory colony retrieves relevant past experiences
        memory_task = {
            "type": "retrieve_similar",
            "query": data.get("experience", {}),
            "limit": 5,
        }
        tasks.append(self.memory_colony.execute_task(f"{task_id}-memory", memory_task))

        # Creativity colony generates novel insights
        creativity_task = {
            "type": "generate_insights",
            "input": data.get("experience", {}),
            "mode": "reflective",
        }
        tasks.append(self.creativity_colony.execute_task(f"{task_id}-creativity", creativity_task))

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process and integrate results
        integrated_result = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "reasoning_analysis": (results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}),
            "memory_context": (results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}),
            "creative_insights": (results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}),
            "distributed": True,
        }

        # Store integrated result in shared state
        await self.shared_state.update("consciousness_reflections", {task_id: integrated_result})

        return integrated_result

    async def _process_integration_distributed(self, task_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process integration tasks across colonies with coordination."""
        self.logger.debug(f"Processing integration task {task_id} with colony coordination")

        # First, use reasoning colony to create integration plan
        planning_task = {
            "type": "create_integration_plan",
            "sources": data.get("sources", []),
            "target": data.get("target", "unified_understanding"),
        }

        plan = await self.reasoning_colony.execute_task(f"{task_id}-planning", planning_task)

        # Execute integration steps based on plan
        integration_results = []

        for step in plan.get("steps", []):
            if step["colony"] == "memory":
                result = await self.memory_colony.execute_task(f"{task_id}-step-{step['id']}", step["task"])
            elif step["colony"] == "creativity":
                result = await self.creativity_colony.execute_task(f"{task_id}-step-{step['id']}", step["task"])
            else:
                result = await self.reasoning_colony.execute_task(f"{task_id}-step-{step['id']}", step["task"])
            integration_results.append(result)

        # Final integration by reasoning colony
        final_integration = {
            "type": "finalize_integration",
            "partial_results": integration_results,
            "original_data": data,
        }

        final_result = await self.reasoning_colony.execute_task(f"{task_id}-final", final_integration)

        return {
            "task_id": task_id,
            "integration_complete": True,
            "result": final_result,
            "colony_contributions": len(integration_results),
            "distributed": True,
        }

    async def _process_awareness_distributed(self, task_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process awareness updates using colony consensus."""
        self.logger.debug(f"Processing awareness task {task_id} with colony consensus")

        # Each colony evaluates awareness from its perspective
        awareness_tasks = []

        # Reasoning colony evaluates logical awareness
        reasoning_awareness = {
            "type": "evaluate_logical_awareness",
            "stimuli": data.get("stimuli", []),
            "current_state": self.global_consciousness_state.to_dict(),
        }
        awareness_tasks.append(self.reasoning_colony.execute_task(f"{task_id}-reasoning-aware", reasoning_awareness))

        # Memory colony evaluates contextual awareness
        memory_awareness = {
            "type": "evaluate_contextual_awareness",
            "stimuli": data.get("stimuli", []),
            "history_depth": 10,
        }
        awareness_tasks.append(self.memory_colony.execute_task(f"{task_id}-memory-aware", memory_awareness))

        # Creativity colony evaluates emergent awareness
        creativity_awareness = {
            "type": "evaluate_emergent_awareness",
            "stimuli": data.get("stimuli", []),
            "exploration_mode": "divergent",
        }
        awareness_tasks.append(self.creativity_colony.execute_task(f"{task_id}-creativity-aware", creativity_awareness))

        # Gather all awareness evaluations
        awareness_results = await asyncio.gather(*awareness_tasks)

        # Calculate consensus awareness level
        awareness_scores = []
        for result in awareness_results:
            if isinstance(result, dict) and "awareness_level" in result:
                awareness_scores.append(result["awareness_level"])

        consensus_awareness = np.mean(awareness_scores) if awareness_scores else 0.5

        # Update global consciousness state
        self.global_consciousness_state.awareness_level = (
            0.7 * self.global_consciousness_state.awareness_level + 0.3 * consensus_awareness
        )

        return {
            "task_id": task_id,
            "consensus_awareness": consensus_awareness,
            "colony_evaluations": awareness_results,
            "updated_global_awareness": self.global_consciousness_state.awareness_level,
            "distributed": True,
        }

    def _update_colony_metrics(self, task_type: str, success: bool):
        """Update colony processing metrics."""
        colony_map = {
            "reflection": "reasoning",
            "integration": "memory",
            "awareness": "creativity",
        }

        colony = colony_map.get(task_type, "reasoning")
        self.colony_metrics[colony]["tasks"] += 1

        if success:
            # Update success rate with exponential moving average
            alpha = 0.1
            self.colony_metrics[colony]["success_rate"] = (
                alpha * 1.0 + (1 - alpha) * self.colony_metrics[colony]["success_rate"]
            )
        else:
            self.colony_metrics[colony]["success_rate"] = (
                alpha * 0.0 + (1 - alpha) * self.colony_metrics[colony]["success_rate"]
            )

    async def _handle_reasoning_complete(self, event_data: dict[str, Any]):
        """Handle completion events from reasoning colony."""
        self.logger.debug(f"Reasoning colony completed task: {event_data.get('task_id')}")
        await self.event_bus.emit("consciousness.reasoning.integrated", event_data)

    async def _handle_memory_stored(self, event_data: dict[str, Any]):
        """Handle memory storage events from memory colony."""
        self.logger.debug(f"Memory colony stored: {event_data.get('memory_id')}")
        await self.event_bus.emit("consciousness.memory.updated", event_data)

    async def _handle_creative_insight(self, event_data: dict[str, Any]):
        """Handle creative insights from creativity colony."""
        self.logger.debug(f"Creativity colony generated insight: {event_data.get('insight_id')}")

        # Potentially trigger new reflection based on insight
        if event_data.get("significance", 0) > 0.8:
            reflection_task = {
                "experience": {"type": "creative_insight", "content": event_data},
                "context": {"triggered_by": "high_significance_insight"},
            }
            asyncio.create_task(self.process_consciousness_task("reflection", reflection_task))

    async def get_colony_status(self) -> dict[str, Any]:
        """Get status of all consciousness colonies."""
        status = {
            "engine_running": self._running,
            "colonies": {
                "reasoning": {
                    "active": (self.reasoning_colony.active if hasattr(self.reasoning_colony, "active") else False),
                    "metrics": self.colony_metrics["reasoning"],
                },
                "memory": {
                    "active": (self.memory_colony.active if hasattr(self.memory_colony, "active") else False),
                    "metrics": self.colony_metrics["memory"],
                },
                "creativity": {
                    "active": (self.creativity_colony.active if hasattr(self.creativity_colony, "active") else False),
                    "metrics": self.colony_metrics["creativity"],
                },
            },
            "total_distributed_tasks": sum(m["tasks"] for m in self.colony_metrics.values()),
            "average_success_rate": np.mean([m["success_rate"] for m in self.colony_metrics.values()]),
        }

        return status

    async def perform_distributed_reflection(self, experience: dict[str, Any]) -> dict[str, Any]:
        """
        High-level method to perform reflection using distributed colonies.
        Overrides base class method to use colony architecture.
        """
        self.logger.info("Performing distributed consciousness reflection")

        # Process through awareness first (can be distributed)
        awareness_task = {"stimuli": [experience], "mode": "focused"}
        awareness_result = await self.process_consciousness_task("awareness", awareness_task)

        # Then perform distributed reflection
        reflection_task = {
            "experience": experience,
            "awareness": awareness_result,
            "context": {
                "current_state": self.global_consciousness_state.to_dict(),
                "timestamp": datetime.now().isoformat(),
            },
        }

        reflection_result = await self.process_consciousness_task("reflection", reflection_task)

        # Update consciousness state based on distributed processing
        self.global_consciousness_state.reflection_count = (
            self.global_consciousness_state.reflection_count + 1
            if hasattr(self.global_consciousness_state, "reflection_count")
            else 1
        )

        # Emit event for other systems
        await self.event_bus.emit(
            "consciousness.distributed.reflected",
            {
                "experience": experience,
                "reflection": reflection_result,
                "colonies_used": ["reasoning", "memory", "creativity"],
            },
        )

        return reflection_result


# Example usage
async def demo_distributed_consciousness():
    """Demonstrate distributed consciousness processing."""

    # Initialize distributed consciousness engine
    engine = DistributedConsciousnessEngine(user_id_context="demo_distributed")

    # Start the engine and colonies
    await engine.start()

    try:
        # Example experience to reflect on
        experience = {
            "type": "user_interaction",
            "content": "Complex philosophical question about consciousness",
            "emotional_context": {"curiosity": 0.8, "confusion": 0.3},
            "timestamp": datetime.now().isoformat(),
        }

        # Perform distributed reflection
        reflection = await engine.perform_distributed_reflection(experience)
        print("Distributed Reflection Result:", reflection)

        # Get colony status
        status = await engine.get_colony_status()
        print("\nColony Status:", status)

        # Process a complex integration task
        integration_data = {
            "sources": [
                {"type": "sensory", "data": "visual_input"},
                {"type": "memory", "data": "past_experience"},
                {"type": "symbolic", "data": "abstract_concept"},
            ],
            "target": "unified_understanding",
        }

        integration_result = await engine.process_consciousness_task("integration", integration_data)
        print("\nIntegration Result:", integration_result)

    finally:
        # Clean shutdown
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(demo_distributed_consciousness())
