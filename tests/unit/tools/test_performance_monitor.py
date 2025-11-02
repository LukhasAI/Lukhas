# owner: Jules-08
# tier: tier3
# module_uid: candidate.tools.performance_monitor
# criticality: P1

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from labs.tools.performance_monitor import (
    PerformanceAnalyzer,
    PerformanceMonitor,
    PerformanceOptimizer,
    SystemMetricsCollector,
    ToolExecutionMetricsCollector,
)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# --- Fixtures ---

@pytest.fixture
def mock_psutil():
    """Fixture to mock psutil functions."""
    with patch('labs.tools.performance_monitor.psutil') as mock_psutil_module:
        # Mock CPU
        mock_psutil_module.cpu_percent.return_value = 50.0

        # Mock Memory
        mock_mem = MagicMock()
        mock_mem.percent = 60.0
        mock_mem.available = 2 * 1024 * 1024 * 1024 # 2 GB
        mock_psutil_module.virtual_memory.return_value = mock_mem

        # Mock Disk
        mock_disk = MagicMock()
        mock_disk.read_bytes = 100 * 1024 * 1024
        mock_disk.write_bytes = 50 * 1024 * 1024
        mock_psutil_module.disk_io_counters.return_value = mock_disk

        # Mock Network
        mock_net = MagicMock()
        mock_net.bytes_sent = 1000 * 1024
        mock_net.bytes_recv = 5000 * 1024
        mock_psutil_module.net_io_counters.return_value = mock_net

        # Mock PIDs
        mock_psutil_module.pids.return_value = [1, 2, 3] * 50 # 150 processes

        yield mock_psutil_module

# --- Test Classes ---

@pytest.mark.tier3
@pytest.mark.performance
@pytest.mark.monitoring
class TestSystemMetricsCollector:
    """Tests for the SystemMetricsCollector."""

    async def test_collect_system_metrics(self, mock_psutil):
        """Tests that system metrics are collected and formatted correctly."""
        collector = SystemMetricsCollector()
        metrics = await collector.collect()

        assert len(metrics) == 7

        metrics_by_name = {m.metric_name: m for m in metrics}

        # CPU
        assert "cpu_usage" in metrics_by_name
        assert metrics_by_name["cpu_usage"].value == 50.0
        assert metrics_by_name["cpu_usage"].unit == "percent"

        # Memory
        assert "memory_usage" in metrics_by_name
        assert metrics_by_name["memory_usage"].value == 60.0
        assert metrics_by_name["memory_usage"].context["available_mb"] == 2048

        # Disk
        assert "disk_read_mb_per_sec" in metrics_by_name
        assert metrics_by_name["disk_read_mb_per_sec"].value == 100.0

        # Network
        assert "network_bytes_sent" in metrics_by_name
        assert metrics_by_name["network_bytes_sent"].value == 1000 * 1024

        # Process count
        assert "process_count" in metrics_by_name
        assert metrics_by_name["process_count"].value == 150


@pytest.mark.tier3
@pytest.mark.performance
@pytest.mark.monitoring
class TestToolExecutionMetricsCollector:
    """Tests for the ToolExecutionMetricsCollector."""

    async def test_collect_tool_metrics(self):
        """Tests recording and collecting tool execution metrics."""
        collector = ToolExecutionMetricsCollector()

        # Record some data
        collector.record_execution("tool_a", 2.5, success=True)
        collector.record_execution("tool_a", 3.5, success=True)
        collector.record_execution("tool_b", 10.0, success=False)

        metrics = await collector.collect()

        assert len(metrics) == 10 # 5 metrics per tool
        metrics_by_tool_and_name = {
            (m.component, m.metric_name): m for m in metrics
        }

        # Check tool_a metrics
        assert metrics_by_tool_and_name[("tool_tool_a", "avg_execution_time")].value == 3.0
        assert metrics_by_tool_and_name[("tool_tool_a", "max_execution_time")].value == 3.5
        assert metrics_by_tool_and_name[("tool_tool_a", "execution_count")].value == 2
        assert metrics_by_tool_and_name[("tool_tool_a", "error_rate")].value == 0.0

        # Check tool_b metrics
        assert metrics_by_tool_and_name[("tool_tool_b", "avg_execution_time")].value == 10.0
        assert metrics_by_tool_and_name[("tool_tool_b", "error_count")].value == 1
        assert metrics_by_tool_and_name[("tool_tool_b", "error_rate")].value == 1.0


@pytest.mark.tier3
@pytest.mark.performance
@pytest.mark.monitoring
class TestPerformanceAnalyzer:
    """Tests for the PerformanceAnalyzer."""

    def test_analyze_metrics_and_generate_alerts(self):
        """Tests that alerts are generated when metrics exceed thresholds."""
        from labs.tools.performance_monitor import PerformanceMetric
        analyzer = PerformanceAnalyzer()

        # Create metrics that should trigger alerts
        metrics = [
            PerformanceMetric(1, "cpu_usage", 85.0, "percent", "system"), # warning
            PerformanceMetric(2, "memory_usage", 96.0, "percent", "system"), # critical
            PerformanceMetric(3, "avg_execution_time", 12.0, "seconds", "tool_slow_tool"), # critical
            PerformanceMetric(4, "error_rate", 0.15, "ratio", "tool_flaky_tool"), # warning
            PerformanceMetric(5, "cpu_usage", 50.0, "percent", "system"), # normal
        ]

        alerts = analyzer.analyze_metrics(metrics)

        assert len(alerts) == 4

        alerts_by_metric = {a.metric_name: a for a in alerts}
        assert alerts_by_metric["cpu_usage"].severity == "warning"
        assert alerts_by_metric["memory_usage"].severity == "critical"
        assert alerts_by_metric["avg_execution_time"].severity == "critical"
        assert alerts_by_metric["error_rate"].severity == "warning"


@pytest.mark.tier3
@pytest.mark.performance
@pytest.mark.monitoring
class TestPerformanceOptimizer:
    """Tests for the PerformanceOptimizer."""

    def test_generate_recommendations(self):
        """Tests that correct recommendations are generated from metrics."""
        from labs.tools.performance_monitor import PerformanceMetric
        optimizer = PerformanceOptimizer()

        metrics = [
            PerformanceMetric(1, "cpu_usage", 90.0, "percent", "system"),
            PerformanceMetric(2, "error_rate", 0.2, "ratio", "tool_flaky_tool"),
        ]

        recommendations = optimizer.generate_recommendations(metrics)

        assert len(recommendations) == 2
        rec_names = {r["name"] for r in recommendations}
        assert "high_cpu_usage" in rec_names
        assert "high_error_rate" in rec_names


@pytest.mark.tier3
@pytest.mark.performance
@pytest.mark.monitoring
class TestPerformanceMonitor:
    """Integration tests for the main PerformanceMonitor class."""

    @patch('builtins.open')
    @patch('labs.tools.performance_monitor.asyncio.sleep', return_value=None)
    async def test_monitor_integration_loop(self, mock_sleep, mock_open, mock_psutil):
        """
        Tests the full integration of the PerformanceMonitor, including the
        collection and analysis loop.
        """
        # --- Setup ---
        monitor = PerformanceMonitor(config={"analysis_interval": 10})

        # Mock psutil to return high values to trigger alerts
        mock_psutil.cpu_percent.return_value = 98.0

        # --- Act ---
        # Run the monitoring loop for a short period in the background
        monitoring_task = asyncio.create_task(monitor.start_monitoring())

        # Let the loop run a couple of times
        # The loop will call our mocked asyncio.sleep, which returns immediately
        await asyncio.sleep(0.1)
        await asyncio.sleep(0.1)
        await asyncio.sleep(0.1)

        # Stop the monitor
        monitor.stop_monitoring()
        # Wait for the task to finish cancelling
        try:
            await asyncio.wait_for(monitoring_task, timeout=1.0)
        except asyncio.CancelledError:
            pass # This is expected

        # --- Assert ---
        # Check the final status of the monitor
        status = monitor.get_current_status()
        assert status["monitoring_active"] is False
        assert status["last_analysis"] is not None

        # Check that alerts were generated
        last_analysis = status["last_analysis"]
        assert len(last_analysis["alerts"]) > 0
        assert any(a["metric_name"] == "cpu_usage" and a["severity"] == "critical" for a in last_analysis["alerts"])

        # Check that recommendations were generated
        assert len(last_analysis["recommendations"]) > 0
        assert any(r["name"] == "high_cpu_usage" for r in last_analysis["recommendations"])

        # Test exporting a report
        report_path = await monitor.export_performance_report()
        assert report_path.endswith(".json")
        mock_open.assert_called_with(report_path, "w")
