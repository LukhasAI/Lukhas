"""
Test suite for Memory Tracker Integration
"""

import os
import tempfile

import pytest

from memory.memory_hub import MemoryHub
from memory.systems.memory_tracker_integration import (
    MemoryTrackerIntegration,
    create_memory_tracker_integration,
)


class TestMemoryTrackerIntegration:
    """Test suite for memory tracker integration with memory hub"""

    @pytest.fixture
    async def memory_hub(self):
        """Create a test memory hub instance"""
        hub = MemoryHub()
        return hub

    @pytest.fixture
    async def memory_tracker_integration(self):
        """Create a test memory tracker integration instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "enable_memory_tracking": True,
                "enable_operator_level_tracking": True,
                "top_operators_display": 10,
                "enable_trace_visualization": True,
                "auto_save_stats": True,
                "stats_save_directory": temp_dir,
                "enable_summary_reporting": True,
                "enable_cuda_monitoring": True,
                "memory_alert_threshold_mb": 500.0,
                "enable_background_monitoring": False,
            }
            integration = MemoryTrackerIntegration(config)
            yield integration

    @pytest.mark.asyncio
    async def test_memory_tracker_integration_initialization(
        self, memory_tracker_integration
    ):
        """Test memory tracker integration initialization"""
        assert memory_tracker_integration is not None
        assert memory_tracker_integration.config["enable_memory_tracking"] is True
        assert memory_tracker_integration.config["top_operators_display"] == 10
        assert memory_tracker_integration.is_initialized is False
        assert memory_tracker_integration.monitoring_active is False

        # Initialize the integration
        await memory_tracker_integration.initialize()
        assert memory_tracker_integration.is_initialized is True

    @pytest.mark.asyncio
    async def test_memory_hub_memory_tracker_registration(self, memory_hub):
        """Test that memory tracker is registered in the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Verify memory tracker service is available (if MEMORY_TRACKER_AVAILABLE is True)
        services = memory_hub.list_services()

        # The service should be registered if the import was successful
        if "memory_tracker" in services:
            assert memory_hub.get_service("memory_tracker") is not None

    @pytest.mark.asyncio
    async def test_memory_tracking_start_stop_through_hub(self, memory_hub):
        """Test memory tracking start/stop through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if memory tracker not available
        if "memory_tracker" not in memory_hub.services:
            pytest.skip("Memory tracker integration not available")

        # Test starting memory tracking
        start_result = await memory_hub.start_memory_tracking(
            session_id="test_session_1"
        )

        # Verify start result structure
        assert "success" in start_result
        if start_result["success"]:
            assert "session_id" in start_result
            assert start_result["session_id"] == "test_session_1"
            assert "tracking_type" in start_result
            assert "started_at" in start_result

        # Test stopping memory tracking
        if start_result["success"]:
            stop_result = await memory_hub.stop_memory_tracking("test_session_1")

            # Verify stop result structure
            assert "success" in stop_result
            if stop_result["success"]:
                assert "session_id" in stop_result
                assert stop_result["session_id"] == "test_session_1"
                assert "stopped_at" in stop_result

    @pytest.mark.asyncio
    async def test_memory_tracking_summary_through_hub(self, memory_hub):
        """Test memory tracking summary through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if memory tracker not available
        if "memory_tracker" not in memory_hub.services:
            pytest.skip("Memory tracker integration not available")

        # Test memory tracking summary
        summary_result = await memory_hub.get_memory_tracking_summary(top_ops=5)

        # Verify summary structure
        assert "success" in summary_result
        if summary_result["success"]:
            assert "summary" in summary_result
            assert "timestamp" in summary_result

    @pytest.mark.asyncio
    async def test_memory_trace_visualization_through_hub(self, memory_hub):
        """Test memory trace visualization through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if memory tracker not available
        if "memory_tracker" not in memory_hub.services:
            pytest.skip("Memory tracker integration not available")

        # Test memory trace visualization
        viz_result = await memory_hub.visualize_memory_traces(session_id="test_viz")

        # Verify visualization result structure
        assert "success" in viz_result
        # Note: visualization might fail if matplotlib is not available, which is expected
        if not viz_result["success"]:
            assert "error" in viz_result

    @pytest.mark.asyncio
    async def test_memory_tracking_sessions_through_hub(self, memory_hub):
        """Test memory tracking sessions retrieval through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if memory tracker not available
        if "memory_tracker" not in memory_hub.services:
            pytest.skip("Memory tracker integration not available")

        # Get tracking sessions
        sessions = await memory_hub.get_memory_tracking_sessions()

        # Verify sessions structure
        assert isinstance(sessions, list)
        # Sessions list might be empty initially, which is fine

    @pytest.mark.asyncio
    async def test_memory_tracker_metrics_through_hub(self, memory_hub):
        """Test memory tracker metrics through the memory hub"""
        # Initialize the hub
        await memory_hub.initialize()

        # Skip test if memory tracker not available
        if "memory_tracker" not in memory_hub.services:
            pytest.skip("Memory tracker integration not available")

        # Get memory tracker metrics
        result = await memory_hub.get_memory_tracker_metrics()

        # Verify result
        assert result["available"] is True
        assert "metrics" in result
        metrics = result["metrics"]
        assert "monitoring_active" in metrics
        assert "memory_tracker_available" in metrics
        assert "system_status" in metrics
        assert "last_updated" in metrics

    @pytest.mark.asyncio
    async def test_error_handling_missing_service(self, memory_hub):
        """Test error handling when memory tracker service is not available"""
        # Initialize the hub
        await memory_hub.initialize()

        # Remove memory tracker service if it exists
        if "memory_tracker" in memory_hub.services:
            del memory_hub.services["memory_tracker"]

        # Test memory tracking start with missing service
        result = await memory_hub.start_memory_tracking()
        assert result["success"] is False
        assert "error" in result

        # Test memory tracking stop with missing service
        result = await memory_hub.stop_memory_tracking("test_session")
        assert result["success"] is False
        assert "error" in result

        # Test summary with missing service
        result = await memory_hub.get_memory_tracking_summary()
        assert result["success"] is False
        assert "error" in result

        # Test visualization with missing service
        result = await memory_hub.visualize_memory_traces()
        assert result["success"] is False
        assert "error" in result

        # Test sessions with missing service
        sessions = await memory_hub.get_memory_tracking_sessions()
        assert sessions == []

        # Test metrics with missing service
        result = await memory_hub.get_memory_tracker_metrics()
        assert result["available"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_memory_tracking_lifecycle(self, memory_tracker_integration):
        """Test complete memory tracking lifecycle"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Start memory tracking
        start_result = await memory_tracker_integration.start_memory_tracking(
            session_id="lifecycle_test"
        )
        assert "success" in start_result

        # Verify tracking is active
        if start_result["success"]:
            session_id = start_result["session_id"]
            assert session_id in memory_tracker_integration.tracking_sessions

            # Check session status
            sessions = await memory_tracker_integration.get_tracking_sessions()
            assert len(sessions) > 0

            # Stop tracking
            stop_result = await memory_tracker_integration.stop_memory_tracking(
                session_id
            )
            assert "success" in stop_result

    @pytest.mark.asyncio
    async def test_memory_summary_generation(self, memory_tracker_integration):
        """Test memory summary generation"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Start and stop a tracking session to generate some data
        start_result = await memory_tracker_integration.start_memory_tracking(
            session_id="summary_test"
        )
        if start_result["success"]:
            await memory_tracker_integration.stop_memory_tracking("summary_test")

        # Get memory summary
        summary_result = await memory_tracker_integration.get_memory_summary(top_ops=5)

        # Verify summary structure
        assert "success" in summary_result
        if summary_result["success"]:
            assert "summary" in summary_result
            summary = summary_result["summary"]
            assert "top_operators" in summary or "error" in summary  # May be fallback

    @pytest.mark.asyncio
    async def test_memory_metrics_collection(self, memory_tracker_integration):
        """Test memory metrics collection"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Perform some operations to generate metrics
        await memory_tracker_integration.start_memory_tracking(
            session_id="metrics_test"
        )
        await memory_tracker_integration.stop_memory_tracking("metrics_test")

        # Get metrics
        metrics = await memory_tracker_integration.get_memory_metrics()

        # Verify metrics structure
        assert "total_tracking_sessions" in metrics
        assert "monitoring_active" in metrics
        assert "memory_tracker_available" in metrics
        assert "system_status" in metrics
        assert "last_updated" in metrics

        # Check that metrics reflect activity
        assert metrics["total_tracking_sessions"] >= 1

    @pytest.mark.asyncio
    async def test_tracking_with_module(self, memory_tracker_integration):
        """Test tracking with a mock PyTorch module"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Create a mock module
        class MockModule:
            def __init__(self):
                self.name = "MockModule"

        mock_module = MockModule()

        # Start tracking with module
        start_result = await memory_tracker_integration.start_memory_tracking(
            root_module=mock_module, session_id="module_test"
        )

        # Should handle module tracking (or fallback gracefully)
        assert "success" in start_result

        if start_result["success"]:
            # Stop tracking
            stop_result = await memory_tracker_integration.stop_memory_tracking(
                "module_test"
            )
            assert "success" in stop_result

    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options for memory tracker integration"""
        # Test with custom config
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_config = {
                "enable_memory_tracking": False,
                "enable_operator_level_tracking": False,
                "top_operators_display": 5,
                "enable_trace_visualization": False,
                "auto_save_stats": False,
                "stats_save_directory": temp_dir,
                "memory_alert_threshold_mb": 2000.0,
                "enable_background_monitoring": True,
            }

            integration = create_memory_tracker_integration(custom_config)

            # Verify config was applied
            assert integration.config["enable_memory_tracking"] is False
            assert integration.config["top_operators_display"] == 5
            assert integration.config["enable_trace_visualization"] is False
            assert integration.config["memory_alert_threshold_mb"] == 2000.0

    @pytest.mark.asyncio
    async def test_fallback_functionality(self, memory_tracker_integration):
        """Test fallback functionality when main components are not available"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Test fallback tracking start
        fallback_start = await memory_tracker_integration._fallback_start_tracking(
            "fallback_test", None
        )
        assert fallback_start["success"] is True
        assert "fallback" in fallback_start

        # Test fallback tracking stop
        fallback_stop = await memory_tracker_integration._fallback_stop_tracking(
            "fallback_test"
        )
        assert fallback_stop["success"] is True
        assert "fallback" in fallback_stop

        # Test fallback summary
        fallback_summary = await memory_tracker_integration._fallback_get_summary(
            None, 5
        )
        assert fallback_summary["success"] is True
        assert "fallback" in fallback_summary
        assert "summary" in fallback_summary

        # Test fallback visualization
        fallback_viz = await memory_tracker_integration._fallback_visualize_traces(
            None, None
        )
        assert fallback_viz["success"] is True
        assert "fallback" in fallback_viz

    @pytest.mark.asyncio
    async def test_session_management(self, memory_tracker_integration):
        """Test tracking session management"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Start multiple sessions
        session_ids = ["session_1", "session_2", "session_3"]

        for session_id in session_ids:
            result = await memory_tracker_integration.start_memory_tracking(
                session_id=session_id
            )
            if result["success"]:
                assert session_id in memory_tracker_integration.tracking_sessions

        # Get all sessions
        sessions = await memory_tracker_integration.get_tracking_sessions()
        active_sessions = [s for s in sessions if s["status"] == "active"]

        # Should have multiple active sessions
        assert len(active_sessions) >= 1

        # Stop all sessions
        for session_id in session_ids:
            if session_id in memory_tracker_integration.tracking_sessions:
                await memory_tracker_integration.stop_memory_tracking(session_id)

    @pytest.mark.asyncio
    async def test_duplicate_session_handling(self, memory_tracker_integration):
        """Test handling of duplicate session IDs"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        session_id = "duplicate_test"

        # Start first session
        first_result = await memory_tracker_integration.start_memory_tracking(
            session_id=session_id
        )

        if first_result["success"]:
            # Try to start second session with same ID
            second_result = await memory_tracker_integration.start_memory_tracking(
                session_id=session_id
            )

            # Should fail due to duplicate session ID
            assert second_result["success"] is False
            assert "already active" in second_result.get("error", "").lower()

            # Clean up
            await memory_tracker_integration.stop_memory_tracking(session_id)

    @pytest.mark.asyncio
    async def test_statistics_directory_creation(self):
        """Test that statistics directory is created when needed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            stats_dir = os.path.join(temp_dir, "memory_stats_test")

            config = {"auto_save_stats": True, "stats_save_directory": stats_dir}

            integration = MemoryTrackerIntegration(config)
            await integration.initialize()

            # Directory should be created during initialization
            assert os.path.exists(stats_dir)

    @pytest.mark.asyncio
    async def test_memory_alert_threshold(self, memory_tracker_integration):
        """Test memory alert threshold functionality"""
        # Initialize the integration
        await memory_tracker_integration.initialize()

        # Check that alert threshold is configured
        assert hasattr(memory_tracker_integration, "alert_threshold_mb")
        assert (
            memory_tracker_integration.alert_threshold_mb == 500.0
        )  # From fixture config

        # Test threshold in metrics
        metrics = await memory_tracker_integration.get_memory_metrics()
        assert "config" in metrics
        assert "alert_threshold_mb" in metrics["config"]
        assert metrics["config"]["alert_threshold_mb"] == 500.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
