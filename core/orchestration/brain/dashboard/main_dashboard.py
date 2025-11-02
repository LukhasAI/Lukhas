from __future__ import annotations

"""Symbolic dashboard integration for the orchestration brain."""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

from core.identity.vault.lukhas_id import (
    IdentityManager,
    IdentityVerificationError,
)

logger = structlog.get_logger(__name__)


# ΛTAG: dashboard_widget_model
@dataclass(slots=True)
class DashboardWidget:
    """Live dashboard widget with real-time data streams."""

    widget_id: str
    widget_type: str  # 'metrics', 'status', 'graph', 'table'
    title: str
    data: Dict[str, Any]
    last_updated: float
    refresh_interval_ms: int = 1000

    def is_stale(self, threshold_ms: int = 5000) -> bool:
        """Check if widget data is stale beyond threshold."""
        return (time.time() * 1000 - self.last_updated) > threshold_ms


# ΛTAG: dashboard_identity_model
@dataclass(slots=True)
class DashboardIdentityView:
    """Materialised view of identity information for dashboard rendering."""

    user_id: str
    display_name: str
    tier_level: int
    scopes: list[str]
    active_sessions: list[str]


# ΛTAG: dashboard_identity_panel
class BrainDashboard:
    """Dashboard service responsible for composing orchestration views."""

    def __init__(self, identity_manager: Optional[IdentityManager] = None) -> None:
        self.identity_manager = identity_manager or IdentityManager()
        self._widgets: Dict[str, DashboardWidget] = {}
        self._widget_refresh_tasks: Dict[str, asyncio.Task] = {}

    async def register_widget(
        self,
        widget_id: str,
        widget_type: str,
        title: str,
        refresh_interval_ms: int = 1000,
        data_source_fn: Optional[callable] = None
    ) -> None:
        """Register a live dashboard widget with optional auto-refresh."""

        widget = DashboardWidget(
            widget_id=widget_id,
            widget_type=widget_type,
            title=title,
            data={},
            last_updated=time.time() * 1000,
            refresh_interval_ms=refresh_interval_ms
        )

        self._widgets[widget_id] = widget

        # Start auto-refresh task if data source provided
        if data_source_fn:
            task = asyncio.create_task(
                self._auto_refresh_widget(widget_id, data_source_fn)
            )
            self._widget_refresh_tasks[widget_id] = task

        logger.info(
            "dashboard_widget_registered",
            widget_id=widget_id,
            widget_type=widget_type,
            refresh_interval_ms=refresh_interval_ms,
            auto_refresh=data_source_fn is not None
        )

    async def _auto_refresh_widget(self, widget_id: str, data_source_fn: callable) -> None:
        """Auto-refresh widget data at specified interval."""

        while widget_id in self._widgets:
            try:
                widget = self._widgets[widget_id]

                # Call data source function
                new_data = await data_source_fn() if asyncio.iscoroutinefunction(data_source_fn) else data_source_fn()

                # Update widget data
                widget.data = new_data
                widget.last_updated = time.time() * 1000

                # Wait for next refresh
                await asyncio.sleep(widget.refresh_interval_ms / 1000.0)

            except Exception as error:
                logger.error(
                    "dashboard_widget_refresh_error",
                    widget_id=widget_id,
                    error=str(error)
                )
                await asyncio.sleep(5.0)  # Error backoff

    async def get_widget_data(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get current widget data with staleness check."""

        widget = self._widgets.get(widget_id)
        if not widget:
            return None

        return {
            "widget_id": widget.widget_id,
            "type": widget.widget_type,
            "title": widget.title,
            "data": widget.data,
            "last_updated": widget.last_updated,
            "is_stale": widget.is_stale(),
            "refresh_interval_ms": widget.refresh_interval_ms
        }

    async def get_all_widgets(self) -> List[Dict[str, Any]]:
        """Get all registered widgets with their current data."""

        widgets = []
        for widget_id in self._widgets:
            widget_data = await self.get_widget_data(widget_id)
            if widget_data:
                widgets.append(widget_data)

        return widgets

    async def build_identity_panel(self, user_id: str) -> dict[str, Any]:
        """Return a serialisable representation of the identity panel."""

        try:
            permissions = await self.identity_manager.describe_permissions(user_id)
        except IdentityVerificationError as error:
            logger.warning(
                "dashboard_identity_unavailable",
                user_id=user_id,
                error=str(error),
            )
            return {
                "status": "error",
                "user_id": user_id,
                "message": "Identity unavailable",
            }

        identity_view = DashboardIdentityView(
            user_id=permissions["user_id"],
            display_name=permissions["attributes"].get("display_name", permissions["user_id"]),
            tier_level=permissions["tier_level"],
            scopes=permissions["scopes"],
            active_sessions=permissions["active_sessions"],
        )

        logger.info(
            "dashboard_identity_panel_built",
            user_id=identity_view.user_id,
            tier_level=identity_view.tier_level,
            scope_count=len(identity_view.scopes),
            affect_delta=len(identity_view.active_sessions),
        )

        panel = {
            "status": "ok",
            "identity": {
                "user_id": identity_view.user_id,
                "display_name": identity_view.display_name,
                "tier": identity_view.tier_level,
                "permissions": identity_view.scopes,
                "active_sessions": identity_view.active_sessions,
            },
            "widgets": await self.get_all_widgets(),  # Live dashboard widgets integration
            "timestamp": time.time() * 1000,
        }

        return panel


class HealixDashboard:
    """Placeholder for Healix dashboard functionality."""

    def __init__(self):
        self.status = "initialized"

    def render(self):
        """Placeholder render method."""
        return {"status": "placeholder"}
