"""
Common utilities and shared components for the core module
"""
import streamlit as st
from datetime import timezone

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Common enums


class ComponentStatus(Enum):
    """Status of a component"""

    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


class MessageType(Enum):
    """Common message types"""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    INFO = "info"


# Common utilities


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def validate_component_id(component_id: str) -> bool:
    """Validate component ID format"""
    if not component_id:
        return False
    if not isinstance(component_id, str):
        return False
    return not len(component_id) < 3


# Common base classes


class BaseComponent:
    """Base class for all components"""

    def __init__(self, component_id: str, component_type: str = "generic"):
        self.component_id = component_id
        self.component_type = component_type
        self.status = ComponentStatus.INITIALIZING
        self.created_at = get_timestamp()
        self.metadata = {}

    def set_status(self, status: ComponentStatus):
        """Update component status"""
        self.status = status
        logger.info(f"Component {self.component_id} status changed to {status.value}")

    def add_metadata(self, key: str, value: Any):
        """Add metadata to component"""
        self.metadata[key] = value


class BaseMessage:
    """Base class for messages"""

    def __init__(
        self,
        message_type: MessageType,
        source: str,
        target: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
    ):
        self.message_type = message_type
        self.source = source
        self.target = target
        self.payload = payload or {}
        self.timestamp = get_timestamp()
        self.message_id = f"{source}_{datetime.now(timezone.utc).timestamp(}"


# Common exceptions


class ComponentError(Exception):
    """Base exception for component errors"""


class ValidationError(ComponentError):
    """Validation error"""


class CommunicationError(ComponentError):
    """Communication error between components"""


# Common configuration
DEFAULT_CONFIG = {
    "timeout": 30,
    "retry_attempts": 3,
    "log_level": "INFO",
    "enable_metrics": True,
    "enable_tracing": True,
}


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return DEFAULT_CONFIG.get(key, default)


# Export all public symbols
__all__ = [
    "DEFAULT_CONFIG",
    "BaseComponent",
    "BaseMessage",
    "CommunicationError",
    "ComponentError",
    "ComponentStatus",
    "MessageType",
    "ValidationError",
    "get_config",
    "get_timestamp",
    "logger",
    "validate_component_id",
]
