"""
Timeline Manager for Causal Memory
==================================
This module provides a system for managing multiple timelines of memory events.
"""

from typing import Any, Dict, List, Optional

class TimelineManager:
    """
    A simulated system for managing different timelines of memory events,
    allowing for branching and what-if scenarios.
    """

    def __init__(self):
        self.timelines: Dict[str, List[str]] = {"main": []} # Start with a main timeline

    def create_timeline(self, timeline_id: str, base_timeline: Optional[str] = None):
        """Creates a new timeline, optionally based on an existing one."""
        if timeline_id in self.timelines:
            print(f"Warning: Timeline {timeline_id} already exists.")
            return

        if base_timeline and base_timeline in self.timelines:
            self.timelines[timeline_id] = list(self.timelines[base_timeline])
            print(f"Created new timeline '{timeline_id}' based on '{base_timeline}'")
        else:
            self.timelines[timeline_id] = []
            print(f"Created new empty timeline '{timeline_id}'")

    def add_event_to_timeline(self, timeline_id: str, event_id: str):
        """Adds an event to a specific timeline."""
        if timeline_id not in self.timelines:
            print(f"Error: Timeline '{timeline_id}' not found.")
            return

        self.timelines[timeline_id].append(event_id)
        print(f"Added event '{event_id}' to timeline '{timeline_id}'")

    def get_timeline(self, timeline_id: str) -> Optional[List[str]]:
        """Retrieves the events for a given timeline."""
        return self.timelines.get(timeline_id)

    def fork_timeline(self, original_timeline_id: str, new_timeline_id: str) -> bool:
        """Creates a new timeline that is a copy of an existing one."""
        if original_timeline_id not in self.timelines:
            print(f"Error: Cannot fork non-existent timeline '{original_timeline_id}'")
            return False

        if new_timeline_id in self.timelines:
            print(f"Error: New timeline id '{new_timeline_id}' already exists.")
            return False

        self.create_timeline(new_timeline_id, base_timeline=original_timeline_id)
        return True
