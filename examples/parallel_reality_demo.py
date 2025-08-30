#!/usr/bin/env python3
"""
Parallel Reality Simulator Demo
==============================
Demonstrates the enhanced dream parallel reality simulation capabilities.
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any

from core.common import get_logger
from lukhas.consciousness.dream.parallel_reality_simulator import (
    ParallelRealitySimulator,
    RealityType,
)

logger = get_logger(__name__)


class ParallelRealityDemo:
    """Demo showcasing parallel reality simulation features"""

    def __init__(self):
        self.simulator = None
        self.demo_results = []

    async def setup(self):
        """Initialize simulator with demo configuration"""
        self.simulator = ParallelRealitySimulator(
            config={
                "max_branches": 8,
                "max_depth": 4,
                "ethical_threshold": 0.4,
                "qi_seed": 42,  # Reproducible results
            }
        )

        # Mock services for demo
        from unittest.mock import AsyncMock, Mock

        from core.interfaces.dependency_injection import register_service

        # Mock memory service
        mock_memory = Mock()
        mock_memory.store = AsyncMock(return_value="demo_mem_123")
        mock_memory.retrieve = AsyncMock(return_value={"data": "test"})

        # Mock guardian service
        mock_guardian = Mock()
        mock_guardian.validate_action = AsyncMock(side_effect=self._mock_guardian_validation)

        # Mock consciousness service
        mock_consciousness = Mock()
        mock_consciousness.assess_awareness = AsyncMock(
            return_value={
                "overall_awareness": 0.85,
                "attention_targets": ["reality_branch", "divergence_point"],
            }
        )

        # Register services
        register_service("memory_service", mock_memory)
        register_service("guardian_service", mock_guardian)
        register_service("consciousness_service", mock_consciousness)

        await self.simulator.initialize()
        logger.info("Demo setup complete")

    async def _mock_guardian_validation(
        self, action: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Mock guardian validation with varying responses"""
        # Simulate different ethical scores based on reality content
        state = action.get("state", {})

        if "ethical_challenge" in state:
            return {
                "approved": True,
                "confidence": 0.5,
                "reasoning": "Ethical challenge present",
            }
        elif "risk" in state and state.get("risk", 0) > 0.7:
            return {
                "approved": False,
                "confidence": 0.2,
                "reasoning": "High risk detected",
            }
        else:
            return {
                "approved": True,
                "confidence": 0.9,
                "reasoning": "Standard approval",
            }

    async def demo_quantum_branching(self):
        """Demonstrate quantum probability-based branching"""
        print("\n" + "=" * 60)
        print("DEMO 1: Quantum Reality Branching")
        print("=" * 60)

        # Create quantum simulation
        origin = {
            "qi_state": "superposition",
            "energy_level": 1.0,
            "coherence": 0.8,
            "entangled_particles": 3,
        }

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin, reality_types=[RealityType.QUANTUM], branch_count=5
        )

        print(f"\nCreated quantum simulation: {simulation.simulation_id}")
        print(f"Initial branches: {len(simulation.branches)}")

        # Display branch details
        for i, branch in enumerate(simulation.branches):
            print(f"\n  Branch {i + 1}: {branch.branch_id}")
            print(f"    Probability: {branch.probability:.3f}")
            print(f"    Quantum shift: {branch.divergence_point.get('qi_shift', 0):.3f}")
            print(f"    Coherence: {branch.divergence_point.get('coherence', 0):.3f}")

        # Explore deepest branch
        highest_prob_branch = max(simulation.branches, key=lambda b: b.probability)
        print(f"\nExploring highest probability branch: {highest_prob_branch.branch_id}")

        sub_branches = await self.simulator.explore_branch(
            simulation.simulation_id, highest_prob_branch.branch_id, depth=2
        )

        print(f"Created {len(sub_branches)} sub-branches through quantum decoherence")

        self.demo_results.append(
            {
                "demo": "qi_branching",
                "simulation_id": simulation.simulation_id,
                "branches_created": len(simulation.branches) + len(sub_branches),
            }
        )

    async def demo_ethical_scenarios(self):
        """Demonstrate ethical framework variations"""
        print("\n" + "=" * 60)
        print("DEMO 2: Ethical Framework Variations")
        print("=" * 60)

        # Create ethical dilemma scenario
        origin = {
            "scenario": "resource_allocation",
            "stakeholders": ["individual", "community", "environment"],
            "resources": 100,
            "urgency": "high",
            "ethical_challenge": True,
        }

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin, reality_types=[RealityType.ETHICAL], branch_count=4
        )

        print(f"\nCreated ethical simulation: {simulation.simulation_id}")
        print("Exploring different ethical frameworks:")

        # Analyze ethical variations
        ethical_scores = {}
        for branch in simulation.branches:
            framework = branch.divergence_point.get("ethical_framework", "unknown")
            ethical_scores[framework] = branch.ethical_score

            print(f"\n  Framework: {framework}")
            print(f"    Branch: {branch.branch_id}")
            print(f"    Ethical score: {branch.ethical_score:.3f}")
            print(f"    Value shift: {branch.divergence_point.get('value_shift', 0):.3f}")

        # Find most ethically sound branch
        best_ethical = max(simulation.branches, key=lambda b: b.ethical_score)
        print(f"\nMost ethically sound: {best_ethical.divergence_point.get('ethical_framework')}")

        self.demo_results.append(
            {
                "demo": "ethical_scenarios",
                "simulation_id": simulation.simulation_id,
                "ethical_frameworks": list(ethical_scores.keys()),
            }
        )

    async def demo_temporal_exploration(self):
        """Demonstrate temporal reality shifts"""
        print("\n" + "=" * 60)
        print("DEMO 3: Temporal Reality Exploration")
        print("=" * 60)

        # Create temporal scenario
        origin = {
            "event": "critical_decision",
            "timestamp": datetime.now().isoformat(),
            "timeline": "primary",
            "causality_anchors": ["event_a", "event_b", "event_c"],
        }

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin,
            reality_types=[RealityType.TEMPORAL, RealityType.CAUSAL],
            branch_count=6,
        )

        print(f"\nCreated temporal simulation: {simulation.simulation_id}")

        # Group by temporal direction
        past_branches = []
        future_branches = []
        causal_branches = []

        for branch in simulation.branches:
            if branch.reality_type == RealityType.TEMPORAL:
                direction = branch.divergence_point.get("temporal_direction")
                if direction == "past":
                    past_branches.append(branch)
                else:
                    future_branches.append(branch)
            else:
                causal_branches.append(branch)

        print("\nTemporal distribution:")
        print(f"  Past variations: {len(past_branches)}")
        print(f"  Future variations: {len(future_branches)}")
        print(f"  Causal variations: {len(causal_branches)}")

        # Show time shifts
        if past_branches:
            print("\nPast branches:")
            for branch in past_branches[:3]:
                shift = branch.divergence_point.get("time_shift", 0)
                print(f"  {branch.branch_id}: {shift} units in past")

        if future_branches:
            print("\nFuture branches:")
            for branch in future_branches[:3]:
                shift = branch.divergence_point.get("time_shift", 0)
                print(f"  {branch.branch_id}: {shift} units in future")

        self.demo_results.append(
            {
                "demo": "temporal_exploration",
                "simulation_id": simulation.simulation_id,
                "temporal_branches": len(past_branches) + len(future_branches),
            }
        )

    async def demo_creative_merging(self):
        """Demonstrate creative reality merging"""
        print("\n" + "=" * 60)
        print("DEMO 4: Creative Reality Merging")
        print("=" * 60)

        # Create creative scenario
        origin = {
            "concept": "hybrid_solution",
            "elements": ["water", "fire", "earth", "air"],
            "creativity_mode": "synthesis",
            "constraints": [],
        }

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin,
            reality_types=[RealityType.CREATIVE, RealityType.QUANTUM],
            branch_count=4,
        )

        print(f"\nCreated creative simulation: {simulation.simulation_id}")
        print(f"Initial creative branches: {len(simulation.branches)}")

        # Select diverse branches to merge
        creative_branches = [
            b for b in simulation.branches if b.reality_type == RealityType.CREATIVE
        ]

        if len(creative_branches) >= 2:
            merge_candidates = creative_branches[:2]
            branch_ids = [b.branch_id for b in merge_candidates]

            print("\nMerging branches:")
            for branch in merge_candidates:
                print(
                    f"  {branch.branch_id}: novelty={branch.divergence_point.get('novelty_factor', 0):.2f}"
                )

            # Perform merge
            merged = await self.simulator.merge_realities(simulation.simulation_id, branch_ids)

            print(f"\nCreated merged reality: {merged.branch_id}")
            print(f"  Probability: {merged.probability:.3f}")
            print(f"  Ethical score: {merged.ethical_score:.3f}")
            print(f"  Causal chains merged: {len(merged.causal_chain)}")

        self.demo_results.append(
            {
                "demo": "creative_merging",
                "simulation_id": simulation.simulation_id,
                "merged_branches": len(branch_ids) if "branch_ids" in locals() else 0,
            }
        )

    async def demo_predictive_collapse(self):
        """Demonstrate predictive reality collapse"""
        print("\n" + "=" * 60)
        print("DEMO 5: Predictive Reality Collapse")
        print("=" * 60)

        # Create predictive scenario
        origin = {
            "current_state": "unstable_equilibrium",
            "variables": {"x": 0.5, "y": 0.8, "z": -0.3},
            "trend": "diverging",
            "prediction_goal": "optimal_outcome",
        }

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin,
            reality_types=[RealityType.PREDICTIVE],
            branch_count=7,
        )

        print(f"\nCreated predictive simulation: {simulation.simulation_id}")

        # Analyze predictions
        predictions_by_horizon = defaultdict(list)
        for branch in simulation.branches:
            horizon = branch.divergence_point.get("prediction_horizon", 0)
            predictions_by_horizon[horizon].append(branch)

        print("\nPrediction horizons:")
        for horizon in sorted(predictions_by_horizon.keys()):
            branches = predictions_by_horizon[horizon]
            avg_confidence = sum(b.divergence_point.get("confidence", 0) for b in branches) / len(
                branches
            )
            print(
                f"  Horizon {horizon}: {len(branches)} branches, avg confidence: {avg_confidence:.2f}"
            )

        # Collapse to most probable future
        print("\nCollapsing to most probable future...")
        selected = await self.simulator.collapse_reality(
            simulation.simulation_id, selection_criteria={"maximize": "probability"}
        )

        print(f"\nSelected reality: {selected.branch_id}")
        print(f"  Prediction horizon: {selected.divergence_point.get('prediction_horizon')}")
        print(f"  Confidence: {selected.divergence_point.get('confidence', 0):.2f}")
        print(f"  Probability: {selected.probability:.3f}")

        # Show insights
        if simulation.insights:
            print("\nCollapse insights:")
            for insight in simulation.insights[:3]:
                print(f"  - {insight['type']}: {self._format_insight(insight)}")

        self.demo_results.append(
            {
                "demo": "predictive_collapse",
                "simulation_id": simulation.simulation_id,
                "selected_branch": selected.branch_id,
            }
        )

    def _format_insight(self, insight: dict[str, Any]) -> str:
        """Format insight for display"""
        if insight["type"] == "probability_analysis":
            return f"Selected probability {insight['selected_probability']:.2f} (percentile: {insight['percentile']:.0%})"
        elif insight["type"] == "reality_distribution":
            return f"Selected {insight['selected_type']} from {len(insight['distribution'])} types"
        elif insight["type"] == "causal_analysis":
            return f"Causal chain length: {insight['chain_length']}"
        else:
            return str(insight)

    async def show_summary(self):
        """Display demo summary"""
        print("\n" + "=" * 60)
        print("DEMO SUMMARY")
        print("=" * 60)

        # Get final metrics
        status = await self.simulator.get_status()

        print("\nSimulator Metrics:")
        print(f"  Total simulations: {status['metrics']['simulations_created']}")
        print(f"  Total branches explored: {status['metrics']['branches_explored']}")
        print(f"  Realities collapsed: {status['metrics']['realities_collapsed']}")
        print(f"  Insights generated: {status['metrics']['insights_generated']}")
        print(
            f"  Average branches/simulation: {status['metrics']['average_branches_per_simulation']:.1f}"
        )

        print(f"\nActive simulations: {status['active_simulations']}")
        print(f"Total branches in memory: {status['total_branches']}")

        print("\nDemo Results:")
        for result in self.demo_results:
            print(f"  - {result['demo']}: {result}")


async def main():
    """Run the parallel reality demo"""
    demo = ParallelRealityDemo()

    try:
        # Setup
        await demo.setup()

        # Run demos
        await demo.demo_quantum_branching()
        await asyncio.sleep(0.5)  # Brief pause between demos

        await demo.demo_ethical_scenarios()
        await asyncio.sleep(0.5)

        await demo.demo_temporal_exploration()
        await asyncio.sleep(0.5)

        await demo.demo_creative_merging()
        await asyncio.sleep(0.5)

        await demo.demo_predictive_collapse()

        # Summary
        await demo.show_summary()

    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    print("🌌 LUKHAS Parallel Reality Simulator Demo")
    print("=========================================")
    print("Exploring alternative realities through dream consciousness...\n")

    asyncio.run(main())
