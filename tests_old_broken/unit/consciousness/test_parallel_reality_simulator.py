#!/usr/bin/env python3
"""
Test Suite for Parallel Reality Simulator
========================================
Tests for the enhanced parallel reality simulation system.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

from candidate.consciousness.dream.parallel_reality_simulator import (
    ParallelRealitySimulator,
    RealityType,
)
from lukhas.core.common import GLYPHSymbol, GLYPHToken
from core.common.exceptions import LukhasError, ValidationError


@pytest.fixture
def mock_services():
    """Create mock services for testing"""
    services = {
        "memory_service": Mock(),
        "consciousness_service": Mock(),
        "guardian_service": Mock(),
        "dream_engine": Mock(),
    }

    # Configure memory service
    services["memory_service"].store = AsyncMock(return_value="mem_test_123")

    # Configure guardian service
    services["guardian_service"].validate_action = AsyncMock(
        return_value={
            "approved": True,
            "confidence": 0.85,
            "reasoning": "Test validation passed",
        }
    )

    # Configure consciousness service
    services["consciousness_service"].assess_awareness = AsyncMock(
        return_value={
            "overall_awareness": 0.8,
            "attention_targets": ["test_target"],
        }
    )

    return services


@pytest.fixture
async def simulator(mock_services):
    """Create initialized simulator with mocked services"""
    with patch(
        "consciousness.dream.parallel_reality_simulator.get_service"
    ) as mock_get:

        def get_service_side_effect(service_name):
            return mock_services.get(service_name)

        mock_get.side_effect = get_service_side_effect

        sim = ParallelRealitySimulator(
            config={
                "max_branches": 5,
                "max_depth": 3,
                "ethical_threshold": 0.4,
                "quantum_seed": 42,  # Fixed seed for reproducible tests
            }
        )

        await sim.initialize()
        return sim


class TestParallelRealitySimulator:
    """Test parallel reality simulator functionality"""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_services):
        """Test simulator initialization"""
        with patch(
            "consciousness.dream.parallel_reality_simulator.get_service"
        ) as mock_get:
            mock_get.side_effect = lambda name: mock_services.get(name)

            simulator = ParallelRealitySimulator()
            assert not simulator.operational

            await simulator.initialize()
            assert simulator.operational
            assert simulator.memory_service is not None
            assert simulator.guardian_service is not None

    @pytest.mark.asyncio
    async def test_create_simulation(self, simulator):
        """Test creating new simulation"""
        origin_scenario = {
            "decision": "test_decision",
            "context": {"environment": "test"},
            "options": ["A", "B", "C"],
        }

        simulation = await simulator.create_simulation(
            origin_scenario=origin_scenario,
            reality_types=[RealityType.QUANTUM, RealityType.CAUSAL],
            branch_count=3,
        )

        assert simulation.simulation_id.startswith("sim_")
        assert len(simulation.branches) == 3
        assert simulation.origin_reality == origin_scenario
        assert simulation.start_time <= datetime.now(timezone.utc)

        # Check branches
        for branch in simulation.branches:
            assert branch.branch_id.startswith("branch_")
            assert branch.parent_id is None  # Initial branches have no parent
            assert branch.reality_type in [
                RealityType.QUANTUM,
                RealityType.CAUSAL,
            ]
            assert 0.0 <= branch.probability <= 1.0
            assert 0.0 <= branch.ethical_score <= 1.0

    @pytest.mark.asyncio
    async def test_explore_branch(self, simulator):
        """Test exploring reality branches"""
        # Create initial simulation
        simulation = await simulator.create_simulation(
            origin_scenario={"test": "scenario"}, branch_count=2
        )

        len(simulation.branches)
        branch_to_explore = simulation.branches[0]

        # Explore the branch
        new_branches = await simulator.explore_branch(
            simulation.simulation_id, branch_to_explore.branch_id, depth=1
        )

        assert len(new_branches) > 0
        assert len(new_branches) <= simulator.max_branches_per_reality

        # Check new branches
        for branch in new_branches:
            assert branch.parent_id == branch_to_explore.branch_id
            assert len(branch.causal_chain) > 0
            assert branch.is_viable() or branch.probability <= simulator.min_probability

    @pytest.mark.asyncio
    async def test_collapse_reality(self, simulator):
        """Test collapsing parallel realities"""
        # Create simulation with multiple branches
        simulation = await simulator.create_simulation(
            origin_scenario={"collapse": "test"}, branch_count=5
        )

        # Set different probabilities for testing
        for i, branch in enumerate(simulation.branches):
            branch.probability = 0.1 + (i * 0.2)

        # Collapse with probability maximization
        selected = await simulator.collapse_reality(
            simulation.simulation_id,
            selection_criteria={"maximize": "probability"},
        )

        assert selected == max(simulation.branches, key=lambda b: b.probability)
        assert simulation.selected_branch == selected.branch_id
        assert len(simulation.insights) > 0

    @pytest.mark.asyncio
    async def test_merge_realities(self, simulator):
        """Test merging multiple reality branches"""
        # Create simulation
        simulation = await simulator.create_simulation(
            origin_scenario={"merge": "test"}, branch_count=3
        )

        # Select branches to merge
        branch_ids = [b.branch_id for b in simulation.branches[:2]]

        # Merge branches
        merged = await simulator.merge_realities(simulation.simulation_id, branch_ids)

        assert merged.branch_id.startswith("merged_")
        assert merged.reality_type == RealityType.CREATIVE
        assert "merge_sources" in merged.divergence_point
        assert len(merged.causal_chain) >= len(branch_ids)

    @pytest.mark.asyncio
    async def test_reality_types(self, simulator):
        """Test different reality type generation"""
        reality_types_to_test = [
            RealityType.QUANTUM,
            RealityType.TEMPORAL,
            RealityType.CAUSAL,
            RealityType.ETHICAL,
            RealityType.CREATIVE,
            RealityType.PREDICTIVE,
        ]

        for reality_type in reality_types_to_test:
            simulation = await simulator.create_simulation(
                origin_scenario={"type_test": reality_type.value},
                reality_types=[reality_type],
                branch_count=1,
            )

            branch = simulation.branches[0]
            assert branch.reality_type == reality_type

            # Check type-specific divergence
            divergence = branch.divergence_point

            if reality_type == RealityType.QUANTUM:
                assert "quantum_shift" in divergence
                assert "coherence" in divergence
            elif reality_type == RealityType.TEMPORAL:
                assert "time_shift" in divergence
                assert "temporal_direction" in divergence
            elif reality_type == RealityType.CAUSAL:
                assert "causal_modification" in divergence
                assert "butterfly_effect" in divergence
            elif reality_type == RealityType.ETHICAL:
                assert "ethical_framework" in divergence
                assert "value_shift" in divergence
            elif reality_type == RealityType.CREATIVE:
                assert "creative_seed" in divergence
                assert "imagination_level" in divergence
            elif reality_type == RealityType.PREDICTIVE:
                assert "prediction_horizon" in divergence
                assert "key_events" in divergence

    @pytest.mark.asyncio
    async def test_glyph_communication(self, simulator):
        """Test GLYPH token handling"""
        # Test DREAM token
        dream_token = GLYPHToken(
            symbol=GLYPHSymbol.DREAM,
            source="test_module",
            target="parallel_reality_simulator",
            payload={"dream_scenario": {"dream": "test"}},
        )

        response = await simulator.handle_glyph(dream_token)
        assert response.symbol == GLYPHSymbol.ACKNOWLEDGE
        assert response.payload["simulation_created"] is True
        assert "simulation_id" in response.payload

        # Test QUERY token
        query_token = GLYPHToken(
            symbol=GLYPHSymbol.QUERY,
            source="test_module",
            target="parallel_reality_simulator",
            payload={"simulation_id": "nonexistent"},
        )

        response = await simulator.handle_glyph(query_token)
        assert response.payload["exists"] is False

    @pytest.mark.asyncio
    async def test_ethical_validation(self, simulator, mock_services):
        """Test ethical score integration"""
        # Configure guardian to reject
        mock_services["guardian_service"].validate_action = AsyncMock(
            return_value={
                "approved": False,
                "confidence": 0.2,
                "reasoning": "Ethical violation detected",
            }
        )

        simulation = await simulator.create_simulation(
            origin_scenario={"ethical": "test"}, branch_count=1
        )

        branch = simulation.branches[0]
        assert branch.ethical_score == 0.0  # Rejected branches get 0 score

    @pytest.mark.asyncio
    async def test_memory_integration(self, simulator, mock_services):
        """Test memory storage integration"""
        simulation = await simulator.create_simulation(
            origin_scenario={"memory": "test"}, branch_count=2
        )

        # Collapse to trigger memory storage
        await simulator.collapse_reality(simulation.simulation_id)

        # Check memory service was called
        assert mock_services["memory_service"].store.called
        call_args = mock_services["memory_service"].store.call_args

        content = call_args[1]["content"]
        assert content["event_type"] == "collapsed"
        assert "insights" in content

    @pytest.mark.asyncio
    async def test_performance_metrics(self, simulator):
        """Test performance metric tracking"""
        initial_metrics = simulator.metrics.copy()

        # Create simulations
        for _ in range(3):
            await simulator.create_simulation(
                origin_scenario={"metrics": "test"}, branch_count=4
            )

        # Check metric updates
        assert (
            simulator.metrics["simulations_created"]
            == initial_metrics["simulations_created"] + 3
        )
        assert (
            simulator.metrics["branches_explored"]
            > initial_metrics["branches_explored"]
        )
        assert simulator.metrics["average_branches_per_simulation"] > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, simulator):
        """Test error handling scenarios"""
        # Test invalid simulation ID
        with pytest.raises(ValidationError):
            await simulator.explore_branch("invalid_sim_id", "branch_id")

        # Test invalid branch ID
        simulation = await simulator.create_simulation(
            origin_scenario={"error": "test"}, branch_count=1
        )

        with pytest.raises(ValidationError):
            await simulator.explore_branch(
                simulation.simulation_id, "invalid_branch_id"
            )

        # Test collapse with no viable branches
        # Make all branches non-viable
        for branch in simulation.branches:
            branch.probability = 0.0
            branch.ethical_score = 0.0

        with pytest.raises(LukhasError):
            await simulator.collapse_reality(simulation.simulation_id)

    @pytest.mark.asyncio
    async def test_process_interface(self, simulator):
        """Test process interface method"""
        # Test create action
        result = await simulator.process(
            {
                "action": "create",
                "scenario": {"process": "test"},
                "branch_count": 3,
            }
        )

        assert "simulation_id" in result
        assert result["branches"] == 3

        # Test explore action
        sim_id = result["simulation_id"]
        simulation = simulator.active_simulations[sim_id]

        result = await simulator.process(
            {
                "action": "explore",
                "simulation_id": sim_id,
                "branch_id": simulation.branches[0].branch_id,
                "depth": 1,
            }
        )

        assert "new_branches" in result
        assert "branch_ids" in result

        # Test collapse action
        result = await simulator.process(
            {
                "action": "collapse",
                "simulation_id": sim_id,
                "criteria": {"maximize": "probability"},
            }
        )

        assert "selected_branch" in result
        assert "insights" in result

    @pytest.mark.asyncio
    async def test_status_reporting(self, simulator):
        """Test status reporting"""
        status = await simulator.get_status()

        assert status["operational"] is True
        assert status["health_score"] == 1.0
        assert "active_simulations" in status
        assert "metrics" in status
        assert "config" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
