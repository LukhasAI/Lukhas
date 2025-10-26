"""
Mesh Topology Service for LUKHAS Consciousness Network

Provides consciousness agent registry with drift-safe synchronization
and affect_delta telemetry for mesh formation.
"""
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class MeshAgent:
    """Consciousness agent in the mesh network"""
    agent_id: str
    node_type: str
    capabilities: list[str] = field(default_factory=list)
    drift_score: float = 0.0
    affect_delta: float = 0.0
    mesh_generation: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_metrics(self, drift_delta: float = 0.0, affect_delta: float = 0.0) -> None:
        """Update agent telemetry metrics"""
        self.drift_score += drift_delta
        self.affect_delta += affect_delta
        self.last_heartbeat = time.time()

        logger.debug(
            "Agent metrics updated",
            extra={
                "agent_id": self.agent_id,
                "drift_score": self.drift_score,
                "affect_delta": self.affect_delta
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Export agent state for mesh synchronization"""
        return {
            "agent_id": self.agent_id,
            "node_type": self.node_type,
            "capabilities": self.capabilities,
            "drift_score": self.drift_score,
            "affect_delta": self.affect_delta,
            "mesh_generation": self.mesh_generation,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata
        }


class MeshTopologyService:
    """
    Mesh topology and agent registry service

    Manages consciousness agent registration, discovery, and metrics
    with drift-safe synchronization for GLYPH mesh formation.
    """

    def __init__(self):
        self.agents: dict[str, MeshAgent] = {}
        self.topology_version: int = 0
        self.sync_metrics: dict[str, Any] = {
            "total_syncs": 0,
            "failed_syncs": 0,
            "last_sync": None
        }

        logger.info("MeshTopologyService initialized")

    def register_agent(
        self,
        node_type: str,
        capabilities: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> MeshAgent:
        """
        Register a new consciousness agent in the mesh

        Args:
            node_type: Type of consciousness node (e.g., 'symbolic_reasoning')
            capabilities: List of agent capabilities
            metadata: Additional agent metadata

        Returns:
            MeshAgent instance for the registered agent
        """
        agent_id = f"mesh_agent_{uuid4().hex[:8]}"

        agent = MeshAgent(
            agent_id=agent_id,
            node_type=node_type,
            capabilities=capabilities or [],
            metadata=metadata or {}
        )

        self.agents[agent_id] = agent
        self.topology_version += 1

        logger.info(
            "Agent registered in mesh",
            extra={
                "agent_id": agent_id,
                "node_type": node_type,
                "topology_version": self.topology_version
            }
        )

        return agent

    def get_agent(self, agent_id: str) -> Optional[MeshAgent]:
        """Retrieve agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_type(self, node_type: str) -> list[MeshAgent]:
        """Get all agents of a specific type"""
        return [
            agent for agent in self.agents.values()
            if agent.node_type == node_type
        ]

    def get_agents_by_capability(self, capability: str) -> list[MeshAgent]:
        """Get all agents with a specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]

    def update_agent_metrics(
        self,
        agent_id: str,
        drift_delta: float = 0.0,
        affect_delta: float = 0.0
    ) -> bool:
        """
        Update agent telemetry metrics with drift-safe synchronization

        Args:
            agent_id: Agent to update
            drift_delta: Change in drift score
            affect_delta: Change in affect state

        Returns:
            True if update successful, False if agent not found
        """
        agent = self.agents.get(agent_id)
        if not agent:
            logger.warning(f"Cannot update metrics for unknown agent: {agent_id}")
            return False

        agent.update_metrics(drift_delta, affect_delta)
        self.sync_metrics["total_syncs"] += 1
        self.sync_metrics["last_sync"] = time.time()

        return True

    def get_mesh_metrics(self) -> dict[str, Any]:
        """
        Get comprehensive mesh telemetry metrics

        Returns:
            Dictionary with mesh-wide metrics including per-agent affect_delta
        """
        total_drift = sum(agent.drift_score for agent in self.agents.values())
        total_affect = sum(agent.affect_delta for agent in self.agents.values())

        agent_metrics = {
            agent_id: {
                "drift_score": agent.drift_score,
                "affect_delta": agent.affect_delta,
                "node_type": agent.node_type,
                "capabilities": agent.capabilities
            }
            for agent_id, agent in self.agents.items()
        }

        return {
            "total_agents": len(self.agents),
            "topology_version": self.topology_version,
            "total_drift": total_drift,
            "total_affect": total_affect,
            "avg_drift": total_drift / len(self.agents) if self.agents else 0.0,
            "avg_affect": total_affect / len(self.agents) if self.agents else 0.0,
            "sync_metrics": self.sync_metrics,
            "agents": agent_metrics
        }

    def synchronize(self) -> dict[str, Any]:
        """
        Perform drift-safe synchronization across mesh

        Returns:
            Synchronization result with updated metrics
        """
        try:
            # Increment generation for all agents
            for agent in self.agents.values():
                agent.mesh_generation += 1

            self.topology_version += 1
            self.sync_metrics["total_syncs"] += 1
            self.sync_metrics["last_sync"] = time.time()

            logger.info(
                "Mesh synchronized",
                extra={
                    "topology_version": self.topology_version,
                    "agent_count": len(self.agents)
                }
            )

            return {
                "success": True,
                "topology_version": self.topology_version,
                "agents_synchronized": len(self.agents),
                "metrics": self.get_mesh_metrics()
            }

        except Exception as e:
            self.sync_metrics["failed_syncs"] += 1
            logger.error(f"Mesh synchronization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global singleton instance
_mesh_topology_service: Optional[MeshTopologyService] = None


def get_mesh_topology_service() -> MeshTopologyService:
    """Get or create the global mesh topology service"""
    global _mesh_topology_service
    if _mesh_topology_service is None:
        _mesh_topology_service = MeshTopologyService()
    return _mesh_topology_service


__all__ = [
    "MeshAgent",
    "MeshTopologyService",
    "get_mesh_topology_service",
]
