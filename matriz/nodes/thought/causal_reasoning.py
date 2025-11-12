import time
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState


class CausalReasoningNode(CognitiveNode):
    """
    Performs causal reasoning to identify cause-effect relationships from a series of events.
    This node conforms to the modern MATRIZ CognitiveNode interface.
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="causal_reasoning",
            capabilities=["causal_inference", "correlation_analysis", "causal_graph_construction"],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Identifies and analyzes cause-effect relationships from a given set of events.

        Args:
            input_data: A dictionary containing:
                - 'events': A list of observed events.
                - 'temporal_order': The temporal relationships between events.
                - 'domain_knowledge': Background knowledge about the domain.

        Returns:
            A dictionary containing the answer, confidence, a MATRIZ node, and processing time.
        """
        start_time = time.time()

        events = input_data.get("events", [])
        temporal_order = input_data.get("temporal_order", {})
        domain_knowledge = input_data.get("domain_knowledge", {})
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        if not events:
            confidence = 0.1
            answer = "Causal reasoning requires a list of events to analyze."
            state = NodeState(confidence=confidence, salience=0.3)
            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={"error": "Missing events list."}
            )
        else:
            potential_links = self._identify_potential_causes(events, temporal_order)
            causal_links = self._filter_spurious_correlations(potential_links, domain_knowledge)
            causal_graph = self._build_causal_graph(causal_links)
            confidence = self._compute_model_confidence(causal_links, causal_graph)

            answer = f"Identified {len(causal_links)} potential causal links among the events."
            state = NodeState(confidence=confidence, salience=0.9, utility=0.8)
            matriz_node = self.create_matriz_node(
                node_type="CAUSAL",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "causal_links": causal_links,
                    "causal_graph": causal_graph,
                    "event_count": len(events),
                }
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validates the output of the causal reasoning node."""
        if not all(k in output for k in ["answer", "confidence", "matriz_node", "processing_time"]):
            return False
        if not (0 <= output["confidence"] <= 1):
            return False
        if not self.validate_matriz_node(output["matriz_node"]):
            return False
        return True

    def _identify_potential_causes(self, events: List[dict], temporal_order: dict) -> List[dict]:
        """Identifies potential causal relationships based on temporal precedence."""
        potential_links = []
        for i, event_a in enumerate(events):
            for j, event_b in enumerate(events):
                if i != j and self._precedes(event_a, event_b, temporal_order):
                    strength = self._compute_correlation(event_a, event_b)
                    if strength > 0.3:
                        potential_links.append({
                            "cause": event_a["name"],
                            "effect": event_b["name"],
                            "strength": strength,
                            "mechanism": "unknown",
                            "confidence": 0.5
                        })
        return potential_links

    def _precedes(self, event_a: dict, event_b: dict, temporal_order: dict) -> bool:
        """Checks if event_a temporally precedes event_b."""
        return event_a.get("timestamp", 0) < event_b.get("timestamp", 0)

    def _compute_correlation(self, event_a: dict, event_b: dict) -> float:
        """Computes the correlation strength between events."""
        return 0.7  # Placeholder for demo

    def _filter_spurious_correlations(self, potential_links: List[dict], domain_knowledge: dict) -> List[dict]:
        """Filters out spurious correlations using domain knowledge."""
        causal_links = []
        for link in potential_links:
            mechanism = self._find_mechanism(link["cause"], link["effect"], domain_knowledge)
            if mechanism:
                link["mechanism"] = mechanism
                link["confidence"] = 0.8
                causal_links.append(link)
            elif link["strength"] > 0.7:
                link["mechanism"] = "unknown (strong correlation)"
                link["confidence"] = 0.6
                causal_links.append(link)
        return causal_links

    def _find_mechanism(self, cause: str, effect: str, domain_knowledge: dict) -> str:
        """Finds a causal mechanism in the domain knowledge."""
        mechanisms = domain_knowledge.get("causal_mechanisms", {})
        key = f"{cause}->{effect}"
        if key in mechanisms:
            return mechanisms[key]
        for pattern, mechanism in mechanisms.items():
            if cause in pattern and effect in pattern:
                return mechanism
        return ""

    def _build_causal_graph(self, causal_links: List[dict]) -> dict:
        """Builds a directed graph of causal relationships."""
        nodes = set()
        edges = []
        for link in causal_links:
            nodes.add(link["cause"])
            nodes.add(link["effect"])
            edges.append({"from": link["cause"], "to": link["effect"], "weight": link["strength"]})
        return {"nodes": list(nodes), "edges": edges}

    def _compute_model_confidence(self, causal_links: List[dict], causal_graph: dict) -> float:
        """Computes the overall confidence in the causal model."""
        if not causal_links:
            return 0.0
        avg_confidence = sum(link["confidence"] for link in causal_links) / len(causal_links)
        complexity_penalty = min(0.2, len(causal_graph["edges"]) * 0.02)
        return max(0.0, avg_confidence - complexity_penalty)
