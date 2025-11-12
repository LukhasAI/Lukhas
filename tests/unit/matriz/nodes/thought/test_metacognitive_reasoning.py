import pytest
from matriz.nodes.thought.metacognitive_reasoning import MetacognitiveReasoningNode


def test_metacognitive_reasoning_basic():
    """Test basic metacognitive reasoning functionality."""
    node = MetacognitiveReasoningNode()

    input_data = {
        "reasoning_trace": [
            {"type": "evidence", "weight": 0.9, "output": "evidence_a"},
            {"type": "deduction", "input": "evidence_a", "output": "conclusion_b"},
            {"type": "alternative", "input": "evidence_a", "output": "conclusion_c"},
        ],
        "conclusions": ["conclusion_b", "conclusion_c"],
        "evidence": ["confirming_evidence_1", "confirming_evidence_2", "confirming_evidence_3", "disconfirming_evidence_1"],
    }

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] > 0.5
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "AWARENESS"
    assessment = matriz_node["additional_data"]["assessment"]
    assert "confirmation_bias" not in assessment["biases_detected"]
    assert "anchoring_bias" in assessment["biases_detected"]

def test_metacognitive_reasoning_missing_input():
    """Test that the node handles missing input gracefully."""
    node = MetacognitiveReasoningNode()

    input_data = {}

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] == 0.1
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "DECISION"
    assert "error" in matriz_node["additional_data"]

def test_metacognitive_reasoning_performance(benchmark):
    """Test the performance of the metacognitive reasoning node."""
    node = MetacognitiveReasoningNode()
    input_data = {
        "reasoning_trace": [
            {"type": "evidence", "weight": 0.9, "output": "evidence_a"},
            {"type": "deduction", "input": "evidence_a", "output": "conclusion_b"},
            {"type": "alternative", "input": "evidence_a", "output": "conclusion_c"},
        ],
        "conclusions": ["conclusion_b", "conclusion_c"],
        "evidence": ["confirming_evidence_1", "confirming_evidence_2", "confirming_evidence_3", "disconfirming_evidence_1"],
    }

    def f():
        node.process(input_data)

    benchmark.pedantic(f, iterations=1, rounds=5)
    assert benchmark.stats.stats.mean < 0.2
