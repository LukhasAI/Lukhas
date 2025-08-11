#!/usr/bin/env python3
"""
LUKHAS AI Drift Metrics Tracker
==============================
Simple drift tracking system for Guardian System monitoring.

Trinity Framework: ⚛️🧠🛡️
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any

# ΛTAG: drift, metrics, guardian
# ΛORIGIN_AGENT: Claude Agent 2 (Guardian Specialist)

__version__ = "1.0.0"


class DriftTracker:
    """Simple drift metrics tracker for Guardian System integration."""

    def __init__(self, window_size: int = 50):
        """
        Initialize drift tracker.

        Args:
            window_size: Number of recent measurements to keep
        """
        self.window_size = window_size
        self.measurements: deque = deque(maxlen=window_size)
        self.timestamps: deque = deque(maxlen=window_size)
        self.categories: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

    def record(
        self, value: float, category: str = "general", metadata: Optional[Dict] = None
    ) -> None:
        """Record a drift measurement."""
        current_time = time.time()

        self.measurements.append(value)
        self.timestamps.append(current_time)
        self.categories[category].append(value)

    def get_current_drift(self) -> float:
        """Get the most recent drift measurement."""
        if not self.measurements:
            return 0.0
        return self.measurements[-1]

    def get_average_drift(self, category: str = None) -> float:
        """Get average drift for category or overall."""
        if category and category in self.categories:
            values = list(self.categories[category])
        else:
            values = list(self.measurements)

        if not values:
            return 0.0

        return sum(values) / len(values)

    def get_drift_trend(self) -> str:
        """Get drift trend: 'increasing', 'decreasing', or 'stable'."""
        if len(self.measurements) < 3:
            return "stable"

        recent = list(self.measurements)[-3:]
        if recent[-1] > recent[0]:
            return "increasing"
        elif recent[-1] < recent[0]:
            return "decreasing"
        else:
            return "stable"

    def reset(self) -> None:
        """Clear all measurements."""
        self.measurements.clear()
        self.timestamps.clear()
        self.categories.clear()
