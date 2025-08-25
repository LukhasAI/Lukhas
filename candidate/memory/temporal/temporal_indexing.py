"""
Temporal Indexing for Memory Events
===================================
This module provides a system for indexing memory events by time.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

class TemporalIndexer:
    """
    A simulated system for indexing memory events by their timestamp,
    allowing for efficient time-based queries.
    """

    def __init__(self):
        # In a real system, this would be a more sophisticated data structure
        # like a B-tree or a time-series database.
        self.time_index: List[Tuple[datetime, str]] = []
        self.event_storage: Dict[str, Dict[str, Any]] = {}

    def index_event(self, event_id: str, event_data: Dict[str, Any], timestamp: datetime):
        """Adds an event to the temporal index."""
        print(f"Indexing event '{event_id}' at {timestamp}")
        self.time_index.append((timestamp, event_id))
        self.event_storage[event_id] = event_data

        # Keep the index sorted by time
        self.time_index.sort(key=lambda x: x[0])

    def get_events_in_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieves all events within a given time range."""
        results = []
        for ts, event_id in self.time_index:
            if start_time <= ts <= end_time:
                results.append(self.event_storage[event_id])

        print(f"Found {len(results)} events between {start_time} and {end_time}")
        return results

    def get_events_near_timestamp(self, timestamp: datetime, window_seconds: int = 60) -> List[Dict[str, Any]]:
        """Retrieves events within a window around a specific timestamp."""
        start_time = timestamp - timedelta(seconds=window_seconds / 2)
        end_time = timestamp + timedelta(seconds=window_seconds / 2)
        return self.get_events_in_range(start_time, end_time)
