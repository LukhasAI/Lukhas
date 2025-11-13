"""
Privacy-first analytics module for LUKHAS.

This module provides GDPR-compliant analytics with:
- Consent-based tracking
- Automatic PII redaction
- Local-first storage
- Zero third-party dependencies
"""

from lukhas.analytics.privacy_client import PrivacyAnalyticsClient

__all__ = ["PrivacyAnalyticsClient"]
