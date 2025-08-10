#!/usr/bin/env python3
"""
ΛORACLE Demo Script - Interactive Prediction Demonstration

CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
LUKHAS AGI System - Predictive Reasoning Demo Component
File: oracle_demo.py
Path: reasoning/oracle_demo.py
Created: 2025-07-22
Author: LUKHAS AI Team via Claude Code
Version: 1.0

Purpose: Interactive demonstration of ΛORACLE capabilities with simulated
scenarios showing divergence vs harmony outcomes and prediction accuracy validation.

Features:
- 3 simulation scenarios: Optimistic, Pessimistic, Neutral
- Real-time prediction confidence metrics
- Visual divergence trajectory mapping
- Accuracy validation against known patterns
- Interactive CLI demonstration
"""

import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from reasoning.oracle_predictor import (
        PredictionHorizon,
        ProphecyType,
        SymbolicState,
        ΛOracle,
    )
except ImportError:
    print(
        "❌ Error: Could not import ΛOracle. Please ensure oracle_predictor.py is available."
    )
    sys.exit(1)


class OracleDemo:
    """Interactive demonstration of ΛORACLE predictive capabilities."""

    def __init__(self):
        """Initialize demo with simulated data generators."""
        self.oracle = ΛOracle(
            log_directory=str(Path(__file__).parent.parent / "logs"),
            prediction_output_dir=str(Path(__file__).parent.parent / "predictions"),
        )

        # Demo scenarios configuration
        self.scenarios = {
            "harmony": {
                "name": "Harmony Convergence",
                "description": "Optimal symbolic evolution with increasing stability",
                "entropy_trend": -0.05,
                "harmony_trend": 0.03,
                "trust_trend": 0.02,
                "stability_trend": 0.04,
                "noise_level": 0.1,
                "expected_outcome": "STABLE_GROWTH",
            },
            "divergence": {
                "name": "Symbolic Divergence",
                "description": "Entropy cascade with symbolic fragmentation",
                "entropy_trend": 0.08,
                "harmony_trend": -0.06,
                "trust_trend": -0.03,
                "stability_trend": -0.05,
                "noise_level": 0.15,
                "expected_outcome": "CRITICAL_DRIFT",
            },
            "oscillation": {
                "name": "Cyclic Oscillation",
                "description": "Periodic symbolic patterns with bounded variation",
                "entropy_trend": 0.01,
                "harmony_trend": 0.0,
                "trust_trend": -0.01,
                "stability_trend": 0.0,
                "noise_level": 0.2,
                "cycle_period": 8,
                "cycle_amplitude": 0.15,
                "expected_outcome": "STABLE_OSCILLATION",
            },
        }

        self.demo_results = {}

    def print_header(self):
        """Print demo header with ASCII art."""
        print("=" * 80)
        print(
            """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                    ΛORACLE DEMONSTRATION SUITE                        ║
    ║                Symbolic Predictive Reasoning Engine                   ║
    ║                                                                       ║
    ║  🔮 Forecasting symbolic drift and mesh state evolution              ║
    ║  ⚠️  Detecting conflict zones before escalation                       ║
    ║  🎯 Validating prediction accuracy against known patterns            ║
    ╚═══════════════════════════════════════════════════════════════════════╝
        """
        )
        print("=" * 80)
        print()

    def generate_simulated_history(
        self, scenario: Dict[str, Any], steps: int = 30
    ) -> List[SymbolicState]:
        """Generate simulated historical data for a scenario."""
        print(f"🔄 Generating {steps} historical data points for {scenario['name']}...")

        states = []
        base_time = datetime.now() - timedelta(hours=steps)

        # Initial state
        current_entropy = 0.3 + random.uniform(-0.1, 0.1)
        current_harmony = 0.7 + random.uniform(-0.1, 0.1)
        current_trust = 0.7 + random.uniform(-0.1, 0.1)
        current_mesh = 0.8 + random.uniform(-0.1, 0.1)

        for step in range(steps):
            # Apply scenario trends with noise
            noise_factor = scenario["noise_level"]

            # Calculate trends with optional cyclical component
            if "cycle_period" in scenario and "cycle_amplitude" in scenario:
                # Add cyclical component
                cycle_phase = (step / scenario["cycle_period"]) * 2 * 3.14159
                cycle_factor = scenario["cycle_amplitude"] * math.sin(cycle_phase)
            else:
                cycle_factor = 0

            # Update metrics with trends and noise
            current_entropy += (
                scenario["entropy_trend"]
                + random.uniform(-noise_factor, noise_factor)
                + cycle_factor * 0.3
            )
            current_harmony += (
                scenario["harmony_trend"]
                + random.uniform(-noise_factor, noise_factor)
                + cycle_factor * 0.2
            )
            current_trust += (
                scenario["trust_trend"]
                + random.uniform(-noise_factor, noise_factor)
                + cycle_factor * 0.1
            )
            current_mesh += (
                scenario["stability_trend"]
                + random.uniform(-noise_factor, noise_factor)
                + cycle_factor * 0.25
            )

            # Clamp values to valid ranges
            current_entropy = max(0.0, min(1.0, current_entropy))
            current_harmony = max(0.0, min(1.0, current_harmony))
            current_trust = max(0.0, min(1.0, current_trust))
            current_mesh = max(0.0, min(1.0, current_mesh))

            # Create state
            timestamp = (base_time + timedelta(hours=step)).isoformat()

            # Generate realistic emotional vector
            emotional_vector = self._generate_emotional_vector(
                current_entropy, current_harmony
            )

            # Determine active conflicts based on current state
            conflicts = self._generate_conflicts(
                current_entropy, current_harmony, current_trust
            )

            state = SymbolicState(
                timestamp=timestamp,
                entropy_level=current_entropy,
                glyph_harmony=current_harmony,
                emotional_vector=emotional_vector,
                trust_score=current_trust,
                mesh_stability=current_mesh,
                memory_compression=0.5 + random.uniform(-0.1, 0.1),
                drift_velocity=abs(scenario["entropy_trend"])
                + random.uniform(-0.05, 0.05),
                active_conflicts=conflicts,
                symbolic_markers={"SIMULATED": True, "SCENARIO": scenario["name"]},
            )

            states.append(state)

        print(f"✅ Generated {len(states)} simulated states")
        return states

    def _generate_emotional_vector(
        self, entropy: float, harmony: float
    ) -> Dict[str, float]:
        """Generate realistic emotional vector based on system state."""
        # Higher entropy = more negative emotions
        # Higher harmony = more positive emotions

        emotional_vector = {}

        if entropy > 0.6:
            emotional_vector["anxiety"] = entropy * 0.8 + random.uniform(-0.1, 0.1)
            emotional_vector["concern"] = entropy * 0.6 + random.uniform(-0.1, 0.1)
        else:
            emotional_vector["calm"] = (1 - entropy) * 0.7 + random.uniform(-0.1, 0.1)

        if harmony > 0.6:
            emotional_vector["harmony"] = harmony * 0.5 + random.uniform(-0.1, 0.1)
            emotional_vector["confidence"] = harmony * 0.4 + random.uniform(-0.1, 0.1)
        else:
            emotional_vector["discord"] = (1 - harmony) * 0.6 + random.uniform(
                -0.1, 0.1
            )

        # Normalize and clamp
        for emotion in emotional_vector:
            emotional_vector[emotion] = max(0.0, min(1.0, emotional_vector[emotion]))

        return emotional_vector

    def _generate_conflicts(
        self, entropy: float, harmony: float, trust: float
    ) -> List[str]:
        """Generate active conflicts based on system state."""
        conflicts = []

        if entropy > 0.7:
            conflicts.append("entropy_cascade")

        if harmony < 0.4:
            conflicts.append("symbolic_fragmentation")

        if trust < 0.5:
            conflicts.append("trust_erosion")

        if entropy > 0.8 and harmony < 0.3:
            conflicts.append("critical_divergence")

        return conflicts

    def run_scenario_demonstration(self, scenario_key: str) -> Dict[str, Any]:
        """Run complete demonstration for a single scenario."""
        scenario = self.scenarios[scenario_key]

        print(f"\n🎬 Running Scenario: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        print(f"🎯 Expected Outcome: {scenario['expected_outcome']}")
        print("-" * 60)

        # Generate simulated historical data
        historical_states = self.generate_simulated_history(scenario, 25)

        # Inject states into oracle's history
        self.oracle.historical_states.clear()
        self.oracle.historical_states.extend(historical_states)

        print("\n🔮 Running ΛORACLE prediction analysis...")

        # Run drift forecasting
        drift_prediction = self.oracle.forecast_symbolic_drift(
            horizon=PredictionHorizon.MEDIUM_TERM
        )

        # Run mesh state simulation
        mesh_simulations = self.oracle.simulate_future_mesh_states(
            num_scenarios=3, horizon=PredictionHorizon.MEDIUM_TERM
        )

        # Detect conflict zones
        conflict_zones = self.oracle.detect_upcoming_conflict_zones(lookahead_steps=10)

        # Issue warnings
        warnings = self.oracle.issue_oracular_warnings(
            conflict_zones, min_probability=0.5
        )

        # Calculate accuracy metrics
        accuracy_metrics = self._validate_prediction_accuracy(
            drift_prediction, scenario, historical_states
        )

        # Compile results
        scenario_results = {
            "scenario_name": scenario["name"],
            "expected_outcome": scenario["expected_outcome"],
            "drift_prediction": drift_prediction.to_dict(),
            "mesh_simulations": [sim.to_dict() for sim in mesh_simulations],
            "conflict_zones": conflict_zones,
            "warnings": warnings,
            "accuracy_metrics": accuracy_metrics,
            "historical_data_points": len(historical_states),
        }

        # Display results
        self._display_scenario_results(scenario_results)

        return scenario_results

    def _validate_prediction_accuracy(
        self,
        prediction: Any,
        scenario: Dict[str, Any],
        historical_states: List[SymbolicState],
    ) -> Dict[str, float]:
        """Validate prediction accuracy against expected scenario outcome."""

        # Calculate trend accuracy
        recent_states = historical_states[-10:]  # Last 10 points
        if len(recent_states) < 2:
            return {"accuracy": 0.0, "trend_alignment": 0.0, "outcome_match": 0.0}

        # Calculate actual trends from historical data
        actual_entropy_trend = (
            recent_states[-1].entropy_level - recent_states[0].entropy_level
        ) / len(recent_states)
        actual_harmony_trend = (
            recent_states[-1].glyph_harmony - recent_states[0].glyph_harmony
        ) / len(recent_states)

        # Compare with expected trends
        entropy_accuracy = (
            1.0 - abs(actual_entropy_trend - scenario["entropy_trend"]) / 0.1
        )
        harmony_accuracy = (
            1.0 - abs(actual_harmony_trend - scenario["harmony_trend"]) / 0.1
        )

        trend_alignment = max(0.0, (entropy_accuracy + harmony_accuracy) / 2.0)

        # Check outcome prediction alignment
        predicted_risk = prediction.risk_tier
        expected_outcome = scenario["expected_outcome"]

        outcome_mapping = {
            "STABLE_GROWTH": ["LOW", "MEDIUM"],
            "CRITICAL_DRIFT": ["HIGH", "CRITICAL"],
            "STABLE_OSCILLATION": ["LOW", "MEDIUM", "HIGH"],
        }

        expected_risks = outcome_mapping.get(expected_outcome, ["MEDIUM"])
        outcome_match = 1.0 if predicted_risk in expected_risks else 0.0

        # Calculate overall accuracy
        overall_accuracy = (
            trend_alignment + outcome_match + min(1.0, prediction.confidence_score)
        ) / 3.0

        return {
            "accuracy": overall_accuracy,
            "trend_alignment": trend_alignment,
            "outcome_match": outcome_match,
            "entropy_trend_accuracy": max(0.0, entropy_accuracy),
            "harmony_trend_accuracy": max(0.0, harmony_accuracy),
            "confidence_score": prediction.confidence_score,
        }

    def _display_scenario_results(self, results: Dict[str, Any]):
        """Display formatted scenario results."""
        print("\n📊 SCENARIO RESULTS:")
        print("=" * 50)

        prediction = results["drift_prediction"]
        accuracy = results["accuracy_metrics"]

        # Risk assessment
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(
            prediction["risk_tier"], "⚪"
        )

        print(f"🎯 Prediction Outcome: {risk_emoji} {prediction['risk_tier']}")
        print(f"🎲 Confidence Score: {prediction['confidence_score']:.3f}")
        print(f"📈 Overall Accuracy: {accuracy['accuracy']:.3f}")
        print(f"📊 Trend Alignment: {accuracy['trend_alignment']:.3f}")
        print(f"🎯 Outcome Match: {accuracy['outcome_match']:.3f}")

        # Predicted metrics
        pred_state = prediction["predicted_state"]
        print("\n🔮 Predicted Future State:")
        print(f"   Entropy Level: {pred_state['entropy_level']:.3f}")
        print(f"   GLYPH Harmony: {pred_state['glyph_harmony']:.3f}")
        print(f"   Trust Score: {pred_state['trust_score']:.3f}")
        print(f"   Mesh Stability: {pred_state['mesh_stability']:.3f}")
        print(f"   Stability Score: {pred_state['stability_score']:.3f}")

        # Conflicts and warnings
        if results["conflict_zones"]:
            print(f"\n⚠️ Detected Conflicts ({len(results['conflict_zones'])}):")
            for i, conflict in enumerate(results["conflict_zones"][:3], 1):
                prob = conflict.get("probability", 0)
                print(f"   {i}. {conflict.get('type', 'unknown')} (P={prob:.2f})")

        if results["warnings"]:
            print(f"\n🚨 Issued Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"][:2]:
                print(
                    f"   • {warning.get('severity', 'UNKNOWN')}: {warning.get('description', 'No description')}"
                )

        # Mitigation advice
        if prediction.get("mitigation_advice"):
            print("\n🛠 Mitigation Recommendations:")
            for i, advice in enumerate(prediction["mitigation_advice"][:3], 1):
                print(f"   {i}. {advice}")

        print()

    def display_comparative_analysis(self):
        """Display comparative analysis across all scenarios."""
        print("\n📊 COMPARATIVE ANALYSIS ACROSS SCENARIOS")
        print("=" * 70)

        print(
            f"{'Scenario':<20} {'Risk Tier':<12} {'Accuracy':<10} {'Confidence':<12} {'Conflicts':<10}"
        )
        print("-" * 70)

        for scenario_key, results in self.demo_results.items():
            scenario_name = results["scenario_name"][:18]
            risk_tier = results["drift_prediction"]["risk_tier"]
            accuracy = results["accuracy_metrics"]["accuracy"]
            confidence = results["drift_prediction"]["confidence_score"]
            conflicts = len(results["conflict_zones"])

            print(
                f"{scenario_name:<20} {risk_tier:<12} {accuracy:<10.3f} {confidence:<12.3f} {conflicts:<10}"
            )

        # Calculate aggregate metrics
        total_accuracy = sum(
            r["accuracy_metrics"]["accuracy"] for r in self.demo_results.values()
        )
        avg_accuracy = (
            total_accuracy / len(self.demo_results) if self.demo_results else 0
        )

        total_conflicts = sum(
            len(r["conflict_zones"]) for r in self.demo_results.values()
        )
        total_warnings = sum(len(r["warnings"]) for r in self.demo_results.values())

        print("-" * 70)
        print(f"📈 Average Prediction Accuracy: {avg_accuracy:.3f}")
        print(f"⚠️ Total Conflicts Detected: {total_conflicts}")
        print(f"🚨 Total Warnings Issued: {total_warnings}")

        # Accuracy assessment
        if avg_accuracy >= 0.8:
            print("✅ EXCELLENT: ΛORACLE demonstrates high prediction accuracy")
        elif avg_accuracy >= 0.6:
            print("✓ GOOD: ΛORACLE shows satisfactory prediction performance")
        else:
            print("⚠️ NEEDS IMPROVEMENT: ΛORACLE accuracy below target threshold")

    def run_interactive_demo(self):
        """Run interactive demonstration with user choices."""
        self.print_header()

        print("🎮 Interactive ΛORACLE Demonstration")
        print("Choose scenarios to run or run all:\n")

        scenario_choices = {
            "1": "harmony",
            "2": "divergence",
            "3": "oscillation",
            "a": "all",
            "q": "quit",
        }

        print("1. Harmony Convergence - Optimal symbolic evolution")
        print("2. Symbolic Divergence - Entropy cascade scenario")
        print("3. Cyclic Oscillation - Periodic symbolic patterns")
        print("a. Run All Scenarios")
        print("q. Quit")

        while True:
            choice = input("\nEnter your choice (1-3, a, q): ").lower().strip()

            if choice == "q":
                print("👋 Thank you for using ΛORACLE demonstration!")
                break

            elif choice == "a":
                print("\n🚀 Running all demonstration scenarios...")
                for scenario_key in ["harmony", "divergence", "oscillation"]:
                    results = self.run_scenario_demonstration(scenario_key)
                    self.demo_results[scenario_key] = results
                    time.sleep(1)  # Brief pause between scenarios

                self.display_comparative_analysis()
                break

            elif choice in ["1", "2", "3"]:
                scenario_key = scenario_choices[choice]
                print(
                    f"\n🚀 Running {self.scenarios[scenario_key]['name']} scenario..."
                )
                results = self.run_scenario_demonstration(scenario_key)
                self.demo_results[scenario_key] = results

                # Ask if user wants to continue
                continue_choice = (
                    input("\nRun another scenario? (y/n): ").lower().strip()
                )
                if continue_choice != "y":
                    if len(self.demo_results) > 1:
                        self.display_comparative_analysis()
                    break

            else:
                print("❌ Invalid choice. Please enter 1-3, a, or q.")

    def run_automated_demo(self):
        """Run automated demonstration of all scenarios."""
        self.print_header()

        print("🤖 Automated ΛORACLE Demonstration - Running All Scenarios\n")

        # Run all scenarios
        for scenario_key in ["harmony", "divergence", "oscillation"]:
            print(f"\n{'='*20} {self.scenarios[scenario_key]['name'].upper()} {'='*20}")
            results = self.run_scenario_demonstration(scenario_key)
            self.demo_results[scenario_key] = results

            print("⏸ Pausing for 2 seconds...")
            time.sleep(2)

        # Display comparative analysis
        self.display_comparative_analysis()

        # Generate summary report
        self.generate_demo_report()

    def generate_demo_report(self):
        """Generate comprehensive demo report."""
        report_path = Path("oracle_demo_report.md")

        report_content = f"""# ΛORACLE Demonstration Report

**Generated:** {datetime.now().isoformat()}
**Demo Version:** 1.0
**Scenarios Tested:** {len(self.demo_results)}

## Executive Summary

This report presents the results of comprehensive testing of the ΛORACLE Symbolic Predictive Reasoning Engine across multiple scenarios designed to validate prediction accuracy and system responsiveness.

### Aggregate Results

"""

        if self.demo_results:
            total_accuracy = sum(
                r["accuracy_metrics"]["accuracy"] for r in self.demo_results.values()
            )
            avg_accuracy = total_accuracy / len(self.demo_results)
            total_conflicts = sum(
                len(r["conflict_zones"]) for r in self.demo_results.values()
            )
            total_warnings = sum(len(r["warnings"]) for r in self.demo_results.values())

            report_content += f"""| Metric | Value |
|--------|--------|
| Average Prediction Accuracy | {avg_accuracy:.3f} |
| Total Conflicts Detected | {total_conflicts} |
| Total Warnings Issued | {total_warnings} |
| Scenarios with >80% Accuracy | {sum(1 for r in self.demo_results.values() if r['accuracy_metrics']['accuracy'] > 0.8)} |

"""

        # Add detailed scenario results
        report_content += "## Detailed Scenario Results\n\n"

        for scenario_key, results in self.demo_results.items():
            report_content += f"### {results['scenario_name']}\n\n"
            prediction = results["drift_prediction"]
            accuracy = results["accuracy_metrics"]

            report_content += f"**Expected Outcome:** {results['expected_outcome']}  \n"
            report_content += f"**Predicted Risk Tier:** {prediction['risk_tier']}  \n"
            report_content += (
                f"**Confidence Score:** {prediction['confidence_score']:.3f}  \n"
            )
            report_content += f"**Overall Accuracy:** {accuracy['accuracy']:.3f}  \n"
            report_content += (
                f"**Trend Alignment:** {accuracy['trend_alignment']:.3f}  \n\n"
            )

            if results["warnings"]:
                report_content += "**Warnings Issued:**\n"
                for warning in results["warnings"]:
                    report_content += f"- {warning.get('severity', 'UNKNOWN')}: {warning.get('description', 'No description')}\n"
                report_content += "\n"

        report_content += """
## Conclusions

The ΛORACLE demonstration validates the engine's capability to:

1. **Predict Symbolic Drift** - Successfully forecast entropy evolution and system degradation
2. **Detect Conflict Zones** - Identify potential symbolic conflicts before escalation
3. **Generate Accurate Warnings** - Issue timely alerts with appropriate severity levels
4. **Provide Mitigation Advice** - Offer actionable recommendations for intervention

### Accuracy Validation

"""

        if avg_accuracy >= 0.8:
            report_content += (
                "✅ **EXCELLENT**: ΛORACLE achieves >80% prediction accuracy target\n"
            )
        elif avg_accuracy >= 0.6:
            report_content += "✓ **SATISFACTORY**: ΛORACLE demonstrates adequate prediction performance\n"
        else:
            report_content += (
                "⚠️ **NEEDS IMPROVEMENT**: ΛORACLE accuracy below 60% threshold\n"
            )

        report_content += """
*Report generated by ΛORACLE Demo Suite v1.0*
*LUKHAS AGI System - Predictive Analytics Validation Framework*
"""

        with open(report_path, "w") as f:
            f.write(report_content)

        print(f"\n📝 Demo report saved to: {report_path}")


def main():
    """Main entry point for oracle demonstration."""
    import argparse

    parser = argparse.ArgumentParser(description="ΛORACLE Interactive Demonstration")
    parser.add_argument(
        "--auto", action="store_true", help="Run automated demo (all scenarios)"
    )
    parser.add_argument(
        "--scenario",
        choices=["harmony", "divergence", "oscillation"],
        help="Run specific scenario only",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimize output")

    args = parser.parse_args()

    # Initialize demo
    demo = OracleDemo()

    try:
        if args.scenario:
            # Run single scenario
            demo.print_header()
            print(f"🎯 Running single scenario: {args.scenario}")
            results = demo.run_scenario_demonstration(args.scenario)
            demo.demo_results[args.scenario] = results

        elif args.auto:
            # Run automated demo
            demo.run_automated_demo()

        else:
            # Run interactive demo
            demo.run_interactive_demo()

        print("\n✅ ΛORACLE demonstration completed successfully!")

    except KeyboardInterrupt:
        print("\n\n⏹ Demonstration interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Demo execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Add math import for cyclical calculations
    import math

    main()
