#!/usr/bin/env python3
"""
MATRIZ Cognitive Orchestrator
Routes queries through MATRIZ nodes with full traceability.

Refactored to emit fully schema-compliant MATRIZ nodes using the
standard node interface helpers (links, triggers, reflections, provenance).
"""

import time
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from matriz.core.node_interface import CognitiveNode
from matriz.core.orchestration import (
    ExecutionTrace,
    ExecutionTracer,
    IntentAnalyzer,
    NodeSelector,
)


class CognitiveOrchestrator:
    """
    Main orchestrator that routes queries through MATRIZ nodes.
    Every thought becomes a traceable, governed node.
    """

    def __init__(self):
        self.available_nodes = {}
        self.context_memory = []  # Recent MATRIZ nodes for context
        self.tracer = ExecutionTracer()
        self.intent_analyzer = IntentAnalyzer()
        self.node_selector = NodeSelector()

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
        intent_node = self.intent_analyzer.analyze(user_input)
        self.tracer.add_node_to_graph(intent_node)

        # 2. Node Selection - Create DECISION node
        selected_node_name = self.node_selector.select_node(intent_node)
        decision_node = self.node_selector.create_decision_node(
            f"Selected {selected_node_name} for processing",
            trigger_id=intent_node["id"],
        )
        self.tracer.add_node_to_graph(decision_node)

        # 3. Process through selected node
        if selected_node_name not in self.available_nodes:
            return {
                "error": f"No node available for {selected_node_name}",
                "trace": self.tracer.execution_trace,
            }

        node = self.available_nodes[selected_node_name]
        try:
            result = node.process({"query": user_input, "trigger_node_id": decision_node["id"]})
            if "matriz_node" in result:
                self.tracer.add_node_to_graph(result["matriz_node"])
        except Exception as e:
            return {
                "error": f"Node '{selected_node_name}' failed during processing",
                "error_details": e,
                "trace": self.tracer.execution_trace,
            }

        # 4. Validation
        if "validator" in self.available_nodes:
            validator = self.available_nodes["validator"]
            validation = validator.validate_output(result)

            # Create validation reflection node
            reflection_node = self._create_reflection_node(
                result_node=result["matriz_node"], validation=validation
            )
            self.tracer.add_node_to_graph(reflection_node)

        # 5. Build execution trace
        trace = ExecutionTrace(
            timestamp=datetime.now(timezone.utc),
            node_id=selected_node_name,
            input_data={"query": user_input},
            output_data=result,
            matriz_node=result.get("matriz_node", {}),
            processing_time=time.time() - start_time,
            validation_result=(validation if "validator" in self.available_nodes else True),
            reasoning_chain=self.tracer.build_reasoning_chain(),
        )
        self.tracer.add_trace(trace)

        return {
            "answer": result.get("answer", "No answer"),
            "confidence": result.get("confidence", 0.0),
            "matriz_nodes": list(self.tracer.matriz_graph.values()),
            "trace": asdict(trace),
            "reasoning_chain": trace.reasoning_chain,
        }

    def _create_reflection_node(self, result_node: dict, validation: bool) -> dict:
        """Create REFLECTION MATRIZ node (schema-compliant)."""
        reflection_type = "affirmation" if validation else "regret"

        class _ReflectionEmitter(CognitiveNode):  # type: ignore
            def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
                raise NotImplementedError

            def can_handle(self, intent: str) -> bool:
                raise NotImplementedError

            def validate_output(self, output: dict[str, Any]) -> bool:
                return True

        emitter = _ReflectionEmitter(
            node_name="matriz_orchestrator_reflection",
            capabilities=["validation_reflection"],
        )

        reflection = {
            "reflection_type": reflection_type,
            "timestamp": int(time.time() * 1000),
            "cause": "validation_check",
        }

        trigger = {
            "event_type": "validation_completed",
            "timestamp": int(time.time() * 1000),
            "trigger_node_id": result_node.get("id"),
            "effect": "validation_reflection",
        }

        node = emitter.create_matriz_node(
            node_type="REFLECTION",
            state={
                "confidence": 1.0 if validation else 0.3,
                "salience": 0.6 if validation else 0.4,
                "valence": 0.8 if validation else -0.5,
            },
            triggers=[trigger],
            reflections=[reflection],
            additional_data={
                "reflection_type": reflection_type,
                "validation_result": validation,
                "reflected_node_id": result_node.get("id"),
            },
        )
        return node

    def get_causal_chain(self, node_id: str) -> list[dict]:
        """Trace back the causal chain for any node"""
        return self.tracer.get_causal_chain(node_id)
