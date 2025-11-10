from typing import Any, Dict


class DeontologicalEvaluator:
    def evaluate(
        self, action_type: str, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        rights_violations_count = sum(
            1 for term in rights_violations if term.lower() in content.lower()
        )
        rights_respect_count = sum(
            1 for term in rights_respect if term.lower() in content.lower()
        )

        # Calculate honesty score
        honesty_violations_count = sum(
            1 for term in honesty_violations if term.lower() in content.lower()
        )
        honesty_adherence_count = sum(
            1 for term in honesty_adherence if term.lower() in content.lower()
        )

        # Calculate rights and honesty scores
        if rights_violations_count + rights_respect_count > 0:
            rights_score = rights_respect_count / (
                rights_violations_count + rights_respect_count
            )
        else:
            rights_score = 0.7  # Default when no indicators

        if honesty_violations_count + honesty_adherence_count > 0:
            honesty_score = honesty_adherence_count / (
                honesty_violations_count + honesty_adherence_count
            )
        else:
            honesty_score = 0.7  # Default when no indicators

        # Combine scores, giving more weight to the lower score (more conservative)
        score = (
            min(rights_score, honesty_score) * 0.7
            + ((rights_score + honesty_score) / 2) * 0.3
        )

        # Determine reason based on the lowest component
        if rights_score < honesty_score:
            if rights_score < 0.5:
                reason = "Potential rights or consent violations"
            else:
                reason = "Acceptable rights consideration"
        else:
            reason = (
                "Potential honesty or truthfulness issues"
                if honesty_score < 0.5
                else "Acceptable truthfulness"
            )

        return {"score": score, "reason": reason}
