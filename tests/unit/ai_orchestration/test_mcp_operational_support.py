import pytest
from unittest.mock import MagicMock, patch
from ai_orchestration.mcp_operational_support import (
    LUKHASMCPOperationalSupport,
    MCPServerContext,
    OperationalMetrics,
    SupportIncident,
)

@pytest.fixture
def operational_support():
    """Fixture for LUKHASMCPOperationalSupport."""
    return LUKHASMCPOperationalSupport()

@pytest.mark.mcp_operational
class TestLUKHASMCPOperationalSupport:
    def test_monitor_mcp_operations(self, operational_support):
        with patch("psutil.cpu_percent") as mock_cpu, patch(
            "psutil.virtual_memory"
        ) as mock_mem:
            # Configure mocks
            mock_cpu.return_value = 50.0
            mock_mem.return_value.percent = 60.0
            mock_mem.return_value.used = 3 * 1024 * 1024 * 1024  # 3GB

            server_context = MCPServerContext()
            server_context.active_connections = 15
            server_context.requests_per_minute = 200
            server_context.error_rate = 0.05

            result = operational_support.monitor_mcp_operations(server_context)

            assert isinstance(result, OperationalMetrics)
            assert result.metrics["cpu_usage_percent"] == 50.0
            assert result.metrics["memory_usage_percent"] == 60.0
            assert result.metrics["active_connections"] == 15

    def test_analyze_operational_patterns_no_history(self, operational_support):
        result = operational_support.analyze_operational_patterns([])
        assert result.findings == ["Not enough metrics history to analyze."]

    def test_analyze_operational_patterns_increasing_cpu(self, operational_support):
        metrics_history = [
            OperationalMetrics({"cpu_usage_percent": 10}),
            OperationalMetrics({"cpu_usage_percent": 20}),
            OperationalMetrics({"cpu_usage_percent": 30}),
            OperationalMetrics({"cpu_usage_percent": 85}), # also triggers high usage
        ]
        result = operational_support.analyze_operational_patterns(metrics_history)
        assert "Increasing CPU usage trend detected (slope: 22.00)." in result.findings
        assert "High CPU usage detected in 1 instances." in result.findings

    def test_automate_support_workflows_restart(self, operational_support):
        incident = SupportIncident("INC-001", "Service is unresponsive, restart required.")
        result = operational_support.automate_support_workflows(incident)
        assert result.success is True
        assert "Service restart workflow triggered" in result.message

    def test_automate_support_workflows_high_memory(self, operational_support):
        incident = SupportIncident("INC-002", "High memory usage detected.")
        result = operational_support.automate_support_workflows(incident)
        assert result.success is True
        assert "Cache clearing workflow triggered" in result.message

    def test_automate_support_workflows_unhandled(self, operational_support):
        incident = SupportIncident("INC-003", "A strange thing happened.")
        result = operational_support.automate_support_workflows(incident)
        assert result.success is False
        assert "Support ticket TICKET-INC-003 created" in result.message
