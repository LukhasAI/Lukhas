from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class QuantumFlux:
    """# ΛTAG: quantum_entropy
    Provides entropy metrics for dream variability."""

    seed: Optional[int] = None

    def measure_entropy(self) -> float:
        """Return a pseudo-random entropy value between 0 and 1."""
        rng = random.Random(self.seed)
        return rng.random()
