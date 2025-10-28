"""
Comprehensive Test Suite for Dashboard Widget System
==================================================

Tests the complete dashboard widget functionality including widget lifecycle,
permission management, data streaming, and integration with the main dashboard.
This test suite validates the TODO item resolution for dashboard widget integration.

Test Coverage Areas:
- Widget lifecycle management (register, update, unregister)
- Permission-based widget access control
- Real-time data streaming and updates
- Widget health monitoring and error handling
- Integration with BrainDashboard identity panels
- Widget manager orchestration and cleanup
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from core.orchestration.brain.dashboard.dashboard_widgets import (
    DashboardWidgetManager,
    DashboardWidget,
    IdentityStatusWidget,
    OrchestrationStatusWidget,
    SystemMetricsWidget,
    WidgetConfig,
    WidgetPermissionLevel,
    WidgetStatus,
    WidgetData,
    create_default_widgets,
)
from core.orchestration.brain.dashboard.main_dashboard import (
    BrainDashboard,
    DashboardIdentityView,
)


class TestDashboardWidgetSystem:
    """Comprehensive test suite for the dashboard widget system."""

    @pytest.fixture
    def widget_config(self):
        """Create a test widget configuration."""
        return WidgetConfig(
            widget_id="test_widget",
            name="Test Widget",
            description="Widget for testing",
            permission_level=WidgetPermissionLevel.AUTHENTICATED,
            refresh_interval=1.0,
            max_data_points=10,
            enable_streaming=True,
            tags={"test", "monitoring"}
        )

    @pytest.fixture
    def mock_identity_manager(self):
        """Create a mock identity manager."""
        manager = Mock()
        manager.describe_permissions = AsyncMock(return_value={
            "user_id": "test_user",
            "attributes": {"display_name": "Test User"},
            "tier_level": 1,
            "scopes": ["read", "write"],
            "active_sessions": ["session_1", "session_2"]
        })
        return manager

    @pytest.fixture
    def widget_manager(self):
        """Create a dashboard widget manager."""
        return DashboardWidgetManager()

    @pytest.fixture
    def identity_widget(self, widget_config, mock_identity_manager):
        """Create an identity status widget."""
        config = WidgetConfig(
            widget_id="identity_status",
            name="Identity Status",
            description="Identity monitoring widget",
            permission_level=WidgetPermissionLevel.AUTHENTICATED,
            refresh_interval=2.0
        )
        return IdentityStatusWidget(config, mock_identity_manager)

    # Widget Configuration Tests
    def test_widget_config_creation(self, widget_config):
        """Test widget configuration creation and validation."""
        assert widget_config.widget_id == "test_widget"
        assert widget_config.name == "Test Widget"
        assert widget_config.permission_level == WidgetPermissionLevel.AUTHENTICATED
        assert widget_config.refresh_interval == 1.0
        assert widget_config.max_data_points == 10
        assert widget_config.enable_streaming is True
        assert "test" in widget_config.tags
        assert "monitoring" in widget_config.tags

    def test_widget_permission_levels(self):
        """Test widget permission level enumeration."""
        assert WidgetPermissionLevel.PUBLIC.value == "public"
        assert WidgetPermissionLevel.AUTHENTICATED.value == "authenticated"
        assert WidgetPermissionLevel.TIER_1.value == "tier_1"
        assert WidgetPermissionLevel.TIER_2.value == "tier_2"
        assert WidgetPermissionLevel.ADMIN.value == "admin"

    def test_widget_status_enumeration(self):
        """Test widget status enumeration."""
        assert WidgetStatus.INITIALIZING.value == "initializing"
        assert WidgetStatus.ACTIVE.value == "active"
        assert WidgetStatus.PAUSED.value == "paused"
        assert WidgetStatus.ERROR.value == "error"
        assert WidgetStatus.TERMINATED.value == "terminated"

    # Identity Status Widget Tests
    @pytest.mark.asyncio
    async def test_identity_widget_initialization(self, identity_widget, mock_identity_manager):
        """Test identity status widget initialization."""
        # Test successful initialization
        success = await identity_widget.initialize()
        
        assert success is True
        assert identity_widget.status == WidgetStatus.ACTIVE
        assert identity_widget.identity_manager == mock_identity_manager

    @pytest.mark.asyncio
    async def test_identity_widget_initialization_failure(self, widget_config):
        """Test identity widget initialization with failed identity manager."""
        # Test with None identity manager
        widget = IdentityStatusWidget(widget_config, None)
        success = await widget.initialize()
        
        assert success is False
        assert widget.status == WidgetStatus.ERROR

    @pytest.mark.asyncio
    async def test_identity_widget_data_update(self, identity_widget):
        """Test identity widget data updates."""
        # Initialize widget
        await identity_widget.initialize()
        
        # Update data
        widget_data = await identity_widget.update_data()
        
        # Verify data structure
        assert isinstance(widget_data, WidgetData)
        assert widget_data.widget_id == identity_widget.config.widget_id
        assert isinstance(widget_data.timestamp, datetime)
        assert "active_sessions" in widget_data.data
        assert "total_users" in widget_data.data
        assert "authentication_rate" in widget_data.data
        assert "tier_distribution" in widget_data.data
        
        # Verify metadata
        assert widget_data.metadata["source"] == "identity_manager"
        
        # Verify widget state
        assert identity_widget.last_update is not None
        assert len(identity_widget.data_history) == 1

    @pytest.mark.asyncio
    async def test_identity_widget_data_history_trimming(self, identity_widget):
        """Test identity widget data history trimming."""
        # Set small max_data_points for testing
        identity_widget.config.max_data_points = 3
        await identity_widget.initialize()
        
        # Add multiple data points
        for i in range(5):
            await identity_widget.update_data()
            await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Verify history is trimmed
        assert len(identity_widget.data_history) == 3
        assert identity_widget.data_history[0].timestamp < identity_widget.data_history[-1].timestamp

    @pytest.mark.asyncio
    async def test_identity_widget_cleanup(self, identity_widget):
        """Test identity widget cleanup."""
        await identity_widget.initialize()
        await identity_widget.update_data()
        
        # Cleanup widget
        await identity_widget.cleanup()
        
        # Verify cleanup
        assert identity_widget.status == WidgetStatus.TERMINATED
        assert len(identity_widget.data_history) == 0

    # Orchestration Status Widget Tests
    @pytest.mark.asyncio
    async def test_orchestration_widget_functionality(self):
        """Test orchestration status widget functionality."""
        config = WidgetConfig(
            widget_id="orchestration_status",
            name="Orchestration Status",
            description="Orchestration monitoring",
            permission_level=WidgetPermissionLevel.TIER_1
        )
        widget = OrchestrationStatusWidget(config)
        
        # Test initialization
        success = await widget.initialize()
        assert success is True
        assert widget.status == WidgetStatus.ACTIVE
        
        # Test data update
        widget_data = await widget.update_data()
        assert isinstance(widget_data, WidgetData)
        assert "active_orchestrations" in widget_data.data
        assert "completed_today" in widget_data.data
        assert "error_rate" in widget_data.data
        assert "system_health" in widget_data.data
        assert "resource_usage" in widget_data.data
        
        # Test cleanup
        await widget.cleanup()
        assert widget.status == WidgetStatus.TERMINATED

    # System Metrics Widget Tests
    @pytest.mark.asyncio
    async def test_system_metrics_widget_functionality(self):
        """Test system metrics widget functionality."""
        config = WidgetConfig(
            widget_id="system_metrics",
            name="System Metrics",
            description="System performance monitoring",
            permission_level=WidgetPermissionLevel.TIER_2
        )
        widget = SystemMetricsWidget(config)
        
        # Test initialization
        success = await widget.initialize()
        assert success is True
        assert widget.status == WidgetStatus.ACTIVE
        
        # Test data update
        widget_data = await widget.update_data()
        assert isinstance(widget_data, WidgetData)
        assert "response_time_p95" in widget_data.data
        assert "response_time_p99" in widget_data.data
        assert "requests_per_second" in widget_data.data
        assert "error_rate" in widget_data.data
        assert "uptime_seconds" in widget_data.data
        
        # Test cleanup
        await widget.cleanup()
        assert widget.status == WidgetStatus.TERMINATED

    # Widget Manager Tests
    @pytest.mark.asyncio
    async def test_widget_manager_registration(self, widget_manager, identity_widget):
        """Test widget registration with widget manager."""
        # Register widget
        success = await widget_manager.register_widget(identity_widget)
        
        assert success is True
        assert identity_widget.config.widget_id in widget_manager.widgets
        assert identity_widget.config.widget_id in widget_manager.update_tasks

    @pytest.mark.asyncio
    async def test_widget_manager_unregistration(self, widget_manager, identity_widget):
        """Test widget unregistration from widget manager."""
        # Register then unregister
        await widget_manager.register_widget(identity_widget)
        success = await widget_manager.unregister_widget(identity_widget.config.widget_id)
        
        assert success is True
        assert identity_widget.config.widget_id not in widget_manager.widgets
        assert identity_widget.config.widget_id not in widget_manager.update_tasks

    @pytest.mark.asyncio
    async def test_widget_manager_get_widget_data(self, widget_manager, identity_widget):
        """Test getting widget data through manager."""
        await widget_manager.register_widget(identity_widget)
        
        # Wait for at least one update
        await asyncio.sleep(0.1)
        
        # Get widget data with sufficient permissions
        data = await widget_manager.get_widget_data(
            identity_widget.config.widget_id, 
            user_tier=1
        )
        
        assert data is not None
        assert isinstance(data, WidgetData)

    @pytest.mark.asyncio
    async def test_widget_manager_permission_check(self, widget_manager, identity_widget):
        """Test widget permission checking."""
        await widget_manager.register_widget(identity_widget)
        
        # Test with insufficient permissions
        data = await widget_manager.get_widget_data(
            identity_widget.config.widget_id,
            user_tier=0  # Below required tier
        )
        
        # Should still work for AUTHENTICATED level with tier 0
        assert data is not None
        
        # Test with tier-restricted widget
        tier2_config = WidgetConfig(
            widget_id="tier2_widget",
            name="Tier 2 Widget", 
            description="Tier 2 only",
            permission_level=WidgetPermissionLevel.TIER_2
        )
        tier2_widget = SystemMetricsWidget(tier2_config)
        await widget_manager.register_widget(tier2_widget)
        
        # Test with insufficient tier
        data = await widget_manager.get_widget_data("tier2_widget", user_tier=1)
        assert data is None
        
        # Test with sufficient tier
        data = await widget_manager.get_widget_data("tier2_widget", user_tier=2)
        assert data is not None

    @pytest.mark.asyncio
    async def test_widget_manager_get_all_widget_data(self, widget_manager, mock_identity_manager):
        """Test getting all widget data with permission filtering."""
        # Create widgets with different permission levels
        widgets = create_default_widgets(mock_identity_manager)
        
        for widget in widgets:
            await widget_manager.register_widget(widget)
        
        # Wait for updates
        await asyncio.sleep(0.1)
        
        # Test with tier 1 user
        all_data = await widget_manager.get_all_widget_data(user_tier=1)
        
        # Should get identity and orchestration widgets, but not system metrics (tier 2)
        assert "identity_status" in all_data
        assert "orchestration_status" in all_data
        assert "system_metrics" not in all_data
        
        # Test with tier 2 user
        all_data_tier2 = await widget_manager.get_all_widget_data(user_tier=2)
        
        # Should get all widgets
        assert "identity_status" in all_data_tier2
        assert "orchestration_status" in all_data_tier2
        assert "system_metrics" in all_data_tier2

    @pytest.mark.asyncio
    async def test_widget_manager_health_monitoring(self, widget_manager, identity_widget):
        """Test widget manager health monitoring."""
        await widget_manager.register_widget(identity_widget)
        
        # Get health status
        health = widget_manager.get_widget_health()
        
        assert identity_widget.config.widget_id in health
        widget_health = health[identity_widget.config.widget_id]
        assert "widget_id" in widget_health
        assert "status" in widget_health
        assert "error_count" in widget_health

    @pytest.mark.asyncio
    async def test_widget_manager_lifecycle(self, widget_manager, mock_identity_manager):
        """Test complete widget manager lifecycle."""
        # Start manager
        await widget_manager.start()
        assert widget_manager.is_running is True
        
        # Register widgets
        widgets = create_default_widgets(mock_identity_manager)
        for widget in widgets:
            await widget_manager.register_widget(widget)
        
        # Verify widgets are registered and running
        assert len(widget_manager.widgets) == 3
        assert len(widget_manager.update_tasks) == 3
        
        # Stop manager
        await widget_manager.stop()
        assert widget_manager.is_running is False
        assert len(widget_manager.widgets) == 0
        assert len(widget_manager.update_tasks) == 0

    # Dashboard Integration Tests
    @pytest.mark.asyncio
    async def test_brain_dashboard_with_widgets(self, mock_identity_manager):
        """Test BrainDashboard integration with widget system."""
        # Create widget manager and register widgets
        widget_manager = DashboardWidgetManager()
        await widget_manager.start()
        
        widgets = create_default_widgets(mock_identity_manager)
        for widget in widgets:
            await widget_manager.register_widget(widget)
        
        # Create dashboard with widget manager
        dashboard = BrainDashboard(
            identity_manager=mock_identity_manager,
            widget_manager=widget_manager
        )
        
        # Wait for widget updates
        await asyncio.sleep(0.1)
        
        # Build identity panel
        panel = await dashboard.build_identity_panel("test_user")
        
        # Verify widget integration
        assert panel["status"] == "ok"
        assert "widgets" in panel
        assert isinstance(panel["widgets"], dict)
        
        # Should have identity and orchestration widgets for tier 1 user
        widget_ids = list(panel["widgets"].keys())
        assert "identity_status" in widget_ids
        assert "orchestration_status" in widget_ids
        
        # Cleanup
        await widget_manager.stop()

    @pytest.mark.asyncio
    async def test_brain_dashboard_without_widgets(self, mock_identity_manager):
        """Test BrainDashboard functionality without widget manager."""
        dashboard = BrainDashboard(identity_manager=mock_identity_manager)
        
        # Build identity panel
        panel = await dashboard.build_identity_panel("test_user")
        
        # Verify basic functionality still works
        assert panel["status"] == "ok"
        assert "identity" in panel
        assert "widgets" in panel
        assert panel["widgets"] == {}  # Empty widgets when no manager

    @pytest.mark.asyncio
    async def test_brain_dashboard_widget_error_handling(self, mock_identity_manager):
        """Test BrainDashboard error handling with failing widget manager."""
        # Create widget manager that will fail
        widget_manager = Mock()
        widget_manager.get_all_widget_data = AsyncMock(side_effect=Exception("Widget error"))
        
        dashboard = BrainDashboard(
            identity_manager=mock_identity_manager,
            widget_manager=widget_manager
        )
        
        # Build identity panel (should handle widget error gracefully)
        panel = await dashboard.build_identity_panel("test_user")
        
        # Verify error is handled gracefully
        assert panel["status"] == "ok"
        assert "widgets" in panel
        assert panel["widgets"] == {}  # Empty on error

    # Widget Factory Tests
    def test_create_default_widgets(self, mock_identity_manager):
        """Test creation of default dashboard widgets."""
        widgets = create_default_widgets(mock_identity_manager)
        
        assert len(widgets) == 3
        
        # Check widget types
        widget_types = [type(widget).__name__ for widget in widgets]
        assert "IdentityStatusWidget" in widget_types
        assert "OrchestrationStatusWidget" in widget_types
        assert "SystemMetricsWidget" in widget_types
        
        # Check widget IDs
        widget_ids = [widget.config.widget_id for widget in widgets]
        assert "identity_status" in widget_ids
        assert "orchestration_status" in widget_ids
        assert "system_metrics" in widget_ids

    # Performance and Error Handling Tests
    @pytest.mark.asyncio
    async def test_widget_error_recovery(self, widget_manager):
        """Test widget error recovery and circuit breaking."""
        # Create a widget that will fail
        config = WidgetConfig(
            widget_id="failing_widget",
            name="Failing Widget",
            description="Widget that fails",
            permission_level=WidgetPermissionLevel.AUTHENTICATED,
            refresh_interval=0.1  # Fast refresh for testing
        )
        
        class FailingWidget(DashboardWidget):
            def __init__(self, config):
                super().__init__(config)
                self.update_count = 0
            
            async def initialize(self):
                self.status = WidgetStatus.ACTIVE
                return True
            
            async def update_data(self):
                self.update_count += 1
                if self.update_count <= 3:
                    raise Exception("Simulated failure")
                
                # Succeed after 3 failures
                return WidgetData(
                    widget_id=self.config.widget_id,
                    timestamp=datetime.now(timezone.utc),
                    data={"status": "recovered"}
                )
            
            async def cleanup(self):
                self.status = WidgetStatus.TERMINATED
        
        failing_widget = FailingWidget(config)
        await widget_manager.start()
        await widget_manager.register_widget(failing_widget)
        
        # Wait for error accumulation
        await asyncio.sleep(0.5)
        
        # Check that widget accumulated errors but didn't crash manager
        assert failing_widget.error_count > 0
        assert failing_widget.status in [WidgetStatus.ACTIVE, WidgetStatus.ERROR]
        
        await widget_manager.stop()

    @pytest.mark.asyncio
    async def test_widget_performance_under_load(self, widget_manager, mock_identity_manager):
        """Test widget system performance under load."""
        # Register multiple widgets
        widgets = []
        for i in range(10):
            config = WidgetConfig(
                widget_id=f"load_test_widget_{i}",
                name=f"Load Test Widget {i}",
                description="Widget for load testing",
                permission_level=WidgetPermissionLevel.AUTHENTICATED,
                refresh_interval=0.1  # Fast refresh
            )
            widget = IdentityStatusWidget(config, mock_identity_manager)
            widgets.append(widget)
        
        await widget_manager.start()
        
        # Register all widgets concurrently
        registration_tasks = [
            widget_manager.register_widget(widget) for widget in widgets
        ]
        results = await asyncio.gather(*registration_tasks)
        
        # All should register successfully
        assert all(results)
        assert len(widget_manager.widgets) == 10
        
        # Wait for updates
        await asyncio.sleep(0.2)
        
        # Get all widget data
        all_data = await widget_manager.get_all_widget_data(user_tier=1)
        assert len(all_data) == 10
        
        await widget_manager.stop()

    @pytest.mark.asyncio
    async def test_widget_cleanup_on_manager_stop(self, widget_manager, mock_identity_manager):
        """Test proper cleanup when widget manager stops."""
        widgets = create_default_widgets(mock_identity_manager)
        
        await widget_manager.start()
        for widget in widgets:
            await widget_manager.register_widget(widget)
        
        # Verify widgets are active
        for widget in widgets:
            assert widget.status == WidgetStatus.ACTIVE
        
        # Stop manager
        await widget_manager.stop()
        
        # Verify all widgets are terminated
        for widget in widgets:
            assert widget.status == WidgetStatus.TERMINATED
            assert len(widget.data_history) == 0