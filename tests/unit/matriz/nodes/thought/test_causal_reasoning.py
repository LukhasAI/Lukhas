import pytest
from matriz.nodes.thought.causal_reasoning import CausalReasoningNode


def test_causal_reasoning_basic():
    """Test basic causal reasoning functionality."""
    node = CausalReasoningNode()

    input_data = {
        "events": [
            {"name": "event_a", "timestamp": 1},
            {"name": "event_b", "timestamp": 2},
        ],
        "temporal_order": {},
        "domain_knowledge": {
            "causal_mechanisms": {
                "event_a->event_b": "direct_causation"
            }
        }
    }

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] > 0.7
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "CAUSAL"
    causal_links = matriz_node["additional_data"]["causal_links"]
    assert len(causal_links) == 1

    link = causal_links[0]
    assert link["cause"] == "event_a"
    assert link["effect"] == "event_b"
    assert link["mechanism"] == "direct_causation"

def test_causal_reasoning_missing_input():
    """Test that the node handles missing input gracefully."""
    node = CausalReasoningNode()

    input_data = {}

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] == 0.1
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "DECISION"
    assert "error" in matriz_node["additional_data"]

def test_causal_reasoning_performance(benchmark):
    """Test the performance of the causal reasoning node."""
    node = CausalReasoningNode()
    input_data = {
        "events": [
            {"name": "event_a", "timestamp": 1},
            {"name": "event_b", "timestamp": 2},
        ],
        "temporal_order": {},
        "domain_knowledge": {
            "causal_mechanisms": {
                "event_a->event_b": "direct_causation"
            }
        }
    }

    def f():
        node.process(input_data)

    benchmark.pedantic(f, iterations=1, rounds=5)
    assert benchmark.stats.stats.mean < 0.2
