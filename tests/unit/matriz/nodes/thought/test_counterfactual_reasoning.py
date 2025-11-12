import pytest
from matriz.nodes.thought.counterfactual_reasoning import CounterfactualReasoningNode


def test_counterfactual_reasoning_basic():
    """Test basic counterfactual reasoning functionality."""
    node = CounterfactualReasoningNode()

    input_data = {
        "actual_scenario": {"outcome": "original_outcome"},
        "intervention": {"variable": "var_a", "value": 1, "description": "Set var_a to 1"},
        "causal_model": {"variables": {"var_a": 0}}
    }

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] > 0.5
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "HYPOTHESIS"
    scenarios = matriz_node["additional_data"]["counterfactual_scenarios"]
    assert len(scenarios) == 3

    most_likely = matriz_node["additional_data"]["most_likely"]
    assert most_likely["counterfactual_outcome"] == "original_outcome_modified"

def test_counterfactual_reasoning_missing_input():
    """Test that the node handles missing input gracefully."""
    node = CounterfactualReasoningNode()

    input_data = {}

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] == 0.1
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "DECISION"
    assert "error" in matriz_node["additional_data"]

def test_counterfactual_reasoning_performance(benchmark):
    """Test the performance of the counterfactual reasoning node."""
    node = CounterfactualReasoningNode()
    input_data = {
        "actual_scenario": {"outcome": "original_outcome"},
        "intervention": {"variable": "var_a", "value": 1, "description": "Set var_a to 1"},
        "causal_model": {"variables": {"var_a": 0}}
    }

    def f():
        node.process(input_data)

    benchmark.pedantic(f, iterations=1, rounds=5)
    assert benchmark.stats.stats.mean < 0.2
