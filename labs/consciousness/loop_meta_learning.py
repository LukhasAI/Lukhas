#!/usr/bin/env python3
"""
Meta-Learning Loop Controller
Manages the intentional Learning → Dream → Creativity → Memory cycle.
This is an INTENTIONAL circular dependency that creates emergent learning capabilities.
"""
# intentional_cycle: Learning → Dream → Creativity → Memory → Learning
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from creativity.core import CreativityEngine

# These imports form an intentional cycle for meta-learning
from learning.learning_gateway import LearningRequest, get_learning_gateway

from dream.engine import DreamEngine  # Will be renamed to dream.synthesizer
from memory.core import MemoryCore


@dataclass
class MetaLearningCycle:
    """Represents one cycle of the meta-learning loop"""

    cycle_id: str
    learning_input: dict[str, Any]
    dream_synthesis: Optional[dict[str, Any]] = None
    creative_output: Optional[dict[str, Any]] = None
    memory_consolidation: Optional[dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class MetaLearningLoop:
    """
    Orchestrates the meta-learning loop that enables the system to:
    1. Learn from experiences
    2. Dream/synthesize new possibilities
    3. Create novel solutions
    4. Consolidate into memory for future learning

    This creates a feedback loop where the system can learn from imagined experiences.
    """

    def __init__(self):
        # Initialize all components of the loop
        self.learning = get_learning_gateway()
        self.dream_engine = DreamEngine()
        self.creativity = CreativityEngine()
        self.memory = MemoryCore()

        # Track active cycles
        self.active_cycles: dict[str, MetaLearningCycle] = {}
        self._lock = asyncio.Lock()

    async def execute_cycle(
        self,
        agent_id: str,
        initial_data: dict[str, Any],
        cycle_params: Optional[dict[str, Any]] = None,
    ) -> MetaLearningCycle:
        """
        Execute one complete meta-learning cycle.

        Args:
            agent_id: ID of the agent undergoing meta-learning
            initial_data: Initial learning data to seed the cycle
            cycle_params: Optional parameters to control the cycle

        Returns:
            Completed MetaLearningCycle with all stages populated
        """
        cycle_id = f"{agent_id}_{datetime.now(timezone.utc).timestamp()}"
        cycle = MetaLearningCycle(cycle_id=cycle_id, learning_input=initial_data)

        async with self._lock:
            self.active_cycles[cycle_id] = cycle

        try:
            # Stage 1: Learning - Process initial data through learning system
            learning_request = LearningRequest(
                agent_id=agent_id,
                operation="meta_learn",
                data=initial_data,
                context={"cycle_type": "meta_learning"},
            )
            learning_result = await self.learning.process_learning_request(learning_request)

            # Stage 2: Dream - Synthesize new possibilities from learned patterns
            dream_seed = {
                "learning_output": learning_result.result,
                "meta_context": "exploratory_synthesis",
                "creativity_level": (cycle_params.get("creativity_level", 0.7) if cycle_params else 0.7),
            }
            cycle.dream_synthesis = await self.dream_engine.synthesize(agent_id, dream_seed)

            # Stage 3: Creativity - Generate novel outputs from dreams
            creative_input = {
                "dream_data": cycle.dream_synthesis,
                "learning_context": learning_result.result,
                "innovation_mode": (cycle_params.get("innovation_mode", "balanced") if cycle_params else "balanced"),
            }
            cycle.creative_output = await self.creativity.generate(agent_id, creative_input)

            # Stage 4: Memory - Consolidate entire cycle into memory
            memory_package = {
                "cycle_id": cycle_id,
                "learning": learning_result.result,
                "dream": cycle.dream_synthesis,
                "creativity": cycle.creative_output,
                "metadata": {
                    "cycle_type": "meta_learning",
                    "timestamp": cycle.timestamp.isoformat(),
                    "agent_id": agent_id,
                },
            }
            cycle.memory_consolidation = await self.memory.consolidate_meta_learning(memory_package)

            # The cycle completes and feeds back into learning for the next iteration
            # This creates the emergent capability to learn from imagined experiences

            return cycle

        finally:
            async with self._lock:
                self.active_cycles.pop(cycle_id, None)

    async def run_continuous_cycles(
        self, agent_id: str, num_cycles: int = 5, cycle_delay: float = 1.0
    ) -> list[MetaLearningCycle]:
        """
        Run multiple meta-learning cycles, each building on the previous.

        This creates a compounding effect where each cycle benefits from
        the consolidated memories of previous cycles.
        """
        cycles = []
        previous_output = None

        for i in range(num_cycles):
            # Use output from previous cycle as input to next
            if previous_output:
                initial_data = {
                    "previous_cycle": previous_output,
                    "cycle_number": i + 1,
                    "continuation": True,
                }
            else:
                initial_data = {"cycle_number": 1, "initialization": True}

            cycle = await self.execute_cycle(agent_id, initial_data)
            cycles.append(cycle)

            # Extract key insights for next cycle
            if cycle.memory_consolidation:
                previous_output = cycle.memory_consolidation.get("key_insights", {})

            # Brief pause between cycles
            if i < num_cycles - 1:
                await asyncio.sleep(cycle_delay)

        return cycles

    async def get_meta_learning_insights(self, agent_id: str) -> dict[str, Any]:
        """
        Extract insights from the meta-learning process.

        Returns aggregated insights from all completed cycles.
        """
        # Query memory for all meta-learning cycles
        cycles_data = await self.memory.query_meta_learning_history(agent_id)

        insights = {
            "total_cycles": len(cycles_data),
            "emergent_patterns": [],
            "creative_breakthroughs": [],
            "learning_efficiency": 0.0,
            "dream_coherence": 0.0,
        }

        # Analyze patterns across cycles
        for cycle in cycles_data:
            # Extract emergent patterns
            if "patterns" in cycle:
                insights["emergent_patterns"].extend(cycle["patterns"])

            # Identify creative breakthroughs
            if cycle.get("creativity", {}).get("breakthrough_score", 0) > 0.8:
                insights["creative_breakthroughs"].append(cycle["creativity"])

        # Calculate metrics
        if cycles_data:
            insights["learning_efficiency"] = sum(
                c.get("learning", {}).get("efficiency", 0) for c in cycles_data
            ) / len(cycles_data)

            insights["dream_coherence"] = sum(c.get("dream", {}).get("coherence", 0) for c in cycles_data) / len(
                cycles_data
            )

        return insights


# Singleton instance
_meta_learning_loop = None


def get_meta_learning_loop() -> MetaLearningLoop:
    """Get the singleton meta-learning loop instance."""
    global _meta_learning_loop
    if _meta_learning_loop is None:
        _meta_learning_loop = MetaLearningLoop()
    return _meta_learning_loop


# 🔁 Cross-layer: This module intentionally creates a learning cycle
# The cycle enables emergent meta-learning capabilities through
# imagination and synthesis, similar to how humans learn from
# mental simulations and creative exploration.

__all__ = ["MetaLearningCycle", "MetaLearningLoop", "get_meta_learning_loop"]
