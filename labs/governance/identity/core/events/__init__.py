"""
Identity System Events Module
==============================
Provides event types and publishers for the identity system.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st


class IdentityEventType(Enum):
    """Types of identity system events"""

    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    TIER_CHANGE = "tier_change"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    CONSENT_GIVEN = "consent_given"
    CONSENT_REVOKED = "consent_revoked"
    IDENTITY_CREATED = "identity_created"
    IDENTITY_UPDATED = "identity_updated"
    IDENTITY_DELETED = "identity_deleted"


@dataclass
class IdentityEvent:
    """Identity system event"""

    event_type: IdentityEventType
    user_id: str
    timestamp: float = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


class IdentityEventPublisher:
    """Publisher for identity events"""

    def __init__(self):
        self.subscribers = []
        self.event_history = []

    def publish(self, event: IdentityEvent):
        """Publish an event to all subscribers"""
        self.event_history.append(event)
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception:
                # Log but don't fail
                pass

    def subscribe(self, handler):
        """Subscribe to events"""
        self.subscribers.append(handler)

    def unsubscribe(self, handler):
        """Unsubscribe from events"""
        if handler in self.subscribers:
            self.subscribers.remove(handler)


# Singleton publisher
_publisher = IdentityEventPublisher()


def publish_event(event_type: IdentityEventType, user_id: str, **metadata):
    """Convenience function to publish events"""
    event = IdentityEvent(event_type=event_type, user_id=user_id, metadata=metadata)
    _publisher.publish(event)


__all__ = [
    "IdentityEvent",
    "IdentityEventPublisher",
    "IdentityEventType",
    "publish_event",
]
