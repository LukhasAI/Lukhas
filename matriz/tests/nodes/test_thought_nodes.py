import pytest
from matriz.nodes.thought.analogical_reasoning import AnalogicalReasoningNode
from matriz.nodes.thought.causal_reasoning import CausalReasoningNode
from matriz.nodes.thought.counterfactual_reasoning import CounterfactualReasoningNode
from matriz.nodes.thought.abductive_reasoning import AbductiveReasoningNode
from matriz.nodes.thought.metacognitive_reasoning import MetacognitiveReasoningNode

@pytest.fixture
def analogical_reasoning_node():
    return AnalogicalReasoningNode()

@pytest.fixture
def causal_reasoning_node():
    return CausalReasoningNode()

@pytest.fixture
def counterfactual_reasoning_node():
    return CounterfactualReasoningNode()

@pytest.fixture
def abductive_reasoning_node():
    return AbductiveReasoningNode()

@pytest.fixture
def metacognitive_reasoning_node():
    return MetacognitiveReasoningNode()

def test_analogical_reasoning_node(analogical_reasoning_node):
    node_input = {"source_domain": "solar_system", "target_domain": "atom"}
    result = analogical_reasoning_node.process(node_input)
    assert result["success"]
    assert "analogy_mappings" in result["data"]
    assert len(result["data"]["analogy_mappings"]) == 2
    assert result["data"]["analogy_mappings"][0]["source_concept"] == "central_solar_system"
    assert result["data"]["analogy_mappings"][0]["target_concept"] == "central_atom"

def test_causal_reasoning_node(causal_reasoning_node):
    node_input = {"events": ["lightning", "thunder"]}
    result = causal_reasoning_node.process(node_input)
    assert result["success"]
    assert "causal_links" in result["data"]
    assert len(result["data"]["causal_links"]) == 1
    assert result["data"]["causal_links"][0]["cause"] == "lightning"
    assert result["data"]["causal_links"][0]["effect"] == "thunder"

def test_counterfactual_reasoning_node(counterfactual_reasoning_node):
    node_input = {"event": "the ship sank"}
    result = counterfactual_reasoning_node.process(node_input)
    assert result["success"]
    assert "scenarios" in result["data"]
    assert len(result["data"]["scenarios"]) == 1
    assert "'the ship sank'" in result["data"]["scenarios"][0]["alternative_event"]

def test_abductive_reasoning_node(abductive_reasoning_node):
    node_input = {"observations": ["wet grass", "dark clouds"]}
    result = abductive_reasoning_node.process(node_input)
    assert result["success"]
    assert "explanations" in result["data"]
    assert len(result["data"]["explanations"]) == 1
    assert "wet grass" in result["data"]["explanations"][0]["hypothesis"]
    assert "dark clouds" in result["data"]["explanations"][0]["hypothesis"]

def test_metacognitive_reasoning_node(metacognitive_reasoning_node):
    node_input = {"cognitive_trace": ["node1", "node2", "node3"]}
    result = metacognitive_reasoning_node.process(node_input)
    assert result["success"]
    assert "assessment" in result["data"]
    assert result["data"]["assessment"]["confidence"] == 0.85
