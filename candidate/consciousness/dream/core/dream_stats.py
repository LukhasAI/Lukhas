"""
Mock dream_stats module
Temporary implementation - see MOCK_TRANSPARENCY_LOG.md
"""
import random
from datetime import datetime, timedelta, timezone
from typing import Any


class DreamStatistics:
    """Mock DreamStatistics class"""

    def __init__(self):
        self.stats = {
            "total_dreams": 0,
            "avg_duration": 0.0,
            "common_themes": [],
            "emotional_distribution": {},
        }

    def update_stats(self, dream_data: dict) -> None:
        """Mock update_stats method"""
        self.stats["total_dreams"] += 1

    def get_summary(self) -> dict[str, Any]:
        """Mock get_summary method"""
        return {
            "total_dreams": self.stats["total_dreams"],
            "avg_duration_minutes": random.randint(5, 30),
            "most_common_theme": "transformation",
            "rem_percentage": random.uniform(20, 25),
        }

    def get_trends(self, days: int = 7) -> list[dict]:
        """Mock get_trends method"""
        trends = []
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=i)
            trends.append(
                {
                    "date": date.isoformat(),
                    "dream_count": random.randint(3, 8),
                    "quality_score": random.uniform(0.6, 0.9),
                }
            )
        return trends


# Global instance
dream_stats = DreamStatistics()
