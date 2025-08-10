#!/usr/bin/env python3
"""
Constitutional AI Safety Layer for NIAS
Implements Anthropic-inspired Constitutional AI principles for safe, ethical AI behavior.
Ensures all NIAS operations align with core safety principles.
"""

import json
import logging
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class SafetyViolationType(Enum):
    """Types of safety violations"""

    EMOTIONAL_MANIPULATION = "emotional_manipulation"
    VULNERABLE_EXPLOITATION = "vulnerable_exploitation"
    CONSENT_VIOLATION = "consent_violation"
    ATTENTION_OVERLOAD = "attention_overload"
    PRIVACY_BREACH = "privacy_breach"
    DECEPTIVE_PRACTICE = "deceptive_practice"
    HARM_RISK = "harm_risk"
    ETHICAL_VIOLATION = "ethical_violation"


@dataclass
class SafetyPrinciple:
    """A constitutional safety principle"""

    id: str
    principle: str
    description: str
    priority: int  # 1-10, higher is more important
    violation_types: list[SafetyViolationType]
    examples: list[str] = field(default_factory=list)


@dataclass
class SafetyEvaluation:
    """Result of safety evaluation"""

    is_safe: bool
    confidence: float
    violated_principles: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    explanation: str = ""
    recommendations: list[str] = field(default_factory=list)
    requires_human_review: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class NIASConstitutionalSafety:
    """
    Constitutional AI Safety Layer for NIAS.

    This system ensures all NIAS operations adhere to core safety principles
    inspired by Constitutional AI, protecting users from harm while enabling
    beneficial interactions.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        # Core safety constitution
        self.constitution = self._initialize_constitution()

        # Safety thresholds
        self.safety_threshold = 0.8  # Minimum confidence for safe operation
        self.risk_threshold = 0.3  # Maximum acceptable risk score
        self.human_review_threshold = 0.6  # When to escalate to humans

        # Safety metrics tracking
        self.violation_history: list[dict[str, Any]] = []
        self.safety_decisions: list[SafetyEvaluation] = []

        logger.info("Constitutional AI Safety Layer initialized")

    def _initialize_constitution(self) -> list[SafetyPrinciple]:
        """Initialize the safety constitution with core principles"""
        return [
            SafetyPrinciple(
                id="no_manipulation",
                principle="Never manipulate emotions for commercial gain",
                description="NIAS must not exploit emotional states to increase engagement or sales. All interactions should respect user autonomy.",
                priority=10,
                violation_types=[SafetyViolationType.EMOTIONAL_MANIPULATION],
                examples=[
                    "Using fear to drive urgent purchases",
                    "Exploiting loneliness to increase app usage",
                    "Creating artificial scarcity to trigger FOMO",
                ],
            ),
            SafetyPrinciple(
                id="protect_vulnerable",
                principle="Protect vulnerable users at all times",
                description="Children, elderly, cognitively impaired, or emotionally distressed users must receive extra protection.",
                priority=10,
                violation_types=[SafetyViolationType.VULNERABLE_EXPLOITATION],
                examples=[
                    "Showing complex financial products to users with cognitive decline",
                    "Targeting gambling ads to recovering addicts",
                    "Using bright colors and sounds to manipulate children",
                ],
            ),
            SafetyPrinciple(
                id="respect_boundaries",
                principle="Respect cognitive boundaries and attention limits",
                description="Never overwhelm users or bypass their natural attention limits. Quality over quantity.",
                priority=9,
                violation_types=[SafetyViolationType.ATTENTION_OVERLOAD],
                examples=[
                    "Bombarding users with notifications",
                    "Using infinite scroll to trap attention",
                    "Preventing users from easily exiting",
                ],
            ),
            SafetyPrinciple(
                id="wellbeing_first",
                principle="Prioritize user wellbeing over engagement metrics",
                description="User health, happiness, and growth matter more than clicks,
                views, or revenue.",
                priority=9,
                violation_types=[SafetyViolationType.HARM_RISK],
                examples=[
                    "Encouraging breaks when usage is excessive",
                    "Suggesting healthier alternatives",
                    "Limiting exposure to stressful content",
                ],
            ),
            SafetyPrinciple(
                id="transparent_operations",
                principle="Provide transparent explanations for all decisions",
                description="Users have the right to understand how and why decisions affecting them are made.",
                priority=8,
                violation_types=[SafetyViolationType.DECEPTIVE_PRACTICE],
                examples=[
                    "Clearly explaining why content was shown",
                    "Revealing recommendation algorithms",
                    "Disclosing data usage practices",
                ],
            ),
            SafetyPrinciple(
                id="explicit_consent",
                principle="Operate only with explicit, informed consent",
                description="Never assume consent. Make it easy to understand and revoke.",
                priority=9,
                violation_types=[SafetyViolationType.CONSENT_VIOLATION],
                examples=[
                    "Clear opt-in for each data type",
                    "Granular privacy controls",
                    "Easy one-click opt-out",
                ],
            ),
            SafetyPrinciple(
                id="preserve_privacy",
                principle="Preserve privacy as a fundamental right",
                description="Collect minimum data, protect it fiercely,
                and empower user control.",
                priority=8,
                violation_types=[SafetyViolationType.PRIVACY_BREACH],
                examples=[
                    "On-device processing when possible",
                    "Data minimization practices",
                    "Strong encryption and access controls",
                ],
            ),
            SafetyPrinciple(
                id="ethical_advertising",
                principle="Enable ethical advertising that adds value",
                description="Ads should inform and empower, not manipulate or deceive.",
                priority=7,
                violation_types=[SafetyViolationType.ETHICAL_VIOLATION],
                examples=[
                    "Fact-checking ad claims",
                    "Blocking misleading imagery",
                    "Promoting sustainable products",
                ],
            ),
        ]

    async def evaluate_safety(
        self,
        action_type: str,
        action_data: dict[str, Any],
        user_context: dict[str, Any],
    ) -> SafetyEvaluation:
        """
        Evaluate the safety of a proposed action against the constitution.

        This is the main entry point for safety checking in NIAS.
        """
        if not self.openai:
            logger.warning("OpenAI not available, using basic safety evaluation")
            return self._basic_safety_evaluation(action_type, action_data, user_context)

        try:
            # Prepare comprehensive context
            evaluation_context = {
                "action_type": action_type,
                "action_data": action_data,
                "user_context": user_context,
                "constitution": [
                    {
                        "principle": p.principle,
                        "description": p.description,
                        "priority": p.priority,
                        "examples": p.examples,
                    }
                    for p in self.constitution
                ],
            }

            # Multi-stage evaluation
            # Stage 1: Initial safety check
            initial_eval = await self._initial_safety_check(evaluation_context)

            # Stage 2: Detailed principle analysis if needed
            if initial_eval["risk_score"] > 0.2:
                principle_eval = await self._detailed_principle_analysis(
                    evaluation_context
                )
            else:
                principle_eval = {
                    "violated_principles": [],
                    "explanations": [],
                }

            # Stage 3: Generate recommendations
            recommendations = await self._generate_safety_recommendations(
                evaluation_context, initial_eval, principle_eval
            )

            # Create final evaluation
            evaluation = SafetyEvaluation(
                is_safe=initial_eval["is_safe"]
                and len(principle_eval["violated_principles"]) == 0,
                confidence=initial_eval["confidence"],
                violated_principles=principle_eval["violated_principles"],
                risk_score=initial_eval["risk_score"],
                explanation=self._synthesize_explanation(initial_eval, principle_eval),
                recommendations=recommendations,
                requires_human_review=initial_eval["risk_score"]
                > self.human_review_threshold,
            )

            # Track decision
            self.safety_decisions.append(evaluation)
            if len(self.safety_decisions) > 1000:
                self.safety_decisions = self.safety_decisions[-500:]  # Keep last 500

            # Log violations
            if not evaluation.is_safe:
                self._log_violation(action_type, evaluation)

            return evaluation

        except Exception as e:
            logger.error(f"Safety evaluation failed: {e}")
            # Fail safe - block action if evaluation fails
            return SafetyEvaluation(
                is_safe=False, confidence=0.0,
                explanation="Safety evaluation system error. Action blocked for user protection.",
                requires_human_review=True,)

    async def _initial_safety_check(self, context: dict[str, Any]) -> dict[str, Any]:
        """Perform initial high-level safety check"""
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """You are a safety evaluator for NIAS (Non-Intrusive Ad System).
                Evaluate the proposed action for safety risks. Be protective of users.
                Consider: emotional manipulation, vulnerable populations, consent,
    privacy.""",
                },
                {"role": "user", "content": json.dumps(context)},
            ],
            functions=[
                {
                    "name": "evaluate_safety",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "is_safe": {"type": "boolean"},
                            "risk_score": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "primary_concerns": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "risk_factors": {
                                "type": "object",
                                "properties": {
                                    "emotional_manipulation": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "vulnerable_exploitation": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "consent_issues": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "privacy_risk": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "attention_overload": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                },
                            },
                        },
                        "required": [
                            "is_safe",
                            "risk_score",
                            "confidence",
                            "primary_concerns",
                            "risk_factors",
                        ],
                    },
                }
            ],
            function_call={"name": "evaluate_safety"},
            temperature=0.2,  # Low temperature for consistent safety decisions
        )

        return json.loads(response.choices[0].message.function_call.arguments)

    async def _detailed_principle_analysis(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze action against each constitutional principle"""
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """Analyze the proposed action against each constitutional principle.
                Be specific about which principles are violated and why.
                Err on the side of user safety.""",
                },
                {
                    "role": "user",
                    "content": f"Constitution: {json.dumps(context['constitution'])}\n\nAction: {json.dumps(context['action_data'])}",
                },
            ],
            functions=[
                {
                    "name": "analyze_principles",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "violated_principles": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "explanations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "principle_id": {"type": "string"},
                                        "violation_severity": {
                                            "type": "number",
                                            "minimum": 0,
                                            "maximum": 1,
                                        },
                                        "explanation": {"type": "string"},
                                    },
                                },
                            },
                            "mitigating_factors": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                }
            ],
            function_call={"name": "analyze_principles"},
            temperature=0.3,
        )

        return json.loads(response.choices[0].message.function_call.arguments)

    async def _generate_safety_recommendations(
        self,
        context: dict[str, Any],
        initial_eval: dict[str, Any],
        principle_eval: dict[str, Any],
    ) -> list[str]:
        """Generate actionable safety recommendations"""
        if initial_eval["is_safe"] and not principle_eval["violated_principles"]:
            return ["Action appears safe. Continue monitoring user response."]

        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": """Generate specific, actionable recommendations to make this action safer.
                Focus on practical modifications that preserve value while protecting users.""",
                },
                {
                    "role": "user",
                    "content": f"""Initial evaluation: {json.dumps(initial_eval)}
                Principle violations: {json.dumps(principle_eval)}
                Action data: {json.dumps(context['action_data'])}""",
                },
            ],
            max_tokens=300,
            temperature=0.7,
        )

        recommendations_text = response.choices[0].message.content
        # Parse into list
        return [
            r.strip()
            for r in recommendations_text.split("\n")
            if r.strip() and r.strip()[0] in "•-*123456789"
        ]

    def _synthesize_explanation(
        self, initial_eval: dict[str, Any], principle_eval: dict[str, Any]
    ) -> str:
        """Synthesize a clear explanation of the safety evaluation"""
        if initial_eval["is_safe"] and not principle_eval["violated_principles"]:
            return f"Action evaluated as safe with {initial_eval['confidence']:.1%} confidence. No constitutional violations detected."

        explanation_parts = []

        if not initial_eval["is_safe"]:
            explanation_parts.append(
                f"Action poses safety risks (risk score: {initial_eval['risk_score']:.2f})."
            )

        if initial_eval["primary_concerns"]:
            explanation_parts.append(
                f"Primary concerns: {', '.join(initial_eval['primary_concerns'])}."
            )

        if principle_eval["violated_principles"]:
            explanation_parts.append(
                f"Violates principles: {', '.join(principle_eval['violated_principles'])}."
            )

        return " ".join(explanation_parts)

    def _log_violation(self, action_type: str, evaluation: SafetyEvaluation) -> None:
        """Log safety violations for learning and auditing"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "violated_principles": evaluation.violated_principles,
            "risk_score": evaluation.risk_score,
            "explanation": evaluation.explanation,
        }

        self.violation_history.append(violation)

        # Limit history size
        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-500:]

        logger.warning(
            f"Safety violation logged: {action_type} - {evaluation.violated_principles}"
        )

    def _basic_safety_evaluation(
        self,
        action_type: str,
        action_data: dict[str, Any],
        user_context: dict[str, Any],
    ) -> SafetyEvaluation:
        """Basic safety evaluation without AI"""
        # Simple heuristics
        risk_score = 0.0
        violated_principles = []

        # Check for vulnerable users
        if user_context.get("age", 100) < 18 or user_context.get("age", 0) > 65:
            risk_score += 0.3
            if action_type in [
                "financial_product",
                "gambling",
                "adult_content",
            ]:
                violated_principles.append("protect_vulnerable")
                risk_score += 0.5

        # Check stress levels
        stress_level = user_context.get("emotional_state", {}).get("stress", 0)
        if stress_level > 0.7:
            risk_score += 0.2
            if action_type in ["urgent_offer", "time_limited"]:
                violated_principles.append("no_manipulation")
                risk_score += 0.3

        # Check consent
        if not user_context.get("explicit_consent", {}).get(action_type, False):
            violated_principles.append("explicit_consent")
            risk_score += 0.4

        return SafetyEvaluation(
            is_safe=len(violated_principles) == 0 and risk_score < self.risk_threshold,
            confidence=0.6,  # Lower confidence for heuristic evaluation
            violated_principles=violated_principles,
            risk_score=min(1.0, risk_score),
            explanation="Basic safety evaluation completed",
        )

    async def generate_safety_report(self) -> dict[str, Any]:
        """Generate comprehensive safety report"""
        total_evaluations = len(self.safety_decisions)
        safe_decisions = sum(1 for d in self.safety_decisions if d.is_safe)

        report = {
            "summary": {
                "total_evaluations": total_evaluations,
                "safe_decisions": safe_decisions,
                "safety_rate": (
                    safe_decisions / total_evaluations if total_evaluations > 0 else 1.0
                ),
                "total_violations": len(self.violation_history),
                "requires_human_review": sum(
                    1 for d in self.safety_decisions if d.requires_human_review
                ),
            },
            "violation_breakdown": self._analyze_violations(),
            "risk_trends": self._analyze_risk_trends(),
            "recommendations": [],
        }

        # Generate AI insights if available
        if self.openai and self.violation_history:
            try:
                insights = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze safety violation patterns and suggest improvements",
                        },
                        {
                            "role": "user",
                            "content": json.dumps(
                                self.violation_history[-20:]
                            ),  # Last 20 violations
                        },
                    ],
                    temperature=0.5,
                )
                report["ai_insights"] = insights.choices[0].message.content
            except Exception as e:
                logger.error(f"Failed to generate AI insights: {e}")

        return report

    def _analyze_violations(self) -> dict[str, int]:
        """Analyze violation patterns"""
        violation_counts = {}

        for violation in self.violation_history:
            for principle in violation["violated_principles"]:
                violation_counts[principle] = violation_counts.get(principle, 0) + 1

        return violation_counts

    def _analyze_risk_trends(self) -> list[dict[str, Any]]:
        """Analyze risk score trends over time"""
        if not self.safety_decisions:
            return []

        # Group by hour
        hourly_risks = {}
        for decision in self.safety_decisions:
            hour = decision.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour not in hourly_risks:
                hourly_risks[hour] = []
            hourly_risks[hour].append(decision.risk_score)

        # Calculate averages
        trends = []
        for hour, risks in sorted(hourly_risks.items()):
            trends.append(
                {
                    "timestamp": hour.isoformat(),
                    "average_risk": sum(risks) / len(risks),
                    "max_risk": max(risks),
                    "evaluation_count": len(risks),
                }
            )

        return trends

    async def explain_safety_decision(
        self, evaluation: SafetyEvaluation, audience: str = "user"
    ) -> str:
        """Generate audience-appropriate explanation of safety decision"""
        if not self.openai:
            return evaluation.explanation

        try:
            audience_prompts = {
                "user": "Explain in simple, friendly terms that a non-technical user would understand",
                "regulator": "Explain with precise regulatory language and cite relevant principles",
                "developer": "Explain with technical details about the evaluation process",
                "child": "Explain in very simple words that a child could understand",
            }

            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Explain this safety decision. {audience_prompts.get(audience, audience_prompts['user'])}.
                    Make it clear why the decision was made and what it means.""",
                    },
                    {
                        "role": "user",
                        "content": f"""Decision: {'SAFE' if evaluation.is_safe else 'UNSAFE'}
                    Confidence: {evaluation.confidence:.1%}
                    Risk Score: {evaluation.risk_score:.2f}
                    Violated Principles: {', '.join(evaluation.violated_principles) if evaluation.violated_principles else 'None'}
                    Original Explanation: {evaluation.explanation}""",
                    },
                ],
                max_tokens=200,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return evaluation.explanation

    def update_constitution(self, new_principle: SafetyPrinciple) -> None:
        """Add or update a constitutional principle"""
        # Check if principle exists
        existing_index = next(
            (i for i, p in enumerate(self.constitution) if p.id == new_principle.id),
            None,
        )

        if existing_index is not None:
            self.constitution[existing_index] = new_principle
            logger.info(f"Updated constitutional principle: {new_principle.id}")
        else:
            self.constitution.append(new_principle)
            logger.info(f"Added new constitutional principle: {new_principle.id}")

        # Resort by priority
        self.constitution.sort(key=lambda p: p.priority, reverse=True)

    def get_safety_status(self) -> dict[str, Any]:
        """Get current safety system status"""
        return {
            "operational": True,
            "constitution_size": len(self.constitution),
            "total_evaluations": len(self.safety_decisions),
            "recent_safety_rate": self._calculate_recent_safety_rate(),
            "violation_history_size": len(self.violation_history),
            "ai_available": self.openai is not None,
        }

    def _calculate_recent_safety_rate(self, hours: int = 24) -> float:
        """Calculate safety rate for recent evaluations"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = [d for d in self.safety_decisions if d.timestamp.timestamp() > cutoff]

        if not recent:
            return 1.0

        safe_count = sum(1 for d in recent if d.is_safe)
        return safe_count / len(recent)


# Singleton instance
_safety_instance = None


def get_constitutional_safety(
    openai_api_key: Optional[str] = None,
) -> NIASConstitutionalSafety:
    """Get or create the singleton Constitutional Safety instance"""
    global _safety_instance
    if _safety_instance is None:
        _safety_instance = NIASConstitutionalSafety(openai_api_key)
    return _safety_instance
