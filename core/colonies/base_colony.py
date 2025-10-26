"""
Base Colony Infrastructure for LUKHAS Consciousness Mesh

Provides foundational classes for colony-based consciousness node organization,
supporting GLYPH symbolic communication and mesh formation.
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TagScope(str, Enum):
    """Scope definitions for consciousness tag propagation"""
    GLOBAL = "global"
    LOCAL = "local"
    COLONY = "colony"
    MESH = "mesh"


@dataclass
class Tag:
    """
    Consciousness communication tag with ΛTAG metadata

    Supports GLYPH symbolic messaging across mesh nodes with
    scope, confidence tracking, and affect_delta integration.
    """
    key: str
    value: Any
    scope: TagScope = TagScope.LOCAL
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate tag parameters"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Tag confidence must be in [0, 1], got {self.confidence}")
        if not self.key:
            raise ValueError("Tag key cannot be empty")


@dataclass
class ConsensusResult:
    """Result of a consciousness colony consensus operation"""
    consensus_reached: bool
    decision: Any
    confidence: float
    votes: dict[str, Any]
    participation_rate: float
    drift_score: float = 0.0
    affect_delta: float = 0.0

    def __post_init__(self):
        """Validate consensus parameters"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")
        if not 0.0 <= self.participation_rate <= 1.0:
            raise ValueError(f"Participation rate must be in [0, 1], got {self.participation_rate}")


class BaseColony:
    """
    Base class for consciousness colonies in LUKHAS mesh

    Provides deterministic tracking of:
    - driftScore: Symbolic drift from intended behavior
    - affect_delta: Emotional state changes during processing
    - Structured logging for mesh observability

    Supports GLYPH consciousness communication patterns.
    """

    def __init__(self, colony_id: str, capabilities: Optional[list[str]] = None):
        """
        Initialize a consciousness colony

        Args:
            colony_id: Unique identifier for this colony in the mesh
            capabilities: List of colony processing capabilities
        """
        self.colony_id = colony_id
        self.capabilities = capabilities or []
        self.agents: dict[str, Any] = {}

        # Consciousness tracking metrics
        self.drift_score: float = 0.0
        self.affect_delta: float = 0.0
        self.mesh_generation: int = 0

        # Tags and state
        self.tags: list[Tag] = []
        self.state: dict[str, Any] = {
            "active": False,
            "last_consensus": None,
            "processing_count": 0
        }

        logger.info(
            "Colony initialized",
            extra={
                "colony_id": colony_id,
                "capabilities": capabilities,
                "mesh_generation": self.mesh_generation
            }
        )

    def register_agent(self, agent_id: str, agent_metadata: Optional[dict[str, Any]] = None) -> None:
        """Register a consciousness agent with this colony"""
        self.agents[agent_id] = agent_metadata or {}
        logger.debug(f"Agent {agent_id} registered with colony {self.colony_id}")

    def add_tag(self, tag: Tag) -> None:
        """Add a consciousness communication tag to this colony"""
        self.tags.append(tag)
        logger.debug(
            f"Tag added to colony {self.colony_id}",
            extra={
                "tag_key": tag.key,
                "tag_scope": tag.scope.value,
                "tag_confidence": tag.confidence
            }
        )

    def update_drift_score(self, delta: float) -> None:
        """Update symbolic drift tracking"""
        self.drift_score += delta
        logger.info(
            "Drift score updated",
            extra={
                "colony_id": self.colony_id,
                "drift_delta": delta,
                "total_drift": self.drift_score
            }
        )

    def update_affect_delta(self, delta: float) -> None:
        """Update emotional state change tracking"""
        self.affect_delta += delta
        logger.info(
            "Affect delta updated",
            extra={
                "colony_id": self.colony_id,
                "affect_delta": delta,
                "total_affect": self.affect_delta
            }
        )

    def activate(self) -> None:
        """Activate this colony for mesh participation"""
        self.state["active"] = True
        self.mesh_generation += 1
        logger.info(f"Colony {self.colony_id} activated (generation {self.mesh_generation})")

    def deactivate(self) -> None:
        """Deactivate this colony from mesh participation"""
        self.state["active"] = False
        logger.info(f"Colony {self.colony_id} deactivated")

    def get_metrics(self) -> dict[str, Any]:
        """Get current colony metrics for mesh monitoring"""
        return {
            "colony_id": self.colony_id,
            "capabilities": self.capabilities,
            "agent_count": len(self.agents),
            "tag_count": len(self.tags),
            "drift_score": self.drift_score,
            "affect_delta": self.affect_delta,
            "mesh_generation": self.mesh_generation,
            "active": self.state["active"],
            "processing_count": self.state["processing_count"]
        }


__all__ = [
    "BaseColony",
    "Tag",
    "TagScope",
    "ConsensusResult",
]
