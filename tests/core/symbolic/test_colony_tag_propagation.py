"""Tests for SymbolicReasoningColony mesh integration logic."""

from __future__ import annotations

import math

import pytest

from core.colonies import MeshTopologyService
from core.symbolic_core import colony_tag_propagation


@pytest.fixture
def mesh_service(monkeypatch: pytest.MonkeyPatch) -> MeshTopologyService:
    """Provide an isolated mesh topology service for each test."""

    service = MeshTopologyService()
    monkeypatch.setattr(colony_tag_propagation, "get_mesh_topology_service", lambda: service)
    return service


@pytest.fixture
def symbolic_colony(mesh_service: MeshTopologyService) -> colony_tag_propagation.SymbolicReasoningColony:
    """Construct a symbolic reasoning colony bound to the isolated mesh service."""

    return colony_tag_propagation.SymbolicReasoningColony("colony-test", agent_count=3)


def test_colony_initialization_registers_mesh_agents(
    symbolic_colony: colony_tag_propagation.SymbolicReasoningColony,
    mesh_service: MeshTopologyService,
) -> None:
    """Ensure colony initialization registers symbolic agents with the mesh service."""

    assert len(symbolic_colony.agents) == 3

    metrics = mesh_service.get_mesh_metrics()
    assert metrics["total_agents"] == 3
    assert all(agent["node_type"] == "symbolic_reasoning" for agent in metrics["agents"].values())


def test_process_updates_drift_and_mesh_metrics(
    symbolic_colony: colony_tag_propagation.SymbolicReasoningColony,
    mesh_service: MeshTopologyService,
) -> None:
    """Processing a task should update drift and propagate metrics to the mesh service."""

    result = symbolic_colony.process({"complexity": 5})

    assert result["processed"] is True
    assert result["drift_score"] == pytest.approx(symbolic_colony.drift_score)
    assert symbolic_colony.drift_score == pytest.approx(0.05)

    metrics = mesh_service.get_mesh_metrics()
    # ΛTAG: driftScore - validate mesh drift aggregation mirrors colony updates
    assert metrics["total_drift"] == pytest.approx(0.05)
    assert metrics["total_affect"] == pytest.approx(0.01 * len(symbolic_colony.agents))


def test_reach_consensus_updates_affect(
    symbolic_colony: colony_tag_propagation.SymbolicReasoningColony,
    mesh_service: MeshTopologyService,
) -> None:
    """Reaching consensus should track affect_delta locally and across the mesh."""

    consensus = symbolic_colony.reach_consensus({"decision": "approve"})

    assert consensus.consensus_reached is True
    assert consensus.participation_rate == pytest.approx(1.0)
    assert symbolic_colony.affect_delta == pytest.approx(0.1)
    assert consensus.affect_delta == pytest.approx(symbolic_colony.affect_delta)

    metrics = mesh_service.get_mesh_metrics()
    # ΛTAG: affect_delta - ensure affect propagation remains drift-safe across mesh agents
    assert metrics["total_affect"] == pytest.approx(0.1)
    assert all(
        agent_metrics["affect_delta"] == pytest.approx(0.1 / len(symbolic_colony.agents))
        for agent_metrics in metrics["agents"].values()
    )


@pytest.mark.asyncio
async def test_propagate_belief_tracks_decay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Belief propagation with a single agent should exhibit exponential decay."""

    service = MeshTopologyService()
    monkeypatch.setattr(colony_tag_propagation, "get_mesh_topology_service", lambda: service)
    colony = colony_tag_propagation.SymbolicReasoningColony("colony-decay", agent_count=1)

    initial_strength = 0.8
    iterations = 3
    belief_state = await colony.propagate_belief(
        {
            "concept": "coherence",
            "value": 0.5,
            "strength": initial_strength,
            "iterations": iterations,
        }
    )

    (agent_id,) = tuple(belief_state.keys())
    expected_strength = initial_strength * math.pow(0.9, iterations)

    assert belief_state[agent_id] == pytest.approx(expected_strength)
    assert len(colony.propagation_history) == iterations
    # ΛTAG: belief_decay - track symbolic decay across recorded propagation history
    assert colony.propagation_history[-1]["belief_distribution"][agent_id] == pytest.approx(expected_strength)
