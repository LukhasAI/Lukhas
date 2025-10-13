import yaml
import hashlib
from typing import List, Dict, Any, Optional
from .policy_models import Context, Decision, Rule

class Policy:
    """Represents a loaded policy, including indexed rules for efficient evaluation."""

    def __init__(self, policy_data: Dict[str, Any], etag: str):
        self.version = policy_data.get("version", 1)
        self.tenant_id = policy_data.get("tenant_id")
        self.combining_algorithm = policy_data.get("combining_algorithm", "deny_overrides")
        self.etag = etag

        raw_rules = policy_data.get("rules", [])
        self.rules = [Rule(**r) for r in raw_rules]

        # Pre-index rules for performance
        self._indexed_rules = self._index_rules(self.rules)

    def _index_rules(self, rules: List[Rule]) -> Dict[str, List[Rule]]:
        """Indexes rules by action for faster lookup."""
        index = {"*": []} # Wildcard actions
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


class PDP:
    """Policy Decision Point: Evaluates a request context against a policy."""

    def __init__(self, policy: Policy):
        self.policy = policy

    def decide(self, ctx: Context) -> Decision:
        """
        Makes a decision based on the deny-overrides algorithm.
        - A single matching 'Deny' rule results in a final 'Deny'.
        - If any 'Allow' rules match and no 'Deny' rules match, the result is 'Allow'.
        - If no rules match, the result is 'Deny' (default_deny).
        """
        matched_allow_rule: Optional[Rule] = None

        # Use the pre-indexed rules for efficiency
        applicable_rules = self.policy.get_applicable_rules(ctx.action)

        for rule in applicable_rules:
            # Check if the rule matches the context
            if not (
                rule.matches_subject(ctx) and
                rule.matches_resource(ctx.resource) and
                rule.matches_action(ctx.action) and
                rule.matches_conditions(ctx)
            ):
                continue

            # If a Deny rule matches, short-circuit and deny immediately
            if rule.effect == "Deny":
                return Decision(
                    allow=False,
                    rule_id=rule.id,
                    reason=f"deny_rule_matched:{rule.id}",
                    audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
                )

            # If an Allow rule matches, store it and continue checking for Deny rules
            if rule.effect == "Allow" and matched_allow_rule is None:
                matched_allow_rule = rule

        # If we found an Allow rule and were not overridden by a Deny, then allow.
        if matched_allow_rule:
            return Decision(
                allow=True,
                rule_id=matched_allow_rule.id,
                reason=f"allow_rule_matched:{matched_allow_rule.id}",
                obligations=matched_allow_rule.obligations,
                audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
            )

        # If no rules matched, or only non-matching Allow rules were found, default to deny.
        return Decision(
            allow=False,
            rule_id=None,
            reason="default_deny",
            audit={"combining": self.policy.combining_algorithm, "trace_id": ctx.trace_id},
        )
