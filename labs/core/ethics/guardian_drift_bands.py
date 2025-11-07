#!/usr/bin/env python3
"""
Guardian Drift Bands: Ethics DSL + Drift Score Integration
==========================================================

# [SEARCH:GUARDIAN_DECISION] - Core Guardian decision engine
# [SEARCH:DRIFT_REPAIR_HOOK] - Drift detection and repair mechanisms

Task 12: Map ethics DSL outputs + drift scores into explicit action bands
(ALLOW, ALLOW-WITH-GUARDRAILS, REQUIRE-HUMAN, BLOCK) with hysteresis.

Features:
- 4-tier action band system with clear guardrails
- Hysteresis mechanism to prevent rapid band oscillations
- Integration with existing ethics DSL and drift detection
- Comprehensive audit logging with band transition history
- Configurable thresholds for different deployment environments

Constellation Framework: ⚛️🧠🛡️
Author: LUKHAS AI System
Version: 1.0.0

#TAG:ethics
#TAG:guardian
#TAG:drift
#TAG:task12
"""

import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# LUKHAS imports
try:
    from ...orchestration.plan_verifier import VerificationContext
    from .dsl_lite import DSLError
    from .ethics_engine import EthicsAction, EthicsEngine, EthicsResult
except ImportError:
    # Fallback for development/testing
    EthicsAction = None
    EthicsResult = None
    EthicsEngine = None
    VerificationContext = None
    DSLError = Exception

# Prometheus metrics for telemetry
try:
    from prometheus_client import Counter, Gauge, Histogram
    METRICS_AVAILABLE = True
except ImportError:
    # Graceful fallback for test environments
    class _NoopMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    Counter = Histogram = Gauge = lambda *args, **kwargs: _NoopMetric()
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Guardian Drift Bands metrics
GUARDIAN_BAND_TRANSITIONS = Counter(
    'guardian_band_transitions_total',
    'Total Guardian band transitions',
    ['from_band', 'to_band', 'trigger']
)

GUARDIAN_BAND_DECISIONS = Counter(
    'guardian_band_decisions_total',
    'Guardian band decisions by action',
    ['band', 'action', 'drift_range']
)

GUARDIAN_DRIFT_SCORE = Histogram(
    'guardian_drift_score',
    'Guardian drift scores',
    buckets=[0.0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.5, 0.75, 1.0]
)

GUARDIAN_HYSTERESIS_BUFFER = Gauge(
    'guardian_hysteresis_buffer_seconds',
    'Time remaining in hysteresis buffer',
    ['current_band']
)

GUARDIAN_BAND_EVALUATION_TIME = Histogram(
    'guardian_band_evaluation_ms',
    'Guardian band evaluation duration in milliseconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0]
)


class GuardianBand(Enum):
    """Guardian action bands with increasing restrictions."""
    ALLOW = "allow"                      # Full autonomy, minimal oversight
    ALLOW_WITH_GUARDRAILS = "allow_guardrails"  # Autonomy with safety nets
    REQUIRE_HUMAN = "require_human"      # Human oversight required
    BLOCK = "block"                      # Complete denial


class BandTrigger(Enum):
    """Reasons for band transitions."""
    ETHICS_VIOLATION = "ethics_violation"
    DRIFT_THRESHOLD = "drift_threshold"
    DRIFT_ACCELERATION = "drift_acceleration"
    HYSTERESIS_DECAY = "hysteresis_decay"
    MANUAL_OVERRIDE = "manual_override"
    SYSTEM_RECOVERY = "system_recovery"


@dataclass
class GuardianThresholds:
    """Configurable thresholds for Guardian band system."""

    # Primary drift thresholds for band boundaries
    allow_drift_threshold: float = 0.05      # ALLOW -> ALLOW_WITH_GUARDRAILS
    guardrails_drift_threshold: float = 0.15 # ALLOW_WITH_GUARDRAILS -> REQUIRE_HUMAN
    human_drift_threshold: float = 0.35      # REQUIRE_HUMAN -> BLOCK

    # Hysteresis buffers (seconds) to prevent rapid oscillations
    hysteresis_buffer_allow: float = 30.0    # Delay before dropping from GUARDRAILS to ALLOW
    hysteresis_buffer_guardrails: float = 60.0  # Delay before dropping from HUMAN to GUARDRAILS
    hysteresis_buffer_human: float = 120.0   # Delay before dropping from BLOCK to HUMAN

    # Drift acceleration detection
    acceleration_window_seconds: float = 300.0  # 5 minutes
    acceleration_threshold: float = 0.1      # Max drift increase per window

    # Ethics DSL integration weights
    ethics_block_weight: float = 1.0         # BLOCK ethics -> band penalty
    ethics_warn_weight: float = 0.3          # WARN ethics -> band penalty
    ethics_allow_weight: float = 0.0         # ALLOW ethics -> no penalty

    # Special case overrides
    critical_violation_immediate_block: bool = True  # Skip bands for critical violations
    system_error_fallback_band: GuardianBand = GuardianBand.BLOCK  # Fail-closed on errors

    def validate(self) -> List[str]:
        """Validate threshold configuration."""
        errors = []

        # Check threshold ordering
        thresholds = [
            self.allow_drift_threshold,
            self.guardrails_drift_threshold,
            self.human_drift_threshold
        ]

        if not all(thresholds[i] < thresholds[i+1] for i in range(len(thresholds)-1)):
            errors.append("Drift thresholds must be in ascending order")

        # Check ranges
        for name, value in [
            ("allow_drift_threshold", self.allow_drift_threshold),
            ("guardrails_drift_threshold", self.guardrails_drift_threshold),
            ("human_drift_threshold", self.human_drift_threshold)
        ]:
            if not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be between 0.0 and 1.0")

        return errors


@dataclass
class BandTransition:
    """Record of a Guardian band transition."""
    timestamp: datetime
    from_band: GuardianBand
    to_band: GuardianBand
    trigger: BandTrigger
    drift_score: float
    ethics_action: Optional[str]
    plan_hash: str
    reason: str
    hysteresis_remaining: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GuardianBandResult:
    """Result of Guardian band evaluation."""
    band: GuardianBand
    action: str  # "allow", "allow_with_guardrails", "require_human", "block"
    drift_score: float
    ethics_action: str
    evaluation_time_ms: float
    plan_hash: str
    transition: Optional[BandTransition]
    guardrails: List[str]
    human_requirements: List[str]
    audit_context: Dict[str, Any]
    hysteresis_active: bool = False
    hysteresis_remaining_seconds: float = 0.0
    # Dual-approval fields
    override_requested: bool = False
    override_approved: bool = False
    override_rationale: Optional[str] = None
    approver1_id: Optional[str] = None
    approver2_id: Optional[str] = None


class GuardianDriftBands:
    """
    Guardian Drift Bands: Map ethics DSL + drift scores to action bands

    Provides 4-tier action system with hysteresis to prevent oscillations:
    - ALLOW: Full autonomy (drift < 0.05, ethics ALLOW)
    - ALLOW_WITH_GUARDRAILS: Autonomy with safety nets (drift < 0.15, ethics ALLOW/WARN)
    - REQUIRE_HUMAN: Human oversight required (drift < 0.35, ethics WARN)
    - BLOCK: Complete denial (drift >= 0.35 or ethics BLOCK)
    """

    def __init__(
        self,
        thresholds: Optional[GuardianThresholds] = None,
        ethics_engine: Optional[EthicsEngine] = None
    ):
        """
        Initialize Guardian Drift Bands system.

        Args:
            thresholds: Custom threshold configuration
            ethics_engine: Ethics DSL engine for integration
        """
        self.thresholds = thresholds or GuardianThresholds()
        self.ethics_engine = ethics_engine

        # Validate configuration
        config_errors = self.thresholds.validate()
        if config_errors:
            raise ValueError(f"Invalid threshold configuration: {config_errors}")

        # Current state
        self.current_band = GuardianBand.ALLOW
        self.last_transition = datetime.now(timezone.utc)
        self.hysteresis_expires = {}  # band -> expiration time

        # History tracking
        self.transition_history: List[BandTransition] = []
        self.drift_history: List[Tuple[datetime, float]] = []
        self.max_history_size = 1000

        # Thread safety
        self._lock = threading.Lock()

        logger.info(
            f"GuardianDriftBands initialized: "
            f"thresholds=[{self.thresholds.allow_drift_threshold}, "
            f"{self.thresholds.guardrails_drift_threshold}, "
            f"{self.thresholds.human_drift_threshold}], "
            f"hysteresis=[{self.thresholds.hysteresis_buffer_allow}s, "
            f"{self.thresholds.hysteresis_buffer_guardrails}s, "
            f"{self.thresholds.hysteresis_buffer_human}s]"
        )

    def evaluate(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        drift_score: Optional[float] = None,
        ethics_result: Optional[EthicsResult] = None
    ) -> GuardianBandResult:
        """
        Evaluate plan against Guardian band system.

        Args:
            plan: Action plan to evaluate
            context: Optional evaluation context
            drift_score: Pre-computed drift score (will calculate if None)
            ethics_result: Pre-computed ethics result (will evaluate if None)

        Returns:
            GuardianBandResult with band assignment and guardrails
        """
        start_time = time.perf_counter()

        with self._lock:
            try:
                # Generate plan hash for tracking
                plan_str = repr(sorted(plan.items()))
                plan_hash = hashlib.sha256(plan_str.encode()).hexdigest()[:16]

                # Get ethics evaluation
                if ethics_result is None and self.ethics_engine:
                    ethics_result = self.ethics_engine.evaluate_plan(plan, context)

                ethics_action = ethics_result.action.value if ethics_result else "unknown"

                # Calculate or use provided drift score
                computed_drift = drift_score if drift_score is not None else self._calculate_drift_score(
                    plan, context, ethics_result
                )

                # Record drift history
                now = datetime.now(timezone.utc)
                self.drift_history.append((now, computed_drift))
                if len(self.drift_history) > self.max_history_size:
                    self.drift_history.pop(0)

                # Calculate target band based on drift + ethics
                target_band = self._calculate_target_band(computed_drift, ethics_result)

                # Apply hysteresis logic
                final_band, transition = self._apply_hysteresis(target_band, computed_drift, ethics_action, plan_hash)

                # Generate guardrails and requirements
                guardrails = self._generate_guardrails(final_band, computed_drift, ethics_result)
                human_requirements = self._generate_human_requirements(final_band, computed_drift, ethics_result)

                # Check if hysteresis is active
                hysteresis_active = self._is_hysteresis_active(final_band)
                hysteresis_remaining = self._get_hysteresis_remaining(final_band)

                evaluation_time_ms = (time.perf_counter() - start_time) * 1000

                # Create result
                result = GuardianBandResult(
                    band=final_band,
                    action=final_band.value,
                    drift_score=computed_drift,
                    ethics_action=ethics_action,
                    evaluation_time_ms=evaluation_time_ms,
                    plan_hash=plan_hash,
                    transition=transition,
                    guardrails=guardrails,
                    human_requirements=human_requirements,
                    audit_context={
                        "timestamp": now.isoformat(),
                        "plan": plan,
                        "context": context or {},
                        "thresholds": {
                            "allow": self.thresholds.allow_drift_threshold,
                            "guardrails": self.thresholds.guardrails_drift_threshold,
                            "human": self.thresholds.human_drift_threshold
                        },
                        "current_band": self.current_band.value,
                        "target_band": target_band.value,
                    },
                    hysteresis_active=hysteresis_active,
                    hysteresis_remaining_seconds=hysteresis_remaining
                )

                # Record metrics
                if METRICS_AVAILABLE:
                    GUARDIAN_DRIFT_SCORE.observe(computed_drift)
                    GUARDIAN_BAND_DECISIONS.labels(
                        band=final_band.value,
                        action=final_band.value,
                        drift_range=self._get_drift_range(computed_drift)
                    ).inc()
                    GUARDIAN_BAND_EVALUATION_TIME.observe(evaluation_time_ms)
                    GUARDIAN_HYSTERESIS_BUFFER.labels(current_band=final_band.value).set(hysteresis_remaining)

                # Emit governance ledger for non-ALLOW decisions (Task 13)
                if final_band != GuardianBand.ALLOW:
                    self._emit_governance_decision(result, plan, context or {})

                logger.info(
                    f"Guardian evaluation: band={final_band.value}, "
                    f"drift={computed_drift:.4f}, ethics={ethics_action}, "
                    f"time={evaluation_time_ms:.2f}ms, hash={plan_hash}"
                )

                return result

            except Exception as e:
                evaluation_time_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"Guardian evaluation error: {e}")

                # Fail-closed error handling
                return GuardianBandResult(
                    band=self.thresholds.system_error_fallback_band,
                    action=self.thresholds.system_error_fallback_band.value,
                    drift_score=1.0,  # Max drift on error
                    ethics_action="error",
                    evaluation_time_ms=evaluation_time_ms,
                    plan_hash="error",
                    transition=None,
                    guardrails=["system_error_detected"],
                    human_requirements=["investigate_system_error"],
                    audit_context={"error": str(e)},
                    hysteresis_active=False,
                    hysteresis_remaining_seconds=0.0
                )

    def _calculate_drift_score(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        ethics_result: Optional[EthicsResult]
    ) -> float:
        """Calculate composite drift score from plan, context, and ethics."""
        base_drift = 0.0

        # Add ethics-based drift penalty
        if ethics_result and hasattr(ethics_result, 'action') and EthicsAction:
            if ethics_result.action == EthicsAction.BLOCK:
                base_drift += self.thresholds.ethics_block_weight
            elif ethics_result.action == EthicsAction.WARN:
                base_drift += self.thresholds.ethics_warn_weight

        # Add plan complexity factors
        if isinstance(plan.get("params"), dict):
            param_count = len(plan["params"])
            if param_count > 10:
                base_drift += 0.05  # Complex plans carry drift risk

        # Add context risk factors
        if context:
            if context.get("user_id") is None:
                base_drift += 0.1  # Missing user context increases drift

            if context.get("session_id") is None:
                base_drift += 0.05  # Missing session context

        # Check for drift acceleration
        acceleration_penalty = self._calculate_drift_acceleration()
        base_drift += acceleration_penalty

        return min(base_drift, 1.0)  # Cap at 1.0

    def _calculate_drift_acceleration(self) -> float:
        """Detect rapid drift increases over recent history."""
        if len(self.drift_history) < 2:
            return 0.0

        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=self.thresholds.acceleration_window_seconds)

        # Get recent drift scores
        recent_scores = [
            score for timestamp, score in self.drift_history
            if timestamp >= window_start
        ]

        if len(recent_scores) < 2:
            return 0.0

        # Calculate drift rate of change
        drift_change = recent_scores[-1] - recent_scores[0]

        if drift_change > self.thresholds.acceleration_threshold:
            return 0.2  # Penalty for rapid drift acceleration

        return 0.0

    def _calculate_target_band(self, drift_score: float, ethics_result: Optional[EthicsResult]) -> GuardianBand:
        """Calculate target band based on drift score and ethics result."""

        # Critical violations skip to BLOCK immediately
        if (ethics_result and
            hasattr(ethics_result, 'action') and
            EthicsAction and
            ethics_result.action == EthicsAction.BLOCK and
            self.thresholds.critical_violation_immediate_block):
            return GuardianBand.BLOCK

        # Map drift score to bands
        if drift_score >= self.thresholds.human_drift_threshold:
            return GuardianBand.BLOCK
        elif drift_score >= self.thresholds.guardrails_drift_threshold:
            return GuardianBand.REQUIRE_HUMAN
        elif drift_score >= self.thresholds.allow_drift_threshold:
            return GuardianBand.ALLOW_WITH_GUARDRAILS
        else:
            return GuardianBand.ALLOW

    def _apply_hysteresis(
        self,
        target_band: GuardianBand,
        drift_score: float,
        ethics_action: str,
        plan_hash: str
    ) -> Tuple[GuardianBand, Optional[BandTransition]]:
        """Apply hysteresis logic to prevent rapid band oscillations."""

        now = datetime.now(timezone.utc)
        transition = None

        # Check if we need to transition up (more restrictive) - immediate
        if target_band.value > self.current_band.value:
            transition = BandTransition(
                timestamp=now,
                from_band=self.current_band,
                to_band=target_band,
                trigger=BandTrigger.DRIFT_THRESHOLD if drift_score >= self.thresholds.allow_drift_threshold else BandTrigger.ETHICS_VIOLATION,
                drift_score=drift_score,
                ethics_action=ethics_action,
                plan_hash=plan_hash,
                reason=f"Drift threshold exceeded: {drift_score:.4f}"
            )

            self.current_band = target_band
            self.last_transition = now

            # Set hysteresis buffer for downward transitions
            self._set_hysteresis_buffer(target_band)

        # Check if we can transition down (less restrictive) - with hysteresis
        elif target_band.value < self.current_band.value:

            # Check if hysteresis period has expired
            hysteresis_key = self.current_band
            if (hysteresis_key not in self.hysteresis_expires or
                now >= self.hysteresis_expires[hysteresis_key]):

                transition = BandTransition(
                    timestamp=now,
                    from_band=self.current_band,
                    to_band=target_band,
                    trigger=BandTrigger.HYSTERESIS_DECAY,
                    drift_score=drift_score,
                    ethics_action=ethics_action,
                    plan_hash=plan_hash,
                    reason=f"Hysteresis expired, drift improved: {drift_score:.4f}"
                )

                self.current_band = target_band
                self.last_transition = now

                # Clear hysteresis for this band
                if hysteresis_key in self.hysteresis_expires:
                    del self.hysteresis_expires[hysteresis_key]

        # Record transition if occurred
        if transition:
            self.transition_history.append(transition)
            if len(self.transition_history) > self.max_history_size:
                self.transition_history.pop(0)

            # Record transition metric
            if METRICS_AVAILABLE:
                GUARDIAN_BAND_TRANSITIONS.labels(
                    from_band=transition.from_band.value,
                    to_band=transition.to_band.value,
                    trigger=transition.trigger.value
                ).inc()

            logger.info(
                f"Guardian band transition: {transition.from_band.value} -> {transition.to_band.value} "
                f"({transition.trigger.value}), drift={drift_score:.4f}"
            )

        return self.current_band, transition

    def _set_hysteresis_buffer(self, band: GuardianBand) -> None:
        """Set hysteresis buffer for downward transitions."""
        now = datetime.now(timezone.utc)

        if band == GuardianBand.ALLOW_WITH_GUARDRAILS:
            self.hysteresis_expires[band] = now + timedelta(seconds=self.thresholds.hysteresis_buffer_allow)
        elif band == GuardianBand.REQUIRE_HUMAN:
            self.hysteresis_expires[band] = now + timedelta(seconds=self.thresholds.hysteresis_buffer_guardrails)
        elif band == GuardianBand.BLOCK:
            self.hysteresis_expires[band] = now + timedelta(seconds=self.thresholds.hysteresis_buffer_human)

    def _is_hysteresis_active(self, band: GuardianBand) -> bool:
        """Check if hysteresis is currently active for the band."""
        now = datetime.now(timezone.utc)
        return (band in self.hysteresis_expires and
                now < self.hysteresis_expires[band])

    def _get_hysteresis_remaining(self, band: GuardianBand) -> float:
        """Get remaining hysteresis time in seconds."""
        if not self._is_hysteresis_active(band):
            return 0.0

        now = datetime.now(timezone.utc)
        return (self.hysteresis_expires[band] - now).total_seconds()

    def _generate_guardrails(
        self,
        band: GuardianBand,
        drift_score: float,
        ethics_result: Optional[EthicsResult]
    ) -> List[str]:
        """Generate specific guardrails for the assigned band."""
        guardrails = []

        if band == GuardianBand.ALLOW_WITH_GUARDRAILS:
            guardrails.extend([
                "enhanced_audit_logging",
                "parameter_validation_required",
                "user_context_verification"
            ])

            if drift_score > 0.1:
                guardrails.append("drift_monitoring_enabled")

            if ethics_result and ethics_result.action == EthicsAction.WARN:
                guardrails.extend([
                    "ethics_warning_logged",
                    "additional_consent_check"
                ])

        elif band == GuardianBand.REQUIRE_HUMAN:
            guardrails.extend([
                "human_approval_required",
                "comprehensive_audit_trail",
                "rollback_capability_verified",
                "impact_assessment_completed"
            ])

            if drift_score > 0.25:
                guardrails.append("senior_oversight_required")

        elif band == GuardianBand.BLOCK:
            guardrails.extend([
                "operation_blocked",
                "security_review_required",
                "incident_logged",
                "system_state_preserved"
            ])

        return guardrails

    def _generate_human_requirements(
        self,
        band: GuardianBand,
        drift_score: float,
        ethics_result: Optional[EthicsResult]
    ) -> List[str]:
        """Generate human oversight requirements for bands that need them."""
        requirements = []

        if band == GuardianBand.REQUIRE_HUMAN:
            requirements.extend([
                "review_plan_parameters",
                "validate_user_intent",
                "confirm_safety_constraints",
                "approve_execution"
            ])

            if drift_score > 0.25:
                requirements.append("escalate_to_senior_staff")

            if ethics_result and len(ethics_result.triggered_rules) > 2:
                requirements.append("ethics_committee_review")

        elif band == GuardianBand.BLOCK:
            requirements.extend([
                "investigate_block_reason",
                "assess_system_security",
                "determine_remediation_steps",
                "approve_system_changes"
            ])

        return requirements

    def _get_drift_range(self, drift_score: float) -> str:
        """Get drift range label for metrics."""
        if drift_score < 0.05:
            return "low"
        elif drift_score < 0.15:
            return "medium"
        elif drift_score < 0.35:
            return "high"
        else:
            return "critical"

    def get_current_status(self) -> Dict[str, Any]:
        """Get current Guardian band system status."""
        now = datetime.now(timezone.utc)

        # Calculate recent statistics
        recent_window = now - timedelta(minutes=10)
        recent_transitions = [
            t for t in self.transition_history
            if t.timestamp >= recent_window
        ]

        recent_drift = [
            score for timestamp, score in self.drift_history
            if timestamp >= recent_window
        ]

        return {
            "current_band": self.current_band.value,
            "last_transition": self.last_transition.isoformat(),
            "hysteresis_active": {
                band.value: self._is_hysteresis_active(band)
                for band in GuardianBand
            },
            "hysteresis_remaining": {
                band.value: self._get_hysteresis_remaining(band)
                for band in GuardianBand
            },
            "recent_transitions_10min": len(recent_transitions),
            "recent_avg_drift": sum(recent_drift) / len(recent_drift) if recent_drift else 0.0,
            "thresholds": {
                "allow": self.thresholds.allow_drift_threshold,
                "guardrails": self.thresholds.guardrails_drift_threshold,
                "human": self.thresholds.human_drift_threshold
            },
            "total_transitions": len(self.transition_history),
            "total_evaluations": len(self.drift_history),
            "system_status": "operational"
        }

    def force_band_transition(
        self,
        target_band: GuardianBand,
        reason: str,
        operator_id: Optional[str] = None
    ) -> BandTransition:
        """Force a manual band transition (for emergency overrides)."""

        with self._lock:
            now = datetime.now(timezone.utc)

            transition = BandTransition(
                timestamp=now,
                from_band=self.current_band,
                to_band=target_band,
                trigger=BandTrigger.MANUAL_OVERRIDE,
                drift_score=0.0,  # Manual override
                ethics_action="manual",
                plan_hash="manual_override",
                reason=reason,
                metadata={"operator_id": operator_id} if operator_id else {}
            )

            self.current_band = target_band
            self.last_transition = now
            self.transition_history.append(transition)

            # Clear any existing hysteresis
            self.hysteresis_expires.clear()

            logger.warning(
                f"Manual Guardian band override: {transition.from_band.value} -> {target_band.value} "
                f"by {operator_id or 'unknown'}: {reason}"
            )

            return transition

    def request_block_override(
        self,
        plan_hash: str,
        rationale: str,
        approver1_id: str,
        approver2_id: str,
        get_tier_fn: callable
    ) -> GuardianBandResult:
        """
        Request dual-approval override for BLOCK actions.

        Args:
            plan_hash: Hash of the blocked plan
            rationale: Justification for override
            approver1_id: First approver's ΛiD
            approver2_id: Second approver's ΛiD
            get_tier_fn: Function to get approver tier

        Returns:
            GuardianBandResult with override decision

        Raises:
            ValueError: If same approver used twice
            PermissionError: If approvers not T4+
        """
        with self._lock:
            try:
                # Validate dual-approval
                if approver1_id == approver2_id:
                    raise ValueError("Dual approval requires different approvers")

                tier1 = get_tier_fn(approver1_id)
                tier2 = get_tier_fn(approver2_id)

                if tier1 < 4 or tier2 < 4:
                    raise PermissionError(f"Critical overrides require T4+ approvers (got T{tier1}, T{tier2})")

                # Create override result
                now = datetime.now(timezone.utc)
                override_result = GuardianBandResult(
                    band=GuardianBand.ALLOW,  # Override allows execution
                    action="allow",
                    drift_score=0.0,  # Reset for override
                    ethics_action="override_approved",
                    evaluation_time_ms=0.0,
                    plan_hash=plan_hash,
                    transition=None,
                    guardrails=["dual_approved_override", "audit_trail_required"],
                    human_requirements=["post_execution_review"],
                    audit_context={
                        "override_timestamp": now.isoformat(),
                        "original_action": "block",
                        "override_rationale": rationale,
                        "dual_approval_tier": f"T{tier1}+T{tier2}"
                    },
                    override_requested=True,
                    override_approved=True,
                    override_rationale=rationale,
                    approver1_id=approver1_id,
                    approver2_id=approver2_id
                )

                logger.warning(
                    f"BLOCK override approved: plan={plan_hash} "
                    f"approvers={approver1_id}(T{tier1})+{approver2_id}(T{tier2}) "
                    f"rationale={rationale}"
                )

                return override_result

            except (ValueError, PermissionError) as e:
                # Create denied result
                deny_result = GuardianBandResult(
                    band=GuardianBand.BLOCK,
                    action="block",
                    drift_score=1.0,  # Max drift for denied override
                    ethics_action="override_denied",
                    evaluation_time_ms=0.0,
                    plan_hash=plan_hash,
                    transition=None,
                    guardrails=["operation_blocked", "override_denied"],
                    human_requirements=["escalate_to_security_team"],
                    audit_context={
                        "override_attempt": datetime.now(timezone.utc).isoformat(),
                        "denial_reason": str(e)
                    },
                    override_requested=True,
                    override_approved=False,
                    override_rationale=f"DENIED: {e}"
                )

                logger.error(f"BLOCK override denied: plan={plan_hash} reason={e}")
                return deny_result

    def evaluate_with_override_option(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        drift_score: Optional[float] = None,
        ethics_result: Optional[EthicsResult] = None,
        override_request: Optional[Dict[str, Any]] = None
    ) -> GuardianBandResult:
        """
        Evaluate plan with optional override request for BLOCK results.

        Args:
            plan: Action plan to evaluate
            context: Optional evaluation context
            drift_score: Pre-computed drift score
            ethics_result: Pre-computed ethics result
            override_request: Override request with approver details

        Returns:
            GuardianBandResult with override handling
        """
        # First, get normal evaluation
        result = self.evaluate(plan, context, drift_score, ethics_result)

        # If result is BLOCK and override requested, process override
        if (result.band == GuardianBand.BLOCK and
            override_request and
            override_request.get('requested')):

            try:
                override_result = self.request_block_override(
                    plan_hash=result.plan_hash,
                    rationale=override_request.get('rationale', 'No rationale provided'),
                    approver1_id=override_request.get('approver1_id'),
                    approver2_id=override_request.get('approver2_id'),
                    get_tier_fn=override_request.get('get_tier_fn')
                )
                return override_result

            except Exception as e:
                # Return original BLOCK with override failure info
                result.override_requested = True
                result.override_approved = False
                result.override_rationale = f"Override failed: {e}"
                result.guardrails.append("override_processing_failed")

        return result

    def _emit_governance_decision(
        self,
        result: GuardianBandResult,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Emit governance ledger entry for non-ALLOW decisions.

        Args:
            result: Guardian band evaluation result
            plan: Original action plan
            context: Evaluation context
        """
        try:
            # Try to import and use governance emitter
            try:
                from ...guardian.emit import emit_guardian_decision
                # Get database connection from context if available
                db = context.get('db')  # Application should provide this

                # Extract safety tags and confidences from context
                safety_tags = context.get('safety_tags', [])
                tagged_plan = context.get('tagged_plan')

                if tagged_plan:
                    # Extract tag details from TaggedPlan object
                    tag_names = list(tagged_plan.tag_names)
                    confidences = {tag.name: tag.confidence for tag in tagged_plan.tags}
                else:
                    # Use basic tags from context
                    tag_names = safety_tags if isinstance(safety_tags, list) else []
                    confidences = {}

                # Emit governance decision
                emit_guardian_decision(
                    db=db,
                    plan_id=result.plan_hash,
                    lambda_id=context.get('lambda_id', 'unknown'),
                    action=result.action,
                    rule_name=context.get('triggered_rule', f'guardian_{result.band.value}'),
                    tags=tag_names,
                    confidences=confidences,
                    band=result.band.value,
                    tenant=context.get('tenant', 'default'),
                    env=context.get('env', 'prod'),
                    purpose=context.get('purpose'),
                    retention_days=context.get('retention_days'),
                    justification=f"Guardian band: {result.band.value}, drift: {result.drift_score:.3f}",
                    override_requested=result.override_requested,
                    override_approved=result.override_approved,
                    approver1_id=result.approver1_id,
                    approver2_id=result.approver2_id
                )

                logger.debug(f"Governance decision emitted: {result.action} for plan {result.plan_hash}")

            except ImportError:
                # Guardian emitter not available, log decision
                logger.info(
                    f"Governance decision (emitter unavailable): action={result.action}, "
                    f"band={result.band.value}, plan={result.plan_hash}, "
                    f"lambda_id={context.get('lambda_id', 'unknown')}"
                )

        except Exception as e:
            # Don't fail Guardian evaluation due to governance emission errors
            logger.warning(f"Failed to emit governance decision: {e}")


# Factory function for easy instantiation
def create_guardian_drift_bands(
    allow_threshold: float = 0.05,
    guardrails_threshold: float = 0.15,
    human_threshold: float = 0.35,
    **kwargs
) -> GuardianDriftBands:
    """
    Create Guardian Drift Bands system with custom thresholds.

    Args:
        allow_threshold: ALLOW -> ALLOW_WITH_GUARDRAILS threshold
        guardrails_threshold: ALLOW_WITH_GUARDRAILS -> REQUIRE_HUMAN threshold
        human_threshold: REQUIRE_HUMAN -> BLOCK threshold
        **kwargs: Additional threshold parameters

    Returns:
        Configured GuardianDriftBands instance
    """
    thresholds = GuardianThresholds(
        allow_drift_threshold=allow_threshold,
        guardrails_drift_threshold=guardrails_threshold,
        human_drift_threshold=human_threshold,
        **kwargs
    )

    return GuardianDriftBands(thresholds=thresholds)


# Export main classes
__all__ = [
    "GuardianBand",
    "GuardianThresholds",
    "GuardianBandResult",
    "GuardianDriftBands",
    "BandTransition",
    "BandTrigger",
    "create_guardian_drift_bands"
]
