#!/usr/bin/env python3
"""
MATRIZ Cognitive Orchestrator
Routes queries through MATRIZ nodes with full traceability.

Refactored to emit fully schema-compliant MATRIZ nodes using the
standard node interface helpers (links, triggers, reflections, provenance).
"""

import time
from collections import deque, OrderedDict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from matriz.core.node_interface import CognitiveNode, NodeReflection, NodeState, NodeTrigger


# A reusable, lightweight node emitter to avoid creating classes on every call
class _NodeEmitter(CognitiveNode):
    def __init__(self, node_name: str, capabilities: list[str]):
        super().__init__(node_name, capabilities)

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("This is a helper class and does not process nodes.")

    def validate_output(self, output: dict[str, Any]) -> bool:
        return True


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


class CognitiveOrchestrator:
    """
    Main orchestrator that routes queries through MATRIZ nodes.
    Every thought becomes a traceable, governed node.
    """

    def __init__(self, max_history=1000):
        self.available_nodes = {}
        self.context_memory = deque(maxlen=max_history)  # Recent MATRIZ nodes for context
        self.execution_trace = deque(maxlen=max_history)  # Full execution history
        self.matriz_graph = OrderedDict()  # All MATRIZ nodes by ID

        # If max_history is set, ensure the graph doesn't grow indefinitely
        if max_history:
            self._max_history = max_history
        else:
            self._max_history = None

        # A single, reusable emitter for creating internal MATRIZ nodes
        self._node_emitter = _NodeEmitter(
            node_name="matriz_orchestrator_internal",
            capabilities=["intent_analysis", "node_selection", "validation_reflection"],
        )

    def register_node(self, name: str, node: "CognitiveNode"):
        """Register a cognitive node that emits MATRIZ format"""
        self.available_nodes[name] = node
        print(f"✓ Registered node: {name}")

    def process_query(self, user_input: str) -> dict[str, Any]:
        """
        Process user query through MATRIZ nodes
        Returns result with full trace
        """
        start_time = time.time()

        # 1. Intent Analysis - Create INTENT node
        intent_node = self._analyze_intent(user_input)
        self._add_to_graph(intent_node)

        # 2. Node Selection - Create DECISION node
        selected_node_name = self._select_node(intent_node)
        decision_node = self._create_decision_node(
            f"Selected {selected_node_name} for processing",
            trigger_id=intent_node["id"],
        )
        self._add_to_graph(decision_node)

        # 3. Process through selected node
        if selected_node_name not in self.available_nodes:
            return {
                "error": f"No node available for {selected_node_name}",
                "trace": self.execution_trace,
            }

        node = self.available_nodes[selected_node_name]
        try:
            result = node.process({"query": user_input, "trigger_node_id": decision_node["id"]})
            if "matriz_node" in result and "id" in result["matriz_node"]:
                self._add_to_graph(result["matriz_node"])
        except Exception as e:
            return {
                "error": f"Node '{selected_node_name}' failed during processing",
                "error_details": e,
                "trace": self.execution_trace,
            }

        # 4. Validation
        if "validator" in self.available_nodes:
            validator = self.available_nodes["validator"]
            validation = validator.validate_output(result)

            # Create validation reflection node
            reflection_node = self._create_reflection_node(
                result_node=result["matriz_node"], validation=validation
            )
            self._add_to_graph(reflection_node)

        # 5. Build execution trace
        trace = ExecutionTrace(
            timestamp=datetime.now(timezone.utc),
            node_id=selected_node_name,
            input_data={"query": user_input},
            output_data=result,
            matriz_node=result.get("matriz_node", {}),
            processing_time=time.time() - start_time,
            validation_result=(validation if "validator" in self.available_nodes else True),
        )
        self.execution_trace.append(trace)

        return {
            "answer": result.get("answer", "No answer"),
            "confidence": result.get("confidence", 0.0),
            "matriz_nodes": list(self.matriz_graph.values()),
            "trace": asdict(trace),
            "reasoning_chain": self._build_reasoning_chain(),
        }

    def _add_to_graph(self, node: dict):
        """Add a node to the graph and enforce history limit."""
        if 'id' in node:
            self.matriz_graph[node['id']] = node
            if self._max_history and len(self.matriz_graph) > self._max_history:
                self.matriz_graph.popitem(last=False)

    def _analyze_intent(self, user_input: str) -> dict:
        """Create INTENT MATRIZ node from user input (schema-compliant)."""
        # Simple intent detection
        if any(op in user_input for op in ["+", "-", "*", "/", "="]):
            detected_intent = "mathematical"
        elif "?" in user_input.lower():
            detected_intent = "question"
        elif "dog" in user_input.lower() or "see" in user_input.lower():
            detected_intent = "perception"
        else:
            detected_intent = "general"

        state = NodeState(confidence=0.9, salience=1.0)

        node = self._node_emitter.create_matriz_node(
            node_type="INTENT",
            state=state,
            additional_data={
                "input_text": user_input,
                "intent": detected_intent,
            },
        )
        return node

    def _select_node(self, intent_node: dict) -> str:
        """Select appropriate node based on intent"""
        intent = intent_node["state"].get("intent", "general")

        return {
            "mathematical": "math",
            "question": "facts",
            "perception": "vision",  # Would handle "boy sees dog"
        }.get(
            intent, "facts"
        )  # Default

    def _create_decision_node(self, decision: str, trigger_id: str) -> dict:
        """Create DECISION MATRIZ node (schema-compliant)."""

        trigger = NodeTrigger(
            event_type="node_selection",
            timestamp=int(time.time() * 1000),
            trigger_node_id=trigger_id,
            effect="selected_processing_node",
        )

        node = self._node_emitter.create_matriz_node(
            node_type="DECISION",
            state=NodeState(confidence=0.85, salience=0.9),
            triggers=[trigger],
            additional_data={"decision": decision},
        )
        return node

    def _create_reflection_node(self, result_node: dict, validation: bool) -> dict:
        """Create REFLECTION MATRIZ node (schema-compliant)."""
        reflection_type = "affirmation" if validation else "regret"

        reflection = NodeReflection(
            reflection_type=reflection_type,
            timestamp=int(time.time() * 1000),
            cause="validation_check",
        )

        trigger = NodeTrigger(
            event_type="validation_completed",
            timestamp=int(time.time() * 1000),
            trigger_node_id=result_node.get("id"),
            effect="validation_reflection",
        )

        node = self._node_emitter.create_matriz_node(
            node_type="REFLECTION",
            state=NodeState(
                confidence=1.0 if validation else 0.3,
                salience=0.6 if validation else 0.4,
                valence=0.8 if validation else -0.5,
            ),
            triggers=[trigger],
            reflections=[reflection],
            additional_data={
                "reflection_type": reflection_type,
                "validation_result": validation,
                "reflected_node_id": result_node.get("id"),
            },
        )
        return node

    def _build_reasoning_chain(self) -> list[str]:
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
