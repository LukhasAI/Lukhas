"""
Identity Event System Integration

Provides event-driven architecture for the LUKHAS identity system,
enabling real-time coordination across colonies, swarms, and services.
"""

from .identity_event_types import (
    IdentityEventType,
    IdentityEventPriority,
    IdentityEvent,
    AuthenticationContext,
    VerificationResult,
    TierChangeContext
)
from .identity_event_publisher import (
    IdentityEventPublisher,
    get_identity_event_publisher
)

__all__ = [
    'IdentityEventType',
    'IdentityEventPriority',
    'IdentityEvent',
    'AuthenticationContext',
    'VerificationResult',
    'TierChangeContext',
    'IdentityEventPublisher',
    'get_identity_event_publisher'
]