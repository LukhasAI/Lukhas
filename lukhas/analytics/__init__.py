"""
Privacy-first analytics module for LUKHAS.

This module provides GDPR-compliant analytics with:
- Differential privacy (ε-DP) with Laplace/Gaussian mechanisms
- Consent-based tracking
- Automatic PII redaction and anonymization
- Privacy budget tracking
- Local-first storage
- GDPR Article 25 (privacy by design) compliance
"""

from lukhas.analytics.privacy_client import (
    AggregateStats,
    DPMechanism,
    PIIAnonymizer,
    PrivacyClient,
)

__all__ = [
    "PrivacyClient",
    "AggregateStats",
    "PIIAnonymizer",
    "DPMechanism",
]
