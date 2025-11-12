import pytest
from matriz.nodes.thought.abductive_reasoning import AbductiveReasoningNode

def test_abductive_reasoning_basic():
    """Test basic abductive reasoning functionality."""
    node = AbductiveReasoningNode()

    input_data = {
        "observations": ["obs_a", "obs_b"],
        "background_knowledge": {
            "patterns": [
                {
                    "requires": ["obs_a", "obs_b"],
                    "explanation": "Hypothesis A is the best explanation."
                }
            ]
        },
        "explanation_constraints": {}
    }

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] > 0.8
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "HYPOTHESIS"
    best_explanation = matriz_node["additional_data"]["best_explanation"]
    assert best_explanation["hypothesis"] == "Hypothesis A is the best explanation."

def test_abductive_reasoning_missing_input():
    """Test that the node handles missing input gracefully."""
    node = AbductiveReasoningNode()

    input_data = {}

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] == 0.1
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "DECISION"
    assert "error" in matriz_node["additional_data"]

def test_abductive_reasoning_performance(benchmark):
    """Test the performance of the abductive reasoning node."""
    node = AbductiveReasoningNode()
    input_data = {
        "observations": ["obs_a", "obs_b"],
        "background_knowledge": {
            "patterns": [
                {
                    "requires": ["obs_a", "obs_b"],
                    "explanation": "Hypothesis A is the best explanation."
                }
            ]
        },
        "explanation_constraints": {}
    }

    def f():
        node.process(input_data)

    benchmark.pedantic(f, iterations=1, rounds=5)
    assert benchmark.stats.stats.mean < 0.2
