from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

try:
    # Prefer Oneiric Core dream generator if available
    from dream.dream_engine.lukhas_oracle_dream import generate_dream
except Exception:  # pragma: no cover - fallback for broken import
    import time
    from datetime import datetime

    def generate_dream(seed: str, context: dict[str, Any] | None = None, timezone) -> dict[str, Any]:
        """Fallback dream generator used when Oneiric Core is unavailable."""
        return {
            "dream_id": f"DREAM_{seed[:4].upper()}_{int(time.time())}",
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "summary": f"Generated dream from seed: '{seed}'",
            "theme": random.choice(["Echo", "Fractal", "Origin"]),
            "context": context or {},
            "emotional_wave": [round(random.uniform(0.1, 1.0), 2) for _ in range(5)],
            "collapse_path": [f"N{random.randint(1, 5)}" for _ in range(3)],
        }


@dataclass
class QIWaveform:
    """# ΛTAG: qi_waveform
    Represents a quantum waveform capable of collapsing into symbolic dreams."""

    base_seed: str

    def collapse(self, probability: float = 0.5, recursion_limit: int = 1) -> dict[str, Any] | None:
        """Collapse waveform and optionally trigger recursive dream generation."""
        if random.random() >= probability:
            return None

        dream = self._request_recursive_dream(self.base_seed, recursion_limit)
        return dream

    def _request_recursive_dream(self, seed: str, limit: int) -> dict[str, Any]:
        dream = generate_dream(seed, context={"recursive": True})
        if limit > 1:
            dream["recursive_child"] = self._request_recursive_dream(dream["dream_id"], limit - 1)
        return dream
