import pytest
from core.colonies.base_colony import BaseColony, ConsensusResult, Tag, TagScope


def test_tag_creation():
    """Test Tag dataclass initialization and validation."""
    tag = Tag(key="test_key", value="test_value", scope=TagScope.GLOBAL, confidence=0.8)
    assert tag.key == "test_key"
    assert tag.value == "test_value"
    assert tag.scope == TagScope.GLOBAL
    assert tag.confidence == 0.8
    assert tag.metadata == {}

    with pytest.raises(ValueError, match="Tag confidence must be in"):
        Tag(key="test", value="invalid", confidence=1.1)

    with pytest.raises(ValueError, match="Tag key cannot be empty"):
        Tag(key="", value="invalid")


def test_consensus_result_creation():
    """Test ConsensusResult dataclass initialization and validation."""
    result = ConsensusResult(
        consensus_reached=True,
        decision="proceed",
        confidence=0.9,
        votes={"agent1": "yes"},
        participation_rate=0.8,
    )
    assert result.consensus_reached
    assert result.decision == "proceed"
    assert result.confidence == 0.9
    assert result.votes == {"agent1": "yes"}
    assert result.participation_rate == 0.8
    assert result.drift_score == 0.0
    assert result.affect_delta == 0.0

    with pytest.raises(ValueError, match="Confidence must be in"):
        ConsensusResult(
            consensus_reached=True,
            decision="proceed",
            confidence=1.1,
            votes={},
            participation_rate=1.0,
        )

    with pytest.raises(ValueError, match="Participation rate must be in"):
        ConsensusResult(
            consensus_reached=True,
            decision="proceed",
            confidence=1.0,
            votes={},
            participation_rate=-0.1,
        )


def test_base_colony_initialization():
    """Test BaseColony initialization."""
    colony = BaseColony(colony_id="test_colony", capabilities=["test_cap"])
    assert colony.colony_id == "test_colony"
    assert colony.capabilities == ["test_cap"]
    assert colony.agents == {}
    assert colony.drift_score == 0.0
    assert colony.affect_delta == 0.0
    assert colony.mesh_generation == 0
    assert colony.tags == []
    assert colony.state["active"] is False


def test_base_colony_register_agent():
    """Test agent registration in BaseColony."""
    colony = BaseColony(colony_id="test_colony")
    colony.register_agent("agent1", {"role": "tester"})
    assert "agent1" in colony.agents
    assert colony.agents["agent1"] == {"role": "tester"}


def test_base_colony_add_tag():
    """Test adding a tag to BaseColony."""
    colony = BaseColony(colony_id="test_colony")
    tag = Tag(key="test_tag", value="data")
    colony.add_tag(tag)
    assert len(colony.tags) == 1
    assert colony.tags[0] == tag


def test_base_colony_update_drift_score():
    """Test updating the drift score in BaseColony."""
    colony = BaseColony(colony_id="test_colony")
    colony.update_drift_score(0.1)
    assert colony.drift_score == 0.1
    colony.update_drift_score(-0.05)
    assert colony.drift_score == 0.05


def test_base_colony_update_affect_delta():
    """Test updating the affect delta in BaseColony."""
    colony = BaseColony(colony_id="test_colony")
    colony.update_affect_delta(0.2)
    assert colony.affect_delta == 0.2
    colony.update_affect_delta(-0.1)
    assert colony.affect_delta == 0.1


def test_base_colony_activation_deactivation():
    """Test colony activation and deactivation."""
    colony = BaseColony(colony_id="test_colony")
    assert not colony.state["active"]
    assert colony.mesh_generation == 0

    colony.activate()
    assert colony.state["active"]
    assert colony.mesh_generation == 1

    colony.deactivate()
    assert not colony.state["active"]


def test_base_colony_get_metrics():
    """Test retrieving metrics from BaseColony."""
    colony = BaseColony(colony_id="test_colony", capabilities=["testing"])
    colony.register_agent("agent1")
    colony.add_tag(Tag(key="metric_tag", value=True))
    colony.update_drift_score(0.3)
    colony.update_affect_delta(-0.15)
    colony.activate()

    metrics = colony.get_metrics()
    assert metrics["colony_id"] == "test_colony"
    assert metrics["capabilities"] == ["testing"]
    assert metrics["agent_count"] == 1
    assert metrics["tag_count"] == 1
    assert metrics["drift_score"] == 0.3
    assert metrics["affect_delta"] == -0.15
    assert metrics["mesh_generation"] == 1
    assert metrics["active"] is True
    assert metrics["processing_count"] == 0
