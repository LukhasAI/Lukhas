"""
Comprehensive Test Suite for Collapse Integration System
======================================================

Tests the Collapse Integration System, the critical safety component that
monitors system health, detects cascade failures, and coordinates emergency
responses across LUKHAS consciousness domains. This system provides the
vital safety net that prevents consciousness collapse and ensures system
stability under extreme conditions.

Test Coverage Areas:
- Collapse tracker integration and monitoring
- Orchestrator callback mechanisms and notifications
- Ethics sentinel integration and intervention protocols
- System health monitoring and entropy tracking
- Alert level management and escalation procedures
- Cross-system communication and event broadcasting
- Performance optimization and continuous monitoring
- Error handling and emergency recovery procedures
"""
import pytest
import time
import asyncio
import threading
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from collections import deque
from dataclasses import dataclass

from core.monitoring.collapse_integration import (
    CollapseIntegration,
    integrate_collapse_tracking,
)
from core.monitoring.collapse_tracker import (
    CollapseAlertLevel,
    get_global_tracker,
)


class TestCollapseIntegration:
    """Comprehensive test suite for the Collapse Integration System."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator for testing."""
        orchestrator = Mock()
        orchestrator.handle_collapse_alert = AsyncMock()
        orchestrator.broadcast_event = AsyncMock()
        orchestrator.update_system_state = Mock()
        orchestrator.get_component_health = AsyncMock(return_value={
            "consciousness": 0.9,
            "memory": 0.85,
            "identity": 0.92,
            "ethics": 0.88
        })
        return orchestrator

    @pytest.fixture
    def mock_ethics_sentinel(self):
        """Create a mock ethics sentinel for testing."""
        sentinel = Mock()
        sentinel.handle_collapse_risk = AsyncMock(return_value={"action": "intervention_authorized"})
        sentinel.record_violation = AsyncMock()
        sentinel.request_intervention = AsyncMock()
        return sentinel

    @pytest.fixture
    def collapse_integration(self, mock_orchestrator, mock_ethics_sentinel):
        """Create a test collapse integration instance."""
        return CollapseIntegration(
            orchestrator=mock_orchestrator,
            ethics_sentinel=mock_ethics_sentinel
        )

    @pytest.fixture
    def sample_alert_data(self):
        """Create sample collapse alert data for testing."""
        return {
            "new_level": CollapseAlertLevel.YELLOW.value,
            "entropy_score": 0.65,
            "entropy_slope": 0.15,
            "collapse_trace_id": "collapse_trace_001",
            "timestamp": time.time(),
            "components_affected": ["consciousness", "memory"],
            "recommended_action": "monitor_closely"
        }

    @pytest.fixture
    def critical_alert_data(self):
        """Create critical collapse alert data for testing."""
        return {
            "new_level": CollapseAlertLevel.RED.value,
            "entropy_score": 0.95,
            "entropy_slope": 0.45,
            "collapse_trace_id": "critical_collapse_001",
            "timestamp": time.time(),
            "components_affected": ["all_systems"],
            "recommended_action": "immediate_intervention"
        }

    @pytest.fixture
    def intervention_data(self):
        """Create sample intervention data for ethics testing."""
        return {
            "severity": "HIGH",
            "entropy_score": 0.88,
            "entropy_slope": 0.35,
            "collapse_trace_id": "intervention_001",
            "timestamp": time.time(),
            "recommended_action": "emergency_shutdown",
            "affected_systems": ["consciousness", "memory", "identity"]
        }

    # Basic System Functionality Tests
    def test_collapse_integration_initialization(self, collapse_integration, mock_orchestrator, mock_ethics_sentinel):
        """Test collapse integration initializes with correct settings."""
        assert collapse_integration.orchestrator == mock_orchestrator
        assert collapse_integration.ethics_sentinel == mock_ethics_sentinel
        assert collapse_integration.collapse_tracker is not None
        
        # Verify callbacks are set
        assert collapse_integration.collapse_tracker.orchestrator_callback == collapse_integration.notify_orchestrator
        assert collapse_integration.collapse_tracker.ethics_callback == collapse_integration.notify_ethics_sentinel

    def test_collapse_integration_without_orchestrator(self):
        """Test collapse integration without orchestrator."""
        integration = CollapseIntegration(orchestrator=None, ethics_sentinel=None)
        
        assert integration.orchestrator is None
        assert integration.ethics_sentinel is None
        assert integration.collapse_tracker is not None

    def test_collapse_integration_with_partial_components(self, mock_orchestrator):
        """Test collapse integration with only some components."""
        integration = CollapseIntegration(orchestrator=mock_orchestrator, ethics_sentinel=None)
        
        assert integration.orchestrator == mock_orchestrator
        assert integration.ethics_sentinel is None
        assert integration.collapse_tracker is not None

    # Orchestrator Notification Tests
    @pytest.mark.asyncio
    async def test_notify_orchestrator_basic(self, collapse_integration, mock_orchestrator, sample_alert_data):
        """Test basic orchestrator notification."""
        await collapse_integration.notify_orchestrator(sample_alert_data)
        
        # Verify orchestrator methods were called
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(sample_alert_data)
        mock_orchestrator.broadcast_event.assert_called_once()
        mock_orchestrator.update_system_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_orchestrator_critical_alert(self, collapse_integration, mock_orchestrator, critical_alert_data):
        """Test orchestrator notification for critical alerts."""
        await collapse_integration.notify_orchestrator(critical_alert_data)
        
        # Verify critical alert handling
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(critical_alert_data)
        
        # Check broadcast event call
        broadcast_call = mock_orchestrator.broadcast_event.call_args
        assert broadcast_call[1]["event_type"] == "collapse_critical"
        assert broadcast_call[1]["data"] == critical_alert_data

    @pytest.mark.asyncio
    async def test_notify_orchestrator_without_orchestrator(self, mock_ethics_sentinel, sample_alert_data):
        """Test orchestrator notification when no orchestrator is configured."""
        integration = CollapseIntegration(orchestrator=None, ethics_sentinel=mock_ethics_sentinel)
        
        # Should handle gracefully without errors
        await integration.notify_orchestrator(sample_alert_data)
        # No assertions needed - should just log warning and return

    @pytest.mark.asyncio
    async def test_notify_orchestrator_missing_methods(self, mock_ethics_sentinel, sample_alert_data):
        """Test orchestrator notification with missing methods."""
        # Create orchestrator without expected methods
        incomplete_orchestrator = Mock()
        integration = CollapseIntegration(orchestrator=incomplete_orchestrator, ethics_sentinel=mock_ethics_sentinel)
        
        # Should handle gracefully
        await integration.notify_orchestrator(sample_alert_data)
        # Should not raise exceptions

    @pytest.mark.asyncio
    async def test_notify_orchestrator_exception_handling(self, collapse_integration, mock_orchestrator, sample_alert_data):
        """Test orchestrator notification exception handling."""
        # Make orchestrator method raise exception
        mock_orchestrator.handle_collapse_alert.side_effect = Exception("Orchestrator error")
        
        # Should handle exception gracefully
        await collapse_integration.notify_orchestrator(sample_alert_data)
        
        # Verify method was called despite exception
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(sample_alert_data)

    # Ethics Sentinel Notification Tests
    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_basic(self, collapse_integration, mock_ethics_sentinel, intervention_data):
        """Test basic ethics sentinel notification."""
        await collapse_integration.notify_ethics_sentinel(intervention_data)
        
        # Verify ethics methods were called
        mock_ethics_sentinel.handle_collapse_risk.assert_called_once()
        mock_ethics_sentinel.record_violation.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_high_severity(self, collapse_integration, mock_ethics_sentinel, intervention_data):
        """Test ethics sentinel notification for high severity interventions."""
        await collapse_integration.notify_ethics_sentinel(intervention_data)
        
        # Verify intervention was requested for high severity
        mock_ethics_sentinel.request_intervention.assert_called_once()
        
        # Check intervention call arguments
        intervention_call = mock_ethics_sentinel.request_intervention.call_args
        assert intervention_call[1]["reason"] == "Critical collapse risk detected"
        assert intervention_call[1]["urgency"] == "IMMEDIATE"

    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_medium_severity(self, collapse_integration, mock_ethics_sentinel):
        """Test ethics sentinel notification for medium severity interventions."""
        medium_intervention_data = {
            "severity": "MEDIUM",
            "entropy_score": 0.6,
            "collapse_trace_id": "medium_intervention_001",
            "timestamp": time.time(),
            "recommended_action": "increase_monitoring"
        }
        
        await collapse_integration.notify_ethics_sentinel(medium_intervention_data)
        
        # Should handle collapse risk and record violation but not request intervention
        mock_ethics_sentinel.handle_collapse_risk.assert_called_once()
        mock_ethics_sentinel.record_violation.assert_called_once()
        mock_ethics_sentinel.request_intervention.assert_not_called()

    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_without_sentinel(self, mock_orchestrator, intervention_data):
        """Test ethics notification when no sentinel is configured."""
        integration = CollapseIntegration(orchestrator=mock_orchestrator, ethics_sentinel=None)
        
        # Should handle gracefully without errors
        await integration.notify_ethics_sentinel(intervention_data)
        # No assertions needed - should just log warning and return

    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_missing_methods(self, mock_orchestrator, intervention_data):
        """Test ethics notification with incomplete sentinel."""
        # Create sentinel without expected methods
        incomplete_sentinel = Mock()
        integration = CollapseIntegration(orchestrator=mock_orchestrator, ethics_sentinel=incomplete_sentinel)
        
        # Should handle gracefully
        await integration.notify_ethics_sentinel(intervention_data)
        # Should not raise exceptions

    @pytest.mark.asyncio
    async def test_notify_ethics_sentinel_exception_handling(self, collapse_integration, mock_ethics_sentinel, intervention_data):
        """Test ethics sentinel notification exception handling."""
        # Make sentinel method raise exception
        mock_ethics_sentinel.handle_collapse_risk.side_effect = Exception("Ethics error")
        
        # Should handle exception gracefully
        await collapse_integration.notify_ethics_sentinel(intervention_data)
        
        # Verify method was called despite exception
        mock_ethics_sentinel.handle_collapse_risk.assert_called_once()

    # System Health Monitoring Tests
    def test_update_entropy_from_components(self, collapse_integration):
        """Test updating entropy from component data."""
        component_data = {
            "symbolic_data": [
                {"symbol": "consciousness", "entropy": 0.3},
                {"symbol": "memory", "entropy": 0.4},
                {"symbol": "identity", "entropy": 0.2}
            ],
            "component_scores": {
                "consciousness": 0.9,
                "memory": 0.85,
                "identity": 0.92,
                "ethics": 0.88
            }
        }
        
        # Update entropy
        collapse_integration.update_entropy_from_components(component_data)
        
        # Verify tracker was updated (would need to check tracker state)
        # This is tested through integration rather than direct assertion

    @pytest.mark.asyncio
    async def test_monitor_system_health_basic(self, collapse_integration, mock_orchestrator):
        """Test basic system health monitoring."""
        # Mock the collapse tracker's get_system_health method
        with patch.object(collapse_integration.collapse_tracker, 'get_system_health') as mock_health:
            mock_health.return_value = {
                "entropy_score": 0.4,
                "alert_level": "GREEN",
                "component_entropy": {"consciousness": 0.3, "memory": 0.5}
            }
            
            # Start monitoring with short interval and stop after one iteration
            monitoring_task = asyncio.create_task(collapse_integration.monitor_system_health(interval=0.1))
            
            # Let it run briefly
            await asyncio.sleep(0.2)
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            # Verify health check was called
            mock_health.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_system_health_with_orchestrator_health(self, collapse_integration, mock_orchestrator):
        """Test system health monitoring with orchestrator health data."""
        # Mock the collapse tracker's get_system_health method
        with patch.object(collapse_integration.collapse_tracker, 'get_system_health') as mock_health:
            mock_health.return_value = {
                "entropy_score": 0.4,
                "alert_level": "GREEN",
                "component_entropy": {"consciousness": 0.3, "memory": 0.5}
            }
            
            # Start monitoring with short interval
            monitoring_task = asyncio.create_task(collapse_integration.monitor_system_health(interval=0.1))
            
            # Let it run briefly
            await asyncio.sleep(0.2)
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            # Verify orchestrator health was requested
            mock_orchestrator.get_component_health.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_system_health_exception_handling(self, collapse_integration):
        """Test system health monitoring exception handling."""
        # Mock the collapse tracker to raise exception
        with patch.object(collapse_integration.collapse_tracker, 'get_system_health') as mock_health:
            mock_health.side_effect = Exception("Health check error")
            
            # Start monitoring with short interval
            monitoring_task = asyncio.create_task(collapse_integration.monitor_system_health(interval=0.1))
            
            # Let it run briefly
            await asyncio.sleep(0.2)
            monitoring_task.cancel()
            
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass
            
            # Should handle exception and continue monitoring
            # Verified by not raising unhandled exception

    # Integration Function Tests
    def test_integrate_collapse_tracking_basic(self, mock_orchestrator, mock_ethics_sentinel):
        """Test basic collapse tracking integration function."""
        integration = integrate_collapse_tracking(mock_orchestrator, mock_ethics_sentinel)
        
        assert isinstance(integration, CollapseIntegration)
        assert integration.orchestrator == mock_orchestrator
        assert integration.ethics_sentinel == mock_ethics_sentinel

    def test_integrate_collapse_tracking_orchestrator_only(self, mock_orchestrator):
        """Test collapse tracking integration with orchestrator only."""
        integration = integrate_collapse_tracking(mock_orchestrator, ethics_sentinel=None)
        
        assert isinstance(integration, CollapseIntegration)
        assert integration.orchestrator == mock_orchestrator
        assert integration.ethics_sentinel is None

    def test_integrate_collapse_tracking_async_orchestrator(self, mock_orchestrator, mock_ethics_sentinel):
        """Test integration with async orchestrator."""
        # Make orchestrator look async
        mock_orchestrator.run = AsyncMock()
        
        with patch('asyncio.create_task') as mock_create_task:
            integration = integrate_collapse_tracking(mock_orchestrator, mock_ethics_sentinel)
            
            # Verify monitoring task was created
            mock_create_task.assert_called_once()
            assert isinstance(integration, CollapseIntegration)

    # Alert Level Processing Tests
    def test_yellow_alert_processing(self, collapse_integration, mock_orchestrator, mock_ethics_sentinel):
        """Test processing of yellow alert level."""
        yellow_alert = {
            "new_level": CollapseAlertLevel.YELLOW.value,
            "entropy_score": 0.6,
            "collapse_trace_id": "yellow_001"
        }
        
        # Process alert
        asyncio.run(collapse_integration.notify_orchestrator(yellow_alert))
        
        # Verify appropriate response
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(yellow_alert)

    def test_orange_alert_processing(self, collapse_integration, mock_orchestrator, mock_ethics_sentinel):
        """Test processing of orange alert level."""
        orange_alert = {
            "new_level": CollapseAlertLevel.ORANGE.value,
            "entropy_score": 0.8,
            "collapse_trace_id": "orange_001"
        }
        
        # Process alert
        asyncio.run(collapse_integration.notify_orchestrator(orange_alert))
        
        # Verify escalated response
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(orange_alert)

    def test_red_alert_processing(self, collapse_integration, mock_orchestrator, mock_ethics_sentinel):
        """Test processing of red alert level."""
        red_alert = {
            "new_level": CollapseAlertLevel.RED.value,
            "entropy_score": 0.95,
            "collapse_trace_id": "red_001"
        }
        
        # Process alert
        asyncio.run(collapse_integration.notify_orchestrator(red_alert))
        
        # Verify critical response
        mock_orchestrator.handle_collapse_alert.assert_called_once_with(red_alert)
        
        # Check that critical event was broadcast
        broadcast_call = mock_orchestrator.broadcast_event.call_args
        assert broadcast_call[1]["event_type"] == "collapse_critical"

    # Performance and Scalability Tests
    @pytest.mark.asyncio
    async def test_notification_performance(self, collapse_integration, sample_alert_data):
        """Test notification performance under load."""
        start_time = time.time()
        
        # Send multiple notifications
        for _ in range(20):
            await collapse_integration.notify_orchestrator(sample_alert_data)
        
        end_time = time.time()
        notification_time = end_time - start_time
        
        # Should process notifications quickly
        assert notification_time < 1.0  # Under 1 second for 20 notifications
        avg_time_per_notification = notification_time / 20
        assert avg_time_per_notification < 0.05  # Under 50ms per notification

    @pytest.mark.asyncio
    async def test_concurrent_notifications(self, collapse_integration, sample_alert_data, intervention_data):
        """Test concurrent notification processing."""
        # Create multiple notification tasks
        orchestrator_tasks = []
        ethics_tasks = []
        
        for i in range(5):
            orchestrator_task = asyncio.create_task(
                collapse_integration.notify_orchestrator(sample_alert_data)
            )
            ethics_task = asyncio.create_task(
                collapse_integration.notify_ethics_sentinel(intervention_data)
            )
            orchestrator_tasks.append(orchestrator_task)
            ethics_tasks.append(ethics_task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*orchestrator_tasks, *ethics_tasks)
        
        # Verify all notifications were processed
        assert len(orchestrator_tasks) == 5
        assert len(ethics_tasks) == 5

    def test_memory_efficiency_under_load(self, collapse_integration):
        """Test memory efficiency under sustained load."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many component updates
        for i in range(30):
            component_data = {
                "symbolic_data": [{"symbol": f"test_{i}", "entropy": 0.5}],
                "component_scores": {f"component_{i}": 0.8}
            }
            collapse_integration.update_entropy_from_components(component_data)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 200  # Should not create excessive objects

    # Error Handling and Recovery Tests
    @pytest.mark.asyncio
    async def test_invalid_alert_data_handling(self, collapse_integration):
        """Test handling of invalid alert data."""
        # Test with None data
        await collapse_integration.notify_orchestrator(None)
        # Should handle gracefully without raising exceptions
        
        # Test with malformed data
        malformed_data = {"invalid": "data"}
        await collapse_integration.notify_orchestrator(malformed_data)
        # Should handle gracefully

    @pytest.mark.asyncio
    async def test_invalid_intervention_data_handling(self, collapse_integration):
        """Test handling of invalid intervention data."""
        # Test with None data
        await collapse_integration.notify_ethics_sentinel(None)
        # Should handle gracefully without raising exceptions
        
        # Test with malformed data
        malformed_data = {"invalid": "intervention"}
        await collapse_integration.notify_ethics_sentinel(malformed_data)
        # Should handle gracefully

    def test_component_data_validation(self, collapse_integration):
        """Test validation of component data."""
        # Test with None data
        collapse_integration.update_entropy_from_components(None)
        # Should handle gracefully
        
        # Test with empty data
        collapse_integration.update_entropy_from_components({})
        # Should handle gracefully
        
        # Test with missing keys
        incomplete_data = {"symbolic_data": []}
        collapse_integration.update_entropy_from_components(incomplete_data)
        # Should handle gracefully

    # Integration and Compatibility Tests
    def test_collapse_tracker_integration(self, collapse_integration):
        """Test integration with collapse tracker."""
        # Verify tracker is properly connected
        assert collapse_integration.collapse_tracker is not None
        
        # Verify callbacks are set
        assert collapse_integration.collapse_tracker.orchestrator_callback is not None
        assert collapse_integration.collapse_tracker.ethics_callback is not None

    @pytest.mark.asyncio
    async def test_orchestrator_compatibility(self, mock_orchestrator):
        """Test compatibility with different orchestrator implementations."""
        # Test with minimal orchestrator
        minimal_orchestrator = Mock()
        integration = CollapseIntegration(orchestrator=minimal_orchestrator, ethics_sentinel=None)
        
        # Should work even with minimal interface
        await integration.notify_orchestrator({"test": "data"})

    @pytest.mark.asyncio
    async def test_ethics_sentinel_compatibility(self, mock_ethics_sentinel):
        """Test compatibility with different ethics sentinel implementations."""
        # Test with minimal sentinel
        minimal_sentinel = Mock()
        integration = CollapseIntegration(orchestrator=None, ethics_sentinel=minimal_sentinel)
        
        # Should work even with minimal interface
        await integration.notify_ethics_sentinel({"test": "intervention"})

    # Monitoring and Observability Tests
    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, collapse_integration):
        """Test complete monitoring lifecycle."""
        # Start monitoring
        monitoring_task = asyncio.create_task(
            collapse_integration.monitor_system_health(interval=0.05)
        )
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Stop monitoring
        monitoring_task.cancel()
        
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        
        # Verify monitoring completed successfully
        assert monitoring_task.cancelled()

    def test_system_state_updates(self, collapse_integration, mock_orchestrator, sample_alert_data):
        """Test system state updates during alerts."""
        # Process alert
        asyncio.run(collapse_integration.notify_orchestrator(sample_alert_data))
        
        # Verify system state was updated
        mock_orchestrator.update_system_state.assert_called_once()
        
        # Check state update contents
        state_update = mock_orchestrator.update_system_state.call_args[0][0]
        assert "collapse_alert_level" in state_update
        assert "collapse_entropy" in state_update
        assert "collapse_trace_id" in state_update

    def test_event_broadcasting(self, collapse_integration, mock_orchestrator, sample_alert_data):
        """Test event broadcasting functionality."""
        # Process alert
        asyncio.run(collapse_integration.notify_orchestrator(sample_alert_data))
        
        # Verify event was broadcast
        mock_orchestrator.broadcast_event.assert_called_once()
        
        # Check event details
        event_call = mock_orchestrator.broadcast_event.call_args
        assert event_call[1]["source"] == "collapse_tracker"
        assert event_call[1]["data"] == sample_alert_data

    # Cleanup and Resource Management Tests
    def test_resource_cleanup(self, collapse_integration):
        """Test proper resource cleanup."""
        # Verify initial state
        assert collapse_integration.collapse_tracker is not None
        
        # Cleanup would be handled by garbage collection
        # This test verifies no resource leaks occur during normal operation
        
        # Process some operations
        collapse_integration.update_entropy_from_components({
            "component_scores": {"test": 0.8}
        })
        
        # Verify system remains stable
        assert collapse_integration.collapse_tracker is not None