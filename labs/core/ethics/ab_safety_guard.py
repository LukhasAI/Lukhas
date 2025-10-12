#!/usr/bin/env python3
"""
A/B Safety Guard: Lane-aware Ethics Enforcement with Kill Switch
================================================================

Task 13: A/B testing safety guard with automatic rollback capabilities.

Features:
- Lane-aware enforcement (candidate=enabled, control=logging only)
- Auto-rollback on Critical → BLOCK rate drops
- Circuit breaker pattern for safety
- Real-time monitoring and alerting

Constellation Framework: ⚛️🧠🛡️
Author: LUKHAS AI System
Version: 1.0.0

#TAG:ethics
#TAG:ab_testing
#TAG:safety_guard
#TAG:task13
"""

import logging
import os
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Prometheus metrics for safety guard
try:
    from prometheus_client import Counter, Gauge, Histogram
    METRICS_AVAILABLE = True
except ImportError:
    class _NoopMetric:
        def inc(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    Counter = Gauge = Histogram = lambda *args, **kwargs: _NoopMetric()
    METRICS_AVAILABLE = False

# Safety Guard Metrics
SAFETY_GUARD_ENFORCEMENT = Counter(
    'safety_guard_enforcement_total',
    'Safety guard enforcement decisions',
    ['lane', 'action', 'enforced']
)

SAFETY_GUARD_ROLLBACK = Counter(
    'safety_guard_rollback_total',
    'Safety guard automatic rollbacks triggered',
    ['lane', 'reason']
)

SAFETY_GUARD_CRITICAL_BLOCK_RATE = Gauge(
    'safety_guard_critical_block_rate',
    'Current Critical → BLOCK conversion rate',
    ['lane']
)

SAFETY_GUARD_CIRCUIT_STATE = Gauge(
    'safety_guard_circuit_state',
    'Circuit breaker state (0=closed, 1=open)',
    ['lane']
)


class EnforcementMode(Enum):
    """Ethics enforcement modes."""
    DISABLED = "disabled"      # No enforcement, logging only
    LOGGING_ONLY = "logging"   # Log decisions but don't enforce
    ENFORCE = "enforce"        # Full enforcement
    CIRCUIT_OPEN = "circuit_open"  # Circuit breaker open, fail-safe


class SafetyGuardState(Enum):
    """Safety guard operational states."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    EMERGENCY_ROLLBACK = "emergency_rollback"


@dataclass
class ABSafetyConfig:
    """A/B Safety Guard configuration."""
    # Lane configuration
    candidate_enforcement: EnforcementMode = EnforcementMode.ENFORCE
    control_enforcement: EnforcementMode = EnforcementMode.LOGGING_ONLY

    # Auto-rollback thresholds
    min_critical_block_rate: float = 0.8  # Critical → BLOCK rate threshold
    rollback_window_minutes: int = 10     # Monitoring window
    min_samples_for_rollback: int = 20    # Minimum samples to trigger rollback

    # Circuit breaker
    circuit_failure_threshold: int = 5    # Failures before opening
    circuit_recovery_time_seconds: int = 300  # Time before attempting recovery

    # Kill switch
    emergency_disable_file: str = "/tmp/guardian_emergency_disable"


class ABSafetyGuard:
    """
    A/B Safety Guard: Lane-aware ethics enforcement with auto-rollback.

    Provides safe A/B testing of ethics enforcement with automatic rollback
    capabilities when safety metrics degrade.
    """

    def __init__(self, config: Optional[ABSafetyConfig] = None):
        """
        Initialize A/B Safety Guard.

        Args:
            config: Safety guard configuration
        """
        self.config = config or ABSafetyConfig()

        # State tracking
        self.state = SafetyGuardState.HEALTHY
        self.circuit_failures = {"labs": 0, "control": 0}
        self.circuit_open_until = {"labs": None, "control": None}

        # Metrics tracking for rollback detection
        self.recent_decisions = {"labs": [], "control": []}
        self.rollback_triggered = False

        # Thread safety
        self._lock = threading.Lock()

        logger.info(f"ABSafetyGuard initialized: candidate={self.config.candidate_enforcement.value}, "
                   f"control={self.config.control_enforcement.value}")

    def should_enforce_ethics(self, lane: str, plan: Dict[str, Any]) -> bool:
        """
        Determine if ethics should be enforced for this lane/plan.

        Args:
            lane: A/B test lane (candidate|control)
            plan: Action plan being evaluated

        Returns:
            bool: True if ethics should be enforced
        """
        with self._lock:
            # Check emergency kill switch
            if os.path.exists(self.config.emergency_disable_file):
                logger.warning("Emergency kill switch active - disabling all enforcement")
                self._record_enforcement_decision(lane, "emergency_disabled", False)
                return False

            # Check circuit breaker
            if self._is_circuit_open(lane):
                logger.warning(f"Circuit breaker open for lane {lane} - disabling enforcement")
                self._record_enforcement_decision(lane, "circuit_open", False)
                return False

            # Check auto-rollback
            if self.rollback_triggered:
                logger.warning("Auto-rollback triggered - disabling candidate enforcement")
                self._record_enforcement_decision(lane, "rollback_active", False)
                return False

            # Get enforcement mode for lane
            enforcement_mode = self._get_enforcement_mode(lane)

            enforce = enforcement_mode == EnforcementMode.ENFORCE
            self._record_enforcement_decision(lane, enforcement_mode.value, enforce)

            return enforce

    def record_guardian_decision(
        self,
        lane: str,
        action: str,
        was_critical: bool = False,
        was_blocked: bool = False
    ) -> None:
        """
        Record Guardian decision for rollback monitoring.

        Args:
            lane: A/B test lane
            action: Guardian action taken
            was_critical: Whether this was a critical risk scenario
            was_blocked: Whether the action resulted in BLOCK
        """
        with self._lock:
            timestamp = datetime.now(timezone.utc)

            # Record decision
            decision = {
                'timestamp': timestamp,
                'action': action,
                'was_critical': was_critical,
                'was_blocked': was_blocked
            }

            # Add to recent decisions
            if lane not in self.recent_decisions:
                self.recent_decisions[lane] = []

            self.recent_decisions[lane].append(decision)

            # Cleanup old decisions (keep last 100 or window + buffer)
            cutoff_time = timestamp - timedelta(minutes=self.config.rollback_window_minutes + 5)
            self.recent_decisions[lane] = [
                d for d in self.recent_decisions[lane]
                if d['timestamp'] >= cutoff_time
            ]

            # Check for rollback conditions
            self._check_rollback_conditions()

    def _get_enforcement_mode(self, lane: str) -> EnforcementMode:
        """Get enforcement mode for lane."""
        if lane == "labs":
            return self.config.candidate_enforcement
        elif lane == "control":
            return self.config.control_enforcement
        else:
            # Unknown lane, default to logging only
            return EnforcementMode.LOGGING_ONLY

    def _is_circuit_open(self, lane: str) -> bool:
        """Check if circuit breaker is open for lane."""
        open_until = self.circuit_open_until.get(lane)

        if open_until is None:
            return False

        if datetime.now(timezone.utc) > open_until:
            # Circuit recovery time passed
            self.circuit_open_until[lane] = None
            self.circuit_failures[lane] = 0
            logger.info(f"Circuit breaker recovered for lane {lane}")

            if METRICS_AVAILABLE:
                SAFETY_GUARD_CIRCUIT_STATE.labels(lane=lane).set(0)

            return False

        return True

    def record_circuit_failure(self, lane: str, error: str) -> None:
        """Record circuit breaker failure."""
        with self._lock:
            self.circuit_failures[lane] = self.circuit_failures.get(lane, 0) + 1

            logger.warning(f"Circuit failure recorded for lane {lane}: {error} "
                          f"(failures: {self.circuit_failures[lane]})")

            if self.circuit_failures[lane] >= self.config.circuit_failure_threshold:
                # Open circuit breaker
                open_until = datetime.now(timezone.utc) + timedelta(
                    seconds=self.config.circuit_recovery_time_seconds
                )
                self.circuit_open_until[lane] = open_until

                logger.error(f"Circuit breaker OPEN for lane {lane} until {open_until}")

                if METRICS_AVAILABLE:
                    SAFETY_GUARD_CIRCUIT_STATE.labels(lane=lane).set(1)

    def _check_rollback_conditions(self) -> None:
        """Check if auto-rollback should be triggered."""
        if self.rollback_triggered:
            return  # Already rolled back

        # Only check candidate lane for rollback
        candidate_decisions = self.recent_decisions.get("labs", [])

        if len(candidate_decisions) < self.config.min_samples_for_rollback:
            return  # Not enough data

        # Get decisions within rollback window
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            minutes=self.config.rollback_window_minutes
        )

        recent_decisions = [
            d for d in candidate_decisions
            if d['timestamp'] >= cutoff_time
        ]

        if len(recent_decisions) < self.config.min_samples_for_rollback:
            return

        # Calculate Critical → BLOCK rate
        critical_decisions = [d for d in recent_decisions if d['was_critical']]

        if not critical_decisions:
            return  # No critical decisions to analyze

        blocked_critical = [d for d in critical_decisions if d['was_blocked']]
        block_rate = len(blocked_critical) / len(critical_decisions)

        # Update metrics
        if METRICS_AVAILABLE:
            SAFETY_GUARD_CRITICAL_BLOCK_RATE.labels(lane="labs").set(block_rate)

        # Check rollback threshold
        if block_rate < self.config.min_critical_block_rate:
            # Trigger rollback
            self.rollback_triggered = True
            self.state = SafetyGuardState.EMERGENCY_ROLLBACK

            logger.error(
                f"AUTO-ROLLBACK TRIGGERED: Critical → BLOCK rate {block_rate:.3f} "
                f"< threshold {self.config.min_critical_block_rate} "
                f"(samples: {len(critical_decisions)})"
            )

            if METRICS_AVAILABLE:
                SAFETY_GUARD_ROLLBACK.labels(
                    lane="labs",
                    reason="critical_block_rate_low"
                ).inc()

            # Alert operators
            self._send_rollback_alert(block_rate, len(critical_decisions))

    def _record_enforcement_decision(self, lane: str, reason: str, enforced: bool) -> None:
        """Record enforcement decision in metrics."""
        if METRICS_AVAILABLE:
            SAFETY_GUARD_ENFORCEMENT.labels(
                lane=lane,
                action=reason,
                enforced=str(enforced).lower()
            ).inc()

    def _send_rollback_alert(self, block_rate: float, sample_count: int) -> None:
        """Send rollback alert to operators."""
        # In production, this would integrate with alerting system
        logger.critical(
            f"GUARDIAN AUTO-ROLLBACK: Critical safety degradation detected. "
            f"Block rate: {block_rate:.1%}, Samples: {sample_count}. "
            f"Candidate enforcement DISABLED."
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current safety guard status."""
        with self._lock:
            candidate_decisions = self.recent_decisions.get("labs", [])
            control_decisions = self.recent_decisions.get("control", [])

            # Calculate recent rates
            def calc_rates(decisions):
                if not decisions:
                    return {"total": 0, "critical_block_rate": 0.0}

                critical = [d for d in decisions if d['was_critical']]
                blocked = [d for d in critical if d['was_blocked']]

                return {
                    "total": len(decisions),
                    "critical": len(critical),
                    "blocked": len(blocked),
                    "critical_block_rate": len(blocked) / len(critical) if critical else 0.0
                }

            return {
                "state": self.state.value,
                "rollback_triggered": self.rollback_triggered,
                "enforcement": {
                    "labs": self.config.candidate_enforcement.value,
                    "control": self.config.control_enforcement.value
                },
                "circuit_breaker": {
                    "candidate_open": self._is_circuit_open("labs"),
                    "control_open": self._is_circuit_open("control"),
                    "candidate_failures": self.circuit_failures.get("labs", 0),
                    "control_failures": self.circuit_failures.get("control", 0)
                },
                "recent_metrics": {
                    "labs": calc_rates(candidate_decisions),
                    "control": calc_rates(control_decisions)
                },
                "config": {
                    "min_critical_block_rate": self.config.min_critical_block_rate,
                    "rollback_window_minutes": self.config.rollback_window_minutes,
                    "min_samples_for_rollback": self.config.min_samples_for_rollback
                }
            }

    def reset_rollback(self, operator_id: str) -> None:
        """Manually reset rollback state (emergency operator action)."""
        with self._lock:
            if self.rollback_triggered:
                self.rollback_triggered = False
                self.state = SafetyGuardState.HEALTHY

                logger.warning(f"Rollback manually reset by operator {operator_id}")

                # Clear recent decision history to start fresh
                self.recent_decisions.clear()


# Global instance for easy access
_safety_guard = None

def get_safety_guard() -> ABSafetyGuard:
    """Get global A/B Safety Guard instance."""
    global _safety_guard
    if _safety_guard is None:
        _safety_guard = ABSafetyGuard()
    return _safety_guard


def should_enforce_for_lane(lane: str, plan: Dict[str, Any]) -> bool:
    """Convenience function to check enforcement for lane."""
    return get_safety_guard().should_enforce_ethics(lane, plan)


# Example usage integration:
"""
# In guardian evaluation:
from lukhas.core.ethics.ab_safety_guard import get_safety_guard

def evaluate_plan_with_ab_safety(plan, lane="candidate"):
    safety_guard = get_safety_guard()

    # Check if ethics should be enforced
    should_enforce = safety_guard.should_enforce_ethics(lane, plan)

    if not should_enforce:
        # Log but don't enforce
        logger.info(f"Ethics disabled for lane {lane} - logging only")
        return GuardianBandResult(band=GuardianBand.ALLOW, action="allow")

    # Full ethics evaluation
    result = guardian.evaluate(plan, context={"lane": lane})

    # Record decision for rollback monitoring
    safety_guard.record_guardian_decision(
        lane=lane,
        action=result.action,
        was_critical=(result.band == GuardianBand.BLOCK),
        was_blocked=(result.action == "block")
    )

    return result
"""