import pytest
from core.symbolic_legacy.colony_tag_propagation import SymbolicReasoningColony


@pytest.fixture()
def colony() -> SymbolicReasoningColony:
    return SymbolicReasoningColony("colony-mesh")


def test_consciousness_mesh_initialized(colony: SymbolicReasoningColony) -> None:
    agent_ids = set(colony.agents.keys())
    assert agent_ids, "expected deterministic mesh agents to be registered"
    assert set(colony.mesh_graph.nodes()) == agent_ids
    # fully connected mesh should have at least n-1 edges
    assert colony.mesh_graph.number_of_edges() >= len(agent_ids) - 1


def test_process_updates_metrics_and_vocab(colony: SymbolicReasoningColony) -> None:
    payload = {"concept": "ethical-alignment", "intensity": 0.82, "affect_delta": 0.12}
    result = colony.process(payload)

    assert result["concept"] == "ethical-alignment"
    assert 0.0 <= result["aggregate_confidence"] <= 1.0
    assert 0.0 <= result["coherence_score"] <= 1.0
    assert 0.0 <= result["mesh_connectivity"] <= 1.0
    assert set(result["agents"].keys()) == set(colony.agents.keys())
    assert result["tag_payload"]["confidence"] == pytest.approx(result["aggregate_confidence"])

    for metrics in result["agents"].values():
        assert 0.0 <= metrics["confidence"] <= 1.0
        assert -1.0 <= metrics["affect_delta"] <= 1.0
        assert 0.0 <= metrics["drift_score"] <= 1.0

    vocabulary = getattr(colony.vocabulary, "vocabulary", {})
    assert "ethical-alignment" in vocabulary
    assert vocabulary["ethical-alignment"]["last_colony"] == colony.colony_id
    assert colony.belief_network.has_node("ethical-alignment")


def test_reach_consensus_aggregates_votes(colony: SymbolicReasoningColony) -> None:
    consensus = colony.reach_consensus({"concept": "ethical-alignment", "intensity": 0.7})

    assert hasattr(consensus, "consensus_reached")
    assert hasattr(consensus, "votes")
    assert set(consensus.votes.keys()) == set(colony.agents.keys())
    assert 0.0 <= consensus.confidence <= 1.0
    assert consensus.participation_rate == pytest.approx(1.0)
