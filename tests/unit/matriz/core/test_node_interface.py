#!/usr/bin/env python3
"""
Tests for the MATRIZ Cognitive Node Interface
"""

import time
from typing import Any, Dict

import numpy as np
import pytest
from matriz.core.node_interface import (
    CognitiveNode,
    NodeLink,
    NodeReflection,
    NodeState,
    NodeTrigger,
)


# A concrete implementation of the abstract CognitiveNode for testing purposes
class TestNode(CognitiveNode):
    __test__ = False
    """A simple concrete implementation of a CognitiveNode for testing."""
    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="test_node",
            capabilities=["testing"],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """A simple process implementation for testing."""
        start_time = time.time()
        state = NodeState(confidence=0.9, salience=0.8)
        matriz_node = self.create_matriz_node(
            node_type="DECISION",
            state=state,
            additional_data={"result": "success"}
        )
        return {
            "answer": "Test successful",
            "confidence": 0.9,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time,
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """A simple validation for testing."""
        return "answer" in output and self.validate_matriz_node(output.get("matriz_node", {}))

class TestNodeInterface:
    """Test suite for the CognitiveNode interface and its components."""

    @pytest.fixture
    def node(self):
        """Provides a TestNode instance for tests."""
        return TestNode(tenant="test-tenant")

    def test_node_creation(self, node):
        """Tests the creation of a concrete TestNode."""
        assert node.node_name == "test_node"
        assert node.capabilities == ["testing"]
        assert node.tenant == "test-tenant"

    def test_create_matriz_node_valid(self, node):
        """Tests the creation of a valid MATRIZ node."""
        state = NodeState(confidence=0.9, salience=0.8, valence=-0.5, arousal=0.4, novelty=0.3, urgency=0.2, shock_factor=0.1, risk=0.6, utility=0.7)
        node_data = node.create_matriz_node(
            node_type="DECISION",
            state=state,
            additional_data={"test": "data"}
        )
        assert node_data["type"] == "DECISION"
        assert node_data["state"]["confidence"] == 0.9
        assert node_data["additional_data"]["test"] == "data"
        assert node_data["provenance"]["tenant"] == "test-tenant"
        assert len(node.get_trace()) == 1

    def test_create_matriz_node_invalid_type(self, node):
        """Tests creating a MATRIZ node with an invalid type."""
        with pytest.raises(ValueError):
            node.create_matriz_node(node_type="INVALID_TYPE", state={"confidence": 0.5, "salience": 0.5})

    def test_create_matriz_node_missing_state_fields(self, node):
        """Tests creating a MATRIZ node with missing required state fields."""
        with pytest.raises(ValueError):
            node.create_matriz_node(node_type="DECISION", state={"confidence": 0.5})

    def test_validate_matriz_node(self, node):
        """Tests the validation of MATRIZ nodes."""
        valid_node = node.create_matriz_node("DECISION", {"confidence": 0.5, "salience": 0.5})
        assert node.validate_matriz_node(valid_node) is True

        invalid_node = {"id": "123"} # Missing fields
        assert node.validate_matriz_node(invalid_node) is False

        # Test missing state fields
        invalid_state_node = node.create_matriz_node("DECISION", {"confidence": 0.5, "salience": 0.5})
        del invalid_state_node["state"]["confidence"]
        assert node.validate_matriz_node(invalid_state_node) is False

        # Test invalid confidence range
        invalid_confidence_node = node.create_matriz_node("DECISION", {"confidence": 2.0, "salience": 0.5})
        assert node.validate_matriz_node(invalid_confidence_node) is False

    def test_create_reflection(self, node):
        """Tests creating a reflection."""
        reflection = node.create_reflection("affirmation", "test cause")
        assert reflection.reflection_type == "affirmation"
        assert reflection.cause == "test cause"

    def test_create_invalid_reflection(self, node):
        """Tests creating a reflection with an invalid type."""
        with pytest.raises(ValueError):
            node.create_reflection("INVALID_TYPE", "test cause")

    def test_create_link(self, node):
        """Tests creating a link."""
        link = node.create_link("123", "causal")
        assert link.target_node_id == "123"
        assert link.link_type == "causal"

    def test_create_invalid_link(self, node):
        """Tests creating a link with an invalid type."""
        with pytest.raises(ValueError):
            node.create_link("123", "INVALID_TYPE")

    def test_get_deterministic_hash(self, node):
        """Tests the deterministic hash generation."""
        input_data = {"a": 1, "b": 2}
        hash1 = node.get_deterministic_hash(input_data)
        hash2 = node.get_deterministic_hash(input_data)
        assert hash1 == hash2

    def test_get_trace(self, node):
        """Tests the processing trace."""
        assert len(node.get_trace()) == 0
        node.process({"query": "test"})
        assert len(node.get_trace()) == 1

    def test_repr(self, node):
        """Tests the __repr__ method."""
        expected_repr = "TestNode(name='test_node', capabilities=['testing'])"
        assert repr(node) == expected_repr

    def test_validate_matriz_node_exception(self, node):
        """Tests the exception handling in validate_matriz_node."""
        assert node.validate_matriz_node("not a dict") is False

    def test_create_link_invalid_direction(self, node):
        """Tests creating a link with an invalid direction."""
        with pytest.raises(ValueError):
            node.create_link("123", "causal", direction="INVALID")

    def test_abstract_process_method(self):
        """Tests that the abstract process method raises TypeError if not implemented."""
        with pytest.raises(TypeError):
            class IncompleteNode(CognitiveNode):
                def __init__(self):
                    super().__init__("incomplete", [])
                def validate_output(self, output):
                    return True
            IncompleteNode()

    def test_abstract_validate_output_method(self):
        """Tests that the abstract validate_output method raises TypeError if not implemented."""
        with pytest.raises(TypeError):
            class IncompleteNode(CognitiveNode):
                def __init__(self):
                    super().__init__("incomplete", [])
                def process(self, input_data):
                    return {}
            IncompleteNode()

# Mock M-A-T-R-I-A Pipeline Nodes
class PipelineNode(TestNode):
    __test__ = False
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """A simple process implementation for testing."""
        start_time = time.time()
        state = NodeState(confidence=0.9, salience=0.8)

        # Get existing trace or start a new one
        trace = input_data.get("matriz_node", {}).get("additional_data", {}).get("trace", [])
        trace.append(self.node_name)

        matriz_node = self.create_matriz_node(
            node_type="DECISION",
            state=state,
            additional_data={"result": "success", "trace": trace}
        )
        return {
            "answer": "Test successful",
            "confidence": 0.9,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time,
        }

class MemoryNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "memory"
        self.capabilities = ["storage", "retrieval"]

class AttentionNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "attention"
        self.capabilities = ["filtering", "focus"]

class ThoughtNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "thought"
        self.capabilities = ["reasoning", "planning"]

class RiskNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "risk"
        self.capabilities = ["assessment", "mitigation"]

class IntentNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "intent"
        self.capabilities = ["goal_setting"]

class ActionNode(PipelineNode):
    __test__ = False
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_name = "action"
        self.capabilities = ["execution"]

class TestMatriaPipeline:
    """Tests the mock M-A-T-R-I-A pipeline."""

    def test_pipeline_flow(self):
        """Tests the flow of data through the pipeline."""
        # 1. Initialize nodes
        memory = MemoryNode()
        attention = AttentionNode()
        thought = ThoughtNode()
        risk = RiskNode()
        intent = IntentNode()
        action = ActionNode()

        # 2. Simulate processing
        input_data = {"query": "test"}
        memory_out = memory.process(input_data)
        attention_out = attention.process(memory_out)
        thought_out = thought.process(attention_out)
        risk_out = risk.process(thought_out)
        intent_out = intent.process(risk_out)
        action_out = action.process(intent_out)

        # 3. Assertions
        assert action_out["confidence"] == 0.9
        assert "matriz_node" in action_out
        trace = action_out["matriz_node"]["additional_data"]["trace"]
        expected_trace = ["memory", "attention", "thought", "risk", "intent", "action"]
        assert trace == expected_trace

class TestPerformance:
    """Performance tests for the CognitiveNode."""

    def test_process_latency(self, benchmark):
        """Tests the p95 latency of the process method."""
        node = TestNode()
        benchmark.pedantic(node.process, args=({"query": "perf_test"},), iterations=10, rounds=5)
        p95 = np.percentile(benchmark.stats.stats.data, 95)
        assert p95 < 0.250 # 250ms

class TestDataStructures:
    """Tests for the data structures used by the CognitiveNode."""

    def test_node_state(self):
        """Tests the NodeState dataclass."""
        state = NodeState(confidence=0.8, salience=0.7, valence=-0.5)
        assert state.confidence == 0.8
        assert state.salience == 0.7
        assert state.valence == -0.5
        assert state.arousal is None

    def test_node_link(self):
        """Tests the NodeLink dataclass."""
        link = NodeLink(target_node_id="123", link_type="causal", direction="unidirectional", weight=0.9, explanation="test")
        assert link.target_node_id == "123"
        assert link.link_type == "causal"
        assert link.direction == "unidirectional"
        assert link.weight == 0.9
        assert link.explanation == "test"

    def test_node_trigger(self):
        """Tests the NodeTrigger dataclass."""
        ts = int(time.time() * 1000)
        trigger = NodeTrigger(event_type="test_event", timestamp=ts, trigger_node_id="456", effect="test_effect")
        assert trigger.event_type == "test_event"
        assert trigger.timestamp == ts
        assert trigger.trigger_node_id == "456"
        assert trigger.effect == "test_effect"

    def test_node_reflection(self):
        """Tests the NodeReflection dataclass."""
        ts = int(time.time() * 1000)
        reflection = NodeReflection(reflection_type="affirmation", timestamp=ts, cause="test_cause", old_state={"a":1}, new_state={"b":2})
        assert reflection.reflection_type == "affirmation"
        assert reflection.timestamp == ts
        assert reflection.cause == "test_cause"
        assert reflection.old_state == {"a":1}
        assert reflection.new_state == {"b":2}
