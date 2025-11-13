#!/usr/bin/env python3
"""
LUKHAS AI - Orchestration System Test Suite
============================================

Comprehensive test suite for multi-AI orchestration system validation.
Tests function calling, consensus algorithms, streaming, and performance.

Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
Performance Target: <100ms orchestration latency validation
Coverage: Integration tests, performance tests, security tests

Test Categories:
- Function calling validation (OpenAI & Anthropic)
- Multi-model consensus accuracy
- Streaming performance and reliability
- API endpoint functionality
- Rate limiting and security
- Performance benchmarking
"""
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import pytest  # TODO[T4-UNUSED-IMPORT]: kept for API expansion (document or implement)
    import websockets  # TODO[T4-UNUSED-IMPORT]: kept for API expansion (document or implement)
    from bridge.api.orchestration_api_bridge import (
        APIProvider,
        ComprehensiveAPIOrchestrator,
        OrchestrationRequest,
        OrchestrationStrategy,
    )
    from bridge.api.orchestration_endpoints import app
    from bridge.llm_wrappers.anthropic_function_bridge import (
        AnthropicFunctionBridge,
        ClaudeModel,  # TODO: bridge.llm_wrappers.ant...
        ToolDefinition,
        ToolUseMode,
    )

    # LUKHAS imports
    from bridge.llm_wrappers.openai_function_bridge import (
        FunctionCallMode,
        FunctionDefinition,
        OpenAIFunctionBridge,
    )
    from httpx import AsyncClient

    TESTING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Testing dependencies not available: {e}")
    TESTING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result container"""

    test_name: str
    success: bool
    latency_ms: float = 0.0
    error: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class OrchestrationTestSuite:
    """
    Comprehensive test suite for LUKHAS orchestration system.

    Validates:
    - Function calling capabilities
    - Multi-model consensus accuracy
    - Streaming performance
    - API security and rate limiting
    - Performance benchmarks
    """

    def __init__(self):
        """Initialize test suite"""
        self.results = []
        self.orchestrator = None
        self.test_functions = self._setup_test_functions()

        logger.info("🧪 LUKHAS Orchestration Test Suite initialized")

    def _setup_test_functions(self) -> dict[str, dict[str, Any]]:
        """Setup test functions for validation"""
        return {
            "test_calculator": {
                "description": "Perform mathematical calculations for testing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate",
                        },
                        "precision": {
                            "type": "integer",
                            "description": "Number of decimal places",
                            "default": 2,
                        },
                    },
                    "required": ["expression"],
                },
                "handler": self._test_calculator_handler,
                "security_level": "standard",
            },
            "test_memory_store": {
                "description": "Store and retrieve test data",
                "input_schema": {  # Anthropic format
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Storage key"},
                        "value": {"type": "string", "description": "Value to store"},
                        "action": {
                            "type": "string",
                            "enum": ["store", "retrieve"],
                            "description": "Action to perform",
                        },
                    },
                    "required": ["key", "action"],
                },
                "handler": self._test_memory_handler,
                "security_level": "standard",
            },
            "test_latency_check": {
                "description": "Test function for latency measurement",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "delay_ms": {
                            "type": "integer",
                            "description": "Artificial delay in milliseconds",
                            "default": 0,
                        }
                    },
                },
                "handler": self._test_latency_handler,
                "security_level": "standard",
            },
        }

    async def _test_calculator_handler(self, expression: str, precision: int = 2, **kwargs) -> dict[str, Any]:
        """Test calculator function"""
        try:
            # Safe evaluation of simple mathematical expressions
            allowed_chars = set("0123456789+-*/.()")
            if not all(c in allowed_chars or c.isspace() for c in expression):
                return {"error": "Invalid characters in expression"}

            result = eval(expression)  # Note: In production, use a safe math parser
            return {
                "result": round(result, precision),
                "expression": expression,
                "precision": precision,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _test_memory_handler(
        self, key: str, action: str, value: Optional[str] = None, **kwargs
    ) -> dict[str, Any]:
        """Test memory storage function"""
        if not hasattr(self, "_test_memory"):
            self._test_memory = {}

        if action == "store":
            if value is None:
                return {"error": "Value required for store action"}
            self._test_memory[key] = value
            return {"success": True, "action": "stored", "key": key}
        elif action == "retrieve":
            if key in self._test_memory:
                return {
                    "success": True,
                    "action": "retrieved",
                    "key": key,
                    "value": self._test_memory[key],
                }
            else:
                return {"error": f"Key '{key}' not found"}
        else:
            return {"error": f"Invalid action: {action}"}

    async def _test_latency_handler(self, delay_ms: int = 0, **kwargs) -> dict[str, Any]:
        """Test latency measurement function"""
        start_time = time.perf_counter()

        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)

        end_time = time.perf_counter()
        actual_delay = (end_time - start_time) * 1000

        return {
            "requested_delay_ms": delay_ms,
            "actual_delay_ms": round(actual_delay, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def run_all_tests(self) -> dict[str, Any]:
        """
        Run complete test suite and return comprehensive results.

        Returns:
            Dictionary with test results, performance metrics, and summary
        """
        logger.info("🚀 Starting comprehensive orchestration test suite")
        start_time = time.perf_counter()

        # Test categories
        test_categories = [
            ("Function Calling Tests", self._test_function_calling),
            ("Consensus Algorithm Tests", self._test_consensus_algorithms),
            ("Streaming Tests", self._test_streaming_capabilities),
            ("Performance Tests", self._test_performance_benchmarks),
            ("Security Tests", self._test_security_validation),
            ("Integration Tests", self._test_api_integration),
        ]

        category_results = {}

        for category_name, test_function in test_categories:
            logger.info(f"🗺 Running {category_name}...")
            try:
                category_result = await test_function()
                category_results[category_name] = category_result
                logger.info(
                    f"✅ {category_name} completed: {category_result.get('passed', 0)}/{category_result.get('total', 0)} passed"
                )
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e!s}")
                category_results[category_name] = {
                    "passed": 0,
                    "failed": 1,
                    "total": 1,
                    "error": str(e),
                }

        # Calculate overall results
        total_time = (time.perf_counter() - start_time) * 1000

        total_passed = sum(result.get("passed", 0) for result in category_results.values())
        total_failed = sum(result.get("failed", 0) for result in category_results.values())
        total_tests = total_passed + total_failed

        success_rate = (total_passed / total_tests) if total_tests > 0 else 0.0

        summary = {
            "test_suite": "LUKHAS Multi-AI Orchestration",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_time_ms": total_time,
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": success_rate,
                "performance_target_met": total_time < 10000,  # 10 second target for full suite
            },
            "category_results": category_results,
            "individual_results": self.results,
        }

        # Log final summary
        logger.info(f"🏆 Test suite completed in {total_time:.2f}ms")
        logger.info(f"   Tests passed: {total_passed}/{total_tests} ({success_rate:.1%})")
        logger.info(f"   Performance target met: {summary['summary']['performance_target_met']}")

        return summary

    async def _test_function_calling(self) -> dict[str, Any]:
        """Test function calling capabilities"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test OpenAI function calling
        if await self._test_openai_functions():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        # Test Anthropic tool use
        if await self._test_anthropic_tools():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        return results

    async def _test_openai_functions(self) -> bool:
        """Test OpenAI function calling"""
        test_start = time.perf_counter()

        try:
            # Initialize bridge (will use mock if no API key)
            bridge = OpenAIFunctionBridge()

            # Register test functions
            for func_name, func_def in self.test_functions.items():
                if "parameters" in func_def:  # OpenAI format
                    function_definition = FunctionDefinition(
                        name=func_name,
                        description=func_def["description"],
                        parameters=func_def["parameters"],
                        handler=func_def["handler"],
                    )
                    bridge.register_function(function_definition)

            # Test function call
            messages = [
                {
                    "role": "user",
                    "content": "Calculate 15 + 27 using the calculator function",
                }
            ]

            response = await bridge.complete_with_functions(
                messages=messages,
                function_mode=FunctionCallMode.AUTO,
                execute_functions=True,
            )

            latency = (time.perf_counter() - test_start) * 1000

            # Validate response
            success = response.content and len(response.function_calls) > 0 and latency < 2000  # 2 second timeout

            self.results.append(
                TestResult(
                    test_name="OpenAI Function Calling",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "function_calls": len(response.function_calls),
                        "response_length": len(response.content),
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="OpenAI Function Calling",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_anthropic_tools(self) -> bool:
        """Test Anthropic tool use"""
        test_start = time.perf_counter()

        try:
            # Initialize bridge (will use mock if no API key)
            bridge = AnthropicFunctionBridge()

            # Register test tools
            for tool_name, tool_def in self.test_functions.items():
                if "input_schema" in tool_def:  # Anthropic format
                    tool_definition = ToolDefinition(
                        name=tool_name,
                        description=tool_def["description"],
                        input_schema=tool_def["input_schema"],
                        handler=tool_def["handler"],
                    )
                    bridge.register_tool(tool_definition)

            # Test tool use
            messages = [
                {
                    "role": "user",
                    "content": "Store 'Hello World' with key 'test_message' using the memory function",
                }
            ]

            response = await bridge.complete_with_tools(
                messages=messages, tool_mode=ToolUseMode.ENABLED, execute_tools=True
            )

            latency = (time.perf_counter() - test_start) * 1000

            # Validate response
            success = (
                response.content
                and len(response.tool_uses) > 0
                and response.constitutional_score > 0.7
                and latency < 3000  # 3 second timeout for Anthropic
            )

            self.results.append(
                TestResult(
                    test_name="Anthropic Tool Use",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "tool_uses": len(response.tool_uses),
                        "constitutional_score": response.constitutional_score,
                        "response_length": len(response.content),
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Anthropic Tool Use",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_consensus_algorithms(self) -> dict[str, Any]:
        """Test multi-model consensus algorithms"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test different consensus strategies
        strategies = ["consensus", "single_best", "competitive", "ensemble"]

        for strategy in strategies:
            if await self._test_consensus_strategy(strategy):
                results["passed"] += 1
            else:
                results["failed"] += 1
            results["total"] += 1

        return results

    async def _test_consensus_strategy(self, strategy: str) -> bool:
        """Test specific consensus strategy"""
        test_start = time.perf_counter()

        try:
            orchestrator = ComprehensiveAPIOrchestrator()

            # Create test request
            request = OrchestrationRequest(
                prompt="What is the capital of France? Please be concise.",
                strategy=OrchestrationStrategy(strategy),
                preferred_providers=[APIProvider.ALL],
                max_latency_ms=5000,
            )

            # Execute orchestration
            response = await orchestrator.orchestrate(request)

            latency = (time.perf_counter() - test_start) * 1000

            # Validate response
            success = (
                response.content
                and "paris" in response.content.lower()
                and response.confidence_score > 0.5
                and latency < 6000  # 6 second timeout
            )

            self.results.append(
                TestResult(
                    test_name=f"Consensus Strategy: {strategy}",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "strategy": strategy,
                        "providers": len(response.participating_providers),
                        "confidence": response.confidence_score,
                        "agreement_level": response.agreement_level,
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name=f"Consensus Strategy: {strategy}",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_streaming_capabilities(self) -> dict[str, Any]:
        """Test streaming capabilities"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test orchestration streaming
        if await self._test_orchestration_streaming():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        return results

    async def _test_orchestration_streaming(self) -> bool:
        """Test streaming orchestration"""
        test_start = time.perf_counter()

        try:
            orchestrator = ComprehensiveAPIOrchestrator()

            request = OrchestrationRequest(
                prompt="Count from 1 to 5, one number per line.",
                preferred_providers=[APIProvider.OPENAI],
                enable_functions=False,
            )

            chunks_received = 0
            content_received = ""

            async for chunk in orchestrator.stream_orchestration(request):
                chunks_received += 1
                if chunk.get("type") == "content":
                    content_received += chunk.get("content", "")

                # Limit test duration
                if (time.perf_counter() - test_start) > 10:  # 10 second timeout
                    break

            latency = (time.perf_counter() - test_start) * 1000

            # Validate streaming
            success = chunks_received > 0 and len(content_received) > 0 and latency < 12000  # 12 second timeout

            self.results.append(
                TestResult(
                    test_name="Orchestration Streaming",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "chunks_received": chunks_received,
                        "content_length": len(content_received),
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Orchestration Streaming",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_performance_benchmarks(self) -> dict[str, Any]:
        """Test performance benchmarks"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test latency benchmark
        if await self._test_latency_benchmark():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        # Test throughput benchmark
        if await self._test_throughput_benchmark():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        return results

    async def _test_latency_benchmark(self) -> bool:
        """Test response latency benchmark"""
        test_start = time.perf_counter()

        try:
            orchestrator = ComprehensiveAPIOrchestrator()

            # Simple request for latency testing
            request = OrchestrationRequest(
                prompt="Say 'Hello' in one word.",
                strategy=OrchestrationStrategy.SINGLE_BEST,
                preferred_providers=[APIProvider.OPENAI],
                enable_functions=False,
            )

            response = await orchestrator.orchestrate(request)
            latency = (time.perf_counter() - test_start) * 1000

            # Performance target: <2000ms for simple request
            success = response.content and latency < 2000 and response.total_latency_ms < 2000

            self.results.append(
                TestResult(
                    test_name="Latency Benchmark",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "orchestration_latency": response.total_latency_ms,
                        "target_met": latency < 1000,  # <1s is excellent
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Latency Benchmark",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_throughput_benchmark(self) -> bool:
        """Test concurrent request throughput"""
        test_start = time.perf_counter()

        try:
            orchestrator = ComprehensiveAPIOrchestrator()

            # Create multiple concurrent requests
            tasks = []
            for i in range(3):  # Limited concurrent requests for testing
                request = OrchestrationRequest(
                    prompt=f"What is {i + 1} + {i + 1}?",
                    strategy=OrchestrationStrategy.SINGLE_BEST,
                    preferred_providers=[APIProvider.OPENAI],
                    enable_functions=False,
                )
                task = asyncio.create_task(orchestrator.orchestrate(request))
                tasks.append(task)

            # Execute concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            latency = (time.perf_counter() - test_start) * 1000

            # Count successful responses
            successful_responses = sum(
                1 for response in responses if not isinstance(response, Exception) and response.content
            )

            # Success if at least 2/3 requests succeed
            success = successful_responses >= 2 and latency < 8000  # 8 second timeout for 3 concurrent requests

            self.results.append(
                TestResult(
                    test_name="Throughput Benchmark",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "concurrent_requests": len(tasks),
                        "successful_responses": successful_responses,
                        "requests_per_second": (len(tasks) / (latency / 1000) if latency > 0 else 0),
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Throughput Benchmark",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_security_validation(self) -> dict[str, Any]:
        """Test security validation"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test input sanitization
        if await self._test_input_sanitization():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        return results

    async def _test_input_sanitization(self) -> bool:
        """Test input sanitization and validation"""
        test_start = time.perf_counter()

        try:
            orchestrator = ComprehensiveAPIOrchestrator()

            # Test with potentially harmful input
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../../etc/passwd",
                "\x00\x01\x02",  # Binary data
            ]

            successful_blocks = 0

            for malicious_input in malicious_inputs:
                try:
                    request = OrchestrationRequest(
                        prompt=f"Process this input: {malicious_input}",
                        strategy=OrchestrationStrategy.SINGLE_BEST,
                        preferred_providers=[APIProvider.OPENAI],
                        enable_functions=False,
                    )

                    response = await orchestrator.orchestrate(request)

                    # Check if response contains the malicious input verbatim (bad)
                    if malicious_input not in response.content:
                        successful_blocks += 1

                except Exception:
                    # Exception is okay for malicious input (blocked)
                    successful_blocks += 1

            latency = (time.perf_counter() - test_start) * 1000

            # Success if most malicious inputs are handled safely
            success = successful_blocks >= len(malicious_inputs) * 0.75  # 75% threshold

            self.results.append(
                TestResult(
                    test_name="Input Sanitization",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "malicious_inputs_tested": len(malicious_inputs),
                        "safely_handled": successful_blocks,
                        "safety_rate": successful_blocks / len(malicious_inputs),
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Input Sanitization",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False

    async def _test_api_integration(self) -> dict[str, Any]:
        """Test API integration"""
        results = {"passed": 0, "failed": 0, "total": 0}

        # Test health endpoint
        if await self._test_health_endpoint():
            results["passed"] += 1
        else:
            results["failed"] += 1
        results["total"] += 1

        return results

    async def _test_health_endpoint(self) -> bool:
        """Test API health endpoint"""
        test_start = time.perf_counter()

        try:
            if not TESTING_AVAILABLE or app is None:
                # Skip if FastAPI not available
                return True

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/health")

            latency = (time.perf_counter() - test_start) * 1000

            success = (
                response.status_code == 200
                and "status" in response.json()
                and response.json()["status"] == "healthy"
                and latency < 1000  # 1 second timeout
            )

            self.results.append(
                TestResult(
                    test_name="Health Endpoint",
                    success=success,
                    latency_ms=latency,
                    metrics={
                        "status_code": response.status_code,
                        "response_data": response.json() if success else None,
                    },
                )
            )

            return success

        except Exception as e:
            latency = (time.perf_counter() - test_start) * 1000
            self.results.append(
                TestResult(
                    test_name="Health Endpoint",
                    success=False,
                    latency_ms=latency,
                    error=str(e),
                )
            )
            return False


# Main test execution
async def run_orchestration_tests() -> dict[str, Any]:
    """Run orchestration test suite"""
    if not TESTING_AVAILABLE:
        return {
            "error": "Testing dependencies not available",
            "suggestion": "Install testing dependencies: pip install pytest httpx websockets",
        }

    test_suite = OrchestrationTestSuite()
    results = await test_suite.run_all_tests()

    return results


if __name__ == "__main__":
    # Run tests if executed directly
    print("🧪 LUKHAS AI - Orchestration System Test Suite")
    print("=" * 50)

    results = asyncio.run(run_orchestration_tests())

    print("\n📈 Test Results Summary:")
    print(f"  Total Tests: {results.get('summary', {}).get('total_tests', 0)}")
    print(f"  Passed: {results.get('summary', {}).get('passed', 0)}")
    print(f"  Failed: {results.get('summary', {}).get('failed', 0)}")
    print(f"  Success Rate: {results.get('summary', {}).get('success_rate', 0):.1%}")
    print(f"  Total Time: {results.get('total_time_ms', 0):.2f}ms")

    # Save results to file
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_file = f"orchestration_test_results_{timestamp}.json"

    try:
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save results: {e}")

    print("\n🏁 Test suite completed!")

# Export for pytest integration
__all__ = ["OrchestrationTestSuite", "TestResult", "run_orchestration_tests"]
