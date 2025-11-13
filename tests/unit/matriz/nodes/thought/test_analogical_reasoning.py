import pytest
from matriz.nodes.thought.analogical_reasoning import AnalogicalReasoningNode


def test_analogical_reasoning_solar_system_atom():
    """Test classic solar system → atom analogy."""
    node = AnalogicalReasoningNode()

    input_data = {
        "source_domain": {
            "name": "solar_system",
            "concepts": [
                {"name": "sun", "relations": ["center", "massive", "attracts"]},
                {"name": "planets", "relations": ["orbit", "smaller", "attracted"]},
            ],
        },
        "target_domain": {
            "name": "atom",
            "concepts": [
                {"name": "nucleus", "relations": ["center", "massive", "attracts"]},
                {"name": "electrons", "relations": ["orbit", "smaller", "attracted"]},
            ],
        },
        "mapping_hints": ["sun -> nucleus", "planets -> electrons"],
    }

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] > 0.7
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "HYPOTHESIS"
    analogies = matriz_node["additional_data"]["analogies"]
    assert len(analogies) >= 2

    sun_mapping = next((a for a in analogies if a["source_concept"] == "sun"), None)
    assert sun_mapping is not None
    assert sun_mapping["target_concept"] == "nucleus"
    assert sun_mapping["mapping_type"] == "structural"

def test_analogical_reasoning_missing_input():
    """Test that the node handles missing input gracefully."""
    node = AnalogicalReasoningNode()

    input_data = {}

    result = node.process(input_data)

    assert "answer" in result
    assert result["confidence"] == 0.1
    assert "matriz_node" in result

    matriz_node = result["matriz_node"]
    assert matriz_node["type"] == "DECISION"
    assert "error" in matriz_node["additional_data"]

def test_analogical_reasoning_performance(benchmark):
    """Test the performance of the analogical reasoning node."""
    node = AnalogicalReasoningNode()
    input_data = {
        "source_domain": {
            "name": "solar_system",
            "concepts": [
                {"name": "sun", "relations": ["center", "massive", "attracts"]},
                {"name": "planets", "relations": ["orbit", "smaller", "attracted"]},
            ],
        },
        "target_domain": {
            "name": "atom",
            "concepts": [
                {"name": "nucleus", "relations": ["center", "massive", "attracts"]},
                {"name": "electrons", "relations": ["orbit", "smaller", "attracted"]},
            ],
        },
        "mapping_hints": ["sun -> nucleus", "planets -> electrons"],
    }

    def f():
        node.process(input_data)

    benchmark.pedantic(f, iterations=1, rounds=5)
    assert benchmark.stats.stats.mean < 0.2
