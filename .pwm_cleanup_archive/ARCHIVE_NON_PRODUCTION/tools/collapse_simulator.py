#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Collapse Simulator CLI

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Command-line utility for simulating collapse scenarios in the LUKHAS AGI
system. This tool allows developers and operators to test system resilience,
validate collapse detection mechanisms, and understand entropy dynamics.

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: Collapse simulation CLI tool
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 13

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from trace.drift_tools import DriftRecoverySimulator, EntropyProfile

    from core.monitoring.collapse_tracker import (
        CollapseAlertLevel,
        CollapseTracker,
    )
    from core.symbolic.collapse.collapse_engine import (
        CollapseEngine,
        MemoryNode,
        get_global_engine,
    )
except ImportError as e:
    print(f"Error importing LUKHAS modules: {e}")
    print("Please ensure LUKHAS is properly installed and PYTHONPATH is set.")
    sys.exit(1)

# Try to import visualization libraries (optional)
try:
    import matplotlib.pyplot as plt
    import numpy as np

    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib not available. Visualization features disabled.")


class CollapseSimulator:
    """
    Interactive collapse simulation tool for LUKHAS AGI.
    """

    def __init__(self, output_dir: Path = None):
        """Initialize the simulator."""
        self.output_dir = output_dir or Path("lukhas/logs/simulations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.collapse_tracker = CollapseTracker(
            persistence_path=self.output_dir / "collapse_simulation.jsonl"
        )
        self.collapse_engine = get_global_engine()
        self.drift_simulator = DriftRecoverySimulator(
            checkpoint_dir=str(self.output_dir / "checkpoints")
        )

        # Simulation state
        self.simulation_id = f"sim_{datetime.now():%Y%m%d_%H%M%S}"
        self.results = []

    async def run_scenario(self, scenario: str = "normal") -> Dict[str, Any]:
        """
        Run a predefined collapse scenario.

        Args:
            scenario: Scenario name (normal, drift, collapse, cascade)

        Returns:
            Dictionary with simulation results
        """
        print(f"\n🌀 Running scenario: {scenario}")
        print("=" * 50)

        start_time = time.time()

        if scenario == "normal":
            result = await self._run_normal_scenario()
        elif scenario == "drift":
            result = await self._run_drift_scenario()
        elif scenario == "collapse":
            result = await self._run_collapse_scenario()
        elif scenario == "cascade":
            result = await self._run_cascade_scenario()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        duration = time.time() - start_time
        result["duration"] = duration
        result["scenario"] = scenario
        result["timestamp"] = datetime.now().isoformat()

        self.results.append(result)
        return result

    async def _run_normal_scenario(self) -> Dict[str, Any]:
        """Simulate normal system operation with low entropy."""
        print("Simulating normal operation...")

        # Generate synthetic data with low entropy
        symbolic_data, component_scores = (
            self.collapse_tracker.generate_synthetic_test_data("normal")
        )

        # Create memory nodes
        nodes = []
        for i in range(10):
            node = MemoryNode(
                content=f"Normal memory {i}",
                semantic_tags=["normal", "stable", "coherent"],
                emotional_weight=0.3 + random.random() * 0.2,
            )
            nodes.append(node)

        # Update entropy
        initial_entropy = self.collapse_tracker.update_entropy_score(
            symbolic_data, component_scores
        )

        # Monitor for 5 seconds
        entropy_history = [initial_entropy]
        alert_history = [self.collapse_tracker.current_state.alert_level]

        for _ in range(5):
            await asyncio.sleep(1)
            # Add slight variations
            variation = random.uniform(-0.05, 0.05)
            new_scores = {
                k: max(0, min(1, v + variation)) for k, v in component_scores.items()
            }

            entropy = self.collapse_tracker.update_entropy_score(
                symbolic_data, new_scores
            )
            entropy_history.append(entropy)
            alert_history.append(self.collapse_tracker.current_state.alert_level)

        # Try consolidation (should succeed with similar nodes)
        collapse_result = self.collapse_engine.collapse_nodes(
            nodes[:5], strategy="consolidation"
        )

        return {
            "initial_entropy": initial_entropy,
            "final_entropy": entropy_history[-1],
            "entropy_history": entropy_history,
            "alert_levels": [a.value for a in alert_history],
            "max_alert": max(
                alert_history, key=lambda x: list(CollapseAlertLevel).index(x)
            ).value,
            "collapse_successful": collapse_result is not None,
            "collapse_type": collapse_result.collapse_type if collapse_result else None,
            "semantic_loss": collapse_result.semantic_loss if collapse_result else 0,
            "health_metrics": self.collapse_tracker.get_system_health(),
        }

    async def _run_drift_scenario(self) -> Dict[str, Any]:
        """Simulate gradual drift with increasing entropy."""
        print("Simulating symbolic drift...")

        # Initial stable state
        symbolic_data = ["glyph_001"] * 30 + ["glyph_002"] * 20
        component_scores = {
            "memory": 0.3,
            "reasoning": 0.25,
            "emotion": 0.35,
            "consciousness": 0.28,
        }

        # Create memory nodes with increasing diversity
        nodes = []
        entropy_history = []
        alert_history = []

        # Simulate drift over time
        for step in range(10):
            # Introduce new glyphs (drift)
            for _ in range(5):
                symbolic_data.append(f"glyph_{random.randint(100, 200):03d}")

            # Increase component entropy
            for key in component_scores:
                component_scores[key] = min(0.9, component_scores[key] * 1.08)

            # Create diverse nodes
            node = MemoryNode(
                content=f"Drifting memory {step}",
                semantic_tags=[f"drift_{step}", f"entropy_{step}", "unstable"],
                emotional_weight=0.5 + step * 0.05,
            )
            nodes.append(node)

            # Update tracking
            entropy = self.collapse_tracker.update_entropy_score(
                symbolic_data, component_scores
            )
            entropy_history.append(entropy)
            alert_history.append(self.collapse_tracker.current_state.alert_level)

            print(
                f"  Step {step}: Entropy={entropy:.3f}, Alert={alert_history[-1].value}"
            )

            await asyncio.sleep(0.5)

        # Attempt compression due to high entropy
        if len(nodes) >= 5:
            collapse_result = self.collapse_engine.collapse_nodes(
                nodes[-5:], strategy="compression"
            )
        else:
            collapse_result = None

        # Use drift recovery simulator
        symbol_id = "drift_test_symbol"
        entropy_profile = EntropyProfile("drift_sine", 0.4, 0.15, 0.3)

        injection_result = await self.drift_simulator.inject_drift(
            symbol_id, magnitude=0.4, entropy_profile=entropy_profile, duration=5.0
        )

        recovery_metrics = await self.drift_simulator.measure_recovery(
            symbol_id, timeout=10.0, intervention_strategy="moderate"
        )

        return {
            "initial_entropy": entropy_history[0] if entropy_history else 0,
            "final_entropy": entropy_history[-1] if entropy_history else 0,
            "entropy_history": entropy_history,
            "alert_levels": [a.value for a in alert_history],
            "max_alert": max(
                alert_history, key=lambda x: list(CollapseAlertLevel).index(x)
            ).value,
            "drift_detected": any(a != CollapseAlertLevel.GREEN for a in alert_history),
            "collapse_result": {
                "successful": collapse_result is not None,
                "type": collapse_result.collapse_type if collapse_result else None,
                "entropy_reduction": (
                    collapse_result.entropy_reduction if collapse_result else 0
                ),
            },
            "recovery_metrics": recovery_metrics.to_dict(),
            "resilience_score": self.drift_simulator.score_resilience(symbol_id),
        }

    async def _run_collapse_scenario(self) -> Dict[str, Any]:
        """Simulate critical collapse with high entropy."""
        print("Simulating system collapse...")

        # Generate high entropy data
        symbolic_data, component_scores = (
            self.collapse_tracker.generate_synthetic_test_data("collapse")
        )

        # Create chaotic memory nodes
        nodes = []
        for i in range(20):
            node = MemoryNode(
                content=f"Chaotic memory {i}",
                semantic_tags=[f"chaos_{random.randint(0, 100)}" for _ in range(5)],
                emotional_weight=random.random(),
            )
            nodes.append(node)

        entropy_history = []
        alert_history = []
        collapse_events = []

        # Rapid entropy injection
        for step in range(5):
            # Update with chaotic data
            entropy = self.collapse_tracker.update_entropy_score(
                [f"glyph_{random.randint(0, 1000):04d}" for _ in range(100)],
                component_scores,
            )
            entropy_history.append(entropy)
            alert_history.append(self.collapse_tracker.current_state.alert_level)

            # Record collapse event if critical
            if (
                self.collapse_tracker.current_state.alert_level
                == CollapseAlertLevel.RED
            ):
                trace_id = self.collapse_tracker.record_collapse_event(
                    affected_components=["memory", "reasoning", "consciousness"],
                    symbolic_drift={k: v for k, v in component_scores.items()},
                    metadata={"step": step, "chaos_level": "extreme"},
                )
                collapse_events.append(trace_id)

            print(
                f"  Step {step}: Entropy={entropy:.3f}, Alert={alert_history[-1].value}"
            )

            # Try emergency fusion to create abstraction
            if step == 3 and len(nodes) >= 10:
                fusion_result = self.collapse_engine.collapse_nodes(
                    nodes[-10:], strategy="fusion"
                )
                if fusion_result:
                    print(
                        f"  Emergency fusion created: {fusion_result.collapsed_node.node_id}"
                    )

            await asyncio.sleep(0.3)

        # Get collapse metrics
        engine_metrics = self.collapse_engine.get_collapse_metrics()

        return {
            "collapse_detected": True,
            "collapse_events": collapse_events,
            "max_entropy": max(entropy_history),
            "entropy_history": entropy_history,
            "alert_levels": [a.value for a in alert_history],
            "time_to_critical": next(
                (i for i, a in enumerate(alert_history) if a == CollapseAlertLevel.RED),
                -1,
            ),
            "engine_metrics": engine_metrics,
            "system_health": self.collapse_tracker.get_system_health(),
        }

    async def _run_cascade_scenario(self) -> Dict[str, Any]:
        """Simulate emotional cascade scenario."""
        print("Simulating emotional cascade...")

        # Use drift simulator for cascade
        cascade_result = await self.drift_simulator.simulate_emotional_cascade(
            trigger_symbol="cascade_trigger",
            cascade_depth=3,
            propagation_factor=0.7,
            dream_integration=True,
        )

        # Monitor entropy during cascade
        entropy_history = []
        for _ in range(5):
            # Simulate cascade affecting system entropy
            affected_count = len(cascade_result["affected_symbols"])
            cascade_entropy = min(1.0, affected_count * 0.1)

            entropy = self.collapse_tracker.update_entropy_score(
                cascade_result["affected_symbols"],
                {"emotional_cascade": cascade_entropy},
            )
            entropy_history.append(entropy)
            await asyncio.sleep(0.5)

        return {
            "cascade_result": cascade_result,
            "entropy_impact": entropy_history,
            "max_entropy": max(entropy_history),
            "cascade_contained": max(entropy_history) < 0.7,
            "final_alert_level": self.collapse_tracker.current_state.alert_level.value,
        }

    async def interactive_mode(self):
        """Run interactive simulation mode."""
        print("\n🎮 LUKHAS Collapse Simulator - Interactive Mode")
        print("=" * 60)

        while True:
            print("\nAvailable commands:")
            print("  1. Run scenario (normal/drift/collapse/cascade)")
            print("  2. Show current system health")
            print("  3. Inject custom entropy")
            print("  4. View collapse history")
            print("  5. Export results")
            print("  6. Plot entropy graph (if available)")
            print("  0. Exit")

            try:
                choice = input("\nEnter command (0-6): ").strip()

                if choice == "0":
                    break
                elif choice == "1":
                    scenario = input(
                        "Enter scenario (normal/drift/collapse/cascade): "
                    ).strip()
                    result = await self.run_scenario(scenario)
                    print(
                        f"\nScenario completed. Max entropy: {result.get('final_entropy', 0):.3f}"
                    )
                elif choice == "2":
                    health = self.collapse_tracker.get_system_health()
                    print("\nSystem Health:")
                    print(f"  Entropy: {health['entropy_score']:.3f}")
                    print(f"  Alert Level: {health['alert_level']}")
                    print(f"  Entropy Slope: {health['entropy_slope']:.3f}")
                elif choice == "3":
                    magnitude = float(input("Enter entropy magnitude (0-1): "))
                    data = [f"custom_{i}" for i in range(int(magnitude * 100))]
                    entropy = self.collapse_tracker.update_entropy_score(data)
                    print(f"Entropy updated to: {entropy:.3f}")
                elif choice == "4":
                    history = self.collapse_tracker.get_collapse_history(limit=5)
                    print(f"\nRecent collapse events: {len(history)}")
                    for event in history:
                        print(
                            f"  - {event['collapse_trace_id']}: {event['alert_level']}"
                        )
                elif choice == "5":
                    self.export_results()
                elif choice == "6":
                    if HAS_PLOTTING:
                        self.plot_entropy_history()
                    else:
                        print("Plotting not available. Install matplotlib.")
                else:
                    print("Invalid choice.")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def export_results(self):
        """Export simulation results to JSON."""
        output_file = self.output_dir / f"{self.simulation_id}_results.json"

        export_data = {
            "simulation_id": self.simulation_id,
            "timestamp": datetime.now().isoformat(),
            "scenarios_run": len(self.results),
            "results": self.results,
            "collapse_metrics": self.collapse_engine.get_collapse_metrics(),
            "system_health": self.collapse_tracker.get_system_health(),
        }

        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\nResults exported to: {output_file}")

    def plot_entropy_history(self):
        """Plot entropy history from simulations."""
        if not HAS_PLOTTING:
            print("Plotting not available.")
            return

        if not self.results:
            print("No simulation results to plot.")
            return

        plt.figure(figsize=(12, 6))

        for i, result in enumerate(self.results):
            if "entropy_history" in result:
                entropy_history = result["entropy_history"]
                scenario = result.get("scenario", f"Simulation {i+1}")
                plt.plot(entropy_history, label=scenario, marker="o")

        # Add alert level thresholds
        plt.axhline(y=0.3, color="y", linestyle="--", label="Yellow Alert")
        plt.axhline(y=0.5, color="orange", linestyle="--", label="Orange Alert")
        plt.axhline(y=0.7, color="r", linestyle="--", label="Red Alert")

        plt.xlabel("Time Steps")
        plt.ylabel("Entropy Score")
        plt.title("LUKHAS Collapse Entropy Simulation")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 1)

        output_file = self.output_dir / f"{self.simulation_id}_entropy_plot.png"
        plt.savefig(output_file)
        print(f"\nPlot saved to: {output_file}")
        plt.show()


async def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="LUKHAS Collapse Simulator - Test and visualize collapse scenarios"
    )

    parser.add_argument(
        "--scenario",
        choices=["normal", "drift", "collapse", "cascade"],
        help="Run a specific scenario",
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument("--batch", type=str, help="Run batch scenarios from JSON file")

    parser.add_argument(
        "--output",
        type=str,
        default="lukhas/logs/simulations",
        help="Output directory for results",
    )

    parser.add_argument(
        "--plot", action="store_true", help="Generate entropy plots after simulation"
    )

    args = parser.parse_args()

    # Initialize simulator
    simulator = CollapseSimulator(output_dir=Path(args.output))

    try:
        if args.interactive:
            await simulator.interactive_mode()
        elif args.scenario:
            result = await simulator.run_scenario(args.scenario)
            print("\nSimulation complete:")
            print(f"  Final entropy: {result.get('final_entropy', 0):.3f}")
            print(f"  Max alert level: {result.get('max_alert', 'GREEN')}")

            if args.plot:
                simulator.plot_entropy_history()
        elif args.batch:
            # Load batch scenarios
            with open(args.batch) as f:
                scenarios = json.load(f)

            for scenario in scenarios.get("scenarios", []):
                print(f"\nRunning batch scenario: {scenario}")
                await simulator.run_scenario(scenario)

            if args.plot:
                simulator.plot_entropy_history()
        else:
            # Run default demonstration
            print("Running demonstration scenarios...")
            for scenario in ["normal", "drift", "collapse"]:
                await simulator.run_scenario(scenario)
                await asyncio.sleep(1)

            if args.plot or HAS_PLOTTING:
                simulator.plot_entropy_history()

        # Always export results
        simulator.export_results()

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError during simulation: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠═══════════════════════════════════════════════════════════════════════════════
║ USAGE EXAMPLES:
║   # Run normal scenario
║   python collapse_simulator.py --scenario normal
║
║   # Interactive mode
║   python collapse_simulator.py --interactive
║
║   # Batch mode with plotting
║   python collapse_simulator.py --batch scenarios.json --plot
║
║   # Custom output directory
║   python collapse_simulator.py --scenario collapse --output /tmp/collapse_test
║
║ INTEGRATION:
║   - CollapseTracker: Core monitoring system
║   - CollapseEngine: Memory node collapse operations
║   - DriftRecoverySimulator: Drift and cascade simulation
║
║ OUTPUT FILES:
║   - {simulation_id}_results.json: Complete simulation results
║   - {simulation_id}_entropy_plot.png: Entropy visualization
║   - collapse_simulation.jsonl: Persistence log
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
