from typing import Any, Dict


class VirtueEthicsEvaluator:
    def evaluate(
        self, action_type: str, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            virtue_counts[virtue] = sum(
                1 for term in terms if term.lower() in content.lower()
            )

        vice_counts = {}
        for vice, terms in vices.items():
            vice_counts[vice] = sum(
                1 for term in terms if term.lower() in content.lower()
            )

        total_virtues = sum(virtue_counts.values())
        total_vices = sum(vice_counts.values())

        # Calculate virtue score
        if total_virtues + total_vices > 0:
            virtue_score = total_virtues / (total_virtues + total_vices)

            # Identify dominant virtues and vices
            dominant_virtue = max(
                virtues.keys(), key=lambda v: virtue_counts[v], default=None
            )
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
