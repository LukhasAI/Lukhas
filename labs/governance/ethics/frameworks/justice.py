from typing import Any, Dict


class JusticeEvaluator:
    def evaluate(
        self, action_type: str, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        positive_count = sum(
            1 for term in justice_positive if term.lower() in content.lower()
        )
        negative_count = sum(
            1 for term in justice_negative if term.lower() in content.lower()
        )

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
