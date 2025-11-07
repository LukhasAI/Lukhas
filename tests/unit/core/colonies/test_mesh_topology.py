import time

import pytest

from core.colonies.mesh_topology import (
    MeshAgent,
    MeshTopologyService,
    get_mesh_topology_service,
)


def test_mesh_agent_creation():
    """Test MeshAgent dataclass initialization."""
    agent = MeshAgent(
        agent_id="test_agent",
        node_type="test_node",
        capabilities=["test_cap"],
    )
    assert agent.agent_id == "test_agent"
    assert agent.node_type == "test_node"
    assert agent.capabilities == ["test_cap"]
    assert agent.drift_score == 0.0
    assert agent.affect_delta == 0.0


def test_mesh_agent_update_metrics():
    """Test updating metrics for a MeshAgent."""
    agent = MeshAgent(agent_id="test_agent", node_type="test_node")
    initial_heartbeat = agent.last_heartbeat
    time.sleep(0.01) # Ensure time progresses
    agent.update_metrics(drift_delta=0.1, affect_delta=-0.05)
    assert agent.drift_score == 0.1
    assert agent.affect_delta == -0.05
    assert agent.last_heartbeat > initial_heartbeat


def test_mesh_topology_service_initialization():
    """Test MeshTopologyService initialization."""
    service = MeshTopologyService()
    assert len(service.agents) == 0
    assert service.topology_version == 0


def test_mesh_topology_service_register_agent():
    """Test agent registration in the MeshTopologyService."""
    service = MeshTopologyService()
    agent = service.register_agent("test_node", ["cap1"])
    assert agent.agent_id in service.agents
    assert service.get_agent(agent.agent_id) == agent
    assert service.topology_version == 1


def test_mesh_topology_service_get_agents():
    """Test retrieving agents by type and capability."""
    service = MeshTopologyService()
    service.register_agent("type1", ["capA", "capB"])
    service.register_agent("type1", ["capA"])
    service.register_agent("type2", ["capB"])

    assert len(service.get_agents_by_type("type1")) == 2
    assert len(service.get_agents_by_type("type2")) == 1
    assert len(service.get_agents_by_capability("capA")) == 2
    assert len(service.get_agents_by_capability("capB")) == 2


def test_mesh_topology_service_update_agent_metrics():
    """Test updating agent metrics through the service."""
    service = MeshTopologyService()
    agent = service.register_agent("test_node")

    result = service.update_agent_metrics(agent.agent_id, drift_delta=0.2, affect_delta=0.1)
    assert result is True
    assert service.get_agent(agent.agent_id).drift_score == 0.2
    assert service.get_agent(agent.agent_id).affect_delta == 0.1

    # Test with an unknown agent
    result_unknown = service.update_agent_metrics("unknown_agent", drift_delta=0.1)
    assert result_unknown is False


def test_mesh_topology_service_get_mesh_metrics():
    """Test retrieving mesh-wide metrics."""
    service = MeshTopologyService()
    service.register_agent("type1", ["capA"])
    service.register_agent("type2", ["capB"])

    metrics = service.get_mesh_metrics()
    assert metrics["total_agents"] == 2
    assert "agents" in metrics
    assert len(metrics["agents"]) == 2


def test_mesh_topology_service_synchronize():
    """Test mesh synchronization."""
    service = MeshTopologyService()
    agent = service.register_agent("test_node")

    initial_generation = agent.mesh_generation
    initial_version = service.topology_version

    sync_result = service.synchronize()
    assert sync_result["success"] is True
    assert service.get_agent(agent.agent_id).mesh_generation == initial_generation + 1
    assert service.topology_version == initial_version + 1


def test_get_mesh_topology_service_singleton():
    """Test that get_mesh_topology_service returns a singleton instance."""
    service1 = get_mesh_topology_service()
    service2 = get_mesh_topology_service()
    assert service1 is service2
