import json

import numpy as np

# JULES05_NOTE: Loop-safe guard added
DEFAULT_TOKEN_BUDGET = 10000


def compute_drift_score(
    state1: dict, state2: dict, max_tokens: int = DEFAULT_TOKEN_BUDGET
) -> float:
    """
    Computes a drift score between two states.
    This is a simplified implementation.
    """
    all_keys = set(state1.keys()) | set(state2.keys())

    total_drift = 0.0
    tokens_used = 0

    for key in all_keys:
        val1 = state1.get(key, 0.0)
        val2 = state2.get(key, 0.0)

        # JULES05_NOTE: Loop-safe guard added
        tokens_used += len(json.dumps({key: val1})) / 4
        tokens_used += len(json.dumps({key: val2})) / 4
        if tokens_used > max_tokens:
            print(
                f"Token budget exceeded in drift computation: {tokens_used} > {max_tokens}"
            )
            break

        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            total_drift += abs(val1 - val2)
        elif isinstance(val1, list) and isinstance(val2, list):
            if len(val1) == len(val2):
                try:
                    v1 = np.array(val1, dtype=float)
                    v2 = np.array(val2, dtype=float)
                    total_drift += np.linalg.norm(v1 - v2)
                except (ValueError, TypeError):
                    # Fallback for non-numeric lists
                    pass

    return total_drift


class DriftTracker:
    def __init__(self):
        self.history = []

    def track(self, state):
        self.history.append(state)

    def get_drift(self):
        if len(self.history) < 2:
            return 0.0
        return compute_drift_score(self.history[-2], self.history[-1])
