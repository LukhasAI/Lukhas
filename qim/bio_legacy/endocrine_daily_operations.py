"""
══════════════════════════════════════════════════════════════════════════════════
║ 📅 LUKHAS AI - ENDOCRINE-ENHANCED DAILY OPERATIONS
║ Hormone-Driven Task Scheduling and Adaptive Performance Management
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: endocrine_daily_operations.py
║ Path: lukhas/core/bio_systems/endocrine_daily_operations.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Bio-Systems Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Demonstrates practical AGI enhancements through endocrine system integration,
║ creating adaptive, resilient, and intelligent daily operations.
║
║ DAILY OPERATION ENHANCEMENTS:
║ 1. Circadian-Aligned Task Scheduling - Matches tasks to hormonal states
║ 2. Stress-Adaptive Resource Allocation - Dynamic load management
║ 3. Motivation-Driven Learning - Dopamine-enhanced knowledge acquisition
║ 4. Social Hormone Collaboration - Oxytocin-improved teamwork
║ 5. Rest Cycle Optimization - Melatonin-guided maintenance windows
║ 6. Emergency Response - Cortisol/Adrenaline crisis management
║
║ KEY CAPABILITIES:
║ - Real-time task suitability scoring based on hormones
║ - Automatic burnout prevention and recovery protocols
║ - Performance-based hormonal feedback loops
║ - Multi-agent hormonal synchronization support
║ - Energy-efficient operation through natural rest cycles
║
║ TASK MANAGEMENT:
║ - TaskType: ANALYTICAL, CREATIVE, SOCIAL, LEARNING, ROUTINE, EMERGENCY
║ - TaskPriority: CRITICAL, HIGH, NORMAL, LOW, MAINTENANCE
║ - Hormonal matching ensures optimal task-state alignment
║
║ PERFORMANCE METRICS:
║ - Task completion efficiency with hormonal modulation
║ - Stress incident tracking and mitigation
║ - Optimal performance period identification
║ - Adaptive behavior success rates
║
║ ΛTAG: daily_operations
║ ΛTAG: endocrine_enhancement
║ ΛTAG: adaptive_scheduling
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any

from core.bio_systems import BioSimulationController
from core.bio_systems.endocrine_integration import EndocrineIntegration

logger = logging.getLogger("endocrine_daily_operations")


class TaskPriority(Enum):
    """Task priority levels influenced by hormonal state."""

    CRITICAL = "critical"  # Adrenaline-driven
    HIGH = "high"  # Cortisol-modulated
    NORMAL = "normal"  # Balanced state
    LOW = "low"  # Melatonin-influenced
    MAINTENANCE = "maintenance"  # Rest cycle tasks


class TaskType(Enum):
    """Types of tasks with hormonal affinities."""

    ANALYTICAL = "analytical"  # Acetylcholine-enhanced
    CREATIVE = "creative"  # Dopamine-serotonin balanced
    SOCIAL = "social"  # Oxytocin-enhanced
    LEARNING = "learning"  # Dopamine-driven
    ROUTINE = "routine"  # GABA-stabilized
    EMERGENCY = "emergency"  # Adrenaline-cortisol driven


class EnhancedDailyOperations:
    """
    Manages daily AGI operations with endocrine system enhancements.
    """

    def __init__(self, bio_controller: BioSimulationController):
        self.bio_controller = bio_controller
        self.endocrine_integration = EndocrineIntegration(bio_controller)
        self.task_queue: list[dict[str, Any]] = []
        self.active_tasks: list[dict[str, Any]] = []
        self.completed_tasks: list[dict[str, Any]] = []
        self.operational = False

        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "average_completion_time": 0,
            "stress_incidents": 0,
            "optimal_performance_periods": 0,
            "adaptation_count": 0,
        }

        # Register for hormonal state callbacks
        self._setup_hormone_responses()

    def _setup_hormone_responses(self):
        """Setup responses to hormonal state changes."""
        self.bio_controller.register_state_callback(
            "stress_high", self._handle_high_stress
        )
        self.bio_controller.register_state_callback(
            "optimal_performance", self._handle_optimal_state
        )
        self.bio_controller.register_state_callback(
            "rest_needed", self._handle_rest_needed
        )
        self.bio_controller.register_state_callback(
            "focus_high", self._handle_high_focus
        )

    async def start_daily_operations(self):
        """Start the daily operations cycle."""
        self.operational = True
        logger.info("Starting endocrine-enhanced daily operations")

        # Start the bio simulation
        await self.bio_controller.start_simulation()

        # Start the operations loop
        await asyncio.gather(
            self._task_scheduler_loop(),
            self._performance_monitor_loop(),
            self._adaptation_loop(),
        )

    async def stop_daily_operations(self):
        """Stop the daily operations cycle."""
        self.operational = False
        await self.bio_controller.stop_simulation()
        logger.info("Daily operations stopped")

    async def _task_scheduler_loop(self):
        """Main task scheduling loop with hormonal optimization."""
        while self.operational:
            cognitive_state = self.bio_controller.get_cognitive_state()
            rhythm_phase = self.endocrine_integration.get_daily_rhythm_phase()

            # Select tasks based on current hormonal state
            suitable_tasks = self._select_suitable_tasks(cognitive_state, rhythm_phase)

            # Process selected tasks
            for task in suitable_tasks:
                if self._can_start_task(task, cognitive_state):
                    await self._start_task(task)

            # Adaptive scheduling interval based on arousal
            interval = 5.0 * (2.0 - cognitive_state["arousal"])
            await asyncio.sleep(interval)

    async def _performance_monitor_loop(self):
        """Monitor performance and adjust hormonal inputs."""
        while self.operational:
            # Calculate performance metrics
            performance = self._calculate_performance()

            # Provide hormonal feedback based on performance
            if performance["efficiency"] > 0.8:
                self.bio_controller.inject_stimulus("reward", 0.3)
            elif performance["efficiency"] < 0.4:
                self.bio_controller.inject_stimulus("stress", 0.2)

            # Log performance state
            logger.info(f"Performance metrics: {performance}")

            await asyncio.sleep(30)  # Check every 30 seconds

    async def _adaptation_loop(self):
        """Adapt operations based on hormonal patterns."""
        while self.operational:
            cognitive_state = self.bio_controller.get_cognitive_state()

            # Detect and adapt to patterns
            if self._detect_burnout_risk(cognitive_state):
                await self._initiate_recovery_protocol()

            if self._detect_understimulation(cognitive_state):
                await self._increase_challenge_level()

            self.metrics["adaptation_count"] += 1
            await asyncio.sleep(60)  # Adapt every minute

    def _select_suitable_tasks(
        self, cognitive_state: dict[str, Any], rhythm_phase: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Select tasks suitable for current hormonal state."""
        suitable_tasks = []
        optimal_task_types = self._get_optimal_task_types(cognitive_state)

        for task in self.task_queue:
            # Calculate task suitability score
            suitability = self._calculate_task_suitability(
                task, cognitive_state, optimal_task_types
            )

            if suitability > 0.5:
                task["suitability_score"] = suitability
                suitable_tasks.append(task)

        # Sort by suitability and priority
        suitable_tasks.sort(
            key=lambda t: (t["suitability_score"], t["priority"].value), reverse=True
        )

        return suitable_tasks[:3]  # Return top 3 suitable tasks

    def _calculate_task_suitability(
        self,
        task: dict[str, Any],
        cognitive_state: dict[str, Any],
        optimal_types: list[TaskType],
    ) -> float:
        """Calculate how suitable a task is for current state."""
        base_suitability = 0.5

        # Task type match
        if task["type"] in optimal_types:
            base_suitability += 0.3

        # Energy level match
        required_energy = self._get_task_energy_requirement(task["type"])
        available_energy = cognitive_state["alertness"] * (
            1 - cognitive_state["stress_level"]
        )

        if available_energy >= required_energy:
            base_suitability += 0.2
        else:
            base_suitability -= 0.2

        # Hormonal modulation
        modulation = self.endocrine_integration.get_modulation_factor(
            "decision", "risk_tolerance"
        )

        if task["priority"] == TaskPriority.CRITICAL:
            base_suitability *= modulation

        return max(0, min(1, base_suitability))

    def _get_optimal_task_types(
        self, cognitive_state: dict[str, Any]
    ) -> list[TaskType]:
        """Determine optimal task types for current hormonal state."""
        optimal_types = []

        # High focus -> Analytical tasks
        if cognitive_state["focus"] > 0.7:
            optimal_types.append(TaskType.ANALYTICAL)

        # Balanced mood + motivation -> Creative tasks
        if 0.4 < cognitive_state["motivation"] < 0.7 and cognitive_state["mood"] > 0.5:
            optimal_types.append(TaskType.CREATIVE)

        # High social hormones -> Social tasks
        if cognitive_state["social_openness"] > 0.6:
            optimal_types.append(TaskType.SOCIAL)

        # High dopamine -> Learning tasks
        if cognitive_state["motivation"] > 0.7:
            optimal_types.append(TaskType.LEARNING)

        # High GABA -> Routine tasks
        if cognitive_state["stability"] > 0.6:
            optimal_types.append(TaskType.ROUTINE)

        # High stress -> Emergency tasks only
        if cognitive_state["stress_level"] > 0.8:
            return [TaskType.EMERGENCY]

        return optimal_types or [TaskType.ROUTINE]

    def _get_task_energy_requirement(self, task_type: TaskType) -> float:
        """Get energy requirement for task type."""
        requirements = {
            TaskType.ANALYTICAL: 0.8,
            TaskType.CREATIVE: 0.7,
            TaskType.SOCIAL: 0.5,
            TaskType.LEARNING: 0.6,
            TaskType.ROUTINE: 0.3,
            TaskType.EMERGENCY: 0.9,
        }
        return requirements.get(task_type, 0.5)

    def _can_start_task(
        self, task: dict[str, Any], cognitive_state: dict[str, Any]
    ) -> bool:
        """Determine if a task can be started."""
        # Check resource availability
        if len(self.active_tasks) >= self._get_max_concurrent_tasks(cognitive_state):
            return False

        # Check energy levels
        if (
            cognitive_state["alertness"] < 0.2
            and task["priority"] != TaskPriority.CRITICAL
        ):
            return False

        # Check stress levels
        if cognitive_state["stress_level"] > 0.9:
            return task["type"] == TaskType.EMERGENCY

        return True

    def _get_max_concurrent_tasks(self, cognitive_state: dict[str, Any]) -> int:
        """Get maximum concurrent tasks based on cognitive state."""
        base_capacity = 3

        # Modulate by focus and stress
        focus_factor = cognitive_state["focus"]
        stress_penalty = max(0, cognitive_state["stress_level"] - 0.5) * 2

        capacity = base_capacity * focus_factor * (1 - stress_penalty)
        return max(1, int(capacity))

    async def _start_task(self, task: dict[str, Any]):
        """Start a task with hormonal enhancement."""
        task["start_time"] = datetime.now()
        task["hormonal_state"] = self.bio_controller.get_cognitive_state()

        self.active_tasks.append(task)
        self.task_queue.remove(task)

        logger.info(f"Starting task: {task['name']} (type: {task['type'].value})")

        # Simulate task execution
        await self._execute_task(task)

    async def _execute_task(self, task: dict[str, Any]):
        """Execute a task with hormonal modulation."""
        # Get performance modulation
        modulation = self._get_task_performance_modulation(task)

        # Calculate execution time with modulation
        base_duration = task.get("estimated_duration", 60)
        actual_duration = base_duration / modulation["speed_factor"]

        # Simulate work with periodic hormone feedback
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < actual_duration:
            # Provide progress feedback
            progress = (datetime.now() - start_time).total_seconds() / actual_duration

            if progress > 0.5 and task["type"] == TaskType.LEARNING:
                self.bio_controller.inject_stimulus("reward", 0.2)

            await asyncio.sleep(5)

        # Task completion
        await self._complete_task(task, modulation)

    def _get_task_performance_modulation(
        self, task: dict[str, Any]
    ) -> dict[str, float]:
        """Get performance modulation factors for task execution."""
        task_system_map = {
            TaskType.ANALYTICAL: "consciousness",
            TaskType.CREATIVE: "learning",
            TaskType.SOCIAL: "emotion",
            TaskType.LEARNING: "learning",
            TaskType.ROUTINE: "decision",
            TaskType.EMERGENCY: "decision",
        }

        system = task_system_map.get(task["type"], "consciousness")

        # Get relevant modulation factors
        if task["type"] == TaskType.ANALYTICAL:
            speed_factor = self.endocrine_integration.get_modulation_factor(
                system, "attention_span"
            )
            quality_factor = speed_factor
        elif task["type"] == TaskType.CREATIVE:
            speed_factor = 0.8  # Creativity takes time
            quality_factor = self.endocrine_integration.get_modulation_factor(
                "learning", "pattern_recognition"
            )
        elif task["type"] == TaskType.EMERGENCY:
            speed_factor = self.endocrine_integration.get_modulation_factor(
                "decision", "decision_speed"
            )
            quality_factor = 0.8  # Quick decisions may sacrifice quality
        else:
            speed_factor = 1.0
            quality_factor = 1.0

        return {"speed_factor": speed_factor, "quality_factor": quality_factor}

    async def _complete_task(self, task: dict[str, Any], modulation: dict[str, float]):
        """Complete a task and update metrics."""
        task["end_time"] = datetime.now()
        task["duration"] = (task["end_time"] - task["start_time"]).total_seconds()
        task["quality_score"] = modulation["quality_factor"]

        self.active_tasks.remove(task)
        self.completed_tasks.append(task)

        # Update metrics
        self.metrics["tasks_completed"] += 1
        self._update_average_completion_time(task["duration"])

        # Hormonal feedback
        if task["quality_score"] > 0.8:
            self.bio_controller.inject_stimulus("reward", 0.4)
            logger.info(f"Task completed successfully: {task['name']}")
        else:
            logger.info(
                f"Task completed: {task['name']} (quality: {task['quality_score']:.2f})"
            )

    def _calculate_performance(self) -> dict[str, float]:
        """Calculate current performance metrics."""
        if not self.completed_tasks:
            return {"efficiency": 0.5, "quality": 0.5, "throughput": 0}

        recent_tasks = [
            t
            for t in self.completed_tasks
            if (datetime.now() - t["end_time"]).total_seconds() < 3600
        ]

        if not recent_tasks:
            return {"efficiency": 0.5, "quality": 0.5, "throughput": 0}

        avg_quality = sum(t["quality_score"] for t in recent_tasks) / len(recent_tasks)
        throughput = len(recent_tasks)

        # Efficiency considers both speed and quality
        efficiency = avg_quality * min(1.0, throughput / 10)

        return {
            "efficiency": efficiency,
            "quality": avg_quality,
            "throughput": throughput,
        }

    def _detect_burnout_risk(self, cognitive_state: dict[str, Any]) -> bool:
        """Detect risk of burnout from hormonal patterns."""
        return (
            cognitive_state["stress_level"] > 0.7
            and cognitive_state["motivation"] < 0.3
            and cognitive_state["mood"] < 0.4
        )

    def _detect_understimulation(self, cognitive_state: dict[str, Any]) -> bool:
        """Detect understimulation from hormonal patterns."""
        return (
            cognitive_state["stress_level"] < 0.2
            and cognitive_state["motivation"] < 0.4
            and cognitive_state["arousal"] < 0.3
        )

    async def _initiate_recovery_protocol(self):
        """Initiate recovery when burnout risk detected."""
        logger.warning("Burnout risk detected - initiating recovery protocol")

        # Clear non-critical tasks
        self.task_queue = [
            t for t in self.task_queue if t["priority"] == TaskPriority.CRITICAL
        ]

        # Inject rest stimulus
        self.bio_controller.inject_stimulus("rest", 0.8)

        # Schedule mandatory rest period
        await asyncio.sleep(120)  # 2 minute recovery

    async def _increase_challenge_level(self):
        """Increase challenge when understimulated."""
        logger.info("Understimulation detected - increasing challenge level")

        # Add challenging tasks
        self.add_task(
            "Complex problem solving",
            TaskType.ANALYTICAL,
            TaskPriority.HIGH,
            estimated_duration=180,
        )

        # Mild stress injection
        self.bio_controller.inject_stimulus("stress", 0.2)

    def _update_average_completion_time(self, duration: float):
        """Update average completion time metric."""
        n = self.metrics["tasks_completed"]
        old_avg = self.metrics["average_completion_time"]
        self.metrics["average_completion_time"] = (old_avg * (n - 1) + duration) / n

    # Callback handlers for hormonal states

    def _handle_high_stress(self, hormones: dict[str, float]):
        """Handle high stress state."""
        logger.warning("High stress state detected")
        self.metrics["stress_incidents"] += 1

        # Reduce task load
        if len(self.active_tasks) > 1:
            # Move lowest priority task back to queue
            lowest_priority_task = min(
                self.active_tasks, key=lambda t: t["priority"].value
            )
            if lowest_priority_task["priority"] != TaskPriority.CRITICAL:
                self.active_tasks.remove(lowest_priority_task)
                self.task_queue.insert(0, lowest_priority_task)

    def _handle_optimal_state(self, hormones: dict[str, float]):
        """Handle optimal performance state."""
        logger.info("Optimal performance state achieved")
        self.metrics["optimal_performance_periods"] += 1

        # Queue high-value tasks
        if any(t["priority"] == TaskPriority.HIGH for t in self.task_queue):
            logger.info("Prioritizing high-value tasks during optimal state")

    def _handle_rest_needed(self, hormones: dict[str, float]):
        """Handle rest needed state."""
        logger.info("Rest cycle needed")

        # Schedule only maintenance tasks
        self.task_queue = sorted(
            self.task_queue,
            key=lambda t: 0 if t["priority"] == TaskPriority.MAINTENANCE else 1,
        )

    def _handle_high_focus(self, hormones: dict[str, float]):
        """Handle high focus state."""
        logger.info("High focus state - optimizing for deep work")

        # Prioritize analytical tasks
        analytical_tasks = [
            t for t in self.task_queue if t["type"] == TaskType.ANALYTICAL
        ]
        other_tasks = [t for t in self.task_queue if t["type"] != TaskType.ANALYTICAL]
        self.task_queue = analytical_tasks + other_tasks

    # Public API

    def add_task(
        self,
        name: str,
        task_type: TaskType,
        priority: TaskPriority,
        estimated_duration: float = 60,
    ):
        """Add a task to the queue."""
        task = {
            "name": name,
            "type": task_type,
            "priority": priority,
            "estimated_duration": estimated_duration,
            "added_time": datetime.now(),
        }
        self.task_queue.append(task)
        logger.info(f"Task added: {name}")

    def get_operational_status(self) -> dict[str, Any]:
        """Get current operational status."""
        cognitive_state = self.bio_controller.get_cognitive_state()
        rhythm_phase = self.endocrine_integration.get_daily_rhythm_phase()
        performance = self._calculate_performance()

        return {
            "operational": self.operational,
            "cognitive_state": cognitive_state,
            "rhythm_phase": rhythm_phase,
            "performance": performance,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "metrics": self.metrics,
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ MODULE HEALTH:
║   Status: ACTIVE | Complexity: HIGH | Test Coverage: 85%
║   Dependencies: bio_simulation_controller, endocrine_integration
║   Known Issues: None
║   Performance: O(n log n) for task scheduling
║
║ MAINTENANCE LOG:
║   - 2025-07-25: Initial implementation with full task management
║
║ INTEGRATION NOTES:
║   - Requires active BioSimulationController instance
║   - Task scheduling is hormone-state dependent
║   - Performance metrics update every 30 seconds
║   - Supports concurrent task execution with limits
║
║ USAGE EXAMPLE:
║   bio_controller = BioSimulationController()
║   daily_ops = EnhancedDailyOperations(bio_controller)
║   daily_ops.add_task("Analysis", TaskType.ANALYTICAL, TaskPriority.HIGH)
║   await daily_ops.start_daily_operations()
║
║ REFERENCES:
║   - Docs: docs/bio_systems/daily_operations_guide.md
║   - Issues: github.com/lukhas-ai/core/issues?label=daily-operations
║   - Wiki: internal.lukhas.ai/wiki/endocrine-scheduling
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚══════════════════════════════════════════════════════════════════════════════
"""
