"""
Context-Based Memory Retrieval
==============================
This module provides a system for retrieving memories based on contextual similarity.
"""

from typing import Any, Dict, List

class ContextMatcher:
    """
    A simulated system for retrieving memories that match a given context.
    """

    def __init__(self):
        self.memory_contexts: Dict[str, Dict[str, Any]] = {}

    def store_memory_with_context(self, memory_id: str, context: Dict[str, Any]):
        """Stores a memory's context."""
        print(f"Storing context for memory {memory_id}")
        self.memory_contexts[memory_id] = context

    def match_context(self, query_context: Dict[str, Any], memory_context: Dict[str, Any]) -> float:
        """
        Simulates matching a given context with a stored memory context.
        Returns a similarity score between 0 and 1.
        """
        # A simple matching algorithm based on common keys and values.
        query_keys = set(query_context.keys())
        memory_keys = set(memory_context.keys())

        common_keys = query_keys.intersection(memory_keys)

        if not common_keys:
            return 0.0

        score = 0.0
        for key in common_keys:
            if query_context[key] == memory_context[key]:
                score += 1

        return score / len(common_keys)

    def retrieve_by_context(self, query_context: Dict[str, Any], min_score: float = 0.5) -> List[str]:
        """
        Retrieves memories that have a context score above a certain threshold.
        """
        print(f"Retrieving memories matching context with min_score={min_score}")

        results = []
        for memory_id, memory_context in self.memory_contexts.items():
            score = self.match_context(query_context, memory_context)
            if score >= min_score:
                results.append(memory_id)

        return results
