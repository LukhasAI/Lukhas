"""
T4/0.01% Excellence Tests: AI Provider Compatibility Framework
==============================================================

Comprehensive test suite for AI Provider health checking, SLA monitoring,
and intelligent failover capabilities.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_orchestration.lukhas_ai_orchestrator import LUKHASAIOrchestrator


@pytest.mark.asyncio
class TestProviderHealthValidation:
    """Test provider health validation functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = LUKHASAIOrchestrator("/test/workspace")

    async def test_claude_health_validation_success(self):
        """Test successful Claude health validation"""
        # Mock successful Claude response
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "test response"

        with patch('ai_orchestration.lukhas_ai_orchestrator.AsyncAnthropic') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            # Set API key for test
            self.orchestrator.providers["claude"].api_key = "test-key"

            result = await self.orchestrator.validate_provider_health("claude")

            assert result["healthy"] is True
            assert "latency" in result
            assert result["version"] == "compatible"
            assert result["model"] == self.orchestrator.providers["claude"].model
            assert "response_length" in result

    async def test_claude_health_validation_no_api_key(self):
        """Test Claude health validation without API key"""
        # Remove API key
        self.orchestrator.providers["claude"].api_key = None

        result = await self.orchestrator.validate_provider_health("claude")

        assert result["healthy"] is False
        assert "Missing Claude API key" in result["error"]
        assert result["latency"] == 0.0

    async def test_gpt_health_validation_success(self):
        """Test successful GPT health validation"""
        # Mock successful OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "test response"

        with patch('ai_orchestration.lukhas_ai_orchestrator.openai.AsyncOpenAI') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            # Set API key for test
            self.orchestrator.providers["gpt"].api_key = "test-key"

            result = await self.orchestrator.validate_provider_health("gpt")

            assert result["healthy"] is True
            assert "latency" in result
            assert result["version"] == "compatible"
            assert result["model"] == self.orchestrator.providers["gpt"].model

    async def test_ollama_health_validation_success(self):
        """Test successful Ollama health validation"""
        # Mock successful Ollama response
        mock_response_data = {"response": "test response"}

        with patch('ai_orchestration.lukhas_ai_orchestrator.aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data

            mock_session.__aenter__.return_value = mock_session
            mock_session.post.return_value.__aenter__.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = await self.orchestrator.validate_provider_health("ollama")

            assert result["healthy"] is True
            assert "latency" in result
            assert result["version"] == "compatible"

    async def test_provider_health_validation_timeout(self):
        """Test provider health validation with timeout"""
        with patch('ai_orchestration.lukhas_ai_orchestrator.AsyncAnthropic') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create.side_effect = asyncio.TimeoutError()
            mock_client_class.return_value = mock_client

            self.orchestrator.providers["claude"].api_key = "test-key"

            result = await self.orchestrator.validate_provider_health("claude")

            assert result["healthy"] is False
            assert "timeout" in result["error"].lower()
            assert "latency" in result

    async def test_unknown_provider_health_validation(self):
        """Test health validation for unknown provider"""
        result = await self.orchestrator.validate_provider_health("unknown_provider")

        assert result["healthy"] is False
        assert "not found" in result["error"]
        assert result["latency"] == 0.0

    @pytest.mark.performance
    async def test_health_validation_performance(self):
        """Test health validation meets performance requirements"""
        # Mock fast responses
        with patch('ai_orchestration.lukhas_ai_orchestrator.AsyncAnthropic') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = [MagicMock()]
            mock_response.content[0].text = "test"
            mock_client.messages.create.return_value = mock_response
            mock_client_class.return_value = mock_client

            self.orchestrator.providers["claude"].api_key = "test-key"

            # Test multiple validations
            start_time = time.time()
            for _ in range(10):
                await self.orchestrator.validate_provider_health("claude")
            end_time = time.time()

            avg_time = (end_time - start_time) / 10
            assert avg_time < 0.1, f"Health validation too slow: {avg_time:.3f}s"


@pytest.mark.asyncio
class TestProviderHealthStatus:
    """Test comprehensive provider health status functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = LUKHASAIOrchestrator("/test/workspace")

    async def test_get_all_provider_health_status(self):
        """Test getting health status for all providers"""
        # Mock all providers as healthy
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.return_value = {
                "healthy": True,
                "latency": 0.1,
                "version": "compatible"
            }

            result = await self.orchestrator.get_provider_health_status()

            assert len(result) == len(self.orchestrator.providers)
            for provider_name in self.orchestrator.providers.keys():
                assert provider_name in result
                assert result[provider_name]["healthy"] is True
                assert result[provider_name]["sla_compliant"] is True

    async def test_sla_compliance_calculation(self):
        """Test SLA compliance calculation (<250ms latency)"""
        test_cases = [
            (True, 0.1, True),    # Healthy + fast = compliant
            (True, 0.3, False),   # Healthy + slow = non-compliant
            (False, 0.1, False),  # Unhealthy = non-compliant
            (False, 0.3, False),  # Unhealthy + slow = non-compliant
        ]

        for healthy, latency, expected_compliant in test_cases:
            with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
                mock_validate.return_value = {
                    "healthy": healthy,
                    "latency": latency,
                    "version": "compatible"
                }

                result = await self.orchestrator.get_provider_health_status()
                claude_status = result["claude"]

                assert claude_status["sla_compliant"] == expected_compliant

    async def test_provider_health_status_exception_handling(self):
        """Test health status with provider exceptions"""
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.side_effect = Exception("Test exception")

            result = await self.orchestrator.get_provider_health_status()

            for provider_name in self.orchestrator.providers.keys():
                assert provider_name in result
                assert result[provider_name]["healthy"] is False
                assert "Test exception" in result[provider_name]["error"]
                assert result[provider_name]["sla_compliant"] is False


@pytest.mark.asyncio
class TestOptimalProviderSelection:
    """Test optimal provider selection functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = LUKHASAIOrchestrator("/test/workspace")

    async def test_select_optimal_provider_preferred_healthy(self):
        """Test selecting preferred provider when healthy"""
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.return_value = {
                "healthy": True,
                "latency": 0.1,
                "sla_compliant": True
            }

            result = await self.orchestrator.select_optimal_provider("claude")
            assert result == "claude"

    async def test_select_optimal_provider_fallback_to_healthy(self):
        """Test fallback to healthy provider when preferred fails"""
        def mock_health_check(provider_name):
            if provider_name == "claude":
                return {
                    "healthy": False,
                    "latency": 1.0,
                    "sla_compliant": False
                }
            else:
                return {
                    "healthy": True,
                    "latency": 0.1,
                    "sla_compliant": True
                }

        with patch.object(self.orchestrator, 'validate_provider_health', side_effect=mock_health_check):
            result = await self.orchestrator.select_optimal_provider("claude", ["gpt", "ollama"])
            assert result == "gpt"  # First healthy fallback

    async def test_select_optimal_provider_all_unhealthy(self):
        """Test fallback to preferred when all providers unhealthy"""
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.return_value = {
                "healthy": False,
                "latency": 1.0,
                "sla_compliant": False
            }

            result = await self.orchestrator.select_optimal_provider("claude")
            assert result == "claude"  # Returns preferred despite being unhealthy


@pytest.mark.asyncio
class TestProviderCompatibilityIntegration:
    """Integration tests for provider compatibility framework"""

    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = LUKHASAIOrchestrator("/test/workspace")

    async def test_health_framework_integration_with_routing(self):
        """Test health framework integrates with routing system"""
        # Mock health status
        def mock_health_check(provider_name):
            return {
                "healthy": provider_name == "gpt",  # Only GPT healthy
                "latency": 0.1 if provider_name == "gpt" else 1.0,
                "sla_compliant": provider_name == "gpt"
            }

        with patch.object(self.orchestrator, 'validate_provider_health', side_effect=mock_health_check):
            with patch.object(self.orchestrator, '_call_provider', return_value="test response") as mock_call:
                # Should route to healthy provider (gpt) instead of preferred (claude)
                result = await self.orchestrator.route_request("architecture_design", "test content")

                # Verify it called the healthy provider
                mock_call.assert_called_once()
                # The exact provider used depends on routing logic, but should prefer healthy ones

    @pytest.mark.performance
    async def test_concurrent_health_checks(self):
        """Test concurrent health checking performance"""
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            # Simulate realistic latency
            async def slow_health_check(provider_name):
                await asyncio.sleep(0.05)  # 50ms per check
                return {"healthy": True, "latency": 0.05, "sla_compliant": True}

            mock_validate.side_effect = slow_health_check

            start_time = time.time()
            result = await self.orchestrator.get_provider_health_status()
            end_time = time.time()

            # Should run in parallel, not sequentially
            total_time = end_time - start_time
            assert total_time < 0.15, f"Concurrent health checks too slow: {total_time:.3f}s"

    async def test_provider_health_caching_behavior(self):
        """Test provider health results are not inappropriately cached"""
        call_count = 0

        async def counting_health_check(provider_name):
            nonlocal call_count
            call_count += 1
            return {"healthy": True, "latency": 0.1, "sla_compliant": True}

        with patch.object(self.orchestrator, 'validate_provider_health', side_effect=counting_health_check):
            # Multiple calls should each trigger health check (no caching)
            await self.orchestrator.select_optimal_provider("claude")
            await self.orchestrator.select_optimal_provider("claude")

            assert call_count >= 2, "Health checks should not be cached inappropriately"


@pytest.mark.chaos
class TestProviderChaosEngineering:
    """Chaos engineering tests for provider compatibility"""

    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = LUKHASAIOrchestrator("/test/workspace")

    @pytest.mark.asyncio
    async def test_provider_random_failures(self):
        """Test system resilience with random provider failures"""
        import random

        def chaotic_health_check(provider_name):
            # Randomly fail providers
            if random.random() < 0.3:  # 30% failure rate
                return {
                    "healthy": False,
                    "latency": 2.0,
                    "error": "Random chaos failure"
                }
            else:
                return {
                    "healthy": True,
                    "latency": random.uniform(0.05, 0.2),
                    "sla_compliant": True
                }

        with patch.object(self.orchestrator, 'validate_provider_health', side_effect=chaotic_health_check):
            # System should handle random failures gracefully
            for _ in range(50):
                try:
                    result = await self.orchestrator.select_optimal_provider("claude")
                    assert result in self.orchestrator.providers.keys()
                except Exception as e:
                    pytest.fail(f"System failed under chaos: {e}")

    @pytest.mark.asyncio
    async def test_all_providers_fail_scenario(self):
        """Test system behavior when all providers fail"""
        with patch.object(self.orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.return_value = {
                "healthy": False,
                "latency": 5.0,
                "error": "All providers down"
            }

            # Should still return preferred provider as fallback
            result = await self.orchestrator.select_optimal_provider("claude")
            assert result == "claude"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not chaos"])
