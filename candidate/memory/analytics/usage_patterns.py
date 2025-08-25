"""
Memory Usage Pattern Analytics
==============================
This module provides utilities for analyzing memory usage patterns.
"""

from collections import Counter
from typing import List, Tuple

class UsagePatternAnalyzer:
    """
    A simulated system for analyzing memory access patterns to identify
    hot and cold spots.
    """

    def __init__(self):
        self.access_log: List[str] = []

    def log_access(self, memory_id: str):
        """Logs an access event for a given memory ID."""
        self.access_log.append(memory_id)

    def get_hot_spots(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Simulates identifying memory "hot spots" (most frequently accessed).
        Returns a list of (memory_id, access_count) tuples.
        """
        if not self.access_log:
            return []

        counts = Counter(self.access_log)
        return counts.most_common(top_n)

    def get_cold_spots(self, bottom_n: int = 5) -> List[Tuple[str, int]]:
        """
        Simulates identifying memory "cold spots" (least frequently accessed).
        Returns a list of (memory_id, access_count) tuples.
        """
        if not self.access_log:
            return []

        counts = Counter(self.access_log)
        # The `most_common` method with a negative argument gives all items,
        # so we can take the last `n` for the least common.
        return counts.most_common()[:-bottom_n-1:-1]
