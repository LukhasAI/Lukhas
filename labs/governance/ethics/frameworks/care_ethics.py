from typing import Any, Dict


class CareEthicsEvaluator:
    def evaluate(
        self, action_type: str, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        positive_count = sum(
            1 for term in care_positive if term.lower() in content.lower()
        )
        negative_count = sum(
            1 for term in care_negative if term.lower() in content.lower()
        )

        # Calculate care score
        if positive_count + negative_count > 0:
            care_ratio = (
                positive_count / (positive_count + negative_count)
                if (positive_count + negative_count) > 0
                else 0.5
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
