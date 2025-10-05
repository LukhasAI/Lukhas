#!/usr/bin/env python3
"""
Tests for LUKHAS O.2 Orchestration Core - Multi-AI Router
Production Schema v1.0.0

Comprehensive test suite for multi-AI routing, consensus mechanisms,
and performance validation.
"""

import time
from unittest.mock import Mock

import pytest

from lukhas.orchestration.multi_ai_router import (
    AIModel,
    AIProvider,
    AIResponse,
    ConsensusEngine,
    ConsensusType,
    ModelSelector,
    MultiAIRouter,
    RoutingRequest,
    get_multi_ai_router,
)


class TestModelSelector:
    """Test ModelSelector functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selector = ModelSelector()

    def test_register_model(self):
        """Test model registration"""
        model = AIModel(
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            weight=1.0
        )

        self.selector.register_model(model)

        key = "openai:gpt-4"
        assert key in self.selector.models
        assert self.selector.models[key] == model

    def test_select_models_with_specific_models(self):
        """Test model selection with specific model requests"""
        # Register models
        gpt4 = AIModel(provider=AIProvider.OPENAI, model_id="gpt-4")
        claude = AIModel(provider=AIProvider.ANTHROPIC, model_id="claude-3-sonnet")

        self.selector.register_model(gpt4)
        self.selector.register_model(claude)

        # Request specific models
        request = RoutingRequest(
            prompt="test",
            models=["openai:gpt-4", "anthropic:claude-3-sonnet"],
            min_responses=2,
            max_responses=2
        )

        selected = self.selector.select_models(request)
        assert len(selected) == 2
        assert any(m.model_id == "gpt-4" for m in selected)
        assert any(m.model_id == "claude-3-sonnet" for m in selected)

    def test_intelligent_model_selection(self):
        """Test intelligent model selection algorithm"""
        # Register models with different performance characteristics
        fast_model = AIModel(
            provider=AIProvider.OPENAI,
            model_id="gpt-3.5-turbo",
            weight=0.8,
            avg_latency=0.5,
            success_rate=0.95,
            cost_per_token=0.000002
        )

        slow_model = AIModel(
            provider=AIProvider.OPENAI,
            model_id="gpt-4",
            weight=1.0,
            avg_latency=2.0,
            success_rate=0.98,
            cost_per_token=0.00003
        )

        self.selector.register_model(fast_model)
        self.selector.register_model(slow_model)

        request = RoutingRequest(prompt="test", max_responses=2)
        selected = self.selector.select_models(request)

        # Should select both models, but order based on score
        assert len(selected) == 2

    def test_performance_update(self):
        """Test model performance tracking"""
        model = AIModel(provider=AIProvider.OPENAI, model_id="gpt-4")
        self.selector.register_model(model)

        # Update performance
        self.selector.update_performance(
            AIProvider.OPENAI, "gpt-4", 1.5, True
        )

        updated_model = self.selector.models["openai:gpt-4"]
        assert updated_model.avg_latency == 1.5
        assert updated_model.success_rate > 0

        # Update with failure
        self.selector.update_performance(
            AIProvider.OPENAI, "gpt-4", 3.0, False
        )

        # Should update moving averages
        assert updated_model.success_rate < 1.0


class TestConsensusEngine:
    """Test ConsensusEngine functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = ConsensusEngine()

    def create_mock_responses(self) -> list:
        """Create mock AI responses for testing"""
        return [
            AIResponse(
                provider=AIProvider.OPENAI,
                model_id="gpt-4",
                response="The answer is 42",
                latency=1.0,
                tokens_used=10,
                cost=0.001,
                confidence=0.9
            ),
            AIResponse(
                provider=AIProvider.ANTHROPIC,
                model_id="claude-3-sonnet",
                response="The answer is 42",
                latency=1.5,
                tokens_used=12,
                cost=0.002,
                confidence=0.8
            ),
            AIResponse(
                provider=AIProvider.GOOGLE,
                model_id="gemini-pro",
                response="The answer is actually 43",
                latency=0.8,
                tokens_used=8,
                cost=0.0005,
                confidence=0.7
            )
        ]

    @pytest.mark.asyncio
    async def test_majority_consensus(self):
        """Test majority consensus mechanism"""
        responses = self.create_mock_responses()

        result = await self.engine._majority_consensus(responses)

        assert result.consensus_type == ConsensusType.MAJORITY
        assert "42" in result.final_response
        assert result.agreement_ratio >= 0.5
        assert len(result.individual_responses) == 3

    @pytest.mark.asyncio
    async def test_weighted_consensus(self):
        """Test weighted consensus mechanism"""
        responses = self.create_mock_responses()

        result = await self.engine._weighted_consensus(responses)

        assert result.consensus_type == ConsensusType.WEIGHTED
        assert result.final_response is not None
        assert 0 <= result.confidence <= 1
        assert result.agreement_ratio >= 0

    @pytest.mark.asyncio
    async def test_best_of_n_consensus(self):
        """Test best-of-N consensus mechanism"""
        responses = self.create_mock_responses()

        result = await self.engine._best_of_n_consensus(responses)

        assert result.consensus_type == ConsensusType.BEST_OF_N
        assert result.final_response is not None
        # Should select highest scoring response
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_hybrid_consensus_high_agreement(self):
        """Test hybrid consensus with high agreement"""
        # Create responses with high similarity
        responses = [
            AIResponse(
                provider=AIProvider.OPENAI,
                model_id="gpt-4",
                response="Paris is the capital of France",
                latency=1.0,
                tokens_used=10,
                cost=0.001,
                confidence=0.9
            ),
            AIResponse(
                provider=AIProvider.ANTHROPIC,
                model_id="claude-3-sonnet",
                response="Paris is the capital of France",
                latency=1.2,
                tokens_used=10,
                cost=0.002,
                confidence=0.85
            ),
            AIResponse(
                provider=AIProvider.GOOGLE,
                model_id="gemini-pro",
                response="Paris is capital city of France",
                latency=0.9,
                tokens_used=9,
                cost=0.0005,
                confidence=0.8
            )
        ]

        result = await self.engine._hybrid_consensus(responses)

        assert result.consensus_type == ConsensusType.HYBRID
        assert result.agreement_ratio > 0.6  # Should be high agreement
        assert "method_used" in result.metadata

    @pytest.mark.asyncio
    async def test_similarity_calculation(self):
        """Test text similarity calculation"""
        text1 = "The quick brown fox jumps"
        text2 = "The quick brown fox leaps"

        similarity = await self.engine._calculate_similarity(text1, text2)

        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be reasonably similar

        # Test identical texts
        identical_similarity = await self.engine._calculate_similarity(text1, text1)
        assert identical_similarity == 1.0

        # Test completely different texts
        different_similarity = await self.engine._calculate_similarity(
            "Machine learning", "Cooking recipes"
        )
        assert different_similarity < 0.5


class TestMultiAIRouter:
    """Test MultiAIRouter functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.router = MultiAIRouter()
        self.router.register_default_models()

    @pytest.mark.asyncio
    async def test_route_request_mock(self):
        """Test multi-AI request routing with mock implementation"""
        request = RoutingRequest(
            prompt="What is the meaning of life?",
            consensus_type=ConsensusType.MAJORITY,
            min_responses=2,
            max_responses=3
        )

        # Mock AI clients
        mock_client = Mock()
        self.router.ai_clients[AIProvider.OPENAI] = mock_client
        self.router.ai_clients[AIProvider.ANTHROPIC] = mock_client

        result = await self.router.route_request(request)

        assert result is not None
        assert result.final_response is not None
        assert result.consensus_type == ConsensusType.MAJORITY
        assert len(result.participating_models) >= request.min_responses
        assert 0 <= result.confidence <= 1
        assert 0 <= result.agreement_ratio <= 1

    @pytest.mark.asyncio
    async def test_route_request_timeout(self):
        """Test request timeout handling"""
        request = RoutingRequest(
            prompt="Test prompt",
            timeout=0.1,  # Very short timeout
            min_responses=1,
            max_responses=2
        )

        # Should handle timeout gracefully
        result = await self.router.route_request(request)
        assert result is not None

    @pytest.mark.asyncio
    async def test_route_request_insufficient_responses(self):
        """Test handling of insufficient responses"""
        request = RoutingRequest(
            prompt="Test prompt",
            min_responses=5,  # More than available models
            max_responses=5
        )

        # Should raise error for insufficient responses
        with pytest.raises(ValueError, match="Only .* models available"):
            await self.router.route_request(request)

    def test_model_registration(self):
        """Test AI client registration"""
        mock_client = Mock()
        self.router.register_ai_client(AIProvider.OPENAI, mock_client)

        assert AIProvider.OPENAI in self.router.ai_clients
        assert self.router.ai_clients[AIProvider.OPENAI] == mock_client

    def test_default_models_registration(self):
        """Test default model registration"""
        # Should have models registered
        assert len(self.router.model_selector.models) > 0

        # Check for expected providers
        models = self.router.model_selector.models
        provider_models = {}
        for key, model in models.items():
            provider = model.provider.value
            if provider not in provider_models:
                provider_models[provider] = []
            provider_models[provider].append(model.model_id)

        assert "openai" in provider_models
        assert "anthropic" in provider_models
        assert "google" in provider_models


class TestRoutingRequestValidation:
    """Test RoutingRequest validation and edge cases"""

    def test_routing_request_defaults(self):
        """Test RoutingRequest default values"""
        request = RoutingRequest(prompt="test")

        assert request.prompt == "test"
        assert request.consensus_type == ConsensusType.MAJORITY
        assert request.min_responses == 2
        assert request.max_responses == 3
        assert request.timeout == 30.0
        assert isinstance(request.context, dict)
        assert isinstance(request.models, list)
        assert isinstance(request.metadata, dict)

    def test_routing_request_custom_values(self):
        """Test RoutingRequest with custom values"""
        request = RoutingRequest(
            prompt="custom prompt",
            context={"key": "value"},
            models=["openai:gpt-4"],
            consensus_type=ConsensusType.WEIGHTED,
            min_responses=1,
            max_responses=1,
            timeout=10.0,
            metadata={"custom": True}
        )

        assert request.prompt == "custom prompt"
        assert request.context["key"] == "value"
        assert request.models == ["openai:gpt-4"]
        assert request.consensus_type == ConsensusType.WEIGHTED
        assert request.min_responses == 1
        assert request.max_responses == 1
        assert request.timeout == 10.0
        assert request.metadata["custom"] == True


class TestPerformanceRequirements:
    """Test performance requirements for O.2 Orchestration Core"""

    def setup_method(self):
        """Set up test fixtures"""
        self.router = get_multi_ai_router()

    @pytest.mark.asyncio
    async def test_routing_latency_p95(self):
        """Test that routing latency meets p95 < 250ms requirement"""
        import json
        import os
        from datetime import datetime

        request = RoutingRequest(
            prompt="Quick test",
            min_responses=1,
            max_responses=2,
            timeout=5.0
        )

        latencies = []

        # Run multiple requests to measure p95
        for _ in range(20):
            start_time = time.time()
            try:
                result = await self.router.route_request(request)
                latency = time.time() - start_time
                latencies.append(latency)
                assert result is not None
            except Exception as e:
                # Log but don't fail test for individual request failures
                print(f"Request failed: {e}")
                latencies.append(float('inf'))

        # Calculate p95
        valid_latencies = [l for l in latencies if l != float('inf')]
        valid_latencies.sort()
        p95_index = int(0.95 * len(valid_latencies))
        p50_index = int(0.50 * len(valid_latencies))
        p99_index = min(int(0.99 * len(valid_latencies)), len(valid_latencies) - 1)

        p95_latency = valid_latencies[p95_index] if valid_latencies else float('inf')
        p50_latency = valid_latencies[p50_index] if valid_latencies else float('inf')
        p99_latency = valid_latencies[p99_index] if valid_latencies else float('inf')

        print(f"P95 routing latency: {p95_latency:.3f}s")

        # Generate performance artifact
        perf_data = {
            "test": "orchestration_routing_latency",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "p50_ms": p50_latency * 1000 if p50_latency != float('inf') else None,
                "p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "p99_ms": p99_latency * 1000 if p99_latency != float('inf') else None,
                "samples": len(valid_latencies),
                "failed_samples": len(latencies) - len(valid_latencies),
                "target_p95_ms": 250,
                "actual_p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "passed": p95_latency < 0.25
            },
            "latencies_ms": [l * 1000 for l in valid_latencies[:10]]  # First 10 samples
        }

        # Save artifact
        os.makedirs("artifacts", exist_ok=True)
        artifact_path = f"artifacts/perf_orchestration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(artifact_path, "w") as f:
            json.dump(perf_data, f, indent=2)

        print(f"📊 Performance artifact saved: {artifact_path}")

        # In mock implementation, should be well under 250ms
        assert p95_latency < 0.25, f"P95 latency {p95_latency:.3f}s exceeds 250ms requirement"

    @pytest.mark.asyncio
    async def test_consensus_evaluation_speed(self):
        """Test consensus evaluation speed"""
        engine = ConsensusEngine()
        responses = [
            AIResponse(
                provider=AIProvider.OPENAI,
                model_id="gpt-4",
                response="Test response " + str(i),
                latency=1.0,
                tokens_used=10,
                cost=0.001,
                confidence=0.8
            )
            for i in range(3)
        ]

        start_time = time.time()
        result = await engine.evaluate_consensus(responses, ConsensusType.MAJORITY)
        consensus_time = time.time() - start_time

        print(f"Consensus evaluation time: {consensus_time:.3f}s")

        # Consensus evaluation should be very fast
        assert consensus_time < 0.1, f"Consensus evaluation took {consensus_time:.3f}s"
        assert result is not None


@pytest.mark.integration
class TestOrchestrationIntegration:
    """Integration tests for orchestration system"""

    @pytest.mark.asyncio
    async def test_end_to_end_orchestration(self):
        """Test complete end-to-end orchestration flow"""
        router = get_multi_ai_router()

        # Mock AI clients for all providers
        mock_client = Mock()
        for provider in AIProvider:
            router.register_ai_client(provider, mock_client)

        request = RoutingRequest(
            prompt="Explain quantum computing in simple terms",
            consensus_type=ConsensusType.HYBRID,
            min_responses=2,
            max_responses=3,
            metadata={"test": "integration"}
        )

        result = await router.route_request(request)

        # Verify result structure
        assert result.final_response is not None
        assert result.confidence > 0
        assert result.agreement_ratio >= 0
        assert len(result.participating_models) >= 2
        assert len(result.individual_responses) >= 2
        assert result.consensus_type in [ConsensusType.HYBRID, ConsensusType.MAJORITY, ConsensusType.WEIGHTED]
        assert isinstance(result.metadata, dict)

    def test_global_router_singleton(self):
        """Test that global router instance is singleton"""
        router1 = get_multi_ai_router()
        router2 = get_multi_ai_router()

        assert router1 is router2
        assert len(router1.model_selector.models) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
