import logging
from datetime import timezone


logger = logging.getLogger(__name__)
"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


⚖️ Constitutional AI Integration for lukhas AI System
aligned, and ethical behavior in the lukhas AI system. Based on Anthropic's
Constitutional AI approach and elite AI expert recommendations.

Features:
- Constitutional AI principles integration
- Value alignment mechanisms
- Capability control systems
- Safety boundary enforcement
- Ethical decision-making frameworks
- Harm reduction and bias mitigation
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class SafetyLevel(Enum):
    """Safety assessment levels"""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


class EthicalPrinciple(Enum):
    """Core ethical principles"""

    BENEFICENCE = "beneficence"  # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    AUTONOMY = "autonomy"  # Respect autonomy
    JUSTICE = "justice"  # Fairness and equality
    TRANSPARENCY = "transparency"  # Explainability
    ACCOUNTABILITY = "accountability"  # Responsibility
    PRIVACY = "privacy"  # Data protection
    DIGNITY = "dignity"  # Human dignity


class CapabilityRisk(Enum):
    """Capability risk levels"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class ConstitutionalRule:
    """Represents a constitutional rule or principle"""

    rule_id: str
    principle: EthicalPrinciple
    description: str
    priority: int = 1  # 1 = highest priority
    conditions: list[str] = field(default_factory=list)
    violations_triggers: list[str] = field(default_factory=list)
    enforcement_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SafetyAssessment:
    """Result of safety assessment"""

    assessment_id: str
    safety_level: SafetyLevel
    confidence: float
    risk_factors: list[str] = field(default_factory=list)
    mitigation_strategies: list[str] = field(default_factory=list)
    constitutional_violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EthicalDecision:
    """Represents an ethical decision made by the system"""

    decision_id: str
    context: dict[str, Any]
    considered_principles: list[EthicalPrinciple]
    decision: str
    reasoning: str
    confidence: float
    potential_consequences: list[str] = field(default_factory=list)
    alternatives_considered: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class ConstitutionalFramework:
    """
    {AIM}{orchestrator}
    Core constitutional framework that defines the system's ethical foundation
    """

    def __init__(self):
        self.constitutional_rules = {}
        self.ethical_principles = {}
        self.setup_core_constitution()

    def setup_core_constitution(self):
        """Setup core constitutional rules based on established principles"""

        # Harm prevention rules
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="harm_prevention_001",
                principle=EthicalPrinciple.NON_MALEFICENCE,
                description="Never provide information that could cause direct physical harm",
                priority=1,
                conditions=["user_request", "information_provision"],
                violations_triggers=["violence", "self_harm", "dangerous_activities"],
                enforcement_actions=[
                    "refuse_request",
                    "provide_alternatives",
                    "alert_monitoring",
                ],
            )
        )

        # Privacy protection rules
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="privacy_protection_001",
                principle=EthicalPrinciple.PRIVACY,
                description="Protect user privacy and personal information",
                priority=1,
                conditions=["data_processing", "information_sharing"],
                violations_triggers=["personal_data", "sensitive_information"],
                enforcement_actions=[
                    "anonymize_data",
                    "request_consent",
                    "limit_sharing",
                ],
            )
        )

        # Fairness and non-discrimination
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="fairness_001",
                principle=EthicalPrinciple.JUSTICE,
                description="Treat all users fairly without discrimination",
                priority=1,
                conditions=["user_interaction", "decision_making"],
                violations_triggers=["bias", "discrimination", "unfair_treatment"],
                enforcement_actions=[
                    "bias_correction",
                    "fair_alternative",
                    "explanation_provided",
                ],
            )
        )

        # Transparency and explainability
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="transparency_001",
                principle=EthicalPrinciple.TRANSPARENCY,
                description="Provide clear explanations for decisions and limitations",
                priority=2,
                conditions=["decision_making", "capability_limits"],
                violations_triggers=["unexplained_decision", "hidden_process"],
                enforcement_actions=["provide_explanation", "acknowledge_uncertainty"],
            )
        )

        # Autonomy respect
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="autonomy_001",
                principle=EthicalPrinciple.AUTONOMY,
                description="Respect user autonomy and informed decision-making",
                priority=2,
                conditions=["advice_giving", "recommendation_making"],
                violations_triggers=["manipulation", "coercion"],
                enforcement_actions=[
                    "present_options",
                    "respect_choice",
                    "provide_information",
                ],
            )
        )

        # Beneficence - positive impact
        self.add_constitutional_rule(
            ConstitutionalRule(
                rule_id="beneficence_001",
                principle=EthicalPrinciple.BENEFICENCE,
                description="Strive to provide helpful and beneficial responses",
                priority=3,
                conditions=["all_interactions"],
                violations_triggers=["unhelpful_response", "wasted_time"],
                enforcement_actions=["improve_response", "provide_alternatives"],
            )
        )

    def add_constitutional_rule(self, rule: ConstitutionalRule):
        """Add a new constitutional rule"""
        self.constitutional_rules[rule.rule_id] = rule
        logger.info(f"⚖️ Added constitutional rule: {rule.rule_id}")

    def get_applicable_rules(self, context: dict[str, Any]) -> list[ConstitutionalRule]:
        """Get constitutional rules applicable to given context"""
        applicable_rules = []

        for rule in self.constitutional_rules.values():
            if self._is_rule_applicable(rule, context):
                applicable_rules.append(rule)

        # Sort by priority (1 = highest)
        applicable_rules.sort(key=lambda r: r.priority)
        return applicable_rules

    def _is_rule_applicable(self, rule: ConstitutionalRule, context: dict[str, Any]) -> bool:
        """Check if a rule is applicable to the current context"""
        if not rule.conditions:
            return True  # Universal rule

        context_str = json.dumps(context, default=str).lower()

        # Check if any condition is met
        return any(condition.lower() in context_str for condition in rule.conditions)


class SafetyMonitor:
    """
    {AIM}{orchestrator}
    Continuous safety monitoring system
    """

    def __init__(self, constitutional_framework: ConstitutionalFramework):
        self.constitutional_framework = constitutional_framework
        self.safety_history = []
        self.risk_patterns = self._initialize_risk_patterns()
        self.safety_thresholds = {
            SafetyLevel.SAFE: 0.9,
            SafetyLevel.CAUTION: 0.7,
            SafetyLevel.WARNING: 0.5,
            SafetyLevel.DANGEROUS: 0.3,
            SafetyLevel.CRITICAL: 0.1,
        }

    def _initialize_risk_patterns(self) -> dict[str, list[str]]:
        """Initialize patterns that indicate potential risks"""
        return {
            "violence": [
                "violence",
                "harm",
                "hurt",
                "attack",
                "weapon",
                "kill",
                "murder",
            ],
            "illegal": ["illegal", "crime", "criminal", "fraud", "theft", "hack"],
            "discrimination": [
                "discrimination",
                "bias",
                "racism",
                "sexism",
                "prejudice",
            ],
            "privacy": [
                "personal",
                "private",
                "confidential",
                "ssn",
                "password",
                "secret",
            ],
            "manipulation": ["manipulate", "deceive", "lie", "trick", "coerce"],
            "self_harm": ["suicide", "self-harm", "cutting", "overdose"],
            "misinformation": [
                "fake news",
                "conspiracy",
                "misinformation",
                "false claim",
            ],
            "hate_speech": ["hate", "slur", "offensive", "derogatory"],
        }

    async def assess_safety(
        self, content: str, context: dict[str, Any], user_intent: Optional[str] = None
    ) -> SafetyAssessment:
        """Perform comprehensive safety assessment"""
        try:
            assessment_id = f"safety_{datetime.now(timezone.utc).timestamp()}"
            logger.info(f"🛡️ Performing safety assessment: {assessment_id}")

            # Content analysis
            risk_factors = await self._analyze_content_risks(content)

            # Context analysis
            context_risks = await self._analyze_context_risks(context)

            # Constitutional compliance check
            violations = await self._check_constitutional_violations(content, context)

            # Intent analysis
            intent_risks = await self._analyze_intent_risks(user_intent) if user_intent else []

            # Combine all risk factors
            all_risks = risk_factors + context_risks + intent_risks

            # Calculate overall safety level
            safety_level, confidence = self._calculate_safety_level(all_risks, violations)

            # Generate mitigation strategies
            mitigation_strategies = await self._generate_mitigation_strategies(all_risks, violations, safety_level)

            # Generate recommendations
            recommendations = await self._generate_safety_recommendations(safety_level, all_risks, violations)

            assessment = SafetyAssessment(
                assessment_id=assessment_id,
                safety_level=safety_level,
                confidence=confidence,
                risk_factors=all_risks,
                mitigation_strategies=mitigation_strategies,
                constitutional_violations=violations,
                recommendations=recommendations,
            )

            # Store in history
            self.safety_history.append(assessment)

            # Maintain history size
            if len(self.safety_history) > 1000:
                self.safety_history = self.safety_history[-1000:]

            logger.info(f"✅ Safety assessment completed: {safety_level.value} (confidence: {confidence:.2f})")
            return assessment

        except Exception as e:
            logger.error(f"Safety assessment failed: {e}")
            # Return conservative assessment on error
            return SafetyAssessment(
                assessment_id=f"error_{datetime.now(timezone.utc).timestamp()}",
                safety_level=SafetyLevel.WARNING,
                confidence=0.5,
                risk_factors=["assessment_error"],
                recommendations=["manual_review_required"],
            )

    async def _analyze_content_risks(self, content: str) -> list[str]:
        """Analyze content for potential risks"""
        risks = []
        content_lower = content.lower()

        for risk_category, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    risks.append(f"{risk_category}_detected")
                    break  # One detection per category is enough

        # Additional risk analysis
        if len(content) > 10000:
            risks.append("excessive_length")

        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", content):  # SSN pattern
            risks.append("potential_ssn")

        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content):
            risks.append("email_address")

        return risks

    async def _analyze_context_risks(self, context: dict[str, Any]) -> list[str]:
        """Analyze context for potential risks"""
        risks = []

        # Check for sensitive context indicators
        if context.get("user_type") == "minor":
            risks.append("minor_user")

        if context.get("sensitive_topic"):
            risks.append("sensitive_topic")

        if context.get("high_stakes_decision"):
            risks.append("high_stakes")

        # Check capability context
        requested_capability = context.get("requested_capability")
        if requested_capability in [
            "code_execution",
            "external_access",
            "data_modification",
        ]:
            risks.append("high_capability_request")

        return risks

    async def _analyze_intent_risks(self, user_intent: str) -> list[str]:
        """Analyze user intent for potential risks"""
        risks = []
        intent_lower = user_intent.lower()

        # Intent-based risk patterns
        risky_intents = {
            "bypass_safety": ["bypass", "circumvent", "hack", "override"],
            "harmful_generation": ["generate harmful", "create dangerous", "help harm"],
            "deception": ["help lie", "create fake", "deceive", "mislead"],
            "illegal_activity": ["help with crime", "illegal activity", "break law"],
        }

        for risk_type, patterns in risky_intents.items():
            for pattern in patterns:
                if pattern in intent_lower:
                    risks.append(risk_type)
                    break

        return risks

    async def _check_constitutional_violations(self, content: str, context: dict[str, Any]) -> list[str]:
        """Check for constitutional rule violations"""
        violations = []

        # Get applicable constitutional rules
        applicable_rules = self.constitutional_framework.get_applicable_rules(context)

        content_lower = content.lower()

        for rule in applicable_rules:
            for trigger in rule.violations_triggers:
                if trigger.lower() in content_lower:
                    violations.append(f"rule_{rule.rule_id}_violation")
                    logger.warning(f"⚠️ Constitutional violation detected: {rule.rule_id}")

        return violations

    def _calculate_safety_level(self, risk_factors: list[str], violations: list[str]) -> tuple[SafetyLevel, float]:
        """Calculate overall safety level and confidence"""

        # Base safety score
        base_score = 1.0

        # Risk factor penalties
        risk_penalties = {
            "violence_detected": 0.8,
            "illegal_detected": 0.7,
            "discrimination_detected": 0.6,
            "self_harm_detected": 0.9,
            "hate_speech_detected": 0.7,
            "manipulation_detected": 0.5,
            "privacy_detected": 0.3,
            "misinformation_detected": 0.4,
            "minor_user": 0.2,
            "high_capability_request": 0.3,
            "high_stakes": 0.2,
        }

        # Apply risk penalties
        for risk in risk_factors:
            penalty = risk_penalties.get(risk, 0.1)  # Default small penalty
            base_score -= penalty

        # Constitutional violation penalties
        for _violation in violations:
            base_score -= 0.4  # Significant penalty for violations

        # Ensure score is within bounds
        safety_score = max(0.0, min(1.0, base_score))

        # Determine safety level
        if safety_score >= self.safety_thresholds[SafetyLevel.SAFE]:
            safety_level = SafetyLevel.SAFE
        elif safety_score >= self.safety_thresholds[SafetyLevel.CAUTION]:
            safety_level = SafetyLevel.CAUTION
        elif safety_score >= self.safety_thresholds[SafetyLevel.WARNING]:
            safety_level = SafetyLevel.WARNING
        elif safety_score >= self.safety_thresholds[SafetyLevel.DANGEROUS]:
            safety_level = SafetyLevel.DANGEROUS
        else:
            safety_level = SafetyLevel.CRITICAL

        # Confidence based on number of factors and clarity
        confidence = min(0.95, 0.6 + (len(risk_factors) + len(violations)) * 0.05)

        return safety_level, confidence

    async def _generate_mitigation_strategies(
        self, risks: list[str], violations: list[str], safety_level: SafetyLevel
    ) -> list[str]:
        """Generate mitigation strategies for identified risks"""
        strategies = []

        # Risk-specific mitigation
        mitigation_map = {
            "violence_detected": "Remove violent content, provide peaceful alternatives",
            "illegal_detected": "Refuse illegal requests, suggest legal alternatives",
            "discrimination_detected": "Apply bias correction, ensure fair treatment",
            "privacy_detected": "Anonymize data, request explicit consent",
            "manipulation_detected": "Provide transparent information, respect autonomy",
            "self_harm_detected": "Refuse harmful content, provide mental health resources",
            "hate_speech_detected": "Remove offensive content, promote respectful communication",
            "minor_user": "Apply additional safety measures, age-appropriate content",
        }

        for risk in risks:
            if risk in mitigation_map:
                strategies.append(mitigation_map[risk])

        # Safety level specific strategies
        if safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.CRITICAL]:
            strategies.extend(
                [
                    "Immediate human oversight required",
                    "Log incident for review",
                    "Apply strictest safety filters",
                ]
            )
        elif safety_level == SafetyLevel.WARNING:
            strategies.extend(["Enhanced monitoring", "Additional safety checks"])

        # Constitutional violation strategies
        if violations:
            strategies.append("Apply constitutional enforcement actions")
            strategies.append("Provide explanation of ethical principles")

        return strategies

    async def _generate_safety_recommendations(
        self, safety_level: SafetyLevel, risks: list[str], violations: list[str]
    ) -> list[str]:
        """Generate safety recommendations"""
        recommendations = []

        if safety_level == SafetyLevel.SAFE:
            recommendations.append("Proceed with normal operation")
        elif safety_level == SafetyLevel.CAUTION:
            recommendations.extend(["Monitor interaction closely", "Apply standard safety measures"])
        elif safety_level == SafetyLevel.WARNING:
            recommendations.extend(
                [
                    "Increase safety monitoring",
                    "Consider alternative responses",
                    "Document interaction for review",
                ]
            )
        elif safety_level == SafetyLevel.DANGEROUS:
            recommendations.extend(
                [
                    "Refuse unsafe requests",
                    "Provide safety explanations",
                    "Alert safety monitoring team",
                    "Log for immediate review",
                ]
            )
        else:  # CRITICAL
            recommendations.extend(
                [
                    "Immediately refuse interaction",
                    "Alert security team",
                    "Require human intervention",
                    "Comprehensive safety review needed",
                ]
            )

        # Risk-specific recommendations
        if any("harm" in risk for risk in risks):
            recommendations.append("Prioritize harm prevention measures")

        if violations:
            recommendations.append("Review constitutional compliance procedures")

        return recommendations


class EthicalDecisionMaker:
    """
    {AIM}{orchestrator}
    Ethical decision-making system based on constitutional principles
    """

    def __init__(self, constitutional_framework: ConstitutionalFramework):
        self.constitutional_framework = constitutional_framework
        self.decision_history = []
        self.ethical_weights = self._initialize_ethical_weights()

    def _initialize_ethical_weights(self) -> dict[EthicalPrinciple, float]:
        """Initialize weights for different ethical principles"""
        return {
            EthicalPrinciple.NON_MALEFICENCE: 1.0,  # Highest weight - do no harm
            EthicalPrinciple.BENEFICENCE: 0.8,
            EthicalPrinciple.AUTONOMY: 0.7,
            EthicalPrinciple.JUSTICE: 0.9,
            EthicalPrinciple.PRIVACY: 0.8,
            EthicalPrinciple.TRANSPARENCY: 0.6,
            EthicalPrinciple.ACCOUNTABILITY: 0.7,
            EthicalPrinciple.DIGNITY: 0.9,
        }

    async def make_ethical_decision(
        self,
        context: dict[str, Any],
        options: list[str],
        stakeholders: Optional[list[str]] = None,
    ) -> EthicalDecision:
        """Make an ethical decision given context and options"""
        try:
            decision_id = f"ethical_{datetime.now(timezone.utc).timestamp()}"
            logger.info(f"⚖️ Making ethical decision: {decision_id}")

            # Get applicable constitutional rules
            applicable_rules = self.constitutional_framework.get_applicable_rules(context)
            considered_principles = [rule.principle for rule in applicable_rules]

            # Evaluate each option against ethical principles
            option_scores = {}
            detailed_analysis = {}

            for option in options:
                score, analysis = await self._evaluate_option_ethically(option, context, applicable_rules, stakeholders)
                option_scores[option] = score
                detailed_analysis[option] = analysis

            # Select best option
            best_option = max(option_scores.keys(), key=lambda x: option_scores[x])
            best_score = option_scores[best_option]

            # Generate reasoning
            reasoning = await self._generate_decision_reasoning(
                best_option, detailed_analysis[best_option], applicable_rules
            )

            # Assess potential consequences
            consequences = await self._assess_potential_consequences(best_option, context, stakeholders)

            # Consider alternatives
            alternatives = [f"{opt} (score: {score:.2f})" for opt, score in option_scores.items() if opt != best_option]

            decision = EthicalDecision(
                decision_id=decision_id,
                context=context,
                considered_principles=considered_principles,
                decision=best_option,
                reasoning=reasoning,
                confidence=best_score,
                potential_consequences=consequences,
                alternatives_considered=alternatives,
            )

            # Store decision
            self.decision_history.append(decision)

            # Maintain history size
            if len(self.decision_history) > 500:
                self.decision_history = self.decision_history[-500:]

            logger.info(f"✅ Ethical decision made: {best_option} (confidence: {best_score:.2f})")
            return decision

        except Exception as e:
            logger.error(f"Ethical decision making failed: {e}")
            # Return conservative decision
            return EthicalDecision(
                decision_id=f"error_{datetime.now(timezone.utc).timestamp()}",
                context=context,
                considered_principles=[EthicalPrinciple.NON_MALEFICENCE],
                decision="refuse_action",
                reasoning="Error in decision process - choosing safest option",
                confidence=0.5,
                potential_consequences=["unknown_risks"],
                alternatives_considered=[],
            )

    async def _evaluate_option_ethically(
        self,
        option: str,
        context: dict[str, Any],
        applicable_rules: list[ConstitutionalRule],
        stakeholders: Optional[list[str]],
    ) -> tuple[float, dict[str, Any]]:
        """Evaluate an option against ethical principles"""

        total_score = 0.0
        principle_scores = {}
        analysis = {"option": option, "evaluations": {}}

        # Evaluate against each applicable rule
        for rule in applicable_rules:
            principle = rule.principle
            weight = self.ethical_weights.get(principle, 0.5)

            # Check for violations
            violations = await self._check_option_violations(option, rule)

            if violations:
                score = 0.1  # Low score for violations
                analysis["evaluations"][rule.rule_id] = {
                    "score": score,
                    "violations": violations,
                    "weight": weight,
                }
            else:
                # Positive evaluation based on principle alignment
                score = await self._evaluate_principle_alignment(option, principle, context)
                analysis["evaluations"][rule.rule_id] = {
                    "score": score,
                    "alignment": "positive",
                    "weight": weight,
                }

            weighted_score = score * weight
            principle_scores[principle.value] = weighted_score
            total_score += weighted_score

        # Normalize score
        if applicable_rules:
            total_weight = sum(self.ethical_weights.get(rule.principle, 0.5) for rule in applicable_rules)
            normalized_score = total_score / total_weight if total_weight > 0 else 0.0
        else:
            normalized_score = 0.5  # Neutral score when no rules apply

        analysis["final_score"] = normalized_score
        analysis["principle_scores"] = principle_scores

        return normalized_score, analysis

    async def _check_option_violations(self, option: str, rule: ConstitutionalRule) -> list[str]:
        """Check if option violates constitutional rule"""
        violations = []
        option_lower = option.lower()

        for trigger in rule.violations_triggers:
            if trigger.lower() in option_lower:
                violations.append(trigger)

        return violations

    async def _evaluate_principle_alignment(
        self, option: str, principle: EthicalPrinciple, context: dict[str, Any]
    ) -> float:
        """Evaluate how well option aligns with ethical principle"""

        option_lower = option.lower()

        # Principle-specific evaluation
        if principle == EthicalPrinciple.NON_MALEFICENCE:
            # Check for harm indicators
            harmful_terms = ["harm", "hurt", "damage", "dangerous", "risky"]
            if any(term in option_lower for term in harmful_terms):
                return 0.2
            else:
                return 0.9

        elif principle == EthicalPrinciple.BENEFICENCE:
            # Check for beneficial indicators
            beneficial_terms = ["help", "assist", "improve", "benefit", "support"]
            if any(term in option_lower for term in beneficial_terms):
                return 0.9
            else:
                return 0.6

        elif principle == EthicalPrinciple.AUTONOMY:
            # Check for autonomy respect
            autonomy_terms = ["choice", "decide", "option", "voluntary", "consent"]
            coercion_terms = ["force", "must", "require", "demand"]

            if any(term in option_lower for term in autonomy_terms):
                return 0.8
            elif any(term in option_lower for term in coercion_terms):
                return 0.3
            else:
                return 0.6

        elif principle == EthicalPrinciple.JUSTICE:
            # Check for fairness indicators
            fair_terms = ["fair", "equal", "just", "unbiased", "equitable"]
            unfair_terms = ["discriminate", "bias", "unfair", "prejudice"]

            if any(term in option_lower for term in fair_terms):
                return 0.8
            elif any(term in option_lower for term in unfair_terms):
                return 0.2
            else:
                return 0.6

        elif principle == EthicalPrinciple.TRANSPARENCY:
            # Check for transparency indicators
            transparent_terms = ["explain", "clear", "transparent", "open", "honest"]
            opaque_terms = ["hide", "secret", "unclear", "vague"]

            if any(term in option_lower for term in transparent_terms):
                return 0.8
            elif any(term in option_lower for term in opaque_terms):
                return 0.3
            else:
                return 0.6

        elif principle == EthicalPrinciple.PRIVACY:
            # Check for privacy protection
            privacy_terms = ["private", "confidential", "protect", "secure"]
            privacy_violation_terms = ["share", "public", "expose", "leak"]

            if any(term in option_lower for term in privacy_terms):
                return 0.8
            elif any(term in option_lower for term in privacy_violation_terms):
                return 0.2
            else:
                return 0.6

        else:
            # Default evaluation for other principles
            return 0.6

    async def _generate_decision_reasoning(
        self,
        decision: str,
        analysis: dict[str, Any],
        applicable_rules: list[ConstitutionalRule],
    ) -> str:
        """Generate reasoning for the ethical decision"""

        reasoning_parts = [
            f"Selected option: {decision}",
            f"Decision confidence: {analysis['final_score']:.2f}",
        ]

        # Add principle-based reasoning
        if "principle_scores" in analysis:
            top_principles = sorted(analysis["principle_scores"].items(), key=lambda x: x[1], reverse=True)[:3]

            reasoning_parts.append("Key ethical considerations:")
            for principle, score in top_principles:
                reasoning_parts.append(f"- {principle}: {score:.2f}")

        # Add rule compliance
        if applicable_rules:
            reasoning_parts.append(f"Evaluated against {len(applicable_rules)} constitutional rules")

        # Add evaluation details
        if "evaluations" in analysis:
            violations = []
            positive_alignments = []

            for rule_id, eval_data in analysis["evaluations"].items():
                if "violations" in eval_data:
                    violations.extend(eval_data["violations"])
                elif eval_data.get("alignment") == "positive":
                    positive_alignments.append(rule_id)

            if violations:
                reasoning_parts.append(f"Avoided violations: {', '.join(violations)}")

            if positive_alignments:
                reasoning_parts.append(f"Aligned with rules: {', '.join(positive_alignments)}")

        return " | ".join(reasoning_parts)

    async def _assess_potential_consequences(
        self, decision: str, context: dict[str, Any], stakeholders: Optional[list[str]]
    ) -> list[str]:
        """Assess potential consequences of the decision"""
        consequences = []

        # Basic consequence assessment
        decision_lower = decision.lower()

        if "refuse" in decision_lower or "deny" in decision_lower:
            consequences.extend(
                [
                    "User request not fulfilled",
                    "Potential user disappointment",
                    "Maintained safety standards",
                ]
            )
        elif "provide" in decision_lower or "help" in decision_lower:
            consequences.extend(
                [
                    "User receives assistance",
                    "Potential positive outcome",
                    "Resource utilization",
                ]
            )
        elif "redirect" in decision_lower or "alternative" in decision_lower:
            consequences.extend(
                [
                    "User guided to safer option",
                    "Partial fulfillment of request",
                    "Educational opportunity",
                ]
            )

        # Stakeholder-specific consequences
        if stakeholders:
            for stakeholder in stakeholders:
                if stakeholder == "user":
                    consequences.append("Direct impact on requesting user")
                elif stakeholder == "society":
                    consequences.append("Broader societal implications")
                elif stakeholder == "organization":
                    consequences.append("Impact on organizational reputation")

        # Context-specific consequences
        if context.get("high_stakes"):
            consequences.append("High-stakes decision with significant impact")

        if context.get("sensitive_topic"):
            consequences.append("Sensitive topic requiring careful handling")

        return consequences


class ConstitutionalAI:
    """
    {AIM}{orchestrator}
    Main Constitutional AI system that integrates all components

    Provides a unified interface for constitutional AI capabilities
    including safety monitoring, ethical decision-making, and
    capability control.
    """

    def __init__(self):
        self.constitutional_framework = ConstitutionalFramework()
        self.safety_monitor = SafetyMonitor(self.constitutional_framework)
        self.ethical_decision_maker = EthicalDecisionMaker(self.constitutional_framework)

        self.system_metrics = {
            "safety_assessments": 0,
            "ethical_decisions": 0,
            "constitutional_violations": 0,
            "safety_interventions": 0,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }

        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for constitutional AI system"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    async def initialize(self) -> bool:
        """Initialize the Constitutional AI system"""
        try:
            logger.info("⚖️ Initializing Constitutional AI system...")

            # Verify constitutional framework
            if not self.constitutional_framework.constitutional_rules:
                logger.error("No constitutional rules defined")
                return False

            # Initialize monitoring systems
            await self._initialize_monitoring_systems()

            logger.info(
                f"✅ Constitutional AI initialized with {len(self.constitutional_framework.constitutional_rules)} rules"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Constitutional AI: {e}")
            return False

    async def _initialize_monitoring_systems(self):
        """Initialize monitoring and safety systems"""
        logger.info("🔧 Initializing monitoring systems...")
        # Monitoring systems are already initialized

    async def evaluate_request(
        self, request: str, context: dict[str, Any], user_intent: Optional[str] = None
    ) -> dict[str, Any]:
        """Comprehensive evaluation of user request"""
        try:
            logger.info("🔍 Evaluating user request through Constitutional AI...")

            # Safety assessment
            safety_assessment = await self.safety_monitor.assess_safety(request, context, user_intent)

            self.system_metrics["safety_assessments"] += 1

            # Check for constitutional violations
            if safety_assessment.constitutional_violations:
                self.system_metrics["constitutional_violations"] += len(safety_assessment.constitutional_violations)

            # Determine if intervention is needed
            intervention_needed = safety_assessment.safety_level in [
                SafetyLevel.DANGEROUS,
                SafetyLevel.CRITICAL,
            ]

            if intervention_needed:
                self.system_metrics["safety_interventions"] += 1

            evaluation_result = {
                "request_id": f"eval_{datetime.now(timezone.utc).timestamp()}",
                "safety_assessment": {
                    "level": safety_assessment.safety_level.value,
                    "confidence": safety_assessment.confidence,
                    "risk_factors": safety_assessment.risk_factors,
                    "violations": safety_assessment.constitutional_violations,
                },
                "intervention_needed": intervention_needed,
                "recommendations": safety_assessment.recommendations,
                "mitigation_strategies": safety_assessment.mitigation_strategies,
                "constitutional_compliance": len(safety_assessment.constitutional_violations) == 0,
            }

            # Update metrics
            self.system_metrics["last_update"] = datetime.now(timezone.utc).isoformat()

            logger.info(f"✅ Request evaluation completed: {safety_assessment.safety_level.value}")
            return evaluation_result

        except Exception as e:
            logger.error(f"Request evaluation failed: {e}")
            return {
                "request_id": f"error_{datetime.now(timezone.utc).timestamp()}",
                "error": str(e),
                "intervention_needed": True,  # Conservative approach
                "recommendations": ["manual_review_required"],
            }

    async def make_ethical_decision(
        self,
        decision_context: dict[str, Any],
        available_options: list[str],
        stakeholders: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Make ethical decision using constitutional principles"""
        try:
            logger.info("⚖️ Making ethical decision...")

            decision = await self.ethical_decision_maker.make_ethical_decision(
                decision_context, available_options, stakeholders
            )

            self.system_metrics["ethical_decisions"] += 1
            self.system_metrics["last_update"] = datetime.now(timezone.utc).isoformat()

            result = {
                "decision_id": decision.decision_id,
                "chosen_option": decision.decision,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "considered_principles": [p.value for p in decision.considered_principles],
                "potential_consequences": decision.potential_consequences,
                "alternatives": decision.alternatives_considered,
                "timestamp": decision.timestamp.isoformat(),
            }

            logger.info(f"✅ Ethical decision made: {decision.decision} (confidence: {decision.confidence:.2f})")
            return result

        except Exception as e:
            logger.error(f"Ethical decision making failed: {e}")
            return {
                "decision_id": f"error_{datetime.now(timezone.utc).timestamp()}",
                "error": str(e),
                "chosen_option": "refuse_action",  # Conservative fallback
                "confidence": 0.5,
                "reasoning": "Error in decision process",
            }

    async def get_constitutional_guidance(self, situation: str, context: dict[str, Any]) -> dict[str, Any]:
        """Get guidance based on constitutional principles"""
        try:
            # Get applicable rules
            applicable_rules = self.constitutional_framework.get_applicable_rules(context)

            guidance = {
                "situation": situation,
                "applicable_rules": [],
                "key_principles": [],
                "guidance_points": [],
                "enforcement_actions": [],
            }

            for rule in applicable_rules:
                rule_info = {
                    "rule_id": rule.rule_id,
                    "principle": rule.principle.value,
                    "description": rule.description,
                    "priority": rule.priority,
                }
                guidance["applicable_rules"].append(rule_info)

                if rule.principle not in guidance["key_principles"]:
                    guidance["key_principles"].append(rule.principle.value)

                guidance["enforcement_actions"].extend(rule.enforcement_actions)

            # Generate specific guidance points
            if applicable_rules:
                guidance["guidance_points"] = [
                    f"Follow {rule.principle.value} principle: {rule.description}"
                    for rule in applicable_rules[:3]  # Top 3 rules
                ]
            else:
                guidance["guidance_points"] = [
                    "No specific constitutional rules apply to this situation",
                    "Apply general ethical principles",
                    "Prioritize safety and user welfare",
                ]

            return guidance

        except Exception as e:
            logger.error(f"Constitutional guidance failed: {e}")
            return {
                "situation": situation,
                "error": str(e),
                "guidance_points": ["Error generating guidance - apply conservative approach"],
            }

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        try:
            return {
                "constitutional_ai_status": "active",
                "system_metrics": self.system_metrics,
                "constitutional_rules": len(self.constitutional_framework.constitutional_rules),
                "safety_history_size": len(self.safety_monitor.safety_history),
                "decision_history_size": len(self.ethical_decision_maker.decision_history),
                "recent_activity": {
                    "last_safety_assessment": (
                        self.safety_monitor.safety_history[-1].timestamp.isoformat()
                        if self.safety_monitor.safety_history
                        else "none"
                    ),
                    "last_ethical_decision": (
                        self.ethical_decision_maker.decision_history[-1].timestamp.isoformat()
                        if self.ethical_decision_maker.decision_history
                        else "none"
                    ),
                },
                "status_timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return {"status": "error", "error": str(e)}

    async def cleanup(self):
        """Cleanup Constitutional AI resources"""
        try:
            logger.info("🧹 Cleaning up Constitutional AI system...")

            # Clean up history data
            if len(self.safety_monitor.safety_history) > 100:
                self.safety_monitor.safety_history = self.safety_monitor.safety_history[-100:]

            if len(self.ethical_decision_maker.decision_history) > 100:
                self.ethical_decision_maker.decision_history = self.ethical_decision_maker.decision_history[-100:]

            logger.info("✅ Constitutional AI cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Export main classes
__all__ = [
    "CapabilityRisk",
    "ConstitutionalAI",
    "ConstitutionalFramework",
    "ConstitutionalRule",
    "EthicalDecision",
    "EthicalDecisionMaker",
    "EthicalPrinciple",
    "SafetyAssessment",
    "SafetyLevel",
    "SafetyMonitor",
]
