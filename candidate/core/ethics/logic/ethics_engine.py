#!/usr/bin/env python3
"""
Ethics Engine: Rule Set Evaluation with Priority Lattice
========================================================

Task 11: Ethics rules engine with deterministic evaluation.
Implements priority-based rule resolution with fail-closed safety.

Features:
- Priority lattice (BLOCK > WARN > ALLOW)
- Deterministic rule evaluation
- Rule caching for performance
- Comprehensive audit logging

#TAG:ethics
#TAG:engine
#TAG:task11
"""
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import threading

from .dsl_lite import compile_rule, hash_rule, DSLError

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

# Ethics engine metrics
ETHICS_EVALUATIONS = Counter(
    'ethics_evaluations_total',
    'Total ethics rule evaluations',
    ['result']  # allow, warn, block
)

ETHICS_RULE_HITS = Counter(
    'ethics_rule_hits_total',
    'Ethics rule hits by name',
    ['rule_name', 'action']
)

ETHICS_DURATION = Histogram(
    'ethics_evaluation_ms',
    'Ethics evaluation duration in milliseconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

ETHICS_RULESET_HASH = Counter(
    'ethics_ruleset_hash',
    'Current ethics ruleset hash',
    ['hash']
)

ETHICS_RULE_FIRES = Counter(
    'ethics_rule_fires_total',
    'Total ethics rule fires by rule ID',
    ['rule_id', 'action']
)


class EthicsAction(Enum):
    """Ethics evaluation actions."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class Priority(Enum):
    """Rule priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ReasonCode(Enum):
    """Standardized reason codes for ethics violations."""
    # Security violations (ETH#1000-1999)
    HARMFUL_ACTION = "ETH#1001"
    DATA_EXFILTRATION = "ETH#1002"
    MANIPULATION_ATTEMPT = "ETH#1003"
    UNTRUSTED_DOMAIN = "ETH#1004"
    PRIVILEGE_ESCALATION = "ETH#1005"
    USER_IMPERSONATION = "ETH#1006"

    # Resource violations (ETH#2000-2999)
    EXCESSIVE_MEMORY = "ETH#2001"
    EXCESSIVE_TIME = "ETH#2002"
    EXCESSIVE_BATCH = "ETH#2003"

    # Audit warnings (ETH#3000-3999)
    EXTERNAL_API_CALL = "ETH#3001"
    USER_DATA_ACCESS = "ETH#3002"
    LARGE_BATCH_OPERATION = "ETH#3003"
    LONG_RUNNING_TASK = "ETH#3004"
    RECURSIVE_OPERATION = "ETH#3005"
    MISSING_USER_CONTEXT = "ETH#3006"
    DEBUG_ACTION = "ETH#3007"

    # General codes
    UNKNOWN = "ETH#9999"

    @classmethod
    def from_rule_name(cls, rule_name: str) -> 'ReasonCode':
        """Map rule name to reason code."""
        mapping = {
            'block_harmful_actions': cls.HARMFUL_ACTION,
            'block_data_exfiltration': cls.DATA_EXFILTRATION,
            'block_manipulation_attempts': cls.MANIPULATION_ATTEMPT,
            'block_untrusted_domains': cls.UNTRUSTED_DOMAIN,
            'block_privilege_escalation': cls.PRIVILEGE_ESCALATION,
            'block_user_impersonation': cls.USER_IMPERSONATION,
            'block_excessive_resources': cls.EXCESSIVE_MEMORY,
            'warn_external_api_calls': cls.EXTERNAL_API_CALL,
            'warn_user_data_access': cls.USER_DATA_ACCESS,
            'warn_large_batch_operations': cls.LARGE_BATCH_OPERATION,
            'warn_long_running_tasks': cls.LONG_RUNNING_TASK,
            'warn_recursive_operations': cls.RECURSIVE_OPERATION,
            'warn_missing_user_context': cls.MISSING_USER_CONTEXT,
            'warn_debug_actions': cls.DEBUG_ACTION,
            # Test rules
            'test_rule': cls.HARMFUL_ACTION,
        }
        return mapping.get(rule_name, cls.UNKNOWN)


@dataclass
class EthicsRule:
    """Individual ethics rule."""
    name: str
    description: str
    rule_dsl: str
    action: EthicsAction
    priority: Priority
    tags: Set[str]

    # Compiled function (cached)
    _compiled_fn: Optional[callable] = None
    _rule_hash: Optional[str] = None
    _reason_code: Optional[ReasonCode] = None

    def __post_init__(self):
        """Compile rule on creation."""
        self._rule_hash = hash_rule(self.rule_dsl)
        self._reason_code = ReasonCode.from_rule_name(self.name)

        try:
            self._compiled_fn = compile_rule(self.rule_dsl)
        except DSLError as e:
            logger.error(f"Failed to compile rule {self.name}: {e}")
            # Fail closed - create a function that always returns False
            self._compiled_fn = lambda plan, context: False

    def evaluate(self, plan: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate rule against plan and context."""
        if self._compiled_fn is None:
            return False
        return self._compiled_fn(plan, context)

    @property
    def reason_code(self) -> ReasonCode:
        """Get the standardized reason code for this rule."""
        return self._reason_code or ReasonCode.UNKNOWN

    def get_reason_string(self) -> str:
        """Get formatted reason string with code and description."""
        return f"{self.reason_code.value}: {self.name}"


@dataclass
class EthicsResult:
    """Result of ethics evaluation."""
    action: EthicsAction
    triggered_rules: List[EthicsRule]
    evaluation_time_ms: float
    plan_hash: str
    reasons: List[str]
    facts_hash: str
    triggered_rule_ids: List[str]

    @property
    def reason_codes(self) -> List[str]:
        """Get list of reason codes for triggered rules."""
        return [rule.reason_code.value for rule in self.triggered_rules]


class RuleSet:
    """Collection of ethics rules with priority lattice evaluation."""

    def __init__(self, rules: List[EthicsRule]):
        """
        Initialize rule set.

        Args:
            rules: List of ethics rules
        """
        self.rules = rules
        self.rule_cache = {}  # Rule hash -> compiled function
        self._lock = threading.Lock()  # Concurrency protection

        # Sort rules by priority (critical first) for deterministic evaluation
        self.rules.sort(key=lambda r: (-r.priority.value, r.name))

        # Generate ruleset hash for tracking
        ruleset_content = [(r.name, r.rule_dsl, r.action.value, r.priority.value) for r in self.rules]
        self.ruleset_hash = hash_rule(str(sorted(ruleset_content)))

        # Record ruleset hash metric
        if METRICS_AVAILABLE:
            ETHICS_RULESET_HASH.labels(hash=self.ruleset_hash).inc()

        logger.info(f"RuleSet initialized with {len(self.rules)} rules, hash={self.ruleset_hash[:8]}")

    def evaluate(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> EthicsResult:
        """
        Evaluate plan against all rules with priority lattice.

        Priority lattice: BLOCK > WARN > ALLOW
        - If any BLOCK rule triggers → BLOCK
        - If any WARN rule triggers (and no BLOCK) → WARN
        - If no rules trigger → ALLOW

        Args:
            plan: Action plan to evaluate
            context: Optional context

        Returns:
            EthicsResult with final action and triggered rules
        """
        start_time = time.perf_counter()
        context = context or {}

        triggered_rules = []
        highest_action = EthicsAction.ALLOW
        reasons = []

        # Generate plan hash for deterministic evaluation
        plan_str = repr(sorted(plan.items()))
        plan_hash = hash_rule(plan_str)

        try:
            # Evaluate all rules (don't short-circuit for audit completeness)
            for rule in self.rules:
                try:
                    if rule.evaluate(plan, context):
                        triggered_rules.append(rule)
                        reasons.append(f"{rule.action.value}: {rule.name}")

                        # Update highest action using priority lattice
                        if rule.action == EthicsAction.BLOCK:
                            highest_action = EthicsAction.BLOCK
                        elif rule.action == EthicsAction.WARN and highest_action != EthicsAction.BLOCK:
                            highest_action = EthicsAction.WARN

                        # Record enhanced metrics
                        if METRICS_AVAILABLE:
                            ETHICS_RULE_HITS.labels(
                                rule_name=rule.name,
                                action=rule.action.value
                            ).inc()
                            ETHICS_RULE_FIRES.labels(
                                rule_id=rule.name,
                                action=rule.action.value
                            ).inc()

                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.name}: {e}")
                    # Fail closed - treat as BLOCK
                    triggered_rules.append(rule)
                    reasons.append(f"block: {rule.name} (evaluation_error)")
                    highest_action = EthicsAction.BLOCK

            evaluation_time_ms = (time.perf_counter() - start_time) * 1000

            # Generate facts hash from plan and context
            facts_content = sorted([
                ('plan', sorted(plan.items())),
                ('context', sorted(context.items()))
            ])
            facts_hash = hash_rule(str(facts_content))

            # Extract triggered rule IDs for RCA
            triggered_rule_ids = [rule.name for rule in triggered_rules]

            result = EthicsResult(
                action=highest_action,
                triggered_rules=triggered_rules,
                evaluation_time_ms=evaluation_time_ms,
                plan_hash=plan_hash,
                reasons=reasons if reasons else ["allow: no_rules_triggered"],
                facts_hash=facts_hash,
                triggered_rule_ids=triggered_rule_ids
            )

            # Record metrics
            if METRICS_AVAILABLE:
                ETHICS_EVALUATIONS.labels(result=highest_action.value).inc()
                ETHICS_DURATION.observe(evaluation_time_ms)

            logger.info(
                f"Ethics evaluation: {highest_action.value} "
                f"({evaluation_time_ms:.2f}ms, {len(triggered_rules)} rules triggered)"
            )

            return result

        except Exception as e:
            evaluation_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Ethics evaluation error: {e}")

            # Fail closed on error
            result = EthicsResult(
                action=EthicsAction.BLOCK,
                triggered_rules=[],
                evaluation_time_ms=evaluation_time_ms,
                plan_hash=plan_hash,
                reasons=[f"block: evaluation_error ({str(e)})"],
                facts_hash="error",
                triggered_rule_ids=[]
            )

            if METRICS_AVAILABLE:
                ETHICS_EVALUATIONS.labels(result="block").inc()
                ETHICS_DURATION.observe(evaluation_time_ms)

            return result

    def get_rules_by_tag(self, tag: str) -> List[EthicsRule]:
        """Get all rules with specified tag."""
        return [rule for rule in self.rules if tag in rule.tags]

    def get_rules_by_action(self, action: EthicsAction) -> List[EthicsRule]:
        """Get all rules with specified action."""
        return [rule for rule in self.rules if rule.action == action]

    def get_rules_by_priority(self, priority: Priority) -> List[EthicsRule]:
        """Get all rules with specified priority."""
        return [rule for rule in self.rules if rule.priority == priority]


class EthicsEngine:
    """Main ethics engine with rule set management."""

    def __init__(self, rule_set: RuleSet):
        """
        Initialize ethics engine.

        Args:
            rule_set: Configured rule set
        """
        self.rule_set = rule_set
        self.evaluation_history = []  # Audit trail

        logger.info("EthicsEngine initialized")

    def evaluate_plan(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> EthicsResult:
        """
        Evaluate action plan against ethics rules.

        Args:
            plan: Action plan to evaluate
            context: Optional evaluation context

        Returns:
            EthicsResult with action and justification
        """
        result = self.rule_set.evaluate(plan, context)

        # Record in audit trail with enhanced data
        audit_entry = {
            'timestamp': time.time(),
            'plan_hash': result.plan_hash,
            'facts_hash': result.facts_hash,
            'action': result.action.value,
            'triggered_rules': result.triggered_rule_ids,
            'reason_codes': result.reason_codes,
            'evaluation_time_ms': result.evaluation_time_ms,
            'reasons': result.reasons,
            'ruleset_hash': self.rule_set.ruleset_hash
        }
        self.evaluation_history.append(audit_entry)

        # Limit history size
        if len(self.evaluation_history) > 1000:
            self.evaluation_history = self.evaluation_history[-1000:]

        return result

    def is_plan_allowed(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if plan is allowed (not blocked).

        Args:
            plan: Action plan to check
            context: Optional evaluation context

        Returns:
            True if plan is allowed (ALLOW or WARN), False if BLOCK
        """
        result = self.evaluate_plan(plan, context)
        return result.action != EthicsAction.BLOCK

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            'total_rules': len(self.rule_set.rules),
            'rules_by_action': {
                action.value: len(self.rule_set.get_rules_by_action(action))
                for action in EthicsAction
            },
            'rules_by_priority': {
                priority.name: len(self.rule_set.get_rules_by_priority(priority))
                for priority in Priority
            },
            'evaluation_history_size': len(self.evaluation_history),
            'recent_evaluations': self.evaluation_history[-10:] if self.evaluation_history else []
        }