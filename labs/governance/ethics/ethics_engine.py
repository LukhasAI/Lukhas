"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Enhanced Core TypeScript - Integrated from Advanced Systems
Original: ethics_engine.py
Advanced: ethics_engine.py
Integration Date: 2025-05-31T07:55:28.248308
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any

from .frameworks import (
    CareEthicsEvaluator,
    DeontologicalEvaluator,
    JusticeEvaluator,
    UtilitarianEvaluator,
    VirtueEthicsEvaluator,
)

"""
Ethics Engine for v1_AGI
Evaluates actions and content against ethical frameworks
"""


logger = logging.getLogger("v1_AGI.compliance.ethics")


class EthicsEngine:
    """
    {AIM}{orchestrator}
    Ethics Engine for v1_AGI.

    Evaluates all Cognitive AI actions and outputs against a comprehensive ethical framework
    to ensure alignment with human values and ethical principles. Implements Sam Altman's
    vision of ethics-first AI development.
    """

    def __init__(self):
        """Initialize the ethics engine."""
        logger.info("Initializing Ethics Engine...")

        # Ethical frameworks
        self.frameworks = {
            "utilitarian": {
                "weight": 0.25,
                "description": "Maximizing overall good and minimizing harm",
                "evaluator": UtilitarianEvaluator(),
            },
            "deontological": {
                "weight": 0.25,
                "description": "Following moral duties and respecting rights",
                "evaluator": DeontologicalEvaluator(),
            },
            "virtue_ethics": {
                "weight": 0.2,
                "description": "Cultivating positive character traits",
                "evaluator": VirtueEthicsEvaluator(),
            },
            "justice": {
                "weight": 0.2,
                "description": "Ensuring fairness and equal treatment",
                "evaluator": JusticeEvaluator(),
            },
            "care_ethics": {
                "weight": 0.1,
                "description": "Maintaining compassion and care for individuals",
                "evaluator": CareEthicsEvaluator(),
            },
        }

        # Core ethical principles
        self.principles = {
            "non_maleficence": {
                "weight": 0.3,
                "description": "Do no harm",
                "threshold": 0.9,  # High threshold for harm prevention
            },
            "beneficence": {
                "weight": 0.15,
                "description": "Act for the benefit of others",
            },
            "autonomy": {
                "weight": 0.2,
                "description": "Respect individual freedom and choice",
            },
            "justice": {
                "weight": 0.15,
                "description": "Treat people fairly and equally",
            },
            "transparency": {
                "weight": 0.1,
                "description": "Be open about decisions and processes",
            },
            "privacy": {
                "weight": 0.1,
                "description": "Respect private information and spaces",
            },
        }

        # Ethics metrics
        self.ethics_metrics = {
            "evaluations_total": 0,
            "passed_evaluations": 0,
            "rejected_evaluations": 0,
            "average_ethical_score": 0.0,
            "principled_violations": {},
        }

        # Configuration
        self.scrutiny_level = 1.0  # Standard level
        self.required_confidence = 0.8  # High confidence requirement for ethical clearance

        # Ethics decision history (limited size for memory efficiency)
        self.decision_history = []
        self.max_history_size = 100

        logger.info("Ethics Engine initialized")

    def evaluate_action(self, action_data: dict[str, Any]) -> bool:
        """
        {AIM}{orchestrator}
        Evaluate an action or content against ethical frameworks.

        Args:
            action_data: Data representing the action to evaluate

        Returns:
            bool: Whether the action is ethically acceptable
        """
        # ΛDREAM_LOOP: This method represents a core processing loop that can be a
        # source of decay if not managed.
        self.ethics_metrics["evaluations_total"] += 1

        # Extract action details
        action_type = self._extract_action_type(action_data)
        content = self._extract_content(action_data)
        context = action_data.get("context", {})

        # Evaluate against each ethical framework
        framework_evaluations = {}
        for framework, details in self.frameworks.items():
            evaluation = details["evaluator"].evaluate(action_type, content, context)
            framework_evaluations[framework] = evaluation

        # Evaluate against core principles
        principle_evaluations = {}
        principle_violations = []

        for principle, details in self.principles.items():
            evaluation = self._evaluate_against_principle(
                principle, action_type, content, context
            )
            principle_evaluations[principle] = evaluation

            # Check for principle violations
            threshold = details.get("threshold", self.required_confidence)
            if evaluation["score"] < threshold:
                principle_violations.append(
                    {
                        "principle": principle,
                        "score": evaluation["score"],
                        "reason": evaluation["reason"],
                    }
                )

                # Track violations for metrics
                if principle not in self.ethics_metrics["principled_violations"]:
                    self.ethics_metrics["principled_violations"][principle] = 0
                self.ethics_metrics["principled_violations"][principle] += 1

        # Calculate final ethical score
        # ΛDRIFT_POINT: The weights for the frameworks and principles are
        # hard-coded and can become outdated.
        framework_score = sum(
            evaluation["score"] * self.frameworks[framework]["weight"]
            for framework, evaluation in framework_evaluations.items()
        ) / sum(details["weight"] for details in self.frameworks.values())

        principle_score = sum(
            evaluation["score"] * self.principles[principle]["weight"]
            for principle, evaluation in principle_evaluations.items()
        ) / sum(details["weight"] for details in self.principles.values())

        # Weighted combination, but principles have higher priority
        final_score = (framework_score * 0.4) + (principle_score * 0.6)

        # Adjust by scrutiny level (higher scrutiny = stricter evaluation)
        adjusted_score = final_score / self.scrutiny_level

        # Make ethical decision
        is_ethical = (adjusted_score >= self.required_confidence) and (
            len(principle_violations) == 0
        )

        # Update metrics
        if is_ethical:
            self.ethics_metrics["passed_evaluations"] += 1
        else:
            self.ethics_metrics["rejected_evaluations"] += 1

        # Update average score using running average
        total_eval = self.ethics_metrics["evaluations_total"]
        prev_avg = self.ethics_metrics["average_ethical_score"]
        self.ethics_metrics["average_ethical_score"] = (
            (prev_avg * (total_eval - 1)) + final_score
        ) / total_eval

        # Record decision in history
        self._add_to_history(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_type": action_type,
                "is_ethical": is_ethical,
                "score": final_score,
                "adjusted_score": adjusted_score,
                "scrutiny_level": self.scrutiny_level,
                "principle_violations": [v["principle"] for v in principle_violations],
            }
        )

        return is_ethical

    def _extract_action_type(self, action_data: dict[str, Any]) -> str:
        """Extract the type of action being evaluated."""
        if "action" in action_data:
            return action_data["action"]
        elif "type" in action_data:
            return action_data["type"]
        elif "text" in action_data:
            return "generate_text"
        elif "content" in action_data:
            if (
                isinstance(action_data["content"], dict)
                and "type" in action_data["content"]
            ):
                return f"generate_{action_data['content']['type']}"
            return "generate_content"
        return "unknown"

    def _extract_content(self, action_data: dict[str, Any]) -> str:
        """Extract content for ethical evaluation."""
        if "text" in action_data:
            return action_data["text"]
        elif "content" in action_data:
            if isinstance(action_data["content"], str):
                return action_data["content"]
            elif (
                isinstance(action_data["content"], dict)
                and "text" in action_data["content"]
            ):
                return action_data["content"]["text"]
            elif isinstance(action_data["content"], dict):
                return json.dumps(action_data["content"])
        elif "result" in action_data:
            if isinstance(action_data["result"], str):
                return action_data["result"]
            return json.dumps(action_data["result"])
        return ""

    def _evaluate_against_principle(
        self, principle: str, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate action against a specific ethical principle.

        Args:
            principle: Ethical principle to use
            action_type: Type of action being evaluated
            content: Content to evaluate
            context: Additional context for evaluation

        Returns:
            Dict: Evaluation results
        """
        # Principle-specific evaluation logic
        if principle == "non_maleficence":
            return self._evaluate_non_maleficence(action_type, content, context)
        elif principle == "beneficence":
            return self._evaluate_beneficence(action_type, content, context)
        elif principle == "autonomy":
            return self._evaluate_autonomy(action_type, content, context)
        elif principle == "justice":
            return self._evaluate_justice_principle(action_type, content, context)
        elif principle == "transparency":
            return self._evaluate_transparency(action_type, content, context)
        elif principle == "privacy":
            return self._evaluate_privacy(action_type, content, context)
        else:
            logger.warning(f"Unknown principle: {principle}")
            return {"score": 0.5, "reason": f"Unknown principle: {principle}"}

    def _evaluate_non_maleficence(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of non-maleficence (do no harm)."""
        # List of harmful content indicators
        harm_indicators = [
            "harm",
            "hurt",
            "injure",
            "damage",
            "suffer",
            "pain",
            "abuse",
            "violence",
            "kill",
            "attack",
            "threat",
            "dangerous",
            "hostile",
        ]

        # Count harm indicators
        harm_count = sum(
            1 for indicator in harm_indicators if indicator.lower() in content.lower()
        )

        # Calculate harm risk
        if harm_count == 0:
            score = 0.95  # Very high score when no harm indicators
            reason = "No harm indicators detected"
        else:
            # Scale down score based on number of harm indicators
            score = max(0.0, 1.0 - (harm_count * 0.15))

            reason = (
                "Multiple indicators of potential harm"
                if score < 0.5
                else "Limited indicators of potential harm"
            )

        # Apply extra scrutiny for certain action types
        high_risk_actions = [
            "generate_image_of_person",
            "generate_personal_advice",
            "execute_command",
        ]
        if action_type in high_risk_actions:
            score = score * 0.9  # 10% reduction for high-risk actions

        return {"score": score, "reason": reason}

    def _evaluate_beneficence(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of beneficence (do good)."""
        # List of benefit indicators
        benefit_indicators = [
            "help",
            "benefit",
            "improve",
            "enhance",
            "support",
            "assist",
            "positive",
            "good",
            "useful",
            "valuable",
            "constructive",
        ]

        # Count benefit indicators
        benefit_count = sum(
            1
            for indicator in benefit_indicators
            if indicator.lower() in content.lower()
        )

        # Calculate benefit score
        if benefit_count == 0:
            score = 0.6  # Neutral score when no benefit indicators
            reason = "No clear beneficence indicators"
        else:
            # Scale up score based on number of benefit indicators
            score = min(0.98, 0.6 + (benefit_count * 0.08))

            reason = (
                "Strong indicators of positive benefit"
                if score > 0.8
                else "Some indicators of potential benefit"
            )

        return {"score": score, "reason": reason}

    def _evaluate_autonomy(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of autonomy (respect freedom)."""
        # List of autonomy respect indicators
        autonomy_respect = [
            "choice",
            "option",
            "decision",
            "consent",
            "permission",
            "agree",
            "voluntary",
            "freedom",
            "control",
            "prefer",
        ]

        # List of autonomy violation indicators
        autonomy_violation = [
            "force",
            "coerce",
            "manipulate",
            "pressure",
            "deceive",
            "trick",
            "require",
            "must",
            "only",
            "no choice",
        ]

        # Count indicators
        respect_count = sum(
            1 for term in autonomy_respect if term.lower() in content.lower()
        )
        violation_count = sum(
            1 for term in autonomy_violation if term.lower() in content.lower()
        )

        # Calculate autonomy score
        if respect_count + violation_count == 0:
            score = 0.7  # Default when no indicators
            reason = "No clear autonomy indicators"
        else:
            autonomy_ratio = (
                respect_count / (respect_count + violation_count)
                if (respect_count + violation_count) > 0
                else 0.5
            )
            score = 0.4 + (autonomy_ratio * 0.6)  # Scale to 0.4-1.0

            if score > 0.8:
                reason = "Strongly respects individual autonomy"
            elif score > 0.6:
                reason = "Generally respects choice and consent"
            else:
                reason = "Potential autonomy concerns"

        return {"score": score, "reason": reason}

    def _evaluate_justice_principle(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of justice (fairness)."""
        # This is similar to the justice framework but focused specifically on fairness
        justice_positive = ["fair", "equal", "equitable", "impartial", "unbiased"]
        justice_negative = [
            "unfair",
            "biased",
            "discriminatory",
            "preferential",
            "prejudiced",
        ]

        # Count indicators
        positive_count = sum(
            1 for term in justice_positive if term.lower() in content.lower()
        )
        negative_count = sum(
            1 for term in justice_negative if term.lower() in content.lower()
        )

        # Calculate justice score
        if positive_count + negative_count == 0:
            score = 0.7  # Default when no indicators
            reason = "No clear fairness indicators"
        else:
            justice_ratio = (
                positive_count / (positive_count + negative_count)
                if (positive_count + negative_count) > 0
                else 0.5
            )
            score = 0.4 + (justice_ratio * 0.6)  # Scale to 0.4-1.0

            reason = (
                "Potential fairness or equality concerns"
                if score < 0.5
                else "Adequate fairness indicators"
            )

        return {"score": score, "reason": reason}

    def _evaluate_transparency(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of transparency."""
        # List of transparency indicators
        transparency_positive = [
            "explain",
            "transparent",
            "clear",
            "disclose",
            "inform",
            "reveal",
            "clarify",
            "detail",
            "specific",
            "open",
        ]

        transparency_negative = [
            "hide",
            "obscure",
            "vague",
            "unclear",
            "ambiguous",
            "secret",
            "withhold",
            "mislead",
            "confuse",
        ]

        # Count indicators
        positive_count = sum(
            1 for term in transparency_positive if term.lower() in content.lower()
        )
        negative_count = sum(
            1 for term in transparency_negative if term.lower() in content.lower()
        )

        # Calculate transparency score
        if positive_count + negative_count == 0:
            score = 0.6  # Default when no indicators
            reason = "No clear transparency indicators"
        else:
            transparency_ratio = (
                positive_count / (positive_count + negative_count)
                if (positive_count + negative_count) > 0
                else 0.5
            )
            score = 0.4 + (transparency_ratio * 0.6)  # Scale to 0.4-1.0

            reason = (
                "Good transparency and clarity"
                if score > 0.7
                else "Limited transparency indicators"
            )

        return {"score": score, "reason": reason}

    def _evaluate_privacy(
        self, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Evaluate against the principle of privacy."""
        # List of privacy risk indicators
        privacy_concerns = [
            "personal",
            "private",
            "confidential",
            "sensitive",
            "data",
            "information",
            "identity",
            "address",
            "number",
            "password",
        ]

        privacy_protections = [
            "anonymous",
            "protected",
            "secure",
            "confidential",
            "encrypted",
            "privacy",
            "consent",
            "permission",
        ]

        # Count indicators
        concerns_count = sum(
            1 for term in privacy_concerns if term.lower() in content.lower()
        )
        protections_count = sum(
            1 for term in privacy_protections if term.lower() in content.lower()
        )

        # Calculate privacy score
        if concerns_count == 0:
            # No privacy concerns detected
            score = 0.9
            reason = "No privacy concerns detected"
        else:
            # Calculate ratio of protections to concerns
            protection_ratio = (
                protections_count / concerns_count if concerns_count > 0 else 1.0
            )
            score = min(0.9, 0.5 + (protection_ratio * 0.4))  # Scale to 0.5-0.9

            if score < 0.6:
                reason = "Potential privacy concerns without adequate protections"
            else:
                reason = "Privacy concerns with appropriate protections"

        return {"score": score, "reason": reason}

    def suggest_alternatives(self, action_data: dict[str, Any]) -> list[str]:
        """
        Suggest ethical alternatives for rejected actions.

        Args:
            action_data: Data representing the rejected action

        Returns:
            List[str]: List of alternative suggestions
        """
        self._extract_action_type(action_data)
        content = self._extract_content(action_data)

        # Identify areas of concern
        concerns = []

        # Check for harmful content
        harm_indicators = [
            "harm",
            "hurt",
            "injure",
            "damage",
            "suffer",
            "pain",
            "abuse",
            "violence",
        ]
        if any(indicator.lower() in content.lower() for indicator in harm_indicators):
            concerns.append("harmful_content")

        # Check for privacy issues
        privacy_indicators = [
            "personal",
            "private",
            "confidential",
            "sensitive",
            "data",
            "address",
        ]
        if any(
            indicator.lower() in content.lower() for indicator in privacy_indicators
        ):
            concerns.append("privacy")

        # Check for potential manipulation
        manipulation_indicators = ["manipulate", "trick", "deceive", "force", "coerce"]
        if any(
            indicator.lower() in content.lower() for indicator in manipulation_indicators
        ):
            concerns.append("manipulation")

        # Check for potential bias
        bias_indicators = ["all", "always", "never", "every", "typical", "group"]
        if any(indicator.lower() in content.lower() for indicator in bias_indicators):
            concerns.append("bias")

        # Generate alternatives based on concerns
        alternatives = []

        if "harmful_content" in concerns:
            alternatives.append(
                "Consider focusing on constructive or positive aspects instead"
            )
            alternatives.append(
                "Reframe to emphasize benefits rather than potential harms"
            )

        if "privacy" in concerns:
            alternatives.append(
                "Use anonymized or generalized examples instead of specific details"
            )
            alternatives.append("Remove any personally identifiable information")

        if "manipulation" in concerns:
            alternatives.append(
                "Present balanced information that respects user autonomy"
            )
            alternatives.append("Focus on informing rather than persuading")

        if "bias" in concerns:
            alternatives.append("Present multiple perspectives on the topic")
            alternatives.append(
                "Avoid generalizations and qualify statements appropriately"
            )

        # If no specific concerns were identified or no alternatives generated
        if not alternatives:
            alternatives.append("Reframe the request to align with ethical guidelines")
            alternatives.append("Focus on educational or constructive content")

        return alternatives

    def increase_scrutiny_level(self, factor: float) -> None:
        """
        Increase the scrutiny level for ethical evaluations.

        Args:
            factor: Factor by which to increase scrutiny (1.0 = standard)
        """
        self.scrutiny_level = min(2.0, self.scrutiny_level * factor)
        logger.info(f"Ethics scrutiny level increased to {self.scrutiny_level}")

    def reset_scrutiny_level(self) -> None:
        """Reset scrutiny level to default."""
        self.scrutiny_level = 1.0
        logger.info("Ethics scrutiny level reset to standard")

    def incorporate_feedback(self, feedback: dict[str, Any]) -> None:
        """
        Incorporate feedback to improve ethical evaluations.

        Args:
            feedback: Feedback data to incorporate
        """
        if "ethical_adjustment" in feedback:
            adjustment = feedback["ethical_adjustment"]

            # Adjust required confidence based on feedback
            if "confidence_threshold" in adjustment:
                self.required_confidence = adjustment["confidence_threshold"]

            # Adjust framework weights if provided
            if "framework_weights" in adjustment and isinstance(
                adjustment["framework_weights"], dict
            ):
                for framework, weight in adjustment["framework_weights"].items():
                    if framework in self.frameworks:
                        self.frameworks[framework]["weight"] = weight

            # Adjust principle weights if provided
            if "principle_weights" in adjustment and isinstance(
                adjustment["principle_weights"], dict
            ):
                for principle, weight in adjustment["principle_weights"].items():
                    if principle in self.principles:
                        self.principles[principle]["weight"] = weight

            logger.info("Ethics engine updated based on feedback")

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current ethics metrics.

        Returns:
            Dict: Current ethics metrics
        """
        return self.ethics_metrics.copy()

    def _add_to_history(self, decision: dict[str, Any]) -> None:
        """Add decision to history with size limit."""
        self.decision_history.append(decision)

        # Prune history if it exceeds max size
        if len(self.decision_history) > self.max_history_size:
            self.decision_history = self.decision_history[-self.max_history_size :]
