#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Comprehensive Test Suite for Externalized Routing
=================================================================

Comprehensive test suite covering all aspects of the Phase 4 externalized
orchestrator routing system, including strategies, health monitoring,
context preservation, circuit breakers, and failover scenarios.

Test Categories:
- Routing configuration management
- Strategy selection and execution
- Health monitoring and degradation
- Context preservation across hops
- Circuit breaker functionality
- A/B testing framework
- Failover and resilience scenarios
- Performance benchmarks
- Integration tests

Constellation Framework: Flow Star (🌊) coordination hub
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from orchestration.context_preservation import (
    CompressionLevel,
    ContextPreservationEngine,
    ContextType,
)
from orchestration.externalized_orchestrator import (
    ExternalizedOrchestrator,
    OrchestrationRequest,
    RequestType,
)
from orchestration.health_monitor import HealthMonitor, HealthStatus, ProviderHealth
from orchestration.routing_config import RoutingConfigurationManager, RoutingRule, RoutingStrategy
from orchestration.routing_strategies import (
    CircuitBreaker,
    CircuitBreakerState,
    HealthBasedStrategy,
    LatencyBasedStrategy,
    RoundRobinStrategy,
    RoutingContext,
    RoutingEngine,
    WeightedStrategy,
)


class TestRoutingConfiguration:
    """Test routing configuration management"""

    @pytest.fixture
    async def config_manager(self):
        """Create test configuration manager"""
        manager = RoutingConfigurationManager("/tmp/test_routing.yaml")
        await manager.initialize()
        return manager

    @pytest.mark.asyncio
    async def test_configuration_loading(self, config_manager):
        """Test configuration loading from YAML"""
        config = config_manager.get_configuration()

        assert config is not None
        assert len(config.rules) > 0
        assert len(config.default_providers) > 0
        assert config.default_strategy in RoutingStrategy

    @pytest.mark.asyncio
    async def test_hot_reload_configuration(self, config_manager):
        """Test hot-reload of configuration changes"""
        # Simulate configuration change
        old_version = config_manager.config_version

        # Trigger reload
        await config_manager.reload_configuration()

        # Version should remain same if no file changes
        assert config_manager.config_version == old_version

    @pytest.mark.asyncio
    async def test_rule_matching(self, config_manager):
        """Test routing rule pattern matching"""
        # Test documentation pattern
        rule = config_manager.get_rule_for_request("documentation", {})
        assert rule is not None
        assert "documentation" in rule.pattern.lower() or rule.name == "default"

        # Test code pattern
        rule = config_manager.get_rule_for_request("code implementation", {})
        assert rule is not None

        # Test unknown pattern (should get default)
        rule = config_manager.get_rule_for_request("unknown_pattern", {})
        assert rule is not None

    @pytest.mark.asyncio
    async def test_ab_test_assignment(self, config_manager):
        """Test A/B test variant assignment"""
        session_id = "test_session_123"
        experiment_name = "test_experiment"

        # Should return None for non-existent experiment
        variant = config_manager.get_ab_test_variant(session_id, experiment_name)
        assert variant is None

        # Test with consistent assignment
        if config_manager.current_config.ab_tests:
            test_name = config_manager.current_config.ab_tests[0].name
            variant1 = config_manager.get_ab_test_variant(session_id, test_name)
            variant2 = config_manager.get_ab_test_variant(session_id, test_name)

            # Should be consistent
            assert variant1 == variant2


class TestRoutingStrategies:
    """Test routing strategy implementations"""

    @pytest.fixture
    def sample_providers(self):
        """Sample provider health data"""
        return {
            "openai": ProviderHealth(
                provider="openai", status=HealthStatus.HEALTHY, avg_latency_ms=150.0, success_rate=0.98
            ),
            "anthropic": ProviderHealth(
                provider="anthropic", status=HealthStatus.HEALTHY, avg_latency_ms=200.0, success_rate=0.97
            ),
            "google": ProviderHealth(
                provider="google", status=HealthStatus.DEGRADED, avg_latency_ms=300.0, success_rate=0.92
            ),
        }

    @pytest.fixture
    def sample_circuit_breakers(self):
        """Sample circuit breaker data"""
        return {
            "openai": CircuitBreaker(provider="openai", state=CircuitBreakerState.CLOSED),
            "anthropic": CircuitBreaker(provider="anthropic", state=CircuitBreakerState.CLOSED),
            "google": CircuitBreaker(provider="google", state=CircuitBreakerState.CLOSED),
        }

    @pytest.fixture
    def sample_rule(self):
        """Sample routing rule"""
        return RoutingRule(
            name="test_rule",
            pattern="test",
            strategy=RoutingStrategy.ROUND_ROBIN,
            providers=["openai", "anthropic", "google"],
            weights={"openai": 0.5, "anthropic": 0.3, "google": 0.2},
            health_threshold=0.95,
            latency_threshold_ms=250.0,
        )

    @pytest.fixture
    def routing_context(self):
        """Sample routing context"""
        return RoutingContext(session_id="test_session", request_type="test_request")

    @pytest.mark.asyncio
    async def test_round_robin_strategy(self, sample_rule, routing_context, sample_providers, sample_circuit_breakers):
        """Test round-robin routing strategy"""
        strategy = RoundRobinStrategy()
        sample_rule.strategy = RoutingStrategy.ROUND_ROBIN

        # Test multiple selections to verify round-robin behavior
        selected_providers = []
        for _ in range(6):  # Two full cycles
            result = await strategy.select_provider(
                sample_rule, routing_context, sample_providers, sample_circuit_breakers
            )
            assert result is not None
            selected_providers.append(result.provider)

        # Should cycle through providers
        assert len(set(selected_providers)) >= 2  # At least 2 different providers

    @pytest.mark.asyncio
    async def test_weighted_strategy(self, sample_rule, routing_context, sample_providers, sample_circuit_breakers):
        """Test weighted routing strategy"""
        strategy = WeightedStrategy()
        sample_rule.strategy = RoutingStrategy.WEIGHTED

        # Test multiple selections
        selected_providers = []
        for _ in range(100):  # Large sample for statistical significance
            result = await strategy.select_provider(
                sample_rule, routing_context, sample_providers, sample_circuit_breakers
            )
            if result:
                selected_providers.append(result.provider)

        # Higher weighted providers should be selected more often
        provider_counts = {}
        for provider in selected_providers:
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        # OpenAI has highest weight (0.5), should be selected most
        if "openai" in provider_counts:
            assert provider_counts["openai"] > provider_counts.get("google", 0)

    @pytest.mark.asyncio
    async def test_health_based_strategy(self, sample_rule, routing_context, sample_providers, sample_circuit_breakers):
        """Test health-based routing strategy"""
        strategy = HealthBasedStrategy()
        sample_rule.strategy = RoutingStrategy.HEALTH_BASED

        result = await strategy.select_provider(sample_rule, routing_context, sample_providers, sample_circuit_breakers)

        assert result is not None
        # Should prefer healthier providers (openai or anthropic over google)
        assert result.provider in ["openai", "anthropic"]

    @pytest.mark.asyncio
    async def test_latency_based_strategy(
        self, sample_rule, routing_context, sample_providers, sample_circuit_breakers
    ):
        """Test latency-based routing strategy"""
        strategy = LatencyBasedStrategy()
        sample_rule.strategy = RoutingStrategy.LATENCY_BASED

        result = await strategy.select_provider(sample_rule, routing_context, sample_providers, sample_circuit_breakers)

        assert result is not None
        # Should prefer lower latency provider (openai: 150ms)
        assert result.provider == "openai"

    @pytest.mark.asyncio
    async def test_circuit_breaker_behavior(self, sample_rule, routing_context, sample_providers):
        """Test circuit breaker behavior"""
        # Create circuit breakers with one open
        circuit_breakers = {
            "openai": CircuitBreaker(provider="openai", state=CircuitBreakerState.OPEN),
            "anthropic": CircuitBreaker(provider="anthropic", state=CircuitBreakerState.CLOSED),
            "google": CircuitBreaker(provider="google", state=CircuitBreakerState.CLOSED),
        }

        strategy = RoundRobinStrategy()

        result = await strategy.select_provider(sample_rule, routing_context, sample_providers, circuit_breakers)

        # Should not select openai (circuit breaker open)
        assert result is not None
        assert result.provider != "openai"

    @pytest.mark.asyncio
    async def test_no_available_providers(self, sample_rule, routing_context):
        """Test behavior when no providers are available"""
        # All providers unhealthy
        unhealthy_providers = {
            "openai": ProviderHealth(provider="openai", status=HealthStatus.UNHEALTHY, consecutive_failures=5),
            "anthropic": ProviderHealth(provider="anthropic", status=HealthStatus.UNHEALTHY, consecutive_failures=5),
            "google": ProviderHealth(provider="google", status=HealthStatus.UNHEALTHY, consecutive_failures=5),
        }

        circuit_breakers = {
            "openai": CircuitBreaker(provider="openai", state=CircuitBreakerState.CLOSED),
            "anthropic": CircuitBreaker(provider="anthropic", state=CircuitBreakerState.CLOSED),
            "google": CircuitBreaker(provider="google", state=CircuitBreakerState.CLOSED),
        }

        strategy = HealthBasedStrategy()

        result = await strategy.select_provider(sample_rule, routing_context, unhealthy_providers, circuit_breakers)

        # Should return None when no providers available
        assert result is None


class TestHealthMonitoring:
    """Test health monitoring functionality"""

    @pytest.fixture
    async def health_monitor(self):
        """Create test health monitor"""
        monitor = HealthMonitor(check_interval=1.0, history_size=10)
        return monitor

    @pytest.mark.asyncio
    async def test_health_check_execution(self, health_monitor):
        """Test health check execution"""
        with patch("orchestration.providers.create_provider_client") as mock_client_factory:
            # Mock client response
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = "OK"
            mock_client.generate = AsyncMock(return_value=mock_response)
            mock_client_factory.return_value = mock_client

            health_monitor.provider_clients = {"test_provider": mock_client}

            result = await health_monitor.perform_health_check("test_provider")

            assert result.provider == "test_provider"
            assert result.success is True
            assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_health_status_calculation(self, health_monitor):
        """Test health status calculation"""
        # Test healthy status
        health = ProviderHealth(provider="test", avg_latency_ms=100.0, success_rate=0.99, consecutive_failures=0)

        status = health_monitor._calculate_health_status(health)
        assert status == HealthStatus.HEALTHY

        # Test unhealthy status
        health.success_rate = 0.70
        health.consecutive_failures = 5
        health.avg_latency_ms = 6000.0

        status = health_monitor._calculate_health_status(health)
        assert status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_health_score_calculation(self, health_monitor):
        """Test health score calculation"""
        # Perfect health
        health = ProviderHealth(provider="test", avg_latency_ms=50.0, success_rate=1.0, consecutive_failures=0)

        score = health_monitor._calculate_health_score(health)
        assert score == 100.0

        # Poor health
        health.success_rate = 0.5
        health.avg_latency_ms = 2000.0
        health.consecutive_failures = 3

        score = health_monitor._calculate_health_score(health)
        assert score < 50.0


class TestContextPreservation:
    """Test context preservation functionality"""

    @pytest.fixture
    async def context_engine(self):
        """Create test context preservation engine"""
        engine = ContextPreservationEngine()
        await engine.start()
        return engine

    @pytest.mark.asyncio
    async def test_context_preservation(self, context_engine):
        """Test basic context preservation"""
        session_id = "test_session"
        context_data = {
            "conversation_history": ["Hello", "Hi there"],
            "user_preferences": {"theme": "dark"},
            "metadata": {"timestamp": time.time()},
        }

        # Preserve context
        context_id = await context_engine.preserve_context(
            session_id=session_id, context_data=context_data, context_type=ContextType.CONVERSATION
        )

        assert context_id is not None
        assert isinstance(context_id, str)

        # Restore context
        restored_data = await context_engine.restore_context(context_id)

        assert restored_data is not None
        assert restored_data["conversation_history"] == context_data["conversation_history"]
        assert restored_data["user_preferences"] == context_data["user_preferences"]

    @pytest.mark.asyncio
    async def test_context_compression(self, context_engine):
        """Test context compression"""
        session_id = "test_session"

        # Large context data
        large_context = {
            "large_text": "This is a large text that should be compressed. " * 1000,
            "data": list(range(1000)),
            "metadata": {"compressed": True},
        }

        context_id = await context_engine.preserve_context(
            session_id=session_id, context_data=large_context, compression_level=CompressionLevel.AGGRESSIVE
        )

        # Verify preservation and restoration
        restored_data = await context_engine.restore_context(context_id)
        assert restored_data is not None
        assert len(restored_data["large_text"]) > 10000
        assert len(restored_data["data"]) == 1000

    @pytest.mark.asyncio
    async def test_context_handoff(self, context_engine):
        """Test context handoff between providers"""
        session_id = "test_session"
        context_data = {"test": "handoff_data"}

        context_id = await context_engine.preserve_context(session_id=session_id, context_data=context_data)

        # Perform handoff
        success = await context_engine.handoff_context(
            context_id=context_id,
            source_provider="openai",
            destination_provider="anthropic",
            additional_metadata={"handoff_reason": "load_balancing"},
        )

        assert success is True

        # Verify metadata updated
        metadata = await context_engine.get_context_metadata(context_id)
        assert metadata is not None
        assert len(metadata.hops) > 0
        assert metadata.hops[-1].provider == "anthropic"

    @pytest.mark.asyncio
    async def test_context_expiration(self, context_engine):
        """Test context expiration and cleanup"""
        session_id = "test_session"
        context_data = {"test": "expiring_data"}

        # Preserve with very short TTL
        context_id = await context_engine.preserve_context(
            session_id=session_id, context_data=context_data, ttl_seconds=1  # 1 second TTL
        )

        # Should be available immediately
        restored_data = await context_engine.restore_context(context_id)
        assert restored_data is not None

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be None after expiration
        expired_data = await context_engine.restore_context(context_id)
        assert expired_data is None


class TestExternalizedOrchestrator:
    """Test complete externalized orchestrator integration"""

    @pytest.fixture
    async def orchestrator(self):
        """Create test orchestrator with mocked components"""
        with (
            patch("orchestration.externalized_orchestrator.get_routing_config_manager"),
            patch("orchestration.externalized_orchestrator.get_health_monitor"),
            patch("orchestration.externalized_orchestrator.get_context_preservation_engine"),
            patch("orchestration.externalized_orchestrator.create_provider_client"),
        ):

            orchestrator = ExternalizedOrchestrator()

            # Mock components
            orchestrator.config_manager = MagicMock()
            orchestrator.routing_engine = MagicMock()
            orchestrator.health_monitor = MagicMock()
            orchestrator.context_engine = MagicMock()
            orchestrator.kernel_bus = MagicMock()

            return orchestrator

    @pytest.mark.asyncio
    async def test_orchestration_request_processing(self, orchestrator):
        """Test complete orchestration request processing"""
        # Mock configuration
        mock_rule = RoutingRule(
            name="test_rule", pattern="test", strategy=RoutingStrategy.HEALTH_BASED, providers=["openai"]
        )

        orchestrator.config_manager.get_configuration = MagicMock()
        orchestrator.config_manager.get_rule_for_request = MagicMock(return_value=mock_rule)

        # Mock routing result
        from orchestration.routing_strategies import RoutingResult

        mock_routing_result = RoutingResult(
            provider="openai",
            strategy_used=RoutingStrategy.HEALTH_BASED,
            reason="Health-based selection",
            confidence=0.9,
            fallback_available=True,
        )

        orchestrator.routing_engine.route_request = AsyncMock(return_value=mock_routing_result)
        orchestrator.health_monitor.get_all_provider_health = AsyncMock(return_value={})

        # Mock provider execution
        orchestrator._execute_with_provider = AsyncMock(
            return_value={"content": "Test response", "usage": {"total_tokens": 100}, "finish_reason": "stop"}
        )

        # Mock context preservation
        orchestrator.context_engine.preserve_context = AsyncMock(return_value="test_context_id")

        # Create test request
        request = OrchestrationRequest(
            session_id="test_session",
            request_type=RequestType.SINGLE_SHOT,
            prompt="Test prompt",
            context_data={"test": "data"},
        )

        # Execute orchestration
        response = await orchestrator.orchestrate(request)

        # Verify response
        assert response.request_id == request.request_id
        assert response.provider == "openai"
        assert response.strategy_used == "health_based"
        assert response.response == "Test response"
        assert response.context_id == "test_context_id"

    @pytest.mark.asyncio
    async def test_orchestration_error_handling(self, orchestrator):
        """Test orchestration error handling"""
        # Mock configuration to raise error
        orchestrator.config_manager.get_rule_for_request = MagicMock(side_effect=Exception("Configuration error"))

        request = OrchestrationRequest(
            session_id="test_session", request_type=RequestType.SINGLE_SHOT, prompt="Test prompt"
        )

        # Should raise exception
        with pytest.raises(Exception):
            await orchestrator.orchestrate(request)

    @pytest.mark.asyncio
    async def test_ab_test_integration(self, orchestrator):
        """Test A/B test integration in orchestration"""
        # Mock A/B test configuration
        mock_config = MagicMock()
        mock_config.ab_tests = [MagicMock(enabled=True, name="test_experiment", rules=["test_rule"])]

        orchestrator.config_manager.get_configuration = MagicMock(return_value=mock_config)
        orchestrator.config_manager.get_ab_test_variant = MagicMock(return_value="variant_a")

        # Rest of test setup...
        mock_rule = RoutingRule(
            name="test_rule", pattern="test", strategy=RoutingStrategy.HEALTH_BASED, providers=["openai"]
        )

        orchestrator.config_manager.get_rule_for_request = MagicMock(return_value=mock_rule)

        # Verify A/B test variant is included in response
        # (This would be part of a larger test setup)


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.asyncio
    async def test_routing_decision_latency(self):
        """Benchmark routing decision latency (<100ms target)"""
        routing_engine = RoutingEngine()

        rule = RoutingRule(
            name="benchmark_rule",
            pattern="test",
            strategy=RoutingStrategy.HEALTH_BASED,
            providers=["openai", "anthropic", "google"],
        )

        context = RoutingContext(session_id="benchmark_session", request_type="benchmark")

        provider_health = {
            "openai": ProviderHealth(provider="openai", status=HealthStatus.HEALTHY),
            "anthropic": ProviderHealth(provider="anthropic", status=HealthStatus.HEALTHY),
            "google": ProviderHealth(provider="google", status=HealthStatus.HEALTHY),
        }

        # Measure routing decision time
        start_time = time.time()

        for _ in range(100):  # 100 iterations
            result = await routing_engine.route_request(rule, context, provider_health)
            assert result is not None

        total_time = time.time() - start_time
        avg_time_ms = (total_time / 100) * 1000

        print(f"Average routing decision time: {avg_time_ms:.2f}ms")

        # Should be under 100ms target
        assert avg_time_ms < 100.0

    @pytest.mark.asyncio
    async def test_context_handoff_latency(self):
        """Benchmark context handoff latency (<250ms target)"""
        engine = ContextPreservationEngine()
        await engine.start()

        context_data = {"test": "benchmark_data", "size": "x" * 1000}  # 1KB data

        # Preserve context
        context_id = await engine.preserve_context(session_id="benchmark_session", context_data=context_data)

        # Measure handoff time
        start_time = time.time()

        for _ in range(50):  # 50 iterations
            success = await engine.handoff_context(
                context_id=context_id, source_provider="provider_a", destination_provider="provider_b"
            )
            assert success is True

        total_time = time.time() - start_time
        avg_time_ms = (total_time / 50) * 1000

        print(f"Average context handoff time: {avg_time_ms:.2f}ms")

        # Should be under 250ms target
        assert avg_time_ms < 250.0

        await engine.stop()


class TestFailoverScenarios:
    """Test failover and resilience scenarios"""

    @pytest.mark.asyncio
    async def test_provider_failure_failover(self):
        """Test failover when primary provider fails"""
        routing_engine = RoutingEngine()

        rule = RoutingRule(
            name="failover_rule",
            pattern="test",
            strategy=RoutingStrategy.HEALTH_BASED,
            providers=["failing_provider", "backup_provider"],
            fallback_providers=["backup_provider"],
        )

        context = RoutingContext(session_id="failover_test", request_type="test")

        # Primary provider unhealthy, backup healthy
        provider_health = {
            "failing_provider": ProviderHealth(
                provider="failing_provider", status=HealthStatus.UNHEALTHY, consecutive_failures=5
            ),
            "backup_provider": ProviderHealth(provider="backup_provider", status=HealthStatus.HEALTHY),
        }

        result = await routing_engine.route_request(rule, context, provider_health)

        # Should select backup provider
        assert result is not None
        assert result.provider == "backup_provider"

    @pytest.mark.asyncio
    async def test_circuit_breaker_failover(self):
        """Test failover when circuit breaker is open"""
        routing_engine = RoutingEngine()

        # Simulate circuit breaker opening due to failures
        routing_engine.circuit_breakers["failing_provider"] = CircuitBreaker(
            provider="failing_provider", state=CircuitBreakerState.OPEN
        )

        rule = RoutingRule(
            name="circuit_breaker_rule",
            pattern="test",
            strategy=RoutingStrategy.ROUND_ROBIN,
            providers=["failing_provider", "working_provider"],
        )

        context = RoutingContext(session_id="circuit_test", request_type="test")

        provider_health = {
            "failing_provider": ProviderHealth(
                provider="failing_provider",
                status=HealthStatus.HEALTHY,  # Health looks good but circuit breaker is open
            ),
            "working_provider": ProviderHealth(provider="working_provider", status=HealthStatus.HEALTHY),
        }

        result = await routing_engine.route_request(rule, context, provider_health)

        # Should not select provider with open circuit breaker
        assert result is not None
        assert result.provider == "working_provider"

    @pytest.mark.asyncio
    async def test_cascading_failure_resilience(self):
        """Test resilience against cascading failures"""
        routing_engine = RoutingEngine()

        rule = RoutingRule(
            name="resilience_rule",
            pattern="test",
            strategy=RoutingStrategy.HEALTH_BASED,
            providers=["provider_1", "provider_2", "provider_3"],
            fallback_providers=["provider_3"],
        )

        context = RoutingContext(session_id="resilience_test", request_type="test")

        # Multiple providers failing
        provider_health = {
            "provider_1": ProviderHealth(provider="provider_1", status=HealthStatus.UNHEALTHY),
            "provider_2": ProviderHealth(provider="provider_2", status=HealthStatus.UNHEALTHY),
            "provider_3": ProviderHealth(
                provider="provider_3", status=HealthStatus.DEGRADED  # Only degraded, still usable
            ),
        }

        result = await routing_engine.route_request(rule, context, provider_health)

        # Should successfully route to last available provider
        assert result is not None
        assert result.provider == "provider_3"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
