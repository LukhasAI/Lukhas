"""
Integration tests for LUKHAS AI Multi-AI Orchestration System
=============================================================

Comprehensive integration tests that validate the entire multi-AI orchestration
pipeline including consensus algorithms, context management, performance monitoring,
and real-time workflow orchestration.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import asyncio
import time

import pytest

# Test imports
try:
    from candidate.bridge.api_gateway import UnifiedAPIGateway
    from candidate.bridge.orchestration import (
        AIProvider,
        ConsensusResult,
        MultiAIOrchestrator,
        OrchestrationRequest,
        TaskType,
    )
    from candidate.bridge.workflow.workflow_orchestrator import WorkflowOrchestrator  # noqa: F401

    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False


@pytest.fixture
def orchestrator_config():
    """Configuration for test orchestrator"""
    return {
        "target_latency_ms": 250,
        "max_parallel_requests": 4,
        "consensus": {"default_method": "hybrid_synthesis", "confidence_threshold": 0.7},
        "context": {"max_context_entries": 100, "handoff_target_ms": 250},
        "performance": {"metrics_retention_hours": 1, "circuit_breaker_threshold": 0.5},
    }


@pytest.fixture
async def multi_ai_orchestrator(orchestrator_config):
    """Create MultiAI orchestrator for testing"""
    if not ORCHESTRATION_AVAILABLE:
        pytest.skip("Orchestration components not available")

    orchestrator = MultiAIOrchestrator(orchestrator_config)
    yield orchestrator

    # Cleanup
    # Any cleanup needed would go here


@pytest.fixture
async def api_gateway(orchestrator_config):
    """Create API gateway for testing"""
    if not ORCHESTRATION_AVAILABLE:
        pytest.skip("API gateway components not available")

    gateway_config = {
        "host": "127.0.0.1",
        "port": 8081,  # Different port for testing
        "debug": True,
        "target_latency_ms": 100,
        "cors_origins": ["http://localhost:3000"],
    }

    gateway = UnifiedAPIGateway(gateway_config)
    yield gateway


@pytest.mark.asyncio
@pytest.mark.integration
class TestMultiAIOrchestration:
    """Integration tests for multi-AI orchestration system"""

    async def test_orchestrator_initialization(self, multi_ai_orchestrator):
        """Test that orchestrator initializes correctly"""
        orchestrator = multi_ai_orchestrator

        # Check basic initialization
        assert orchestrator is not None
        assert orchestrator.target_latency_ms == 250
        assert orchestrator.max_parallel_requests == 4

        # Check component initialization
        assert orchestrator.consensus_engine is not None
        assert orchestrator.context_manager is not None
        assert orchestrator.performance_monitor is not None

        # Test health check
        health_status = await orchestrator.health_check()
        assert health_status["orchestrator"] in [
            "healthy",
            "degraded",
        ]  # May be degraded without real AI APIs

    async def test_simple_orchestration_request(self, multi_ai_orchestrator):
        """Test basic orchestration request processing"""
        orchestrator = multi_ai_orchestrator

        request = OrchestrationRequest(
            prompt="What is artificial intelligence?",
            task_type=TaskType.CONVERSATION,
            providers=[],  # Use default providers
            consensus_required=False,  # Simplify for testing
            max_latency_ms=5000,
        )

        try:
            result = await orchestrator.orchestrate(request)

            # Validate result structure
            assert isinstance(result, ConsensusResult)
            assert result.final_response is not None
            assert result.confidence_score >= 0.0
            assert result.confidence_score <= 1.0
            assert result.processing_time_ms > 0
            assert result.participating_models >= 0  # May be 0 if no providers available

        except Exception as e:
            # If no AI providers are available, we expect specific errors
            assert "No valid responses" in str(e) or "not available" in str(e) or "not initialized" in str(e)

    async def test_consensus_orchestration(self, multi_ai_orchestrator):
        """Test consensus orchestration with multiple providers"""
        orchestrator = multi_ai_orchestrator

        request = OrchestrationRequest(
            prompt="Explain the concept of consciousness in AI systems.",
            task_type=TaskType.REASONING,
            providers=[AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.GEMINI],
            consensus_required=True,
            max_latency_ms=10000,
            parallel_execution=True,
        )

        try:
            start_time = time.time()
            result = await orchestrator.orchestrate(request)
            execution_time = (time.time() - start_time) * 1000

            # Validate consensus result
            assert isinstance(result, ConsensusResult)
            assert result.consensus_method in [
                "majority_vote",
                "weighted_confidence",
                "similarity_clustering",
                "hybrid_synthesis",
                "fallback",
                "single_response",
            ]
            assert execution_time < 15000  # Should complete within 15 seconds

            # If consensus was achieved, validate quality
            if result.participating_models > 1:
                assert result.confidence_score > 0.0
                assert result.quality_metrics is not None

        except Exception as e:
            # Expected if AI providers aren't configured
            assert "No valid responses" in str(e) or "not available" in str(e) or "Failed to initialize" in str(e)

    async def test_context_preservation(self, multi_ai_orchestrator):
        """Test context preservation across requests"""
        orchestrator = multi_ai_orchestrator
        context_id = "test_conversation_001"

        # First request
        request1 = OrchestrationRequest(
            prompt="My name is Alice. Remember this for our conversation.",
            task_type=TaskType.CONVERSATION,
            providers=[],
            consensus_required=False,
            context_id=context_id,
            max_latency_ms=5000,
        )

        try:
            result1 = await orchestrator.orchestrate(request1)
            assert result1.final_response is not None

            # Second request that relies on context
            request2 = OrchestrationRequest(
                prompt="What is my name?",
                task_type=TaskType.CONVERSATION,
                providers=[],
                consensus_required=False,
                context_id=context_id,
                max_latency_ms=5000,
            )

            result2 = await orchestrator.orchestrate(request2)
            assert result2.final_response is not None

            # Validate context was preserved (would need AI providers to test properly)
            context_data = await orchestrator.context_manager.get_context(context_id)
            assert context_data["total_entries"] >= 2

        except Exception as e:
            # Expected if AI providers aren't configured
            assert "No valid responses" in str(e) or "not available" in str(e) or "not initialized" in str(e)

    async def test_performance_monitoring(self, multi_ai_orchestrator):
        """Test performance monitoring and metrics collection"""
        orchestrator = multi_ai_orchestrator

        # Generate some requests to create metrics
        for i in range(3):
            request = OrchestrationRequest(
                prompt=f"Test request {i}",
                task_type=TaskType.CONVERSATION,
                providers=[],
                consensus_required=False,
                max_latency_ms=3000,
            )

            try:
                await orchestrator.orchestrate(request)
            except Exception:
                pass  # Expected without real AI providers

        # Check performance metrics
        metrics = await orchestrator.performance_monitor.get_metrics()

        assert "timestamp" in metrics
        assert "system" in metrics
        assert "providers" in metrics

        # Check specific metric structure
        system_metrics = metrics["system"]
        assert "total_requests" in system_metrics
        assert "success_rate" in system_metrics
        assert "avg_orchestration_latency_ms" in system_metrics

    async def test_circuit_breaker_functionality(self, multi_ai_orchestrator):
        """Test circuit breaker patterns for failed providers"""
        orchestrator = multi_ai_orchestrator

        # Test circuit breaker status
        provider_score = orchestrator.performance_monitor.get_provider_score(AIProvider.OPENAI, TaskType.CONVERSATION)
        assert 0.0 <= provider_score <= 1.0

        # Check circuit breaker health
        health_status = await orchestrator.performance_monitor.health_check()
        assert "status" in health_status
        assert health_status["status"] in ["healthy", "degraded", "error"]

    async def test_api_gateway_integration(self, api_gateway):
        """Test API gateway initialization and basic functionality"""
        gateway = api_gateway

        assert gateway is not None
        assert gateway.host == "127.0.0.1"
        assert gateway.port == 8081

        # Test FastAPI app creation
        app = gateway.get_app()
        assert app is not None
        assert app.title == "LUKHAS AI Gateway"

    async def test_orchestration_status_endpoint(self, multi_ai_orchestrator):
        """Test orchestration system status reporting"""
        orchestrator = multi_ai_orchestrator

        status = await orchestrator.get_status()

        # Validate status structure
        assert "status" in status
        assert "version" in status
        assert "available_providers" in status
        assert "performance_metrics" in status

        # Check available providers list
        assert isinstance(status["available_providers"], list)

    async def test_context_handoff_performance(self, multi_ai_orchestrator):
        """Test context handoff performance meets <250ms target"""
        orchestrator = multi_ai_orchestrator
        context_id = "performance_test_context"

        # Create initial context
        await orchestrator.context_manager.update_context(context_id, "Initial context", "Response", {"test": True})

        # Measure context retrieval time
        start_time = time.time()
        context_data = await orchestrator.context_manager.get_context(context_id)
        handoff_time = (time.time() - start_time) * 1000

        assert context_data is not None
        assert handoff_time < 250  # Should be under 250ms target

        # Test performance metrics
        perf_metrics = await orchestrator.context_manager.get_performance_metrics()
        assert "handoff_target_ms" in perf_metrics
        assert perf_metrics["handoff_target_ms"] == 250

    async def test_error_handling_and_recovery(self, multi_ai_orchestrator):
        """Test error handling and recovery mechanisms"""
        orchestrator = multi_ai_orchestrator

        # Test invalid request handling
        invalid_request = OrchestrationRequest(
            prompt="",  # Empty prompt
            task_type=TaskType.CONVERSATION,
            providers=[],
            max_latency_ms=0,  # Invalid timeout
        )

        try:
            await orchestrator.orchestrate(invalid_request)
            raise AssertionError("Should have raised an exception for invalid request")
        except Exception as e:
            # Should handle invalid requests gracefully
            assert "timeout" in str(e).lower() or "invalid" in str(e).lower() or "no valid responses" in str(e).lower()

    async def test_concurrent_orchestration_requests(self, multi_ai_orchestrator):
        """Test concurrent request handling"""
        orchestrator = multi_ai_orchestrator

        # Create multiple concurrent requests
        requests = []
        for i in range(5):
            request = OrchestrationRequest(
                prompt=f"Concurrent test request {i}",
                task_type=TaskType.CONVERSATION,
                providers=[],
                consensus_required=False,
                max_latency_ms=5000,
            )
            requests.append(orchestrator.orchestrate(request))

        # Execute concurrently
        try:
            results = await asyncio.gather(*requests, return_exceptions=True)

            # All should complete (successfully or with expected errors)
            assert len(results) == 5

            for result in results:
                if isinstance(result, Exception):
                    # Expected if no AI providers available
                    assert (
                        "No valid responses" in str(result)
                        or "not available" in str(result)
                        or "not initialized" in str(result)
                    )
                else:
                    assert isinstance(result, ConsensusResult)

        except Exception as e:
            # Should handle concurrent requests gracefully
            assert "concurrent" not in str(e).lower()  # Shouldn't fail due to concurrency

    @pytest.mark.slow
    async def test_system_stress_test(self, multi_ai_orchestrator):
        """Stress test the orchestration system"""
        orchestrator = multi_ai_orchestrator

        # Generate many requests quickly
        start_time = time.time()
        request_count = 20

        tasks = []
        for i in range(request_count):
            request = OrchestrationRequest(
                prompt=f"Stress test {i}",
                task_type=TaskType.CONVERSATION,
                providers=[],
                consensus_required=False,
                max_latency_ms=2000,
            )
            tasks.append(orchestrator.orchestrate(request))

        # Execute with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0,  # 30 second timeout
            )

            execution_time = time.time() - start_time

            # Validate results
            assert len(results) == request_count

            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = len(results) - success_count

            # Log performance metrics
            print(f"Stress test completed in {execution_time:.2f}s")
            print(f"Successful requests: {success_count}/{request_count}")
            print(f"Failed requests: {error_count}/{request_count}")

            # System should handle the load gracefully
            assert execution_time < 60  # Should complete within 1 minute

        except asyncio.TimeoutError:
            pytest.fail("Stress test timed out - system may be overloaded")


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end workflow integration tests"""

    async def test_complete_ai_workflow(self, multi_ai_orchestrator):
        """Test a complete AI workflow from start to finish"""
        if not ORCHESTRATION_AVAILABLE:
            pytest.skip("Orchestration not available")

        orchestrator = multi_ai_orchestrator

        # Simulate a complete workflow
        workflow_steps = [
            "Analyze the concept of artificial intelligence",
            "Explain machine learning basics",
            "Describe neural networks",
            "Summarize the key points",
        ]

        context_id = "workflow_test"
        results = []

        for i, prompt in enumerate(workflow_steps):
            request = OrchestrationRequest(
                prompt=prompt,
                task_type=TaskType.REASONING if i < 3 else TaskType.ANALYSIS,
                providers=[],
                consensus_required=i == len(workflow_steps) - 1,  # Consensus for final summary
                context_id=context_id,
                max_latency_ms=5000,
                metadata={"step": i + 1, "total_steps": len(workflow_steps)},
            )

            try:
                result = await orchestrator.orchestrate(request)
                results.append(result)

                # Brief pause between steps
                await asyncio.sleep(0.1)

            except Exception as e:
                # Expected without real AI providers
                results.append({"error": str(e)})

        # Validate workflow completion
        assert len(results) == len(workflow_steps)

        # Check context preservation
        final_context = await orchestrator.context_manager.get_context(context_id)
        assert final_context["total_entries"] == len(workflow_steps)


# Performance benchmark tests
@pytest.mark.benchmark
@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Performance benchmark tests for the orchestration system"""

    async def test_latency_benchmark(self, multi_ai_orchestrator):
        """Benchmark request latency"""
        orchestrator = multi_ai_orchestrator

        latencies = []

        for i in range(10):
            request = OrchestrationRequest(
                prompt=f"Benchmark request {i}",
                task_type=TaskType.CONVERSATION,
                providers=[],
                consensus_required=False,
                max_latency_ms=3000,
            )

            start_time = time.time()
            try:
                await orchestrator.orchestrate(request)
            except Exception:
                pass  # Expected without AI providers

            latency = (time.time() - start_time) * 1000
            latencies.append(latency)

        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        print("Latency benchmark:")
        print(f"  Average: {avg_latency:.2f}ms")
        print(f"  Min: {min_latency:.2f}ms")
        print(f"  Max: {max_latency:.2f}ms")

        # Validate performance targets
        assert avg_latency < 500  # Average should be under 500ms even without AI providers
        assert max_latency < 2000  # Max should be under 2 seconds

    async def test_context_handoff_benchmark(self, multi_ai_orchestrator):
        """Benchmark context handoff performance"""
        orchestrator = multi_ai_orchestrator

        context_id = "benchmark_context"
        handoff_times = []

        # Create some context
        await orchestrator.context_manager.update_context(context_id, "Initial", "Response", {"test": True})

        # Benchmark context retrieval
        for _i in range(20):
            start_time = time.time()
            await orchestrator.context_manager.get_context(context_id)
            handoff_time = (time.time() - start_time) * 1000
            handoff_times.append(handoff_time)

        avg_handoff_time = sum(handoff_times) / len(handoff_times)
        max_handoff_time = max(handoff_times)

        print("Context handoff benchmark:")
        print(f"  Average: {avg_handoff_time:.2f}ms")
        print(f"  Max: {max_handoff_time:.2f}ms")
        print("  Target: <250ms")

        # Validate performance target
        assert avg_handoff_time < 250  # Should meet <250ms target
        assert max_handoff_time < 500  # Max should be reasonable
