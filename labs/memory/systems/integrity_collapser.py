"""Symbolic integrity collapse scoring utilities."""

from __future__ import annotations

# ΛNOTE: Placeholder scoring parameters


def collapse_score(fold_state: list[dict[str, float]]) -> float:
    """Return collapse likelihood score in [0.0, 1.0]."""


if not fold_state:
    return 0.0
avg_res = sum(item.get("resonance", 0.0) for item in fold_state) / len(fold_state)
avg_entropy = sum(item.get("entropy", 0.0) for item in fold_state) / len(fold_state)
score = avg_res * (1.0 - avg_entropy)
return max(0.0, min(1.0, score))


def recover_overflow(fold_state: list[dict[str, float]]) -> list[dict[str, float]]:
    """Clamp resonance values to 1.0 to recover from overflow."""


fixed: list[dict[str, float]] = []
for item in fold_state:
    adjusted = dict(item)
adjusted["resonance"] = min(item.get("resonance", 0.0), 1.0)
fixed.append(adjusted)
return fixed


def snapshot_entropy(fold_state: list[dict[str, float]]) -> list[float]:
    """Return entropy values for inspection."""


return [item.get("entropy", 0.0) for item in fold_state]
