"""
LUKHAS Comprehensive Test Framework
Base classes and utilities for testing all core systems
"""

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from unittest.mock import AsyncMock, Mock, patch

import pytest
import structlog

log = structlog.get_logger(__name__)


class LUKHASTestCase:
    """Base test case for LUKHAS components"""

    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Setup structured logging for tests"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_config(self, temp_dir):
        """Create mock configuration"""
        return {
            "data_dir": str(temp_dir),
            "log_level": "DEBUG",
            "test_mode": True,
            "encryption_enabled": False,  # Disable for tests
            "max_memory_size": 1000,
            "consciousness_levels": 5,
            "dream_iterations": 3,
        }

    async def assert_eventually(
        self,
        condition: Callable,
        timeout: float = 5.0,
        interval: float = 0.1,
        message: str = "",
    ):
        """Assert that condition becomes true eventually"""
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            if (
                await condition()
                if asyncio.iscoroutinefunction(condition)
                else condition()
            ):
                return
            await asyncio.sleep(interval)

        pytest.fail(f"Condition not met within {timeout}s: {message}")

    def create_mock_service(self, service_name: str) -> AsyncMock:
        """Create a mock service with common methods"""
        mock = AsyncMock()
        mock.initialize = AsyncMock()
        mock.shutdown = AsyncMock()
        mock.get_status = AsyncMock(return_value={"status": "healthy"})
        mock.get_metrics = AsyncMock(return_value={"requests": 0})
        mock.name = service_name
        return mock


class IntegrationTestCase(LUKHASTestCase):
    """Base class for integration tests"""

    @pytest.fixture
    async def mock_guardian(self):
        """Create mock Guardian system"""
        guardian = AsyncMock()
        guardian.validate_action = AsyncMock(return_value={"approved": True})
        guardian.check_drift = AsyncMock(return_value={"drift_score": 0.1})
        return guardian

    async def wait_for_event(self, event_bus, event_type: str, timeout: float = 5.0):
        """Wait for specific event on event bus"""
        # Use the global kernel bus for subscriptions
        from orchestration.symbolic_kernel_bus import kernel_bus

        received_event = None

        async def handler(event):
            nonlocal received_event
            received_event = event

        kernel_bus.subscribe(event_type, handler)

        await self.assert_eventually(
            lambda: received_event is not None,
            timeout=timeout,
            message=f"Event {event_type} not received",
        )

        return received_event


class PerformanceTestCase(LUKHASTestCase):
    """Base class for performance tests"""

    @pytest.fixture
    def performance_metrics(self):
        """Track performance metrics"""
        return {
            "start_time": None,
            "end_time": None,
            "operations": [],
            "memory_usage": [],
            "response_times": [],
        }

    async def measure_operation(self, operation: Callable, metrics: dict[str, Any]):
        """Measure operation performance"""
        import inspect
        import time

        import psutil

        process = psutil.Process()

        # Memory before
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Time operation
        start = time.perf_counter()
        # Call operation; it may return an awaitable even if it's not a
        # coroutinefunction (e.g., lambda)
        op_result = operation() if callable(operation) else operation
        if inspect.isawaitable(op_result):
            result = await op_result
        else:
            result = op_result
        end = time.perf_counter()

        # Memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB

        # Record metrics
        metrics["operations"].append(
            {
                "duration": end - start,
                "memory_delta": mem_after - mem_before,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        metrics["response_times"].append(end - start)
        metrics["memory_usage"].append(mem_after)

        return result

    def assert_performance(
        self,
        metrics: dict[str, Any],
        max_response_time: float = 1.0,
        max_memory_mb: float = 500,
    ):
        """Assert performance requirements met"""
        avg_response = sum(metrics["response_times"]) / len(metrics["response_times"])
        max_response = max(metrics["response_times"])
        max_memory = max(metrics["memory_usage"])

        assert (
            avg_response < max_response_time
        ), f"Average response time {avg_response:.3f}s exceeds limit {max_response_time}s"

        assert (
            max_response < max_response_time * 2
        ), f"Max response time {max_response:.3f}s exceeds limit {max_response_time * 2}s"

        assert (
            max_memory < max_memory_mb
        ), f"Max memory usage {max_memory:.1f}MB exceeds limit {max_memory_mb}MB"


class SecurityTestCase(LUKHASTestCase):
    """Base class for security tests"""

    @pytest.fixture
    def mock_security(self):
        """Create mock security system"""
        from core.security.security_integration import SecurityIntegration

        security = Mock(spec=SecurityIntegration)
        security.validate_request = AsyncMock(return_value=(True, None))
        security.encrypt_module_data = AsyncMock(return_value=(b"encrypted", "key_id"))
        return security

    async def assert_secure_operation(
        self, operation: Callable, expected_validations: list[str]
    ):
        """Assert operation performs required security checks"""
        with patch(
            "core.security.security_integration.get_security_integration"
        ) as mock:
            security = AsyncMock()
            validation_calls = []

            async def track_validation(request_data):
                validation_calls.append(request_data.get("operation"))
                return True, None

            security.validate_request = track_validation
            mock.return_value = security

            await operation()

            for expected in expected_validations:
                assert (
                    expected in validation_calls
                ), f"Expected security validation for '{expected}' not performed"


class MockDataGenerator:
    """Generate mock data for tests"""

    @staticmethod
    def create_consciousness_state(state: str = "aware") -> dict[str, Any]:
        """Create mock consciousness state"""
        return {
            "state": state,
            "awareness_level": 0.8,
            "vector": [0.1, 0.5, 0.3, 0.7, 0.2],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def create_memory_entry(content: str = "test memory") -> dict[str, Any]:
        """Create mock memory entry"""
        return {
            "id": f"mem_{datetime.now(timezone.utc).timestamp()}",
            "content": content,
            "type": "episodic",
            "importance": 0.7,
            "emotional_weight": 0.5,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def create_action_proposal(action: str = "test_action") -> dict[str, Any]:
        """Create mock action proposal"""
        return {
            "action": action,
            "parameters": {},
            "context": {"source": "test"},
            "urgency": "normal",
            "ethical_implications": [],
        }

    @staticmethod
    def create_glyph_sequence(length: int = 5) -> list[str]:
        """Create mock GLYPH sequence"""
        glyphs = ["λ", "Ω", "Δ", "Σ", "Φ", "Ψ", "Θ"]
        import random

        return [random.choice(glyphs) + str(i) for i in range(length)]


class TestValidator:
    """Validate test results against expected patterns"""

    @staticmethod
    def validate_api_response(response: dict[str, Any]):
        """Validate standard API response format"""
        assert "status" in response, "Response missing status"
        assert response["status"] in ["success", "error", "partial"]
        assert "timestamp" in response, "Response missing timestamp"

        if response["status"] == "error":
            assert "error" in response, "Error response missing error details"
        else:
            assert "result" in response, "Success response missing result"

    @staticmethod
    def validate_consciousness_response(response: dict[str, Any]):
        """Validate consciousness query response"""
        assert "interpretation" in response
        assert "consciousness_state" in response
        assert "awareness_vector" in response
        assert len(response["awareness_vector"]) > 0

    @staticmethod
    def validate_memory_response(response: dict[str, Any]):
        """Validate memory operation response"""
        if "memory_id" in response:
            assert response["memory_id"].startswith("mem_")
        if "results" in response:
            assert isinstance(response["results"], list)

    @staticmethod
    def validate_governance_response(response: dict[str, Any]):
        """Validate governance check response"""
        assert "approved" in response
        assert isinstance(response["approved"], bool)
        assert "risk_score" in response
        assert 0 <= response["risk_score"] <= 1

        if not response["approved"]:
            assert "violated_rules" in response
            assert len(response["violated_rules"]) > 0


# Test fixtures for common components
@pytest.fixture
async def symbolic_engine():
    """Create test symbolic engine"""
    from core.api.service_stubs import SymbolicEngine

    engine = SymbolicEngine()
    await engine.initialize()
    yield engine


@pytest.fixture
async def consciousness_system():
    """Create test consciousness system"""
    from core.api.service_stubs import UnifiedConsciousness

    consciousness = UnifiedConsciousness()
    await consciousness.initialize()
    yield consciousness


@pytest.fixture
async def memory_system():
    """Create test memory system"""
    from core.api.service_stubs import MemoryManager

    memory = MemoryManager()
    await memory.initialize()
    yield memory


@pytest.fixture
async def guardian_system():
    """Create test guardian system"""
    from core.api.service_stubs import GuardianSystem

    guardian = GuardianSystem()
    await guardian.initialize()
    yield guardian


# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "consciousness_query": {
        "max_response_time": 0.5,  # 500ms
        "max_memory_mb": 100,
    },
    "memory_store": {"max_response_time": 0.1, "max_memory_mb": 80},  # 100ms
    "memory_search": {"max_response_time": 0.3, "max_memory_mb": 200},  # 300ms
    "governance_check": {
        "max_response_time": 0.2,  # 200ms
        "max_memory_mb": 50,
    },
    "dream_generation": {
        "max_response_time": 2.0,  # 2s for creative generation
        "max_memory_mb": 300,
    },
}


# Test data sets
TEST_DATASETS = {
    "consciousness_queries": [
        "What is the nature of consciousness?",
        "How do you perceive reality?",
        "What emotions are you experiencing?",
        "Describe your current state of awareness.",
        "What patterns do you recognize in this data?",
    ],
    "memory_content": [
        {"event": "System initialization", "importance": "high"},
        {"learning": "New pattern recognized", "type": "semantic"},
        {"experience": "User interaction", "emotion": "positive"},
        {"observation": "Environmental change", "timestamp": "recent"},
        {"reflection": "Self-analysis complete", "depth": "deep"},
    ],
    "action_proposals": [
        {"action": "respond_to_user", "content": "Hello"},
        {"action": "store_memory", "data": {"important": True}},
        {"action": "analyze_pattern", "complexity": "high"},
        {"action": "generate_content", "creativity": 0.8},
        {"action": "modify_behavior", "risk": "low"},
    ],
}
