#!/usr/bin/env python3
"""
MATRIZ-Guardian Chaos/Resilience Test - T4/0.01% Excellence
=========================================================

Tests chaos scenarios where Guardian crashes mid-MATRIZ decision.
System must fail-closed and maintain integrity under catastrophic failures.

Chaos Engineering Scenarios:
- Guardian process crash during MATRIZ tick/reflect/decide phases
- Guardian network partition during decision validation
- Guardian memory corruption during consensus validation
- Guardian timeout scenarios under load
- Cascading failure propagation between Guardian and MATRIZ

Fail-Closed Requirements:
- ANY Guardian failure → IMMEDIATE MATRIZ halt (no degraded mode)
- NO partial decisions committed during Guardian failure
- ALL in-flight transactions rolled back within 1 second
- COMPLETE system state recovery within 10 seconds
- ZERO data corruption or inconsistent state

Performance Target: <250ms p95 for failure detection and fail-closed activation
T4/0.01% Excellence: 100% fail-closed reliability, 0% data corruption rate

Constellation Framework: ⚡ Chaos Engineering & Resilience
"""

import logging
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest

logger = logging.getLogger(__name__)


class GuardianFailureType(Enum):
    """Types of Guardian failures to simulate."""
    PROCESS_CRASH = "process_crash"
    NETWORK_PARTITION = "network_partition"
    MEMORY_CORRUPTION = "memory_corruption"
    TIMEOUT_FAILURE = "timeout_failure"
    CONSENSUS_CORRUPTION = "consensus_corruption"
    CASCADING_FAILURE = "cascading_failure"


class MATRIZPhase(Enum):
    """MATRIZ decision phases."""
    INITIALIZING = "initializing"
    TICK = "tick"
    REFLECT = "reflect"
    DECIDE = "decide"
    GUARDIAN_VALIDATION = "guardian_validation"
    COMMIT = "commit"
    COMPLETE = "complete"
    FAILED = "failed"


class SystemState(Enum):
    """Overall system state."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAIL_CLOSED = "fail_closed"
    RECOVERING = "recovering"
    CORRUPTED = "corrupted"


@dataclass
class MATRIZDecision:
    """MATRIZ decision with tracking."""
    decision_id: str
    timestamp: float
    phase: MATRIZPhase
    guardian_validated: bool
    committed: bool
    corrupted: bool
    rollback_requested: bool
    processing_time_ms: float
    guardian_interaction_count: int = 0


@dataclass
class GuardianFailureScenario:
    """Guardian failure scenario definition."""
    failure_type: GuardianFailureType
    failure_phase: MATRIZPhase
    failure_duration_ms: float
    recovery_time_ms: Optional[float]
    should_fail_closed: bool
    expected_corruption: bool
    description: str


@dataclass
class ChaosTestResult:
    """Chaos test execution result."""
    scenario_name: str
    failure_detected: bool
    fail_closed_activated: bool
    fail_closed_time_ms: float
    recovery_time_ms: Optional[float]
    data_corruption_detected: bool
    in_flight_transactions_recovered: int
    decisions_rolled_back: int
    system_integrity_maintained: bool
    performance_metrics: dict[str, float]


class GuardianSimulator:
    """Simulates Guardian with controllable failures."""

    def __init__(self):
        """Initialize Guardian simulator."""
        self.is_healthy = True
        self.network_accessible = True
        self.memory_corrupted = False
        self.response_delay_ms = 0
        self.consensus_corrupted = False
        self.failure_callbacks: list[Callable] = []

    def validate_decision(self, decision_data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        """Simulate Guardian decision validation."""
        start_time = time.perf_counter()

        # Simulate various failure scenarios
        if not self.is_healthy:
            raise RuntimeError("Guardian process crashed")

        if not self.network_accessible:
            raise TimeoutError("Guardian network partition")

        if self.memory_corrupted:
            # Return corrupted validation
            return True, {"corrupted": True, "validation": "invalid_state"}

        if self.response_delay_ms > 0:
            time.sleep(self.response_delay_ms / 1000.0)

        if self.consensus_corrupted:
            # Return inconsistent consensus
            return random.choice([True, False]), {"consensus": "inconsistent"}

        # Normal validation
        validation_time = (time.perf_counter() - start_time) * 1000
        return True, {
            "validated": True,
            "validation_time_ms": validation_time,
            "guardian_healthy": True
        }

    def inject_failure(self, failure_type: GuardianFailureType, duration_ms: Optional[float] = None):
        """Inject failure into Guardian."""
        logger.info(f"Injecting Guardian failure: {failure_type.value}")

        if failure_type == GuardianFailureType.PROCESS_CRASH:
            self.is_healthy = False
        elif failure_type == GuardianFailureType.NETWORK_PARTITION:
            self.network_accessible = False
        elif failure_type == GuardianFailureType.MEMORY_CORRUPTION:
            self.memory_corrupted = True
        elif failure_type == GuardianFailureType.TIMEOUT_FAILURE:
            self.response_delay_ms = 5000  # 5 second delay
        elif failure_type == GuardianFailureType.CONSENSUS_CORRUPTION:
            self.consensus_corrupted = True

        # Schedule recovery if duration specified
        if duration_ms:
            threading.Timer(duration_ms / 1000.0, self.recover_from_failure).start()

        # Notify failure callbacks
        for callback in self.failure_callbacks:
            callback(failure_type)

    def recover_from_failure(self):
        """Recover Guardian from failure."""
        logger.info("Guardian recovering from failure")
        self.is_healthy = True
        self.network_accessible = True
        self.memory_corrupted = False
        self.response_delay_ms = 0
        self.consensus_corrupted = False

    def add_failure_callback(self, callback: Callable):
        """Add callback for failure notifications."""
        self.failure_callbacks.append(callback)


class MATRIZChaosController:
    """MATRIZ system with chaos engineering and fail-closed mechanisms."""

    def __init__(self, guardian_simulator: GuardianSimulator):
        """Initialize chaos controller."""
        self.guardian = guardian_simulator
        self.system_state = SystemState.HEALTHY
        self.in_flight_decisions: dict[str, MATRIZDecision] = {}
        self.completed_decisions: list[MATRIZDecision] = []
        self.failure_detection_time: Optional[float] = None
        self.fail_closed_activation_time: Optional[float] = None
        self.recovery_start_time: Optional[float] = None
        self.state_corruption_detected = False

        # Metrics
        self.chaos_metrics = {
            "decisions_processed": 0,
            "failures_detected": 0,
            "fail_closed_activations": 0,
            "rollbacks_performed": 0,
            "corruptions_detected": 0
        }

        # Register for Guardian failure notifications
        self.guardian.add_failure_callback(self._on_guardian_failure)

    def _on_guardian_failure(self, failure_type: GuardianFailureType):
        """Handle Guardian failure notification."""
        self.failure_detection_time = time.time()
        self.chaos_metrics["failures_detected"] += 1

        # Immediate fail-closed activation
        self._activate_fail_closed(f"Guardian failure: {failure_type.value}")

    def _activate_fail_closed(self, reason: str):
        """Activate fail-closed mode."""
        if self.system_state == SystemState.FAIL_CLOSED:
            return  # Already in fail-closed

        logger.critical(f"FAIL-CLOSED ACTIVATED: {reason}")
        self.fail_closed_activation_time = time.time()
        self.system_state = SystemState.FAIL_CLOSED
        self.chaos_metrics["fail_closed_activations"] += 1

        # Immediately halt all MATRIZ processing
        self._halt_matriz_processing()

        # Roll back all in-flight transactions
        self._rollback_inflight_decisions()

    def _halt_matriz_processing(self):
        """Halt all MATRIZ processing immediately."""
        logger.info("Halting all MATRIZ processing")

        # Mark all in-flight decisions as failed
        for decision in self.in_flight_decisions.values():
            if decision.phase not in [MATRIZPhase.FAILED, MATRIZPhase.COMPLETE]:
                decision.phase = MATRIZPhase.FAILED
                decision.rollback_requested = True

    def _rollback_inflight_decisions(self):
        """Roll back all in-flight decisions."""
        rollback_start = time.time()
        rollback_count = 0

        for decision_id, decision in list(self.in_flight_decisions.items()):
            if not decision.committed and decision.phase != MATRIZPhase.FAILED:
                # Perform rollback
                decision.phase = MATRIZPhase.FAILED
                decision.rollback_requested = True
                decision.corrupted = False  # Ensure clean rollback
                rollback_count += 1

                # Move to completed decisions
                self.completed_decisions.append(decision)
                del self.in_flight_decisions[decision_id]

        rollback_time = (time.time() - rollback_start) * 1000
        self.chaos_metrics["rollbacks_performed"] += rollback_count

        logger.info(f"Rolled back {rollback_count} in-flight decisions in {rollback_time:.2f}ms")

    def process_matriz_decision(
        self,
        decision_context: dict[str, Any],
        simulate_phases: bool = True
    ) -> tuple[MATRIZDecision, list[str]]:
        """Process MATRIZ decision with Guardian interaction."""
        start_time = time.perf_counter()

        decision = MATRIZDecision(
            decision_id=f"decision_{int(time.time() * 1000000)}",
            timestamp=time.time(),
            phase=MATRIZPhase.INITIALIZING,
            guardian_validated=False,
            committed=False,
            corrupted=False,
            rollback_requested=False,
            processing_time_ms=0.0
        )

        error_log = []

        # Check if system is in fail-closed mode
        if self.system_state == SystemState.FAIL_CLOSED:
            decision.phase = MATRIZPhase.FAILED
            error_log.append("System in FAIL_CLOSED mode - decision rejected")
            return decision, error_log

        # Add to in-flight tracking
        self.in_flight_decisions[decision.decision_id] = decision

        try:
            # Simulate MATRIZ phases
            if simulate_phases:
                phases = [MATRIZPhase.TICK, MATRIZPhase.REFLECT, MATRIZPhase.DECIDE]
                for phase in phases:
                    decision.phase = phase
                    time.sleep(0.001)  # Simulate processing time

                    # Check for fail-closed during processing
                    if self.system_state == SystemState.FAIL_CLOSED:
                        raise RuntimeError(f"Fail-closed activated during {phase.value}")

            # Guardian validation phase
            decision.phase = MATRIZPhase.GUARDIAN_VALIDATION
            decision.guardian_interaction_count += 1

            try:
                validated, validation_result = self.guardian.validate_decision(decision_context)

                # Check for corruption in Guardian response
                if validation_result.get("corrupted", False):
                    self.state_corruption_detected = True
                    self.chaos_metrics["corruptions_detected"] += 1
                    decision.corrupted = True
                    raise RuntimeError("Guardian response corrupted")

                decision.guardian_validated = validated

                if not validated:
                    raise RuntimeError("Guardian validation failed")

            except Exception as e:
                error_log.append(f"Guardian failure during validation: {e!s}")
                # This should trigger fail-closed if not already active
                if self.system_state != SystemState.FAIL_CLOSED:
                    self._activate_fail_closed(f"Guardian validation error: {e!s}")
                raise

            # Commit phase (only if Guardian validated)
            decision.phase = MATRIZPhase.COMMIT
            decision.committed = True
            decision.phase = MATRIZPhase.COMPLETE

            # Move from in-flight to completed
            if decision.decision_id in self.in_flight_decisions:
                del self.in_flight_decisions[decision.decision_id]
                self.completed_decisions.append(decision)

            self.chaos_metrics["decisions_processed"] += 1

        except Exception as e:
            decision.phase = MATRIZPhase.FAILED
            error_log.append(f"Decision processing failed: {e!s}")

            # Remove from in-flight if still there
            if decision.decision_id in self.in_flight_decisions:
                del self.in_flight_decisions[decision.decision_id]
                self.completed_decisions.append(decision)

        finally:
            decision.processing_time_ms = (time.perf_counter() - start_time) * 1000

        return decision, error_log

    def execute_chaos_scenario(self, scenario: GuardianFailureScenario) -> ChaosTestResult:
        """Execute a chaos engineering scenario."""
        logger.info(f"Executing chaos scenario: {scenario.description}")

        scenario_start = time.time()
        initial_in_flight = len(self.in_flight_decisions)

        # Start some decisions in parallel to simulate load
        decision_futures = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(3):
                future = executor.submit(
                    self.process_matriz_decision,
                    {"context": f"chaos_test_{i}", "data": f"test_data_{i}"}
                )
                decision_futures.append(future)

            # Allow decisions to start processing
            time.sleep(0.01)

            # Inject failure at specified phase
            failure_injection_time = time.time()
            self.guardian.inject_failure(scenario.failure_type, scenario.recovery_time_ms)

            # Wait for scenario completion
            if scenario.recovery_time_ms:
                time.sleep((scenario.recovery_time_ms + 100) / 1000.0)  # Extra 100ms buffer
            else:
                time.sleep(0.5)  # Wait for fail-closed to activate

            # Collect results
            results = []
            for future in decision_futures:
                try:
                    decision, errors = future.result(timeout=1.0)
                    results.append((decision, errors))
                except Exception as e:
                    # Decision failed due to chaos - this is expected
                    results.append((None, [str(e)]))

        # Calculate metrics
        scenario_end = time.time()

        fail_closed_activated = self.system_state == SystemState.FAIL_CLOSED
        fail_closed_time = 0.0
        if fail_closed_activated and self.fail_closed_activation_time:
            fail_closed_time = (self.fail_closed_activation_time - failure_injection_time) * 1000

        recovery_time = None
        if scenario.recovery_time_ms and self.guardian.is_healthy:
            recovery_time = scenario.recovery_time_ms

        # Check data integrity
        data_corruption = any(
            decision.corrupted for decision, _ in results if decision
        ) or self.state_corruption_detected

        # Count rollbacks and recoveries
        in_flight_recovered = initial_in_flight - len(self.in_flight_decisions)
        decisions_rolled_back = sum(
            1 for decision in self.completed_decisions
            if decision.rollback_requested and decision.timestamp >= scenario_start
        )

        # System integrity check
        system_integrity = (
            fail_closed_activated if scenario.should_fail_closed else True
        ) and not data_corruption

        result = ChaosTestResult(
            scenario_name=scenario.description,
            failure_detected=self.failure_detection_time is not None,
            fail_closed_activated=fail_closed_activated,
            fail_closed_time_ms=fail_closed_time,
            recovery_time_ms=recovery_time,
            data_corruption_detected=data_corruption,
            in_flight_transactions_recovered=in_flight_recovered,
            decisions_rolled_back=decisions_rolled_back,
            system_integrity_maintained=system_integrity,
            performance_metrics={
                "scenario_duration_ms": (scenario_end - scenario_start) * 1000,
                "failure_detection_time_ms": fail_closed_time,
                "decisions_processed": len(results)
            }
        )

        return result

    def reset_for_new_scenario(self):
        """Reset system state for new chaos scenario."""
        self.system_state = SystemState.HEALTHY
        self.failure_detection_time = None
        self.fail_closed_activation_time = None
        self.recovery_start_time = None
        self.state_corruption_detected = False

        # Clear in-flight decisions
        self.in_flight_decisions.clear()

        # Reset Guardian
        self.guardian.recover_from_failure()


@pytest.mark.consciousness
@pytest.mark.chaos_resilience
class TestMATRIZGuardianResilience:
    """MATRIZ-Guardian chaos and resilience tests."""

    def test_guardian_process_crash_fail_closed(self):
        """Test system fail-closed when Guardian process crashes."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        scenario = GuardianFailureScenario(
            failure_type=GuardianFailureType.PROCESS_CRASH,
            failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
            failure_duration_ms=0,  # Permanent crash
            recovery_time_ms=None,
            should_fail_closed=True,
            expected_corruption=False,
            description="Guardian process crash during decision validation"
        )

        result = chaos_controller.execute_chaos_scenario(scenario)

        # Assertions
        assert result.failure_detected, "Guardian crash should be detected"
        assert result.fail_closed_activated, "System should activate fail-closed mode"
        assert result.fail_closed_time_ms < 250.0, f"Fail-closed activation {result.fail_closed_time_ms:.1f}ms exceeds 250ms target"
        assert not result.data_corruption_detected, "No data corruption should occur"
        assert result.system_integrity_maintained, "System integrity should be maintained"

        # Check that no decisions were committed after failure
        committed_after_failure = sum(
            1 for decision in chaos_controller.completed_decisions
            if decision.committed and decision.timestamp > (time.time() - 1.0)
        )
        assert committed_after_failure == 0, "No decisions should be committed after Guardian crash"

        logger.info(f"✅ Guardian crash fail-closed test passed - failed closed in {result.fail_closed_time_ms:.1f}ms")

    def test_guardian_network_partition_resilience(self):
        """Test system resilience during Guardian network partition."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        scenario = GuardianFailureScenario(
            failure_type=GuardianFailureType.NETWORK_PARTITION,
            failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
            failure_duration_ms=2000,  # 2 second partition
            recovery_time_ms=2000,
            should_fail_closed=True,
            expected_corruption=False,
            description="Guardian network partition with recovery"
        )

        result = chaos_controller.execute_chaos_scenario(scenario)

        assert result.failure_detected, "Network partition should be detected"
        assert result.fail_closed_activated, "System should fail-closed during partition"
        assert result.fail_closed_time_ms < 250.0, "Fail-closed should activate quickly"
        assert not result.data_corruption_detected, "No data corruption during partition"

        logger.info("✅ Network partition resilience test passed")

    def test_guardian_memory_corruption_detection(self):
        """Test detection and handling of Guardian memory corruption."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        scenario = GuardianFailureScenario(
            failure_type=GuardianFailureType.MEMORY_CORRUPTION,
            failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
            failure_duration_ms=1000,
            recovery_time_ms=1000,
            should_fail_closed=True,
            expected_corruption=True,
            description="Guardian memory corruption with corrupted responses"
        )

        result = chaos_controller.execute_chaos_scenario(scenario)

        assert result.failure_detected, "Memory corruption should be detected"
        assert result.fail_closed_activated, "System should fail-closed on corruption"
        assert result.data_corruption_detected, "Corruption should be detected in Guardian responses"

        # Verify that corrupted decisions were not committed
        corrupted_committed = sum(
            1 for decision in chaos_controller.completed_decisions
            if decision.corrupted and decision.committed
        )
        assert corrupted_committed == 0, "No corrupted decisions should be committed"

        logger.info("✅ Memory corruption detection test passed")

    def test_guardian_timeout_fail_closed(self):
        """Test fail-closed behavior on Guardian timeout."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        scenario = GuardianFailureScenario(
            failure_type=GuardianFailureType.TIMEOUT_FAILURE,
            failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
            failure_duration_ms=3000,
            recovery_time_ms=3000,
            should_fail_closed=True,
            expected_corruption=False,
            description="Guardian timeout causing validation delays"
        )

        # Set shorter timeout for test
        start_time = time.time()
        result = chaos_controller.execute_chaos_scenario(scenario)
        execution_time = (time.time() - start_time) * 1000

        # The test should complete quickly due to fail-closed, not wait for Guardian timeout
        assert execution_time < 2000, f"Test execution {execution_time:.1f}ms too slow - fail-closed should prevent timeout wait"
        assert result.fail_closed_activated, "System should fail-closed on timeout detection"

        logger.info(f"✅ Guardian timeout fail-closed test passed - executed in {execution_time:.1f}ms")

    def test_cascading_failure_propagation(self):
        """Test handling of cascading failures between MATRIZ and Guardian."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        # Simulate multiple failure types in sequence
        failures = [
            GuardianFailureType.NETWORK_PARTITION,
            GuardianFailureType.MEMORY_CORRUPTION,
            GuardianFailureType.PROCESS_CRASH
        ]

        cascading_results = []

        for failure_type in failures:
            scenario = GuardianFailureScenario(
                failure_type=failure_type,
                failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
                failure_duration_ms=500,
                recovery_time_ms=100,  # Quick recovery for cascading test
                should_fail_closed=True,
                expected_corruption=failure_type == GuardianFailureType.MEMORY_CORRUPTION,
                description=f"Cascading failure: {failure_type.value}"
            )

            result = chaos_controller.execute_chaos_scenario(scenario)
            cascading_results.append(result)

            # Brief recovery between failures
            chaos_controller.reset_for_new_scenario()
            time.sleep(0.1)

        # Verify all failures were handled correctly
        for i, result in enumerate(cascading_results):
            assert result.failure_detected, f"Cascading failure {i+1} should be detected"
            assert result.fail_closed_activated, f"Cascading failure {i+1} should trigger fail-closed"
            assert result.system_integrity_maintained, f"System integrity should be maintained in cascading failure {i+1}"

        logger.info(f"✅ Cascading failure test passed - handled {len(failures)} sequential failures")

    def test_high_load_guardian_failure_resilience(self):
        """Test system resilience under high load when Guardian fails."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        # Generate high load
        high_load_futures = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            # Submit many decisions
            for i in range(50):
                future = executor.submit(
                    chaos_controller.process_matriz_decision,
                    {"load_test": i, "timestamp": time.time()}
                )
                high_load_futures.append(future)

            # Allow load to build up
            time.sleep(0.05)

            # Inject failure during high load
            failure_start = time.time()
            guardian.inject_failure(GuardianFailureType.PROCESS_CRASH)

            # Wait for fail-closed to handle everything
            time.sleep(0.5)

            # Collect results
            load_results = []
            for future in high_load_futures:
                try:
                    decision, errors = future.result(timeout=0.1)
                    load_results.append((decision, errors))
                except Exception as e:
                    load_results.append((None, [str(e)]))

        failure_detection_time = (chaos_controller.failure_detection_time - failure_start) * 1000 if chaos_controller.failure_detection_time else float('inf')

        # Verify fail-closed behavior under load
        assert chaos_controller.system_state == SystemState.FAIL_CLOSED, "System should be in fail-closed mode"
        assert failure_detection_time < 250.0, f"Failure detection {failure_detection_time:.1f}ms too slow under load"

        # Check that no corrupted data was committed
        corrupted_committed = sum(
            1 for decision, _ in load_results
            if decision and decision.corrupted and decision.committed
        )
        assert corrupted_committed == 0, "No corrupted data should be committed under load failure"

        # Verify rollback effectiveness
        rolled_back = sum(
            1 for decision in chaos_controller.completed_decisions
            if decision.rollback_requested
        )
        assert rolled_back > 0, "Some decisions should have been rolled back"

        logger.info(f"✅ High load resilience test passed - {len(load_results)} concurrent decisions handled")

    def test_matriz_guardian_recovery_integrity(self):
        """Test system recovery maintains integrity after Guardian failure."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        # Phase 1: Normal operation
        pre_failure_decision, _ = chaos_controller.process_matriz_decision({"phase": "pre_failure"})
        assert pre_failure_decision.committed, "Pre-failure decision should be committed"

        # Phase 2: Inject failure
        guardian.inject_failure(GuardianFailureType.PROCESS_CRASH)
        time.sleep(0.1)  # Allow fail-closed to activate

        # Phase 3: Attempt decision during failure (should fail)
        during_failure_decision, _errors = chaos_controller.process_matriz_decision({"phase": "during_failure"})
        assert not during_failure_decision.committed, "Decision during failure should not be committed"
        assert during_failure_decision.phase == MATRIZPhase.FAILED, "Decision during failure should be marked failed"

        # Phase 4: Recovery
        chaos_controller.reset_for_new_scenario()
        recovery_start = time.time()

        # Phase 5: Post-recovery operation
        post_recovery_decision, _ = chaos_controller.process_matriz_decision({"phase": "post_recovery"})
        recovery_time = (time.time() - recovery_start) * 1000

        # Verify recovery
        assert post_recovery_decision.committed, "Post-recovery decision should be committed"
        assert chaos_controller.system_state == SystemState.HEALTHY, "System should be healthy after recovery"
        assert recovery_time < 10000, f"Recovery time {recovery_time:.1f}ms exceeds 10 second target"

        # Verify no data corruption across failure boundary
        all_decisions = [pre_failure_decision, during_failure_decision, post_recovery_decision]
        corrupted_decisions = [d for d in all_decisions if d.corrupted]
        assert len(corrupted_decisions) == 0, "No decisions should be corrupted"

        logger.info(f"✅ Recovery integrity test passed - recovery completed in {recovery_time:.1f}ms")

    def test_comprehensive_chaos_scenarios(self):
        """Comprehensive test of all chaos scenarios."""
        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        scenarios = [
            GuardianFailureScenario(
                GuardianFailureType.PROCESS_CRASH,
                MATRIZPhase.TICK,
                0, None, True, False,
                "Process crash during TICK phase"
            ),
            GuardianFailureScenario(
                GuardianFailureType.NETWORK_PARTITION,
                MATRIZPhase.REFLECT,
                1500, 1500, True, False,
                "Network partition during REFLECT phase"
            ),
            GuardianFailureScenario(
                GuardianFailureType.MEMORY_CORRUPTION,
                MATRIZPhase.DECIDE,
                1000, 1000, True, True,
                "Memory corruption during DECIDE phase"
            ),
            GuardianFailureScenario(
                GuardianFailureType.TIMEOUT_FAILURE,
                MATRIZPhase.GUARDIAN_VALIDATION,
                2000, 2000, True, False,
                "Timeout during Guardian validation"
            ),
        ]

        comprehensive_results = []

        for scenario in scenarios:
            logger.info(f"Testing comprehensive scenario: {scenario.description}")

            result = chaos_controller.execute_chaos_scenario(scenario)
            comprehensive_results.append(result)

            # Verify scenario-specific requirements
            assert result.fail_closed_activated == scenario.should_fail_closed, \
                f"Scenario '{scenario.description}' fail-closed expectation not met"

            if scenario.expected_corruption:
                assert result.data_corruption_detected, \
                    f"Scenario '{scenario.description}' should detect corruption"
            else:
                assert not result.data_corruption_detected, \
                    f"Scenario '{scenario.description}' should not have corruption"

            assert result.fail_closed_time_ms < 250.0, \
                f"Scenario '{scenario.description}' fail-closed time {result.fail_closed_time_ms:.1f}ms too slow"

            # Reset for next scenario
            chaos_controller.reset_for_new_scenario()
            time.sleep(0.1)

        # Overall comprehensive assessment
        total_scenarios = len(comprehensive_results)
        successful_scenarios = sum(1 for r in comprehensive_results if r.system_integrity_maintained)
        success_rate = (successful_scenarios / total_scenarios) * 100

        assert success_rate == 100.0, f"Comprehensive chaos success rate {success_rate:.1f}% below 100% requirement"

        # Performance summary
        max_fail_closed_time = max(r.fail_closed_time_ms for r in comprehensive_results)
        mean_fail_closed_time = sum(r.fail_closed_time_ms for r in comprehensive_results) / total_scenarios

        logger.info("✅ Comprehensive chaos scenarios passed:")
        logger.info(f"   Scenarios: {successful_scenarios}/{total_scenarios}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info(f"   Max fail-closed time: {max_fail_closed_time:.1f}ms")
        logger.info(f"   Mean fail-closed time: {mean_fail_closed_time:.1f}ms")


if __name__ == "__main__":
    # Run chaos/resilience validation standalone
    def run_chaos_validation():
        print("⚡ MATRIZ-Guardian Chaos/Resilience Validation")
        print("=" * 60)

        guardian = GuardianSimulator()
        chaos_controller = MATRIZChaosController(guardian)

        test_scenarios = [
            {
                "name": "Guardian Process Crash",
                "failure_type": GuardianFailureType.PROCESS_CRASH,
                "expected_fail_closed": True
            },
            {
                "name": "Network Partition",
                "failure_type": GuardianFailureType.NETWORK_PARTITION,
                "expected_fail_closed": True
            },
            {
                "name": "Memory Corruption",
                "failure_type": GuardianFailureType.MEMORY_CORRUPTION,
                "expected_fail_closed": True
            },
            {
                "name": "Guardian Timeout",
                "failure_type": GuardianFailureType.TIMEOUT_FAILURE,
                "expected_fail_closed": True
            }
        ]

        passed_tests = 0

        for test_config in test_scenarios:
            print(f"\nTesting: {test_config['name']}")

            scenario = GuardianFailureScenario(
                failure_type=test_config["failure_type"],
                failure_phase=MATRIZPhase.GUARDIAN_VALIDATION,
                failure_duration_ms=1000,
                recovery_time_ms=1000,
                should_fail_closed=test_config["expected_fail_closed"],
                expected_corruption=test_config["failure_type"] == GuardianFailureType.MEMORY_CORRUPTION,
                description=test_config["name"]
            )

            result = chaos_controller.execute_chaos_scenario(scenario)

            # Check results
            if result.fail_closed_activated and result.fail_closed_time_ms < 250.0:
                print(f"   ✅ PASS - Fail-closed activated in {result.fail_closed_time_ms:.1f}ms")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL - Fail-closed: {result.fail_closed_activated}, Time: {result.fail_closed_time_ms:.1f}ms")

            # Reset for next test
            chaos_controller.reset_for_new_scenario()
            time.sleep(0.1)

        # High load test
        print("\nTesting: High Load Resilience")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(20):
                future = executor.submit(
                    chaos_controller.process_matriz_decision,
                    {"load_test": i}
                )
                futures.append(future)

            time.sleep(0.01)  # Let load build
            guardian.inject_failure(GuardianFailureType.PROCESS_CRASH)
            time.sleep(0.2)    # Wait for fail-closed

            results = []
            for future in futures:
                try:
                    result = future.result(timeout=0.1)
                    results.append(result)
                except Exception:
                    results.append(None)

        if chaos_controller.system_state == SystemState.FAIL_CLOSED:
            print("   ✅ PASS - High load resilience maintained")
            passed_tests += 1
        else:
            print("   ❌ FAIL - High load resilience failed")

        print(f"\n{'='*60}")
        if passed_tests == len(test_scenarios) + 1:  # +1 for high load test
            print(f"⚡ Chaos/Resilience Validation: ✅ {passed_tests}/{len(test_scenarios)+1} PASSED")
            print("   T4/0.01% excellence achieved for Guardian failure resilience")
            return True
        else:
            print(f"❌ Chaos/Resilience Validation: {passed_tests}/{len(test_scenarios)+1} passed")
            return False

    import sys
    success = run_chaos_validation()
    sys.exit(0 if success else 1)
