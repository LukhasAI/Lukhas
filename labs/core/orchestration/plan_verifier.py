#!/usr/bin/env python3
"""
Plan Verifier - Fail-Closed Constraints on Action Plans
=======================================================

Task 5: Deterministic verification of action plans before execution
to ensure safe, compliant, and resource-bounded orchestration.

Task 11: Enhanced with Ethics DSL-lite for sophisticated rule evaluation.

Features:
- Deterministic allow/deny decisions (same plan+ctx → same result)
- Ethics DSL rules engine with priority lattice (BLOCK > WARN > ALLOW)
- Resource caps, loop limits, external-call whitelist
- Comprehensive telemetry and audit ledger integration
- <5% p95 latency impact on orchestration hot path

#TAG:orchestration
#TAG:safety
#TAG:task5
#TAG:task11
#TAG:ethics
"""
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def _is_truthy(value: Optional[str]) -> bool:
    """Helper to evaluate truthy environment/config flags."""
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# Ethics DSL integration (Task 11), Guardian Drift Bands (Task 12), and Safety Tags (Task 13)
try:
    from ..ethics.guardian_drift_bands import (  # noqa: F401  # TODO: ..ethics.guardian_drift_bands....
        GuardianBand,
        GuardianDriftBands,
        create_guardian_drift_bands,
    )
    from ..ethics.logic.ethics_engine import EthicsAction
    from ..ethics.logic.rule_loader import get_ethics_engine
    from ..ethics.safety_tags import (  # noqa: F401  # TODO: ..ethics.safety_tags.SafetyTag...
        SafetyTagEnricher,
        create_safety_tag_enricher,
    )
    ETHICS_DSL_AVAILABLE = True
    GUARDIAN_BANDS_AVAILABLE = True
    SAFETY_TAGS_AVAILABLE = True
except ImportError:
    # Graceful fallback if ethics DSL not available
    logger.warning("Ethics DSL, Guardian Drift Bands, and Safety Tags not available, using legacy ethics constraints")
    ETHICS_DSL_AVAILABLE = False
    GUARDIAN_BANDS_AVAILABLE = False
    SAFETY_TAGS_AVAILABLE = False

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

# Guardian Drift Bands metrics (Task 12)
PLAN_VERIFIER_GUARDIAN_BANDS = Counter(
    'plan_verifier_guardian_bands_total',
    'Plan verifications by Guardian band',
    ['band', 'action']
)

PLAN_VERIFIER_DRIFT_SCORE = Histogram(
    'plan_verifier_drift_score',
    'Plan verification drift scores',
    buckets=[0.0, 0.05, 0.1, 0.15, 0.25, 0.35, 0.5, 0.75, 1.0]
)

# Safety Tags metrics (Task 13)
PLAN_VERIFIER_SAFETY_TAGS = Counter(
    'plan_verifier_safety_tags_total',
    'Plan verifications with safety tags',
    ['tag_name', 'has_tag']
)

PLAN_VERIFIER_TAG_ENRICHMENT_TIME = Histogram(
    'plan_verifier_tag_enrichment_ms',
    'Safety tag enrichment duration in milliseconds',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
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
    # Guardian Drift Bands integration (Task 12)
    guardian_band: Optional[str] = None
    drift_score: Optional[float] = None
    guardrails: Optional[List[str]] = None
    human_requirements: Optional[List[str]] = None
    # Safety Tags integration (Task 13)
    safety_tags: Optional[List[str]] = None
    tag_enrichment_time_ms: Optional[float] = None
    counterfactual_decisions: Optional[List[Dict[str, Any]]] = None

    @property
    def result(self) -> VerificationResult:
        return VerificationResult.ALLOW if self.allow else VerificationResult.DENY


@dataclass(frozen=True)
class GuardianEnforcementDecision:
    """Represents Guardian enforcement state for a verification cycle."""
    enforce: bool
    lane: str
    emergency_disabled: bool = False


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

        # Ethics DSL engine (Task 11)
        self.ethics_engine = None
        if self.ethics_enabled and ETHICS_DSL_AVAILABLE:
            try:
                ethics_rules_path = self.config.get('ethics_rules_path')
                self.ethics_engine = get_ethics_engine(ethics_rules_path)
                logger.info("Ethics DSL engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ethics DSL engine: {e}")
                # Fall back to legacy ethics constraints
                self.ethics_engine = None

        # Guardian Drift Bands system (Task 12)
        self.guardian_bands = None
        self.guardian_enabled = self.config.get(
            'guardian_enabled',
            os.getenv('PLAN_GUARDIAN_ENABLED', '1') == '1'
        )

        if self.guardian_enabled and GUARDIAN_BANDS_AVAILABLE:
            try:
                # Load Guardian thresholds from config
                guardian_config = {
                    'allow_threshold': float(self.config.get('guardian_allow_threshold', '0.05')),
                    'guardrails_threshold': float(self.config.get('guardian_guardrails_threshold', '0.15')),
                    'human_threshold': float(self.config.get('guardian_human_threshold', '0.35')),
                }
                self.guardian_bands = create_guardian_drift_bands(**guardian_config)

                # Link ethics engine for integrated evaluation
                if self.ethics_engine:
                    self.guardian_bands.ethics_engine = self.ethics_engine

                logger.info("Guardian Drift Bands initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Guardian Drift Bands: {e}")
                self.guardian_bands = None

        # Safety Tag Enricher system (Task 13)
        self.safety_tag_enricher = None
        self.safety_tags_enabled = self.config.get(
            'safety_tags_enabled',
            os.getenv('PLAN_SAFETY_TAGS_ENABLED', '1') == '1'
        )

        if self.safety_tags_enabled and SAFETY_TAGS_AVAILABLE:
            try:
                # Create safety tag enricher with caching
                enable_caching = self.config.get('safety_tags_caching', True)
                self.safety_tag_enricher = create_safety_tag_enricher(enable_caching=enable_caching)
                logger.info("Safety Tag Enricher initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Safety Tag Enricher: {e}")
                self.safety_tag_enricher = None

        # Audit ledger
        self.verification_ledger = []

        # ΛTAG: guardian_canary — Configure gradual Guardian enforcement rollout
        canary_percent_config = self.config.get(
            'guardian_canary_percent',
            os.getenv('LUKHAS_CANARY_PERCENT', '10')
        )
        try:
            self.guardian_canary_percent = max(0.0, min(100.0, float(canary_percent_config)))
        except (TypeError, ValueError):
            self.guardian_canary_percent = 0.0

        self.guardian_emergency_disable_path = Path(
            self.config.get(
                'guardian_emergency_disable_path',
                os.getenv('GUARDIAN_EMERGENCY_DISABLE_PATH', '/tmp/guardian_emergency_disable')
            )
        )

        config_flag = self.config.get('enforce_ethics_dsl')
        if isinstance(config_flag, bool):
            self.guardian_enforcement_enabled = config_flag
        elif config_flag is not None:
            self.guardian_enforcement_enabled = _is_truthy(str(config_flag))
        else:
            env_value = os.getenv('ENFORCE_ETHICS_DSL')
            if env_value is None:
                self.guardian_enforcement_enabled = self.guardian_canary_percent > 0.0
            else:
                self.guardian_enforcement_enabled = _is_truthy(env_value)

        lanes_config = self.config.get(
            'guardian_enforced_lanes',
            os.getenv('LUKHAS_GUARDIAN_ENFORCED_LANES', 'labs')
        )
        self.guardian_enforced_lanes: Set[str] = {
            lane.strip().lower()
            for lane in str(lanes_config).split(',')
            if lane and lane.strip()
        }

        self.guardian_default_lane = str(
            self.config.get('guardian_default_lane', os.getenv('LUKHAS_LANE', 'experimental'))
        ).lower()
        self.guardian_counterfactual_logging = bool(
            self.config.get('guardian_counterfactual_logging', True)
        )

        ethics_mode = "DSL" if self.ethics_engine else "legacy" if self.ethics_enabled else "disabled"
        guardian_mode = "enabled" if self.guardian_bands else "disabled"
        safety_tags_mode = "enabled" if self.safety_tag_enricher else "disabled"
        logger.info(f"PlanVerifier initialized: ethics={ethics_mode}, guardian={guardian_mode}, "
                   f"safety_tags={safety_tags_mode}, max_time={self.max_execution_time}s, "
                   f"max_memory={self.max_memory_mb}MB, max_loops={self.max_loop_iterations}, "
                   f"domains={len(self.allowed_external_domains)}")

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

            # 2. Safety Tag Enrichment (Task 13)
            tagged_plan = None
            tag_enrichment_time_ms = 0.0
            if self.safety_tag_enricher:
                try:
                    tagged_plan = self.safety_tag_enricher.enrich_plan(
                        plan=plan,
                        context=ctx.metadata or {}
                    )
                    tag_enrichment_time_ms = tagged_plan.enrichment_time_ms

                    # Add safety tags to context for DSL evaluation
                    if ctx.metadata is None:
                        ctx.metadata = {}
                    ctx.metadata['safety_tags'] = tagged_plan.tag_names

                    # Record metrics
                    if METRICS_AVAILABLE:
                        PLAN_VERIFIER_TAG_ENRICHMENT_TIME.observe(tag_enrichment_time_ms)
                        for tag in tagged_plan.tags:
                            PLAN_VERIFIER_SAFETY_TAGS.labels(
                                tag_name=tag.name,
                                has_tag="true"
                            ).inc()

                except Exception as e:
                    logger.error(f"Error in safety tag enrichment: {e}")
                    tagged_plan = None

            # 3. Ethics and Guardian Drift Bands evaluation (Task 11 + Task 12)
            guardian_result = None
            counterfactual_decisions: List[Dict[str, Any]] = []
            guardian_enforced = False
            guardian_lane = self._determine_lane(ctx)
            if ctx.metadata is None:
                ctx.metadata = {}
            ctx.metadata.setdefault('guardian_lane', guardian_lane)
            emergency_disabled = self._is_guardian_emergency_disabled()
            ctx.metadata['guardian_emergency_disabled'] = emergency_disabled
            if self.guardian_bands:
                # Integrated Guardian Drift Bands evaluation
                guardian_result = self.guardian_bands.evaluate(
                    plan=plan,
                    context=ctx.metadata or {}
                )

                # Guardian band enforcement
                decision = self._should_enforce_guardian(plan_hash, ctx, emergency_disabled)
                guardian_enforced = decision.enforce
                guardian_lane = decision.lane
                ctx.metadata['guardian_lane'] = guardian_lane
                ctx.metadata['guardian_emergency_disabled'] = decision.emergency_disabled

                if guardian_result.band == GuardianBand.BLOCK:
                    if guardian_enforced:
                        violations.append(f"guardian_block: {guardian_result.band.value}")
                    else:
                        counterfactual_decisions.append(
                            self._record_guardian_counterfactual(guardian_result, guardian_lane, plan_hash)
                        )
                elif guardian_result.band == GuardianBand.REQUIRE_HUMAN:
                    if guardian_enforced:
                        # REQUIRE_HUMAN is treated as a constraint violation that requires human override
                        violations.append(f"guardian_human_required: {guardian_result.band.value}")
                    else:
                        counterfactual_decisions.append(
                            self._record_guardian_counterfactual(guardian_result, guardian_lane, plan_hash)
                        )

                ctx.metadata['guardian_enforced'] = guardian_enforced

            elif self.ethics_enabled:
                # Fallback to legacy ethics constraints if Guardian not available
                ethics_violations = self._check_ethics_constraints(plan, ctx)
                guardian_enforced = self.guardian_enforcement_enabled and not emergency_disabled
                ctx.metadata['guardian_enforced'] = guardian_enforced
                if ethics_violations:
                    if guardian_enforced:
                        violations.extend(ethics_violations)
                    else:
                        counterfactual = {
                            "lane": guardian_lane,
                            "would_action": "block",
                            "actual_action": "allow",
                            "plan_hash": plan_hash[:16],
                            "reasons": ethics_violations,
                        }
                        counterfactual_decisions.append(counterfactual)
                        if self.guardian_counterfactual_logging:
                            logger.warning(
                                "Guardian legacy counterfactual triggered",
                                extra={
                                    "lane": guardian_lane,
                                    "plan_hash": plan_hash[:16],
                                },
                            )

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

            # Create outcome with Guardian band and Safety Tags information
            outcome = VerificationOutcome(
                allow=allow,
                reasons=reasons,
                context=ctx,
                plan_hash=plan_hash,
                verification_time_ms=verification_time_ms,
                guardian_band=guardian_result.band.value if guardian_result else None,
                drift_score=guardian_result.drift_score if guardian_result else None,
                guardrails=guardian_result.guardrails if guardian_result else None,
                human_requirements=guardian_result.human_requirements if guardian_result else None,
                safety_tags=list(tagged_plan.tag_names) if tagged_plan else None,
                tag_enrichment_time_ms=tag_enrichment_time_ms if tag_enrichment_time_ms > 0 else None,
                counterfactual_decisions=counterfactual_decisions or None
            )

            # Record metrics
            if METRICS_AVAILABLE:
                PLAN_VERIFIER_ATTEMPTS.labels(result=outcome.result.value).inc()
                PLAN_VERIFIER_DURATION.observe(verification_time_ms)

                # Guardian Drift Bands metrics
                if guardian_result:
                    PLAN_VERIFIER_GUARDIAN_BANDS.labels(
                        band=guardian_result.band.value,
                        action=guardian_result.action
                    ).inc()
                    PLAN_VERIFIER_DRIFT_SCORE.observe(guardian_result.drift_score)

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
                reasons=[f"verification_error: {e!s}"],
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

    def _determine_lane(self, ctx: VerificationContext) -> str:
        """Determine the active orchestration lane."""
        if ctx.metadata:
            lane = ctx.metadata.get('lane') or ctx.metadata.get('LUKHAS_LANE')
            if lane:
                return str(lane).lower()
        return self.guardian_default_lane

    def _should_enforce_guardian(
        self,
        plan_hash: str,
        ctx: VerificationContext,
        emergency_override: Optional[bool] = None,
    ) -> GuardianEnforcementDecision:
        """Decide whether Guardian enforcement should block for this request."""
        lane = self._determine_lane(ctx)

        emergency_disabled = (
            emergency_override
            if emergency_override is not None
            else self._is_guardian_emergency_disabled()
        )
        if emergency_disabled:
            logger.warning("Guardian enforcement disabled via emergency kill-switch")
            return GuardianEnforcementDecision(False, lane, True)

        if not self.guardian_enforcement_enabled:
            return GuardianEnforcementDecision(False, lane, False)

        if lane not in self.guardian_enforced_lanes:
            return GuardianEnforcementDecision(False, lane, False)

        if self.guardian_canary_percent >= 100.0:
            return GuardianEnforcementDecision(True, lane, False)

        if self.guardian_canary_percent <= 0.0:
            return GuardianEnforcementDecision(False, lane, False)

        sample_source = plan_hash or ctx.request_id or ctx.session_id or ctx.user_id or lane
        sample_int = int(hashlib.sha256(sample_source.encode("utf-8")).hexdigest(), 16)
        sample_percent = (sample_int % 10000) / 100.0
        return GuardianEnforcementDecision(sample_percent < self.guardian_canary_percent, lane, False)

    def _is_guardian_emergency_disabled(self) -> bool:
        """Return True when the emergency kill-switch file is present."""
        try:
            return self.guardian_emergency_disable_path.exists()
        except OSError as exc:
            logger.error("Failed to read guardian emergency disable flag: %s", exc)
            return False

    def _record_guardian_counterfactual(
        self,
        guardian_result,
        lane: str,
        plan_hash: str,
    ) -> Dict[str, Any]:
        """Record counterfactual Guardian decisions for audit logging."""
        counterfactual = {
            "lane": lane,
            "would_action": guardian_result.band.value,
            "actual_action": "allow",
            "plan_hash": plan_hash[:16],
            "ethics_action": guardian_result.ethics_action,
            "drift_score": guardian_result.drift_score,
        }

        if guardian_result.guardrails:
            counterfactual["guardrails"] = guardian_result.guardrails
        if guardian_result.human_requirements:
            counterfactual["human_requirements"] = guardian_result.human_requirements

        if self.guardian_counterfactual_logging:
            # ΛTAG: guardian_counterfactual — emit shadow-mode telemetry
            logger.warning(
                "Guardian counterfactual triggered",
                extra={
                    "lane": lane,
                    "would_action": guardian_result.band.value,
                    "plan_hash": plan_hash[:16],
                    "drift_score": guardian_result.drift_score,
                }
            )

        return counterfactual

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
        """Check ethics constraints using DSL engine or legacy rules."""
        violations = []

        if self.ethics_engine:
            # Use Ethics DSL engine (Task 11)
            try:
                # Convert VerificationContext to dict for ethics engine
                context_dict = {
                    'user_id': ctx.user_id,
                    'session_id': ctx.session_id,
                    'request_id': ctx.request_id,
                    'timestamp': ctx.timestamp,
                    'metadata': ctx.metadata or {}
                }

                ethics_result = self.ethics_engine.evaluate_plan(plan, context_dict)

                if ethics_result.action == EthicsAction.BLOCK:
                    # Convert ethics reasons to violations
                    for reason in ethics_result.reasons:
                        violations.append(f"ethics_dsl: {reason}")

                elif ethics_result.action == EthicsAction.WARN:
                    # Log warnings but don't block (allow through)
                    logger.warning(f"Ethics DSL warnings for plan {plan.get('action', 'unknown')}: {ethics_result.reasons}")

                # Log ethics evaluation for audit
                logger.debug(f"Ethics DSL evaluation: {ethics_result.action.value} "
                           f"({ethics_result.evaluation_time_ms:.2f}ms, "
                           f"{len(ethics_result.triggered_rules)} rules)")

            except Exception as e:
                logger.error(f"Ethics DSL evaluation error: {e}")
                # Fail closed - treat as violation
                violations.append(f"ethics_dsl: evaluation_error ({e!s})")

        else:
            # Legacy ethics constraints (fallback)
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
                except Exception:
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

        if outcome.counterfactual_decisions:
            ledger_entry['counterfactual'] = outcome.counterfactual_decisions

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
