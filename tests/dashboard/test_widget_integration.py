#!/usr/bin/env python3
"""
Brain Dashboard Widget Integration Tests

Tests live dashboard widget functionality, auto-refresh, data staleness,
and integration with identity services.

# ΛTAG: dashboard_tests, widget_integration, live_dashboard
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

try:
    from core.identity.vault.lukhas_id import IdentityManager, IdentityVerificationError
    from core.orchestration.brain.dashboard.main_dashboard import (
        BrainDashboard,
        DashboardIdentityView,
        DashboardWidget,
    )

    DASHBOARD_AVAILABLE = True
except ImportError:
    # Fallback for testing without full dashboard system
    DASHBOARD_AVAILABLE = False
    BrainDashboard = None
    DashboardWidget = None
    DashboardIdentityView = None
    IdentityManager = None
    IdentityVerificationError = Exception


@pytest.mark.skipif(not DASHBOARD_AVAILABLE, reason="Dashboard system not available")
class TestBrainDashboardWidgets:
    """Test live dashboard widget functionality."""

    @pytest.fixture
    def mock_identity_manager(self):
        """Create mock identity manager."""
        manager = Mock(spec=IdentityManager)
        manager.describe_permissions = AsyncMock(
            return_value={
                "user_id": "test_user",
                "tier_level": 2,
                "attributes": {"display_name": "Test User"},
                "scopes": ["core:read", "core:write"],
                "active_sessions": ["session_1", "session_2"],
            }
        )
        return manager

    @pytest.fixture
    def dashboard(self, mock_identity_manager):
        """Create dashboard instance with mock identity manager."""
        return BrainDashboard(identity_manager=mock_identity_manager)

    @pytest.mark.asyncio
    async def test_widget_registration_basic(self, dashboard):
        """Test basic widget registration."""

        await dashboard.register_widget(
            widget_id="test_widget", widget_type="metrics", title="Test Metrics", refresh_interval_ms=1000
        )

        # Verify widget was registered
        widget_data = await dashboard.get_widget_data("test_widget")
        assert widget_data is not None
        assert widget_data["widget_id"] == "test_widget"
        assert widget_data["type"] == "metrics"
        assert widget_data["title"] == "Test Metrics"
        assert widget_data["refresh_interval_ms"] == 1000

    @pytest.mark.asyncio
    async def test_widget_auto_refresh(self, dashboard):
        """Test widget auto-refresh functionality."""

        call_count = 0

        async def mock_data_source():
            nonlocal call_count
            call_count += 1
            return {"value": call_count, "timestamp": time.time()}

        # Register widget with auto-refresh
        await dashboard.register_widget(
            widget_id="auto_refresh_widget",
            widget_type="status",
            title="Auto Refresh Status",
            refresh_interval_ms=100,  # Fast refresh for testing
            data_source_fn=mock_data_source,
        )

        # Wait for multiple refresh cycles
        await asyncio.sleep(0.35)  # Should trigger ~3 refreshes

        # Verify data source was called multiple times
        assert call_count >= 2, f"Data source should be called multiple times, got {call_count}"

        # Verify widget data reflects latest call
        widget_data = await dashboard.get_widget_data("auto_refresh_widget")
        assert widget_data["data"]["value"] >= 2

    @pytest.mark.asyncio
    async def test_widget_staleness_detection(self, dashboard):
        """Test widget staleness detection."""

        # Register widget without auto-refresh
        await dashboard.register_widget(
            widget_id="stale_widget", widget_type="table", title="Stale Data Widget", refresh_interval_ms=1000
        )

        # Get initial widget data
        widget_data = await dashboard.get_widget_data("stale_widget")
        assert not widget_data["is_stale"], "Fresh widget should not be stale"

        # Mock time passage to make widget stale
        with patch("time.time", return_value=time.time() + 10):  # 10 seconds later
            widget_data = await dashboard.get_widget_data("stale_widget")
            assert widget_data["is_stale"], "Old widget should be marked as stale"

    @pytest.mark.asyncio
    async def test_widget_error_handling(self, dashboard):
        """Test error handling in widget data sources."""

        call_count = 0

        async def failing_data_source():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception(f"Simulated error {call_count}")
            return {"value": "success", "attempt": call_count}

        # Register widget with failing data source
        await dashboard.register_widget(
            widget_id="error_widget",
            widget_type="graph",
            title="Error Handling Widget",
            refresh_interval_ms=50,  # Fast refresh for testing
            data_source_fn=failing_data_source,
        )

        # Wait for error recovery
        await asyncio.sleep(0.3)  # Allow time for errors and recovery

        # Verify widget eventually succeeds
        assert call_count >= 3, "Data source should be called multiple times through errors"

        widget_data = await dashboard.get_widget_data("error_widget")
        # Widget should exist even if data source failed
        assert widget_data is not None

    @pytest.mark.asyncio
    async def test_identity_panel_with_widgets(self, dashboard, mock_identity_manager):
        """Test identity panel integration with widgets."""

        # Register test widgets
        await dashboard.register_widget(
            widget_id="identity_metrics", widget_type="metrics", title="Identity Metrics", refresh_interval_ms=1000
        )

        await dashboard.register_widget(
            widget_id="session_status", widget_type="status", title="Session Status", refresh_interval_ms=500
        )

        # Build identity panel
        panel = await dashboard.build_identity_panel("test_user")

        # Verify panel structure
        assert panel["status"] == "ok"
        assert "identity" in panel
        assert "widgets" in panel
        assert "timestamp" in panel

        # Verify widgets are included
        assert len(panel["widgets"]) == 2
        widget_ids = [w["widget_id"] for w in panel["widgets"]]
        assert "identity_metrics" in widget_ids
        assert "session_status" in widget_ids

    @pytest.mark.asyncio
    async def test_get_all_widgets(self, dashboard):
        """Test getting all registered widgets."""

        # Register multiple widgets
        widgets_to_register = [
            ("widget_1", "metrics", "Widget 1"),
            ("widget_2", "status", "Widget 2"),
            ("widget_3", "graph", "Widget 3"),
        ]

        for widget_id, widget_type, title in widgets_to_register:
            await dashboard.register_widget(
                widget_id=widget_id, widget_type=widget_type, title=title, refresh_interval_ms=1000
            )

        # Get all widgets
        all_widgets = await dashboard.get_all_widgets()

        # Verify all widgets are returned
        assert len(all_widgets) == 3
        returned_ids = [w["widget_id"] for w in all_widgets]
        for widget_id, _, _ in widgets_to_register:
            assert widget_id in returned_ids

    @pytest.mark.asyncio
    async def test_widget_data_persistence(self, dashboard):
        """Test that widget data persists between calls."""

        initial_data = {"counter": 1, "status": "active"}

        def sync_data_source():
            return initial_data

        await dashboard.register_widget(
            widget_id="persistent_widget",
            widget_type="table",
            title="Persistent Widget",
            refresh_interval_ms=1000,
            data_source_fn=sync_data_source,
        )

        # Wait for initial data load
        await asyncio.sleep(0.1)

        # Get widget data multiple times
        widget_data_1 = await dashboard.get_widget_data("persistent_widget")
        widget_data_2 = await dashboard.get_widget_data("persistent_widget")

        # Verify data consistency
        assert widget_data_1["data"] == widget_data_2["data"]
        assert widget_data_1["data"]["counter"] == 1
        assert widget_data_1["data"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_identity_error_handling(self, dashboard):
        """Test dashboard behavior when identity service fails."""

        # Configure identity manager to fail
        dashboard.identity_manager.describe_permissions = AsyncMock(
            side_effect=IdentityVerificationError("Identity service unavailable")
        )

        # Attempt to build identity panel
        panel = await dashboard.build_identity_panel("failing_user")

        # Verify graceful error handling
        assert panel["status"] == "error"
        assert panel["user_id"] == "failing_user"
        assert "message" in panel
        assert "Identity unavailable" in panel["message"]

    def test_dashboard_widget_staleness_logic(self):
        """Test widget staleness detection logic."""

        current_time = time.time() * 1000  # Current time in milliseconds

        # Create fresh widget
        fresh_widget = DashboardWidget(
            widget_id="fresh", widget_type="metrics", title="Fresh Widget", data={}, last_updated=current_time
        )

        # Create stale widget
        stale_widget = DashboardWidget(
            widget_id="stale",
            widget_type="metrics",
            title="Stale Widget",
            data={},
            last_updated=current_time - 10000,  # 10 seconds ago
        )

        # Test staleness with default threshold (5 seconds)
        assert not fresh_widget.is_stale(), "Fresh widget should not be stale"
        assert stale_widget.is_stale(), "Old widget should be stale"

        # Test with custom threshold
        assert not stale_widget.is_stale(threshold_ms=15000), "Widget should not be stale with higher threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
