import pytest
from datetime import datetime, timedelta, timezone
from labs.governance.consent.consent_manager import (
    AdvancedConsentManager,
    ConsentStatus,
    ConsentType,
    ConsentMethod,
    DataCategory,
    ConsentRecord,
)

@pytest.fixture
async def consent_manager():
    """Fixture for an AdvancedConsentManager instance."""
    manager = AdvancedConsentManager()
    await manager.initialize()
    return manager

@pytest.mark.asyncio
async def test_initialization(consent_manager):
    """Test that the AdvancedConsentManager initializes correctly."""
    manager = await consent_manager
    assert manager is not None
    assert len(manager.consent_purposes) > 0

@pytest.mark.asyncio
async def test_request_and_validate_consent(consent_manager):
    """Test requesting and validating a consent."""
    manager = await consent_manager
    user_id = "user_123"
    purpose_id = "service_improvement"

    await manager.request_consent(
        user_id, [purpose_id], ConsentMethod.WEB_FORM, {"privacy_policy_accessible": True, "withdrawal_info_provided": True}
    )

    validation = await manager.validate_consent(user_id, purpose_id)
    assert validation["valid"]
    assert validation["consent_id"] is not None

@pytest.mark.asyncio
async def test_withdraw_consent(consent_manager):
    """Test withdrawing a consent."""
    manager = await consent_manager
    user_id = "user_456"
    purpose_id = "personalization"

    await manager.request_consent(
        user_id, [purpose_id], ConsentMethod.WEB_FORM, {"privacy_policy_accessible": True, "withdrawal_info_provided": True}
    )

    await manager.withdraw_consent(user_id, [purpose_id])

    validation = await manager.validate_consent(user_id, purpose_id)
    assert not validation["valid"]
    assert validation["reason"] == "Consent status is withdrawn"

@pytest.mark.asyncio
async def test_expired_consent(consent_manager):
    """Test that expired consent is correctly identified."""
    manager = await consent_manager
    user_id = "user_789"
    purpose_id = "marketing_communications"

    # Manually create an expired consent record
    consent_record = await manager._create_consent_record(
        user_id,
        manager.consent_purposes[purpose_id],
        ConsentMethod.WEB_FORM,
        {"privacy_policy_accessible": True, "withdrawal_info_provided": True},
    )
    consent_record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    manager.consent_records[consent_record.consent_id] = consent_record

    validation = await manager.validate_consent(user_id, purpose_id)
    assert not validation["valid"]
    assert validation["reason"] == "Consent has expired"

@pytest.mark.asyncio
async def test_data_category_validation(consent_manager):
    """Test validation of data categories."""
    manager = await consent_manager
    user_id = "user_101"
    purpose_id = "personalization"

    await manager.request_consent(
        user_id, [purpose_id], ConsentMethod.WEB_FORM, {"privacy_policy_accessible": True, "withdrawal_info_provided": True}
    )

    validation = await manager.validate_consent(user_id, purpose_id, data_categories=[DataCategory.BEHAVIORAL])
    assert validation["valid"]

    validation = await manager.validate_consent(user_id, purpose_id, data_categories=[DataCategory.FINANCIAL])
    assert not validation["valid"]
    assert "uncovered_categories" in validation

@pytest.mark.asyncio
async def test_audit_trail(consent_manager):
    """Test the audit trail functionality."""
    manager = await consent_manager
    user_id = "user_audit"
    purpose_id = "research_development"

    await manager.request_consent(
        user_id, [purpose_id], ConsentMethod.API_CALL, {"privacy_policy_accessible": True, "withdrawal_info_provided": True}
    )

    audit_trail = await manager.export_consent_audit_trail(user_id)
    assert len(audit_trail) == 1
    assert audit_trail[0]["user_id"] == user_id
    assert audit_trail[0]["purpose"]["id"] == purpose_id

@pytest.mark.asyncio
async def test_cleanup_expired_consents(consent_manager):
    """Test the cleanup_expired_consents method."""
    manager = await consent_manager
    user_id = "user_cleanup"
    purpose_id = "marketing_communications"

    consent_record = await manager._create_consent_record(
        user_id,
        manager.consent_purposes[purpose_id],
        ConsentMethod.WEB_FORM,
        {"privacy_policy_accessible": True, "withdrawal_info_provided": True},
    )
    consent_record.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    manager.consent_records[consent_record.consent_id] = consent_record

    cleanup_count = await manager.cleanup_expired_consents()
    assert cleanup_count == 1

    validation = await manager.validate_consent(user_id, purpose_id)
    assert not validation["valid"]
    assert validation["reason"] == "Consent has expired"

@pytest.mark.asyncio
async def test_get_user_consent_dashboard(consent_manager):
    """Test the get_user_consent_dashboard method."""
    manager = await consent_manager
    user_id = "user_dashboard"
    purpose_id = "personalization"

    await manager.request_consent(
        user_id, [purpose_id], ConsentMethod.WEB_FORM, {"privacy_policy_accessible": True, "withdrawal_info_provided": True}
    )

    dashboard = await manager.get_user_consent_dashboard(user_id)
    assert dashboard["user_id"] == user_id
    assert dashboard["total_consents"] == 1
    assert dashboard["active_consents"] == 1

@pytest.mark.asyncio
async def test_validate_non_existent_purpose(consent_manager):
    """Test validation for a purpose that doesn't exist."""
    manager = await consent_manager
    user_id = "user_no_purpose"
    purpose_id = "non_existent_purpose"

    validation = await manager.validate_consent(user_id, purpose_id)
    assert not validation["valid"]
    assert validation["reason"] == "No active consent found"
