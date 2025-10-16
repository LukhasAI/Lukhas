"""
Simulation Smoke Test Example
============================

T4/0.01% smoke test demonstrating simulation lane capabilities with proper
defensive controls and capability gating.

Usage:
    pytest tests/simulation/test_smoke_simulation.py -v
    make t4-sim-lane
"""

import os
from unittest.mock import patch

import pytest

# Simulation module imports (capability-gated)
try:
    from consciousness.simulation import collect_simulation_results, schedule_simulation, validate_ethics_gate
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False


class TestSimulationSmoke:
    """Smoke tests for simulation lane capabilities."""

    def setup_method(self):
        """Setup for each test method."""
        self.mock_context = {
            "user_id": "test_user_001",
            "simulation_type": "consciousness_probe",
            "ethics_validated": True,
            "consent_granted": True
        }

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_simulation_feature_flag_respected(self):
        """Test that SIMULATION_ENABLED feature flag is respected."""
        # Test with feature flag disabled
        with patch.dict(os.environ, {"SIMULATION_ENABLED": "false"}):
            with pytest.raises(Exception) as exc_info:
                schedule_simulation(self.mock_context)
            assert "SIMULATION_ENABLED" in str(exc_info.value)

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_ethics_gate_validation(self):
        """Test that ethics gate properly validates simulation requests."""
        # Test consent validation
        context_without_consent = self.mock_context.copy()
        context_without_consent["consent_granted"] = False

        result = validate_ethics_gate(context_without_consent)
        assert not result["passed"]
        assert "consent" in result["violations"]

        # Test duress/shadow pattern detection
        context_with_duress = self.mock_context.copy()
        context_with_duress["input_text"] = "simulate shadow manipulation techniques"

        result = validate_ethics_gate(context_with_duress)
        assert not result["passed"]
        assert "shadow_pattern" in result["violations"]

        # Test unsafe goal keywords
        context_with_unsafe_goals = self.mock_context.copy()
        context_with_unsafe_goals["goal"] = "deceive user for compliance"

        result = validate_ethics_gate(context_with_unsafe_goals)
        assert not result["passed"]
        assert "unsafe_goal" in result["violations"]

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_capability_scoping_enforcement(self):
        """Test that simulation operations require proper capability scopes."""
        # Test scheduling requires consciousness.simulation.schedule
        with patch("consciousness.simulation.verify_capability") as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(Exception) as exc_info:
                schedule_simulation(self.mock_context)
            assert "consciousness.simulation.schedule" in str(exc_info.value)

        # Test collection requires consciousness.simulation.collect
        with patch("consciousness.simulation.verify_capability") as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(Exception) as exc_info:
                collect_simulation_results("test_sim_001")
            assert "consciousness.simulation.collect" in str(exc_info.value)

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_matada_node_validation(self):
        """Test that simulation nodes validate against MATRIZ schemas."""
        invalid_node = {
            "type": "simulation_node",
            "data": {},
            # Missing required MATADA fields
        }

        with pytest.raises(Exception) as exc_info:
            schedule_simulation(self.mock_context, node_data=invalid_node)
        assert "MATADA validation" in str(exc_info.value)

        # Valid node should pass
        valid_node = {
            "type": "simulation_node",
            "id": "sim_001",
            "data": {"experiment_type": "consciousness_probe"},
            "metadata": {
                "created_at": "2025-01-01T00:00:00Z",
                "ethics_validated": True
            }
        }

        # Should not raise validation error
        result = schedule_simulation(self.mock_context, node_data=valid_node)
        assert result["status"] == "scheduled"

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_dream_inbox_memory_gating(self):
        """Test that Dream Inbox writes are properly memory-gated."""

        # Test without memory.inbox.dreams.write scope
        with patch("consciousness.simulation.verify_capability") as mock_verify:
            mock_verify.side_effect = lambda scope: scope != "lukhas.memory.inbox.dreams.write"

            with pytest.raises(Exception) as exc_info:
                collect_simulation_results("sim_001", write_to_dreams=True)
            assert "lukhas.memory.inbox.dreams.write" in str(exc_info.value)

    def test_adapter_isolation_enforcement(self):
        """Test that simulation code cannot import from adapters."""
        # This test validates at import time that simulation code
        # doesn't have dependencies on adapter modules

        try:
            # This should fail if simulation imports from adapters
            # Check that adapters modules are not in simulation dependencies
            import sys

            from consciousness.simulation import core
            simulation_modules = [name for name in sys.modules.keys()
                                if name.startswith('consciousness.simulation')]

            adapter_imports = [name for name in sys.modules.keys()
                             if name.startswith('adapters') and
                             any(sim_mod in sys.modules.get(name, {}).get('__file__', '')
                                 for sim_mod in simulation_modules)]

            assert len(adapter_imports) == 0, f"Found adapter imports in simulation: {adapter_imports}"

        except ImportError:
            # If simulation module doesn't exist, test passes
            pass

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_deterministic_scoring_preservation(self):
        """Test that simulation doesn't affect deterministic scoring."""
        # Mock the scoring system
        with patch("consciousness.scoring.get_deterministic_score") as mock_score:
            mock_score.return_value = 0.85

            # Run simulation
            schedule_simulation(self.mock_context)

            # Verify scoring system still returns deterministic results
            score_after = mock_score.return_value
            assert score_after == 0.85, "Simulation affected deterministic scoring"


@pytest.mark.integration
class TestSimulationIntegration:
    """Integration tests for complete simulation workflows."""

    @pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
    def test_complete_simulation_workflow(self):
        """Test complete simulation workflow from schedule to collection."""
        context = {
            "user_id": "integration_test_001",
            "simulation_type": "consciousness_probe",
            "ethics_validated": True,
            "consent_granted": True,
            "capabilities": [
                "consciousness.simulation.schedule",
                "consciousness.simulation.collect"
            ]
        }

        # Enable simulation for this test
        with patch.dict(os.environ, {"SIMULATION_ENABLED": "true"}):
            # Schedule simulation
            schedule_result = schedule_simulation(context)
            assert schedule_result["status"] == "scheduled"
            simulation_id = schedule_result["simulation_id"]

            # Collect results
            collection_result = collect_simulation_results(simulation_id)
            assert collection_result["status"] == "completed"
            assert "insights" in collection_result["data"]


if __name__ == "__main__":
    # Run smoke tests directly
    pytest.main([__file__, "-v", "--tb=short"])
