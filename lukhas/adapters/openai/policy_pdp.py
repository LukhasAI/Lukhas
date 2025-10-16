import hashlib
import time
from typing import Any, Dict, List, Optional

import yaml

from .policy_models import Context, Decision, Rule

# Try to import Guardian metrics (graceful fallback)
try:
    from lukhas.observability.guardian_metrics import (
        record_decision,
        record_rule_evaluation,
        set_policy_version,
    )

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

    # No-op fallbacks
    def record_decision(*args, **kwargs):
        pass

    def record_rule_evaluation(*args, **kwargs):
        pass

    def set_policy_version(*args, **kwargs):
        pass


class Policy:
    """Represents a loaded policy, including indexed rules for efficient evaluation."""

    def __init__(self, policy_data: Dict[str, Any], etag: str):
        self.version = policy_data.get("version", 1)
        self.tenant_id = policy_data.get("tenant_id")
        self.combining_algorithm = policy_data.get("combining_algorithm", "deny_overrides")
        self.etag = etag

        raw_rules = policy_data.get("rules", [])
        # Normalize rules: map 'when' to 'conditions' and filter unknown keys
        normalized_rules = []
        for r in raw_rules:
            rule_dict = dict(r)
            # If YAML has 'when' but Rule expects 'conditions', rename the key
            if "when" in rule_dict and "conditions" not in rule_dict:
                rule_dict["conditions"] = rule_dict.pop("when")
            # Remove keys that Rule doesn't accept (like 'unless')
            # Only keep keys that are in Rule dataclass fields
            valid_keys = {
                "id",
                "effect",
                "subjects",
                "actions",
                "resources",
                "conditions",
                "obligations",
            }
            filtered_dict = {k: v for k, v in rule_dict.items() if k in valid_keys}
            normalized_rules.append(Rule(
                id=filtered_dict.get('id', 'unknown'),
                effect=filtered_dict.get('effect', 'deny'),
                subjects=filtered_dict.get('subjects', {}),
                actions=filtered_dict.get('actions', []),
                resources=filtered_dict.get('resources', []),
                conditions=filtered_dict.get('conditions', {}),
                obligations=filtered_dict.get('obligations', [])
            ))
        self.rules = normalized_rules

        # Pre-index rules for performance
        self._indexed_rules = self._index_rules(self.rules)

    def _index_rules(self, rules: List[Rule]) -> Dict[str, List[Rule]]:
        """Indexes rules by action for faster lookup."""
        index = {"*": []}  # Wildcard actions
        for rule in rules:
            if "*" in rule.actions:
                index["*"].append(rule)
            else:
                for action in rule.actions:
                    if action not in index:
                        index[action] = []
                    index[action].append(rule)
        return index

    def get_applicable_rules(self, action: str) -> List[Rule]:
        """Returns a list of rules that might apply to a given action."""
        return self._indexed_rules.get(action, []) + self._indexed_rules.get("*", [])


class PolicyLoader:
    """Loads a policy from a YAML file."""

    @staticmethod
    def load_from_file(filepath: str) -> Policy:
        """Loads, parses, and creates a Policy object from a YAML file."""
        with open(filepath, "r") as f:
            content = f.read()

        policy_data = yaml.safe_load(content)
        etag = hashlib.sha256(content.encode()).hexdigest()

        return Policy(policy_data, etag)


class GuardianPDP:
    """Policy Decision Point: Evaluates a request context against a policy."""

    def __init__(self, policy: Policy):
        self.policy = policy
        self.decision_count = 0
        self.allow_count = 0
        self.deny_count = 0

        # Set policy version metric
        if METRICS_AVAILABLE:
            set_policy_version(policy.etag, policy.tenant_id)

    def decide(self, ctx: Context) -> Decision:
        """
        Makes a decision based on the deny-overrides algorithm.
        - A single matching 'Deny' rule results in a final 'Deny'.
        - If any 'Allow' rules match and no 'Deny' rules match, the result is 'Allow'.
        - If no rules match, the result is 'Deny' (default_deny).
        """
        start_time = time.time()
        matched_allow_rule: Optional[Rule] = None

        # Use the pre-indexed rules for efficiency
        applicable_rules = self.policy.get_applicable_rules(ctx.action)

        for rule in applicable_rules:
            # Record rule evaluation metric
            if METRICS_AVAILABLE:
                record_rule_evaluation(rule.id, rule.effect)

            # Check if the rule matches the context
            if not (
                rule.matches_subject(ctx)
                and rule.matches_resource(ctx.resource)
                and rule.matches_action(ctx.action)
                and rule.matches_conditions(ctx)
            ):
                continue

            # If a Deny rule matches, short-circuit and deny immediately
            if rule.effect == "Deny":
                decision = Decision(
                    allow=False,
                    rule_id=rule.id,
                    reason=f"deny_rule_matched:{rule.id}",
                    audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
                )
                self._record_decision(decision, ctx, start_time)
                return decision

            # If an Allow rule matches, store it and continue checking for Deny rules
            if rule.effect == "Allow" and matched_allow_rule is None:
                matched_allow_rule = rule

        # If we found an Allow rule and were not overridden by a Deny, then allow.
        if matched_allow_rule:
            decision = Decision(
                allow=True,
                rule_id=matched_allow_rule.id,
                reason=f"allow_rule_matched:{matched_allow_rule.id}",
                obligations=matched_allow_rule.obligations,
                audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
            )
            self._record_decision(decision, ctx, start_time)
            return decision

        # If no rules matched, or only non-matching Allow rules were found, default to deny.
        decision = Decision(
            allow=False,
            rule_id=None,
            reason="default_deny",
            audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
        )
        self._record_decision(decision, ctx, start_time)
        return decision

    def _record_decision(self, decision: Decision, ctx: Context, start_time: float) -> None:
        """Record decision metrics and internal counters."""
        # Update internal counters
        self.decision_count += 1
        if decision.allow:
            self.allow_count += 1
        else:
            self.deny_count += 1

        # Record Prometheus metrics
        if METRICS_AVAILABLE:
            duration = time.time() - start_time
            # Extract scope from context (first scope if multiple)
            scope = list(ctx.scopes)[0] if ctx.scopes else None
            record_decision(
                allow=decision.allow,
                scope=scope,
                route=ctx.resource,
                reason=decision.reason if not decision.allow else None,
                duration_seconds=duration,
            )

    def get_stats(self) -> dict:
        """Get PDP statistics for health monitoring."""
        return {
            "total_decisions": self.decision_count,
            "allow_count": self.allow_count,
            "deny_count": self.deny_count,
            "policy_etag": self.policy.etag[:8] if self.policy.etag else "unknown",
        }


# Backward-compatible alias for legacy imports/tests
PDP = GuardianPDP
