#!/usr/bin/env python3
"""
Plan Verifier - Fail-Closed Constraints on Action Plans
=======================================================

Task 5: Deterministic verification of action plans before execution
to ensure safe, compliant, and resource-bounded orchestration.

Features:
- Deterministic allow/deny decisions (same plan+ctx → same result)
- Ethics guard, resource caps, loop limits, external-call whitelist
- Comprehensive telemetry and audit ledger integration
- <5% p95 latency impact on orchestration hot path

#TAG:orchestration
#TAG:safety
#TAG:task5
"""
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Prometheus metrics for telemetry
try:
    from prometheus_client import Counter, Histogram
    METRICS_AVAILABLE = True
except ImportError:
    # Graceful fallback for test environments
    class _NoopMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    Counter = Histogram = lambda *args, **kwargs: _NoopMetric()
    METRICS_AVAILABLE = False

# Plan verifier metrics
PLAN_VERIFIER_ATTEMPTS = Counter(
    'plan_verifier_attempts_total',
    'Total plan verification attempts',
    ['result']  # allow, deny
)

PLAN_VERIFIER_DENIALS = Counter(
    'plan_verifier_denials_total',
    'Total plan denials by reason',
    ['reason']  # ethics, resources, loops, external_calls, invalid
)

PLAN_VERIFIER_DURATION = Histogram(
    'plan_verifier_p95_ms',
    'Plan verification duration in milliseconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 25.0, 50.0]
)


class VerificationResult(Enum):
    """Plan verification outcomes."""
    ALLOW = "allow"
    DENY = "deny"


class DenialReason(Enum):
    """Standardized denial reasons for ledger."""
    ETHICS_VIOLATION = "ethics_violation"
    RESOURCE_EXCEEDED = "resource_exceeded"
    LOOP_DETECTED = "loop_detected"
    EXTERNAL_CALL_BLOCKED = "external_call_blocked"
    INVALID_PLAN = "invalid_plan"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class VerificationContext:
    """Context information for plan verification."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class VerificationOutcome:
    """Result of plan verification."""
    allow: bool
    reasons: List[str]
    context: VerificationContext
    plan_hash: str
    verification_time_ms: float

    @property
    def result(self) -> VerificationResult:
        return VerificationResult.ALLOW if self.allow else VerificationResult.DENY


class PlanVerifier:
    """
    Deterministic plan verifier with fail-closed safety constraints.

    Implements strict verification of action plans before execution to ensure
    ethical compliance, resource bounds, and operational safety.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plan verifier with configuration.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

        # Load constraints from config/environment
        self.max_execution_time = self.config.get(
            'max_execution_time',
            float(os.getenv('PLAN_MAX_EXECUTION_TIME', '300'))  # 5 minutes
        )
        self.max_memory_mb = self.config.get(
            'max_memory_mb',
            int(os.getenv('PLAN_MAX_MEMORY_MB', '1024'))  # 1GB
        )
        self.max_loop_iterations = self.config.get(
            'max_loop_iterations',
            int(os.getenv('PLAN_MAX_LOOPS', '100'))
        )

        # External call whitelist
        self.allowed_external_domains = set(self.config.get(
            'allowed_external_domains',
            os.getenv('PLAN_ALLOWED_DOMAINS', 'openai.com,api.openai.com,anthropic.com').split(',')
        ))

        # Ethics constraints
        self.ethics_enabled = self.config.get(
            'ethics_enabled',
            os.getenv('PLAN_ETHICS_ENABLED', '1') == '1'
        )

        # Audit ledger
        self.verification_ledger = []

        logger.info(f"PlanVerifier initialized: ethics={self.ethics_enabled}, "
                   f"max_time={self.max_execution_time}s, max_memory={self.max_memory_mb}MB, "
                   f"max_loops={self.max_loop_iterations}, domains={len(self.allowed_external_domains)}")

    def verify(self, plan: Dict[str, Any], ctx: VerificationContext) -> VerificationOutcome:
        """
        Verify action plan against all constraints.

        Deterministic: same plan+ctx → same allow/deny + same reasons

        Args:
            plan: Action plan to verify (must be JSON-serializable)
            ctx: Verification context

        Returns:
            VerificationOutcome with allow/deny decision and reasons
        """
        start_time = time.perf_counter()

        try:
            # Generate deterministic plan hash for caching/deduplication
            plan_hash = self._hash_plan(plan, ctx)

            # Run verification constraints
            violations = []

            # 1. Validate plan structure (early exit on invalid plan)
            if not isinstance(plan, dict):
                violations.append("invalid_plan_structure: plan must be dict")
                # Early exit for completely invalid plans
                allow = False
                reasons = violations
                verification_time_ms = (time.perf_counter() - start_time) * 1000

                outcome = VerificationOutcome(
                    allow=allow,
                    reasons=reasons,
                    context=ctx,
                    plan_hash="invalid_plan",
                    verification_time_ms=verification_time_ms
                )

                if METRICS_AVAILABLE:
                    PLAN_VERIFIER_ATTEMPTS.labels(result="deny").inc()
                    PLAN_VERIFIER_DENIALS.labels(reason=DenialReason.INVALID_PLAN.value).inc()
                    PLAN_VERIFIER_DURATION.observe(verification_time_ms)

                self._record_verification(outcome)
                return outcome

            structure_violations = self._check_plan_structure(plan)
            violations.extend(structure_violations)

            # 2. Ethics guard check
            if self.ethics_enabled:
                ethics_violations = self._check_ethics_constraints(plan, ctx)
                violations.extend(ethics_violations)

            # 3. Resource limits check
            resource_violations = self._check_resource_constraints(plan)
            violations.extend(resource_violations)

            # 4. Loop detection
            loop_violations = self._check_loop_constraints(plan)
            violations.extend(loop_violations)

            # 5. External call whitelist
            external_violations = self._check_external_call_constraints(plan)
            violations.extend(external_violations)

            # Determine outcome
            allow = len(violations) == 0
            reasons = [v for v in violations] if violations else ["all_constraints_passed"]

            # Calculate verification time
            verification_time_ms = (time.perf_counter() - start_time) * 1000

            # Create outcome
            outcome = VerificationOutcome(
                allow=allow,
                reasons=reasons,
                context=ctx,
                plan_hash=plan_hash,
                verification_time_ms=verification_time_ms
            )

            # Record metrics
            if METRICS_AVAILABLE:
                PLAN_VERIFIER_ATTEMPTS.labels(result=outcome.result.value).inc()
                PLAN_VERIFIER_DURATION.observe(verification_time_ms)

                if not allow:
                    for reason in reasons:
                        # Map reasons to standardized denial reasons
                        denial_reason = self._map_to_denial_reason(reason)
                        PLAN_VERIFIER_DENIALS.labels(reason=denial_reason.value).inc()

            # Record in audit ledger
            self._record_verification(outcome)

            logger.info(f"Plan verification: {outcome.result.value} "
                       f"({verification_time_ms:.2f}ms, hash={plan_hash[:8]})")

            return outcome

        except Exception as e:
            verification_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Plan verification error: {e}")

            # Fail closed on error
            outcome = VerificationOutcome(
                allow=False,
                reasons=[f"verification_error: {str(e)}"],
                context=ctx,
                plan_hash="error",
                verification_time_ms=verification_time_ms
            )

            if METRICS_AVAILABLE:
                PLAN_VERIFIER_ATTEMPTS.labels(result="deny").inc()
                PLAN_VERIFIER_DENIALS.labels(reason=DenialReason.UNKNOWN_ERROR.value).inc()
                PLAN_VERIFIER_DURATION.observe(verification_time_ms)

            self._record_verification(outcome)
            return outcome

    def _hash_plan(self, plan: Dict[str, Any], ctx: VerificationContext) -> str:
        """Generate deterministic hash of plan and relevant context."""
        # Create normalized representation for hashing
        normalized = {
            'plan': plan,
            'user_id': ctx.user_id,
            'session_id': ctx.session_id,
            # Note: deliberately excluding timestamp for determinism
        }

        # Convert to deterministic string and hash
        plan_str = repr(sorted(normalized.items()))
        return hashlib.sha256(plan_str.encode()).hexdigest()

    def _check_plan_structure(self, plan: Dict[str, Any]) -> List[str]:
        """Validate basic plan structure."""
        violations = []

        if not isinstance(plan, dict):
            violations.append("invalid_plan_structure: plan must be dict")
            return violations

        # Required fields
        required_fields = ['action', 'params']
        for field in required_fields:
            if field not in plan:
                violations.append(f"invalid_plan_structure: missing_field_{field}")

        # Action must be string
        if 'action' in plan and not isinstance(plan['action'], str):
            violations.append("invalid_plan_structure: action_must_be_string")

        return violations

    def _check_ethics_constraints(self, plan: Dict[str, Any], ctx: VerificationContext) -> List[str]:
        """Check ethics guard constraints."""
        violations = []

        action = plan.get('action', '')
        params = plan.get('params', {})

        # Block harmful actions (safely handle non-string actions)
        harmful_actions = {'delete_user_data', 'access_private_info', 'manipulate_system'}
        if isinstance(action, str) and action in harmful_actions:
            violations.append(f"ethics_violation: harmful_action_{action}")

        # Block manipulation attempts
        params_str = str(params).lower()
        if any(term in params_str for term in ['hack', 'exploit', 'bypass']):
            violations.append("ethics_violation: manipulation_detected")

        # Check for data exfiltration patterns
        if isinstance(action, str) and action == 'external_call' and 'sensitive' in params_str:
            violations.append("ethics_violation: potential_data_exfiltration")

        return violations

    def _check_resource_constraints(self, plan: Dict[str, Any]) -> List[str]:
        """Check resource limit constraints."""
        violations = []

        params = plan.get('params', {})

        # Execution time limits
        estimated_time = params.get('estimated_time_seconds', 0)
        if estimated_time > self.max_execution_time:
            violations.append(f"resource_exceeded: execution_time_{estimated_time}s > {self.max_execution_time}s")

        # Memory limits
        estimated_memory = params.get('estimated_memory_mb', 0)
        if estimated_memory > self.max_memory_mb:
            violations.append(f"resource_exceeded: memory_{estimated_memory}MB > {self.max_memory_mb}MB")

        # Large batch operations
        batch_size = params.get('batch_size', 0)
        if batch_size > 1000:
            violations.append(f"resource_exceeded: batch_size_{batch_size} > 1000")

        return violations

    def _check_loop_constraints(self, plan: Dict[str, Any]) -> List[str]:
        """Check for loop limit violations."""
        violations = []

        params = plan.get('params', {})

        # Direct loop iteration limits
        iterations = params.get('iterations', params.get('max_iterations', 0))
        if iterations > self.max_loop_iterations:
            violations.append(f"loop_detected: iterations_{iterations} > {self.max_loop_iterations}")

        # Recursive call depth
        recursion_depth = params.get('recursion_depth', 0)
        if recursion_depth > 10:
            violations.append(f"loop_detected: recursion_depth_{recursion_depth} > 10")

        return violations

    def _check_external_call_constraints(self, plan: Dict[str, Any]) -> List[str]:
        """Check external call whitelist constraints."""
        violations = []

        action = plan.get('action', '')
        params = plan.get('params', {})

        if isinstance(action, str) and (action == 'external_call' or 'external' in action):
            url = params.get('url', '')
            domain = params.get('domain', '')

            # Extract domain from URL if provided
            if url and not domain:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                except:
                    domain = ''

            # Check whitelist
            if domain and domain not in self.allowed_external_domains:
                violations.append(f"external_call_blocked: domain_{domain}_not_whitelisted")

        return violations

    def _map_to_denial_reason(self, reason: str) -> DenialReason:
        """Map violation reason to standardized denial reason."""
        if 'ethics_violation' in reason:
            return DenialReason.ETHICS_VIOLATION
        elif 'resource_exceeded' in reason:
            return DenialReason.RESOURCE_EXCEEDED
        elif 'loop_detected' in reason:
            return DenialReason.LOOP_DETECTED
        elif 'external_call_blocked' in reason:
            return DenialReason.EXTERNAL_CALL_BLOCKED
        elif 'invalid_plan' in reason:
            return DenialReason.INVALID_PLAN
        else:
            return DenialReason.UNKNOWN_ERROR

    def _record_verification(self, outcome: VerificationOutcome) -> None:
        """Record verification in audit ledger."""
        ledger_entry = {
            'timestamp': outcome.context.timestamp,
            'result': outcome.result.value,
            'plan_hash': outcome.plan_hash,
            'verification_time_ms': outcome.verification_time_ms,
            'reasons': outcome.reasons,
            'user_id': outcome.context.user_id,
            'session_id': outcome.context.session_id,
            'request_id': outcome.context.request_id,
            'source': 'plan_verifier'
        }

        self.verification_ledger.append(ledger_entry)

        # Limit ledger size (keep last 1000 entries)
        if len(self.verification_ledger) > 1000:
            self.verification_ledger = self.verification_ledger[-1000:]


# Global instance for router integration
_plan_verifier_instance = None

def get_plan_verifier(config: Optional[Dict[str, Any]] = None) -> PlanVerifier:
    """Get or create global plan verifier instance."""
    global _plan_verifier_instance
    if _plan_verifier_instance is None:
        _plan_verifier_instance = PlanVerifier(config)
    return _plan_verifier_instance