from typing import Any, Dict


class UtilitarianEvaluator:
    def evaluate(
        self, action_type: str, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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

        positive_count = sum(
            1 for kw in positive_keywords if kw.lower() in content.lower()
        )
        negative_count = sum(
            1 for kw in negative_keywords if kw.lower() in content.lower()
        )

        # Simple scoring algorithm
        if positive_count + negative_count == 0:
            score = 0.7  # Default neutral-positive score when no indicators
            reason = "No clear utilitarian indicators"
        else:
            # Calculate score as ratio of positive keywords
            utilitarian_ratio = (
                positive_count / (positive_count + negative_count)
                if (positive_count + negative_count) > 0
                else 0.5
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
