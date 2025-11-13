"""Self-contradiction detection signals."""
from typing import Optional, Any
from datetime import datetime


def contradiction_score(a: str, b: str) -> float:
    """
    Compute contradiction score between two statements (stub).

    In production, this would use semantic embeddings and NLI models.

    Args:
        a: First statement
        b: Second statement

    Returns:
        Contradiction score (0.0 = consistent, 1.0 = contradictory)
    """
    # Simple keyword-based heuristic for demo
    negation_pairs = [
        ("is", "is not"),
        ("can", "cannot"),
        ("will", "will not"),
        ("true", "false"),
        ("yes", "no")
    ]

    a_lower = a.lower()
    b_lower = b.lower()

    for pos, neg in negation_pairs:
        if (pos in a_lower and neg in b_lower) or (neg in a_lower and pos in b_lower):
            return 0.8  # High contradiction

    # Check for opposite statements (very naive)
    if a_lower == b_lower:
        return 0.0  # Identical, no contradiction

    return 0.3  # Some potential contradiction


class SelfContradictionDetected:
    """Event emitted when self-contradiction is detected."""

    def __init__(
        self,
        statement_a: str,
        statement_b: str,
        score: float,
        context: Optional[dict] = None
    ):
        self.statement_a = statement_a
        self.statement_b = statement_b
        self.score = score
        self.context = context or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "statement_a": self.statement_a,
            "statement_b": self.statement_b,
            "score": self.score,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }


if __name__ == "__main__":
    print("=== Self-Contradiction Signal Demo ===\n")

    pairs = [
        ("The system is stable", "The system is not stable"),
        ("This will work", "This will not work"),
        ("The answer is yes", "The answer is no"),
        ("Same statement", "Same statement")
    ]

    for a, b in pairs:
        score = contradiction_score(a, b)
        print(f"'{a}' vs '{b}': {score:.2f}")

        if score > 0.5:
            event = SelfContradictionDetected(a, b, score)
            print(f"  ⚠️ Contradiction detected at {event.timestamp}")
        print()
