#!/usr/bin/env python3
"""
MATRIZ Causal Reasoning Node

Identifies and analyzes cause-effect relationships between events.
Uses causal inference to distinguish correlation from causation.

Example: "Rain causes wet ground" (temporal precedence + mechanism)
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class CausalLink:
    """A causal relationship between two events."""
    cause: str
    effect: str
    strength: float  # 0.0 - 1.0
    mechanism: str  # How cause produces effect
    confidence: float  # Confidence in this link


class CausalReasoningNode(CognitiveNode):
    """
    Performs causal reasoning: identifying cause-effect relationships.

    Capabilities:
    - Temporal precedence detection
    - Correlation strength computation
    - Spurious correlation filtering
    - Causal graph construction
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_causal_reasoning",
            capabilities=[
                "causal_inference",
                "correlation_detection",
                "mechanism_discovery",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform causal reasoning.

        Args:
            input_data: Dict containing:
                - events: List of observed events
                - temporal_order: Temporal relationships between events
                - domain_knowledge: Background knowledge about domain

        Returns:
            Dict with causal links, graph, confidence, and MATRIZ node
        """
        start_time = time.time()

        events = input_data.get("events", [])
        temporal_order = input_data.get("temporal_order", {})
        domain_knowledge = input_data.get("domain_knowledge", {})

        # Identify potential causal links
        potential_links = self._identify_potential_causes(events, temporal_order)

        # Filter out spurious correlations
        causal_links = self._filter_spurious_correlations(
            potential_links,
            domain_knowledge
        )

        # Build causal graph
        causal_graph = self._build_causal_graph(causal_links)

        # Compute confidence
        confidence = self._compute_model_confidence(causal_links, causal_graph)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.5 + 0.1 * len(causal_links)),
            novelty=max(0.1, 1.0 - confidence),
            utility=min(1.0, 0.6 + confidence / 2)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="causal_reasoning_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "CAUSAL",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "event_count": len(events),
                "link_count": len(causal_links)
            },
            "causal_links": [
                {
                    "cause": link.cause,
                    "effect": link.effect,
                    "strength": link.strength,
                    "mechanism": link.mechanism,
                    "confidence": link.confidence
                }
                for link in causal_links
            ],
            "causal_graph": causal_graph
        }

        return {
            "answer": {
                "causal_links": matriz_node["causal_links"],
                "causal_graph": causal_graph,
                "link_count": len(causal_links)
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        return "causal_links" in output["answer"]

    def _identify_potential_causes(
        self,
        events: List[dict],
        temporal_order: dict
    ) -> List[CausalLink]:
        """Identify potential causal relationships based on temporal precedence."""
        potential_links = []

        for i, event_a in enumerate(events):
            for j, event_b in enumerate(events):
                if i == j:
                    continue

                # Check temporal precedence (cause must precede effect)
                if self._precedes(event_a, event_b, temporal_order):
                    # Compute correlation strength
                    strength = self._compute_correlation(event_a, event_b)

                    if strength > 0.3:  # Threshold for consideration
                        potential_links.append(
                            CausalLink(
                                cause=event_a.get("name", f"event_{i}"),
                                effect=event_b.get("name", f"event_{j}"),
                                strength=strength,
                                mechanism="unknown",
                                confidence=0.5  # Low initial confidence
                            )
                        )

        return potential_links

    def _precedes(self, event_a: dict, event_b: dict, temporal_order: dict) -> bool:
        """Check if event_a temporally precedes event_b."""
        ts_a = event_a.get("timestamp", 0)
        ts_b = event_b.get("timestamp", 0)
        return ts_a < ts_b

    def _compute_correlation(self, event_a: dict, event_b: dict) -> float:
        """Compute correlation strength between events."""
        # Simplified: based on temporal proximity and co-occurrence
        ts_a = event_a.get("timestamp", 0)
        ts_b = event_b.get("timestamp", 0)

        # Closer in time = higher correlation
        time_diff = abs(ts_b - ts_a)
        max_diff = 1000  # milliseconds

        temporal_score = max(0.0, 1.0 - time_diff / max_diff)

        # Default correlation with temporal component
        return min(1.0, 0.5 + temporal_score * 0.5)

    def _filter_spurious_correlations(
        self,
        potential_links: List[CausalLink],
        domain_knowledge: dict
    ) -> List[CausalLink]:
        """Filter out spurious correlations using domain knowledge."""
        causal_links = []

        for link in potential_links:
            # Check if mechanism exists in domain knowledge
            mechanism = self._find_mechanism(link.cause, link.effect, domain_knowledge)

            if mechanism:
                link.mechanism = mechanism
                link.confidence = 0.8  # Higher confidence with known mechanism
                causal_links.append(link)
            elif link.strength > 0.7:
                # Strong correlation without known mechanism
                link.mechanism = "unknown (strong correlation)"
                link.confidence = 0.6
                causal_links.append(link)

        return causal_links

    def _find_mechanism(self, cause: str, effect: str, domain_knowledge: dict) -> str:
        """Find causal mechanism in domain knowledge."""
        mechanisms = domain_knowledge.get("causal_mechanisms", {})

        # Look for direct mechanism
        key = f"{cause}->{effect}"
        if key in mechanisms:
            return mechanisms[key]

        # Look for general pattern
        for pattern, mechanism in mechanisms.items():
            if cause in pattern and effect in pattern:
                return mechanism

        return ""

    def _build_causal_graph(self, causal_links: List[CausalLink]) -> dict:
        """Build directed graph of causal relationships."""
        nodes = set()
        edges = []

        for link in causal_links:
            nodes.add(link.cause)
            nodes.add(link.effect)
            edges.append({
                "from": link.cause,
                "to": link.effect,
                "weight": link.strength
            })

        return {
            "nodes": list(nodes),
            "edges": edges
        }

    def _compute_model_confidence(
        self,
        causal_links: List[CausalLink],
        causal_graph: dict
    ) -> float:
        """Compute overall confidence in causal model."""
        if not causal_links:
            return 0.0

        # Average confidence across links
        avg_confidence = sum(link.confidence for link in causal_links) / len(causal_links)

        # Penalty for complex graphs (more uncertainty)
        complexity_penalty = min(0.2, len(causal_graph["edges"]) * 0.02)

        return max(0.0, avg_confidence - complexity_penalty)
