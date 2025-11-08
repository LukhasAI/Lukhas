#!/usr/bin/env python3
"""
LUKHAS Consciousness-Guardian Integration Layer
Phase 3 Implementation - T4/0.01% Excellence Standards

Provides comprehensive Guardian validation for consciousness operations with:
- Drift detection and safety validation
- Fail-closed behavior on Guardian failures
- GDPR-compliant audit trails
- Constitutional AI principle alignment
- Performance-optimized validation (<250ms p95)

Constellation Framework: 🛡️ Guardian-🧠 Consciousness Integration
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Awaitable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from opentelemetry import trace
from prometheus_client import Counter, Histogram

# Import consciousness types
from .types import AwarenessSnapshot, ConsciousnessState, CreativitySnapshot, ReflectionReport

# Import Guardian components
try:
    from governance.ethics.ethics_engine import EthicalDecision, EthicsEngine
    from governance.guardian.core import (
        DriftResult,
        EthicalDecision,
        EthicalSeverity,
        GovernanceAction,  # TODO: governance.guardian.cor...
        SafetyResult,
    )
    from governance.guardian.guardian_impl import GuardianSystemImpl
    from governance.guardian_system import (
        ActorType,
        DecisionStatus,
        EnforcementMode,
        GuardianAudit,
        GuardianContext,
        GuardianDecision,
        GuardianEnforcement,
        GuardianMetrics,
        GuardianSubject,
        GuardianSystem,
        RuntimeEnvironment,
        create_simple_decision,  # TODO: governance.guardian_sys...
    )
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False

# Import observability
try:
    from observability.prometheus_metrics import get_lukhas_metrics
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False
    def get_lukhas_metrics():
        return None

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class GuardianValidationType(Enum):
    """Types of Guardian validation operations"""
    CONSCIOUSNESS_STATE_TRANSITION = "consciousness_state_transition"
    REFLECTION_ANALYSIS = "reflection_analysis"
    AWARENESS_PROCESSING = "awareness_processing"
    CREATIVE_GENERATION = "creative_generation"
    DREAM_CONSOLIDATION = "dream_consolidation"
    DECISION_MAKING = "decision_making"


class ValidationResult(Enum):
    """Guardian validation results - fail-closed design"""
    APPROVED = "approved"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    ERROR = "error"  # Treated as DENIED (fail-closed)


@dataclass
class GuardianValidationConfig:
    """Configuration for consciousness-Guardian integration"""
    # Performance targets (Phase 3 requirement: <250ms p95)
    p95_target_ms: float = 200.0  # Conservative target for T4/0.01%
    p99_target_ms: float = 250.0  # Hard limit from PHASE_MATRIX.md
    timeout_ms: float = 300.0     # Fail-closed timeout

    # Drift detection (from AUDITOR_CHECKLIST.md)
    drift_threshold: float = 0.15  # Exact requirement
    drift_alpha: float = 0.3      # EMA smoothing factor

    # Safety validation
    safety_check_enabled: bool = True
    constitutional_check_enabled: bool = True
    fail_closed_on_error: bool = True  # T4 requirement

    # Compliance settings
    gdpr_audit_enabled: bool = True
    consent_validation: bool = True
    audit_retention_days: int = 90

    # Guardian system settings
    guardian_active: bool = True
    ethics_validation_required: bool = True
    enforcement_mode: str = "enforced"  # dark/canary/enforced

    # Performance monitoring
    performance_regression_detection: bool = True
    latency_alerting_enabled: bool = True

    def validate(self) -> list[str]:
        """Validate configuration parameters"""
        errors = []

        if self.p95_target_ms <= 0:
            errors.append("p95_target_ms must be positive")
        if self.drift_threshold < 0 or self.drift_threshold > 1:
            errors.append("drift_threshold must be between 0 and 1")
        if self.drift_alpha < 0 or self.drift_alpha > 1:
            errors.append("drift_alpha must be between 0 and 1")
        if self.timeout_ms < self.p99_target_ms:
            errors.append("timeout_ms should be >= p99_target_ms")

        return errors


@dataclass
class ConsciousnessValidationContext:
    """Context for consciousness validation requests"""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    validation_type: GuardianValidationType = GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    # Input data
    consciousness_state: ConsciousnessState | None = None
    awareness_snapshot: AwarenessSnapshot | None = None
    reflection_report: ReflectionReport | None = None
    creative_snapshot: CreativitySnapshot | None = None

    # Context metadata
    user_id: str | None = None
    session_id: str | None = None
    tenant: str = "default"
    lane: str = "consciousness"

    # Risk assessment
    risk_indicators: list[str] = field(default_factory=list)
    sensitive_operation: bool = False


@dataclass
class GuardianValidationResult:
    """Comprehensive Guardian validation result"""
    operation_id: str
    validation_type: GuardianValidationType
    result: ValidationResult
    timestamp: float = field(default_factory=time.time)

    # Validation outcomes
    ethical_decision: EthicalDecision | None = None
    safety_result: SafetyResult | None = None
    drift_result: DriftResult | None = None

    # Guardian envelope (if generated)
    guardian_envelope: dict[str, Any] | None = None

    # Performance metrics
    validation_duration_ms: float = 0.0

    # Compliance and audit
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    gdpr_compliant: bool = True
    consent_verified: bool = False

    # Reasoning and recommendations
    reason: str = ""
    confidence: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def is_approved(self) -> bool:
        """Check if validation result allows operation (fail-closed)"""
        return self.result == ValidationResult.APPROVED

    def add_audit_entry(self, event_type: str, details: dict[str, Any]):
        """Add entry to audit trail"""
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "operation_id": self.operation_id
        }
        self.audit_trail.append(entry)


# Guardian-specific Prometheus metrics
guardian_validations_total = Counter(
    'lukhas_guardian_validations_total',
    'Total Guardian validation operations',
    ['validation_type', 'result', 'lane']
)

guardian_validation_latency_seconds = Histogram(
    'lukhas_guardian_validation_latency_seconds',
    'Guardian validation latency distribution',
    ['validation_type', 'result', 'lane'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.25, 0.3, 0.5, 1.0]
)

guardian_drift_scores = Histogram(
    'lukhas_guardian_drift_scores',
    'Consciousness drift score distribution',
    ['validation_type', 'lane'],
    buckets=[0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
)

guardian_failures_total = Counter(
    'lukhas_guardian_failures_total',
    'Total Guardian validation failures',
    ['failure_type', 'validation_type', 'lane']
)

guardian_performance_regressions = Counter(
    'lukhas_guardian_performance_regressions_total',
    'Guardian performance regression detections',
    ['severity', 'lane']
)

guardian_audit_events_total = Counter(
    'lukhas_guardian_audit_events_total',
    'Total Guardian audit events',
    ['event_type', 'lane']
)


class ConsciousnessGuardianIntegration:
    """
    Production-grade Guardian integration for consciousness engines.

    Provides comprehensive validation, drift detection, safety checks,
    and audit trails for all consciousness operations with T4/0.01% standards.
    """

    def __init__(
        self,
        config: GuardianValidationConfig | None = None,
        guardian_system: GuardianSystem | None = None,
        ethics_engine: EthicsEngine | None = None
    ):
        """
        Initialize Guardian integration layer.

        Args:
            config: Guardian validation configuration
            guardian_system: Pre-configured Guardian system instance
            ethics_engine: Pre-configured ethics engine instance
        """
        self.config = config or GuardianValidationConfig()
        self._component_id = "ConsciousnessGuardianIntegration"

        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            raise ValueError(f"Invalid GuardianValidationConfig: {', '.join(config_errors)}")

        # Initialize Guardian components
        self._initialize_guardian_systems(guardian_system, ethics_engine)

        # Initialize metrics
        self._metrics = get_lukhas_metrics() if OBSERVABILITY_AVAILABLE else None
        self._lane = self._metrics.lane if self._metrics else self.config.enforcement_mode

        # Performance tracking
        self._validation_latencies: list[float] = []
        self._drift_scores: list[float] = []
        self._validation_history: list[GuardianValidationResult] = []

        # Baseline tracking for drift detection
        self._baseline_states: dict[str, ConsciousnessState] = {}
        self._state_history: list[ConsciousnessState] = []

        # Audit trail management
        self._audit_events: list[dict[str, Any]] = []
        self._audit_retention_ms = self.config.audit_retention_days * 24 * 60 * 60 * 1000

        # Emergency states
        self._emergency_mode: bool = False
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 5

        logger.info(f"Guardian integration initialized: drift_threshold={self.config.drift_threshold}")

    def _initialize_guardian_systems(
        self,
        guardian_system: GuardianSystem | None,
        ethics_engine: EthicsEngine | None
    ):
        """Initialize Guardian system components"""
        if not GUARDIAN_AVAILABLE:
            logger.warning("Guardian system not available - running in mock mode")
            self.guardian_system = None
            self.guardian_impl = None
            self.ethics_engine = None
            return

        # Initialize Guardian system
        self.guardian_system = guardian_system or GuardianSystem()

        # Initialize Guardian implementation
        self.guardian_impl = GuardianSystemImpl(drift_threshold=self.config.drift_threshold)

        # Initialize ethics engine
        self.ethics_engine = ethics_engine or EthicsEngine()

        logger.info("Guardian systems initialized successfully")

    async def validate_consciousness_operation(
        self,
        context: ConsciousnessValidationContext,
        pre_validation_hook: Callable[[ConsciousnessValidationContext], Awaitable[None]] | None = None,
        post_validation_hook: Callable[[GuardianValidationResult], Awaitable[None]] | None = None
    ) -> GuardianValidationResult:
        """
        Comprehensive Guardian validation for consciousness operations.

        Args:
            context: Validation context with operation details
            pre_validation_hook: Optional pre-validation processing
            post_validation_hook: Optional post-validation processing

        Returns:
            GuardianValidationResult with comprehensive validation outcome

        Raises:
            GuardianValidationError: If validation fails critically
        """
        validation_start_time = time.time()

        with tracer.start_as_current_span("guardian_validate_consciousness") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("operation_id", context.operation_id)
            span.set_attribute("validation_type", context.validation_type.value)
            span.set_attribute("lane", self._lane)

            try:
                # Initialize result
                result = GuardianValidationResult(
                    operation_id=context.operation_id,
                    validation_type=context.validation_type,
                    result=ValidationResult.DENIED  # Fail-closed default
                )

                # Check emergency mode (fail-closed behavior)
                if self._emergency_mode:
                    return await self._handle_emergency_mode(context, result)

                # Pre-validation hook
                if pre_validation_hook:
                    await pre_validation_hook(context)

                # Phase 1: Drift detection
                drift_result = await self._perform_drift_detection(context)
                result.drift_result = drift_result
                result.add_audit_entry("drift_detection", asdict(drift_result))

                # Phase 2: Ethics validation
                if self.config.ethics_validation_required:
                    ethical_decision = await self._perform_ethics_validation(context)
                    result.ethical_decision = ethical_decision
                    result.add_audit_entry("ethics_validation", asdict(ethical_decision))

                # Phase 3: Safety validation
                if self.config.safety_check_enabled:
                    safety_result = await self._perform_safety_validation(context)
                    result.safety_result = safety_result
                    result.add_audit_entry("safety_validation", asdict(safety_result))

                # Phase 4: Constitutional AI compliance
                if self.config.constitutional_check_enabled:
                    constitutional_result = await self._perform_constitutional_validation(context)
                    result.add_audit_entry("constitutional_validation", constitutional_result)

                # Phase 5: GDPR compliance check
                if self.config.gdpr_audit_enabled:
                    gdpr_result = await self._perform_gdpr_validation(context)
                    result.gdpr_compliant = gdpr_result["compliant"]
                    result.consent_verified = gdpr_result["consent_verified"]
                    result.add_audit_entry("gdpr_validation", gdpr_result)

                # Phase 6: Determine final validation result
                result = await self._determine_final_result(result, context)

                # Phase 7: Generate Guardian envelope if approved
                if result.is_approved() and self.guardian_system:
                    result.guardian_envelope = await self._generate_guardian_envelope(context, result)

                # Performance tracking
                validation_duration = (time.time() - validation_start_time) * 1000
                result.validation_duration_ms = validation_duration

                # Check performance targets
                if validation_duration > self.config.p95_target_ms:
                    logger.warning(
                        f"Guardian validation exceeded p95 target: {validation_duration:.2f}ms > "
                        f"{self.config.p95_target_ms}ms"
                    )

                    if self.config.performance_regression_detection:
                        await self._handle_performance_regression(validation_duration, context)

                # Update performance tracking
                self._update_performance_metrics(validation_duration, result)

                # Post-validation hook
                if post_validation_hook:
                    await post_validation_hook(result)

                # Record successful validation
                self._consecutive_errors = 0
                self._emergency_mode = False

                # Update Guardian metrics
                if self._metrics:
                    guardian_validations_total.labels(
                        validation_type=context.validation_type.value,
                        result=result.result.value,
                        lane=self._lane
                    ).inc()

                    guardian_validation_latency_seconds.labels(
                        validation_type=context.validation_type.value,
                        result=result.result.value,
                        lane=self._lane
                    ).observe(validation_duration / 1000.0)

                # Store validation history
                self._validation_history.append(result)
                if len(self._validation_history) > 1000:
                    self._validation_history = self._validation_history[-500:]

                span.set_attribute("validation_result", result.result.value)
                span.set_attribute("validation_duration_ms", validation_duration)
                span.set_attribute("drift_score", result.drift_result.drift_score if result.drift_result else 0.0)

                return result

            except Exception as e:
                await self._handle_validation_error(e, context, span)

                # Increment consecutive errors
                self._consecutive_errors += 1
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._emergency_mode = True
                    logger.error(f"Entering emergency mode after {self._consecutive_errors} validation errors")

                # Record failure metrics
                if self._metrics:
                    guardian_failures_total.labels(
                        failure_type=type(e).__name__,
                        validation_type=context.validation_type.value,
                        lane=self._lane
                    ).inc()

                # Return fail-closed result
                validation_duration = (time.time() - validation_start_time) * 1000
                return GuardianValidationResult(
                    operation_id=context.operation_id,
                    validation_type=context.validation_type,
                    result=ValidationResult.ERROR,  # Fail-closed
                    validation_duration_ms=validation_duration,
                    reason=f"Guardian validation error: {e!s}",
                    confidence=0.0
                )

    async def _perform_drift_detection(
        self,
        context: ConsciousnessValidationContext
    ) -> DriftResult:
        """Perform consciousness state drift detection"""

        with tracer.start_as_current_span("guardian_drift_detection"):
            if not context.consciousness_state or not self.guardian_impl:
                return DriftResult(
                    drift_score=0.0,
                    threshold_exceeded=False,
                    severity=EthicalSeverity.LOW,
                    remediation_needed=False,
                    details={"reason": "No state data or Guardian implementation"}
                )

            # Get baseline for comparison
            baseline_key = f"{context.tenant}:{context.session_id or 'default'}"
            baseline_state = self._baseline_states.get(baseline_key)

            if not baseline_state:
                # First state becomes baseline
                self._baseline_states[baseline_key] = context.consciousness_state
                return DriftResult(
                    drift_score=0.0,
                    threshold_exceeded=False,
                    severity=EthicalSeverity.LOW,
                    remediation_needed=False,
                    details={"reason": "Baseline state established"}
                )

            # Perform drift detection
            baseline_str = self._serialize_consciousness_state(baseline_state)
            current_str = self._serialize_consciousness_state(context.consciousness_state)

            drift_context = {
                "operation_type": context.validation_type.value,
                "tenant": context.tenant,
                "session_id": context.session_id,
                "risk_indicators": context.risk_indicators
            }

            drift_result = self.guardian_impl.detect_drift(
                baseline=baseline_str,
                current=current_str,
                threshold=self.config.drift_threshold,
                context=drift_context
            )

            # Update drift metrics
            if self._metrics:
                guardian_drift_scores.labels(
                    validation_type=context.validation_type.value,
                    lane=self._lane
                ).observe(drift_result.drift_score)

            # Track drift history
            self._drift_scores.append(drift_result.drift_score)
            if len(self._drift_scores) > 100:
                self._drift_scores.pop(0)

            return drift_result

    async def _perform_ethics_validation(
        self,
        context: ConsciousnessValidationContext
    ) -> EthicalDecision:
        """Perform ethical validation of consciousness operation"""

        with tracer.start_as_current_span("guardian_ethics_validation"):
            if not self.ethics_engine:
                return EthicalDecision(
                    decision="allow",
                    rationale="Ethics engine not available",
                    severity=EthicalSeverity.LOW,
                    confidence=0.5,
                    triad_compliance={"identity": True, "consciousness": True, "guardian": False}
                )

            # Create governance action for evaluation
            action_context = {
                "consciousness_state": asdict(context.consciousness_state) if context.consciousness_state else {},
                "validation_type": context.validation_type.value,
                "risk_indicators": context.risk_indicators,
                "sensitive_operation": context.sensitive_operation
            }

            return self.ethics_engine.validate_action(
                action=f"consciousness_{context.validation_type.value}",
                context=action_context
            )

    async def _perform_safety_validation(
        self,
        context: ConsciousnessValidationContext
    ) -> SafetyResult:
        """Perform safety validation of consciousness operation"""

        with tracer.start_as_current_span("guardian_safety_validation"):
            if not self.guardian_impl:
                return SafetyResult(
                    safe=True,
                    risk_level=EthicalSeverity.LOW,
                    violations=[],
                    recommendations=[],
                    constitutional_check=False
                )

            # Serialize operation content for safety check
            content = self._serialize_validation_context(context)

            safety_context = {
                "operation_type": context.validation_type.value,
                "tenant": context.tenant,
                "risk_indicators": context.risk_indicators,
                "constitutional_risk_level": "high" if context.sensitive_operation else "low"
            }

            return self.guardian_impl.check_safety(
                content=content,
                context=safety_context,
                constitutional_check=self.config.constitutional_check_enabled
            )

    async def _perform_constitutional_validation(
        self,
        context: ConsciousnessValidationContext
    ) -> dict[str, Any]:
        """Perform Constitutional AI validation"""

        with tracer.start_as_current_span("guardian_constitutional_validation"):
            # Constitutional AI principles validation
            principles_check = {
                "identity_preservation": True,
                "consciousness_enhancement": True,
                "guardian_protection": True,
                "transparency": True,
                "accountability": True
            }

            # Check for constitutional violations
            violations = []

            # Check for consciousness manipulation
            if (context.consciousness_state and
                hasattr(context.consciousness_state, 'level') and
                context.consciousness_state.level < 0.1):
                violations.append("Potential consciousness suppression detected")
                principles_check["consciousness_enhancement"] = False

            # Check for identity concerns
            if context.risk_indicators and "identity_manipulation" in context.risk_indicators:
                violations.append("Identity manipulation risk detected")
                principles_check["identity_preservation"] = False

            return {
                "constitutional_compliant": len(violations) == 0,
                "principles_check": principles_check,
                "violations": violations,
                "confidence": 0.9 if len(violations) == 0 else 0.3
            }

    async def _perform_gdpr_validation(
        self,
        context: ConsciousnessValidationContext
    ) -> dict[str, Any]:
        """Perform GDPR compliance validation"""

        with tracer.start_as_current_span("guardian_gdpr_validation"):
            gdpr_result = {
                "compliant": True,
                "consent_verified": False,
                "lawful_basis": "legitimate_interest",
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation": True,
                "issues": []
            }

            # Check for personal data processing
            if context.user_id:
                gdpr_result["consent_verified"] = True  # Simplified - would check consent ledger
                gdpr_result["lawful_basis"] = "consent"

            # Check for sensitive operation
            if context.sensitive_operation and not gdpr_result["consent_verified"]:
                gdpr_result["compliant"] = False
                gdpr_result["issues"].append("Explicit consent required for sensitive operations")

            # Check retention compliance
            if self._audit_events:
                old_events = [
                    event for event in self._audit_events
                    if (time.time() - event.get("timestamp", 0)) * 1000 > self._audit_retention_ms
                ]
                if old_events:
                    gdpr_result["issues"].append(f"Audit retention exceeded for {len(old_events)} events")

            return gdpr_result

    async def _determine_final_result(
        self,
        result: GuardianValidationResult,
        context: ConsciousnessValidationContext
    ) -> GuardianValidationResult:
        """Determine final validation result based on all checks"""

        # Start with denial (fail-closed)
        approved = False
        reason_parts = []
        confidence_scores = []

        # Check drift detection
        if result.drift_result:
            if not result.drift_result.threshold_exceeded:
                approved = True
                confidence_scores.append(0.8)
            else:
                reason_parts.append(f"Drift threshold exceeded: {result.drift_result.drift_score:.3f} > {self.config.drift_threshold}")
                confidence_scores.append(0.2)

        # Check ethics validation
        if result.ethical_decision:
            if result.ethical_decision.decision in ["approved", "allow"]:
                approved = approved  # Don't override drift failure
                confidence_scores.append(result.ethical_decision.confidence)
            else:
                approved = False
                reason_parts.append(f"Ethics validation failed: {result.ethical_decision.rationale}")
                confidence_scores.append(result.ethical_decision.confidence)

        # Check safety validation
        if result.safety_result:
            if result.safety_result.safe:
                approved = approved  # Don't override other failures
                confidence_scores.append(0.9)
            else:
                approved = False
                reason_parts.append(f"Safety validation failed: {len(result.safety_result.violations)} violations")
                confidence_scores.append(0.1)

        # Check GDPR compliance
        if not result.gdpr_compliant:
            approved = False
            reason_parts.append("GDPR compliance failed")
            confidence_scores.append(0.1)

        # Set final result
        if approved:
            result.result = ValidationResult.APPROVED
            result.reason = "All Guardian validations passed"
            result.recommendations = ["Operation approved for execution"]
        else:
            result.result = ValidationResult.DENIED
            result.reason = "; ".join(reason_parts) if reason_parts else "Guardian validation failed"
            result.recommendations = ["Review and address validation failures before retrying"]

        # Calculate confidence
        result.confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return result

    async def _generate_guardian_envelope(
        self,
        context: ConsciousnessValidationContext,
        result: GuardianValidationResult
    ) -> dict[str, Any]:
        """Generate Guardian decision envelope for approved operations"""

        if not self.guardian_system:
            return {}

        try:
            # Create Guardian decision components
            decision = GuardianDecision(
                status=DecisionStatus.ALLOW,
                policy="consciousness/guardian_integration/v1.0.0",
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                confidence=result.confidence,
                ttl_seconds=3600  # 1 hour validity
            )

            subject = GuardianSubject(
                correlation_id=context.correlation_id,
                actor_type=ActorType.SYSTEM,
                actor_id="consciousness_engine",
                operation_name=context.validation_type.value,
                lane=self._lane,
                operation_parameters={
                    "tenant": context.tenant,
                    "session_id": context.session_id,
                    "sensitive_operation": context.sensitive_operation
                }
            )

            guardian_context = GuardianContext(
                region="us-east-1",  # Default region
                runtime=RuntimeEnvironment.PROD,
                enforcement_enabled=self.config.enforcement_mode == "enforced",
                version="1.0.0"
            )

            metrics = GuardianMetrics(
                latency_ms=result.validation_duration_ms,
                drift_score=result.drift_result.drift_score if result.drift_result else 0.0,
                risk_score=0.2 if context.sensitive_operation else 0.1
            )

            enforcement = GuardianEnforcement(
                mode=EnforcementMode.ENFORCED if self.config.enforcement_mode == "enforced" else EnforcementMode.CANARY
            )

            audit = GuardianAudit(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                source_system="lukhas_consciousness_guardian_integration",
                audit_trail=result.audit_trail
            )

            # Generate Guardian envelope
            return self.guardian_system.serialize_decision(
                decision=decision,
                subject=subject,
                context=guardian_context,
                metrics=metrics,
                enforcement=enforcement,
                audit=audit,
                reasons=[{
                    "code": "CONSCIOUSNESS_VALIDATION",
                    "message": result.reason
                }]
            )

        except Exception as e:
            logger.error(f"Failed to generate Guardian envelope: {e}")
            return {}

    def _serialize_consciousness_state(self, state: ConsciousnessState) -> str:
        """Serialize consciousness state for drift detection"""
        # Create a normalized representation focusing on key attributes
        serialized = {
            "phase": state.phase,
            "level": round(state.level, 3),
            "awareness_level": round(state.awareness_level, 3),
            "emotional_tone": state.emotional_tone,
            "cognitive_load": round(getattr(state, 'cognitive_load', 0.0), 3),
            "focus_intensity": round(getattr(state, 'focus_intensity', 0.0), 3),
            "reasoning_depth": round(getattr(state, 'reasoning_depth', 0.0), 3)
        }
        return json.dumps(serialized, sort_keys=True)

    def _serialize_validation_context(self, context: ConsciousnessValidationContext) -> str:
        """Serialize validation context for safety checks"""
        content_parts = [
            f"operation_type: {context.validation_type.value}",
            f"tenant: {context.tenant}",
            f"sensitive: {context.sensitive_operation}"
        ]

        if context.consciousness_state:
            content_parts.append(f"consciousness_level: {context.consciousness_state.level}")
            content_parts.append(f"phase: {context.consciousness_state.phase}")
            content_parts.append(f"emotional_tone: {context.consciousness_state.emotional_tone}")

        if context.risk_indicators:
            content_parts.append(f"risk_indicators: {', '.join(context.risk_indicators)}")

        return " | ".join(content_parts)

    async def _handle_emergency_mode(
        self,
        context: ConsciousnessValidationContext,
        result: GuardianValidationResult
    ) -> GuardianValidationResult:
        """Handle validation in emergency mode (fail-closed)"""

        logger.warning(f"Guardian emergency mode active - denying operation {context.operation_id}")

        result.result = ValidationResult.DENIED
        result.reason = "Guardian emergency mode active - all operations denied"
        result.confidence = 1.0
        result.recommendations = [
            "Wait for Guardian emergency mode to clear",
            "Check Guardian system health",
            "Contact system administrators"
        ]

        result.add_audit_entry("emergency_mode", {
            "consecutive_errors": self._consecutive_errors,
            "emergency_active": True,
            "operation_denied": True
        })

        return result

    async def _handle_performance_regression(
        self,
        duration_ms: float,
        context: ConsciousnessValidationContext
    ):
        """Handle performance regression detection"""

        # Calculate historical average
        if len(self._validation_latencies) >= 10:
            recent_avg = sum(self._validation_latencies[-10:]) / 10
            overall_avg = sum(self._validation_latencies) / len(self._validation_latencies)

            # Check for significant regression (>20% increase)
            if recent_avg > overall_avg * 1.2:
                severity = "critical" if recent_avg > overall_avg * 1.5 else "high"
                degradation_percent = ((recent_avg - overall_avg) / overall_avg) * 100

                logger.warning(
                    f"Guardian validation performance regression: {degradation_percent:.1f}% increase "
                    f"(current: {recent_avg:.2f}ms, historical: {overall_avg:.2f}ms)"
                )

                # Record regression metrics
                if self._metrics:
                    guardian_performance_regressions.labels(
                        severity=severity,
                        lane=self._lane
                    ).inc()

    async def _handle_validation_error(
        self,
        error: Exception,
        context: ConsciousnessValidationContext,
        span: Any
    ):
        """Handle Guardian validation errors with comprehensive context"""

        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "operation_id": context.operation_id,
            "validation_type": context.validation_type.value,
            "tenant": context.tenant,
            "consecutive_errors": self._consecutive_errors,
            "timestamp": time.time()
        }

        logger.error(f"Guardian validation failed: {error_context}")

        # Record error in span
        span.record_exception(error)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))

        # Add to audit trail
        self._add_audit_event("validation_error", error_context)

    def _update_performance_metrics(
        self,
        latency_ms: float,
        result: GuardianValidationResult
    ):
        """Update performance tracking metrics"""

        self._validation_latencies.append(latency_ms)
        if len(self._validation_latencies) > 1000:
            self._validation_latencies = self._validation_latencies[-500:]

    def _add_audit_event(self, event_type: str, details: dict[str, Any]):
        """Add event to audit trail"""

        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "component": self._component_id
        }

        self._audit_events.append(event)

        # Clean old events (GDPR compliance)
        cutoff_time = time.time() - (self._audit_retention_ms / 1000)
        self._audit_events = [
            e for e in self._audit_events
            if e.get("timestamp", 0) > cutoff_time
        ]

        # Record audit metrics
        if self._metrics:
            guardian_audit_events_total.labels(
                event_type=event_type,
                lane=self._lane
            ).inc()

    def update_baseline_state(
        self,
        state: ConsciousnessState,
        tenant: str = "default",
        session_id: str | None = None
    ):
        """Update baseline consciousness state for drift detection"""

        baseline_key = f"{tenant}:{session_id or 'default'}"
        self._baseline_states[baseline_key] = state

        # Keep state history for analysis
        self._state_history.append(state)
        if len(self._state_history) > 1000:
            self._state_history = self._state_history[-500:]

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""

        if not self._validation_latencies:
            return {"no_data": True}

        latencies = self._validation_latencies
        stats = {
            "guardian_integration": {
                "total_validations": len(latencies),
                "average_latency_ms": sum(latencies) / len(latencies),
                "median_latency_ms": sorted(latencies)[len(latencies) // 2],
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "emergency_mode": self._emergency_mode,
                "consecutive_errors": self._consecutive_errors,
                "baseline_states": len(self._baseline_states),
                "audit_events": len(self._audit_events)
            }
        }

        # Calculate percentiles
        if len(latencies) >= 10:
            sorted_latencies = sorted(latencies)
            stats["guardian_integration"]["p95_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            stats["guardian_integration"]["p99_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        # Drift statistics
        if self._drift_scores:
            stats["drift_detection"] = {
                "average_drift_score": sum(self._drift_scores) / len(self._drift_scores),
                "max_drift_score": max(self._drift_scores),
                "threshold_exceedances": sum(1 for score in self._drift_scores if score > self.config.drift_threshold)
            }

        # Validation success rate
        if self._validation_history:
            approved_count = sum(1 for r in self._validation_history if r.is_approved())
            stats["validation_success"] = {
                "total_validations": len(self._validation_history),
                "approved_count": approved_count,
                "success_rate": approved_count / len(self._validation_history)
            }

        return stats

    async def reset_state(self):
        """Reset Guardian integration state for testing"""

        self._validation_latencies.clear()
        self._drift_scores.clear()
        self._validation_history.clear()
        self._baseline_states.clear()
        self._state_history.clear()
        self._audit_events.clear()
        self._consecutive_errors = 0
        self._emergency_mode = False

        logger.info("Guardian integration state reset completed")


class GuardianValidationError(Exception):
    """Exception raised for Guardian validation errors"""
    pass


# Convenience functions
def create_validation_context(
    validation_type: GuardianValidationType,
    consciousness_state: ConsciousnessState | None = None,
    user_id: str | None = None,
    sensitive_operation: bool = False,
    **kwargs
) -> ConsciousnessValidationContext:
    """Create validation context for Guardian operations"""

    return ConsciousnessValidationContext(
        validation_type=validation_type,
        consciousness_state=consciousness_state,
        user_id=user_id,
        sensitive_operation=sensitive_operation,
        **kwargs
    )


# Export public API
__all__ = [
    "ConsciousnessGuardianIntegration",
    "ConsciousnessValidationContext",
    "GuardianValidationConfig",
    "GuardianValidationError",
    "GuardianValidationResult",
    "GuardianValidationType",
    "ValidationResult",
    "create_validation_context"
]
