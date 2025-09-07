"""
Example of a module that integrates with the endocrine orchestration system.
This shows how modules can send stress signals and adapt to hormonal states.
"""
import asyncio
import random
import time
from typing import Any

import streamlit as st


class EndocrineAwareModule:
    """
    Example module that can communicate stress and adapt to hormonal states.
    """

    def __init__(self, name: str):
        self.name = name
        self.endocrine_integration = None
        self.current_load = 0.5
        self.error_rate = 0.02
        self.stress_level = 0.3
        self.processing_multiplier = 1.0

        # Modulatable parameters
        self.modulatable_params = [
            "processing_speed",
            "error_tolerance",
            "memory_usage",
            "attention_span",
        ]

        # Task queue
        self.task_queue = asyncio.Queue()
        self.is_running = False

    # === Endocrine Integration ===

    def set_endocrine_integration(self, integration):
        """Set the endocrine integration for hormonal modulation"""
        self.endocrine_integration = integration

    def get_modulatable_parameters(self) -> list[str]:
        """Return parameters that can be modulated by hormones"""
        return self.modulatable_params

    # === Component Interface ===

    async def start(self):
        """Start the module"""
        self.is_running = True
        # Start background processing
        asyncio.create_task(self._process_tasks())

    async def stop(self):
        """Stop the module"""
        self.is_running = False

    async def health_check(self) -> bool:
        """Simple health check"""
        return self.stress_level < 0.8 and self.error_rate < 0.1

    async def get_detailed_health(self) -> dict[str, Any]:
        """Detailed health information"""
        return {
            "stress_level": self.stress_level,
            "error_rate": self.error_rate,
            "current_load": self.current_load,
            "warning_signs": 1 if self.stress_level > 0.6 else 0,
            "task_queue_size": self.task_queue.qsize(),
        }

    # === Stress and Load Management ===

    async def get_stress_level(self) -> float:
        """Get current stress level"""
        return self.stress_level

    async def get_error_rate(self) -> float:
        """Get current error rate"""
        return self.error_rate

    async def get_load(self) -> float:
        """Get current processing load"""
        return self.current_load

    # === Resource Management ===

    async def process(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Process an operation"""
        op_type = operation.get("type")

        if op_type == "adjust_resources":
            multiplier = operation.get("multiplier", 1.0)
            self.processing_multiplier = multiplier
            return {"success": True, "new_multiplier": multiplier}

        elif op_type == "adjust_processing":
            target_load = operation.get("target_load", 0.5)
            self.current_load = target_load
            return {"success": True, "new_load": target_load}

        elif op_type == "endocrine_state":
            # Handle endocrine state changes
            return await self._handle_endocrine_state(operation)

        elif op_type == "task":
            # Queue a task for processing
            await self.task_queue.put(operation.get("data", {}))
            return {"success": True, "queued": True}

        return {"success": False, "error": "Unknown operation"}

    async def _handle_endocrine_state(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Handle endocrine state notifications"""
        state = operation.get("state")
        action = operation.get("action")

        if state == "high_stress" and action == "reduce_non_critical_operations":
            # Reduce processing to critical tasks only
            self.processing_multiplier *= 0.7

        elif state == "rest_needed" and action == "enter_maintenance_mode":
            # Switch to maintenance mode
            self.current_load = 0.2
            # Process backlog slowly

        elif state == "optimal_performance" and action == "maximize_exploration":
            # Increase exploration and processing
            self.processing_multiplier *= 1.5

        elif state == "normal" and action == "resume_normal_operations":
            # Reset to normal
            self.processing_multiplier = 1.0
            self.current_load = 0.5

        return {"success": True, "state_handled": state}

    # === Task Processing ===

    async def _process_tasks(self):
        """Background task processor that adapts to hormonal state"""
        while self.is_running:
            try:
                # Get hormonal modulation if available
                speed_modulation = 1.0
                if self.endocrine_integration:
                    speed_modulation = self.endocrine_integration.get_modulation_factor(self.name, "processing_speed")

                # Calculate actual processing delay
                base_delay = 1.0  # 1 second base
                actual_delay = base_delay / (self.processing_multiplier * speed_modulation)

                # Process task if available
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=actual_delay)

                    # Simulate processing
                    await self._process_single_task(task)

                except asyncio.TimeoutError:
                    # No tasks, just wait
                    pass

                # Update stress based on queue size
                queue_size = self.task_queue.qsize()
                self.stress_level = min(1.0, queue_size / 100)  # Stress increases with queue

                # Simulate occasional errors based on stress
                if random.random() < self.stress_level * 0.1:
                    self.error_rate = min(1.0, self.error_rate + 0.01)
                else:
                    self.error_rate = max(0.0, self.error_rate - 0.001)

                # Send feedback to endocrine system if stress is high
                if self.stress_level > 0.7 and self.endocrine_integration:
                    self.endocrine_integration.inject_system_feedback(self.name, "overload", self.stress_level)

                await asyncio.sleep(actual_delay)

            except Exception as e:
                print(f"Error in {self.name}: {e}")
                self.error_rate = min(1.0, self.error_rate + 0.05)

    async def _process_single_task(self, task: dict[str, Any]):
        """Process a single task"""
        # Simulate work based on load
        processing_time = 0.1 * (1.0 + self.current_load)
        await asyncio.sleep(processing_time)

        # Update load based on task complexity
        complexity = task.get("complexity", 0.5)
        self.current_load = 0.9 * self.current_load + 0.1 * complexity


# === Example Usage ===


async def example_usage():
    """
    Example of how to use the endocrine-aware module with the orchestrator.
    """
    from bio.simulation_controller import BioSimulationController
    from candidate.orchestration.endocrine_orchestrator import (
        EndocrineOrchestrator,
        EndocrineOrchestratorConfig,
    )

    # Create bio controller
    bio_controller = BioSimulationController()
    await bio_controller.initialize()

    # Create orchestrator config
    config = EndocrineOrchestratorConfig(
        name="example_orchestrator",
        module_name="example",
        enable_hormonal_modulation=True,
        stress_threshold=0.7,
        circadian_awareness=True,
    )

    # Create orchestrator
    orchestrator = EndocrineOrchestrator(config, bio_controller)

    # Register our example module
    orchestrator.register_component("worker1", "worker")
    orchestrator.register_component("worker2", "worker")

    # Initialize and start
    await orchestrator.initialize()
    await orchestrator.start()

    # Simulate some work
    for i in range(100):
        # Send tasks to workers
        await orchestrator.process(
            {
                "type": "task",
                "component": "worker1",
                "data": {"id": i, "complexity": random.random()},
            }
        )

        if i % 2 == 0:
            await orchestrator.process(
                {
                    "type": "task",
                    "component": "worker2",
                    "data": {"id": i, "complexity": random.random()},
                }
            )

        # Check endocrine status periodically
        if i % 10 == 0:
            status = orchestrator.get_endocrine_status()
            print(f"Step {i} - Stress: {status['cognitive_state']['stress_level']:.2f}")
            print(f"  Stressed components: {status['stressed_components']}")

        await asyncio.sleep(0.1)

    # Simulate high stress by sending many tasks quickly
    print("\nSimulating stress burst...")
    for i in range(50):
        await orchestrator.process(
            {
                "type": "task",
                "component": "worker1",
                "data": {"id": f"stress_{i}", "complexity": 0.9},
            }
        )

    # Let the system adapt
    await asyncio.sleep(5)

    # Check final status
    final_status = orchestrator.get_endocrine_status()
    print("\nFinal hormone levels:")
    for hormone, level in final_status["hormone_levels"].items():
        print(f"  {hormone}: {level:.2f}")

    # Stop everything
    await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())
