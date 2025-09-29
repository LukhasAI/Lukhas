"""
LUKHAS Ledger - Event-Driven Consent Management
==============================================

Event-sourced architecture for GDPR/CCPA compliant consent tracking
with immutable audit trails and T4/0.01% excellence performance.
"""

from .events import (
    ConsentEvent,
    ConsentGrantedEvent,
    ConsentRevokedEvent,
    ConsentCheckedEvent,
    TraceCreatedEvent,
    DuressDetectedEvent,
)
from .event_bus import AsyncEventBus, EventOffset, ReplayIterator
from .consent_handlers import IdempotentConsentHandler, HandlerState

__all__ = [
    "ConsentEvent",
    "ConsentGrantedEvent",
    "ConsentRevokedEvent",
    "ConsentCheckedEvent",
    "TraceCreatedEvent",
    "DuressDetectedEvent",
    "AsyncEventBus",
    "EventOffset",
    "ReplayIterator",
    "IdempotentConsentHandler",
    "HandlerState",
]

__version__ = "2.0.0"