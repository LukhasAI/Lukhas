"""GDPR compliance module for LUKHAS AI.

This module provides GDPR (General Data Protection Regulation) compliance features:

- Right to Access: Export all user data in portable format (Article 15)
- Right to Erasure: Delete all user data ("right to be forgotten") (Article 17)
- Privacy Policy: Transparent data processing information (Article 13/14)

Usage:
    from lukhas.governance.gdpr import GDPRService

    service = GDPRService()

    # Export user data
    data_export = await service.export_user_data(user_id="user_abc")

    # Delete user data
    deleted = await service.delete_user_data(user_id="user_abc")
"""

from lukhas.governance.gdpr.service import GDPRService, DataExport, DeletionResult
from lukhas.governance.gdpr.config import GDPRConfig

__all__ = [
    "GDPRService",
    "DataExport",
    "DeletionResult",
    "GDPRConfig",
]
