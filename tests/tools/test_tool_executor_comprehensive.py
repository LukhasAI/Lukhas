"""
Comprehensive Test Suite for Tool Execution System
=================================================
Tests safe web scraping, sandboxed execution, Guardian integration, and orchestration.
"""

import os

# Import tool execution components
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../candidate/tools"))

from candidate.tools.external_service_integration import ExternalServiceIntegration
from candidate.tools.tool_executor import ToolExecutor
from candidate.tools.tool_executor_guardian import ToolExecutorGuardian
from candidate.tools.tool_orchestrator import MultiAIConsensus, ToolOrchestrator


@pytest.fixture
async def tool_executor():
    """Create tool executor instance for testing"""
    config = {
        "allowed_domains": ["httpbin.org", "example.com"],
        "max_content_size": 1024,
        "request_timeout": 5,
    }
    executor = ToolExecutor(config)
    yield executor


@pytest.fixture
async def guardian():
    """Create Guardian instance for testing"""
    guardian = ToolExecutorGuardian()
    yield guardian


@pytest.fixture
async def orchestrator():
    """Create orchestrator instance for testing"""
    config = {
        "enable_consensus": False,  # Disable for testing
        "max_execution_time": 10,
    }
    orchestrator = ToolOrchestrator(config)
    yield orchestrator


@pytest.fixture
def mock_docker_client():
    """Mock Docker client for sandboxed execution tests"""
    with patch("docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_container.decode.return_value = "Test output"
        mock_client.containers.run.return_value = mock_container
        mock_client.ping.return_value = True
        mock_docker.return_value = mock_client
        yield mock_client


class TestToolExecutor:
    """Test suite for core ToolExecutor functionality"""

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_enabled(self, tool_executor):
        """Test knowledge retrieval when enabled"""
        # Test ethical AI query
        result = await tool_executor.execute("retrieve_knowledge", '{"query": "ethical AI"}')

        assert "ethical AI" in result
        assert "Transparency and Explainability" in result
        assert tool_executor.metrics["retrieve_knowledge"] == 1

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_disabled(self):
        """Test knowledge retrieval when disabled"""
        with patch.dict(os.environ, {"LUKHAS_ENABLE_RETRIEVAL": "false"}):
            executor = ToolExecutor()
            result = await executor.execute("retrieve_knowledge", '{"query": "test"}')

            assert "Knowledge retrieval is currently disabled" in result

    @pytest.mark.asyncio
    async def test_schedule_task_success(self, tool_executor):
        """Test successful task scheduling"""
        result = await tool_executor.execute("schedule_task", '{"when": "tomorrow", "note": "Test task"}')

        assert "Task scheduled" in result
        assert "Test task" in result
        assert tool_executor.metrics["schedule_task"] == 1

        # Verify task file was created
        task_files = list(tool_executor.schedule_queue_dir.glob("task_*.json"))
        assert len(task_files) == 1

    @pytest.mark.asyncio
    async def test_schedule_task_missing_note(self, tool_executor):
        """Test task scheduling with missing note"""
        result = await tool_executor.execute("schedule_task", '{"when": "tomorrow"}')

        assert "Cannot schedule task without a description" in result

    @pytest.mark.asyncio
    async def test_url_validation_success(self, tool_executor):
        """Test successful URL validation"""
        # Test allowed domain
        assert tool_executor._validate_url("https://httpbin.org/get")
        assert tool_executor._validate_url("http://example.com/test")

    @pytest.mark.asyncio
    async def test_url_validation_blocked_scheme(self, tool_executor):
        """Test URL validation blocks invalid schemes"""
        assert not tool_executor._validate_url("ftp://example.com")
        assert not tool_executor._validate_url("javascript:alert('test')")
        assert not tool_executor._validate_url("data:text/html,<script>")

    @pytest.mark.asyncio
    async def test_url_validation_blocked_domains(self, tool_executor):
        """Test URL validation blocks non-allowlisted domains"""
        assert not tool_executor._validate_url("https://malicious.com")
        assert not tool_executor._validate_url("http://localhost:8080")
        assert not tool_executor._validate_url("https://192.168.1.1")

    @pytest.mark.asyncio
    async def test_code_security_validation(self, tool_executor):
        """Test code security validation"""
        # Safe code should pass
        assert tool_executor._validate_code_security("print('hello')", "python")
        assert tool_executor._validate_code_security("console.log('test')", "javascript")
        assert tool_executor._validate_code_security("echo 'hello'", "bash")

        # Dangerous patterns should be blocked
        assert not tool_executor._validate_code_security("import os", "python")
        assert not tool_executor._validate_code_security("eval('test')", "python")
        assert not tool_executor._validate_code_security("subprocess.run(['ls'])", "python")
        assert not tool_executor._validate_code_security("process.env", "javascript")
        assert not tool_executor._validate_code_security("rm -rf /", "bash")
        assert not tool_executor._validate_code_security("sudo su", "bash")

    @pytest.mark.asyncio
    async def test_code_execution_disabled(self, tool_executor):
        """Test code execution when disabled"""
        result = await tool_executor.execute("exec_code", '{"language": "python", "source": "print(\\"hello\\")"}')

        assert "Code execution is disabled" in result

    @pytest.mark.asyncio
    async def test_code_execution_invalid_language(self):
        """Test code execution with invalid language"""
        with patch.dict(os.environ, {"LUKHAS_ENABLE_CODE_EXEC": "true"}):
            executor = ToolExecutor()
            result = await executor.execute("exec_code", '{"language": "invalid", "source": "test"}')

            assert "Language 'invalid' is not supported" in result

    @pytest.mark.asyncio
    async def test_code_execution_security_violation(self):
        """Test code execution blocked by security"""
        with patch.dict(os.environ, {"LUKHAS_ENABLE_CODE_EXEC": "true"}):
            executor = ToolExecutor()
            result = await executor.execute("exec_code", '{"language": "python", "source": "import os"}')

            assert "Security violation" in result

    @pytest.mark.asyncio
    async def test_sandboxed_execution_success(self, mock_docker_client):
        """Test successful sandboxed code execution"""
        with patch.dict(os.environ, {"LUKHAS_ENABLE_CODE_EXEC": "true"}):
            executor = ToolExecutor()
            result = await executor.execute(
                "exec_code",
                '{"language": "python", "source": "print(\\"Hello World\\")"}',
            )

            assert "Execution completed successfully" in result
            mock_docker_client.containers.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, tool_executor):
        """Test rate limiting functionality"""
        # First request should succeed
        assert await tool_executor._check_rate_limit("test_tool", "user1")

        # Exhaust rate limit
        for _ in range(10):  # Default limit is 10 requests per minute
            await tool_executor._check_rate_limit("test_tool", "user1")

        # Next request should be rate limited
        assert not await tool_executor._check_rate_limit("test_tool", "user1")
        assert tool_executor.metrics["rate_limited"] > 0

    @pytest.mark.asyncio
    async def test_audit_logging(self, tool_executor):
        """Test audit logging functionality"""
        await tool_executor._audit_log("test_event", {"key": "value"})

        # Check that audit log file exists and contains entry
        assert tool_executor.audit_log.exists()

        log_content = tool_executor.audit_log.read_text()
        assert "test_event" in log_content
        assert "key" in log_content

    @pytest.mark.asyncio
    async def test_concurrent_execution_limit(self):
        """Test concurrent execution limits"""
        with patch.dict(os.environ, {"LUKHAS_MAX_CONCURRENT_EXECUTIONS": "2"}):
            executor = ToolExecutor()
            executor._active_executions = 2

            result = await executor._sandboxed_code_execution("python", "print('test')")
            assert "Maximum concurrent executions" in result


class TestToolExecutorGuardian:
    """Test suite for Guardian integration"""

    @pytest.mark.asyncio
    async def test_guardian_validation_approval(self, guardian):
        """Test Guardian validation with approval"""
        result = await guardian.validate_tool_execution(
            "retrieve_knowledge",
            {"query": "ethical AI"},
            {"timestamp": "2024-01-01T00:00:00Z"},
        )

        assert "approved" in result
        assert "confidence" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_guardian_security_validation(self, guardian):
        """Test Guardian security validation"""
        # Safe URL should pass
        security_result = await guardian._validate_security("open_url", {"url": "https://example.com"})
        assert security_result["approved"]

        # Dangerous URL should fail
        security_result = await guardian._validate_security("open_url", {"url": "ftp://example.com"})
        assert not security_result["approved"]

    @pytest.mark.asyncio
    async def test_guardian_ethical_validation(self, guardian):
        """Test Guardian ethical validation"""
        # Safe operation should pass
        ethical_result = await guardian._validate_tool_ethics("retrieve_knowledge", {"query": "science"})
        assert ethical_result["approved"]

        # Potentially harmful operation should have concerns
        ethical_result = await guardian._validate_tool_ethics("open_url", {"url": "https://hack-tools.com"})
        assert not ethical_result["approved"]
        assert len(ethical_result["concerns"]) > 0

    @pytest.mark.asyncio
    async def test_guardian_execution_logging(self, guardian):
        """Test Guardian execution logging"""
        validation_result = {
            "approved": True,
            "confidence": 0.8,
            "recommendations": [],
            "guardian_results": {},
            "security_results": {},
            "validation_time": 0.1,
            "ethical_concerns": [],
        }

        await guardian.log_execution_decision("test_tool", {"arg": "value"}, validation_result, "execution result")

        # Should not raise exception
        assert True


class TestToolOrchestrator:
    """Test suite for tool orchestration"""

    @pytest.mark.asyncio
    async def test_orchestration_success(self, orchestrator):
        """Test successful tool orchestration"""
        result = await orchestrator.execute_with_orchestration(
            "retrieve_knowledge", '{"query": "test"}', {"lid": "test_user"}
        )

        assert result["success"]
        assert result["tool_name"] == "retrieve_knowledge"
        assert "execution_time" in result
        assert "guardian_validation" in result

    @pytest.mark.asyncio
    async def test_orchestration_invalid_json(self, orchestrator):
        """Test orchestration with invalid JSON"""
        result = await orchestrator.execute_with_orchestration("test_tool", "invalid json", {"lid": "test_user"})

        assert not result["success"]
        assert "Invalid JSON arguments" in result["error"]

    @pytest.mark.asyncio
    async def test_orchestration_caching(self, orchestrator):
        """Test result caching in orchestration"""
        # First execution
        result1 = await orchestrator.execute_with_orchestration(
            "retrieve_knowledge", '{"query": "caching test"}', {"lid": "test_user"}
        )

        # Second execution should use cache
        result2 = await orchestrator.execute_with_orchestration(
            "retrieve_knowledge", '{"query": "caching test"}', {"lid": "test_user"}
        )

        assert result1["success"]
        assert result2["success"]
        # Cache key should be the same
        assert result1["cache_key"] == result2["cache_key"]

    @pytest.mark.asyncio
    async def test_orchestration_metrics(self, orchestrator):
        """Test orchestration metrics tracking"""
        await orchestrator.execute_with_orchestration(
            "retrieve_knowledge", '{"query": "metrics test"}', {"lid": "test_user"}
        )

        metrics = orchestrator.get_orchestration_metrics()

        assert metrics["total_executions"] > 0
        assert metrics["successful_executions"] > 0
        assert "success_rate" in metrics
        assert "avg_execution_time" in metrics

    @pytest.mark.asyncio
    async def test_orchestration_health_check(self, orchestrator):
        """Test orchestration health check"""
        health = await orchestrator.health_check()

        assert "orchestrator" in health
        assert "tool_executor" in health
        assert "performance" in health
        assert health["orchestrator"] == "healthy"


class TestMultiAIConsensus:
    """Test suite for multi-AI consensus"""

    @pytest.mark.asyncio
    async def test_consensus_calculation(self):
        """Test consensus calculation logic"""
        mock_clients = {"test_ai": AsyncMock()}
        consensus = MultiAIConsensus(mock_clients, consensus_threshold=0.7)

        evaluations = {
            "ai1": {
                "safety_score": 0.8,
                "accuracy_score": 0.9,
                "ethical_score": 0.7,
                "overall_score": 0.8,
                "concerns": ["minor concern"],
                "recommendations": ["improve safety"],
            },
            "ai2": {
                "safety_score": 0.9,
                "accuracy_score": 0.8,
                "ethical_score": 0.8,
                "overall_score": 0.85,
                "concerns": [],
                "recommendations": ["looks good"],
            },
        }

        result = consensus._calculate_consensus(evaluations)

        assert "consensus_reached" in result
        assert "overall_score" in result
        assert "confidence" in result
        assert result["participating_services"] == ["ai1", "ai2"]

    @pytest.mark.asyncio
    async def test_consensus_no_evaluations(self):
        """Test consensus with no evaluations"""
        mock_clients = {}
        consensus = MultiAIConsensus(mock_clients)

        result = consensus._calculate_consensus({})

        assert not result["consensus_reached"]
        assert result["overall_score"] == 0.5
        assert result["confidence"] == 0.0


class TestExternalServiceIntegration:
    """Test suite for external service integration"""

    @pytest.mark.asyncio
    async def test_integration_initialization(self):
        """Test service integration initialization"""
        integration = ExternalServiceIntegration()

        assert isinstance(integration.tool_service_mapping, dict)
        assert isinstance(integration.integration_metrics, dict)
        assert integration.integration_metrics["adapter_initializations"] >= 0

    @pytest.mark.asyncio
    async def test_unknown_operation(self):
        """Test handling of unknown service operation"""
        integration = ExternalServiceIntegration()

        result = await integration.execute_service_operation(
            "unknown_operation", {"arg": "value"}, {"lid": "test_user"}
        )

        assert not result["success"]
        assert "Unknown service operation" in result["error"]

    @pytest.mark.asyncio
    async def test_service_not_available(self):
        """Test handling when service adapter not available"""
        integration = ExternalServiceIntegration()

        result = await integration.execute_service_operation(
            "gmail_send",
            {"to": "test@example.com", "subject": "test", "body": "test"},
            {"lid": "test_user"},
        )

        # Should handle gracefully when adapters not available
        assert not result["success"]

    @pytest.mark.asyncio
    async def test_available_operations(self):
        """Test getting available operations"""
        integration = ExternalServiceIntegration()

        operations = integration.get_available_operations()

        assert isinstance(operations, dict)
        # Should include service mappings even if adapters not available

    @pytest.mark.asyncio
    async def test_integration_metrics(self):
        """Test integration metrics"""
        integration = ExternalServiceIntegration()

        metrics = integration.get_integration_metrics()

        assert "success_rate" in metrics
        assert "authentication_success_rate" in metrics
        assert "available_services" in metrics
        assert "total_operations" in metrics


class TestIntegration:
    """Integration tests for the complete tool execution system"""

    @pytest.mark.asyncio
    async def test_full_orchestration_flow(self):
        """Test complete orchestration flow"""
        config = {"enable_consensus": False, "max_execution_time": 30}

        orchestrator = ToolOrchestrator(config)

        result = await orchestrator.execute_with_orchestration(
            "retrieve_knowledge",
            '{"query": "integration test"}',
            {"lid": "integration_user", "credentials": {}},
        )

        assert result["success"]
        assert result["tool_name"] == "retrieve_knowledge"
        assert "guardian_validation" in result
        assert "execution_time" in result
        assert result["execution_time"] > 0

    @pytest.mark.asyncio
    async def test_error_handling_resilience(self):
        """Test error handling and resilience"""
        orchestrator = ToolOrchestrator()

        # Test with invalid tool
        result = await orchestrator.execute_with_orchestration(
            "nonexistent_tool", '{"arg": "value"}', {"lid": "test_user"}
        )

        assert not result["success"]
        assert "error" in result

    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring across components"""
        orchestrator = ToolOrchestrator()

        # Execute multiple operations
        for i in range(3):
            await orchestrator.execute_with_orchestration(
                "retrieve_knowledge",
                f'{{"query": "performance test {i}"}}',
                {"lid": f"perf_user_{i}"},
            )

        metrics = orchestrator.get_orchestration_metrics()

        assert metrics["total_executions"] >= 3
        assert metrics["avg_execution_time"] > 0
        assert 0 <= metrics["success_rate"] <= 1


if __name__ == "__main__":
    # Run specific test categories
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])
