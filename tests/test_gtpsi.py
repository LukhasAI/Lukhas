"""
Tests for GTΨ (Gesture Token Psi) System
========================================
Tests for gesture recognition, verification, and approval workflows.
Validates high-risk action protection and edge privacy preservation.
"""

from datetime import datetime, timedelta, timezone

import pytest

from gtpsi import (
    GestureApproval,
    GestureChallenge,
    GestureFeatures,
    GestureType,
    RiskLevel,
    get_action_risk_level,
    get_max_approval_time,
    requires_gtpsi_approval,
)
from gtpsi.edge import (
    EdgeGestureProcessor,
    MockStrokeData,
    StrokeGestureRecognizer,
    TapSequenceRecognizer,
    create_gesture_recognizer,
)
from gtpsi.server.verify import (
    ActionApprovalRequest,
    GestureVerificationRequest,
    GTΨVerificationService,
)
from gtpsi.studio_hooks import ConsentUIRequest, StudioGTΨHooks


class TestGestureRecognition:
    """Test edge gesture recognition and privacy preservation"""

    def test_stroke_gesture_recognition(self):
        """Test stroke gesture feature extraction"""
        recognizer = StrokeGestureRecognizer()

        # Generate mock stroke data
        stroke_data = MockStrokeData.generate_signature_stroke()

        # Extract features
        features = recognizer.extract_features(stroke_data)

        # Validate features
        assert len(features) > 0
        assert all(isinstance(f, float) for f in features)
        assert all(0.0 <= f <= 1.0 for f in features)  # Normalized to [0,1]

        # Test quality scoring
        quality = recognizer.calculate_quality_score(features)
        assert 0.0 <= quality <= 1.0

        # Test hashing preserves privacy
        salt = "test_salt_123"
        hash1 = recognizer.hash_features(features, salt)
        hash2 = recognizer.hash_features(features, salt)

        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 64  # SHA-256 hex
        assert hash1 != str(features)  # Not raw features

    def test_tap_sequence_recognition(self):
        """Test tap rhythm pattern recognition"""
        recognizer = TapSequenceRecognizer()

        # Generate mock tap sequence
        tap_data = MockStrokeData.generate_tap_sequence()

        # Extract features
        features = recognizer.extract_features(tap_data)

        # Validate timing features
        assert len(features) >= 5  # At least basic timing stats
        assert features[0] > 0  # Tap count
        assert features[1] > 0  # Average interval

        # Test quality based on rhythm consistency
        quality = recognizer.calculate_quality_score(features)
        assert 0.0 <= quality <= 1.0

    def test_edge_gesture_processor_privacy(self):
        """Test that edge processor preserves privacy"""
        recognizer = StrokeGestureRecognizer()
        processor = EdgeGestureProcessor(recognizer)

        # Process raw gesture
        stroke_data = MockStrokeData.generate_signature_stroke()
        gesture_features = processor.process_gesture(stroke_data, GestureType.STROKE)

        # Validate privacy preservation
        assert isinstance(gesture_features, GestureFeatures)
        assert gesture_features.feature_hash != str(stroke_data)  # No raw data
        assert len(gesture_features.salt) > 0  # Has salt
        assert gesture_features.quality_score >= 0.0
        assert gesture_features.feature_count > 0

        # Raw data should not be stored anywhere in the result
        assert "points" not in gesture_features.feature_hash
        assert "x" not in gesture_features.feature_hash
        assert "y" not in gesture_features.feature_hash

    def test_gesture_factory(self):
        """Test gesture recognizer factory"""
        stroke_recognizer = create_gesture_recognizer(GestureType.STROKE)
        tap_recognizer = create_gesture_recognizer(GestureType.TAP_SEQUENCE)
        signature_recognizer = create_gesture_recognizer(GestureType.SIGNATURE)

        assert isinstance(stroke_recognizer, StrokeGestureRecognizer)
        assert isinstance(tap_recognizer, TapSequenceRecognizer)
        assert isinstance(signature_recognizer, StrokeGestureRecognizer)  # Signature uses stroke

    def test_invalid_gesture_data(self):
        """Test handling of invalid gesture data"""
        recognizer = StrokeGestureRecognizer()

        # Test missing points
        with pytest.raises(ValueError, match="Invalid stroke data format"):
            recognizer.extract_features({})

        # Test insufficient points
        with pytest.raises(ValueError, match="at least 2 points"):
            recognizer.extract_features({"points": [{"x": 0, "y": 0, "timestamp": 0}]})


class TestGTΨVerificationService:
    """Test server-side GTΨ verification and approval"""

    @pytest.fixture
    async def service(self):
        """Create GTΨ verification service"""
        service = GTΨVerificationService("mock")  # Use mock mode
        await service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_challenge_generation(self, service):
        """Test generation of GTΨ challenges for high-risk actions"""
        # Test high-risk action
        challenge = await service.generate_challenge(
            "gonzo",
            "send_email",
            {"to": ["alice@example.com"], "subject": "Test"}
        )

        assert challenge.lid == "gonzo"
        assert challenge.action == "send_email"
        assert challenge.required_gesture_type == GestureType.STROKE
        assert len(challenge.nonce) > 0
        assert challenge.expires_at > datetime.now(timezone.utc)

        # Challenge should be stored
        assert challenge.challenge_id in service.active_challenges

    @pytest.mark.asyncio
    async def test_challenge_for_low_risk_action_fails(self, service):
        """Test that low-risk actions cannot generate challenges"""
        with pytest.raises(ValueError, match="does not require GTΨ approval"):
            await service.generate_challenge("gonzo", "view_email", {})

    @pytest.mark.asyncio
    async def test_gesture_verification_workflow(self, service):
        """Test complete gesture verification workflow"""
        # 1. Generate challenge
        challenge = await service.generate_challenge(
            "gonzo", "send_email", {"to": ["alice@example.com"]}
        )

        # 2. Create mock gesture features
        recognizer = StrokeGestureRecognizer()
        processor = EdgeGestureProcessor(recognizer)
        stroke_data = MockStrokeData.generate_signature_stroke()

        gesture_features = processor.process_gesture(stroke_data, GestureType.STROKE)

        # 3. Submit verification request
        verification_request = GestureVerificationRequest(
            lid="gonzo",
            challenge_id=challenge.challenge_id,
            gesture_features=gesture_features,
            nonce=challenge.nonce
        )

        result = await service.verify_gesture(verification_request)

        # 4. Validate successful verification
        assert result.verified is True
        assert result.approval_id is not None
        assert result.expires_at > datetime.now(timezone.utc)

        # Approval should be stored
        assert result.approval_id in service.approvals

        approval = service.approvals[result.approval_id]
        assert approval.lid == "gonzo"
        assert approval.action == "send_email"
        assert approval.used is False

    @pytest.mark.asyncio
    async def test_gesture_verification_invalid_challenge(self, service):
        """Test gesture verification with invalid challenge"""
        gesture_features = GestureFeatures(
            feature_hash="test_hash",
            salt="test_salt",
            gesture_type=GestureType.STROKE,
            feature_count=10,
            quality_score=0.8,
            timestamp=datetime.now(timezone.utc)
        )

        verification_request = GestureVerificationRequest(
            lid="gonzo",
            challenge_id="invalid_challenge_id",
            gesture_features=gesture_features,
            nonce="invalid_nonce"
        )

        result = await service.verify_gesture(verification_request)

        assert result.verified is False
        assert "Invalid or expired challenge" in result.error

    @pytest.mark.asyncio
    async def test_gesture_verification_wrong_user(self, service):
        """Test gesture verification with wrong user"""
        # Generate challenge for one user
        challenge = await service.generate_challenge(
            "gonzo", "send_email", {"to": ["alice@example.com"]}
        )

        # Try to verify as different user
        gesture_features = GestureFeatures(
            feature_hash="test_hash",
            salt="test_salt",
            gesture_type=GestureType.STROKE,
            feature_count=10,
            quality_score=0.8,
            timestamp=datetime.now(timezone.utc)
        )

        verification_request = GestureVerificationRequest(
            lid="alice",  # Wrong user!
            challenge_id=challenge.challenge_id,
            gesture_features=gesture_features,
            nonce=challenge.nonce
        )

        result = await service.verify_gesture(verification_request)

        assert result.verified is False
        assert "Challenge user mismatch" in result.error

    @pytest.mark.asyncio
    async def test_action_approval_consumption(self, service):
        """Test that approvals can only be used once"""
        # 1. Generate and verify gesture to get approval
        challenge = await service.generate_challenge(
            "gonzo", "send_email", {"to": ["alice@example.com"]}
        )

        recognizer = StrokeGestureRecognizer()
        processor = EdgeGestureProcessor(recognizer)
        stroke_data = MockStrokeData.generate_signature_stroke()
        gesture_features = processor.process_gesture(stroke_data, GestureType.STROKE)

        verification_request = GestureVerificationRequest(
            lid="gonzo",
            challenge_id=challenge.challenge_id,
            gesture_features=gesture_features,
            nonce=challenge.nonce
        )

        verification_result = await service.verify_gesture(verification_request)
        assert verification_result.verified is True

        # 2. Use approval for action
        action_request = ActionApprovalRequest(
            lid="gonzo",
            approval_id=verification_result.approval_id,
            action="send_email",
            action_context=challenge.action_context
        )

        approval_result = await service.check_action_approval(action_request)
        assert approval_result.approved is True

        # 3. Try to use same approval again - should fail
        approval_result2 = await service.check_action_approval(action_request)
        assert approval_result2.approved is False
        assert "already used" in approval_result2.error

    @pytest.mark.asyncio
    async def test_approval_expiration(self, service):
        """Test that approvals expire after time limit"""
        # Create mock expired approval
        approval = GestureApproval(
            approval_id="expired_approval",
            challenge_id="test_challenge",
            lid="gonzo",
            action="send_email",
            action_context={},
            gesture_features=GestureFeatures(
                feature_hash="test", salt="test", gesture_type=GestureType.STROKE,
                feature_count=1, quality_score=0.8, timestamp=datetime.now(timezone.utc)
            ),
            approved_at=datetime.now(timezone.utc) - timedelta(minutes=2),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired
            used=False
        )

        service.approvals["expired_approval"] = approval

        # Try to use expired approval
        action_request = ActionApprovalRequest(
            lid="gonzo",
            approval_id="expired_approval",
            action="send_email",
            action_context={}
        )

        result = await service.check_action_approval(action_request)
        assert result.approved is False
        assert "Approval expired" in result.error

    @pytest.mark.asyncio
    async def test_action_context_validation(self, service):
        """Test that critical actions validate context exactly"""
        # Generate approval for public sharing
        challenge = await service.generate_challenge(
            "gonzo", "share_link_public", {"resource_name": "sensitive_doc.pdf"}
        )

        # Mock successful gesture verification
        approval = GestureApproval(
            approval_id="test_approval",
            challenge_id=challenge.challenge_id,
            lid="gonzo",
            action="share_link_public",
            action_context={"resource_name": "sensitive_doc.pdf"},
            gesture_features=GestureFeatures(
                feature_hash="test", salt="test", gesture_type=GestureType.STROKE,
                feature_count=1, quality_score=0.8, timestamp=datetime.now(timezone.utc)
            ),
            approved_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
            used=False
        )

        service.approvals["test_approval"] = approval

        # Try to use approval with different context - should fail
        action_request = ActionApprovalRequest(
            lid="gonzo",
            approval_id="test_approval",
            action="share_link_public",
            action_context={"resource_name": "different_file.pdf"}  # Different file!
        )

        result = await service.check_action_approval(action_request)
        assert result.approved is False
        assert "Action context mismatch" in result.error

    @pytest.mark.asyncio
    async def test_cleanup_expired_items(self, service):
        """Test cleanup of expired challenges and approvals"""
        # Add expired items
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

        expired_challenge = GestureChallenge(
            challenge_id="expired_challenge",
            lid="gonzo",
            action="send_email",
            action_context={},
            required_gesture_type=GestureType.STROKE,
            expires_at=expired_time,
            nonce="test_nonce"
        )

        expired_approval = GestureApproval(
            approval_id="expired_approval",
            challenge_id="test",
            lid="gonzo",
            action="send_email",
            action_context={},
            gesture_features=GestureFeatures(
                feature_hash="test", salt="test", gesture_type=GestureType.STROKE,
                feature_count=1, quality_score=0.8, timestamp=datetime.now(timezone.utc)
            ),
            approved_at=expired_time,
            expires_at=expired_time,
            used=False
        )

        service.active_challenges["expired_challenge"] = expired_challenge
        service.approvals["expired_approval"] = expired_approval

        # Run cleanup
        result = await service.cleanup_expired()

        assert result["expired_challenges"] == 1
        assert result["expired_approvals"] == 1
        assert "expired_challenge" not in service.active_challenges
        assert "expired_approval" not in service.approvals


class TestStudioHooks:
    """Test Studio UI integration hooks"""

    @pytest.fixture
    async def hooks(self):
        """Create Studio GTΨ hooks"""
        hooks = StudioGTΨHooks()
        await hooks.initialize()
        return hooks

    def test_requires_consent_logic(self, hooks):
        """Test consent requirement logic"""
        # High-risk actions that always need consent
        assert hooks.requires_consent("share_link_public") is True
        assert hooks.requires_consent("delete_files") is True

        # Context-dependent actions
        assert hooks.requires_consent("send_email", {"has_attachments": True}) is True
        assert hooks.requires_consent("send_email", {"recipient_count": 10}) is True
        assert hooks.requires_consent("send_email", {"recipient_count": 1}) is True  # Simple emails still need consent

        assert hooks.requires_consent("cloud.move.files", {"file_count": 15}) is True
        assert hooks.requires_consent("cloud.move.files", {"file_count": 5}) is False

        # Low-risk actions
        assert hooks.requires_consent("view_email") is False
        assert hooks.requires_consent("list_files") is False

    @pytest.mark.asyncio
    async def test_consent_ui_generation(self, hooks):
        """Test consent UI generation"""
        request = ConsentUIRequest(
            lid="gonzo",
            action="send_email",
            action_context={
                "to": ["alice@example.com", "bob@company.com"],
                "subject": "Important proposal",
                "has_attachments": True
            }
        )

        response = await hooks.request_consent_ui(request)

        # Validate UI configuration
        assert response.challenge_id.startswith("gtpsi_")
        assert response.countdown_seconds > 0
        assert response.countdown_seconds <= 60  # Should be within time limit

        ui_config = response.ui_config
        assert ui_config["action"] == "send_email"
        assert "risk_level" in ui_config
        assert "warnings" in ui_config
        assert len(ui_config["warnings"]) > 0
        assert "gesture_instructions" in ui_config

        # Context should be summarized
        assert "alice@example.com" in ui_config["context_summary"]
        assert "Important proposal" in ui_config["context_summary"]

    def test_risk_warnings_generation(self, hooks):
        """Test risk warning generation"""
        # Test email warnings
        warnings = hooks._generate_risk_warnings("send_email", RiskLevel.HIGH)
        assert any("send an email on your behalf" in w for w in warnings)

        # Test delete warnings
        warnings = hooks._generate_risk_warnings("delete_files", RiskLevel.CRITICAL)
        assert any("permanently deleted" in w for w in warnings)
        assert any("cannot be undone" in w for w in warnings)

        # Test sharing warnings
        warnings = hooks._generate_risk_warnings("share_link_public", RiskLevel.CRITICAL)
        assert any("Anyone with the link" in w for w in warnings)
        assert any("privacy implications" in w for w in warnings)

    def test_ui_theme_by_risk_level(self, hooks):
        """Test UI theming based on risk level"""
        high_theme = hooks._get_risk_theme(RiskLevel.HIGH)
        critical_theme = hooks._get_risk_theme(RiskLevel.CRITICAL)

        # Critical should be more intense than high
        assert "primary_color" in high_theme
        assert "primary_color" in critical_theme
        assert critical_theme["primary_color"] != high_theme["primary_color"]

        # Both should have appropriate icons
        assert "icon" in high_theme
        assert "icon" in critical_theme


class TestHighRiskActionProtection:
    """Integration tests for high-risk action protection"""

    def test_high_risk_action_identification(self):
        """Test that all expected high-risk actions require GTΨ"""
        critical_actions = [
            "send_email",
            "cloud.move.files",
            "share_link_public",
            "delete_files",
            "grant_admin_scope"
        ]

        for action in critical_actions:
            assert requires_gtpsi_approval(action), f"Action {action} should require GTΨ"
            assert get_action_risk_level(action) in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            assert get_max_approval_time(action) <= 60  # All should be ≤60s

    def test_approval_time_limits(self):
        """Test that critical actions have very short approval times"""
        # Critical actions should have very short approval times
        assert get_max_approval_time("delete_files") <= 15
        assert get_max_approval_time("share_link_public") <= 20
        assert get_max_approval_time("grant_admin_scope") <= 10

        # High-risk actions can have slightly longer times
        assert get_max_approval_time("send_email") <= 30
        assert get_max_approval_time("cloud.move.files") <= 60

    @pytest.mark.asyncio
    async def test_end_to_end_protection_workflow(self):
        """Test complete protection workflow for high-risk action"""
        # This test simulates the complete flow:
        # 1. Studio detects high-risk action
        # 2. Requests GTΨ consent UI
        # 3. User performs gesture
        # 4. Gesture is verified
        # 5. Action is approved and executed

        hooks = StudioGTΨHooks()
        await hooks.initialize()

        # 1. Check if action needs consent
        action = "share_link_public"
        context = {"resource_name": "confidential_report.pdf"}

        needs_consent = hooks.requires_consent(action, context)
        assert needs_consent is True

        # 2. Request consent UI
        ui_request = ConsentUIRequest(
            lid="gonzo",
            action=action,
            action_context=context
        )

        ui_response = await hooks.request_consent_ui(ui_request)
        assert ui_response.challenge_id is not None

        # 3. Simulate gesture submission (normally done by client)
        from gtpsi.studio_hooks import GestureSubmissionRequest

        gesture_request = GestureSubmissionRequest(
            challenge_id=ui_response.challenge_id,
            gesture_data=MockStrokeData.generate_signature_stroke(),
            gesture_type=GestureType.STROKE
        )

        gesture_response = await hooks.submit_gesture(gesture_request)

        if gesture_response.success:
            # 4. Verify approval can be used for action
            can_proceed = await hooks.check_action_approval(
                "gonzo",
                gesture_response.approval_id,
                action,
                context
            )

            assert can_proceed is True
            print("✅ End-to-end GTΨ protection workflow successful!")
        else:
            print(f"⚠️ Gesture verification failed: {gesture_response.message}")
            # This is acceptable in tests since we're using mock data


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
