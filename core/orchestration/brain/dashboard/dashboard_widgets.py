"""
Dashboard Widget System for LUKHAS Brain Orchestration
====================================================

This module implements the live dashboard widget system that was previously
marked as TODO in main_dashboard.py. It provides a pluggable widget framework
for real-time dashboard functionality with identity-aware permissions.

Features:
- Live widget registration and management
- Identity-aware widget permissions
- Real-time data streaming for widgets
- Widget lifecycle management (load, update, unload)
- Performance monitoring and health checks
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, Set
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class WidgetPermissionLevel(Enum):
    """Permission levels for dashboard widgets."""
    PUBLIC = "public"           # No authentication required
    AUTHENTICATED = "authenticated"  # Basic authentication required
    TIER_1 = "tier_1"          # Tier 1+ access required
    TIER_2 = "tier_2"          # Tier 2+ access required
    ADMIN = "admin"            # Admin access required


class WidgetStatus(Enum):
    """Widget lifecycle status."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget."""
    widget_id: str
    name: str
    description: str
    permission_level: WidgetPermissionLevel
    refresh_interval: float = 5.0  # seconds
    max_data_points: int = 100
    enable_streaming: bool = True
    tags: Set[str] = field(default_factory=set)


@dataclass
class WidgetData:
    """Data container for widget content."""
    widget_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DashboardWidget(ABC):
    """Abstract base class for dashboard widgets."""
    
    def __init__(self, config: WidgetConfig):
        self.config = config
        self.status = WidgetStatus.INITIALIZING
        self.last_update = None
        self.error_count = 0
        self.data_history: List[WidgetData] = []
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the widget. Return True if successful."""
        pass
    
    @abstractmethod
    async def update_data(self) -> WidgetData:
        """Update widget data. Return new WidgetData."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up widget resources."""
        pass
    
    async def get_current_data(self) -> Optional[WidgetData]:
        """Get the most recent widget data."""
        if self.data_history:
            return self.data_history[-1]
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get widget health status."""
        return {
            "widget_id": self.config.widget_id,
            "status": self.status.value,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "error_count": self.error_count,
            "data_points": len(self.data_history)
        }


class IdentityStatusWidget(DashboardWidget):
    """Widget showing current identity status and session info."""
    
    def __init__(self, config: WidgetConfig, identity_manager):
        super().__init__(config)
        self.identity_manager = identity_manager
        
    async def initialize(self) -> bool:
        """Initialize identity status widget."""
        try:
            # Test identity manager connectivity
            if self.identity_manager:
                self.status = WidgetStatus.ACTIVE
                logger.info("identity_status_widget_initialized", 
                          widget_id=self.config.widget_id)
                return True
            else:
                self.status = WidgetStatus.ERROR
                return False
        except Exception as e:
            logger.error("identity_status_widget_init_failed", 
                        widget_id=self.config.widget_id, error=str(e))
            self.status = WidgetStatus.ERROR
            self.error_count += 1
            return False
    
    async def update_data(self) -> WidgetData:
        """Update identity status data."""
        try:
            # Get current active sessions count
            # This is a placeholder - would integrate with actual identity manager
            current_time = datetime.now(timezone.utc)
            
            data = {
                "active_sessions": 0,  # Would get from identity_manager
                "total_users": 0,      # Would get from identity_manager
                "authentication_rate": 0.0,  # Would calculate from recent auths
                "tier_distribution": {
                    "tier_0": 0,
                    "tier_1": 0, 
                    "tier_2": 0,
                    "admin": 0
                }
            }
            
            widget_data = WidgetData(
                widget_id=self.config.widget_id,
                timestamp=current_time,
                data=data,
                metadata={"source": "identity_manager"}
            )
            
            # Add to history and trim if needed
            self.data_history.append(widget_data)
            if len(self.data_history) > self.config.max_data_points:
                self.data_history = self.data_history[-self.config.max_data_points:]
            
            self.last_update = current_time
            
            logger.debug("identity_status_widget_updated",
                        widget_id=self.config.widget_id,
                        active_sessions=data["active_sessions"])
            
            return widget_data
            
        except Exception as e:
            logger.error("identity_status_widget_update_failed",
                        widget_id=self.config.widget_id, error=str(e))
            self.error_count += 1
            self.status = WidgetStatus.ERROR
            raise
    
    async def cleanup(self) -> None:
        """Clean up identity status widget."""
        self.status = WidgetStatus.TERMINATED
        self.data_history.clear()
        logger.info("identity_status_widget_cleaned_up",
                   widget_id=self.config.widget_id)


class OrchestrationStatusWidget(DashboardWidget):
    """Widget showing orchestration system status."""
    
    async def initialize(self) -> bool:
        """Initialize orchestration status widget."""
        self.status = WidgetStatus.ACTIVE
        logger.info("orchestration_status_widget_initialized",
                   widget_id=self.config.widget_id)
        return True
    
    async def update_data(self) -> WidgetData:
        """Update orchestration status data."""
        current_time = datetime.now(timezone.utc)
        
        # Placeholder data - would integrate with actual orchestration metrics
        data = {
            "active_orchestrations": 0,
            "completed_today": 0,
            "error_rate": 0.0,
            "avg_completion_time": 0.0,
            "system_health": "healthy",
            "resource_usage": {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "active_threads": 0
            }
        }
        
        widget_data = WidgetData(
            widget_id=self.config.widget_id,
            timestamp=current_time,
            data=data,
            metadata={"source": "orchestration_manager"}
        )
        
        self.data_history.append(widget_data)
        if len(self.data_history) > self.config.max_data_points:
            self.data_history = self.data_history[-self.config.max_data_points:]
        
        self.last_update = current_time
        return widget_data
    
    async def cleanup(self) -> None:
        """Clean up orchestration status widget."""
        self.status = WidgetStatus.TERMINATED
        self.data_history.clear()
        logger.info("orchestration_status_widget_cleaned_up",
                   widget_id=self.config.widget_id)


class SystemMetricsWidget(DashboardWidget):
    """Widget showing system performance metrics."""
    
    async def initialize(self) -> bool:
        """Initialize system metrics widget."""
        self.status = WidgetStatus.ACTIVE
        logger.info("system_metrics_widget_initialized",
                   widget_id=self.config.widget_id)
        return True
    
    async def update_data(self) -> WidgetData:
        """Update system metrics data."""
        current_time = datetime.now(timezone.utc)
        
        # Placeholder data - would integrate with actual metrics collection
        data = {
            "response_time_p95": 0.0,
            "response_time_p99": 0.0,
            "requests_per_second": 0.0,
            "error_rate": 0.0,
            "uptime_seconds": 0,
            "memory_usage_mb": 0.0,
            "disk_usage_percent": 0.0
        }
        
        widget_data = WidgetData(
            widget_id=self.config.widget_id,
            timestamp=current_time,
            data=data,
            metadata={"source": "system_monitor"}
        )
        
        self.data_history.append(widget_data)
        if len(self.data_history) > self.config.max_data_points:
            self.data_history = self.data_history[-self.config.max_data_points:]
        
        self.last_update = current_time
        return widget_data
    
    async def cleanup(self) -> None:
        """Clean up system metrics widget."""
        self.status = WidgetStatus.TERMINATED
        self.data_history.clear()
        logger.info("system_metrics_widget_cleaned_up",
                   widget_id=self.config.widget_id)


class DashboardWidgetManager:
    """Manages the lifecycle of dashboard widgets."""
    
    def __init__(self):
        self.widgets: Dict[str, DashboardWidget] = {}
        self.update_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
    async def register_widget(self, widget: DashboardWidget) -> bool:
        """Register and initialize a widget."""
        try:
            if await widget.initialize():
                self.widgets[widget.config.widget_id] = widget
                
                # Start update task if streaming is enabled
                if widget.config.enable_streaming:
                    task = asyncio.create_task(
                        self._widget_update_loop(widget)
                    )
                    self.update_tasks[widget.config.widget_id] = task
                
                logger.info("dashboard_widget_registered",
                           widget_id=widget.config.widget_id,
                           widget_type=type(widget).__name__)
                return True
            else:
                logger.error("dashboard_widget_registration_failed",
                           widget_id=widget.config.widget_id)
                return False
                
        except Exception as e:
            logger.error("dashboard_widget_registration_error",
                        widget_id=widget.config.widget_id,
                        error=str(e))
            return False
    
    async def unregister_widget(self, widget_id: str) -> bool:
        """Unregister and cleanup a widget."""
        try:
            # Cancel update task
            if widget_id in self.update_tasks:
                self.update_tasks[widget_id].cancel()
                del self.update_tasks[widget_id]
            
            # Cleanup widget
            if widget_id in self.widgets:
                await self.widgets[widget_id].cleanup()
                del self.widgets[widget_id]
            
            logger.info("dashboard_widget_unregistered", widget_id=widget_id)
            return True
            
        except Exception as e:
            logger.error("dashboard_widget_unregistration_error",
                        widget_id=widget_id, error=str(e))
            return False
    
    async def get_widget_data(self, widget_id: str, user_tier: int = 0) -> Optional[WidgetData]:
        """Get current data for a specific widget with permission check."""
        if widget_id not in self.widgets:
            return None
        
        widget = self.widgets[widget_id]
        
        # Check permissions
        if not self._check_widget_permission(widget.config.permission_level, user_tier):
            logger.warning("dashboard_widget_access_denied",
                          widget_id=widget_id, user_tier=user_tier,
                          required_permission=widget.config.permission_level.value)
            return None
        
        return await widget.get_current_data()
    
    async def get_all_widget_data(self, user_tier: int = 0) -> Dict[str, WidgetData]:
        """Get current data for all widgets that user has permission to access."""
        result = {}
        
        for widget_id, widget in self.widgets.items():
            if self._check_widget_permission(widget.config.permission_level, user_tier):
                data = await widget.get_current_data()
                if data:
                    result[widget_id] = data
        
        return result
    
    def get_widget_health(self) -> Dict[str, Any]:
        """Get health status for all widgets."""
        return {
            widget_id: widget.get_health_status()
            for widget_id, widget in self.widgets.items()
        }
    
    async def start(self) -> None:
        """Start the widget manager."""
        self.is_running = True
        logger.info("dashboard_widget_manager_started")
    
    async def stop(self) -> None:
        """Stop the widget manager and cleanup all widgets."""
        self.is_running = False
        
        # Cancel all update tasks
        for task in self.update_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.update_tasks:
            await asyncio.gather(*self.update_tasks.values(), return_exceptions=True)
        
        # Cleanup all widgets
        for widget in self.widgets.values():
            await widget.cleanup()
        
        self.widgets.clear()
        self.update_tasks.clear()
        
        logger.info("dashboard_widget_manager_stopped")
    
    def _check_widget_permission(self, required_level: WidgetPermissionLevel, user_tier: int) -> bool:
        """Check if user has permission to access widget."""
        if required_level == WidgetPermissionLevel.PUBLIC:
            return True
        elif required_level == WidgetPermissionLevel.AUTHENTICATED:
            return user_tier >= 0
        elif required_level == WidgetPermissionLevel.TIER_1:
            return user_tier >= 1
        elif required_level == WidgetPermissionLevel.TIER_2:
            return user_tier >= 2
        elif required_level == WidgetPermissionLevel.ADMIN:
            return user_tier >= 10  # Assuming admin is tier 10+
        return False
    
    async def _widget_update_loop(self, widget: DashboardWidget) -> None:
        """Background task to update widget data periodically."""
        while self.is_running and widget.status == WidgetStatus.ACTIVE:
            try:
                await widget.update_data()
                await asyncio.sleep(widget.config.refresh_interval)
                
            except asyncio.CancelledError:
                logger.info("dashboard_widget_update_loop_cancelled",
                           widget_id=widget.config.widget_id)
                break
                
            except Exception as e:
                logger.error("dashboard_widget_update_loop_error",
                           widget_id=widget.config.widget_id,
                           error=str(e))
                widget.error_count += 1
                
                # Pause widget if too many errors
                if widget.error_count >= 5:
                    widget.status = WidgetStatus.ERROR
                    logger.error("dashboard_widget_disabled_due_to_errors",
                               widget_id=widget.config.widget_id)
                    break
                
                # Back off on errors
                await asyncio.sleep(min(widget.config.refresh_interval * 2, 30.0))


def create_default_widgets(identity_manager=None) -> List[DashboardWidget]:
    """Create default dashboard widgets."""
    widgets = []
    
    # Identity Status Widget
    identity_config = WidgetConfig(
        widget_id="identity_status",
        name="Identity Status",
        description="Shows current identity and session information",
        permission_level=WidgetPermissionLevel.AUTHENTICATED,
        refresh_interval=10.0,
        tags={"identity", "authentication", "sessions"}
    )
    widgets.append(IdentityStatusWidget(identity_config, identity_manager))
    
    # Orchestration Status Widget
    orchestration_config = WidgetConfig(
        widget_id="orchestration_status",
        name="Orchestration Status",
        description="Shows orchestration system status and metrics",
        permission_level=WidgetPermissionLevel.TIER_1,
        refresh_interval=5.0,
        tags={"orchestration", "system", "performance"}
    )
    widgets.append(OrchestrationStatusWidget(orchestration_config))
    
    # System Metrics Widget
    metrics_config = WidgetConfig(
        widget_id="system_metrics",
        name="System Metrics",
        description="Shows system performance and health metrics",
        permission_level=WidgetPermissionLevel.TIER_2,
        refresh_interval=3.0,
        tags={"metrics", "performance", "monitoring"}
    )
    widgets.append(SystemMetricsWidget(metrics_config))
    
    return widgets