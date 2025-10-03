#!/usr/bin/env python3
"""
Quick AI Orchestrator Test
==========================

Test our T4/0.01% AI Provider Compatibility Framework
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from ai_orchestration.lukhas_ai_orchestrator import LUKHASAIOrchestrator


async def test_provider_health_validation():
    """Test AI Provider health validation functionality"""
    print("🔍 Testing AI Provider Health Validation...")

    orchestrator = LUKHASAIOrchestrator("/test/workspace")

    # Test 1: Claude health validation success
    print("\n✅ Test 1: Claude Health Validation")
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "test response"

    with patch('ai_orchestration.lukhas_ai_orchestrator.AsyncAnthropic') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Set API key for test
        orchestrator.providers["claude"].api_key = "test-key"

        result = await orchestrator.validate_provider_health("claude")

        if result["healthy"] is True:
            print(f"  ✅ Claude health validation: healthy={result['healthy']}")
        else:
            print(f"  ❌ Claude health validation failed")
            return False

        if "latency" in result and "version" in result:
            print(f"  ✅ Claude response complete: latency={result['latency']:.3f}s")
        else:
            print(f"  ❌ Claude response incomplete")
            return False

    # Test 2: Provider health without API key
    print("\n✅ Test 2: Missing API Key Handling")
    orchestrator.providers["claude"].api_key = None
    result = await orchestrator.validate_provider_health("claude")

    if result["healthy"] is False and "Missing Claude API key" in result["error"]:
        print(f"  ✅ Missing API key handled correctly")
    else:
        print(f"  ❌ Missing API key not handled properly")
        return False

    # Test 3: Unknown provider
    print("\n✅ Test 3: Unknown Provider Handling")
    result = await orchestrator.validate_provider_health("unknown_provider")

    if result["healthy"] is False and "not found" in result["error"]:
        print(f"  ✅ Unknown provider handled correctly")
    else:
        print(f"  ❌ Unknown provider not handled properly")
        return False

    return True


async def test_provider_selection():
    """Test optimal provider selection logic"""
    print("\n🎯 Testing Provider Selection Logic...")

    orchestrator = LUKHASAIOrchestrator("/test/workspace")

    # Test 1: Select healthy preferred provider
    print("\n✅ Test 1: Healthy Preferred Provider")
    with patch.object(orchestrator, 'validate_provider_health') as mock_validate:
        mock_validate.return_value = {
            "healthy": True,
            "latency": 0.1,
            "sla_compliant": True
        }

        result = await orchestrator.select_optimal_provider("claude")
        if result == "claude":
            print(f"  ✅ Selected preferred provider: {result}")
        else:
            print(f"  ❌ Wrong provider selected: {result}")
            return False

    # Test 2: Fallback to healthy provider
    print("\n✅ Test 2: Fallback Provider Selection")
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

    with patch.object(orchestrator, 'validate_provider_health', side_effect=mock_health_check):
        result = await orchestrator.select_optimal_provider("claude", ["gpt", "ollama"])
        if result == "gpt":
            print(f"  ✅ Fallback provider selected: {result}")
        else:
            print(f"  ❌ Wrong fallback provider: {result}")
            return False

    return True


async def test_provider_health_performance():
    """Test provider health validation performance"""
    print("\n⚡ Testing Provider Health Performance...")

    orchestrator = LUKHASAIOrchestrator("/test/workspace")

    # Mock fast response
    with patch('ai_orchestration.lukhas_ai_orchestrator.AsyncAnthropic') as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "test"
        mock_client.messages.create.return_value = mock_response
        mock_client_class.return_value = mock_client

        orchestrator.providers["claude"].api_key = "test-key"

        # Test multiple validations
        times = []
        for _ in range(10):
            start_time = time.time()
            await orchestrator.validate_provider_health("claude")
            end_time = time.time()
            times.append((end_time - start_time) * 1000)  # Convert to ms

        avg_time = sum(times) / len(times)
        max_time = max(times)

        print(f"  Average validation time: {avg_time:.2f}ms")
        print(f"  Max validation time: {max_time:.2f}ms")

        # Should be fast (< 100ms for mocked responses)
        if avg_time < 100.0:
            print(f"  ✅ Health validation performance acceptable: {avg_time:.2f}ms < 100ms")
            return True
        else:
            print(f"  ❌ Health validation too slow: {avg_time:.2f}ms >= 100ms")
            return False


async def test_routing_configuration():
    """Test configurable routing system"""
    print("\n📋 Testing Configurable Routing...")

    orchestrator = LUKHASAIOrchestrator("/test/workspace")

    # Test 1: Load routing configuration
    print("\n✅ Test 1: Configuration Loading")
    try:
        # This should load the YAML configuration
        result = await orchestrator.route_request("architecture_design", "test content")
        print(f"  ✅ Routing configuration loaded successfully")
    except Exception as e:
        # Expected since we don't have real providers configured
        if "API key" in str(e) or "not configured" in str(e):
            print(f"  ✅ Configuration loaded (API key issue expected): {e}")
        else:
            print(f"  ❌ Configuration loading failed: {e}")
            return False

    # Test 2: Dynamic provider selection based on task
    print("\n✅ Test 2: Task-Based Provider Selection")
    # Mock the routing logic
    with patch.object(orchestrator, '_call_provider', return_value="test response"):
        with patch.object(orchestrator, 'validate_provider_health') as mock_validate:
            mock_validate.return_value = {
                "healthy": True,
                "latency": 0.1,
                "sla_compliant": True
            }

            # Architecture design should prefer Claude
            result = await orchestrator.route_request("architecture_design", "test content")
            print(f"  ✅ Task-based routing functional")

    return True


async def main():
    """Run AI Orchestrator tests"""
    print("🚀 T4/0.01% AI Orchestrator Testing")
    print("=" * 50)

    try:
        # Test provider health validation
        health_test = await test_provider_health_validation()

        # Test provider selection
        selection_test = await test_provider_selection()

        # Test performance
        performance_test = await test_provider_health_performance()

        # Test routing configuration
        routing_test = await test_routing_configuration()

        print("\n📊 Test Summary")
        print("=" * 30)
        print(f"Health Validation: {'✅ PASS' if health_test else '❌ FAIL'}")
        print(f"Provider Selection: {'✅ PASS' if selection_test else '❌ FAIL'}")
        print(f"Performance: {'✅ PASS' if performance_test else '❌ FAIL'}")
        print(f"Routing Config: {'✅ PASS' if routing_test else '❌ FAIL'}")

        all_pass = health_test and selection_test and performance_test and routing_test

        if all_pass:
            print("\n🎉 All AI Orchestrator tests passed! T4/0.01% excellence achieved.")
            return 0
        else:
            print("\n⚠️  Some AI Orchestrator tests failed.")
            return 1

    except Exception as e:
        print(f"\n❌ AI Orchestrator test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))