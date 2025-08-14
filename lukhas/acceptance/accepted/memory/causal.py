"""
LUKHAS AI Memory - Causal System
Preserves causal chains and relationships
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple


@dataclass
class CausalEvent:
    """Represents a causal event"""

    id: str
    cause: Any
    effect: Any
    confidence: float = 0.5
    timestamp: datetime = None


class CausalMemory:
    """Manages causal relationships in memory"""

    def __init__(self):
        self.causal_graph: Dict[str, List[str]] = {}
        self.events: Dict[str, CausalEvent] = {}
        self.inference_cache: Dict[Tuple, float] = {}

    def add_causal_link(self, cause_id: str, effect_id: str, confidence: float = 0.5):
        """Add a causal relationship"""
        if cause_id not in self.causal_graph:
            self.causal_graph[cause_id] = []

        self.causal_graph[cause_id].append(effect_id)

        # Store event
        event = CausalEvent(
            id=f"{cause_id}->{effect_id}",
            cause=cause_id,
            effect=effect_id,
            confidence=confidence,
            timestamp=datetime.now(),
        )
        self.events[event.id] = event

    def get_effects(self, cause_id: str) -> List[str]:
        """Get all effects of a cause"""
        return self.causal_graph.get(cause_id, [])

    def get_causes(self, effect_id: str) -> List[str]:
        """Get all causes of an effect"""
        causes = []
        for cause, effects in self.causal_graph.items():
            if effect_id in effects:
                causes.append(cause)
        return causes

    def infer_causality(self, event_a: str, event_b: str) -> float:
        """Infer causal relationship strength"""
        cache_key = (event_a, event_b)

        if cache_key in self.inference_cache:
            return self.inference_cache[cache_key]

        # Simple inference based on graph distance
        if event_b in self.get_effects(event_a):
            confidence = 0.8
        elif event_b in self.get_transitive_effects(event_a):
            confidence = 0.5
        else:
            confidence = 0.1

        self.inference_cache[cache_key] = confidence
        return confidence

    def get_transitive_effects(self, cause_id: str, max_depth: int = 3) -> List[str]:
        """Get transitive effects up to max_depth"""
        visited = set()
        effects = []

        def traverse(node, depth):
            if depth > max_depth or node in visited:
                return
            visited.add(node)

            for effect in self.causal_graph.get(node, []):
                effects.append(effect)
                traverse(effect, depth + 1)

        traverse(cause_id, 0)
        return effects


# Singleton instance
_causal_memory = None


def get_causal_memory() -> CausalMemory:
    """Get or create causal memory singleton"""
    global _causal_memory
    if _causal_memory is None:
        _causal_memory = CausalMemory()
    return _causal_memory
