#!/usr/bin/env python3
"""
MATRIZ Canary Circuit Breaker Test - T4/0.01% Excellence
=======================================================

Tests canary deployment circuit breaker with burn-rate violation simulation.
Ensures automatic rollback triggers when error rates exceed thresholds.

Circuit Breaker Rules:
- ERROR_RATE > 5% for 3 consecutive minutes → IMMEDIATE ROLLBACK
- LATENCY_P95 > SLO + 50% for 2 minutes → IMMEDIATE ROLLBACK
- THROUGHPUT < 90% baseline for 5 minutes → GRADUAL ROLLBACK
- Any MATRIZ decision failure → FAIL_CLOSED protection

Performance Target: <100ms p95 for circuit breaker evaluation
T4/0.01% Excellence: 99.9% accurate rollback decision making

Constellation Framework: 🔥 Canary Circuit Protection
"""

import logging
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import pytest

logger = logging.getLogger(__name__)


class CanaryState(Enum):
    """Canary deployment states."""
    INITIALIZING = "initializing"
    RAMPING_UP = "ramping_up"
    STABLE = "stable"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


class RollbackTrigger(Enum):
    """Rollback trigger types."""
    ERROR_RATE_SPIKE = "error_rate_spike"
    LATENCY_BREACH = "latency_breach"
    THROUGHPUT_DROP = "throughput_drop"
    MATRIZ_DECISION_FAILURE = "matriz_decision_failure"
    MANUAL_TRIGGER = "manual_trigger"


@dataclass
class CanaryMetrics:
    """Canary deployment metrics snapshot."""
    timestamp: float
    error_rate: float  # Percentage
    latency_p95_ms: float
    throughput_rps: float  # Requests per second
    matriz_success_rate: float  # Percentage
    active_traffic_percentage: float


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    error_rate_threshold: float = 5.0  # 5%
    error_rate_duration_minutes: int = 3
    latency_multiplier_threshold: float = 1.5  # 150% of SLO
    latency_duration_minutes: int = 2
    throughput_percentage_threshold: float = 90.0  # 90% of baseline
    throughput_duration_minutes: int = 5
    matriz_failure_tolerance: float = 99.9  # 99.9% success rate required
    evaluation_interval_seconds: int = 30


class MATRIZCanaryCircuitBreaker:
    """MATRIZ-aware canary circuit breaker with burn-rate simulation."""

    def __init__(self, config: CircuitBreakerConfig):
        """Initialize circuit breaker."""
        self.config = config
        self.state = CanaryState.INITIALIZING
        self.metrics_history: list[CanaryMetrics] = []
        self.rollback_triggers: list[RollbackTrigger] = []
        self.baseline_throughput: Optional[float] = None
        self.slo_latency_p95: float = 100.0  # 100ms SLO
        self.rollback_decisions: list[dict[str, Any]] = []

    def set_baseline_metrics(self, throughput_rps: float, latency_p95_ms: float):
        """Set baseline metrics for comparison."""
        self.baseline_throughput = throughput_rps
        self.slo_latency_p95 = latency_p95_ms  # This becomes the SLO
        logger.info(f"Baseline set: {throughput_rps} RPS, {latency_p95_ms}ms P95 SLO")

    def evaluate_circuit_breaker(self, current_metrics: CanaryMetrics) -> tuple[bool, Optional[RollbackTrigger], dict[str, Any]]:
        """Evaluate if circuit breaker should trigger rollback."""
        start_time = time.perf_counter()

        # Add current metrics to history
        self.metrics_history.append(current_metrics)

        # Keep only relevant history (last 10 minutes)
        cutoff_time = current_metrics.timestamp - (10 * 60)
        self.metrics_history = [m for m in self.metrics_history if m.timestamp >= cutoff_time]

        # Evaluation logic
        rollback_needed = False
        trigger = None
        evaluation_details = {
            "timestamp": current_metrics.timestamp,
            "evaluations": {},
            "decision": "CONTINUE"
        }

        # 1. Error Rate Evaluation
        error_rate_trigger = self._evaluate_error_rate(current_metrics)
        evaluation_details["evaluations"]["error_rate"] = error_rate_trigger
        if error_rate_trigger["trigger_rollback"]:
            rollback_needed = True
            trigger = RollbackTrigger.ERROR_RATE_SPIKE

        # 2. Latency Evaluation
        latency_trigger = self._evaluate_latency(current_metrics)
        evaluation_details["evaluations"]["latency"] = latency_trigger
        if not rollback_needed and latency_trigger["trigger_rollback"]:
            rollback_needed = True
            trigger = RollbackTrigger.LATENCY_BREACH

        # 3. Throughput Evaluation
        throughput_trigger = self._evaluate_throughput(current_metrics)
        evaluation_details["evaluations"]["throughput"] = throughput_trigger
        if not rollback_needed and throughput_trigger["trigger_rollback"]:
            rollback_needed = True
            trigger = RollbackTrigger.THROUGHPUT_DROP

        # 4. MATRIZ Decision Evaluation
        matriz_trigger = self._evaluate_matriz_health(current_metrics)
        evaluation_details["evaluations"]["matriz"] = matriz_trigger
        if not rollback_needed and matriz_trigger["trigger_rollback"]:
            rollback_needed = True
            trigger = RollbackTrigger.MATRIZ_DECISION_FAILURE

        # Record decision
        evaluation_time = (time.perf_counter() - start_time) * 1000
        evaluation_details["evaluation_time_ms"] = evaluation_time
        evaluation_details["decision"] = "ROLLBACK" if rollback_needed else "CONTINUE"
        evaluation_details["trigger"] = trigger.value if trigger else None

        if rollback_needed:
            # Get the appropriate evaluation based on trigger type
            if trigger == RollbackTrigger.ERROR_RATE_SPIKE:
                trigger_eval = evaluation_details['evaluations']['error_rate']
            elif trigger == RollbackTrigger.LATENCY_BREACH:
                trigger_eval = evaluation_details['evaluations']['latency']
            elif trigger == RollbackTrigger.THROUGHPUT_DROP:
                trigger_eval = evaluation_details['evaluations']['throughput']
            elif trigger == RollbackTrigger.MATRIZ_DECISION_FAILURE:
                trigger_eval = evaluation_details['evaluations']['matriz']
            else:
                trigger_eval = {"reason": "Unknown trigger"}

            evaluation_details["rollback_reason"] = f"{trigger.value}: {trigger_eval['reason']}"
            self.rollback_triggers.append(trigger)

        self.rollback_decisions.append(evaluation_details)
        return rollback_needed, trigger, evaluation_details

    def _evaluate_error_rate(self, metrics: CanaryMetrics) -> dict[str, Any]:
        """Evaluate error rate breach."""
        duration_cutoff = metrics.timestamp - (self.config.error_rate_duration_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= duration_cutoff]

        if len(recent_metrics) < 3:  # Need at least 3 data points
            return {
                "trigger_rollback": False,
                "reason": "Insufficient data points",
                "current_error_rate": metrics.error_rate,
                "threshold": self.config.error_rate_threshold,
                "data_points": len(recent_metrics)
            }

        avg_error_rate = statistics.mean([m.error_rate for m in recent_metrics])
        sustained_breach = all(m.error_rate > self.config.error_rate_threshold for m in recent_metrics[-3:])

        return {
            "trigger_rollback": sustained_breach,
            "reason": f"Error rate {avg_error_rate:.1f}% > {self.config.error_rate_threshold}% for {len(recent_metrics)} intervals",
            "current_error_rate": metrics.error_rate,
            "avg_error_rate": avg_error_rate,
            "threshold": self.config.error_rate_threshold,
            "sustained_breach": sustained_breach
        }

    def _evaluate_latency(self, metrics: CanaryMetrics) -> dict[str, Any]:
        """Evaluate latency breach."""
        latency_threshold = self.slo_latency_p95 * self.config.latency_multiplier_threshold
        duration_cutoff = metrics.timestamp - (self.config.latency_duration_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= duration_cutoff]

        if len(recent_metrics) < 2:
            return {
                "trigger_rollback": False,
                "reason": "Insufficient data points for latency evaluation",
                "current_latency_p95": metrics.latency_p95_ms,
                "threshold": latency_threshold,
                "data_points": len(recent_metrics)
            }

        avg_latency = statistics.mean([m.latency_p95_ms for m in recent_metrics])
        sustained_breach = all(m.latency_p95_ms > latency_threshold for m in recent_metrics) and len(recent_metrics) >= 2

        return {
            "trigger_rollback": sustained_breach,
            "reason": f"Latency P95 {avg_latency:.1f}ms > {latency_threshold:.1f}ms for {len(recent_metrics)} intervals",
            "current_latency_p95": metrics.latency_p95_ms,
            "avg_latency": avg_latency,
            "threshold": latency_threshold,
            "sustained_breach": sustained_breach
        }

    def _evaluate_throughput(self, metrics: CanaryMetrics) -> dict[str, Any]:
        """Evaluate throughput drop."""
        if not self.baseline_throughput:
            return {
                "trigger_rollback": False,
                "reason": "No baseline throughput set",
                "current_throughput": metrics.throughput_rps
            }

        throughput_threshold = self.baseline_throughput * (self.config.throughput_percentage_threshold / 100.0)
        duration_cutoff = metrics.timestamp - (self.config.throughput_duration_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= duration_cutoff]

        if len(recent_metrics) < 5:
            return {
                "trigger_rollback": False,
                "reason": "Insufficient data points for throughput evaluation",
                "current_throughput": metrics.throughput_rps,
                "threshold": throughput_threshold,
                "data_points": len(recent_metrics)
            }

        avg_throughput = statistics.mean([m.throughput_rps for m in recent_metrics])
        sustained_drop = all(m.throughput_rps < throughput_threshold for m in recent_metrics) and len(recent_metrics) >= 5

        return {
            "trigger_rollback": sustained_drop,
            "reason": f"Throughput {avg_throughput:.1f} RPS < {throughput_threshold:.1f} RPS ({self.config.throughput_percentage_threshold}% of baseline)",
            "current_throughput": metrics.throughput_rps,
            "avg_throughput": avg_throughput,
            "baseline_throughput": self.baseline_throughput,
            "threshold": throughput_threshold,
            "sustained_drop": sustained_drop
        }

    def _evaluate_matriz_health(self, metrics: CanaryMetrics) -> dict[str, Any]:
        """Evaluate MATRIZ decision health."""
        matriz_threshold = self.config.matriz_failure_tolerance

        # Immediate failure if MATRIZ success rate drops below threshold
        trigger_rollback = metrics.matriz_success_rate < matriz_threshold

        return {
            "trigger_rollback": trigger_rollback,
            "reason": f"MATRIZ success rate {metrics.matriz_success_rate:.2f}% < {matriz_threshold}% (FAIL_CLOSED)",
            "current_success_rate": metrics.matriz_success_rate,
            "threshold": matriz_threshold,
            "fail_closed_triggered": trigger_rollback
        }

    def simulate_burn_rate_scenario(self, scenario_name: str, metrics_sequence: list[CanaryMetrics]) -> dict[str, Any]:
        """Simulate a burn-rate scenario and track rollback decision."""
        logger.info(f"Simulating burn-rate scenario: {scenario_name}")

        scenario_results = {
            "scenario_name": scenario_name,
            "total_metrics": len(metrics_sequence),
            "rollback_triggered": False,
            "rollback_trigger": None,
            "rollback_time": None,
            "evaluation_decisions": [],
            "performance_metrics": []
        }

        for i, metrics in enumerate(metrics_sequence):
            start_time = time.perf_counter()

            rollback_needed, trigger, evaluation = self.evaluate_circuit_breaker(metrics)

            eval_time = (time.perf_counter() - start_time) * 1000
            scenario_results["performance_metrics"].append(eval_time)
            scenario_results["evaluation_decisions"].append(evaluation)

            if rollback_needed and not scenario_results["rollback_triggered"]:
                scenario_results["rollback_triggered"] = True
                scenario_results["rollback_trigger"] = trigger
                scenario_results["rollback_time"] = metrics.timestamp
                logger.info(f"Rollback triggered at step {i+1}: {trigger.value}")
                break

            logger.debug(f"Step {i+1}: {evaluation['decision']} (eval: {eval_time:.1f}ms)")

        # Performance analysis
        if scenario_results["performance_metrics"]:
            scenario_results["mean_eval_time_ms"] = statistics.mean(scenario_results["performance_metrics"])
            scenario_results["p95_eval_time_ms"] = sorted(scenario_results["performance_metrics"])[int(len(scenario_results["performance_metrics"]) * 0.95)]
            scenario_results["max_eval_time_ms"] = max(scenario_results["performance_metrics"])

        return scenario_results


@pytest.mark.deployment
@pytest.mark.canary_circuit
class TestMATRIZCanaryCircuitBreaker:
    """MATRIZ canary circuit breaker tests."""

    def test_error_rate_burn_simulation(self):
        """Test error rate burn-rate scenario triggers rollback."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        # Set baseline
        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        # Create burn-rate scenario: gradual error rate increase
        base_time = time.time()
        metrics_sequence = []

        # Normal operation (2 minutes)
        for i in range(4):
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (i * 30),
                error_rate=1.5,  # Normal error rate
                latency_p95_ms=87.0,
                throughput_rps=1020.0,
                matriz_success_rate=99.98,
                active_traffic_percentage=20.0
            ))

        # Error rate spike (sustained for 3+ minutes)
        for i in range(6):  # 3 minutes of high error rate
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (120 + i * 30),  # After 2 minutes
                error_rate=8.5,  # Above 5% threshold
                latency_p95_ms=89.0,
                throughput_rps=980.0,
                matriz_success_rate=99.95,
                active_traffic_percentage=25.0
            ))

        # Run simulation
        results = circuit_breaker.simulate_burn_rate_scenario("Error Rate Spike", metrics_sequence)

        # Assertions
        assert results["rollback_triggered"], "Error rate burn should trigger rollback"
        assert results["rollback_trigger"] == RollbackTrigger.ERROR_RATE_SPIKE, "Should trigger due to error rate"
        assert results["p95_eval_time_ms"] < 100.0, f"Evaluation time {results['p95_eval_time_ms']:.1f}ms exceeds 100ms target"

        # Should trigger after 3 sustained intervals of high error rate
        rollback_step = next(i for i, decision in enumerate(results["evaluation_decisions"]) if decision["decision"] == "ROLLBACK")
        assert rollback_step >= 6, "Should wait for sustained error rate before triggering"  # 4 normal + at least 3 high error rate

        logger.info(f"✅ Error rate burn simulation passed - triggered at step {rollback_step + 1}")

    def test_latency_breach_simulation(self):
        """Test latency breach scenario triggers rollback."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        # Set baseline (SLO: 100ms)
        circuit_breaker.set_baseline_metrics(1000.0, 100.0)

        base_time = time.time()
        metrics_sequence = []

        # Normal latency (1 minute)
        for i in range(2):
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (i * 30),
                error_rate=2.0,
                latency_p95_ms=95.0,  # Under SLO
                throughput_rps=1010.0,
                matriz_success_rate=99.97,
                active_traffic_percentage=15.0
            ))

        # Latency breach (sustained for 2+ minutes)
        for i in range(4):  # 2 minutes of high latency
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (60 + i * 30),
                error_rate=3.0,
                latency_p95_ms=155.0,  # 155ms > 150ms (100ms * 1.5)
                throughput_rps=995.0,
                matriz_success_rate=99.94,
                active_traffic_percentage=20.0
            ))

        results = circuit_breaker.simulate_burn_rate_scenario("Latency Breach", metrics_sequence)

        assert results["rollback_triggered"], "Latency breach should trigger rollback"
        assert results["rollback_trigger"] == RollbackTrigger.LATENCY_BREACH, "Should trigger due to latency"
        assert results["p95_eval_time_ms"] < 100.0, "Evaluation performance target not met"

        logger.info("✅ Latency breach simulation passed")

    def test_throughput_drop_simulation(self):
        """Test throughput drop scenario triggers rollback."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        # Set baseline
        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        base_time = time.time()
        metrics_sequence = []

        # Normal throughput (2 minutes)
        for i in range(4):
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (i * 30),
                error_rate=2.5,
                latency_p95_ms=88.0,
                throughput_rps=1050.0,  # Above baseline
                matriz_success_rate=99.96,
                active_traffic_percentage=10.0
            ))

        # Throughput drop (sustained for 5+ minutes)
        for i in range(10):  # 5 minutes of low throughput
            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (120 + i * 30),
                error_rate=3.0,
                latency_p95_ms=92.0,
                throughput_rps=850.0,  # 85% of baseline (< 90% threshold)
                matriz_success_rate=99.93,
                active_traffic_percentage=30.0
            ))

        results = circuit_breaker.simulate_burn_rate_scenario("Throughput Drop", metrics_sequence)

        assert results["rollback_triggered"], "Throughput drop should trigger rollback"
        assert results["rollback_trigger"] == RollbackTrigger.THROUGHPUT_DROP, "Should trigger due to throughput"

        logger.info("✅ Throughput drop simulation passed")

    def test_matriz_decision_failure_simulation(self):
        """Test MATRIZ decision failure triggers immediate fail-closed rollback."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        base_time = time.time()

        # Single metric with MATRIZ failure should trigger immediate rollback
        failed_metrics = CanaryMetrics(
            timestamp=base_time,
            error_rate=1.0,  # Low error rate
            latency_p95_ms=80.0,  # Good latency
            throughput_rps=1100.0,  # Good throughput
            matriz_success_rate=99.5,  # Below 99.9% threshold → FAIL_CLOSED
            active_traffic_percentage=5.0
        )

        results = circuit_breaker.simulate_burn_rate_scenario("MATRIZ Failure", [failed_metrics])

        assert results["rollback_triggered"], "MATRIZ failure should trigger immediate rollback"
        assert results["rollback_trigger"] == RollbackTrigger.MATRIZ_DECISION_FAILURE, "Should trigger due to MATRIZ failure"
        assert len(results["evaluation_decisions"]) == 1, "Should trigger on first evaluation"

        # Check fail-closed behavior
        evaluation = results["evaluation_decisions"][0]
        assert evaluation["evaluations"]["matriz"]["fail_closed_triggered"], "Fail-closed should be triggered"

        logger.info("✅ MATRIZ fail-closed simulation passed")

    def test_no_false_positive_rollbacks(self):
        """Test that normal operations don't trigger false positive rollbacks."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        base_time = time.time()
        metrics_sequence = []

        # 10 minutes of normal operation with minor variations
        for i in range(20):
            # Add realistic variations
            error_variation = 1.0 + (i % 3) * 0.5  # 1.0-2.0%
            latency_variation = 85.0 + (i % 4) * 3  # 85-97ms
            throughput_variation = 1000.0 + (i % 5) * 20  # 1000-1080 RPS

            metrics_sequence.append(CanaryMetrics(
                timestamp=base_time + (i * 30),
                error_rate=error_variation,
                latency_p95_ms=latency_variation,
                throughput_rps=throughput_variation,
                matriz_success_rate=99.95 + (i % 3) * 0.02,  # 99.95-99.99%
                active_traffic_percentage=5.0 + (i * 2.5)  # Gradual ramp-up
            ))

        results = circuit_breaker.simulate_burn_rate_scenario("Normal Operations", metrics_sequence)

        assert not results["rollback_triggered"], "Normal operations should not trigger rollback"
        assert all(decision["decision"] == "CONTINUE" for decision in results["evaluation_decisions"]), "All decisions should be CONTINUE"
        assert results["p95_eval_time_ms"] < 100.0, "Performance target not met for normal operations"

        logger.info(f"✅ No false positive test passed - {len(metrics_sequence)} evaluations, no rollbacks")

    def test_circuit_breaker_performance_targets(self):
        """Test circuit breaker meets T4/0.01% performance targets."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        # Generate large number of evaluation scenarios
        base_time = time.time()
        evaluation_times = []

        for i in range(1000):  # 1000 evaluations
            metrics = CanaryMetrics(
                timestamp=base_time + (i * 30),
                error_rate=2.0 + (i % 10) * 0.5,
                latency_p95_ms=85.0 + (i % 8) * 4,
                throughput_rps=1000.0 + (i % 12) * 25,
                matriz_success_rate=99.9 + (i % 5) * 0.02,
                active_traffic_percentage=min(100.0, i * 0.1)
            )

            start_time = time.perf_counter()
            _rollback_needed, _trigger, _evaluation = circuit_breaker.evaluate_circuit_breaker(metrics)
            eval_time = (time.perf_counter() - start_time) * 1000

            evaluation_times.append(eval_time)

        # Performance analysis
        mean_time = statistics.mean(evaluation_times)
        p95_time = sorted(evaluation_times)[int(len(evaluation_times) * 0.95)]
        p99_time = sorted(evaluation_times)[int(len(evaluation_times) * 0.99)]
        max_time = max(evaluation_times)

        # T4/0.01% performance requirements
        assert mean_time < 50.0, f"Mean evaluation time {mean_time:.2f}ms exceeds 50ms target"
        assert p95_time < 100.0, f"P95 evaluation time {p95_time:.2f}ms exceeds 100ms target"
        assert p99_time < 150.0, f"P99 evaluation time {p99_time:.2f}ms exceeds 150ms target"

        logger.info("✅ Performance targets met:")
        logger.info(f"   Mean: {mean_time:.2f}ms")
        logger.info(f"   P95:  {p95_time:.2f}ms")
        logger.info(f"   P99:  {p99_time:.2f}ms")
        logger.info(f"   Max:  {max_time:.2f}ms")

    def test_comprehensive_burn_rate_scenarios(self):
        """Comprehensive test covering multiple burn-rate scenarios."""
        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)

        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        # Test scenarios with expected outcomes
        test_scenarios = [
            {
                "name": "Gradual Error Rate Increase",
                "expected_trigger": RollbackTrigger.ERROR_RATE_SPIKE,
                "should_trigger": True
            },
            {
                "name": "Sudden Latency Spike",
                "expected_trigger": RollbackTrigger.LATENCY_BREACH,
                "should_trigger": True
            },
            {
                "name": "Traffic Drop",
                "expected_trigger": RollbackTrigger.THROUGHPUT_DROP,
                "should_trigger": True
            },
            {
                "name": "MATRIZ Health Issue",
                "expected_trigger": RollbackTrigger.MATRIZ_DECISION_FAILURE,
                "should_trigger": True
            },
            {
                "name": "Normal Variation",
                "expected_trigger": None,
                "should_trigger": False
            }
        ]

        passed_scenarios = 0

        for scenario_config in test_scenarios:
            scenario_name = scenario_config["name"]

            # Generate appropriate metrics for scenario
            metrics_sequence = self._generate_scenario_metrics(scenario_name)

            # Run simulation
            results = circuit_breaker.simulate_burn_rate_scenario(scenario_name, metrics_sequence)

            # Validate results
            should_trigger = scenario_config["should_trigger"]
            expected_trigger = scenario_config["expected_trigger"]

            if should_trigger:
                assert results["rollback_triggered"], f"Scenario '{scenario_name}' should trigger rollback"
                assert results["rollback_trigger"] == expected_trigger, f"Scenario '{scenario_name}' should trigger due to {expected_trigger}"
                passed_scenarios += 1
            else:
                assert not results["rollback_triggered"], f"Scenario '{scenario_name}' should not trigger rollback"
                passed_scenarios += 1

            logger.info(f"✓ Scenario '{scenario_name}': {'ROLLBACK' if results['rollback_triggered'] else 'CONTINUE'}")

        # Assert all scenarios passed
        assert passed_scenarios == len(test_scenarios), f"Only {passed_scenarios}/{len(test_scenarios)} scenarios passed"

        logger.info(f"✅ Comprehensive burn-rate scenarios: {passed_scenarios}/{len(test_scenarios)} passed")

    def _generate_scenario_metrics(self, scenario_name: str) -> list[CanaryMetrics]:
        """Generate metrics sequence for specific scenario."""
        base_time = time.time()
        metrics = []

        if scenario_name == "Gradual Error Rate Increase":
            # Start normal, gradually increase error rate
            for i in range(8):
                error_rate = 1.0 + (i * 1.2) if i >= 4 else 2.0  # Spike after 4 intervals
                metrics.append(CanaryMetrics(
                    timestamp=base_time + (i * 30),
                    error_rate=error_rate,
                    latency_p95_ms=87.0,
                    throughput_rps=1010.0,
                    matriz_success_rate=99.96,
                    active_traffic_percentage=10.0 + i * 5
                ))

        elif scenario_name == "Sudden Latency Spike":
            for i in range(6):
                latency = 160.0 if i >= 2 else 88.0  # Spike after 2 intervals
                metrics.append(CanaryMetrics(
                    timestamp=base_time + (i * 30),
                    error_rate=2.0,
                    latency_p95_ms=latency,
                    throughput_rps=990.0,
                    matriz_success_rate=99.94,
                    active_traffic_percentage=15.0
                ))

        elif scenario_name == "Traffic Drop":
            for i in range(12):
                throughput = 800.0 if i >= 4 else 1020.0  # Drop after 4 intervals
                metrics.append(CanaryMetrics(
                    timestamp=base_time + (i * 30),
                    error_rate=2.5,
                    latency_p95_ms=89.0,
                    throughput_rps=throughput,
                    matriz_success_rate=99.92,
                    active_traffic_percentage=25.0
                ))

        elif scenario_name == "MATRIZ Health Issue":
            metrics.append(CanaryMetrics(
                timestamp=base_time,
                error_rate=1.5,
                latency_p95_ms=82.0,
                throughput_rps=1050.0,
                matriz_success_rate=99.7,  # Below threshold
                active_traffic_percentage=5.0
            ))

        elif scenario_name == "Normal Variation":
            for i in range(10):
                metrics.append(CanaryMetrics(
                    timestamp=base_time + (i * 30),
                    error_rate=1.5 + (i % 3) * 0.3,
                    latency_p95_ms=85.0 + (i % 4) * 2,
                    throughput_rps=1000.0 + (i % 5) * 15,
                    matriz_success_rate=99.95 + (i % 2) * 0.03,
                    active_traffic_percentage=5.0 + i * 3
                ))

        return metrics


if __name__ == "__main__":
    # Run circuit breaker validation standalone
    def run_circuit_breaker_validation():
        print("🔥 MATRIZ Canary Circuit Breaker Validation")
        print("=" * 60)

        config = CircuitBreakerConfig()
        circuit_breaker = MATRIZCanaryCircuitBreaker(config)
        circuit_breaker.set_baseline_metrics(1000.0, 85.0)

        test_scenarios = [
            ("Error Rate Spike", RollbackTrigger.ERROR_RATE_SPIKE, True),
            ("Latency Breach", RollbackTrigger.LATENCY_BREACH, True),
            ("Throughput Drop", RollbackTrigger.THROUGHPUT_DROP, True),
            ("MATRIZ Failure", RollbackTrigger.MATRIZ_DECISION_FAILURE, True),
            ("Normal Operations", None, False)
        ]

        passed_tests = 0

        for scenario_name, expected_trigger, should_trigger in test_scenarios:
            print(f"\nTesting: {scenario_name}")

            # Reset circuit breaker for each scenario
            circuit_breaker = MATRIZCanaryCircuitBreaker(config)
            circuit_breaker.set_baseline_metrics(1000.0, 85.0)

            # Generate test metrics based on scenario
            if scenario_name == "Error Rate Spike":
                metrics = [CanaryMetrics(
                    timestamp=time.time() + i * 30,
                    error_rate=7.0,  # Above threshold
                    latency_p95_ms=88.0,
                    throughput_rps=1020.0,
                    matriz_success_rate=99.96,
                    active_traffic_percentage=20.0
                ) for i in range(6)]

            elif scenario_name == "Latency Breach":
                # Need sustained latency breach for 2 minutes (4 intervals)
                # Threshold will be 85ms * 1.5 = 127.5ms, so use 140ms
                metrics = [CanaryMetrics(
                    timestamp=time.time() + i * 30,
                    error_rate=2.0,  # Keep below 5% threshold
                    latency_p95_ms=140.0,  # Above 127.5ms threshold (85ms * 1.5)
                    throughput_rps=1010.0,
                    matriz_success_rate=99.97,
                    active_traffic_percentage=10.0
                ) for i in range(4)]

            elif scenario_name == "Throughput Drop":
                # Need sustained throughput drop for 5 minutes (10 intervals)
                metrics = [CanaryMetrics(
                    timestamp=time.time() + i * 30,
                    error_rate=2.0,
                    latency_p95_ms=87.0,
                    throughput_rps=850.0,  # Below 900 threshold (1000 * 0.9)
                    matriz_success_rate=99.97,
                    active_traffic_percentage=10.0
                ) for i in range(10)]

            elif scenario_name == "MATRIZ Failure":
                metrics = [CanaryMetrics(
                    timestamp=time.time(),
                    error_rate=1.0,
                    latency_p95_ms=80.0,
                    throughput_rps=1100.0,
                    matriz_success_rate=99.5,  # Below threshold
                    active_traffic_percentage=5.0
                )]
            else:
                # Normal operations - should not trigger
                metrics = [CanaryMetrics(
                    timestamp=time.time() + i * 30,
                    error_rate=2.0,
                    latency_p95_ms=87.0,
                    throughput_rps=1010.0,
                    matriz_success_rate=99.97,
                    active_traffic_percentage=10.0
                ) for i in range(3)]

            results = circuit_breaker.simulate_burn_rate_scenario(scenario_name, metrics)

            # Debug output
            if should_trigger and not results["rollback_triggered"]:
                print(f"   DEBUG - Last evaluation: {results['evaluation_decisions'][-1] if results['evaluation_decisions'] else 'None'}")

            if should_trigger:
                if results["rollback_triggered"] and results["rollback_trigger"] == expected_trigger:
                    print(f"   ✅ PASS - Correctly triggered {expected_trigger.value}")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAIL - Expected {expected_trigger.value}, got {results.get('rollback_trigger')}")
            else:
                if not results["rollback_triggered"]:
                    print("   ✅ PASS - Correctly did not trigger rollback")
                    passed_tests += 1
                else:
                    print("   ❌ FAIL - Unexpected rollback triggered")

        print(f"\n{'='*60}")
        if passed_tests == len(test_scenarios):
            print(f"🎯 Circuit Breaker Validation: ✅ {passed_tests}/{len(test_scenarios)} PASSED")
            print("   T4/0.01% excellence achieved for canary protection")
            return True
        else:
            print(f"❌ Circuit Breaker Validation: {passed_tests}/{len(test_scenarios)} passed")
            return False

    import sys
    success = run_circuit_breaker_validation()
    sys.exit(0 if success else 1)
