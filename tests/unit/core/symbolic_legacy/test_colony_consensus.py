from unittest.mock import patch

import pytest
from core.symbolic_legacy.colony_tag_propagation import SymbolicReasoningColony


class TestConsciousnessConsensus:
    """Test consciousness consensus implementation."""

    def test_consensus_with_agents(self):
        """Test consensus reaches decision with registered agents."""
        colony = SymbolicReasoningColony("test_colony")

        # Register additional agents (3 already exist from __init__)
        for i in range(3, 6):
            colony.register_agent(f"agent_{i}", {"consciousness_type": "test"})

        # Reach consensus
        result = colony.reach_consensus({"action": "test_decision"})

        assert isinstance(result.consensus_reached, bool)
        assert len(result.votes) == 6  # 3 initial + 3 new
        assert 0.0 <= result.confidence <= 1.0
        assert 0.0 <= result.participation_rate <= 1.0

    def test_consensus_without_agents(self):
        """Test consensus fails gracefully without agents."""
        colony = SymbolicReasoningColony("empty_colony")
        colony.agents = {}  # Clear initial agents

        result = colony.reach_consensus({"action": "test"})

        assert result.consensus_reached is False
        assert result.decision is None
        assert result.confidence == 0.0
        assert result.participation_rate == 0.0

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_mesh_generation_increments_on_success(self, mock_agent_vote):
        """Test mesh generation increments only on successful consensus."""
        mock_agent_vote.return_value = {"decision": "approved", "strength": 0.9}

        colony = SymbolicReasoningColony("test_colony")
        initial_gen = colony.mesh_generation

        result = colony.reach_consensus({"action": "increment_test"})

        assert result.consensus_reached is True
        assert colony.mesh_generation == initial_gen + 1

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_mesh_generation_does_not_increment_on_failure(self, mock_agent_vote):
        """Test mesh generation does not increment on failed consensus."""
        mock_agent_vote.return_value = {"decision": "rejected", "strength": 0.9}

        colony = SymbolicReasoningColony("test_colony")
        initial_gen = colony.mesh_generation

        result = colony.reach_consensus({"action": "no_increment_test"})

        assert result.consensus_reached is False
        assert colony.mesh_generation == initial_gen

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_supermajority_consensus_success(self, mock_agent_vote):
        """Test supermajority consensus succeeds with enough votes."""
        # 3 initial agents. 2 approve, 1 rejects. 2/3 = 66.7% -> fails supermajority
        # Let's make it 3 approve, 1 reject among 4 agents
        colony = SymbolicReasoningColony("test_colony")
        colony.register_agent("agent_4", {"consciousness_type": "test"})

        votes = [
            {"decision": "approved", "strength": 0.9},
            {"decision": "approved", "strength": 0.9},
            {"decision": "approved", "strength": 0.9},
            {"decision": "rejected", "strength": 0.9},
        ]
        mock_agent_vote.side_effect = votes

        result = colony.reach_supermajority_consensus({"action": "critical_decision"}, threshold=0.75)

        assert result.consensus_reached is True
        assert len(result.votes) == 4
        assert colony.mesh_generation == 1 # Incremented

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_supermajority_consensus_failure(self, mock_agent_vote):
        """Test supermajority consensus fails with insufficient votes."""
        colony = SymbolicReasoningColony("test_colony")
        colony.register_agent("agent_4", {"consciousness_type": "test"})

        votes = [
            {"decision": "approved", "strength": 0.9},
            {"decision": "approved", "strength": 0.9},
            {"decision": "rejected", "strength": 0.9},
            {"decision": "rejected", "strength": 0.9},
        ]
        mock_agent_vote.side_effect = votes

        result = colony.reach_supermajority_consensus({"action": "critical_decision"}, threshold=0.75)

        assert result.consensus_reached is False
        assert colony.mesh_generation == 0 # Not incremented

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_unanimous_consensus_success(self, mock_agent_vote):
        """Test unanimous consensus succeeds when all approve."""
        mock_agent_vote.return_value = {"decision": "approved", "strength": 1.0}

        colony = SymbolicReasoningColony("test_colony")
        result = colony.reach_unanimous_consensus({"action": "unanimous_test"})

        assert result.consensus_reached is True
        assert all(v == "approved" for v in result.votes.values())
        assert colony.mesh_generation == 1

    @patch('core.symbolic_legacy.colony_tag_propagation.SymbolicReasoningColony._agent_vote')
    def test_unanimous_consensus_failure_due_to_rejection(self, mock_agent_vote):
        """Test unanimous consensus fails with one rejection."""
        votes = [
            {"decision": "approved", "strength": 1.0},
            {"decision": "approved", "strength": 1.0},
            {"decision": "rejected", "strength": 1.0},
        ]
        mock_agent_vote.side_effect = votes

        colony = SymbolicReasoningColony("test_colony")
        result = colony.reach_unanimous_consensus({"action": "unanimous_test"})

        assert result.consensus_reached is False
        assert colony.mesh_generation == 0

    def test_mesh_status_reporting(self):
        """Test mesh formation status reporting."""
        colony = SymbolicReasoningColony("test_colony")

        status = colony.get_mesh_status()

        assert "mesh_generation" in status
        assert "agent_count" in status
        assert "network_nodes" in status
        assert "drift_score" in status
        assert status["agent_count"] >= 3  # Initial agents

    def test_consensus_updates_history(self):
        """Test consensus attempts are recorded in history."""
        colony = SymbolicReasoningColony("test_colony")

        initial_count = len(colony.propagation_history)
        colony.reach_consensus({"action": "history_test"})

        assert len(colony.propagation_history) > initial_count
        last_entry = colony.propagation_history[-1]
        assert last_entry["action"] == "consensus"
        assert "consensus_reached" in last_entry
