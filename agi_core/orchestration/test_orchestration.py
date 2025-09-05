"""
Comprehensive test suite for AGI Multi-Model Orchestration Hub.

Tests all components: ModelRouter, ConsensusEngine, CapabilityMatrix, CostOptimizer.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from .model_router import ModelRouter, RoutingRequest, ModelResponse, RoutingDecision
from .consensus_engine import ConsensusEngine, ConsensusResult, ConsensusMethod
from .capability_matrix import CapabilityMatrix, TaskType, TaskRequirements, CapabilityDimension
from .cost_optimizer import CostOptimizer, CostConstraints, OptimizationStrategy, CostTier

class TestCapabilityMatrix:
    """Test capability matrix functionality."""
    
    def test_initialization(self):
        """Test capability matrix initializes with model profiles."""
        matrix = CapabilityMatrix()
        
        assert len(matrix.model_profiles) > 0
        assert "gpt-4-turbo" in matrix.model_profiles
        assert "claude-3-5-sonnet" in matrix.model_profiles
        assert "gemini-1.5-pro" in matrix.model_profiles
    
    def test_model_score_calculation(self):
        """Test model scoring for task requirements."""
        matrix = CapabilityMatrix()
        
        requirements = TaskRequirements(
            task_type=TaskType.REASONING,
            required_capabilities={CapabilityDimension.REASONING: 0.8},
            preferred_capabilities={CapabilityDimension.REASONING: 0.9}
        )
        
        score = matrix.calculate_model_score("claude-3-5-sonnet", requirements)
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Should meet requirements
    
    def test_model_ranking(self):
        """Test model ranking functionality."""
        matrix = CapabilityMatrix()
        
        requirements = TaskRequirements(
            task_type=TaskType.CREATIVE,
            required_capabilities={CapabilityDimension.CREATIVITY: 0.7},
            preferred_capabilities={CapabilityDimension.CREATIVITY: 0.85}
        )
        
        rankings = matrix.rank_models(requirements)
        
        assert len(rankings) > 0
        assert all(score > 0.0 for _, score in rankings)
        assert rankings == sorted(rankings, key=lambda x: x[1], reverse=True)  # Sorted descending
    
    def test_constellation_alignment(self):
        """Test constellation framework integration."""
        matrix = CapabilityMatrix()
        
        requirements = TaskRequirements(
            task_type=TaskType.REASONING,
            required_capabilities={CapabilityDimension.REASONING: 0.7},
            preferred_capabilities={CapabilityDimension.REASONING: 0.8},
            constellation_context={"DREAM": 0.9, "ETHICS": 0.8}  # Dream-focused ethical reasoning
        )
        
        score = matrix.calculate_model_score("claude-3-5-sonnet", requirements)
        assert score > 0.0
    
    def test_performance_tracking(self):
        """Test performance statistics tracking."""
        matrix = CapabilityMatrix()
        
        # Add some task results
        matrix.add_task_result("gpt-4-turbo", TaskType.REASONING, True, 2000, 0.85)
        matrix.add_task_result("gpt-4-turbo", TaskType.REASONING, True, 1800, 0.90)
        matrix.add_task_result("gpt-4-turbo", TaskType.CREATIVE, False, 2500, 0.60)
        
        stats = matrix.get_model_performance_stats("gpt-4-turbo")
        
        assert "success_rate" in stats
        assert "average_latency_ms" in stats
        assert "average_quality" in stats
        assert stats["task_count"] == 3
        
        # Test task type filtering
        reasoning_stats = matrix.get_model_performance_stats("gpt-4-turbo", TaskType.REASONING)
        assert reasoning_stats["task_count"] == 2
        assert reasoning_stats["success_rate"] == 1.0


class TestCostOptimizer:
    """Test cost optimization functionality."""
    
    def test_initialization(self):
        """Test cost optimizer initializes with cost profiles."""
        optimizer = CostOptimizer()
        
        assert len(optimizer.cost_profiles) > 0
        assert "gpt-4-turbo" in optimizer.cost_profiles
        assert optimizer.cost_profiles["gpt-4-turbo"].cost_tier == CostTier.PREMIUM
    
    def test_cost_calculation(self):
        """Test cost calculation for requests."""
        optimizer = CostOptimizer()
        
        profile = optimizer.cost_profiles["gpt-4-turbo"]
        cost = profile.calculate_request_cost(1000, 500)
        
        expected_cost = 1000 * profile.cost_per_input_token + 500 * profile.cost_per_output_token
        assert cost == expected_cost
    
    def test_cost_constraint_checking(self):
        """Test cost constraint validation."""
        optimizer = CostOptimizer()
        
        constraints = CostConstraints(
            max_cost_per_request=0.01,
            max_cost_per_hour=1.0
        )
        
        # Should pass for reasonable cost
        assert optimizer.check_cost_constraints(0.005, constraints) == True
        
        # Should fail for high cost
        assert optimizer.check_cost_constraints(0.02, constraints) == False
    
    def test_model_selection_optimization(self):
        """Test optimized model selection."""
        optimizer = CostOptimizer()
        
        candidate_models = [
            ("gpt-4-turbo", 0.90),
            ("claude-3-5-sonnet", 0.92),
            ("gpt-3.5-turbo", 0.75)
        ]
        
        constraints = CostConstraints(
            strategy=OptimizationStrategy.BALANCE_COST_QUALITY,
            quality_threshold=0.7
        )
        
        optimized = optimizer.optimize_model_selection(candidate_models, constraints)
        
        assert len(optimized) > 0
        assert all(quality >= constraints.quality_threshold for _, quality, _ in optimized)
    
    def test_usage_recording(self):
        """Test usage recording and statistics."""
        optimizer = CostOptimizer()
        
        # Record some usage
        optimizer.record_usage("gpt-4-turbo", 1000, 500, 0.85)
        optimizer.record_usage("claude-3-5-sonnet", 1200, 600, 0.90)
        
        stats = optimizer.get_usage_statistics()
        
        assert stats.requests_count == 2
        assert stats.total_cost > 0.0
        assert stats.avg_quality_score > 0.0
    
    def test_cost_optimization_recommendations(self):
        """Test cost optimization recommendations."""
        optimizer = CostOptimizer()
        
        # Record high-cost usage
        for _ in range(10):
            optimizer.record_usage("gpt-4-turbo", 2000, 1000, 0.85)
        
        stats = optimizer.get_usage_statistics()
        constraints = CostConstraints(max_cost_per_day=1.0)
        
        recommendations = optimizer.recommend_cost_optimization(stats, constraints)
        
        assert "current_efficiency" in recommendations
        assert "suggestions" in recommendations


class TestModelRouter:
    """Test model router functionality."""
    
    @pytest.fixture
    def router(self):
        """Create router instance for testing."""
        return ModelRouter()
    
    @pytest.mark.asyncio
    async def test_router_initialization(self, router):
        """Test router initializes properly."""
        assert router.capability_matrix is not None
        assert router.cost_optimizer is not None
        assert len(router.model_clients) == 0  # No real clients in test
    
    @pytest.mark.asyncio
    async def test_routing_decision_logic(self, router):
        """Test routing decision logic."""
        request = RoutingRequest(
            content="Explain quantum mechanics",
            task_type=TaskType.SCIENTIFIC,
            priority=1.0,
            max_cost_per_request=0.05
        )
        
        # Mock the model clients to avoid real API calls
        with patch.object(router, '_call_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = ModelResponse(
                content="Quantum mechanics explanation...",
                model_used="claude-3-5-sonnet",
                latency_ms=2000,
                cost=0.018,
                quality_score=0.92,
                metadata={}
            )
            
            decision, response = await router.route_request(request)
            
            assert isinstance(decision, RoutingDecision)
            assert isinstance(response, ModelResponse)
            assert decision.selected_model in router.capability_matrix.model_profiles
    
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, router):
        """Test fallback to alternative models on failure."""
        request = RoutingRequest(
            content="Simple task",
            task_type=TaskType.CONVERSATIONAL
        )
        
        with patch.object(router, '_call_model', side_effect=[
            Exception("API error"),  # First model fails
            ModelResponse(  # Fallback succeeds
                content="Response from fallback",
                model_used="gpt-3.5-turbo",
                latency_ms=800,
                cost=0.002,
                quality_score=0.75,
                metadata={}
            )
        ]) as mock_call:
            
            decision, response = await router.route_request(request)
            
            assert response is not None
            assert response.model_used == "gpt-3.5-turbo"
            assert mock_call.call_count == 2  # Tried primary then fallback


class TestConsensusEngine:
    """Test consensus engine functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create consensus engine for testing."""
        return ConsensusEngine()
    
    @pytest.mark.asyncio
    async def test_consensus_initialization(self, engine):
        """Test consensus engine initializes properly."""
        assert engine.model_router is not None
        assert len(engine.consensus_history) == 0
    
    @pytest.mark.asyncio
    async def test_majority_voting_consensus(self, engine):
        """Test majority voting consensus method."""
        # Mock model responses
        mock_responses = [
            ModelResponse("Answer A", "gpt-4-turbo", 2000, 0.03, 0.85, {}),
            ModelResponse("Answer A", "claude-3-5-sonnet", 2500, 0.018, 0.90, {}),
            ModelResponse("Answer B", "gemini-1.5-pro", 1800, 0.015, 0.82, {})
        ]
        
        with patch.object(engine.model_router, 'route_request', side_effect=mock_responses):
            result = await engine.reach_consensus(
                question="Test question",
                models=["gpt-4-turbo", "claude-3-5-sonnet", "gemini-1.5-pro"],
                method=ConsensusMethod.MAJORITY_VOTE
            )
            
            assert isinstance(result, ConsensusResult)
            assert result.consensus_reached == True
            assert result.final_answer == "Answer A"  # Majority answer
            assert result.agreement_level > 0.5
    
    @pytest.mark.asyncio 
    async def test_weighted_consensus(self, engine):
        """Test weighted consensus by model quality."""
        mock_responses = [
            ModelResponse("High quality answer", "claude-3-5-sonnet", 2500, 0.018, 0.95, {}),
            ModelResponse("Lower quality answer", "gpt-3.5-turbo", 800, 0.002, 0.70, {})
        ]
        
        with patch.object(engine.model_router, 'route_request', side_effect=mock_responses):
            result = await engine.reach_consensus(
                question="Test question",
                models=["claude-3-5-sonnet", "gpt-3.5-turbo"],
                method=ConsensusMethod.WEIGHTED_QUALITY
            )
            
            assert result.consensus_reached == True
            # Should prefer higher quality response
            assert "High quality" in result.final_answer
    
    @pytest.mark.asyncio
    async def test_dream_integrated_consensus(self, engine):
        """Test dream-integrated consensus method."""
        with patch('agi_core.reasoning.dream_integration.DreamReasoningBridge') as mock_dream:
            mock_dream.return_value.generate_insight.return_value = Mock(
                content="Dream insight: The answer involves quantum principles",
                confidence=0.85,
                insight_type="SYNTHESIS"
            )
            
            mock_responses = [
                ModelResponse("Quantum answer", "gpt-4-turbo", 2000, 0.03, 0.88, {}),
                ModelResponse("Classical answer", "claude-3-5-sonnet", 2500, 0.018, 0.85, {})
            ]
            
            with patch.object(engine.model_router, 'route_request', side_effect=mock_responses):
                result = await engine.reach_consensus(
                    question="Physics question",
                    models=["gpt-4-turbo", "claude-3-5-sonnet"],
                    method=ConsensusMethod.DREAM_SYNTHESIS
                )
                
                assert result.consensus_reached == True
                # Should incorporate dream insight
                assert "quantum" in result.final_answer.lower()
    
    @pytest.mark.asyncio
    async def test_no_consensus_scenario(self, engine):
        """Test scenario where no consensus is reached."""
        # Mock completely different responses
        mock_responses = [
            ModelResponse("Answer A", "gpt-4-turbo", 2000, 0.03, 0.80, {}),
            ModelResponse("Answer B", "claude-3-5-sonnet", 2500, 0.018, 0.80, {}),
            ModelResponse("Answer C", "gemini-1.5-pro", 1800, 0.015, 0.80, {})
        ]
        
        with patch.object(engine.model_router, 'route_request', side_effect=mock_responses):
            result = await engine.reach_consensus(
                question="Ambiguous question",
                models=["gpt-4-turbo", "claude-3-5-sonnet", "gemini-1.5-pro"],
                consensus_threshold=0.8,  # High threshold
                method=ConsensusMethod.MAJORITY_VOTE
            )
            
            assert result.consensus_reached == False
            assert result.agreement_level < 0.8
            assert len(result.disagreements) > 0


class TestIntegratedOrchestration:
    """Test integrated orchestration functionality."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_orchestration(self):
        """Test complete end-to-end orchestration workflow."""
        router = ModelRouter()
        consensus_engine = ConsensusEngine()
        
        # Mock API responses to avoid real calls
        mock_response = ModelResponse(
            content="Integrated response from orchestration",
            model_used="claude-3-5-sonnet",
            latency_ms=2200,
            cost=0.018,
            quality_score=0.92,
            metadata={"orchestration": "integrated"}
        )
        
        with patch.object(router, '_call_model', return_value=mock_response):
            # Test routing
            request = RoutingRequest(
                content="Complex AGI reasoning task",
                task_type=TaskType.REASONING,
                constellation_context={"DREAM": 0.8, "GUARDIAN": 0.9}
            )
            
            decision, response = await router.route_request(request)
            
            assert response.quality_score > 0.8
            assert decision.reasoning is not None
            
            # Test consensus for critical decisions
            with patch.object(consensus_engine.model_router, 'route_request', return_value=(decision, response)):
                consensus_result = await consensus_engine.reach_consensus(
                    question="Critical AGI decision",
                    models=["claude-3-5-sonnet", "gpt-4-turbo"]
                )
                
                assert consensus_result.consensus_reached == True
                assert consensus_result.confidence_score > 0.8
    
    def test_performance_benchmarks(self):
        """Test performance meets AGI requirements."""
        matrix = CapabilityMatrix()
        optimizer = CostOptimizer()
        
        # Test capability matrix performance
        requirements = TaskRequirements(
            task_type=TaskType.REASONING,
            required_capabilities={CapabilityDimension.REASONING: 0.8}
        )
        
        import time
        start_time = time.time()
        rankings = matrix.rank_models(requirements)
        matrix_time = time.time() - start_time
        
        assert matrix_time < 0.1  # Should be fast (<100ms)
        assert len(rankings) > 0
        
        # Test cost optimizer performance
        candidates = [("gpt-4-turbo", 0.9), ("claude-3-5-sonnet", 0.92)]
        constraints = CostConstraints()
        
        start_time = time.time()
        optimized = optimizer.optimize_model_selection(candidates, constraints)
        optimizer_time = time.time() - start_time
        
        assert optimizer_time < 0.05  # Should be very fast (<50ms)
        assert len(optimized) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])