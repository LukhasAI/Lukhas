"""Basic governance decision example integrated into core lane."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Iterable, List, Protocol

logger = logging.getLogger(__name__)


class CasePredicate(Protocol):
    """Callable protocol for governance rule predicates."""

    def __call__(self, case: "GovernanceCase") -> bool:  # pragma: no cover - protocol definition
        """Return ``True`` when a rule matches the provided case."""


@dataclass(slots=True)
class GovernanceCase:
    """Describe a governance decision request."""

    actor_id: str
    action: str
    risk_score: float
    channel: str = "api"
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class GovernanceRule:
    """Simple governance rule for demonstration purposes."""

    identifier: str
    description: str
    predicate: CasePredicate
    severity: str = "info"


@dataclass
class EvaluationResult:
    """Outcome of evaluating a :class:`GovernanceCase`."""

    approved: bool
    requires_review: bool
    matched_rules: list[GovernanceRule]
    notes: list[str] = field(default_factory=list)


class BasicGovernanceEngine:
    """Evaluate governance cases with deterministic sample rules."""

    def __init__(self, rules: Iterable[GovernanceRule]):
        self._rules: List[GovernanceRule] = list(rules)
        if not self._rules:
            raise ValueError("At least one governance rule must be provided")

    @property
    def rules(self) -> tuple[GovernanceRule, ...]:
        """Expose configured rules in an immutable collection."""

        return tuple(self._rules)

    def evaluate(self, case: GovernanceCase) -> EvaluationResult:
        """Evaluate a governance case using the configured rules."""

        matched: list[GovernanceRule] = []
        notes: list[str] = []

        for rule in self._rules:
            if rule.predicate(case):
                matched.append(rule)
                notes.append(rule.description)

        # ΛTAG: driftScore - treat risk_score as symbolic drift indicator for policy gates
        requires_review = case.risk_score >= 0.7 or any(r.severity == "critical" for r in matched)
        approved = case.risk_score < 0.5 and not any(r.severity == "critical" for r in matched)

        logger.debug(
            "Evaluated governance case",
            extra={
                "actor_id": case.actor_id,
                "action": case.action,
                "risk_score": case.risk_score,
                "matched_rules": [rule.identifier for rule in matched],
                "requires_review": requires_review,
                "approved": approved,
            },
        )

        return EvaluationResult(
            approved=approved,
            requires_review=requires_review,
            matched_rules=matched,
            notes=notes,
        )


def build_default_engine() -> BasicGovernanceEngine:
    """Create an engine with sample rules that mirror governance policies."""

    def high_risk(case: GovernanceCase) -> bool:
        return case.risk_score >= 0.7

    def privileged_channel(case: GovernanceCase) -> bool:
        return case.channel == "admin"

    def flagged_action(case: GovernanceCase) -> bool:
        return case.action in {"delete_user", "override_guardian"}

    rules = [
        GovernanceRule(
            identifier="RISK_THRESHOLD",
            description="Flag requests exceeding baseline risk threshold",
            predicate=high_risk,
            severity="warning",
        ),
        GovernanceRule(
            identifier="ADMIN_CHANNEL",
            description="Escalate admin channel requests for validation",
            predicate=privileged_channel,
            severity="warning",
        ),
        GovernanceRule(
            identifier="CRITICAL_ACTION",
            description="Block critical governance overrides without review",
            predicate=flagged_action,
            severity="critical",
        ),
    ]

    return BasicGovernanceEngine(rules)


def demo_decision_flow() -> EvaluationResult:
    """Run the default governance demo and return its evaluation result."""

    engine = build_default_engine()
    example_case = GovernanceCase(
        actor_id="operator-17",
        action="delete_user",
        risk_score=0.42,
        channel="admin",
        metadata={"context": "tutorial"},
    )
    return engine.evaluate(example_case)


__all__ = [
    "BasicGovernanceEngine",
    "EvaluationResult",
    "GovernanceCase",
    "GovernanceRule",
    "build_default_engine",
    "demo_decision_flow",
]
