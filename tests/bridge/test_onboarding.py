"""
Tests for Onboarding API Module

Comprehensive functional tests for onboarding.py implementation.
Replaces all pytest.skip() with actual test implementations.

Part of BATCH-JULES-API-GOVERNANCE-02
Tasks Tested:
- TODO-HIGH-BRIDGE-API-a1b2c3d4: Onboarding start logic
- TODO-HIGH-BRIDGE-API-e5f6a7b8: Tier setup logic
- TODO-HIGH-BRIDGE-API-c9d0e1f2: Consent collection logic
- TODO-HIGH-BRIDGE-API-g3h4i5j6: Onboarding completion logic
"""

from datetime import datetime, timedelta, timezone

import pytest

from labs.bridge.api.onboarding import (
    ConsentRecord,
    OnboardingAPI,
    OnboardingSession,
    OnboardingStatus,
    OnboardingTier,
    TierConfiguration,
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def api():
    """Fresh OnboardingAPI instance for each test."""
    return OnboardingAPI()


@pytest.fixture
async def started_session(api):
    """Pre-started onboarding session."""
    result = await api.start_onboarding(email="test@example.com")
    return result["session_id"]


@pytest.fixture
async def session_with_tier(api):
    """Session with tier already assigned."""
    result = await api.start_onboarding(email="test@example.com")
    session_id = result["session_id"]
    await api.setup_tier(session_id=session_id, tier="free")
    return session_id


@pytest.fixture
async def session_with_consent(api):
    """Session with tier and consent collected."""
    result = await api.start_onboarding(email="test@example.com")
    session_id = result["session_id"]
    await api.setup_tier(session_id=session_id, tier="free")
    await api.collect_consent(
        session_id=session_id,
        consents={"data_processing": True, "analytics": True}
    )
    return session_id


# ============================================================================
# Test Onboarding Start (TODO-HIGH-BRIDGE-API-a1b2c3d4)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_start_success(api):
    """Test successful onboarding initiation."""
    result = await api.start_onboarding(
        email="test@example.com",
        metadata={"source": "web", "device": "desktop"},
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )

    # Verify response structure
    assert "session_id" in result
    assert result["session_id"].startswith("onboard_")
    assert "user_id" in result
    assert result["user_id"].startswith("user_")
    assert result["status"] == "initiated"
    assert "expires_at" in result
    assert result["next_steps"] == ["verify_email", "setup_profile", "select_tier", "grant_consent"]

    # Verify session was created
    session = api.sessions[result["session_id"]]
    assert session.email == "test@example.com"
    assert session.status == OnboardingStatus.INITIATED
    assert session.metadata["source"] == "web"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_start_invalid_email(api):
    """Test onboarding with invalid email addresses."""
    with pytest.raises(ValueError, match="Invalid email address"):
        await api.start_onboarding(email="not-an-email")

    with pytest.raises(ValueError, match="Invalid email address"):
        await api.start_onboarding(email="")

    with pytest.raises(ValueError, match="Invalid email address"):
        await api.start_onboarding(email=None)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_duplicate_session(api):
    """Test preventing duplicate active sessions for same email."""
    # First session succeeds
    result1 = await api.start_onboarding(email="test@example.com")
    assert "session_id" in result1

    # Second session for same email fails
    with pytest.raises(ValueError, match="already has active onboarding session"):
        await api.start_onboarding(email="test@example.com")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_session_expiration_set(api):
    """Test that session expiration is properly set to 24 hours."""
    result = await api.start_onboarding(email="test@example.com")
    session = api.sessions[result["session_id"]]

    # Verify expiration is ~24 hours from now
    assert session.expires_at is not None
    time_until_expiration = (session.expires_at - datetime.now(timezone.utc)).total_seconds()
    expected_seconds = 24 * 60 * 60  # 24 hours
    assert abs(time_until_expiration - expected_seconds) < 10  # Allow 10 second variance


# ============================================================================
# Test Tier Setup (TODO-HIGH-BRIDGE-API-e5f6a7b8)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_setup_free_tier(api, started_session):
    """Test free tier assignment."""
    result = await api.setup_tier(session_id=started_session, tier="free")

    assert result["tier"] == "free"
    assert "tier_config" in result
    assert result["tier_config"]["max_requests_per_day"] > 0
    assert result["tier_config"]["max_context_length"] > 0
    assert isinstance(result["tier_config"]["features"], list)
    assert result["next_steps"] == ["grant_consent", "complete_onboarding"]

    # Verify session updated
    session = api.sessions[started_session]
    assert session.tier == OnboardingTier.FREE
    assert session.status == OnboardingStatus.TIER_ASSIGNED
    assert session.tier_config is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_setup_pro_with_payment(api, started_session):
    """Test pro tier assignment with valid payment token."""
    result = await api.setup_tier(
        session_id=started_session,
        tier="pro",
        payment_token="tok_valid_payment_12345678"
    )

    assert result["tier"] == "pro"
    assert result["tier_config"]["max_requests_per_day"] > 100

    session = api.sessions[started_session]
    assert session.tier == OnboardingTier.PRO


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_setup_pro_without_payment(api, started_session):
    """Test pro tier fails without payment token."""
    with pytest.raises(ValueError, match="requires payment"):
        await api.setup_tier(session_id=started_session, tier="pro")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_setup_invalid_tier(api, started_session):
    """Test rejection of invalid tier names."""
    with pytest.raises(ValueError, match="Invalid tier"):
        await api.setup_tier(session_id=started_session, tier="invalid_premium_ultra")

    with pytest.raises(ValueError, match="Invalid tier"):
        await api.setup_tier(session_id=started_session, tier="super_mega_tier")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_setup_invalid_session(api):
    """Test tier setup with non-existent session."""
    with pytest.raises(ValueError, match="Session not found"):
        await api.setup_tier(session_id="nonexistent_session", tier="free")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tier_configuration_schema_loading():
    """Test TierConfiguration loads from schema or defaults."""
    # Test all tier types load without error
    free_config = TierConfiguration.load_from_schema(OnboardingTier.FREE)
    assert free_config.tier == OnboardingTier.FREE
    assert free_config.max_requests_per_day > 0
    assert not free_config.requires_payment

    pro_config = TierConfiguration.load_from_schema(OnboardingTier.PRO)
    assert pro_config.tier == OnboardingTier.PRO
    assert pro_config.requires_payment

    enterprise_config = TierConfiguration.load_from_schema(OnboardingTier.ENTERPRISE)
    assert enterprise_config.tier == OnboardingTier.ENTERPRISE
    assert enterprise_config.max_requests_per_day > pro_config.max_requests_per_day


# ============================================================================
# Test Consent Collection (TODO-HIGH-BRIDGE-API-c9d0e1f2)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_collection_success(api, session_with_tier):
    """Test successful GDPR-compliant consent collection."""
    result = await api.collect_consent(
        session_id=session_with_tier,
        consents={
            "data_processing": True,
            "analytics": True,
            "marketing": False
        },
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0"
    )

    assert result["session_id"] == session_with_tier
    assert len(result["consents"]) == 3
    assert result["guardian_validation"] == "PASSED"
    assert result["next_steps"] == ["complete_onboarding"]

    # Verify consent records
    session = api.sessions[session_with_tier]
    assert session.status == OnboardingStatus.CONSENT_COLLECTED
    assert len(session.consents) == 3

    # Verify consent record structure
    consent = session.consents[0]
    assert consent.consent_id.startswith("consent_")
    assert consent.user_id == session.user_id
    assert consent.ip_address == "192.168.1.1"
    assert consent.user_agent == "Mozilla/5.0"
    assert isinstance(consent.granted, bool)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_missing_required(api, session_with_tier):
    """Test consent collection fails without required data_processing consent."""
    with pytest.raises(ValueError, match="Required consent missing"):
        await api.collect_consent(
            session_id=session_with_tier,
            consents={"analytics": True, "marketing": False}  # Missing data_processing
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_required_denied(api, session_with_tier):
    """Test consent collection fails if required consent is denied."""
    with pytest.raises(ValueError, match="must consent"):
        await api.collect_consent(
            session_id=session_with_tier,
            consents={"data_processing": False}  # Required consent denied
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_revocation_flow(api, session_with_consent):
    """Test GDPR Article 7(3) consent revocation."""
    session = api.sessions[session_with_consent]

    # Find a granted consent
    consent_to_revoke = None
    for consent in session.consents:
        if consent.granted:
            consent_to_revoke = consent
            break

    assert consent_to_revoke is not None

    # Revoke consent
    result = await api.revoke_consent(
        session_id=session_with_consent,
        consent_id=consent_to_revoke.consent_id,
        ip_address="192.168.1.1"
    )

    assert result["status"] == "revoked"
    assert "revoked_at" in result

    # Verify consent was revoked
    assert not consent_to_revoke.granted
    assert consent_to_revoke.withdrawal_timestamp is not None


# ============================================================================
# Test Onboarding Completion (TODO-HIGH-BRIDGE-API-g3h4i5j6)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_completion_success(api, session_with_consent):
    """Test successful onboarding completion with identity activation."""
    result = await api.complete_onboarding(
        session_id=session_with_consent,
        profile_data={"name": "Test User", "preferences": {"theme": "dark"}}
    )

    assert result["status"] == "completed"
    assert result["session_id"] == session_with_consent
    assert "lambda_id" in result
    assert result["lambda_id"].startswith("Λ")
    assert result["identity_activated"] is True
    assert "access_token" in result
    assert result["tier"] == "free"

    # Verify Trinity Framework integration
    assert "trinity_framework" in result
    trinity = result["trinity_framework"]
    assert trinity["identity"]["lambda_id"]
    assert trinity["consciousness"]["profile_initialized"] is True
    assert trinity["guardian"]["consents_collected"] > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_lambda_id_generation(api):
    """Test ΛID generation and format."""
    # Create complete onboarding flow
    start = await api.start_onboarding(email="test@example.com")
    session_id = start["session_id"]

    await api.setup_tier(
        session_id=session_id,
        tier="pro",
        payment_token="tok_test_payment"
    )
    await api.collect_consent(
        session_id=session_id,
        consents={"data_processing": True}
    )

    result = await api.complete_onboarding(session_id=session_id)

    # Verify ΛID format: Λ{hash}-{tier}-{suffix}
    lambda_id = result["lambda_id"]
    assert lambda_id.startswith("Λ")
    assert "-PRO-" in lambda_id
    parts = lambda_id.split("-")
    assert len(parts) == 3

    # Verify session state
    session = api.sessions[session_id]
    assert session.identity_activated is True
    assert session.lambda_id == lambda_id
    assert session.status == OnboardingStatus.COMPLETED
    assert session.completed_at is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_completion_missing_tier(api, started_session):
    """Test completion fails without tier assignment."""
    with pytest.raises(ValueError, match="Cannot complete onboarding in current status.*prerequisite"):
        await api.complete_onboarding(session_id=started_session)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_completion_missing_consent(api, session_with_tier):
    """Test completion fails without consent collection."""
    with pytest.raises(ValueError, match="Cannot complete onboarding in current status.*prerequisite"):
        await api.complete_onboarding(session_id=session_with_tier)


# ============================================================================
# Integration Tests - Full Flows
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_onboarding_flow_free_tier(api):
    """Integration test: Complete free tier onboarding flow."""
    # Step 1: Start
    start = await api.start_onboarding(
        email="integration@example.com",
        metadata={"source": "integration_test"}
    )
    session_id = start["session_id"]
    assert start["status"] == "initiated"

    # Step 2: Setup tier
    tier = await api.setup_tier(session_id=session_id, tier="free")
    assert tier["tier"] == "free"

    # Step 3: Collect consent
    consent = await api.collect_consent(
        session_id=session_id,
        consents={
            "data_processing": True,
            "analytics": True,
            "marketing": False
        }
    )
    assert consent["guardian_validation"] == "PASSED"

    # Step 4: Complete
    completion = await api.complete_onboarding(
        session_id=session_id,
        profile_data={"name": "Integration User"}
    )

    assert completion["status"] == "completed"
    assert completion["identity_activated"] is True
    assert completion["lambda_id"].startswith("Λ")
    assert "-FREE-" in completion["lambda_id"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_onboarding_flow_pro_tier(api):
    """Integration test: Complete pro tier onboarding with payment."""
    start = await api.start_onboarding(email="pro@example.com")
    session_id = start["session_id"]

    tier = await api.setup_tier(
        session_id=session_id,
        tier="pro",
        payment_token="tok_integration_payment"
    )
    assert tier["tier"] == "pro"

    await api.collect_consent(
        session_id=session_id,
        consents={"data_processing": True}
    )

    completion = await api.complete_onboarding(session_id=session_id)

    assert "-PRO-" in completion["lambda_id"]
    assert completion["tier"] == "pro"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_session_status_retrieval(api, session_with_consent):
    """Test retrieving session status at any point."""
    status = await api.get_session_status(session_with_consent)

    assert status["session_id"] == session_with_consent
    assert status["email"] == "test@example.com"
    assert status["status"] == "consent_collected"
    assert status["tier"] == "free"
    assert len(status["consents"]) > 0


# ============================================================================
# Error Handling & Edge Cases
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_expired_session_handling(api):
    """Test that expired sessions are properly rejected."""
    start = await api.start_onboarding(email="expiry@example.com")
    session_id = start["session_id"]

    # Manually expire the session
    session = api.sessions[session_id]
    session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

    # Operations should fail
    with pytest.raises(ValueError, match="Session expired"):
        await api.setup_tier(session_id=session_id, tier="free")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_invalid_session_operations(api):
    """Test operations with non-existent session IDs."""
    with pytest.raises(ValueError, match="Session not found"):
        await api.setup_tier(session_id="fake_session", tier="free")

    with pytest.raises(ValueError, match="Session not found"):
        await api.collect_consent(
            session_id="fake_session",
            consents={"data_processing": True}
        )

    with pytest.raises(ValueError, match="Session not found"):
        await api.complete_onboarding(session_id="fake_session")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_revoke_nonexistent_consent(api, session_with_consent):
    """Test revoking non-existent consent ID."""
    with pytest.raises(ValueError, match="Consent not found"):
        await api.revoke_consent(
            session_id=session_with_consent,
            consent_id="fake_consent_id"
        )


@pytest.mark.asyncio
@pytest.mark.unit
async def test_revoke_already_revoked_consent(api, session_with_consent):
    """Test revoking already revoked consent."""
    session = api.sessions[session_with_consent]
    consent_id = session.consents[0].consent_id

    # First revocation succeeds
    await api.revoke_consent(session_id=session_with_consent, consent_id=consent_id)

    # Second revocation fails
    with pytest.raises(ValueError, match="already revoked"):
        await api.revoke_consent(session_id=session_with_consent, consent_id=consent_id)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_record_structure(api, session_with_tier):
    """Test ConsentRecord data structure integrity."""
    await api.collect_consent(
        session_id=session_with_tier,
        consents={"data_processing": True, "marketing": False},
        ip_address="10.0.0.1",
        user_agent="Test Agent"
    )

    session = api.sessions[session_with_tier]
    consent = session.consents[0]

    # Test to_dict() conversion
    consent_dict = consent.to_dict()
    assert "consent_id" in consent_dict
    assert "user_id" in consent_dict
    assert "consent_type" in consent_dict
    assert "granted" in consent_dict
    assert "timestamp" in consent_dict
    assert consent_dict["ip_address"] == "10.0.0.1"
    assert consent_dict["version"] == "1.0"


# ============================================================================
# Coverage: Additional Test Cases
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_onboarding_session_to_dict(api, session_with_consent):
    """Test OnboardingSession.to_dict() serialization."""
    session = api.sessions[session_with_consent]
    session_dict = session.to_dict()

    assert "session_id" in session_dict
    assert "user_id" in session_dict
    assert "email" in session_dict
    assert "status" in session_dict
    assert "tier" in session_dict
    assert "consents" in session_dict
    assert isinstance(session_dict["consents"], list)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_payment_verification_placeholder(api, started_session):
    """Test payment verification logic (placeholder for real integration)."""
    # Valid payment token format
    result = await api.setup_tier(
        session_id=started_session,
        tier="pro",
        payment_token="tok_valid_12345678"  # 8+ characters
    )
    assert result["tier"] == "pro"

    # Invalid payment token (too short) should fail
    start2 = await api.start_onboarding(email="test2@example.com")
    with pytest.raises(ValueError, match="Payment verification failed"):
        await api.setup_tier(
            session_id=start2["session_id"],
            tier="pro",
            payment_token="short"  # < 8 characters
        )
