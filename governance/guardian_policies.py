#!/usr/bin/env python3
"""
LUKHAS Guardian Policies Engine - G.3 Implementation

Advanced policy evaluation engine with configurable rules and actions.
Implements standardized Guardian response schema with comprehensive validation.

T4/0.01% Excellence: High-performance policy engine with Guardian integration.
"""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs): return self
    def inc(self, amount=1): pass
    def observe(self, amount): pass
    def set(self, value): pass

try:
    policy_evaluations_total = Counter(
        'lukhas_guardian_policy_evaluations_total',
        'Total policy evaluations',
        ['policy_type', 'decision', 'component']
    )
    policy_evaluation_latency = Histogram(
        'lukhas_guardian_policy_evaluation_latency_seconds',
        'Policy evaluation latency',
        ['policy_type'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
    active_policies_gauge = Gauge(
        'lukhas_guardian_active_policies_total',
        'Number of active policies',
        ['policy_type']
    )
except ValueError:
    policy_evaluations_total = MockMetric()
    policy_evaluation_latency = MockMetric()
    active_policies_gauge = MockMetric()


class DecisionType(Enum):
    """Guardian policy decisions."""
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"
    DEFER = "defer"


class SeverityLevel(Enum):
    """Severity levels for policy reasons."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of actions Guardian can take."""
    LOG = "log"
    ALERT = "alert"
    THROTTLE = "throttle"
    BLOCK = "block"
    AUDIT = "audit"


@dataclass
class PolicyReason:
    """Reason for a policy decision."""
    code: str
    message: str
    severity: SeverityLevel
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value
        }
        if self.details:
            result["details"] = self.details
        return result


@dataclass
class PolicyAction:
    """Action to be taken based on policy decision."""
    type: ActionType
    target: str
    parameters: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "type": self.type.value,
            "target": self.target
        }
        if self.parameters:
            result["parameters"] = self.parameters
        return result


@dataclass
class PolicyContext:
    """Context information for policy evaluation."""
    operation_type: str
    component: str
    user_id: str | None = None
    tier: str | None = None
    lane: str | None = None
    request_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"operation_type": self.operation_type, "component": self.component}
        if self.user_id:
            result["user_id"] = self.user_id
        if self.tier:
            result["tier"] = self.tier
        if self.lane:
            result["lane"] = self.lane
        return result


@dataclass
class GuardianResponse:
    """Standardized Guardian response following G.3 schema."""
    schema_version: str
    timestamp: float
    correlation_id: str
    emergency_active: bool
    enforcement_enabled: bool
    decision: DecisionType
    reasons: list[PolicyReason] = field(default_factory=list)
    metrics: dict[str, Any] | None = None
    context: PolicyContext | None = None
    actions: list[PolicyAction] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "schema_version": self.schema_version,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "emergency_active": self.emergency_active,
            "enforcement_enabled": self.enforcement_enabled,
            "decision": self.decision.value,
            "reasons": [reason.to_dict() for reason in self.reasons]
        }

        if self.metrics:
            result["metrics"] = self.metrics

        if self.context:
            result["context"] = self.context.to_dict()

        if self.actions:
            result["actions"] = [action.to_dict() for action in self.actions]

        return result


class PolicyRule:
    """Base class for policy rules."""

    def __init__(self, name: str, enabled: bool = True, priority: int = 100):
        self.name = name
        self.enabled = enabled
        self.priority = priority

    def evaluate(self, context: PolicyContext, request_data: dict[str, Any]) -> PolicyReason | None:
        """
        Evaluate the policy rule.

        Returns:
            PolicyReason if rule is violated, None if rule passes
        """
        raise NotImplementedError

    def __str__(self) -> str:
        return f"PolicyRule({self.name})"


class DriftThresholdPolicy(PolicyRule):
    """Policy to check drift score against thresholds."""

    def __init__(self, threshold: float = 0.15, **kwargs):
        super().__init__(name="drift_threshold", **kwargs)
        self.threshold = threshold

    def evaluate(self, context: PolicyContext, request_data: dict[str, Any]) -> PolicyReason | None:
        """Check if drift score exceeds threshold."""
        drift_score = request_data.get("drift_score", 0.0)

        if drift_score > self.threshold:
            return PolicyReason(
                code="DRIFT_THRESHOLD_EXCEEDED",
                message=f"Drift score {drift_score:.3f} exceeds threshold {self.threshold}",
                severity=SeverityLevel.HIGH if drift_score > self.threshold * 1.5 else SeverityLevel.MEDIUM,
                details={
                    "current_drift": drift_score,
                    "threshold": self.threshold,
                    "excess": drift_score - self.threshold
                }
            )
        return None


class RateLimitPolicy(PolicyRule):
    """Policy to enforce rate limits per component/operation."""

    def __init__(self, requests_per_minute: int = 100, **kwargs):
        super().__init__(name="rate_limit", **kwargs)
        self.requests_per_minute = requests_per_minute
        self._request_counts: dict[str, list[float]] = {}

    def evaluate(self, context: PolicyContext, request_data: dict[str, Any]) -> PolicyReason | None:
        """Check if request rate exceeds limits."""
        key = f"{context.component}:{context.operation_type}"
        current_time = time.time()

        # Initialize tracking for this key
        if key not in self._request_counts:
            self._request_counts[key] = []

        # Clean old requests (older than 1 minute)
        cutoff_time = current_time - 60
        self._request_counts[key] = [
            timestamp for timestamp in self._request_counts[key]
            if timestamp > cutoff_time
        ]

        # Add current request
        self._request_counts[key].append(current_time)

        # Check if rate limit exceeded
        if len(self._request_counts[key]) > self.requests_per_minute:
            return PolicyReason(
                code="RATE_LIMIT_EXCEEDED",
                message=f"Rate limit exceeded: {len(self._request_counts[key])} requests in last minute (limit: {self.requests_per_minute})",
                severity=SeverityLevel.MEDIUM,
                details={
                    "current_rate": len(self._request_counts[key]),
                    "limit": self.requests_per_minute,
                    "key": key
                }
            )
        return None


class TierAccessPolicy(PolicyRule):
    """Policy to validate tier-based access control."""

    def __init__(self, **kwargs):
        super().__init__(name="tier_access", **kwargs)
        self.tier_permissions = {
            "T1": {"memory": ["read"], "consciousness": [], "identity": ["public"]},
            "T2": {"memory": ["read", "write"], "consciousness": ["basic"], "identity": ["auth"]},
            "T3": {"memory": ["read", "write"], "consciousness": ["basic", "reflect"], "identity": ["auth", "mfa"]},
            "T4": {"memory": ["read", "write", "admin"], "consciousness": ["basic", "reflect", "dream"], "identity": ["auth", "mfa", "webauthn"]},
            "T5": {"memory": ["read", "write", "admin"], "consciousness": ["full"], "identity": ["full"]}
        }

    def evaluate(self, context: PolicyContext, request_data: dict[str, Any]) -> PolicyReason | None:
        """Check if tier has permission for the operation."""
        if not context.tier:
            return None  # No tier restriction

        required_permission = request_data.get("required_permission")
        if not required_permission:
            return None  # No permission requirement

        tier_perms = self.tier_permissions.get(context.tier, {})
        component_perms = tier_perms.get(context.component, [])

        if required_permission not in component_perms:
            return PolicyReason(
                code="INSUFFICIENT_TIER",
                message=f"Tier {context.tier} lacks permission '{required_permission}' for component '{context.component}'",
                severity=SeverityLevel.HIGH,
                details={
                    "tier": context.tier,
                    "required_permission": required_permission,
                    "component": context.component,
                    "available_permissions": component_perms
                }
            )
        return None


class EmergencyStopPolicy(PolicyRule):
    """Policy to check for emergency stop conditions."""

    def __init__(self, **kwargs):
        super().__init__(name="emergency_stop", priority=1, **kwargs)  # Highest priority

    def evaluate(self, context: PolicyContext, request_data: dict[str, Any]) -> PolicyReason | None:
        """Check for emergency stop conditions."""
        # Check for emergency file
        emergency_file = Path("/tmp/guardian_emergency_disable")
        if emergency_file.exists():
            return PolicyReason(
                code="EMERGENCY_STOP_ACTIVE",
                message="Emergency stop is active - all operations blocked",
                severity=SeverityLevel.CRITICAL,
                details={"emergency_file": str(emergency_file)}
            )

        # Check for critical system state
        if request_data.get("system_state") == "critical":
            return PolicyReason(
                code="CRITICAL_SYSTEM_STATE",
                message="System in critical state - risky operations blocked",
                severity=SeverityLevel.CRITICAL,
                details={"system_state": "critical"}
            )

        return None


class GuardianPoliciesEngine:
    """Guardian Policies Engine implementing G.3 standardized responses."""

    def __init__(self):
        """Initialize the policies engine."""
        self.schema_version = "1.0.0"
        self.policies: dict[str, PolicyRule] = {}
        self._load_default_policies()

        # Performance tracking
        self._evaluation_start_time = None

    def _load_default_policies(self):
        """Load default LUKHAS policies."""
        default_policies = [
            EmergencyStopPolicy(),
            DriftThresholdPolicy(threshold=0.15),
            RateLimitPolicy(requests_per_minute=100),
            TierAccessPolicy()
        ]

        for policy in default_policies:
            self.add_policy(policy)

        # Update metrics
        for policy_type in ["emergency", "drift", "rate_limit", "tier_access"]:
            active_policies_gauge.labels(policy_type=policy_type).set(1)

    def add_policy(self, policy: PolicyRule):
        """Add a policy to the engine."""
        self.policies[policy.name] = policy

    def remove_policy(self, name: str):
        """Remove a policy from the engine."""
        if name in self.policies:
            del self.policies[name]

    def evaluate_policies(self,
                         context: PolicyContext,
                         request_data: dict[str, Any] | None = None) -> GuardianResponse:
        """
        Evaluate all policies and return standardized Guardian response.

        Args:
            context: Policy evaluation context
            request_data: Request-specific data for policy evaluation

        Returns:
            GuardianResponse following G.3 schema
        """
        with tracer.start_span("guardian.evaluate_policies") as span:
            start_time = time.time()
            correlation_id = str(uuid.uuid4())

            request_data = request_data or {}

            # Check system state
            emergency_active = self._check_emergency_state()
            enforcement_enabled = self._check_enforcement_enabled()

            span.set_attribute("guardian.correlation_id", correlation_id)
            span.set_attribute("guardian.component", context.component)
            span.set_attribute("guardian.operation", context.operation_type)

            reasons: list[PolicyReason] = []
            actions: list[PolicyAction] = []

            # Evaluate policies in priority order
            active_policies = [p for p in self.policies.values() if p.enabled]
            active_policies.sort(key=lambda p: p.priority)

            policies_evaluated = 0

            try:
                for policy in active_policies:
                    with policy_evaluation_latency.labels(policy_type=policy.name).time():
                        reason = policy.evaluate(context, request_data)
                        policies_evaluated += 1

                        if reason:
                            reasons.append(reason)
                            span.set_attribute(f"guardian.policy.{policy.name}.violated", True)

                            # Add automatic actions based on severity
                            if reason.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                                actions.extend(self._get_severity_actions(reason, context))

                        else:
                            span.set_attribute(f"guardian.policy.{policy.name}.violated", False)

                # Determine final decision
                decision = self._make_decision(reasons, emergency_active, enforcement_enabled)

                # Record metrics
                processing_time_ms = (time.time() - start_time) * 1000

                metrics = {
                    "processing_time_ms": processing_time_ms,
                    "drift_score": request_data.get("drift_score", 0.0),
                    "confidence_score": self._calculate_confidence(reasons, policies_evaluated),
                    "policies_evaluated": policies_evaluated,
                    "circuit_breaker_state": "closed"  # TODO: Integrate with actual circuit breaker
                }

                # Create response
                response = GuardianResponse(
                    schema_version=self.schema_version,
                    timestamp=time.time(),
                    correlation_id=correlation_id,
                    emergency_active=emergency_active,
                    enforcement_enabled=enforcement_enabled,
                    decision=decision,
                    reasons=reasons,
                    metrics=metrics,
                    context=context,
                    actions=actions
                )

                # Update Prometheus metrics
                policy_evaluations_total.labels(
                    policy_type="all",
                    decision=decision.value,
                    component=context.component
                ).inc()

                span.set_attribute("guardian.decision", decision.value)
                span.set_attribute("guardian.reasons_count", len(reasons))
                span.set_attribute("guardian.processing_time_ms", processing_time_ms)

                return response

            except Exception as e:
                # Error handling - return safe response
                span.set_attribute("guardian.error", str(e))

                error_response = GuardianResponse(
                    schema_version=self.schema_version,
                    timestamp=time.time(),
                    correlation_id=correlation_id,
                    emergency_active=True,  # Fail safe
                    enforcement_enabled=enforcement_enabled,
                    decision=DecisionType.DENY,
                    reasons=[PolicyReason(
                        code="POLICY_EVALUATION_ERROR",
                        message=f"Error during policy evaluation: {e!s}",
                        severity=SeverityLevel.CRITICAL,
                        details={"error": str(e)}
                    )],
                    metrics={"processing_time_ms": (time.time() - start_time) * 1000},
                    context=context
                )

                policy_evaluations_total.labels(
                    policy_type="error",
                    decision="deny",
                    component=context.component
                ).inc()

                return error_response

    def _check_emergency_state(self) -> bool:
        """Check if emergency state is active."""
        emergency_file = Path("/tmp/guardian_emergency_disable")
        return emergency_file.exists()

    def _check_enforcement_enabled(self) -> bool:
        """Check if policy enforcement is enabled."""
        return os.getenv("LUKHAS_GUARDIAN_ENFORCEMENT", "1") != "0"

    def _make_decision(self,
                      reasons: list[PolicyReason],
                      emergency_active: bool,
                      enforcement_enabled: bool) -> DecisionType:
        """Make final policy decision based on reasons and system state."""
        if emergency_active:
            return DecisionType.DENY

        if not enforcement_enabled:
            return DecisionType.ALLOW

        if not reasons:
            return DecisionType.ALLOW

        # Check severity levels
        critical_reasons = [r for r in reasons if r.severity == SeverityLevel.CRITICAL]
        high_reasons = [r for r in reasons if r.severity == SeverityLevel.HIGH]

        if critical_reasons:
            return DecisionType.DENY
        elif high_reasons or len(reasons) > 3:
            return DecisionType.REVIEW
        else:
            return DecisionType.ALLOW  # Low severity issues don't block

    def _calculate_confidence(self, reasons: list[PolicyReason], policies_evaluated: int) -> float:
        """Calculate confidence score for the decision."""
        if policies_evaluated == 0:
            return 0.0

        # Base confidence on policy coverage and reason severity
        base_confidence = min(policies_evaluated / len(self.policies), 1.0)

        # Reduce confidence based on severe reasons
        severe_penalty = sum(
            0.2 if r.severity == SeverityLevel.CRITICAL else
            0.1 if r.severity == SeverityLevel.HIGH else
            0.05
            for r in reasons
        )

        return max(base_confidence - severe_penalty, 0.0)

    def _get_severity_actions(self, reason: PolicyReason, context: PolicyContext) -> list[PolicyAction]:
        """Get automatic actions based on reason severity."""
        actions = []

        if reason.severity == SeverityLevel.CRITICAL:
            actions.extend([
                PolicyAction(ActionType.LOG, "security_log", {
                    "level": "critical",
                    "category": "policy_violation",
                    "immediate": True
                }),
                PolicyAction(ActionType.ALERT, "ops_team", {
                    "severity": "critical",
                    "escalation_delay": 0
                }),
                PolicyAction(ActionType.AUDIT, "compliance_log", {
                    "violation_type": reason.code,
                    "component": context.component
                })
            ])

        elif reason.severity == SeverityLevel.HIGH:
            actions.extend([
                PolicyAction(ActionType.LOG, "security_log", {
                    "level": "warning",
                    "category": "policy_violation"
                }),
                PolicyAction(ActionType.ALERT, "ops_team", {
                    "severity": "high",
                    "escalation_delay": 300
                })
            ])

        return actions

    def get_policy_stats(self) -> dict[str, Any]:
        """Get policy engine statistics."""
        return {
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.enabled]),
            "policies": {
                name: {
                    "name": policy.name,
                    "enabled": policy.enabled,
                    "priority": policy.priority,
                    "type": type(policy).__name__
                }
                for name, policy in self.policies.items()
            }
        }


# Global policies engine instance
_policies_engine: GuardianPoliciesEngine | None = None

def get_guardian_policies_engine() -> GuardianPoliciesEngine:
    """Get the default Guardian policies engine instance."""
    global _policies_engine
    if _policies_engine is None:
        _policies_engine = GuardianPoliciesEngine()
    return _policies_engine
