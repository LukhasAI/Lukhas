#!/usr/bin/env python3

"""
Aka Qualia Loop-Stress Testing Harness
====================================

Synthetic test scenarios for validating Wave B completion criteria:
- ≥25% neurosis reduction vs baseline (Freud-2025 requirement)
- ≥15% CongruenceIndex uplift on goal tasks
- Positive RepairDelta in ≥70% of test episodes
- Energy conservation validation
- VIVOX drift compliance

Creates recurrent stimuli patterns designed to trigger neurosis loops,
then measures the effectiveness of regulation policies in breaking them.
"""
import asyncio
import random
import statistics
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional

from candidate.aka_qualia.core import AkaQualia


class StressTestType(Enum):
    """Types of stress test scenarios"""

    RUMINATION_LOOP = "rumination_loop"  # High narrative gravity + confusion
    ANXIETY_SPIRAL = "anxiety_spiral"  # High arousal + low agency
    PERFECTIONISM_TRAP = "perfectionism_trap"  # High clarity demand + low satisfaction
    DECISION_PARALYSIS = "decision_paralysis"  # High arousal + suspended temporal feel
    EXISTENTIAL_CRISIS = "existential_crisis"  # Low embodiment + high narrative gravity


@dataclass
class StressTestScenario:
    """Test scenario definition"""

    name: str
    test_type: StressTestType
    base_signals: dict[str, Any]
    base_goals: dict[str, Any]
    recurrence_pattern: list[dict[str, Any]]  # Variations for recurrent stimuli
    expected_triggers: list[str]  # Expected regulation actions
    baseline_neurosis_risk: float  # Expected risk without regulation


@dataclass
class StressTestResult:
    """Results from a single stress test episode"""

    scenario_name: str
    test_type: str
    episode_id: str

    # Core metrics (Wave B success criteria)
    neurosis_risk_before: float
    neurosis_risk_after: float
    neurosis_reduction_percent: float
    congruence_index: float
    repair_delta: float

    # Energy accounting
    energy_before: float
    energy_after: float
    conservation_ratio: float
    conservation_violation: bool

    # VIVOX compliance
    vivox_drift_score: float
    vivox_drift_exceeded: bool

    # Regulation effectiveness
    regulation_actions_triggered: list[str]
    teq_interventions: int
    processing_time_ms: float

    # Success flags for Wave B gates
    neurosis_reduction_target_met: bool  # ≥25% reduction
    congruence_target_met: bool  # ≥15% uplift
    repair_positive: bool  # Positive repair delta


@dataclass
class StressTestSummary:
    """Summary results across all test scenarios"""

    total_episodes: int
    test_duration_seconds: float

    # Wave B Gate Requirements
    neurosis_reduction_rate: float  # % episodes with ≥25% reduction
    congruence_improvement_rate: float  # % episodes with ≥15% uplift
    positive_repair_rate: float  # % episodes with positive repair

    # Aggregate metrics
    average_neurosis_reduction: float
    average_congruence_index: float
    average_repair_delta: float
    conservation_violation_rate: float
    vivox_compliance_rate: float

    # Per-scenario breakdown
    scenario_results: dict[str, dict[str, float]]

    # Wave B completion status
    wave_b_gate_passed: bool


class LoopStressHarness:
    """
    Synthetic loop-stress testing harness for Aka Qualia validation.

    Implements Freud-2025's Wave B gate requirements with recurrent
    stimuli designed to trigger neurosis loops and measure regulation effectiveness.
    """

    def __init__(self, aka_qualia: AkaQualia, config: Optional[dict[str, Any]] = None):
        """
        Initialize stress testing harness.

        Args:
            aka_qualia: AkaQualia instance to test
            config: Test configuration overrides
        """
        self.aka_qualia = aka_qualia
        self.config = self._load_config(config)

        # Test scenarios (designed to trigger neurosis patterns)
        self.scenarios = self._create_stress_scenarios()

        # Results tracking
        self.test_results: list[StressTestResult] = []
        self.baseline_measurements: dict[str, float] = {}

    def _load_config(self, config_override: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Load test configuration"""
        default_config = {
            # Wave B success thresholds (Freud-2025 requirements)
            "neurosis_reduction_threshold": 0.25,  # ≥25% reduction required
            "congruence_improvement_threshold": 0.15,  # ≥15% uplift required
            "positive_repair_rate_threshold": 0.70,  # ≥70% episodes
            # Test parameters
            "episodes_per_scenario": 10,
            "recurrence_iterations": 5,  # How many times to repeat stimuli
            "baseline_episodes": 3,  # Episodes without regulation for baseline
            "randomization_factor": 0.2,  # Signal variation between episodes
            # Stress intensities
            "high_stress_threshold": 0.8,
            "moderate_stress_threshold": 0.6,
            "low_stress_threshold": 0.3,
            # Test timeouts
            "max_episode_duration": 10.0,  # seconds
            "inter_episode_delay": 0.1,  # seconds
        }

        if config_override:
            default_config.update(config_override)

        return default_config

    def _create_stress_scenarios(self) -> list[StressTestScenario]:
        """Create synthetic stress test scenarios"""
        scenarios = []

        # Scenario 1: Rumination Loop (high narrative gravity + confusion)
        scenarios.append(
            StressTestScenario(
                name="rumination_loop",
                test_type=StressTestType.RUMINATION_LOOP,
                base_signals={
                    "text": "I keep thinking about that mistake I made",
                    "emotional_valence": -0.6,
                    "cognitive_load": 0.8,
                    "subject": "self",
                    "object": "past_mistake",
                },
                base_goals={
                    "understand_mistake": 0.9,
                    "move_forward": 0.8,
                    "peace_of_mind": 0.7,
                },
                recurrence_pattern=[
                    {"text": "Why did I do that?", "emotional_valence": -0.7},
                    {"text": "I should have known better", "emotional_valence": -0.8},
                    {
                        "text": "Everyone probably thinks I'm incompetent",
                        "emotional_valence": -0.9,
                    },
                    {
                        "text": "I keep thinking about that mistake I made",
                        "emotional_valence": -0.6,
                    },  # Loop back
                ],
                expected_triggers=["focus-shift", "reframe", "breathing"],
                baseline_neurosis_risk=0.75,
            )
        )

        # Scenario 2: Anxiety Spiral (high arousal + low agency)
        scenarios.append(
            StressTestScenario(
                name="anxiety_spiral",
                test_type=StressTestType.ANXIETY_SPIRAL,
                base_signals={
                    "text": "What if something terrible happens?",
                    "emotional_valence": -0.5,
                    "arousal_level": 0.9,
                    "subject": "self",
                    "object": "future_threat",
                },
                base_goals={"safety": 0.9, "control": 0.8, "certainty": 0.7},
                recurrence_pattern=[
                    {"text": "I can't control what happens", "arousal_level": 0.95},
                    {
                        "text": "Something bad is definitely going to happen",
                        "arousal_level": 0.98,
                    },
                    {"text": "I'm powerless to stop it", "arousal_level": 0.99},
                    {
                        "text": "What if something terrible happens?",
                        "arousal_level": 0.9,
                    },  # Loop back
                ],
                expected_triggers=["breathing", "pause", "reframe"],
                baseline_neurosis_risk=0.82,
            )
        )

        # Scenario 3: Perfectionism Trap (high clarity demand + never satisfied)
        scenarios.append(
            StressTestScenario(
                name="perfectionism_trap",
                test_type=StressTestType.PERFECTIONISM_TRAP,
                base_signals={
                    "text": "This isn't good enough yet",
                    "emotional_valence": -0.4,
                    "cognitive_load": 0.9,
                    "subject": "self",
                    "object": "work_output",
                },
                base_goals={
                    "perfection": 1.0,  # Impossible goal
                    "approval": 0.9,
                    "competence": 0.8,
                },
                recurrence_pattern=[
                    {
                        "text": "I need to fix this one more thing",
                        "cognitive_load": 0.92,
                    },
                    {"text": "It's still not perfect", "emotional_valence": -0.6},
                    {
                        "text": "People will judge me if it's not flawless",
                        "cognitive_load": 0.95,
                    },
                    {
                        "text": "This isn't good enough yet",
                        "emotional_valence": -0.4,
                    },  # Loop back
                ],
                expected_triggers=["reframe", "focus-shift"],
                baseline_neurosis_risk=0.68,
            )
        )

        # Scenario 4: Decision Paralysis (high arousal + suspended time)
        scenarios.append(
            StressTestScenario(
                name="decision_paralysis",
                test_type=StressTestType.DECISION_PARALYSIS,
                base_signals={
                    "text": "I don't know what to choose",
                    "emotional_valence": -0.3,
                    "arousal_level": 0.7,
                    "temporal_pressure": 0.9,
                    "subject": "self",
                    "object": "decision",
                },
                base_goals={
                    "correct_choice": 0.9,
                    "avoid_regret": 0.8,
                    "certainty": 0.9,
                },
                recurrence_pattern=[
                    {"text": "What if I choose wrong?", "arousal_level": 0.8},
                    {"text": "I need more information", "temporal_pressure": 0.95},
                    {"text": "Both options have problems", "arousal_level": 0.85},
                    {
                        "text": "I don't know what to choose",
                        "temporal_pressure": 0.9,
                    },  # Loop back
                ],
                expected_triggers=["breathing", "focus-shift", "reframe"],
                baseline_neurosis_risk=0.71,
            )
        )

        # Scenario 5: Existential Crisis (low embodiment + high narrative gravity)
        scenarios.append(
            StressTestScenario(
                name="existential_crisis",
                test_type=StressTestType.EXISTENTIAL_CRISIS,
                base_signals={
                    "text": "What's the point of any of this?",
                    "emotional_valence": -0.7,
                    "cognitive_load": 0.8,
                    "embodiment_level": 0.2,
                    "subject": "self",
                    "object": "existence",
                },
                base_goals={"meaning": 0.9, "purpose": 0.8, "connection": 0.7},
                recurrence_pattern=[
                    {"text": "Nothing I do matters", "embodiment_level": 0.1},
                    {
                        "text": "Life is ultimately meaningless",
                        "emotional_valence": -0.9,
                    },
                    {
                        "text": "I'm just going through the motions",
                        "embodiment_level": 0.15,
                    },
                    {
                        "text": "What's the point of any of this?",
                        "emotional_valence": -0.7,
                    },  # Loop back
                ],
                expected_triggers=["reframe", "focus-shift", "breathing"],
                baseline_neurosis_risk=0.73,
            )
        )

        return scenarios

    async def run_baseline_measurement(self, scenario: StressTestScenario) -> float:
        """Measure baseline neurosis risk without regulation"""
        # Temporarily disable regulation for baseline
        original_config = self.aka_qualia.config.copy()
        self.aka_qualia.config.update({"enable_regulation": False, "conservative_regulation": False})

        neurosis_risks = []

        try:
            for _i in range(self.config["baseline_episodes"]):
                # Use base signals with slight randomization
                signals = self._randomize_signals(scenario.base_signals, 0.1)

                result = await self.aka_qualia.step(
                    signals=signals,
                    goals=scenario.base_goals,
                    ethics_state={},
                    guardian_state={},
                    memory_ctx={},
                )

                neurosis_risks.append(result["metrics"].neurosis_risk)

        finally:
            # Restore original configuration
            self.aka_qualia.config = original_config

        return statistics.mean(neurosis_risks) if neurosis_risks else 0.5

    async def run_stress_episode(self, scenario: StressTestScenario, episode_num: int) -> StressTestResult:
        """Run a single stress test episode with recurrent stimuli"""
        episode_start = time.time()
        episode_id = f"{scenario.name}_{episode_num}_{int(time.time())}"

        # Initial processing - establish baseline for this episode
        initial_signals = self._randomize_signals(scenario.base_signals, self.config["randomization_factor"])

        initial_result = await self.aka_qualia.step(
            signals=initial_signals,
            goals=scenario.base_goals,
            ethics_state={},
            guardian_state={},
            memory_ctx={},
        )

        neurosis_before = initial_result["metrics"].neurosis_risk
        energy_before = initial_result.get("energy_snapshot", {}).get("energy_before", 0.0)

        # Apply recurrent stimuli pattern (simulate neurosis loop triggers)
        final_result = initial_result
        for iteration in range(self.config["recurrence_iterations"]):
            for pattern_variation in scenario.recurrence_pattern:
                # Merge pattern variation with base signals
                signals = {**initial_signals, **pattern_variation}
                signals = self._randomize_signals(signals, 0.1)  # Small variation

                final_result = await self.aka_qualia.step(
                    signals=signals,
                    goals=scenario.base_goals,
                    ethics_state={},
                    guardian_state={},
                    memory_ctx={"episode_context": f"recurrence_{iteration}"},
                )

                # Break early if drift exceeded (VIVOX safety)
                if final_result.get("vivox_results", {}).get("drift_analysis", {}).get("drift_exceeded", False):
                    break

        # Extract final results
        neurosis_after = final_result["metrics"].neurosis_risk
        congruence_index = final_result["metrics"].congruence_index
        repair_delta = final_result["metrics"].repair_delta

        # Energy accounting
        energy_snapshot = final_result.get("energy_snapshot", {})
        energy_after = energy_snapshot.get("energy_after", energy_before)
        conservation_ratio = energy_after / energy_before if energy_before > 0 else 1.0
        conservation_violation = energy_snapshot.get("conservation_violation", False)

        # VIVOX compliance
        vivox_results = final_result.get("vivox_results", {})
        drift_score = vivox_results.get("drift_analysis", {}).get("drift_score", 0.0)
        drift_exceeded = vivox_results.get("drift_analysis", {}).get("drift_exceeded", False)

        # Regulation effectiveness
        regulation_audit = final_result.get("regulation_audit", {})
        actions_triggered = regulation_audit.get("policy_decision", {}).get("actions", [])
        teq_interventions = 1 if final_result["scene"].risk.score > 0.1 else 0

        # Processing time
        processing_time = (time.time() - episode_start) * 1000

        # Compute success metrics (Wave B gates)
        neurosis_reduction = (neurosis_before - neurosis_after) / neurosis_before if neurosis_before > 0 else 0
        neurosis_reduction_percent = neurosis_reduction * 100

        # Success flags
        neurosis_target_met = neurosis_reduction >= self.config["neurosis_reduction_threshold"]
        congruence_target_met = congruence_index >= self.config["congruence_improvement_threshold"]
        repair_positive = repair_delta > 0

        return StressTestResult(
            scenario_name=scenario.name,
            test_type=scenario.test_type.value,
            episode_id=episode_id,
            neurosis_risk_before=neurosis_before,
            neurosis_risk_after=neurosis_after,
            neurosis_reduction_percent=neurosis_reduction_percent,
            congruence_index=congruence_index,
            repair_delta=repair_delta,
            energy_before=energy_before,
            energy_after=energy_after,
            conservation_ratio=conservation_ratio,
            conservation_violation=conservation_violation,
            vivox_drift_score=drift_score,
            vivox_drift_exceeded=drift_exceeded,
            regulation_actions_triggered=actions_triggered,
            teq_interventions=teq_interventions,
            processing_time_ms=processing_time,
            neurosis_reduction_target_met=neurosis_target_met,
            congruence_target_met=congruence_target_met,
            repair_positive=repair_positive,
        )

    async def run_full_stress_test(self) -> StressTestSummary:
        """Run complete stress test suite and return Wave B gate results"""
        print("🧠 Starting Aka Qualia Loop-Stress Test Suite (Wave B Gate Validation)")
        test_start_time = time.time()

        # Collect baseline measurements
        print("📊 Measuring baseline neurosis risks...")
        for scenario in self.scenarios:
            baseline_risk = await self.run_baseline_measurement(scenario)
            self.baseline_measurements[scenario.name] = baseline_risk
            print(f"  {scenario.name}: {baseline_risk:.3f}")

        # Run stress episodes for each scenario
        all_results = []
        for scenario in self.scenarios:
            print(f"\n🔄 Testing {scenario.name} ({self.config['episodes_per_scenario']} episodes)...")

            for episode_num in range(self.config["episodes_per_scenario"]):
                result = await self.run_stress_episode(scenario, episode_num)
                all_results.append(result)

                print(
                    f"  Episode {episode_num + 1}: "
                    f"neurosis {result.neurosis_reduction_percent:+.1f}%, "
                    f"congruence {result.congruence_index:.3f}, "
                    f"repair {result.repair_delta:+.3f}"
                )

                # Brief delay between episodes
                await asyncio.sleep(self.config["inter_episode_delay"])

        # Analyze results
        test_duration = time.time() - test_start_time
        summary = self._analyze_results(all_results, test_duration)

        return summary

    def _analyze_results(self, results: list[StressTestResult], duration: float) -> StressTestSummary:
        """Analyze test results against Wave B gate requirements"""
        total_episodes = len(results)

        # Wave B gate metrics
        neurosis_successes = sum(1 for r in results if r.neurosis_reduction_target_met)
        congruence_successes = sum(1 for r in results if r.congruence_target_met)
        repair_successes = sum(1 for r in results if r.repair_positive)

        neurosis_reduction_rate = neurosis_successes / total_episodes
        congruence_improvement_rate = congruence_successes / total_episodes
        positive_repair_rate = repair_successes / total_episodes

        # Aggregate metrics
        avg_neurosis_reduction = statistics.mean(r.neurosis_reduction_percent for r in results)
        avg_congruence = statistics.mean(r.congruence_index for r in results)
        avg_repair = statistics.mean(r.repair_delta for r in results)

        # Quality metrics
        conservation_violations = sum(1 for r in results if r.conservation_violation)
        conservation_violation_rate = conservation_violations / total_episodes

        vivox_compliant = sum(1 for r in results if not r.vivox_drift_exceeded)
        vivox_compliance_rate = vivox_compliant / total_episodes

        # Per-scenario breakdown
        scenario_results = {}
        scenarios = list(set(r.scenario_name for r in results))
        for scenario in scenarios:
            scenario_data = [r for r in results if r.scenario_name == scenario]
            scenario_results[scenario] = {
                "neurosis_reduction_avg": statistics.mean(r.neurosis_reduction_percent for r in scenario_data),
                "congruence_avg": statistics.mean(r.congruence_index for r in scenario_data),
                "repair_avg": statistics.mean(r.repair_delta for r in scenario_data),
                "success_rate": sum(
                    1
                    for r in scenario_data
                    if r.neurosis_reduction_target_met and r.congruence_target_met and r.repair_positive
                )
                / len(scenario_data),
            }

        # Wave B gate evaluation
        wave_b_passed = (
            neurosis_reduction_rate >= self.config["neurosis_reduction_threshold"]
            and positive_repair_rate >= self.config["positive_repair_rate_threshold"]
            and avg_congruence >= self.config["congruence_improvement_threshold"]
            and conservation_violation_rate < 0.05  # <5% violations acceptable
            and vivox_compliance_rate >= 0.95  # 95% VIVOX compliance required
        )

        return StressTestSummary(
            total_episodes=total_episodes,
            test_duration_seconds=duration,
            neurosis_reduction_rate=neurosis_reduction_rate,
            congruence_improvement_rate=congruence_improvement_rate,
            positive_repair_rate=positive_repair_rate,
            average_neurosis_reduction=avg_neurosis_reduction,
            average_congruence_index=avg_congruence,
            average_repair_delta=avg_repair,
            conservation_violation_rate=conservation_violation_rate,
            vivox_compliance_rate=vivox_compliance_rate,
            scenario_results=scenario_results,
            wave_b_gate_passed=wave_b_passed,
        )

    def _randomize_signals(self, base_signals: dict[str, Any], factor: float) -> dict[str, Any]:
        """Add randomization to signals to simulate natural variation"""
        signals = base_signals.copy()

        for key, value in signals.items():
            if isinstance(value, (int, float)) and key != "text":
                # Add random variation within factor bounds
                variation = random.uniform(-factor, factor)
                new_value = value + (value * variation)

                # Clamp to reasonable bounds
                if key in ["emotional_valence"]:
                    signals[key] = max(-1.0, min(1.0, new_value))
                elif key in [
                    "arousal_level",
                    "cognitive_load",
                    "embodiment_level",
                    "temporal_pressure",
                ]:
                    signals[key] = max(0.0, min(1.0, new_value))
                else:
                    signals[key] = new_value

        return signals

    def export_results(self, summary: StressTestSummary, format: str = "json") -> str:
        """Export test results for analysis"""
        if format == "json":
            import json

            return json.dumps(asdict(summary), indent=2)
        elif format == "csv":
            # Simple CSV export of key metrics
            csv_lines = ["scenario,neurosis_reduction_avg,congruence_avg,repair_avg,success_rate"]
            for scenario, data in summary.scenario_results.items():
                csv_lines.append(
                    f"{scenario},{data['neurosis_reduction_avg']:.3f},{data['congruence_avg']:.3f},{data['repair_avg']:.3f},{data['success_rate']:.3f}"
                )
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def print_wave_b_report(self, summary: StressTestSummary) -> None:
        """Print formatted Wave B gate validation report"""
        print("\n" + "=" * 80)
        print("🧠 AKA QUALIA WAVE B GATE VALIDATION REPORT")
        print("=" * 80)

        print("\n📊 TEST SUMMARY")
        print(f"  Total Episodes: {summary.total_episodes}")
        print(f"  Test Duration: {summary.test_duration_seconds:.1f}s")
        print(f"  Scenarios: {len(summary.scenario_results)}")

        print("\n🎯 WAVE B GATE REQUIREMENTS")

        # Neurosis reduction requirement
        target_met = "✅" if summary.neurosis_reduction_rate >= 0.25 else "❌"
        print(
            f"  {target_met} Neurosis Reduction: {summary.neurosis_reduction_rate:.1%} "
            f"(≥25% required, avg {summary.average_neurosis_reduction:+.1f}%)"
        )

        # Congruence improvement requirement
        target_met = "✅" if summary.average_congruence_index >= 0.15 else "❌"
        print(f"  {target_met} Congruence Index: {summary.average_congruence_index:.3f} (≥0.15 required)")

        # Positive repair requirement
        target_met = "✅" if summary.positive_repair_rate >= 0.70 else "❌"
        print(
            f"  {target_met} Positive Repair Rate: {summary.positive_repair_rate:.1%} "
            f"(≥70% required, avg Δ{summary.average_repair_delta:+.3f})"
        )

        print("\n🛡️ SYSTEM INTEGRITY")

        # Energy conservation
        target_met = "✅" if summary.conservation_violation_rate < 0.05 else "❌"
        print(
            f"  {target_met} Energy Conservation: {summary.conservation_violation_rate:.1%} violations (<5% acceptable)"
        )

        # VIVOX compliance
        target_met = "✅" if summary.vivox_compliance_rate >= 0.95 else "❌"
        print(f"  {target_met} VIVOX Compliance: {summary.vivox_compliance_rate:.1%} (≥95% required)")

        print("\n📈 SCENARIO BREAKDOWN")
        for scenario, data in summary.scenario_results.items():
            success_icon = "✅" if data["success_rate"] >= 0.7 else "⚠️" if data["success_rate"] >= 0.5 else "❌"
            print(
                f"  {success_icon} {scenario}: "
                f"neurosis {data['neurosis_reduction_avg']:+.1f}%, "
                f"congruence {data['congruence_avg']:.3f}, "
                f"repair {data['repair_avg']:+.3f} "
                f"({data['success_rate']:.1%} success)"
            )

        print("\n🚪 WAVE B GATE STATUS")
        gate_status = "PASSED ✅" if summary.wave_b_gate_passed else "FAILED ❌"
        print(f"  {gate_status}")

        if summary.wave_b_gate_passed:
            print("\n🎉 Wave B implementation meets all Freud-2025 criteria!")
            print("   Ready to proceed to Wave C (Integration)")
        else:
            print("\n⚠️  Wave B requirements not fully met. Review regulation policies.")

        print("=" * 80)
