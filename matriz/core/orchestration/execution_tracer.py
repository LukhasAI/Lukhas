from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class ExecutionTrace:
    """Complete trace of cognitive processing"""

    timestamp: datetime
    node_id: str
    input_data: dict
    output_data: dict
    matriz_node: dict  # The actual MATRIZ node created
    processing_time: float
    validation_result: bool
    reasoning_chain: list[str]


class ExecutionTracer:
    def __init__(self):
        self.execution_trace = []
        self.matriz_graph = {}

    def add_trace(self, trace: ExecutionTrace):
        self.execution_trace.append(trace)

    def add_node_to_graph(self, node: dict):
        if "id" in node:
            self.matriz_graph[node["id"]] = node

    def get_causal_chain(self, node_id: str) -> list[dict]:
        """Trace back the causal chain for any node"""
        if node_id not in self.matriz_graph:
            return []

        chain = []
        visited = set()
        to_visit = [node_id]

        while to_visit:
            current_id = to_visit.pop(0)
            if current_id in visited:
                continue

            visited.add(current_id)
            node = self.matriz_graph.get(current_id)
            if node:
                chain.append(node)
                # Follow triggers backward (schema-compliant triggers list)
                for trig in node.get("triggers", []) or []:
                    trigger_id = trig.get("trigger_node_id") if isinstance(trig, dict) else None
                    if trigger_id and trigger_id not in visited:
                        to_visit.append(trigger_id)

        return chain

    def build_reasoning_chain(self) -> list[str]:
        """Build human-readable reasoning chain from MATRIZ nodes"""
        chain = []
        for node in self.matriz_graph.values():
            if node["type"] == "INTENT":
                chain.append(f"Understood intent: {node['state'].get('intent', 'unknown')}")
            elif node["type"] == "DECISION":
                chain.append(f"Decision: {node['state'].get('decision', 'unknown')}")
            elif node["type"] == "REFLECTION":
                chain.append(f"Reflection: {node['state'].get('reflection_type', 'unknown')}")
        return chain
