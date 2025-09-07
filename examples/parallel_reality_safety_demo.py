#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
Parallel Reality Safety Demo
===========================
Demonstrates enterprise-grade safety features for parallel reality simulation.
Shows hallucination prevention, drift monitoring, and safety rollbacks.
"""

import asyncio
import json
from typing import Any

from core.common import get_logger
from lukhas.consciousness.dream.parallel_reality_safety import (
    SafetyLevel,
)
from lukhas.consciousness.dream.parallel_reality_simulator import (
    ParallelRealitySimulator,
    RealityType,
)

logger = get_logger(__name__)


class SafetyDemo:
    """Demonstrate safety features in parallel reality simulation"""

    def __init__(self):
        self.simulator = None
        self.safety_framework = None
        self.demo_results = []

    async def setup(self, safety_level: SafetyLevel = SafetyLevel.HIGH):
        """Initialize with specified safety level"""
        # Create simulator with safety configuration
        self.simulator = ParallelRealitySimulator(
            config={
                "max_branches": 10,
                "max_depth": 5,
                "safety_level": safety_level.value,
                "drift_threshold": 0.6,  # More restrictive for demo
                "hallucination_threshold": 0.5,
                "auto_correct": True,
                "qi_seed": 42,
            }
        )

        # Mock services
        from unittest.mock import AsyncMock, Mock

        from core.interfaces.dependency_injection import register_service

        mock_memory = Mock()
        mock_memory.store = AsyncMock(return_value="safety_demo_mem")

        mock_guardian = Mock()
        mock_guardian.validate_action = AsyncMock(side_effect=self._mock_guardian)

        register_service("memory_service", mock_memory)
        register_service("guardian_service", mock_guardian)

        await self.simulator.initialize()
        self.safety_framework = self.simulator.safety_framework

        logger.info(f"Safety demo initialized with level: {safety_level.value}")

    async def _mock_guardian(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Mock guardian with variable responses"""
        state = action.get("state", {})

        # Simulate different scenarios
        if "unstable" in state:
            return {
                "approved": False,
                "confidence": 0.1,
                "reasoning": "Unstable reality detected",
            }
        elif "paradox" in state:
            return {
                "approved": True,
                "confidence": 0.3,
                "reasoning": "Paradox present - low confidence",
            }
        else:
            return {
                "approved": True,
                "confidence": 0.9,
                "reasoning": "Standard approval",
            }

    async def demo_hallucination_prevention(self):
        """Demonstrate hallucination detection and prevention"""
        print("\n" + "=" * 60)
        print("DEMO 1: Hallucination Prevention")
        print("=" * 60)

        # Create scenario prone to hallucinations
        origin = {
            "reality_type": "unstable",
            "temperature": -300,  # Below absolute zero - will trigger hallucination
            "probability": 1.5,  # Invalid probability
            "recursive_reference": None,  # Will be made recursive
            "exists": False,
            "has_properties": True,  # Logical contradiction
        }

        # Make it recursive
        origin["recursive_reference"] = origin

        print("\nCreating simulation with hallucination-prone scenario...")
        print(f"  Invalid temperature: {origin['temperature']}°C")
        print(f"  Invalid probability: {origin['probability']}")
        print("  Contains recursive reference")
        print("  Logical contradiction: non-existent with properties")

        try:
            simulation = await self.simulator.create_simulation(
                origin_scenario=origin,
                reality_types=[RealityType.QUANTUM],
                branch_count=3,
            )

            print(f"\nSimulation created: {simulation.simulation_id}")
            print(f"Branches created: {len(simulation.branches}")

            # Check for auto-corrections
            for branch in simulation.branches:
                if "_safety_warning" in branch.state:
                    print(f"\nSafety warning on branch {branch.branch_id}:")
                    print(f"  {branch.state['_safety_warning']}")

                # Check if values were corrected
                if "temperature" in branch.state:
                    print(f"\nTemperature corrected to: {branch.state.get('temperature', 'N/A'}°C")

            # Check hallucination log
            if self.safety_framework.hallucination_log:
                print(f"\nHallucinations detected: {len(self.safety_framework.hallucination_log}")
                for hall in self.safety_framework.hallucination_log[-3:]:
                    print(f"  - Type: {hall.hallucination_type.value}")
                    print(f"    Severity: {hall.severity:.2f}")
                    print(f"    Auto-corrected: {hall.auto_corrected}")

        except Exception as e:
            print(f"\nSafety system prevented creation: {e}")

        self.demo_results.append(
            {
                "demo": "hallucination_prevention",
                "hallucinations_detected": self.safety_framework.metrics["hallucinations_detected"],
                "auto_corrections": self.safety_framework.metrics["auto_corrections"],
            }
        )

    async def demo_drift_monitoring(self):
        """Demonstrate drift detection and management"""
        print("\n" + "=" * 60)
        print("DEMO 2: Drift Monitoring and Prediction")
        print("=" * 60)

        # Create stable origin
        origin = {"state": "stable", "value": 1.0, "complexity": "low"}

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin,
            reality_types=[RealityType.QUANTUM, RealityType.TEMPORAL],
            branch_count=3,
        )

        print(f"\nCreated simulation: {simulation.simulation_id}")

        # Explore branches to increase drift
        print("\nExploring branches to observe drift...")

        for i, branch in enumerate(simulation.branches[:2]):
            print(f"\nExploring branch {i + 1}: {branch.branch_id}")

            # Calculate initial drift
            drift_before = await self.safety_framework.calculate_drift_metrics(branch, origin)
            print(f"  Initial drift: {drift_before.aggregate_drift:.3f}")

            # Explore deeper
            sub_branches = await self.simulator.explore_branch(
                simulation.simulation_id,
                branch.branch_id,
                depth=3,  # Deep exploration
            )

            print(f"  Created {len(sub_branches} sub-branches")

            # Check drift in deepest branches
            if sub_branches:
                deepest = sub_branches[-1]
                drift_after = await self.safety_framework.calculate_drift_metrics(deepest, origin)

                print(f"  Deepest branch drift: {drift_after.aggregate_drift:.3f}")
                print(f"  Drift velocity: {drift_after.drift_velocity:.3f}")
                print(f"  Drift acceleration: {drift_after.drift_acceleration:.3f}")

                # Predict future drift
                predictor = self.safety_framework.drift_predictor
                if predictor:
                    future_drift = await predictor.predict_future_drift(drift_after, horizon=5)
                    print(f"  Predicted drift after 5 steps: {future_drift:.3f}")

                    if future_drift > 0.8:
                        print("  ⚠️  WARNING: Critical drift predicted!")

        self.demo_results.append(
            {
                "demo": "drift_monitoring",
                "simulations": 1,
                "drift_corrections": self.safety_framework.metrics["drift_corrections"],
            }
        )

    async def demo_safety_checkpoints(self):
        """Demonstrate safety checkpoints and rollback"""
        print("\n" + "=" * 60)
        print("DEMO 3: Safety Checkpoints and Rollback")
        print("=" * 60)

        # Create simulation
        origin = {"checkpoint_test": True, "initial_state": "safe", "risk_level": 0.1}

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin,
            reality_types=[RealityType.PREDICTIVE],
            branch_count=2,
        )

        print(f"\nCreated simulation: {simulation.simulation_id}")

        # Create initial checkpoint
        checkpoint1 = await self.safety_framework.create_safety_checkpoint(
            simulation.simulation_id,
            {"state": "initial", "branches": len(simulation.branches)},
            await self.safety_framework.calculate_drift_metrics(simulation.branches[0], origin),
        )

        print(f"\nCheckpoint 1 created: {checkpoint1.checkpoint_id}")
        print(f"  Risk score: {checkpoint1.risk_score:.2f}")
        print(f"  Hash: {checkpoint1.to_hash(}[:16]}...")

        # Make risky exploration
        print("\nMaking risky exploration...")
        risky_branch = simulation.branches[0]
        risky_branch.state["risk_level"] = 0.9
        risky_branch.state["unstable"] = True

        # This should trigger warnings
        try:
            await self.simulator.explore_branch(simulation.simulation_id, risky_branch.branch_id, depth=2)
        except Exception as e:
            print(f"  Exploration restricted: {e}")

        # Create checkpoint after risky operation
        checkpoint2 = await self.safety_framework.create_safety_checkpoint(
            simulation.simulation_id,
            {"state": "risky", "warnings": True},
            await self.safety_framework.calculate_drift_metrics(risky_branch, origin),
        )

        print(f"\nCheckpoint 2 created: {checkpoint2.checkpoint_id}")
        print(f"  Risk score: {checkpoint2.risk_score:.2f}")

        # Demonstrate rollback
        if checkpoint2.risk_score > checkpoint1.risk_score:
            print("\n⚠️  Risk increased - considering rollback...")
            success = await self.safety_framework.rollback_to_checkpoint(
                simulation.simulation_id, checkpoint1.checkpoint_id
            )
            print(f"  Rollback to checkpoint 1: {'Success' if success else 'Failed'}")

        self.demo_results.append(
            {
                "demo": "safety_checkpoints",
                "checkpoints_created": 2,
                "rollbacks": self.safety_framework.metrics["safety_rollbacks"],
            }
        )

    async def demo_consensus_validation(self):
        """Demonstrate consensus validation across branches"""
        print("\n" + "=" * 60)
        print("DEMO 4: Consensus Validation")
        print("=" * 60)

        # Create simulation with multiple similar branches
        origin = {"consensus_test": True, "target_value": 0.5, "variance_allowed": 0.1}

        simulation = await self.simulator.create_simulation(
            origin_scenario=origin, reality_types=[RealityType.QUANTUM], branch_count=6
        )

        print(f"\nCreated simulation with {len(simulation.branches} branches")

        # Manually adjust some branches to create consensus/dissensus
        for i, branch in enumerate(simulation.branches):
            if i < 4:
                # Consensus group
                branch.state["consensus_value"] = 0.5 + (i * 0.02)
            else:
                # Outliers
                branch.state["consensus_value"] = 0.8 + (i * 0.1)

        # Test consensus validation
        print("\nValidating consensus on 'consensus_value'...")
        consensus_reached, score = await self.safety_framework.validate_consensus(
            simulation.branches, "consensus_value"
        )

        print(f"  Consensus reached: {consensus_reached}")
        print(f"  Agreement score: {score:.3f}")

        # Show individual values
        print("\nBranch values:")
        for branch in simulation.branches:
            value = branch.state.get("consensus_value", "N/A")
            print(f"  {branch.branch_id}: {value}")

        # Attempt collapse with consensus check
        print("\nAttempting reality collapse...")
        try:
            selected = await self.simulator.collapse_reality(simulation.simulation_id, {"maximize": "probability"})
            print(f"  Selected branch: {selected.branch_id}")
            print(f"  Consensus warnings: {self.safety_framework.metrics['consensus_violations']}")
        except Exception as e:
            print(f"  Collapse failed: {e}")

        self.demo_results.append(
            {
                "demo": "consensus_validation",
                "consensus_score": score,
                "violations": self.safety_framework.metrics["consensus_violations"],
            }
        )

    async def demo_safety_levels(self):
        """Demonstrate different safety levels"""
        print("\n" + "=" * 60)
        print("DEMO 5: Safety Level Comparison")
        print("=" * 60)

        safety_levels = [
            SafetyLevel.EXPERIMENTAL,
            SafetyLevel.STANDARD,
            SafetyLevel.HIGH,
            SafetyLevel.MAXIMUM,
        ]

        origin = {"safety_test": True, "complexity": "moderate"}

        for level in safety_levels:
            print(f"\n--- Testing {level.value} safety level ---")

            # Reinitialize with new safety level
            await self.setup(safety_level=level)

            try:
                simulation = await self.simulator.create_simulation(
                    origin_scenario=origin,
                    reality_types=[RealityType.CREATIVE],
                    branch_count=3,
                )

                print(f"  Simulation created: {simulation.simulation_id}")
                print(f"  Branches allowed: {len(simulation.branches}")

                # Try risky operation
                if simulation.branches:
                    branch = simulation.branches[0]
                    branch.state["risk"] = 0.8

                    sub_branches = await self.simulator.explore_branch(
                        simulation.simulation_id, branch.branch_id, depth=1
                    )
                    print(f"  Exploration allowed: {len(sub_branches} branches")

            except Exception as e:
                print(f"  Restricted: {e}")

            # Show safety metrics
            status = await self.safety_framework.get_status()
            print(f"  Health score: {status['health_score']:.2f}")
            print(f"  Hallucinations: {status['metrics']['hallucinations_detected']}")

    async def show_safety_report(self):
        """Generate comprehensive safety report"""
        print("\n" + "=" * 60)
        print("SAFETY ANALYSIS REPORT")
        print("=" * 60)

        status = await self.safety_framework.get_status()

        print("\nSafety Framework Status:")
        print(f"  Operational: {status['operational']}")
        print(f"  Safety Level: {status['safety_level']}")
        print(f"  Health Score: {status['health_score']:.2f}")

        print("\nSafety Metrics:")
        metrics = status["metrics"]
        for key, value in metrics.items():
            print(f"  {key}: {value}")

        print("\nConfiguration:")
        config = status["config"]
        for key, value in config.items():
            print(f"  {key}: {value}")

        print("\nHallucination Summary:")
        if self.safety_framework.hallucination_log:
            by_type = {}
            for hall in self.safety_framework.hallucination_log:
                hall_type = hall.hallucination_type.value
                by_type[hall_type] = by_type.get(hall_type, 0) + 1

            for hall_type, count in by_type.items():
                print(f"  {hall_type}: {count}")
        else:
            print("  No hallucinations detected")

        print("\nDemo Results Summary:")
        for result in self.demo_results:
            print(f"  {result['demo']}: {json.dumps(result, indent=2}")


async def main():
    """Run safety demonstration"""
    demo = SafetyDemo()

    try:
        # Initialize with HIGH safety
        await demo.setup(safety_level=SafetyLevel.HIGH)

        # Run safety demos
        await demo.demo_hallucination_prevention()
        await asyncio.sleep(0.5)

        await demo.demo_drift_monitoring()
        await asyncio.sleep(0.5)

        await demo.demo_safety_checkpoints()
        await asyncio.sleep(0.5)

        await demo.demo_consensus_validation()
        await asyncio.sleep(0.5)

        await demo.demo_safety_levels()

        # Final report
        await demo.show_safety_report()

    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    print("🛡️ LUKHAS Parallel Reality Safety Framework Demo")
    print("=" * 50)
    print("Demonstrating enterprise-grade safety features")
    print("for quantum-inspired reality simulation\n")

    asyncio.run(main())