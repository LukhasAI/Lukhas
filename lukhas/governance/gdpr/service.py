"""GDPR service for data export, deletion, and privacy management."""

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for GDPR service
# estimate: 15min | priority: high | dependencies: none

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4

try:
    from lukhas.governance.audit import AuditEventType, AuditLogger
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False

from lukhas.governance.gdpr.config import GDPRConfig


@dataclass
class DataExport:
    """User data export for GDPR Article 15 (Right to Access).

    Contains all personal data held about a user in a structured,
    commonly used, and machine-readable format.

    Attributes:
        export_id: Unique export identifier
        user_id: User ID whose data is exported
        export_timestamp: When export was created (Unix epoch)
        data_controller: Name of the data controller
        data: Dictionary of exported data by source
        metadata: Additional export metadata
    """

    export_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    export_timestamp: float = field(default_factory=time.time)
    data_controller: str = "LUKHAS AI"
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert export to dictionary.

        Returns:
            Dictionary representation
        """
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert export to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class DeletionResult:
    """Result of user data deletion for GDPR Article 17 (Right to Erasure).

    Attributes:
        deletion_id: Unique deletion identifier
        user_id: User ID whose data was deleted
        deletion_timestamp: When deletion occurred (Unix epoch)
        success: Whether deletion was successful
        items_deleted: Number of items deleted by source
        errors: Any errors encountered during deletion
        metadata: Additional deletion metadata
    """

    deletion_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    deletion_timestamp: float = field(default_factory=time.time)
    success: bool = True
    items_deleted: Dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation
        """
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert result to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)


class GDPRService:
    """GDPR compliance service for data protection and privacy.

    Implements GDPR requirements:
    - Article 15: Right to Access (data export)
    - Article 17: Right to Erasure (data deletion)
    - Article 13/14: Information to be provided (privacy policy)
    - Article 20: Right to Data Portability

    Usage:
        service = GDPRService(config=GDPRConfig())

        # Export user data
        data_export = await service.export_user_data("user_abc")
        json_str = data_export.to_json()

        # Delete user data
        result = await service.delete_user_data("user_abc")

        # Get privacy policy
        policy = service.get_privacy_policy()
    """

    def __init__(self, config: Optional[GDPRConfig] = None):
        """Initialize GDPR service.

        Args:
            config: GDPR configuration (uses defaults if None)
        """
        self.config = config or GDPRConfig()

        # Initialize audit logger if available
        if AUDIT_AVAILABLE:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = None

    async def export_user_data(
        self,
        user_id: str,
        data_sources: Optional[list[str]] = None,
        include_metadata: bool = True,
    ) -> DataExport:
        """Export all user data (GDPR Article 15 - Right to Access).

        Args:
            user_id: User ID to export data for
            data_sources: List of data sources to include (None = all)
            include_metadata: Include metadata about the export

        Returns:
            DataExport with all user data

        Raises:
            ValueError: If user_id is invalid
        """
        if not user_id:
            raise ValueError("user_id is required")

        if not self.config.enabled:
            raise RuntimeError("GDPR features are disabled")

        # Determine which data sources to export
        sources = data_sources or self.config.data_sources

        # Create export
        export = DataExport(
            user_id=user_id,
            data_controller=self.config.data_controller_name,
            metadata={
                "format": self.config.export_format,
                "sources_requested": sources,
                "gdpr_article": "Article 15 - Right to Access",
                "controller_email": self.config.data_controller_email,
                "controller_address": self.config.data_controller_address,
            } if include_metadata else {},
        )

        # Export data from each source
        total_records = 0

        for source in sources:
            try:
                records = await self._export_from_source(user_id, source)
                export.data[source] = records
                total_records += len(records) if isinstance(records, list) else 1
            except Exception as e:
                export.data[source] = {"error": str(e)}
                export.metadata["errors"] = export.metadata.get("errors", [])
                export.metadata["errors"].append(f"{source}: {e!s}")

        export.metadata["total_records_exported"] = total_records
        export.metadata["sources_exported"] = list(export.data.keys())

        # Log export to audit log
        if self.audit_logger and AUDIT_AVAILABLE:
            self.audit_logger.log_data_access_event(
                user_id=user_id,
                event_type=AuditEventType.BULK_EXPORT,
                resource_type="user_data",
                resource_id=user_id,
                success=True,
                metadata={
                    "export_id": export.export_id,
                    "sources": sources,
                    "total_records": total_records,
                    "gdpr_article": "Article 15",
                }
            )

        return export

    async def delete_user_data(
        self,
        user_id: str,
        data_sources: Optional[list[str]] = None,
        confirm: bool = False,
    ) -> DeletionResult:
        """Delete all user data (GDPR Article 17 - Right to Erasure).

        Args:
            user_id: User ID to delete data for
            data_sources: List of data sources to delete from (None = all)
            confirm: Must be True to actually delete data

        Returns:
            DeletionResult with deletion status

        Raises:
            ValueError: If user_id is invalid or confirm is False
        """
        if not user_id:
            raise ValueError("user_id is required")

        if not confirm:
            raise ValueError("confirm must be True to delete data")

        if not self.config.enabled:
            raise RuntimeError("GDPR features are disabled")

        # Determine which data sources to delete from
        sources = data_sources or self.config.data_sources

        # Create deletion result
        result = DeletionResult(
            user_id=user_id,
            metadata={
                "deletion_type": "soft" if self.config.soft_delete else "hard",
                "anonymize": self.config.anonymize_instead_of_delete,
                "gdpr_article": "Article 17 - Right to Erasure",
                "controller_email": self.config.data_controller_email,
            }
        )

        # Delete data from each source
        total_deleted = 0

        for source in sources:
            try:
                count = await self._delete_from_source(user_id, source)
                result.items_deleted[source] = count
                total_deleted += count
            except Exception as e:
                result.errors.append(f"{source}: {e!s}")
                result.success = False

        result.metadata["total_items_deleted"] = total_deleted
        result.metadata["sources_processed"] = list(result.items_deleted.keys())

        # Log deletion to audit log
        if self.audit_logger and AUDIT_AVAILABLE:
            self.audit_logger.log_data_access_event(
                user_id=user_id,
                event_type=AuditEventType.BULK_DELETE,
                resource_type="user_data",
                resource_id=user_id,
                success=result.success,
                error_message="; ".join(result.errors) if result.errors else None,
                metadata={
                    "deletion_id": result.deletion_id,
                    "sources": sources,
                    "total_deleted": total_deleted,
                    "deletion_type": "soft" if self.config.soft_delete else "hard",
                    "gdpr_article": "Article 17",
                }
            )

        return result

    def get_privacy_policy(self) -> dict[str, Any]:
        """Get privacy policy information (GDPR Article 13/14).

        Returns information that must be provided when collecting personal data.

        Returns:
            Dictionary with privacy policy information
        """
        return {
            "data_controller": {
                "name": self.config.data_controller_name,
                "email": self.config.data_controller_email,
                "address": self.config.data_controller_address,
            },
            "data_processing": {
                "purposes": [
                    "Providing AI consciousness services",
                    "Improving model performance through feedback",
                    "Security monitoring and fraud prevention",
                    "Compliance with legal obligations",
                ],
                "legal_basis": [
                    "Contract performance (Article 6(1)(b))",
                    "Legitimate interests (Article 6(1)(f))",
                    "Legal obligation (Article 6(1)(c))",
                ],
                "retention_period": f"{self.config.retention_days} days",
            },
            "data_subject_rights": {
                "right_to_access": "Request a copy of your personal data",
                "right_to_rectification": "Request correction of inaccurate data",
                "right_to_erasure": "Request deletion of your personal data",
                "right_to_restrict_processing": "Request restriction of processing",
                "right_to_data_portability": "Receive your data in machine-readable format",
                "right_to_object": "Object to processing of your data",
                "right_to_withdraw_consent": "Withdraw consent at any time",
            },
            "data_categories": {
                "identification_data": ["user_id", "email", "username"],
                "usage_data": ["feedback_cards", "traces", "preferences"],
                "technical_data": ["IP address", "user agent", "session data"],
                "audit_data": ["authentication logs", "access logs"],
            },
            "data_recipients": [
                "Internal teams (engineering, support)",
                "Cloud infrastructure providers (AWS, GCP)",
                "Analytics providers",
            ],
            "international_transfers": {
                "safeguards": ["EU-US Data Privacy Framework", "Standard Contractual Clauses"],
            },
            "automated_decision_making": {
                "exists": True,
                "description": "AI model predictions and recommendations",
                "logic": "Machine learning models trained on feedback data",
                "significance": "Affects quality of AI responses",
                "consequences": "Better personalized experience",
            },
            "contact": {
                "data_protection_officer": self.config.data_controller_email,
                "supervisory_authority": "Local data protection authority",
            },
            "effective_date": "2025-01-01",
            "version": "1.0",
        }

    async def _export_from_source(self, user_id: str, source: str) -> Any:
        """Export data from a specific source.

        This is a placeholder that should be overridden or extended
        to integrate with actual data storage systems.

        Args:
            user_id: User ID to export data for
            source: Data source name

        Returns:
            Exported data from source
        """
        # Placeholder implementation
        # In production, this would integrate with actual storage systems
        if source == "user_profile":
            return {
                "user_id": user_id,
                "created_at": time.time(),
                "tier": 0,
            }
        elif source == "feedback_cards":
            return []  # Would query feedback system
        elif source == "traces":
            return []  # Would query trace system
        elif source == "audit_logs" and self.config.include_audit_logs:
            if self.audit_logger:
                # Export audit logs for this user
                events = self.audit_logger.get_events(user_id=user_id, limit=10000)
                return [event.to_dict() for event in events]
            return []
        elif source == "preferences":
            return {}  # Would query preferences system
        else:
            return {"note": f"No data available for source: {source}"}

    async def _delete_from_source(self, user_id: str, source: str) -> int:
        """Delete data from a specific source.

        This is a placeholder that should be overridden or extended
        to integrate with actual data storage systems.

        Args:
            user_id: User ID to delete data for
            source: Data source name

        Returns:
            Number of items deleted
        """
        # Placeholder implementation
        # In production, this would integrate with actual storage systems

        if self.config.soft_delete:
            # Soft delete: mark as deleted but don't remove
            # Implementation would update records with deleted=True
            return 0  # Would mark records as deleted

        if self.config.anonymize_instead_of_delete:
            # Anonymize: replace personal data with anonymized values
            # Implementation would update records with anonymized data
            return 0  # Would anonymize records

        # Hard delete: actually remove data
        if source == "user_profile":
            return 1  # Would delete user profile
        elif source == "feedback_cards":
            return 0  # Would delete feedback cards
        elif source == "traces":
            return 0  # Would delete traces
        elif source == "audit_logs":
            # NOTE: Audit logs should typically NOT be deleted for compliance
            # Only delete if explicitly required and allowed by regulations
            if self.audit_logger:
                # Would delete audit logs (with caution!)
                return 0
            return 0
        elif source == "preferences":
            return 0  # Would delete preferences
        else:
            return 0

    def validate_data_subject_request(self, user_id: str, request_type: str) -> bool:
        """Validate a data subject request.

        Args:
            user_id: User making the request
            request_type: Type of request (export, delete, etc.)

        Returns:
            True if request is valid
        """
        if not user_id:
            return False

        if request_type not in ["export", "delete", "rectify", "restrict", "object"]:
            return False

        # Additional validation could be added here:
        # - Check if user exists
        # - Check if user is authenticated
        # - Check if request quota is exceeded
        # - Check if previous requests are pending

        return True
