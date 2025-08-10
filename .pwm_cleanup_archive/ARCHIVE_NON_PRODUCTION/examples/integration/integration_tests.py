"""
🧪 LUKHAS INTEGRATION TESTING FRAMEWORK
=====================================

Comprehensive integration testing system for the Lukhas modular framework.
Tests module interactions, performance, and system-wide functionality.

Features:
- Automated module discovery and testing
- Integration test scenarios
- Performance benchmarking
- Health monitoring validation
- Inter-module communication testing
- Load testing and stress testing
- Regression testing framework
"""

import asyncio
import io
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from dream.core import DreamType, LUKHASDreamModule
from modules.bio.core import LUKHASBioModule
from modules.vision.core import LUKHASVisionModule, VisionProvider
from modules.voice.core import LUKHASVoiceModule, VoiceEmotion, VoiceProvider
from PIL import Image

from core.common.base_module import SymbolicLogger
from core.module_registry import ModulePriority, ModuleStatus, get_registry
from memory.core import LUKHASMemoryModule


class TestResult(Enum):
    """Test execution results."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class TestSeverity(Enum):
    """Test failure severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class TestCase:
    """Individual test case definition."""

    name: str
    description: str
    test_function: Callable
    severity: TestSeverity = TestSeverity.MEDIUM
    timeout: int = 30
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class TestRun:
    """Test execution result."""

    test_case: TestCase
    result: TestResult
    start_time: datetime
    end_time: datetime
    duration: float
    error_message: Optional[str] = None
    performance_data: Dict[str, Any] = field(default_factory=dict)


class LUKHASIntegrationTester:
    """Integration testing framework for Lukhas modules."""

    def __init__(self):
        self.logger = SymbolicLogger("IntegrationTester")
        self.registry = get_registry()
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestRun] = []

        # Register all test cases
        self._register_test_cases()

    def _create_test_image(self) -> io.BytesIO:
        """Create a valid test image for vision module testing."""
        # Create a simple test image
        image = Image.new("RGB", (100, 100), color="red")

        # Save to BytesIO buffer
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="JPEG")
        image_buffer.seek(0)

        return image_buffer

    async def setup_core_modules(self):
        """Register and start core modules for testing."""
        await self.logger.info("🔧 Setting up core modules for integration testing...")

        try:
            # Register Memory module (critical priority)
            await self.registry.register_module(
                name="memory",
                module_class=LUKHASMemoryModule,
                priority=ModulePriority.CRITICAL,
            )
            await self.registry.start_module("memory")
            await self.logger.symbolic("🧠 Memory module loaded")

            # Register Dream module
            await self.registry.register_module(
                name="dream",
                module_class=LUKHASDreamModule,
                priority=ModulePriority.MEDIUM,
            )
            await self.registry.start_module("dream")
            await self.logger.symbolic("🌙 Dream module loaded")

            # Register Voice module
            await self.registry.register_module(
                name="voice",
                module_class=LUKHASVoiceModule,
                priority=ModulePriority.MEDIUM,
            )
            await self.registry.start_module("voice")
            await self.logger.symbolic("🗣️ Voice module loaded")

            # Register Bio module
            await self.registry.register_module(
                name="bio", module_class=LUKHASBioModule, priority=ModulePriority.MEDIUM
            )
            await self.registry.start_module("bio")
            await self.logger.symbolic("🫀 Bio module loaded")

            # Register Vision module
            await self.registry.register_module(
                name="vision",
                module_class=LUKHASVisionModule,
                priority=ModulePriority.MEDIUM,
            )
            await self.registry.start_module("vision")
            await self.logger.symbolic("👁️ Vision module loaded")

            await self.logger.info(
                "✅ All core modules successfully registered and started"
            )
            return True

        except Exception as e:
            await self.logger.error(f"❌ Failed to setup core modules: {e}")
            return False

    async def teardown_core_modules(self):
        """Clean up modules after testing."""
        await self.logger.info("🧹 Cleaning up modules after testing...")

        for module_name in ["dream", "voice", "bio", "memory"]:
            try:
                if module_name in self.registry._modules:
                    await self.registry.stop_module(module_name)
                    await self.registry.unregister_module(module_name)
            except Exception as e:
                await self.logger.error(f"Error cleaning up {module_name}: {e}")

    def _register_test_cases(self):
        """Register all integration test cases."""

        # Module Lifecycle Tests
        self.test_cases.extend(
            [
                TestCase(
                    name="test_module_registration",
                    description="Test module registration and discovery",
                    test_function=self._test_module_registration,
                    severity=TestSeverity.CRITICAL,
                    tags=["lifecycle", "registry"],
                ),
                TestCase(
                    name="test_module_startup_sequence",
                    description="Test proper module startup sequence with dependencies",
                    test_function=self._test_module_startup_sequence,
                    severity=TestSeverity.CRITICAL,
                    tags=["lifecycle", "startup"],
                ),
                TestCase(
                    name="test_module_health_monitoring",
                    description="Test module health monitoring and reporting",
                    test_function=self._test_module_health_monitoring,
                    severity=TestSeverity.HIGH,
                    tags=["health", "monitoring"],
                ),
            ]
        )

        # Core Module Integration Tests
        self.test_cases.extend(
            [
                TestCase(
                    name="test_dream_module_integration",
                    description="Test Dream module functionality and integration",
                    test_function=self._test_dream_module_integration,
                    severity=TestSeverity.HIGH,
                    dependencies=["dream"],
                    tags=["dream", "integration"],
                ),
                TestCase(
                    name="test_voice_module_integration",
                    description="Test Voice module functionality and integration",
                    test_function=self._test_voice_module_integration,
                    severity=TestSeverity.HIGH,
                    dependencies=["voice"],
                    tags=["voice", "integration"],
                ),
                TestCase(
                    name="test_bio_module_integration",
                    description="Test Bio module functionality and integration",
                    test_function=self._test_bio_module_integration,
                    severity=TestSeverity.HIGH,
                    dependencies=["bio"],
                    tags=["bio", "integration"],
                ),
                TestCase(
                    name="test_vision_module_integration",
                    description="Test Vision module functionality and integration",
                    test_function=self._test_vision_module_integration,
                    severity=TestSeverity.HIGH,
                    dependencies=["vision"],
                    tags=["vision", "integration"],
                ),
            ]
        )

        # Inter-Module Communication Tests
        self.test_cases.extend(
            [
                TestCase(
                    name="test_dream_voice_integration",
                    description="Test Dream and Voice module interaction",
                    test_function=self._test_dream_voice_integration,
                    severity=TestSeverity.MEDIUM,
                    dependencies=["dream", "voice"],
                    tags=["integration", "dream", "voice"],
                ),
                TestCase(
                    name="test_bio_voice_integration",
                    description="Test Bio and Voice module emotional state integration",
                    test_function=self._test_bio_voice_integration,
                    severity=TestSeverity.MEDIUM,
                    dependencies=["bio", "voice"],
                    tags=["integration", "bio", "voice"],
                ),
                TestCase(
                    name="test_vision_dream_integration",
                    description="Test Vision and Dream module symbolic processing",
                    test_function=self._test_vision_dream_integration,
                    severity=TestSeverity.MEDIUM,
                    dependencies=["vision", "dream"],
                    tags=["integration", "vision", "dream"],
                ),
            ]
        )

        # Performance and Load Tests
        self.test_cases.extend(
            [
                TestCase(
                    name="test_system_performance_baseline",
                    description="Establish performance baseline for all modules",
                    test_function=self._test_system_performance_baseline,
                    severity=TestSeverity.INFO,
                    timeout=60,
                    tags=["performance", "baseline"],
                ),
                TestCase(
                    name="test_concurrent_module_operations",
                    description="Test concurrent operations across multiple modules",
                    test_function=self._test_concurrent_module_operations,
                    severity=TestSeverity.MEDIUM,
                    timeout=90,
                    tags=["performance", "concurrency"],
                ),
                TestCase(
                    name="test_module_stress_testing",
                    description="Stress test module under high load",
                    test_function=self._test_module_stress_testing,
                    severity=TestSeverity.LOW,
                    timeout=120,
                    tags=["performance", "stress"],
                ),
            ]
        )

    async def run_all_tests(self, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run all integration tests."""
        await self.logger.info("Starting Lukhas integration test suite...")
        await self.logger.symbolic("🧪 Beginning constellation testing sequence")

        # Setup core modules for testing
        setup_success = await self.setup_core_modules()
        if not setup_success:
            await self.logger.error("❌ Failed to setup core modules, aborting tests")
            return {
                "status": "error",
                "message": "Failed to setup core modules",
                "tests_run": 0,
                "success_rate": 0.0,
            }

        try:
            # Filter tests by tags if specified
            tests_to_run = self.test_cases
            if tags:
                tests_to_run = [
                    tc for tc in self.test_cases if any(tag in tc.tags for tag in tags)
                ]

            self.test_results = []
            start_time = time.time()

            # Run tests sequentially to avoid conflicts
            for test_case in tests_to_run:
                result = await self._run_single_test(test_case)
                self.test_results.append(result)

            total_time = time.time() - start_time

            # Generate test report
            report = await self._generate_test_report(total_time)

            await self.logger.info(
                f"Integration testing completed in {total_time:.2f}s"
            )
            await self.logger.symbolic("🔮 Constellation testing sequence complete")

            return report

        finally:
            # Clean up modules after testing
            await self.teardown_core_modules()

    async def _run_single_test(self, test_case: TestCase) -> TestRun:
        """Run a single test case."""
        await self.logger.info(f"Running test: {test_case.name}")

        start_time = datetime.now()

        try:
            # Check dependencies
            for dep in test_case.dependencies:
                if dep not in self.registry._modules:
                    return TestRun(
                        test_case=test_case,
                        result=TestResult.SKIP,
                        start_time=start_time,
                        end_time=datetime.now(),
                        duration=0.0,
                        error_message=f"Missing dependency: {dep}",
                    )

            # Run test with timeout
            await asyncio.wait_for(test_case.test_function(), timeout=test_case.timeout)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            await self.logger.info(f"✅ Test passed: {test_case.name}")

            return TestRun(
                test_case=test_case,
                result=TestResult.PASS,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )

        except asyncio.TimeoutError:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_msg = f"Test timed out after {test_case.timeout}s"

            await self.logger.error(f"⏱️ Test timed out: {test_case.name}")

            return TestRun(
                test_case=test_case,
                result=TestResult.FAIL,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=error_msg,
            )

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            error_msg = f"{type(e).__name__}: {str(e)}"

            await self.logger.error(f"❌ Test failed: {test_case.name} - {error_msg}")

            return TestRun(
                test_case=test_case,
                result=TestResult.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_message=error_msg,
            )

    async def _generate_test_report(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.test_results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.test_results if r.result == TestResult.ERROR)
        skipped = sum(1 for r in self.test_results if r.result == TestResult.SKIP)

        # Calculate performance metrics
        avg_duration = (
            sum(r.duration for r in self.test_results) / total_tests
            if total_tests > 0
            else 0
        )
        slowest_test = (
            max(self.test_results, key=lambda r: r.duration)
            if self.test_results
            else None
        )

        # Categorize failures by severity
        critical_failures = [
            r
            for r in self.test_results
            if r.result in [TestResult.FAIL, TestResult.ERROR]
            and r.test_case.severity == TestSeverity.CRITICAL
        ]

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_time,
                "average_test_duration": avg_duration,
            },
            "performance": {
                "slowest_test": (
                    {
                        "name": slowest_test.test_case.name,
                        "duration": slowest_test.duration,
                    }
                    if slowest_test
                    else None
                ),
                "total_runtime": total_time,
            },
            "failures": {
                "critical": len(critical_failures),
                "details": [
                    {
                        "test": r.test_case.name,
                        "severity": r.test_case.severity.value,
                        "error": r.error_message,
                        "duration": r.duration,
                    }
                    for r in self.test_results
                    if r.result in [TestResult.FAIL, TestResult.ERROR]
                ],
            },
            "system_health": await self.registry.get_system_health(),
        }

        return report

    # Individual Test Implementations

    async def _test_module_registration(self):
        """Test module registration and discovery."""
        # Test registering a mock module
        from core.common.base_module import BaseLUKHASModule

        class MockTestModule(BaseLUKHASModule):
            async def process_request(self, request):
                return {"status": "ok", "request": request}

            async def get_health_status(self):
                return {"healthy": True, "status": "running"}

        # Test registration
        success = await self.registry.register_module(
            "test_mock", MockTestModule, ModulePriority.LOW
        )
        assert success, "Module registration failed"

        # Test duplicate registration
        duplicate = await self.registry.register_module(
            "test_mock", MockTestModule, ModulePriority.LOW
        )
        assert not duplicate, "Duplicate registration should fail"

        # Clean up
        await self.registry.unregister_module("test_mock")

    async def _test_module_startup_sequence(self):
        """Test module startup sequence with dependencies."""
        # Verify that required modules are registered
        expected_modules = ["dream", "voice", "bio", "vision"]

        for module_name in expected_modules:
            if module_name in self.registry._modules:
                module_info = self.registry._modules[module_name]

                # Test starting the module
                success = await self.registry.start_module(module_name)
                assert success, f"Failed to start module: {module_name}"

                # Verify module is running
                assert (
                    module_info.status == ModuleStatus.RUNNING
                ), f"Module {module_name} not running"

    async def _test_module_health_monitoring(self):
        """Test module health monitoring and reporting."""
        # Get system health
        system_health = await self.registry.get_system_health()
        assert system_health is not None, "System health check failed"

        # Verify health structure
        assert "overall_status" in system_health
        assert "total_modules" in system_health
        assert "running_modules" in system_health
        assert "modules" in system_health

        # Test individual module health
        for module_name in self.registry._modules:
            health = await self.registry.get_module_health(module_name)
            if health:
                assert "status" in health
                assert "uptime" in health

    async def _test_dream_module_integration(self):
        """Test Dream module functionality."""
        if "dream" not in self.registry._modules:
            return

        # Test dream generation request
        request = {
            "type": "generate_dream",
            "dream_type": DreamType.CREATIVE.value,
            "emotion_vector": {"joy": 0.7, "calm": 0.8},
        }

        result = await self.registry.route_request("dream", request)
        assert result is not None, "Dream module request failed"
        assert "dream_content" in result or "status" in result

    async def _test_voice_module_integration(self):
        """Test Voice module functionality."""
        if "voice" not in self.registry._modules:
            return

        # Test voice synthesis request
        request = {
            "type": "synthesize",
            "text": "Hello, this is a test of the Lukhas voice system.",
            "emotion": VoiceEmotion.NEUTRAL.value,
            "provider": VoiceProvider.MOCK.value,
        }

        result = await self.registry.route_request("voice", request)
        assert result is not None, "Voice module request failed"
        assert "success" in result or "status" in result

    async def _test_bio_module_integration(self):
        """Test Bio module functionality."""
        if "bio" not in self.registry._modules:
            return

        # Test biometric health snapshot request
        request = {"type": "health_snapshot"}

        result = await self.registry.route_request("bio", request)
        assert result is not None, "Bio module request failed"
        assert "success" in result or "status" in result

    async def _test_vision_module_integration(self):
        """Test Vision module functionality."""
        if "vision" not in self.registry._modules:
            return

        # Create proper test image data
        test_image = self._create_test_image()

        # Test image analysis request
        request = {
            "type": "analyze_image",
            "provider": VisionProvider.MOCK.value,
            "image_data": test_image,
        }

        result = await self.registry.route_request("vision", request)
        assert result is not None, "Vision module request failed"
        assert "status" in result or "success" in result

    async def _test_dream_voice_integration(self):
        """Test Dream and Voice module interaction."""
        if (
            "dream" not in self.registry._modules
            or "voice" not in self.registry._modules
        ):
            return

        # Test dream narration
        dream_request = {
            "type": "generate_dream",
            "dream_type": DreamType.CREATIVE.value,
            "suggest_voice": True,
        }

        dream_result = await self.registry.route_request("dream", dream_request)
        assert dream_result is not None, "Dream generation failed"

        if "voice_suggestion" in dream_result:
            voice_request = {
                "type": "synthesize",
                "text": dream_result.get("voice_suggestion", "Test narration"),
                "emotion": VoiceEmotion.CALM.value,
            }

            voice_result = await self.registry.route_request("voice", voice_request)
            assert voice_result is not None, "Dream voice narration failed"

    async def _test_bio_voice_integration(self):
        """Test Bio and Voice emotional state integration."""
        if "bio" not in self.registry._modules or "voice" not in self.registry._modules:
            return

        # Test emotional state detection and voice adaptation
        bio_request = {"type": "get_emotional_state"}

        bio_result = await self.registry.route_request("bio", bio_request)
        if bio_result and "emotional_state" in bio_result:
            emotion_state = bio_result["emotional_state"]

            voice_request = {
                "type": "synthesize",
                "text": "Testing emotional voice adaptation",
                "emotion": emotion_state.get("primary_emotion", "neutral"),
            }

            voice_result = await self.registry.route_request("voice", voice_request)
            assert voice_result is not None, "Emotional voice adaptation failed"

    async def _test_vision_dream_integration(self):
        """Test Vision and Dream symbolic processing."""
        if (
            "vision" not in self.registry._modules
            or "dream" not in self.registry._modules
        ):
            return

        # Create proper test image data
        test_image = self._create_test_image()

        # Test visual symbolic processing for dreams
        vision_request = {
            "type": "analyze_image",
            "image_data": test_image,
            "analysis_type": "symbolic",
        }

        vision_result = await self.registry.route_request("vision", vision_request)
        if vision_result and "symbolic_elements" in vision_result:
            # Use visual symbols to inspire dreams
            dream_request = {
                "type": "generate_dream",
                "dream_type": DreamType.PATTERN.value,
                "visual_inspiration": vision_result["symbolic_elements"],
            }

            dream_result = await self.registry.route_request("dream", dream_request)
            assert dream_result is not None, "Vision-inspired dream generation failed"

    async def _test_system_performance_baseline(self):
        """Establish performance baseline."""
        performance_data = {}

        for module_name in self.registry._modules:
            if self.registry._modules[module_name].status == ModuleStatus.RUNNING:
                start_time = time.time()

                # Simple health check request
                health = await self.registry.get_module_health(module_name)

                response_time = time.time() - start_time
                performance_data[module_name] = {
                    "health_check_time": response_time,
                    "status": (
                        "healthy"
                        if health and health.get("healthy", False)
                        else "unhealthy"
                    ),
                }

        # Store baseline for comparison
        self.performance_baseline = performance_data

    async def _test_concurrent_module_operations(self):
        """Test concurrent operations across modules."""
        # Create concurrent requests to different modules
        tasks = []

        if "dream" in self.registry._modules:
            tasks.append(self.registry.route_request("dream", {"type": "get_health"}))

        if "voice" in self.registry._modules:
            tasks.append(self.registry.route_request("voice", {"type": "get_health"}))

        if "bio" in self.registry._modules:
            tasks.append(self.registry.route_request("bio", {"type": "get_health"}))

        # TODO: Re-enable once vision module issues are fixed
        # if "vision" in self.registry._modules:
        #     tasks.append(self.registry.route_request("vision", {"type": "get_health"}))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all requests completed successfully
            for i, result in enumerate(results):
                assert not isinstance(
                    result, Exception
                ), f"Concurrent request {i} failed: {result}"

    async def _test_module_stress_testing(self):
        """Stress test modules under load."""
        # Send rapid requests to test module resilience
        stress_requests = 50
        concurrent_limit = 10

        for module_name in [
            "dream",
            "voice",
            "bio",
        ]:  # TODO: Add "vision" back when fixed
            if module_name not in self.registry._modules:
                continue

            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(concurrent_limit)

            async def stress_request():
                async with semaphore:
                    return await self.registry.route_request(
                        module_name, {"type": "health_check", "stress_test": True}
                    )

            # Send stress requests
            tasks = [stress_request() for _ in range(stress_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check that module survived stress test
            failures = sum(1 for r in results if isinstance(r, Exception))
            failure_rate = failures / len(results)

            assert (
                failure_rate < 0.1
            ), f"Module {module_name} failure rate too high: {failure_rate:.2%}"


# Integration Test Runner
async def run_integration_tests(tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run Lukhas integration tests."""
    tester = LUKHASIntegrationTester()
    return await tester.run_all_tests(tags)


# Performance Benchmark Runner
async def run_performance_benchmarks() -> Dict[str, Any]:
    """Run performance benchmarks for all modules."""
    tester = LUKHASIntegrationTester()
    return await tester.run_all_tests(tags=["performance"])


# Main execution block
if __name__ == "__main__":
    import sys

    async def main():
        """Main function to run integration tests."""
        print("🧪 Starting Lukhas Integration Test Suite")
        print("=" * 50)

        try:
            # Run all integration tests
            report = await run_integration_tests()

            # Print summary
            print("\n📊 TEST SUMMARY")
            print("-" * 30)
            summary = report["summary"]
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Passed: {summary['passed']} ✅")
            print(f"Failed: {summary['failed']} ❌")
            print(f"Errors: {summary['errors']} 💥")
            print(f"Skipped: {summary['skipped']} ⏭️")
            print(f"Success Rate: {summary['success_rate']:.1f}%")
            print(f"Total Duration: {summary['total_duration']:.2f}s")

            # Print failures if any
            if report["failures"]["details"]:
                print("\n💥 FAILURES")
                print("-" * 30)
                for failure in report["failures"]["details"]:
                    print(f"❌ {failure['test']} ({failure['severity']})")
                    print(f"   Error: {failure['error']}")
                    print(f"   Duration: {failure['duration']:.2f}s")

            # Print system health
            print("\n🏥 SYSTEM HEALTH")
            print("-" * 30)
            health = report["system_health"]
            print(f"Overall Status: {health['overall_status']}")
            print(
                f"Running Modules: {health['running_modules']}/{health['total_modules']}"
            )

            # Exit with appropriate code
            if summary["failed"] > 0 or summary["errors"] > 0:
                sys.exit(1)
            else:
                print("\n🎉 All tests passed!")
                sys.exit(0)

        except Exception as e:
            print(f"\n💥 Fatal error running tests: {e}")
            traceback.print_exc()
            sys.exit(1)

    # Run the main function
    asyncio.run(main())
