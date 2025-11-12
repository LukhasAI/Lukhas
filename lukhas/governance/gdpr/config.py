"""GDPR configuration for compliance and data protection."""

from dataclasses import dataclass
from typing import List


@dataclass
class GDPRConfig:
    """Configuration for GDPR compliance features.

    GDPR Articles Implemented:
    - Article 15: Right to Access (data export)
    - Article 17: Right to Erasure (data deletion)
    - Article 13/14: Information to be provided (privacy policy)
    - Article 20: Right to Data Portability

    Attributes:
        enabled: Enable/disable GDPR features
        data_controller_name: Name of the data controller
        data_controller_email: Email of the data controller/DPO
        data_controller_address: Physical address of data controller
        retention_days: Default data retention period (days)
        export_format: Format for data export ("json", "csv")
        include_audit_logs: Include audit logs in data export
        soft_delete: Use soft delete (mark as deleted) vs hard delete
        anonymize_instead_of_delete: Anonymize data instead of deleting
        data_sources: List of data sources to export/delete from
    """

    enabled: bool = True
    data_controller_name: str = "LUKHAS AI"
    data_controller_email: str = "privacy@lukhas.ai"
    data_controller_address: str = "LUKHAS AI, Privacy Department"
    retention_days: int = 2555  # 7 years default
    export_format: str = "json"
    include_audit_logs: bool = True
    soft_delete: bool = True  # Mark as deleted, don't remove immediately
    anonymize_instead_of_delete: bool = False
    data_sources: List[str] = None

    def __post_init__(self):
        """Validate configuration and set defaults."""
        if self.retention_days < 1:
            raise ValueError("retention_days must be at least 1")

        if self.export_format not in ["json", "csv"]:
            raise ValueError("export_format must be 'json' or 'csv'")

        if not self.data_controller_email or "@" not in self.data_controller_email:
            raise ValueError("data_controller_email must be a valid email")

        if self.data_sources is None:
            # Default data sources
            self.data_sources = [
                "user_profile",
                "feedback_cards",
                "traces",
                "audit_logs",
                "preferences",
            ]


def get_default_config() -> GDPRConfig:
    """Get default GDPR configuration for production.

    Returns:
        GDPRConfig with production-safe defaults
    """
    return GDPRConfig(
        enabled=True,
        data_controller_name="LUKHAS AI",
        data_controller_email="privacy@lukhas.ai",
        data_controller_address="LUKHAS AI, Privacy Department",
        retention_days=2555,  # 7 years
        export_format="json",
        include_audit_logs=True,
        soft_delete=True,
        anonymize_instead_of_delete=False,
    )


def get_testing_config() -> GDPRConfig:
    """Get GDPR configuration for testing.

    Returns:
        GDPRConfig with testing-friendly settings
    """
    return GDPRConfig(
        enabled=True,
        data_controller_name="LUKHAS AI Test",
        data_controller_email="test@lukhas.ai",
        data_controller_address="Test Environment",
        retention_days=1,
        export_format="json",
        include_audit_logs=False,
        soft_delete=False,  # Hard delete for tests
        anonymize_instead_of_delete=False,
    )
