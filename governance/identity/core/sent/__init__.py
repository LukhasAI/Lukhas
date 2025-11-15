"""
Consent Management Module for GDPR Compliance

This module provides GDPR-compliant consent management functionality including:
- Consent history tracking with cryptographic audit trails
- Symbolic consent scopes
- GDPR Article 7(1) compliance (demonstrable consent)
- GDPR Article 20 compliance (data portability)

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

from governance.identity.core.sent.consent_history import (
    ConsentEventType,
    ConsentHistoryManager,
    StorageBackend,
    TraceLogger,
)

__all__ = [
    "ConsentHistoryManager",
    "ConsentEventType",
    "StorageBackend",
    "TraceLogger",
]
