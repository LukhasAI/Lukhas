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
from datetime import datetime
from typing import Any

"""
Ethics Engine for v1_AGI
Evaluates actions and content against ethical frameworks
"""


logger = logging.getLogger("v1_AGI.compliance.ethics")


class EthicsEngine:
    """
    {AIM}{orchestrator}
    Ethics Engine for v1_AGI.

    Evaluates all AGI actions and outputs against a comprehensive ethical framework
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
            },
            "deontological": {
                "weight": 0.25,
                "description": "Following moral duties and respecting rights",
            },
            "virtue_ethics": {
                "weight": 0.2,
                "description": "Cultivating positive character traits",
            },
            "justice": {
                "weight": 0.2,
                "description": "Ensuring fairness and equal treatment",
            },
            "care_ethics": {
                "weight": 0.1,
                "description": "Maintaining compassion and care for individuals",
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
            evaluation = self._evaluate_against_framework(framework, action_type, content, context)
            framework_evaluations[framework] = evaluation

        # Evaluate against core principles
        principle_evaluations = {}
        principle_violations = []

        for principle, details in self.principles.items():
            evaluation = self._evaluate_against_principle(principle, action_type, content, context)
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
        is_ethical = (adjusted_score >= self.required_confidence) and (len(principle_violations) == 0)

        # Update metrics
        if is_ethical:
            self.ethics_metrics["passed_evaluations"] += 1
        else:
            self.ethics_metrics["rejected_evaluations"] += 1

        # Update average score using running average
        total_eval = self.ethics_metrics["evaluations_total"]
        prev_avg = self.ethics_metrics["average_ethical_score"]
        self.ethics_metrics["average_ethical_score"] = ((prev_avg * (total_eval - 1)) + final_score) / total_eval

        # Record decision in history
        self._add_to_history(
            {
                "timestamp": datetime.now().isoformat(),
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
            if isinstance(action_data["content"], dict) and "type" in action_data["content"]:
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
            elif isinstance(action_data["content"], dict) and "text" in action_data["content"]:
                return action_data["content"]["text"]
            elif isinstance(action_data["content"], dict):
                return json.dumps(action_data["content"])
        elif "result" in action_data:
            if isinstance(action_data["result"], str):
                return action_data["result"]
            return json.dumps(action_data["result"])
        return ""

    def _evaluate_against_framework(
        self, framework: str, action_type: str, content: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate action against a specific ethical framework.

        Args:
            framework: Ethical framework to use
            action_type: Type of action being evaluated
            content: Content to evaluate
            context: Additional context for evaluation

        Returns:
            Dict: Evaluation results
        """
        # Framework-specific evaluation logic
        if framework == "utilitarian":
            return self._evaluate_utilitarian(action_type, content, context)
        elif framework == "deontological":
            return self._evaluate_deontological(action_type, content, context)
        elif framework == "virtue_ethics":
            return self._evaluate_virtue_ethics(action_type, content, context)
        elif framework == "justice":
            return self._evaluate_justice(action_type, content, context)
        elif framework == "care_ethics":
            return self._evaluate_care_ethics(action_type, content, context)
        else:
            logger.warning(f"Unknown framework: {framework}")
            return {"score": 0.5, "reason": f"Unknown framework: {framework}"}

    def _evaluate_utilitarian(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate from a utilitarian perspective."""
        # Simplified utilitarian calculation using keywords
        positive_keywords = [
            "benefit",
            "helps",
            "improves",
            "positive",
            "good",
            "useful",
            "valuable",
            "welfare",
        ]
        negative_keywords = [
            "harm",
            "hurt",
            "damage",
            "negative",
            "painful",
            "suffering",
            "distress",
        ]

        positive_count = sum(1 for kw in positive_keywords if kw.lower() in content.lower())
        negative_count = sum(1 for kw in negative_keywords if kw.lower() in content.lower())

        # Simple scoring algorithm
        if positive_count + negative_count == 0:
            score = 0.7  # Default neutral-positive score when no indicators
            reason = "No clear utilitarian indicators"
        else:
            # Calculate score as ratio of positive keywords
            utilitarian_ratio = (
                positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
            )

            # Scale to 0.4-1.0 range (minimum 0.4 baseline)
            score = 0.4 + (utilitarian_ratio * 0.6)

            if score >= 0.8:
                reason = "Strong positive utility indicators"
            elif score >= 0.6:
                reason = "Moderate positive utility"
            elif score >= 0.4:
                reason = "Mixed utility indicators"
            else:
                reason = "Potential negative utility concerns"

        return {"score": score, "reason": reason}

    def _evaluate_deontological(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate from a deontological (duty-based) perspective."""
        # Rights-based keywords
        rights_violations = [
            "violate",
            "infringe",
            "against consent",
            "force",
            "manipulate",
            "deceive",
        ]
        rights_respect = [
            "consent",
            "permission",
            "rights",
            "dignity",
            "respect",
            "agreement",
        ]

        # Truth and honesty keywords
        honesty_violations = ["lie", "deceive", "mislead", "false", "fake", "untrue"]
        honesty_adherence = ["truth", "honest", "accurate", "factual", "verified"]

        # Calculate rights score
        rights_violations_count = sum(1 for term in rights_violations if term.lower() in content.lower())
        rights_respect_count = sum(1 for term in rights_respect if term.lower() in content.lower())

        # Calculate honesty score
        honesty_violations_count = sum(1 for term in honesty_violations if term.lower() in content.lower())
        honesty_adherence_count = sum(1 for term in honesty_adherence if term.lower() in content.lower())

        # Calculate rights and honesty scores
        if rights_violations_count + rights_respect_count > 0:
            rights_score = rights_respect_count / (rights_violations_count + rights_respect_count)
        else:
            rights_score = 0.7  # Default when no indicators

        if honesty_violations_count + honesty_adherence_count > 0:
            honesty_score = honesty_adherence_count / (honesty_violations_count + honesty_adherence_count)
        else:
            honesty_score = 0.7  # Default when no indicators

        # Combine scores, giving more weight to the lower score (more conservative)
        score = min(rights_score, honesty_score) * 0.7 + ((rights_score + honesty_score) / 2) * 0.3

        # Determine reason based on the lowest component
        if rights_score < honesty_score:
            if rights_score < 0.5:
                reason = "Potential rights or consent violations"
            else:
                reason = "Acceptable rights consideration"
        else:
            reason = "Potential honesty or truthfulness issues" if honesty_score < 0.5 else "Acceptable truthfulness"

        return {"score": score, "reason": reason}

    def _evaluate_virtue_ethics(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate from a virtue ethics perspective."""
        # Virtues to check for
        virtues = {
            "honesty": ["honest", "truth", "authentic"],
            "compassion": ["compassion", "empathy", "care"],
            "courage": ["courage", "brave", "stand up"],
            "wisdom": ["wisdom", "thoughtful", "consider"],
            "temperance": ["balance", "moderation", "restraint"],
        }

        # Vices to check against
        vices = {
            "dishonesty": ["dishonest", "lie", "deceit"],
            "cruelty": ["cruel", "callous", "indifferent"],
            "cowardice": ["fear", "avoid responsibility", "evade"],
            "foolishness": ["rash", "impulsive", "thoughtless"],
            "excess": ["excessive", "extreme", "immoderate"],
        }

        # Count virtues and vices
        virtue_counts = {}
        for virtue, terms in virtues.items():
            virtue_counts[virtue] = sum(1 for term in terms if term.lower() in content.lower())

        vice_counts = {}
        for vice, terms in vices.items():
            vice_counts[vice] = sum(1 for term in terms if term.lower() in content.lower())

        total_virtues = sum(virtue_counts.values())
        total_vices = sum(vice_counts.values())

        # Calculate virtue score
        if total_virtues + total_vices > 0:
            virtue_score = total_virtues / (total_virtues + total_vices)

            # Identify dominant virtues and vices
            dominant_virtue = max(virtues.keys(), key=lambda v: virtue_counts[v], default=None)
            dominant_vice = max(vices.keys(), key=lambda v: vice_counts[v], default=None)

            if virtue_score > 0.7:
                reason = f"Demonstrates virtuous qualities, particularly {dominant_virtue}"
            elif virtue_score < 0.4:
                reason = f"May exhibit negative qualities, such as {dominant_vice}"
            else:
                reason = "Mixed virtue indicators"
        else:
            virtue_score = 0.6  # Default when no indicators
            reason = "No clear virtue indicators"

        return {"score": virtue_score, "reason": reason}

    def _evaluate_justice(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate from a justice perspective."""
        # Justice indicators
        justice_positive = [
            "fair",
            "equal",
            "equitable",
            "rights",
            "deserves",
            "justice",
        ]
        justice_negative = [
            "unfair",
            "biased",
            "discriminate",
            "prejudice",
            "inequality",
            "privilege",
        ]

        # Count indicators
        positive_count = sum(1 for term in justice_positive if term.lower() in content.lower())
        negative_count = sum(1 for term in justice_negative if term.lower() in content.lower())

        # Calculate justice score
        if positive_count + negative_count > 0:
            justice_ratio = positive_count / (positive_count + negative_count)
            justice_score = 0.4 + (justice_ratio * 0.6)  # Scale to 0.4-1.0

            if justice_score > 0.8:
                reason = "Strong commitment to fairness and equality"
            elif justice_score > 0.6:
                reason = "Generally supports fair treatment"
            elif justice_score > 0.5:
                reason = "Mixed justice considerations"
            else:
                reason = "Potential justice or fairness concerns"
        else:
            justice_score = 0.7  # Default when no indicators
            reason = "No clear justice indicators"

        return {"score": justice_score, "reason": reason}

    def _evaluate_care_ethics(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate from a care ethics perspective."""
        # Care indicators
        care_positive = [
            "care",
            "support",
            "nurture",
            "protect",
            "help",
            "compassion",
            "empathy",
        ]
        care_negative = ["neglect", "abandon", "ignore", "callous", "indifferent"]

        # Count indicators
        positive_count = sum(1 for term in care_positive if term.lower() in content.lower())
        negative_count = sum(1 for term in care_negative if term.lower() in content.lower())

        # Calculate care score
        if positive_count + negative_count > 0:
            care_ratio = (
                positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
            )
            care_score = 0.4 + (care_ratio * 0.6)  # Scale to 0.4-1.0

            if care_score > 0.8:
                reason = "Demonstrates strong care and compassion"
            elif care_score > 0.6:
                reason = "Shows consideration for wellbeing"
            elif care_score > 0.5:
                reason = "Mixed care considerations"
            else:
                reason = "May lack sufficient care or compassion"
        else:
            care_score = 0.65  # Default when no indicators
            reason = "No clear care indicators"

        return {"score": care_score, "reason": reason}

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

    def _evaluate_non_maleficence(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        harm_count = sum(1 for indicator in harm_indicators if indicator.lower() in content.lower())

        # Calculate harm risk
        if harm_count == 0:
            score = 0.95  # Very high score when no harm indicators
            reason = "No harm indicators detected"
        else:
            # Scale down score based on number of harm indicators
            score = max(0.0, 1.0 - (harm_count * 0.15))

            reason = "Multiple indicators of potential harm" if score < 0.5 else "Limited indicators of potential harm"

        # Apply extra scrutiny for certain action types
        high_risk_actions = [
            "generate_image_of_person",
            "generate_personal_advice",
            "execute_command",
        ]
        if action_type in high_risk_actions:
            score = score * 0.9  # 10% reduction for high-risk actions

        return {"score": score, "reason": reason}

    def _evaluate_beneficence(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        benefit_count = sum(1 for indicator in benefit_indicators if indicator.lower() in content.lower())

        # Calculate benefit score
        if benefit_count == 0:
            score = 0.6  # Neutral score when no benefit indicators
            reason = "No clear beneficence indicators"
        else:
            # Scale up score based on number of benefit indicators
            score = min(0.98, 0.6 + (benefit_count * 0.08))

            reason = "Strong indicators of positive benefit" if score > 0.8 else "Some indicators of potential benefit"

        return {"score": score, "reason": reason}

    def _evaluate_autonomy(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        respect_count = sum(1 for term in autonomy_respect if term.lower() in content.lower())
        violation_count = sum(1 for term in autonomy_violation if term.lower() in content.lower())

        # Calculate autonomy score
        if respect_count + violation_count == 0:
            score = 0.7  # Default when no indicators
            reason = "No clear autonomy indicators"
        else:
            autonomy_ratio = (
                respect_count / (respect_count + violation_count) if (respect_count + violation_count) > 0 else 0.5
            )
            score = 0.4 + (autonomy_ratio * 0.6)  # Scale to 0.4-1.0

            if score > 0.8:
                reason = "Strongly respects individual autonomy"
            elif score > 0.6:
                reason = "Generally respects choice and consent"
            else:
                reason = "Potential autonomy concerns"

        return {"score": score, "reason": reason}

    def _evaluate_justice_principle(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        positive_count = sum(1 for term in justice_positive if term.lower() in content.lower())
        negative_count = sum(1 for term in justice_negative if term.lower() in content.lower())

        # Calculate justice score
        if positive_count + negative_count == 0:
            score = 0.7  # Default when no indicators
            reason = "No clear fairness indicators"
        else:
            justice_ratio = (
                positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
            )
            score = 0.4 + (justice_ratio * 0.6)  # Scale to 0.4-1.0

            reason = "Potential fairness or equality concerns" if score < 0.5 else "Adequate fairness indicators"

        return {"score": score, "reason": reason}

    def _evaluate_transparency(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        positive_count = sum(1 for term in transparency_positive if term.lower() in content.lower())
        negative_count = sum(1 for term in transparency_negative if term.lower() in content.lower())

        # Calculate transparency score
        if positive_count + negative_count == 0:
            score = 0.6  # Default when no indicators
            reason = "No clear transparency indicators"
        else:
            transparency_ratio = (
                positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
            )
            score = 0.4 + (transparency_ratio * 0.6)  # Scale to 0.4-1.0

            reason = "Good transparency and clarity" if score > 0.7 else "Limited transparency indicators"

        return {"score": score, "reason": reason}

    def _evaluate_privacy(self, action_type: str, content: str, context: dict[str, Any]) -> dict[str, Any]:
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
        concerns_count = sum(1 for term in privacy_concerns if term.lower() in content.lower())
        protections_count = sum(1 for term in privacy_protections if term.lower() in content.lower())

        # Calculate privacy score
        if concerns_count == 0:
            # No privacy concerns detected
            score = 0.9
            reason = "No privacy concerns detected"
        else:
            # Calculate ratio of protections to concerns
            protection_ratio = protections_count / concerns_count if concerns_count > 0 else 1.0
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
        if any(indicator.lower() in content.lower() for indicator in privacy_indicators):
            concerns.append("privacy")

        # Check for potential manipulation
        manipulation_indicators = ["manipulate", "trick", "deceive", "force", "coerce"]
        if any(indicator.lower() in content.lower() for indicator in manipulation_indicators):
            concerns.append("manipulation")

        # Check for potential bias
        bias_indicators = ["all", "always", "never", "every", "typical", "group"]
        if any(indicator.lower() in content.lower() for indicator in bias_indicators):
            concerns.append("bias")

        # Generate alternatives based on concerns
        alternatives = []

        if "harmful_content" in concerns:
            alternatives.append("Consider focusing on constructive or positive aspects instead")
            alternatives.append("Reframe to emphasize benefits rather than potential harms")

        if "privacy" in concerns:
            alternatives.append("Use anonymized or generalized examples instead of specific details")
            alternatives.append("Remove any personally identifiable information")

        if "manipulation" in concerns:
            alternatives.append("Present balanced information that respects user autonomy")
            alternatives.append("Focus on informing rather than persuading")

        if "bias" in concerns:
            alternatives.append("Present multiple perspectives on the topic")
            alternatives.append("Avoid generalizations and qualify statements appropriately")

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
            if "framework_weights" in adjustment and isinstance(adjustment["framework_weights"], dict):
                for framework, weight in adjustment["framework_weights"].items():
                    if framework in self.frameworks:
                        self.frameworks[framework]["weight"] = weight

            # Adjust principle weights if provided
            if "principle_weights" in adjustment and isinstance(adjustment["principle_weights"], dict):
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
