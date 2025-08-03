"""
Drift Harmonizer
================
Suggests realignment actions when drift metrics diverge.
"""

from typing import List

# ΛTAG: codex, drift, harmonizer


class DriftHarmonizer:
    """Analyze drift history and suggest realignment."""

    def __init__(self, threshold: float = 0.2):
        self.threshold = threshold
        self.history: List[float] = []

    def record_drift(self, score: float) -> None:
        self.history.append(score)

    def suggest_realignment(self) -> str:
        if not self.history:
            return "No drift data"

        avg_drift = sum(self.history) / len(self.history)
        if avg_drift > self.threshold:
            return "Apply symbolic grounding"
        return "Drift stable"
