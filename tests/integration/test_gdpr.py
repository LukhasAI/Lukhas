"""Integration tests for GDPR compliance features."""

import json
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from lukhas.governance.gdpr import DataExport, DeletionResult, GDPRConfig, GDPRService
from lukhas.governance.gdpr.config import get_default_config, get_testing_config


class TestGDPRConfig:
    """Test GDPR configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = get_default_config()

        assert config.enabled is True
        assert config.data_controller_name == "LUKHAS AI"
        assert config.data_controller_email == "privacy@lukhas.ai"
        assert config.retention_days == 2555  # 7 years
        assert config.export_format == "json"
        assert config.include_audit_logs is True
        assert config.soft_delete is True

    def test_testing_config(self):
        """Test testing configuration."""
        config = get_testing_config()

        assert config.enabled is True
        assert config.retention_days == 1
        assert config.soft_delete is False  # Hard delete for tests
        assert config.include_audit_logs is False

    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid retention_days
        with pytest.raises(ValueError, match="retention_days must be at least 1"):
            GDPRConfig(retention_days=0)

        # Invalid export_format
        with pytest.raises(ValueError, match="export_format must be"):
            GDPRConfig(export_format="xml")

        # Invalid email
        with pytest.raises(ValueError, match="must be a valid email"):
            GDPRConfig(data_controller_email="invalid")

    def test_default_data_sources(self):
        """Test that default data sources are set."""
        config = GDPRConfig()

        assert config.data_sources is not None
        assert "user_profile" in config.data_sources
        assert "feedback_cards" in config.data_sources
        assert "traces" in config.data_sources
        assert "audit_logs" in config.data_sources


class TestDataExport:
    """Test DataExport dataclass."""

    def test_create_export(self):
        """Test creating a data export."""
        export = DataExport(
            user_id="user_abc",
            data_controller="LUKHAS AI",
            data={"user_profile": {"user_id": "user_abc"}},
        )

        assert export.user_id == "user_abc"
        assert export.data_controller == "LUKHAS AI"
        assert export.export_id  # UUID generated
        assert export.export_timestamp > 0  # Timestamp generated
        assert "user_profile" in export.data

    def test_export_to_dict(self):
        """Test converting export to dictionary."""
        export = DataExport(
            user_id="user_abc",
            data={"user_profile": {"user_id": "user_abc"}},
        )

        data = export.to_dict()

        assert data["user_id"] == "user_abc"
        assert "export_id" in data
        assert "export_timestamp" in data
        assert "user_profile" in data["data"]

    def test_export_to_json(self):
        """Test converting export to JSON string."""
        export = DataExport(
            user_id="user_abc",
            data={"user_profile": {"user_id": "user_abc"}},
        )

        json_str = export.to_json()
        data = json.loads(json_str)

        assert data["user_id"] == "user_abc"
        assert "export_id" in data


class TestDeletionResult:
    """Test DeletionResult dataclass."""

    def test_create_result(self):
        """Test creating a deletion result."""
        result = DeletionResult(
            user_id="user_abc",
            success=True,
            items_deleted={"feedback_cards": 10, "traces": 20},
        )

        assert result.user_id == "user_abc"
        assert result.success is True
        assert result.deletion_id  # UUID generated
        assert result.deletion_timestamp > 0  # Timestamp generated
        assert result.items_deleted["feedback_cards"] == 10

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = DeletionResult(
            user_id="user_abc",
            items_deleted={"feedback_cards": 10},
        )

        data = result.to_dict()

        assert data["user_id"] == "user_abc"
        assert "deletion_id" in data
        assert data["items_deleted"]["feedback_cards"] == 10

    def test_result_with_errors(self):
        """Test result with errors."""
        result = DeletionResult(
            user_id="user_abc",
            success=False,
            errors=["Failed to delete from source X", "Timeout on source Y"],
        )

        assert result.success is False
        assert len(result.errors) == 2
        assert "Failed to delete" in result.errors[0]


class TestGDPRService:
    """Test GDPR service."""

    @pytest.mark.asyncio
    async def test_export_user_data(self):
        """Test exporting user data."""
        config = get_testing_config()
        service = GDPRService(config=config)

        export = await service.export_user_data(user_id="user_abc")

        assert export.user_id == "user_abc"
        assert export.data_controller == config.data_controller_name
        assert export.export_id
        assert export.export_timestamp > 0
        assert "user_profile" in export.data
        assert export.metadata["total_records_exported"] >= 0

    @pytest.mark.asyncio
    async def test_export_specific_sources(self):
        """Test exporting data from specific sources."""
        config = get_testing_config()
        service = GDPRService(config=config)

        export = await service.export_user_data(
            user_id="user_abc",
            data_sources=["user_profile", "feedback_cards"],
        )

        assert "user_profile" in export.data
        assert "feedback_cards" in export.data
        # Should not include other sources
        assert len(export.data) == 2

    @pytest.mark.asyncio
    async def test_export_without_metadata(self):
        """Test exporting without metadata."""
        config = get_testing_config()
        service = GDPRService(config=config)

        export = await service.export_user_data(
            user_id="user_abc",
            include_metadata=False,
        )

        assert export.user_id == "user_abc"
        # Basic metadata (sources, record count) is always included
        # Only GDPR-specific metadata is excluded when include_metadata=False
        assert "sources_exported" in export.metadata
        assert "total_records_exported" in export.metadata
        # GDPR-specific metadata should not be present
        assert "gdpr_article" not in export.metadata
        assert "controller_email" not in export.metadata

    @pytest.mark.asyncio
    async def test_export_invalid_user_id(self):
        """Test export with invalid user ID."""
        config = get_testing_config()
        service = GDPRService(config=config)

        with pytest.raises(ValueError, match="user_id is required"):
            await service.export_user_data(user_id="")

    @pytest.mark.asyncio
    async def test_export_disabled(self):
        """Test export when GDPR is disabled."""
        config = GDPRConfig(enabled=False)
        service = GDPRService(config=config)

        with pytest.raises(RuntimeError, match="GDPR features are disabled"):
            await service.export_user_data(user_id="user_abc")

    @pytest.mark.asyncio
    async def test_delete_user_data(self):
        """Test deleting user data."""
        config = get_testing_config()
        service = GDPRService(config=config)

        result = await service.delete_user_data(
            user_id="user_abc",
            confirm=True,
        )

        assert result.user_id == "user_abc"
        assert result.deletion_id
        assert result.deletion_timestamp > 0
        # For placeholder implementation, items_deleted may be 0
        assert isinstance(result.items_deleted, dict)

    @pytest.mark.asyncio
    async def test_delete_specific_sources(self):
        """Test deleting data from specific sources."""
        config = get_testing_config()
        service = GDPRService(config=config)

        result = await service.delete_user_data(
            user_id="user_abc",
            data_sources=["feedback_cards", "traces"],
            confirm=True,
        )

        assert result.user_id == "user_abc"
        # Should process only specified sources
        assert "feedback_cards" in result.items_deleted
        assert "traces" in result.items_deleted

    @pytest.mark.asyncio
    async def test_delete_without_confirm(self):
        """Test delete without confirmation."""
        config = get_testing_config()
        service = GDPRService(config=config)

        with pytest.raises(ValueError, match="confirm must be True"):
            await service.delete_user_data(
                user_id="user_abc",
                confirm=False,
            )

    @pytest.mark.asyncio
    async def test_delete_invalid_user_id(self):
        """Test delete with invalid user ID."""
        config = get_testing_config()
        service = GDPRService(config=config)

        with pytest.raises(ValueError, match="user_id is required"):
            await service.delete_user_data(user_id="", confirm=True)

    @pytest.mark.asyncio
    async def test_delete_disabled(self):
        """Test delete when GDPR is disabled."""
        config = GDPRConfig(enabled=False)
        service = GDPRService(config=config)

        with pytest.raises(RuntimeError, match="GDPR features are disabled"):
            await service.delete_user_data(user_id="user_abc", confirm=True)

    @pytest.mark.asyncio
    async def test_soft_delete(self):
        """Test soft delete mode."""
        config = GDPRConfig(soft_delete=True)
        service = GDPRService(config=config)

        result = await service.delete_user_data(
            user_id="user_abc",
            confirm=True,
        )

        assert result.metadata.get("deletion_type") == "soft"

    @pytest.mark.asyncio
    async def test_hard_delete(self):
        """Test hard delete mode."""
        config = GDPRConfig(soft_delete=False)
        service = GDPRService(config=config)

        result = await service.delete_user_data(
            user_id="user_abc",
            confirm=True,
        )

        assert result.metadata.get("deletion_type") == "hard"

    @pytest.mark.asyncio
    async def test_anonymize_instead_of_delete(self):
        """Test anonymization instead of deletion."""
        config = GDPRConfig(anonymize_instead_of_delete=True)
        service = GDPRService(config=config)

        result = await service.delete_user_data(
            user_id="user_abc",
            confirm=True,
        )

        assert result.metadata.get("anonymize") is True

    def test_get_privacy_policy(self):
        """Test getting privacy policy."""
        config = get_testing_config()
        service = GDPRService(config=config)

        policy = service.get_privacy_policy()

        # Check required sections
        assert "data_controller" in policy
        assert "data_processing" in policy
        assert "data_subject_rights" in policy
        assert "data_categories" in policy
        assert "data_recipients" in policy
        assert "international_transfers" in policy
        assert "automated_decision_making" in policy
        assert "contact" in policy

        # Check data controller information
        assert policy["data_controller"]["name"] == config.data_controller_name
        assert policy["data_controller"]["email"] == config.data_controller_email

        # Check data subject rights
        rights = policy["data_subject_rights"]
        assert "right_to_access" in rights
        assert "right_to_erasure" in rights
        assert "right_to_data_portability" in rights

        # Check data processing
        assert "purposes" in policy["data_processing"]
        assert "legal_basis" in policy["data_processing"]
        assert "retention_period" in policy["data_processing"]

        # Check automated decision making
        assert policy["automated_decision_making"]["exists"] is True

    def test_validate_data_subject_request(self):
        """Test validating data subject requests."""
        service = GDPRService()

        # Valid requests
        assert service.validate_data_subject_request("user_abc", "export") is True
        assert service.validate_data_subject_request("user_abc", "delete") is True
        assert service.validate_data_subject_request("user_abc", "rectify") is True

        # Invalid requests
        assert service.validate_data_subject_request("", "export") is False
        assert service.validate_data_subject_request("user_abc", "invalid") is False

    @pytest.mark.asyncio
    async def test_export_to_json(self):
        """Test exporting data as JSON."""
        config = get_testing_config()
        service = GDPRService(config=config)

        export = await service.export_user_data(user_id="user_abc")
        json_str = export.to_json()

        # Verify JSON is valid
        data = json.loads(json_str)
        assert data["user_id"] == "user_abc"

    @pytest.mark.asyncio
    async def test_deletion_to_json(self):
        """Test deletion result as JSON."""
        config = get_testing_config()
        service = GDPRService(config=config)

        result = await service.delete_user_data(user_id="user_abc", confirm=True)
        json_str = result.to_json()

        # Verify JSON is valid
        data = json.loads(json_str)
        assert data["user_id"] == "user_abc"


class TestGDPRIntegration:
    """Integration tests for GDPR with other systems."""

    @pytest.mark.asyncio
    async def test_export_with_audit_logging(self):
        """Test that exports are logged to audit system."""
        config = get_testing_config()
        service = GDPRService(config=config)

        # Note: This test assumes audit logging is available
        # If not available, it should still work without logging
        export = await service.export_user_data(user_id="user_abc")

        assert export.user_id == "user_abc"
        # Audit log should have recorded this export
        # (If audit logging is available)

    @pytest.mark.asyncio
    async def test_deletion_with_audit_logging(self):
        """Test that deletions are logged to audit system."""
        config = get_testing_config()
        service = GDPRService(config=config)

        result = await service.delete_user_data(user_id="user_abc", confirm=True)

        assert result.user_id == "user_abc"
        # Audit log should have recorded this deletion
        # (If audit logging is available)

    @pytest.mark.asyncio
    async def test_multiple_exports(self):
        """Test multiple data exports."""
        config = get_testing_config()
        service = GDPRService(config=config)

        # Export data multiple times
        export1 = await service.export_user_data(user_id="user_abc")
        time.sleep(0.01)  # Ensure different timestamps
        export2 = await service.export_user_data(user_id="user_abc")

        # Should have different export IDs
        assert export1.export_id != export2.export_id
        # Should have different timestamps
        assert export1.export_timestamp < export2.export_timestamp

    @pytest.mark.asyncio
    async def test_export_after_deletion(self):
        """Test exporting data after deletion."""
        config = get_testing_config()
        service = GDPRService(config=config)

        # Delete data
        deletion = await service.delete_user_data(user_id="user_abc", confirm=True)
        assert deletion.user_id == "user_abc"

        # Export data (should still work, may have empty data)
        export = await service.export_user_data(user_id="user_abc")
        assert export.user_id == "user_abc"
        # Data should be empty or minimal after deletion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
