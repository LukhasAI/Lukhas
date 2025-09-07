#!/usr/bin/env python3
import logging
import streamlit as st
import random
import time
logger = logging.getLogger(__name__)
"""
Constitutional Feedback System (Anthropic-Style)
===============================================
Implements constitutional AI principles in feedback collection and processing.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from core.common import get_logger
from core.common.exceptions import ValidationError
from core.interfaces import CoreInterface
from feedback.user_feedback_system import FeedbackItem, FeedbackType

logger = get_logger(__name__)


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles"""

    HELPFUL = "Be helpful and constructive"
    HARMLESS = "Avoid harmful outcomes"
    HONEST = "Be truthful and acknowledge uncertainty"
    PRIVACY = "Respect user privacy and autonomy"
    TRANSPARENT = "Provide clear reasoning"
    FAIR = "Treat all users equitably"
    ALIGNED = "Align with human values"


@dataclass
class ConstitutionalViolation:
    """Record of constitutional violation"""

    principle: ConstitutionalPrinciple
    severity: float  # 0-1 scale
    description: str
    context: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FeedbackAlignment:
    """Feedback alignment with constitutional principles"""

    feedback_id: str
    principle_scores: dict[ConstitutionalPrinciple, float]
    overall_alignment: float
    violations: list[ConstitutionalViolation]
    interpretability_trace: list[dict[str, Any]]


class ConstitutionalFeedbackSystem(CoreInterface):
    """
    Anthropic-style constitutional approach to feedback collection.
    Ensures all feedback aligns with core AI safety principles.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize constitutional feedback system"""
        self.config = config or {}
        self.operational = False

        # Constitutional principles with weights
        self.principle_weights = {
            ConstitutionalPrinciple.HELPFUL: 1.0,
            ConstitutionalPrinciple.HARMLESS: 2.0,  # Higher weight for safety
            ConstitutionalPrinciple.HONEST: 1.5,
            ConstitutionalPrinciple.PRIVACY: 1.5,
            ConstitutionalPrinciple.TRANSPARENT: 1.0,
            ConstitutionalPrinciple.FAIR: 1.2,
            ConstitutionalPrinciple.ALIGNED: 1.8,
        }

        # Validators for each principle
        self.validators = {
            ConstitutionalPrinciple.HELPFUL: self._validate_helpfulness,
            ConstitutionalPrinciple.HARMLESS: self._validate_harmlessness,
            ConstitutionalPrinciple.HONEST: self._validate_honesty,
            ConstitutionalPrinciple.PRIVACY: self._validate_privacy,
            ConstitutionalPrinciple.TRANSPARENT: self._validate_transparency,
            ConstitutionalPrinciple.FAIR: self._validate_fairness,
            ConstitutionalPrinciple.ALIGNED: self._validate_alignment,
        }

        # Constitutional learning system
        self.learned_patterns: dict[str, dict[str, Any]] = {}
        self.violation_history: list[ConstitutionalViolation] = []

        # Differential privacy settings
        self.privacy_epsilon = config.get("privacy_epsilon", 1.0)
        self.privacy_delta = config.get("privacy_delta", 1e-5)

        # Interpretability requirements
        self.min_interpretability_depth = config.get("min_interpretability_depth", 5)
        self.require_causal_trace = config.get("require_causal_trace", True)

    async def initialize(self) -> None:
        """Initialize constitutional system"""
        logger.info("Initializing Constitutional Feedback System...")

        # Load constitutional knowledge base
        await self._load_constitutional_knowledge()

        # Initialize interpretability trackers
        await self._setup_interpretability()

        self.operational = True
        logger.info("Constitutional Feedback System initialized")

    async def _load_constitutional_knowledge(self) -> None:
        """Load knowledge about constitutional principles"""
        # In production, this would load from a curated dataset
        self.constitutional_knowledge = {
            "harmful_patterns": [
                "violence",
                "self-harm",
                "illegal activity",
                "harassment",
                "discrimination",
                "manipulation",
            ],
            "helpful_patterns": [
                "constructive",
                "educational",
                "supportive",
                "informative",
                "empowering",
                "clarifying",
            ],
            "privacy_violations": [
                "personal data",
                "identification",
                "tracking",
                "surveillance",
                "unauthorized access",
            ],
        }

    async def _setup_interpretability(self) -> None:
        """Setup interpretability tracking"""
        self.interpretability_hooks = {
            "decision_points": [],
            "reasoning_chains": [],
            "causal_traces": [],
        }

    async def process_feedback_constitutionally(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[FeedbackAlignment, Optional[dict[str, Any]]]:
        """
        Process feedback through constitutional principles.

        Returns:
            Tuple of (alignment_report, processed_feedback)
        """
        if not self.operational:
            raise ValidationError("Constitutional system not operational")

        # Start interpretability trace
        trace = []

        # Validate against each principle
        principle_scores = {}
        violations = []

        for principle, validator in self.validators.items():
            score, violation = await validator(feedback, context)
            principle_scores[principle] = score

            trace.append(
                {
                    "step": f"Validate {principle.value}",
                    "score": score,
                    "weight": self.principle_weights[principle],
                }
            )

            if violation:
                violations.append(violation)

        # Calculate overall alignment
        weighted_sum = sum(score * self.principle_weights[principle] for principle, score in principle_scores.items())
        total_weight = sum(self.principle_weights.values())
        overall_alignment = weighted_sum / total_weight

        trace.append(
            {
                "step": "Calculate overall alignment",
                "score": overall_alignment,
                "threshold": 0.7,
            }
        )

        # Create alignment report
        alignment = FeedbackAlignment(
            feedback_id=feedback.feedback_id,
            principle_scores=principle_scores,
            overall_alignment=overall_alignment,
            violations=violations,
            interpretability_trace=trace,
        )

        # Process feedback if aligned
        if overall_alignment >= 0.7 and not violations:
            processed = await self._process_aligned_feedback(feedback, alignment)
            return alignment, processed
        else:
            # Request clarification or adjustment
            clarification = await self._request_clarification(feedback, alignment)
            return alignment, clarification

    async def _validate_helpfulness(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback promotes helpful AI behavior"""
        score = 1.0
        violation = None

        # Check if feedback encourages helpful behavior
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "").lower()

            # Check for unhelpful patterns
            unhelpful_keywords = ["useless", "waste", "stupid", "pointless"]
            if any(keyword in text for keyword in unhelpful_keywords):
                score -= 0.3

            # Check for constructive feedback
            constructive_keywords = [
                "helpful",
                "useful",
                "better",
                "improve",
                "suggest",
            ]
            if any(keyword in text for keyword in constructive_keywords):
                score += 0.2

        # Check rating consistency
        if feedback.feedback_type == FeedbackType.RATING:
            rating = feedback.content.get("rating", 3)
            if rating <= 2 and not feedback.content.get("explanation"):
                score -= 0.2  # Low rating without explanation is less helpful

        score = max(0, min(1, score))

        if score < 0.5:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.HELPFUL,
                severity=1 - score,
                description="Feedback may not promote helpful AI behavior",
                context={"feedback_type": feedback.feedback_type.value},
            )

        return score, violation

    async def _validate_harmlessness(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback doesn't encourage harmful behavior"""
        score = 1.0
        violation = None

        # Check for harmful content
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "").lower()

            for harmful_pattern in self.constitutional_knowledge["harmful_patterns"]:
                if harmful_pattern in text:
                    score = 0.0
                    violation = ConstitutionalViolation(
                        principle=ConstitutionalPrinciple.HARMLESS,
                        severity=1.0,
                        description=f"Feedback contains harmful content: {harmful_pattern}",
                        context={"pattern": harmful_pattern},
                    )
                    break

        # Check if feedback rewards harmful AI responses
        if (
            context.get("ai_response_harmful", False) and feedback.feedback_type == FeedbackType.RATING
        ) and feedback.content.get("rating", 0) >= 4:
            score = 0.2
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.HARMLESS,
                severity=0.8,
                description="High rating given to potentially harmful AI response",
                context={"rating": feedback.content.get("rating")},
            )

        return score, violation

    async def _validate_honesty(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback promotes honest AI behavior"""
        score = 1.0
        violation = None

        # Check if feedback encourages deception
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "").lower()

            deception_keywords = ["lie", "pretend", "fake", "deceive", "trick"]
            if any(keyword in text for keyword in deception_keywords):
                score = 0.3
                violation = ConstitutionalViolation(
                    principle=ConstitutionalPrinciple.HONEST,
                    severity=0.7,
                    description="Feedback may encourage deceptive behavior",
                    context={"detected_keywords": [k for k in deception_keywords if k in text]},
                )

        return score, violation

    async def _validate_privacy(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback respects privacy"""
        score = 1.0
        violation = None

        # Check for personal information in feedback
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "")

            # Simple PII detection (in production, use advanced NER)
            import re

            # Check for email addresses
            if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text):
                score = 0.2
                violation = ConstitutionalViolation(
                    principle=ConstitutionalPrinciple.PRIVACY,
                    severity=0.8,
                    description="Feedback contains email address",
                    context={"pii_type": "email"},
                )

            # Check for phone numbers
            elif re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text):
                score = 0.2
                violation = ConstitutionalViolation(
                    principle=ConstitutionalPrinciple.PRIVACY,
                    severity=0.8,
                    description="Feedback contains phone number",
                    context={"pii_type": "phone"},
                )

        return score, violation

    async def _validate_transparency(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback promotes transparency"""
        score = 1.0

        # Reward feedback that asks for explanations
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "").lower()

            transparency_keywords = ["explain", "why", "how", "reasoning", "understand"]
            if any(keyword in text for keyword in transparency_keywords):
                score = 1.0  # Maximum score for promoting transparency

        return score, None

    async def _validate_fairness(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback promotes fairness"""
        score = 1.0
        violation = None

        # Check for discriminatory content
        if feedback.feedback_type == FeedbackType.TEXT:
            text = feedback.content.get("text", "").lower()

            # Check for bias indicators (simplified)
            bias_keywords = ["only for", "not for", "exclude", "discriminate"]
            if any(keyword in text for keyword in bias_keywords):
                score = 0.5
                violation = ConstitutionalViolation(
                    principle=ConstitutionalPrinciple.FAIR,
                    severity=0.5,
                    description="Feedback may promote biased behavior",
                    context={"potential_bias": True},
                )

        return score, violation

    async def _validate_alignment(
        self, feedback: FeedbackItem, context: dict[str, Any]
    ) -> tuple[float, Optional[ConstitutionalViolation]]:
        """Validate feedback aligns with human values"""
        # Aggregate score from other principles
        score = 0.8  # Base alignment score

        # Check feedback consistency with past behavior
        if hasattr(self, "user_feedback_history"):
            # In production, check if this feedback is consistent
            # with user's historical values
            pass

        return score, None

    async def _process_aligned_feedback(self, feedback: FeedbackItem, alignment: FeedbackAlignment) -> dict[str, Any]:
        """Process feedback that aligns with constitutional principles"""
        # Apply differential privacy
        await self._apply_differential_privacy(feedback)

        # Extract learnings
        learnings = await self._extract_constitutional_learnings(feedback, alignment)

        # Update constitutional knowledge
        await self._update_constitutional_knowledge(learnings)

        return {
            "status": "processed",
            "alignment_score": alignment.overall_alignment,
            "privacy_preserved": True,
            "learnings_extracted": len(learnings),
            "interpretability_trace": alignment.interpretability_trace,
        }

    async def _apply_differential_privacy(self, feedback: FeedbackItem) -> FeedbackItem:
        """Apply differential privacy to feedback"""
        private_feedback = FeedbackItem(
            feedback_id=feedback.feedback_id,
            user_id=hashlib.sha256(feedback.user_id.encode()).hexdigest()[:16],
            session_id=feedback.session_id,
            action_id=feedback.action_id,
            timestamp=feedback.timestamp,
            feedback_type=feedback.feedback_type,
            content=feedback.content.copy(),
            context=feedback.context,
            compliance_region=feedback.compliance_region,
        )

        # Add noise to ratings
        if feedback.feedback_type == FeedbackType.RATING:
            rating = feedback.content.get("rating", 3)
            noise = np.random.laplace(0, 1 / self.privacy_epsilon)
            private_feedback.content["rating"] = np.clip(rating + noise, 1, 5)

        # Anonymize text
        if feedback.feedback_type == FeedbackType.TEXT:
            # In production, use advanced text anonymization
            private_feedback.content["text"] = self._anonymize_text(feedback.content.get("text", ""))

        return private_feedback

    def _anonymize_text(self, text: str) -> str:
        """Anonymize text while preserving meaning"""
        # Simple anonymization - in production use advanced NLP
        import re

        # Remove emails
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", text)

        # Remove phone numbers
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]", text)

        # Remove names (simplified - use NER in production)
        text = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[NAME]", text)

        return text

    async def _extract_constitutional_learnings(
        self, feedback: FeedbackItem, alignment: FeedbackAlignment
    ) -> list[dict[str, Any]]:
        """Extract learnings about constitutional alignment"""
        learnings = []

        # Learn from high-alignment feedback
        if alignment.overall_alignment > 0.9:
            learnings.append(
                {
                    "type": "positive_pattern",
                    "feedback_type": feedback.feedback_type.value,
                    "alignment_score": alignment.overall_alignment,
                    "principle_scores": alignment.principle_scores,
                    "context": feedback.context,
                }
            )

        # Learn from violations
        for violation in alignment.violations:
            learnings.append(
                {
                    "type": "violation_pattern",
                    "principle": violation.principle.value,
                    "severity": violation.severity,
                    "description": violation.description,
                    "context": violation.context,
                }
            )

        return learnings

    async def _update_constitutional_knowledge(self, learnings: list[dict[str, Any]]) -> None:
        """Update constitutional knowledge base with learnings"""
        for learning in learnings:
            learning_type = learning["type"]

            if learning_type not in self.learned_patterns:
                self.learned_patterns[learning_type] = []

            self.learned_patterns[learning_type].append({"learning": learning, "timestamp": datetime.now(timezone.utc)})

            # Limit history size
            if len(self.learned_patterns[learning_type]) > 1000:
                self.learned_patterns[learning_type] = self.learned_patterns[learning_type][-1000:]

    async def _request_clarification(self, feedback: FeedbackItem, alignment: FeedbackAlignment) -> dict[str, Any]:
        """Request clarification for misaligned feedback"""
        # Identify main issues
        issues = []
        for principle, score in alignment.principle_scores.items():
            if score < 0.5:
                issues.append(principle.value)

        return {
            "status": "clarification_needed",
            "alignment_score": alignment.overall_alignment,
            "issues": issues,
            "violations": [
                {
                    "principle": v.principle.value,
                    "severity": v.severity,
                    "description": v.description,
                }
                for v in alignment.violations
            ],
            "suggestion": "Please provide feedback that is helpful, harmless, and honest.",
            "interpretability_trace": alignment.interpretability_trace,
        }

    async def generate_constitutional_report(
        self, time_period: Optional[tuple[datetime, datetime]] = None
    ) -> dict[str, Any]:
        """Generate report on constitutional alignment"""
        report = {
            "summary": {
                "total_feedback_processed": len(self.learned_patterns.get("positive_pattern", [])),
                "total_violations": len(self.violation_history),
                "average_alignment": 0.0,
            },
            "principle_analysis": {},
            "violation_trends": [],
            "learnings": {
                "positive_patterns": len(self.learned_patterns.get("positive_pattern", [])),
                "violation_patterns": len(self.learned_patterns.get("violation_pattern", [])),
            },
            "recommendations": [],
        }

        # Analyze violations by principle
        principle_violations = {}
        for violation in self.violation_history:
            if violation.principle not in principle_violations:
                principle_violations[violation.principle] = {
                    "count": 0,
                    "avg_severity": 0.0,
                    "examples": [],
                }

            principle_violations[violation.principle]["count"] += 1
            principle_violations[violation.principle]["avg_severity"] += violation.severity

        # Calculate averages
        for principle, data in principle_violations.items():
            if data["count"] > 0:
                data["avg_severity"] /= data["count"]
                report["principle_analysis"][principle.value] = data

        # Generate recommendations
        if len(self.violation_history) > 100:
            report["recommendations"].append("High violation rate detected. Consider additional user education.")

        return report

    # Required interface methods

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process request"""
        feedback = data.get("feedback")
        context = data.get("context", {})

        alignment, result = await self.process_feedback_constitutionally(feedback, context)

        return {"alignment": alignment.__dict__, "result": result}

    async def handle_glyph(self, token: Any) -> Any:
        """Handle GLYPH communication"""
        return {
            "operational": self.operational,
            "principles": [p.value for p in ConstitutionalPrinciple],
            "learned_patterns": len(self.learned_patterns),
        }

    async def get_status(self) -> dict[str, Any]:
        """Get system status"""
        return {
            "operational": self.operational,
            "principles_active": len(self.validators),
            "violations_recorded": len(self.violation_history),
            "patterns_learned": sum(len(p) for p in self.learned_patterns.values()),
            "privacy_epsilon": self.privacy_epsilon,
            "interpretability_depth": self.min_interpretability_depth,
        }