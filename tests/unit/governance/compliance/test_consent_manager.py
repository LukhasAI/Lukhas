# owner: Jules-04
# tier: tier2
# module_uid: candidate.governance.consent.consent_manager
# criticality: P1

from datetime import datetime, timedelta, timezone

import pytest

from lukhas.governance.consent.consent_manager import (
    AdvancedConsentManager,
    ConsentMethod,
    ConsentStatus,
    DataCategory,
)


@pytest.fixture
def manager() -> AdvancedConsentManager:
    """Provides a fresh instance of AdvancedConsentManager for each test."""
    return AdvancedConsentManager()


@pytest.mark.asyncio
class TestAdvancedConsentManager:
    async def test_initialization(self, manager: AdvancedConsentManager):
        """Test that the consent manager initializes with standard purposes."""
        await manager.initialize()
        assert len(manager.consent_purposes) > 0
        assert "essential_functionality" in manager.consent_purposes
        assert manager.metrics["total_consents"] == 0

    async def test_request_consent_success(self, manager: AdvancedConsentManager):
        """Test successful consent request for a single purpose."""
        await manager.initialize()
        user_id = "test-user-123"
        purpose_id = "service_improvement"

        valid_context = {
            "privacy_policy_version": "1.1",
            "ip_address": "127.0.0.1",
            "privacy_policy_accessible": True,
            "withdrawal_info_provided": True,
            "necessity_assessed": True,
        }

        consent_records = await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM, context=valid_context
        )

        assert purpose_id in consent_records
        record = consent_records[purpose_id]

        assert record.user_id == user_id
        assert record.purpose.purpose_id == purpose_id
        assert record.status == ConsentStatus.GRANTED

        assert len(manager.consent_receipts) == 1
        assert manager.metrics["total_consents"] == 1
        assert manager.metrics["active_consents"] == 1

    async def test_withdraw_consent(self, manager: AdvancedConsentManager):
        """Test withdrawing a previously granted consent."""
        await manager.initialize()
        user_id = "test-user-456"
        purpose_id = "personalization"
        valid_context = {
            "privacy_policy_accessible": True,
            "withdrawal_info_provided": True,
            "necessity_assessed": True,
        }

        await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM, context=valid_context
        )

        validation_before = await manager.validate_consent(user_id, purpose_id)
        assert validation_before["valid"] is True

        success = await manager.withdraw_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.API_CALL, reason="User requested deletion"
        )
        assert success is True

        validation_after = await manager.validate_consent(user_id, purpose_id)
        assert validation_after["valid"] is False
        assert validation_after["reason"] == "No active consent found"

        user_consents = await manager.export_consent_audit_trail(user_id)
        withdrawn_record = user_consents[0]
        assert withdrawn_record["status"] == ConsentStatus.WITHDRAWN.value
        assert withdrawn_record["withdrawal_info"]["method"] == ConsentMethod.API_CALL.value

        assert manager.metrics["withdrawn_consents"] == 1
        assert manager.metrics["active_consents"] == 0

    async def test_consent_expiration_and_cleanup(self, manager: AdvancedConsentManager):
        """Test that consent expires and is cleaned up."""
        await manager.initialize()
        user_id = "test-user-789"
        purpose_id = "marketing_communications"
        valid_context = {
            "privacy_policy_accessible": True,
            "withdrawal_info_provided": True,
            "necessity_assessed": True,
        }

        await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM, context=valid_context
        )

        consent_id = list(manager.consent_records.keys())[0]
        record = manager.consent_records[consent_id]

        record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

        validation = await manager.validate_consent(user_id, purpose_id)
        assert validation["valid"] is False
        assert validation["reason"] == "Consent has expired"
        assert record.status == ConsentStatus.EXPIRED

        record.status = ConsentStatus.GRANTED
        record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        cleanup_count = await manager.cleanup_expired_consents()
        assert cleanup_count == 1
        assert record.status == ConsentStatus.EXPIRED
        assert manager.metrics["expired_consents"] == 1

    async def test_request_consent_for_unknown_purpose(self, manager: AdvancedConsentManager):
        """Test requesting consent for a purpose that does not exist."""
        await manager.initialize()
        user_id = "test-user-unknown"
        purpose_id = "non_existent_purpose"

        consent_records = await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM
        )

        assert not consent_records
        assert len(manager.consent_records) == 0

    async def test_gdpr_validation_failure(self, manager: AdvancedConsentManager):
        """Test that consent request fails if GDPR Article 7 requirements are not met."""
        await manager.initialize()
        user_id = "test-user-gdpr-fail"
        purpose_id = "research_development"

        invalid_context = {"privacy_policy_accessible": True, "withdrawal_info_provided": False}

        consent_records = await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM, context=invalid_context
        )

        record = consent_records[purpose_id]
        assert record.status == ConsentStatus.INVALID
        assert "GDPR validation failed: Withdrawal information not provided" in record.guardian_validations

    async def test_validate_consent_for_specific_data_categories(self, manager: AdvancedConsentManager):
        """Test validation for specific data categories within a purpose."""
        await manager.initialize()
        user_id = "test-user-datacat"
        purpose_id = "personalization"
        valid_context = {
            "privacy_policy_accessible": True,
            "withdrawal_info_provided": True,
            "necessity_assessed": True,
        }

        await manager.request_consent(
            user_id=user_id, purpose_ids=[purpose_id], method=ConsentMethod.WEB_FORM, context=valid_context
        )

        validation1 = await manager.validate_consent(user_id, purpose_id, data_categories=[DataCategory.BEHAVIORAL])
        assert validation1["valid"] is True

        validation2 = await manager.validate_consent(
            user_id, purpose_id, data_categories=[DataCategory.BEHAVIORAL, DataCategory.DEMOGRAPHIC]
        )
        assert validation2["valid"] is True

        validation3 = await manager.validate_consent(
            user_id, purpose_id, data_categories=[DataCategory.BEHAVIORAL, DataCategory.FINANCIAL]
        )
        assert validation3["valid"] is False
        assert validation3["reason"] == "Consent doesn't cover all requested data categories"
        assert "financial" in validation3["uncovered_categories"]

    async def test_export_audit_trail(self, manager: AdvancedConsentManager):
        """Test the export_consent_audit_trail method."""
        await manager.initialize()
        user_id_1 = "audit-user-1"
        user_id_2 = "audit-user-2"
        valid_context = {
            "privacy_policy_accessible": True,
            "withdrawal_info_provided": True,
            "necessity_assessed": True,
        }

        await manager.request_consent(
            user_id=user_id_1, purpose_ids=["service_improvement"], method=ConsentMethod.WEB_FORM, context=valid_context
        )
        await manager.request_consent(
            user_id=user_id_2, purpose_ids=["personalization"], method=ConsentMethod.API_CALL, context=valid_context
        )

        audit_trail_1 = await manager.export_consent_audit_trail(user_id=user_id_1)
        assert len(audit_trail_1) == 1
        assert audit_trail_1[0]["user_id"] == user_id_1
        assert audit_trail_1[0]["purpose"]["id"] == "service_improvement"

        audit_trail_all = await manager.export_consent_audit_trail()
        assert len(audit_trail_all) == 2
