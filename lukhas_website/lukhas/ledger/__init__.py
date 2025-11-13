"""
LUKHAS Ledger - Event-Driven Consent Management
==============================================

Event-sourced architecture for GDPR/CCPA compliant consent tracking
with immutable audit trails and T4/0.01% excellence performance.
"""

from .consent_handlers import HandlerState, IdempotentConsentHandler
from .event_bus import AsyncEventBus, EventOffset, ReplayIterator
from .events import (
    ConsentCheckedEvent,
    ConsentEvent,
    ConsentGrantedEvent,
    ConsentRevokedEvent,
    DuressDetectedEvent,
    TraceCreatedEvent,
)

__all__ = [
    "AsyncEventBus",
    "ConsentCheckedEvent",
    "ConsentEvent",
    "ConsentGrantedEvent",
    "ConsentRevokedEvent",
    "DuressDetectedEvent",
    "EventOffset",
    "HandlerState",
    "IdempotentConsentHandler",
    "ReplayIterator",
    "TraceCreatedEvent",
]

__version__ = "2.0.0"
