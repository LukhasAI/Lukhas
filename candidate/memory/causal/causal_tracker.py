"""
Causal Relationship Tracker for Memory
=======================================
This module provides a system for tracking causal relationships between memory events.
"""

from typing import Any, Dict, List, Optional

class CausalTracker:
    """
    A simulated system for tracking causal relationships between memory events.
    """

    def __init__(self):
        self.events: Dict[str, Dict[str, Any]] = {}
        self.causal_links: Dict[str, List[str]] = {} # event_id -> list of causes

    def add_event(self, event_id: str, event_data: Dict[str, Any]):
        """Adds a new event to the tracker."""
        print(f"Adding event: {event_id}")
        self.events[event_id] = event_data

    def add_causal_link(self, effect_id: str, cause_id: str):
        """Creates a causal link between two events."""
        if effect_id not in self.events or cause_id not in self.events:
            print(f"Warning: Cannot link non-existent events: {cause_id} -> {effect_id}")
            return

        if effect_id not in self.causal_links:
            self.causal_links[effect_id] = []

        self.causal_links[effect_id].append(cause_id)
        print(f"Added causal link: {cause_id} -> {effect_id}")

    def get_causal_chain(self, event_id: str) -> Optional[List[str]]:
        """Retrieves the causal chain for a given event."""
        if event_id not in self.events:
            return None

        chain = [event_id]

        # Follow the causal links backwards
        current_id = event_id
        while current_id in self.causal_links:
            causes = self.causal_links[current_id]
            if not causes:
                break
            # For simplicity, we'll just follow the first cause in the list
            # A real implementation might handle multiple causes differently.
            cause_id = causes[0]
            chain.insert(0, cause_id)
            current_id = cause_id

        return chain
