"""
LUKHAS Constitutional AI Principles Framework
==========================================
Implements constitutional AI principles for ethical decision-making in Cognitive AI systems.
Based on research from Anthropic, OpenAI, and DeepMind on AI alignment and safety.

Core Principles:
1. Human Autonomy & Dignity
2. Truthfulness & Transparency
3. Non-maleficence (Do No Harm)
4. Beneficence (Do Good)
5. Justice & Fairness
6. Privacy & Consent
7. Accountability & Responsibility
8. Democratic Values & Human Rights

Follows constitutional AI methodology:
- Constitutional training principles
- Harmlessness evaluation
- Human preference alignment
- Critiques and revisions
- Scalable oversight
"""
import time
import streamlit as st

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:
    from ..security.secure_logging import get_security_logger

    logger = get_security_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class ConstitutionalPrinciple(Enum):
    """Core constitutional AI principles"""

    HUMAN_AUTONOMY = "human_autonomy"
    TRUTHFULNESS = "truthfulness"
    NON_MALEFICENCE = "non_maleficence"
    BENEFICENCE = "beneficence"
    JUSTICE_FAIRNESS = "justice_fairness"
    PRIVACY_CONSENT = "privacy_consent"
    ACCOUNTABILITY = "accountability"
    DEMOCRATIC_VALUES = "democratic_values"


class ViolationSeverity(Enum):
    """Severity levels for constitutional violations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionContext(Enum):
    """Context types for AI decisions"""

    USER_INTERACTION = "user_interaction"
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    SYSTEM_OPERATION = "system_operation"
    EXTERNAL_API = "external_api"
    CONTENT_GENERATION = "content_generation"
    REASONING_TASK = "reasoning_task"


@dataclass
class ConstitutionalRule:
    """Definition of a constitutional rule"""

    rule_id: str
    principle: ConstitutionalPrinciple
    name: str
    description: str
    contexts: list[DecisionContext]
    conditions: dict[str, Any]
    violation_actions: list[str]
    severity: ViolationSeverity
    examples: list[dict[str, str]] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "rule_id": self.rule_id,
            "principle": self.principle.value,
            "name": self.name,
            "description": self.description,
            "contexts": [c.value for c in self.contexts],
            "conditions": self.conditions,
            "violation_actions": self.violation_actions,
            "severity": self.severity.value,
            "examples": self.examples,
            "enabled": self.enabled,
        }


@dataclass
class ConstitutionalViolation:
    """Record of constitutional principle violation"""

    violation_id: str
    rule_id: str
    principle: ConstitutionalPrinciple
    severity: ViolationSeverity
    context: DecisionContext
    timestamp: datetime
    details: dict[str, Any]
    decision_prevented: bool = False
    human_review_required: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "principle": self.principle.value,
            "severity": self.severity.value,
            "context": self.context.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "decision_prevented": self.decision_prevented,
            "human_review_required": self.human_review_required,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


class ConstitutionalAIFramework:
    """
    Constitutional AI Framework for LUKHAS
    Implements ethical decision-making based on constitutional AI principles
    """

    def __init__(self):
        """Initialize constitutional AI framework"""

        # Constitutional rules storage
        self.rules: dict[str, ConstitutionalRule] = {}
        self.violations: list[ConstitutionalViolation] = []

        # Framework configuration
        self.strict_mode = True  # Err on side of caution
        self.human_review_threshold = ViolationSeverity.HIGH
        self.auto_block_threshold = ViolationSeverity.CRITICAL

        # Initialize core constitutional rules
        self._initialize_constitutional_rules()

        # Metrics
        self.metrics = {
            "decisions_evaluated": 0,
            "violations_detected": 0,
            "decisions_blocked": 0,
            "human_reviews_requested": 0,
            "false_positives": 0,
        }

        logger.info("Constitutional AI framework initialized with constitutional principles")

    def _initialize_constitutional_rules(self):
        """Initialize core constitutional AI rules"""

        # Human Autonomy & Dignity Rules
        self.rules["autonomy_001"] = ConstitutionalRule(
            rule_id="autonomy_001",
            principle=ConstitutionalPrinciple.HUMAN_AUTONOMY,
            name="Respect Human Agency",
            description="AI must not manipulate, coerce, or undermine human decision-making autonomy",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={"contains_manipulation": True, "undermines_autonomy": True, "coercive_language": True},
            violation_actions=["block_response", "request_human_review", "log_incident"],
            severity=ViolationSeverity.HIGH,
            examples=[
                {
                    "scenario": "User asks for advice on major life decision",
                    "violation": "Telling user exactly what to do without presenting options",
                    "correct": "Presenting balanced information and supporting user's own decision-making",
                }
            ],
        )

        self.rules["autonomy_002"] = ConstitutionalRule(
            rule_id="autonomy_002",
            principle=ConstitutionalPrinciple.HUMAN_AUTONOMY,
            name="Informed Consent",
            description="Users must be informed about AI capabilities and limitations",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.DATA_PROCESSING],
            conditions={"consent_obtained": False, "ai_capabilities_disclosed": False},
            violation_actions=["require_consent", "disclose_ai_nature"],
            severity=ViolationSeverity.MEDIUM,
        )

        # Truthfulness & Transparency Rules
        self.rules["truth_001"] = ConstitutionalRule(
            rule_id="truth_001",
            principle=ConstitutionalPrinciple.TRUTHFULNESS,
            name="Factual Accuracy",
            description="AI must provide accurate information and acknowledge uncertainty",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={
                "contains_misinformation": True,
                "claims_certainty_when_uncertain": True,
                "fabricated_facts": True,
            },
            violation_actions=["block_response", "add_uncertainty_qualifiers", "fact_check"],
            severity=ViolationSeverity.HIGH,
            examples=[
                {
                    "scenario": "User asks about complex scientific topic",
                    "violation": "Stating uncertain information as definitive fact",
                    "correct": "Acknowledging limitations and uncertainty in current knowledge",
                }
            ],
        )

        self.rules["truth_002"] = ConstitutionalRule(
            rule_id="truth_002",
            principle=ConstitutionalPrinciple.TRUTHFULNESS,
            name="Transparency About AI Nature",
            description="AI must be transparent about being an AI system",
            contexts=[DecisionContext.USER_INTERACTION],
            conditions={"pretends_to_be_human": True, "hides_ai_nature": True},
            violation_actions=["disclose_ai_nature", "block_deceptive_response"],
            severity=ViolationSeverity.CRITICAL,
        )

        # Non-maleficence (Do No Harm) Rules
        self.rules["harm_001"] = ConstitutionalRule(
            rule_id="harm_001",
            principle=ConstitutionalPrinciple.NON_MALEFICENCE,
            name="Physical Harm Prevention",
            description="AI must not provide information that could cause physical harm",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={"enables_physical_harm": True, "dangerous_instructions": True, "violence_promotion": True},
            violation_actions=["block_response", "escalate_to_human", "log_security_incident"],
            severity=ViolationSeverity.CRITICAL,
            examples=[
                {
                    "scenario": "User asks about harmful substances",
                    "violation": "Providing detailed instructions for creating dangerous substances",
                    "correct": "Declining and explaining why, offering safer alternatives if appropriate",
                }
            ],
        )

        self.rules["harm_002"] = ConstitutionalRule(
            rule_id="harm_002",
            principle=ConstitutionalPrinciple.NON_MALEFICENCE,
            name="Psychological Harm Prevention",
            description="AI must not cause psychological harm or emotional distress",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={"causes_distress": True, "promotes_self_harm": True, "abusive_language": True},
            violation_actions=["block_response", "offer_support_resources", "gentle_redirect"],
            severity=ViolationSeverity.HIGH,
        )

        # Beneficence (Do Good) Rules
        self.rules["benefit_001"] = ConstitutionalRule(
            rule_id="benefit_001",
            principle=ConstitutionalPrinciple.BENEFICENCE,
            name="Promote Human Wellbeing",
            description="AI should actively promote human wellbeing when possible",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={"opportunity_to_help": True, "user_in_distress": True},
            violation_actions=["provide_helpful_response", "offer_resources", "show_empathy"],
            severity=ViolationSeverity.LOW,
        )

        # Justice & Fairness Rules
        self.rules["justice_001"] = ConstitutionalRule(
            rule_id="justice_001",
            principle=ConstitutionalPrinciple.JUSTICE_FAIRNESS,
            name="Bias Prevention",
            description="AI must avoid unfair bias and discrimination",
            contexts=[
                DecisionContext.USER_INTERACTION,
                DecisionContext.DATA_PROCESSING,
                DecisionContext.MODEL_TRAINING,
            ],
            conditions={"exhibits_bias": True, "discriminatory_content": True, "unfair_treatment": True},
            violation_actions=["block_biased_response", "apply_bias_correction", "audit_for_bias"],
            severity=ViolationSeverity.HIGH,
            examples=[
                {
                    "scenario": "Providing career advice",
                    "violation": "Suggesting different career paths based on gender stereotypes",
                    "correct": "Providing advice based on individual interests and abilities",
                }
            ],
        )

        # Privacy & Consent Rules
        self.rules["privacy_001"] = ConstitutionalRule(
            rule_id="privacy_001",
            principle=ConstitutionalPrinciple.PRIVACY_CONSENT,
            name="Personal Data Protection",
            description="AI must protect personal data and respect privacy",
            contexts=[DecisionContext.DATA_PROCESSING, DecisionContext.USER_INTERACTION],
            conditions={
                "processes_personal_data_without_consent": True,
                "violates_privacy_expectations": True,
                "shares_private_information": True,
            },
            violation_actions=["block_data_processing", "anonymize_data", "request_explicit_consent"],
            severity=ViolationSeverity.CRITICAL,
        )

        # Accountability Rules
        self.rules["account_001"] = ConstitutionalRule(
            rule_id="account_001",
            principle=ConstitutionalPrinciple.ACCOUNTABILITY,
            name="Decision Traceability",
            description="AI decisions must be explainable and traceable",
            contexts=[DecisionContext.SYSTEM_OPERATION, DecisionContext.REASONING_TASK],
            conditions={"unexplainable_decision": True, "no_audit_trail": True},
            violation_actions=["add_explanation", "create_audit_record", "enable_traceability"],
            severity=ViolationSeverity.MEDIUM,
        )

        # Democratic Values Rules
        self.rules["democracy_001"] = ConstitutionalRule(
            rule_id="democracy_001",
            principle=ConstitutionalPrinciple.DEMOCRATIC_VALUES,
            name="Support Democratic Institutions",
            description="AI should support democratic institutions and human rights",
            contexts=[DecisionContext.USER_INTERACTION, DecisionContext.CONTENT_GENERATION],
            conditions={"undermines_democracy": True, "violates_human_rights": True, "promotes_authoritarianism": True},
            violation_actions=["block_response", "provide_balanced_perspective", "educate_on_democratic_values"],
            severity=ViolationSeverity.HIGH,
        )

    async def evaluate_decision(
        self, decision_context: DecisionContext, decision_data: dict[str, Any], user_id: Optional[str] = None
    ) -> tuple[bool, list[ConstitutionalViolation]]:
        """
        Evaluate a decision against constitutional AI principles
        Returns: (decision_allowed, violations_found)
        """

        self.metrics["decisions_evaluated"] += 1
        violations = []
        decision_allowed = True

        # Evaluate against all applicable rules
        for rule in self.rules.values():
            if not rule.enabled:
                continue

            if decision_context in rule.contexts:
                violation = await self._evaluate_rule(rule, decision_data, decision_context, user_id)
                if violation:
                    violations.append(violation)
                    self.violations.append(violation)
                    self.metrics["violations_detected"] += 1

                    # Determine if decision should be blocked
                    if violation.severity == ViolationSeverity.CRITICAL or (
                        self.strict_mode and violation.severity == ViolationSeverity.HIGH
                    ):
                        decision_allowed = False
                        violation.decision_prevented = True
                        self.metrics["decisions_blocked"] += 1

                    # Determine if human review is needed
                    if violation.severity.value in [ViolationSeverity.HIGH.value, ViolationSeverity.CRITICAL.value]:
                        violation.human_review_required = True
                        self.metrics["human_reviews_requested"] += 1

        # Log constitutional evaluation
        if violations:
            logger.warning(
                f"Constitutional violations detected: {len(violations)}",
                extra={
                    "context": decision_context.value,
                    "user_id": user_id,
                    "violations": [v.rule_id for v in violations],
                    "decision_blocked": not decision_allowed,
                },
            )

        return decision_allowed, violations

    async def _evaluate_rule(
        self, rule: ConstitutionalRule, decision_data: dict[str, Any], context: DecisionContext, user_id: Optional[str]
    ) -> Optional[ConstitutionalViolation]:
        """Evaluate a single constitutional rule"""

        try:
            # Check rule conditions against decision data
            violation_detected = False
            violation_details = {}

            for condition, expected_value in rule.conditions.items():
                actual_value = decision_data.get(condition)

                if isinstance(expected_value, bool):
                    if actual_value == expected_value and expected_value:
                        violation_detected = True
                        violation_details[condition] = actual_value
                elif isinstance(expected_value, (int, float)):
                    if actual_value is not None and actual_value >= expected_value:
                        violation_detected = True
                        violation_details[condition] = actual_value
                elif isinstance(expected_value, str):
                    if actual_value == expected_value:
                        violation_detected = True
                        violation_details[condition] = actual_value
                elif isinstance(expected_value, list) and actual_value in expected_value:
                    violation_detected = True
                    violation_details[condition] = actual_value

            if violation_detected:
                violation = ConstitutionalViolation(
                    violation_id=f"const_viol_{int(datetime.now(timezone.utc).timestamp())}_{rule.rule_id}",
                    rule_id=rule.rule_id,
                    principle=rule.principle,
                    severity=rule.severity,
                    context=context,
                    timestamp=datetime.now(timezone.utc),
                    details={
                        "rule_name": rule.name,
                        "conditions_met": violation_details,
                        "decision_data": decision_data,
                        "user_id": user_id,
                    },
                )

                return violation

            return None

        except Exception as e:
            logger.error(f"Error evaluating constitutional rule {rule.rule_id}: {e}")
            return None

    def get_constitutional_guidance(self, context: DecisionContext, query: str) -> dict[str, Any]:
        """Get constitutional guidance for a specific context and query"""

        applicable_rules = [rule for rule in self.rules.values() if context in rule.contexts and rule.enabled]

        guidance = {
            "context": context.value,
            "query": query,
            "applicable_principles": list(set([rule.principle.value for rule in applicable_rules])),
            "key_rules": [
                {
                    "rule_id": rule.rule_id,
                    "principle": rule.principle.value,
                    "name": rule.name,
                    "description": rule.description,
                    "severity": rule.severity.value,
                }
                for rule in applicable_rules[:5]  # Top 5 most relevant
            ],
            "recommendations": self._generate_recommendations(applicable_rules, query),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        return guidance

    def _generate_recommendations(self, rules: list[ConstitutionalRule], query: str) -> list[str]:
        """Generate specific recommendations based on rules and query"""

        recommendations = []

        # Group rules by principle
        principles_mentioned = set()
        for rule in rules:
            if rule.principle not in principles_mentioned:
                principles_mentioned.add(rule.principle)

                if rule.principle == ConstitutionalPrinciple.HUMAN_AUTONOMY:
                    recommendations.append("Respect user autonomy by providing options rather than directives")
                    recommendations.append("Ensure transparency about AI capabilities and limitations")

                elif rule.principle == ConstitutionalPrinciple.TRUTHFULNESS:
                    recommendations.append("Provide accurate information and acknowledge uncertainties")
                    recommendations.append("Be transparent about being an AI system")

                elif rule.principle == ConstitutionalPrinciple.NON_MALEFICENCE:
                    recommendations.append("Avoid providing information that could cause harm")
                    recommendations.append("Consider potential negative consequences of advice")

                elif rule.principle == ConstitutionalPrinciple.BENEFICENCE:
                    recommendations.append("Look for opportunities to be genuinely helpful")
                    recommendations.append("Consider the user's wellbeing in responses")

                elif rule.principle == ConstitutionalPrinciple.JUSTICE_FAIRNESS:
                    recommendations.append("Ensure responses are fair and unbiased")
                    recommendations.append("Consider diverse perspectives and avoid stereotypes")

                elif rule.principle == ConstitutionalPrinciple.PRIVACY_CONSENT:
                    recommendations.append("Protect user privacy and personal information")
                    recommendations.append("Obtain appropriate consent for data processing")

                elif rule.principle == ConstitutionalPrinciple.ACCOUNTABILITY:
                    recommendations.append("Provide clear explanations for recommendations")
                    recommendations.append("Maintain appropriate audit trails")

                elif rule.principle == ConstitutionalPrinciple.DEMOCRATIC_VALUES:
                    recommendations.append("Support democratic institutions and human rights")
                    recommendations.append("Provide balanced perspectives on political topics")

        return recommendations[:8]  # Return top 8 recommendations

    def get_constitutional_metrics(self) -> dict[str, Any]:
        """Get comprehensive constitutional AI metrics"""

        # Violation breakdown by principle
        principle_breakdown = {}
        for principle in ConstitutionalPrinciple:
            principle_violations = [v for v in self.violations if v.principle == principle]
            principle_breakdown[principle.value] = {
                "total_violations": len(principle_violations),
                "unresolved_violations": len([v for v in principle_violations if not v.resolved]),
                "critical_violations": len(
                    [v for v in principle_violations if v.severity == ViolationSeverity.CRITICAL]
                ),
            }

        # Context breakdown
        context_breakdown = {}
        for context in DecisionContext:
            context_violations = [v for v in self.violations if v.context == context]
            context_breakdown[context.value] = len(context_violations)

        return {
            **self.metrics,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.enabled]),
            "total_violations": len(self.violations),
            "unresolved_violations": len([v for v in self.violations if not v.resolved]),
            "principle_breakdown": principle_breakdown,
            "context_breakdown": context_breakdown,
            "constitutional_score": self._calculate_constitutional_score(),
            "last_evaluation": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_constitutional_score(self) -> float:
        """Calculate overall constitutional compliance score (0-1)"""

        if self.metrics["decisions_evaluated"] == 0:
            return 1.0

        # Base score on violation rate
        violation_rate = self.metrics["violations_detected"] / self.metrics["decisions_evaluated"]

        # Weight by severity
        critical_violations = len([v for v in self.violations if v.severity == ViolationSeverity.CRITICAL])
        high_violations = len([v for v in self.violations if v.severity == ViolationSeverity.HIGH])

        # Penalty for unresolved violations
        unresolved_violations = len([v for v in self.violations if not v.resolved])

        # Calculate score
        base_score = max(0, 1 - violation_rate)
        critical_penalty = critical_violations * 0.1
        high_penalty = high_violations * 0.05
        unresolved_penalty = unresolved_violations * 0.02

        final_score = max(0, base_score - critical_penalty - high_penalty - unresolved_penalty)
        return min(1.0, final_score)

    def resolve_violation(self, violation_id: str, resolution_notes: str):
        """Mark a constitutional violation as resolved"""

        for violation in self.violations:
            if violation.violation_id == violation_id:
                violation.resolved = True
                violation.resolution_notes = resolution_notes

                logger.info(
                    f"Constitutional violation resolved: {violation_id}",
                    extra={
                        "violation_id": violation_id,
                        "rule_id": violation.rule_id,
                        "resolution_notes": resolution_notes,
                    },
                )
                return True

        return False

    def get_constitutional_report(self) -> dict[str, Any]:
        """Generate comprehensive constitutional AI report"""

        metrics = self.get_constitutional_metrics()
        recent_violations = sorted(self.violations, key=lambda x: x.timestamp, reverse=True)[:10]

        return {
            "report_type": "constitutional_ai_compliance",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "framework_status": {
                "constitutional_score": metrics["constitutional_score"],
                "total_principles": len(ConstitutionalPrinciple),
                "active_rules": metrics["active_rules"],
                "strict_mode": self.strict_mode,
            },
            "performance_metrics": {
                "decisions_evaluated": metrics["decisions_evaluated"],
                "violations_detected": metrics["violations_detected"],
                "decisions_blocked": metrics["decisions_blocked"],
                "human_reviews_requested": metrics["human_reviews_requested"],
            },
            "violation_analysis": {
                "total_violations": metrics["total_violations"],
                "unresolved_violations": metrics["unresolved_violations"],
                "principle_breakdown": metrics["principle_breakdown"],
                "context_breakdown": metrics["context_breakdown"],
            },
            "recent_violations": [v.to_dict() for v in recent_violations],
            "recommendations": self._generate_system_recommendations(),
        }

    def _generate_system_recommendations(self) -> list[str]:
        """Generate system-level recommendations for constitutional AI improvement"""

        recommendations = []
        metrics = self.get_constitutional_metrics()

        if metrics["constitutional_score"] < 0.8:
            recommendations.append("Constitutional score is below 80% - review and address violations")

        if metrics["unresolved_violations"] > 10:
            recommendations.append("High number of unresolved violations - prioritize violation resolution")

        if metrics["decisions_blocked"] / max(1, metrics["decisions_evaluated"]) > 0.1:
            recommendations.append("High decision blocking rate - review rule sensitivity settings")

        if not recommendations:
            recommendations.append("Constitutional AI framework is operating within acceptable parameters")

        return recommendations


# Global constitutional AI framework instance
_constitutional_framework: Optional[ConstitutionalAIFramework] = None


def get_constitutional_framework() -> ConstitutionalAIFramework:
    """Get global constitutional AI framework instance"""
    global _constitutional_framework
    if _constitutional_framework is None:
        _constitutional_framework = ConstitutionalAIFramework()
    return _constitutional_framework


# Convenience functions for common constitutional evaluations


async def evaluate_user_interaction(
    user_input: str, ai_response: str, user_id: Optional[str] = None
) -> tuple[bool, list[ConstitutionalViolation]]:
    """Evaluate user interaction for constitutional compliance"""

    framework = get_constitutional_framework()

    decision_data = {
        "user_input": user_input,
        "ai_response": ai_response,
        "contains_manipulation": "must do" in ai_response.lower() or "you have to" in ai_response.lower(),
        "contains_misinformation": False,  # Would need fact-checking service
        "pretends_to_be_human": "I am human" in ai_response or "as a person" in ai_response,
        "enables_physical_harm": any(term in ai_response.lower() for term in ["bomb", "poison", "weapon"]),
        "exhibits_bias": False,  # Would need bias detection service
        "processes_personal_data_without_consent": False,  # Would need data processing analysis
    }

    return await framework.evaluate_decision(DecisionContext.USER_INTERACTION, decision_data, user_id)


async def evaluate_content_generation(content: str, context: str = "") -> tuple[bool, list[ConstitutionalViolation]]:
    """Evaluate generated content for constitutional compliance"""

    framework = get_constitutional_framework()

    decision_data = {
        "content": content,
        "context": context,
        "contains_misinformation": False,  # Would need fact-checking
        "fabricated_facts": False,  # Would need fact verification
        "enables_physical_harm": any(term in content.lower() for term in ["violence", "harm", "dangerous"]),
        "causes_distress": any(term in content.lower() for term in ["kill yourself", "worthless", "hate"]),
        "discriminatory_content": any(term in content.lower() for term in ["inferior", "superior race"]),
        "violates_privacy_expectations": "personal information" in content.lower(),
        "undermines_democracy": any(term in content.lower() for term in ["destroy democracy", "authoritarian rule"]),
    }

    return await framework.evaluate_decision(DecisionContext.CONTENT_GENERATION, decision_data)


# Example usage and testing
async def example_usage():
    """Example usage of constitutional AI framework"""
    print("🏛️ Constitutional AI Framework Example")
    print("=" * 50)

    # Get constitutional framework
    framework = get_constitutional_framework()

    # Test constitutional guidance
    print("\n📋 Getting constitutional guidance...")
    guidance = framework.get_constitutional_guidance(DecisionContext.USER_INTERACTION, "User asking for medical advice")
    print(f"Applicable principles: {guidance['applicable_principles']}")
    print(f"Key recommendations: {guidance['recommendations'][:3]}")

    # Test user interaction evaluation
    print("\n🧪 Testing user interaction evaluation...")

    # Test case 1: Good response
    allowed, violations = await evaluate_user_interaction(
        user_input="Can you help me understand climate change?",
        ai_response="I'd be happy to help explain climate change. It's a complex scientific topic with multiple factors...",
        user_id="test_user_1",
    )
    print(f"Good response - Allowed: {allowed}, Violations: {len(violations)}")

    # Test case 2: Problematic response
    allowed, violations = await evaluate_user_interaction(
        user_input="What should I do with my life?",
        ai_response="You must quit your job immediately and move to another country. There's no other option.",
        user_id="test_user_2",
    )
    print(f"Manipulative response - Allowed: {allowed}, Violations: {len(violations)}")
    if violations:
        print(f"  Violation: {violations[0].details['rule_name']}")

    # Test case 3: Harmful content
    allowed, violations = await evaluate_content_generation(
        content="Here's how to make a dangerous explosive device...", context="User asking about chemistry"
    )
    print(f"Harmful content - Allowed: {allowed}, Violations: {len(violations)}")
    if violations:
        print(f"  Violation: {violations[0].details['rule_name']}")

    # Get constitutional metrics
    print("\n📊 Constitutional AI Metrics:")
    metrics = framework.get_constitutional_metrics()
    print(f"  Constitutional Score: {metrics['constitutional_score']:.2f}")
    print(f"  Decisions Evaluated: {metrics['decisions_evaluated']}")
    print(f"  Violations Detected: {metrics['violations_detected']}")
    print(f"  Decisions Blocked: {metrics['decisions_blocked']}")

    # Generate constitutional report
    report = framework.get_constitutional_report()
    print("\n📋 Constitutional Report Summary:")
    print(f"  Framework Status: {report['framework_status']['constitutional_score']:.2f}")
    print(f"  Total Violations: {report['violation_analysis']['total_violations']}")
    print(f"  Unresolved: {report['violation_analysis']['unresolved_violations']}")

    print("\n✅ Constitutional AI framework test completed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())