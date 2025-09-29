"""
Tests for multi-agent dream mesh.
Ensures multi-agent aggregation is deterministic and safe.
"""
import os
from unittest.mock import patch

from lukhas.consciousness.dream.expand.mesh import (
    mesh_align, mesh_consensus, analyze_mesh_diversity,
    validate_mesh_output, get_mesh_config
)

class TestMeshAlignment:
    """Test multi-agent dream mesh functionality."""

    def test_disabled_by_default(self):
        """Test that mesh is disabled by default."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.5, "joy": 0.8}}],
            [{"emotional_context": {"confidence": 0.7, "joy": 0.6}}]
        ]

        result = mesh_align(agent_snapshots)
        assert result == {}  # Should be empty when disabled

        config = get_mesh_config()
        assert config["enabled"] is False

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_AGGREGATION": "mean"})
    def test_mean_aggregation(self):
        """Test mean aggregation across agents."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.6, "joy": 0.8}}],
            [{"emotional_context": {"confidence": 0.4, "joy": 0.2}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should compute mean across agents
        expected_confidence = (0.6 + 0.4) / 2  # = 0.5
        expected_joy = (0.8 + 0.2) / 2  # = 0.5

        assert abs(result["confidence"] - expected_confidence) < 0.001
        assert abs(result["joy"] - expected_joy) < 0.001

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_AGGREGATION": "median"})
    def test_median_aggregation(self):
        """Test median aggregation across agents."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.2}}],
            [{"emotional_context": {"confidence": 0.5}}],
            [{"emotional_context": {"confidence": 0.8}}]
        ]

        result = mesh_align(agent_snapshots)

        # Median of [0.2, 0.5, 0.8] = 0.5
        assert abs(result["confidence"] - 0.5) < 0.001

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_AGGREGATION": "max"})
    def test_max_aggregation(self):
        """Test max aggregation across agents."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.3, "joy": 0.9}}],
            [{"emotional_context": {"confidence": 0.7, "joy": 0.4}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should take maximum values
        assert result["confidence"] == 0.7
        assert result["joy"] == 0.9

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_AGGREGATION": "min"})
    def test_min_aggregation(self):
        """Test min aggregation across agents."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.3, "joy": 0.9}}],
            [{"emotional_context": {"confidence": 0.7, "joy": 0.4}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should take minimum values
        assert result["confidence"] == 0.3
        assert result["joy"] == 0.4

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_insufficient_agents(self):
        """Test behavior with insufficient agents."""
        # Only one agent (below minimum)
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.5}}]
        ]

        result = mesh_align(agent_snapshots)
        assert result == {}  # Should return empty

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_value_clamping(self):
        """Test that aggregated values are clamped to [0,1] range."""
        # Use values that might aggregate outside valid range
        agent_snapshots = [
            [{"emotional_context": {"confidence": 1.5}}],  # Invalid input (will be clamped)
            [{"emotional_context": {"confidence": -0.5}}]  # Invalid input (will be clamped)
        ]

        result = mesh_align(agent_snapshots)

        # Should clamp individual values and aggregation result
        for key, value in result.items():
            assert 0.0 <= value <= 1.0

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_multiple_snapshots_per_agent(self):
        """Test aggregation with multiple snapshots per agent."""
        agent_snapshots = [
            [
                {"emotional_context": {"confidence": 0.4}},
                {"emotional_context": {"confidence": 0.6}}
            ],
            [
                {"emotional_context": {"confidence": 0.2}},
                {"emotional_context": {"confidence": 0.8}}
            ]
        ]

        result = mesh_align(agent_snapshots)

        # Should include all snapshots from all agents
        # Values: [0.4, 0.6, 0.2, 0.8] -> mean = 0.5
        assert abs(result["confidence"] - 0.5) < 0.001

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_missing_emotional_context(self):
        """Test handling of snapshots without emotional context."""
        agent_snapshots = [
            [{"no_emotion": "test"}],  # Missing emotional_context
            [{"emotional_context": {"confidence": 0.5}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should skip invalid snapshots
        assert result.get("confidence") == 0.5

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_invalid_emotion_values(self):
        """Test handling of invalid emotion values."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": "invalid"}}],
            [{"emotional_context": {"confidence": 0.5}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should skip invalid values
        assert result.get("confidence") == 0.5

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_mesh_consensus(self):
        """Test mesh consensus functionality."""
        # Simple majority case
        agent_selections = ["option_a", "option_a", "option_b"]
        consensus = mesh_consensus(agent_selections)

        assert consensus == "option_a"  # Majority winner

        # Weighted consensus
        agent_selections = ["option_a", "option_b"]
        agent_confidences = [0.3, 0.7]
        consensus = mesh_consensus(agent_selections, agent_confidences)

        assert consensus == "option_b"  # Higher weight

    def test_mesh_consensus_disabled(self):
        """Test mesh consensus when disabled."""
        agent_selections = ["option_a", "option_b"]
        consensus = mesh_consensus(agent_selections)

        assert consensus is None  # Should return None when disabled

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_diversity_analysis(self):
        """Test mesh diversity analysis."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.9, "joy": 0.1}}],
            [{"emotional_context": {"confidence": 0.1, "joy": 0.9}}]
        ]

        analysis = analyze_mesh_diversity(agent_snapshots)

        assert analysis["enabled"] is True
        assert analysis["agent_count"] == 2
        assert "emotion_diversity" in analysis
        assert "overall_diversity" in analysis

        # Should detect high diversity between agents
        assert analysis["overall_diversity"] > 0.1

    def test_diversity_analysis_disabled(self):
        """Test diversity analysis when disabled."""
        agent_snapshots = []
        analysis = analyze_mesh_diversity(agent_snapshots)

        assert analysis["enabled"] is False

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1"})
    def test_mesh_validation(self):
        """Test mesh output validation."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.3, "joy": 0.7}}],
            [{"emotional_context": {"confidence": 0.7, "joy": 0.3}}]
        ]

        aggregated = mesh_align(agent_snapshots)
        is_valid = validate_mesh_output(agent_snapshots, aggregated)

        assert is_valid

        # Test with invalid output
        invalid_output = {"confidence": 1.5, "joy": -0.5}
        is_valid = validate_mesh_output(agent_snapshots, invalid_output)

        assert not is_valid

    def test_mesh_validation_disabled(self):
        """Test mesh validation when disabled."""
        agent_snapshots = []
        aggregated = {"should": "be_empty"}

        # When disabled, should only validate that output is empty
        assert not validate_mesh_output(agent_snapshots, aggregated)
        assert validate_mesh_output(agent_snapshots, {})

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_MIN_AGENTS": "3"})
    def test_custom_min_agents(self):
        """Test custom minimum agent requirement."""
        # Only 2 agents (below custom minimum of 3)
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.5}}],
            [{"emotional_context": {"confidence": 0.7}}]
        ]

        result = mesh_align(agent_snapshots)
        assert result == {}  # Should be empty due to insufficient agents

    def test_config_reporting(self):
        """Test mesh configuration reporting."""
        with patch.dict(os.environ, {
            "LUKHAS_MULTI_AGENT": "1",
            "LUKHAS_MESH_AGGREGATION": "median",
            "LUKHAS_MESH_MIN_AGENTS": "5"
        }):
            config = get_mesh_config()

            assert config["enabled"] is True
            assert config["aggregation_method"] == "median"
            assert config["min_agents"] == 5
            assert "valid_methods" in config

    @patch.dict(os.environ, {"LUKHAS_MULTI_AGENT": "1", "LUKHAS_MESH_AGGREGATION": "invalid"})
    def test_invalid_aggregation_method(self):
        """Test handling of invalid aggregation method."""
        agent_snapshots = [
            [{"emotional_context": {"confidence": 0.3}}],
            [{"emotional_context": {"confidence": 0.7}}]
        ]

        result = mesh_align(agent_snapshots)

        # Should default to mean for invalid methods
        expected_mean = (0.3 + 0.7) / 2
        assert abs(result["confidence"] - expected_mean) < 0.001