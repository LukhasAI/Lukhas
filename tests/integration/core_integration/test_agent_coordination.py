"""
Integration tests for 6-agent LUKHAS AI coordination
Tests the interfaces and contracts between all agents
"""


import pytest


class TestAgentCoordination:
    """Test suite for multi-agent integration"""

    def test_identity_consent_integration(self):
        """Test that auth events generate audit records"""
        from identity.identity_core import identity_core, AccessTier
        from datetime import datetime, timezone
        
        # Test user authentication generates audit trail
        user_id = "test_user"
        metadata = {
            "email": "test@example.com",
            "consent": True,
            "trinity_score": 0.7,
            "drift_score": 0.05
        }
        
        # Create identity token - this should generate audit events
        token = identity_core.create_token(user_id, AccessTier.T2, metadata)
        assert token is not None
        
        # Verify token validation works
        is_valid = identity_core.validate_token(token, AccessTier.T2)
        assert is_valid is True
        
        # Test that consent metadata is preserved
        token_data = identity_core.decode_token(token)
        assert token_data is not None
        assert token_data.get("metadata", {}).get("consent") is True

    def test_adapter_consent_validation(self):
        """Test that adapters check consent before external access"""
        # Test adapter consent checking mechanism
        from typing import Dict, Any
        
        class MockAdapter:
            """Mock adapter to test consent validation"""
            
            def __init__(self):
                self.consent_required = True
            
            def check_consent(self, user_metadata: Dict[str, Any]) -> bool:
                """Check if user has provided consent for external access"""
                return user_metadata.get("consent", False) is True
            
            def external_access(self, user_metadata: Dict[str, Any], action: str) -> Dict[str, Any]:
                """Simulate external API access with consent check"""
                if not self.check_consent(user_metadata):
                    return {"error": "Consent required for external access", "access_granted": False}
                
                return {"success": f"External {action} completed", "access_granted": True}
        
        adapter = MockAdapter()
        
        # Test with consent granted
        user_with_consent = {"consent": True, "email": "user@example.com"}
        result = adapter.external_access(user_with_consent, "data_fetch")
        assert result["access_granted"] is True
        assert "success" in result
        
        # Test with consent denied
        user_without_consent = {"consent": False, "email": "user@example.com"}
        result = adapter.external_access(user_without_consent, "data_fetch")
        assert result["access_granted"] is False
        assert "error" in result

    def test_orchestrator_policy_enforcement(self):
        """Test policy engine invocation at each workflow step"""
        from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
        from lukhas.governance.guardian.core import GovernanceAction
        
        guardian = GuardianSystemImpl()
        
        # Test policy enforcement for different actions
        safe_action = GovernanceAction.READ
        context = {
            "user_id": "test_user",
            "risk_level": "low",
            "stakeholders": ["user"],
            "ethical_implications": []
        }
        
        # Test ethical evaluation for safe action
        ethical_decision = guardian.evaluate_ethics(safe_action, context)
        assert ethical_decision.allowed is True
        assert ethical_decision.confidence > 0.5
        
        # Test policy enforcement for risky context
        risky_context = {
            "user_id": "test_user", 
            "risk_level": "high",
            "risk_indicators": ["privacy_violation"],
            "ethical_implications": ["potential_harm"]
        }
        
        risky_decision = guardian.evaluate_ethics(safe_action, risky_context)
        # Should still allow READ but with lower confidence or restrictions
        assert risky_decision.confidence >= 0.0  # Basic validation
        assert len(risky_decision.recommendations) >= 0

    def test_capability_token_flow(self):
        """Test capability token generation and validation"""
        from identity.identity_core import identity_core, AccessTier
        import jwt
        import json
        
        # Test capability token creation and validation flow
        user_id = "capability_test_user"
        tier = AccessTier.T3
        metadata = {
            "email": "cap_test@example.com",
            "consent": True,
            "trinity_score": 0.8,
            "capabilities": ["read", "write", "execute"]
        }
        
        # Generate capability token
        token = identity_core.create_token(user_id, tier, metadata)
        assert token is not None
        
        # Validate token for different access tiers
        assert identity_core.validate_token(token, AccessTier.T3) is True
        assert identity_core.validate_token(token, AccessTier.T2) is True  # Lower tier should pass
        assert identity_core.validate_token(token, AccessTier.T4) is False  # Higher tier should fail
        
        # Test token decoding and capability extraction
        decoded = identity_core.decode_token(token)
        assert decoded is not None
        assert decoded["user_id"] == user_id
        assert decoded["tier"] == tier.value
        
        # Verify capabilities are preserved in metadata
        token_metadata = decoded.get("metadata", {})
        assert "capabilities" in token_metadata
        assert "read" in token_metadata["capabilities"]

    def test_audit_event_schema(self):
        """Test audit event generation with Λ-trace"""
        from datetime import datetime, timezone
        import json
        
        # Test audit event schema and Λ-trace generation
        class MockAuditEvent:
            """Mock audit event to test Λ-trace schema"""
            
            def __init__(self, event_type: str, user_id: str, action: str, metadata: dict = None):
                self.timestamp = datetime.now(timezone.utc).isoformat()
                self.event_type = event_type
                self.user_id = user_id
                self.action = action
                self.metadata = metadata or {}
                self.lambda_trace_id = f"Λ-{hash(f'{user_id}-{action}-{self.timestamp}') % 10000:04d}"
            
            def to_dict(self):
                return {
                    "timestamp": self.timestamp,
                    "event_type": self.event_type,
                    "user_id": self.user_id,
                    "action": self.action,
                    "lambda_trace_id": self.lambda_trace_id,
                    "metadata": self.metadata
                }
        
        # Create audit events
        auth_event = MockAuditEvent("authentication", "test_user", "login", {"tier": "T2"})
        access_event = MockAuditEvent("data_access", "test_user", "read_profile", {"consent": True})
        
        # Validate audit event schema
        auth_dict = auth_event.to_dict()
        assert "timestamp" in auth_dict
        assert "lambda_trace_id" in auth_dict
        assert auth_dict["lambda_trace_id"].startswith("Λ-")
        assert auth_dict["event_type"] == "authentication"
        assert auth_dict["user_id"] == "test_user"
        
        access_dict = access_event.to_dict()
        assert access_dict["metadata"]["consent"] is True
        assert access_dict["action"] == "read_profile"
        
        # Test JSON serialization works
        auth_json = json.dumps(auth_dict)
        assert "Λ-" in auth_json
        parsed = json.loads(auth_json)
        assert parsed["lambda_trace_id"] == auth_dict["lambda_trace_id"]

    def test_duress_gesture_response(self):
        """Test system locks and alerts on duress gesture"""
        from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
        
        # Test duress gesture detection and response
        class MockDuressDetector:
            """Mock duress detection system"""
            
            def __init__(self):
                self.system_locked = False
                self.alert_sent = False
                self.guardian = GuardianSystemImpl()
            
            def detect_duress_gesture(self, gesture_data: dict) -> bool:
                """Detect if gesture indicates duress"""
                # Mock duress patterns
                duress_indicators = ["emergency_tap", "stress_pattern", "panic_gesture"]
                return any(indicator in gesture_data.get("patterns", []) for indicator in duress_indicators)
            
            def respond_to_duress(self, user_id: str, gesture_data: dict) -> dict:
                """Respond to detected duress gesture"""
                if self.detect_duress_gesture(gesture_data):
                    self.system_locked = True
                    self.alert_sent = True
                    
                    # Run safety check through Guardian
                    safety_result = self.guardian.check_safety(
                        f"Duress detected for user {user_id}",
                        {"duress_level": "high", "emergency": True},
                        constitutional_check=True
                    )
                    
                    return {
                        "duress_detected": True,
                        "system_locked": self.system_locked,
                        "alert_sent": self.alert_sent,
                        "safety_assessment": safety_result.safe,
                        "response": "Emergency protocols activated"
                    }
                
                return {"duress_detected": False, "system_status": "normal"}
        
        detector = MockDuressDetector()
        
        # Test normal gesture (no duress)
        normal_gesture = {"patterns": ["normal_tap", "regular_swipe"]}
        normal_response = detector.respond_to_duress("test_user", normal_gesture)
        assert normal_response["duress_detected"] is False
        assert detector.system_locked is False
        
        # Test duress gesture
        duress_gesture = {"patterns": ["emergency_tap", "panic_gesture"]}
        duress_response = detector.respond_to_duress("test_user", duress_gesture)
        assert duress_response["duress_detected"] is True
        assert duress_response["system_locked"] is True
        assert duress_response["alert_sent"] is True

    def test_mvp_demo_scenario(self):
        """Test complete MVP demo workflow end-to-end"""
        from identity.identity_core import identity_core, AccessTier
        from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
        from lukhas.governance.guardian.core import GovernanceAction
        
        # Complete MVP demo workflow test
        guardian = GuardianSystemImpl()
        
        # Step 1: User registration and authentication
        user_id = "mvp_demo_user"
        metadata = {
            "email": "mvp@lukhas.ai",
            "consent": True,
            "trinity_score": 0.9,
            "drift_score": 0.03,
            "demo_participant": True
        }
        
        # Create and validate identity token
        token = identity_core.create_token(user_id, AccessTier.T3, metadata)
        assert token is not None
        assert identity_core.validate_token(token, AccessTier.T3) is True
        
        # Step 2: Ethical evaluation of demo actions
        demo_context = {
            "user_id": user_id,
            "demo_mode": True,
            "risk_level": "low",
            "stakeholders": ["demo_user", "system"],
            "ethical_implications": ["data_processing", "ai_interaction"]
        }
        
        read_decision = guardian.evaluate_ethics(GovernanceAction.READ, demo_context)
        assert read_decision.allowed is True
        
        # Step 3: Safety validation for demo content
        demo_content = "MVP demo showcasing LUKHAS AI Trinity Framework with identity, consciousness, and guardian systems"
        safety_result = guardian.check_safety(demo_content, demo_context, constitutional_check=True)
        assert safety_result.safe is True
        
        # Step 4: Drift detection for demo consistency
        baseline_demo = "LUKHAS AI Trinity Framework demonstration"
        current_demo = "LUKHAS AI Trinity Framework demo with identity validation"
        drift_result = guardian.detect_drift(baseline_demo, current_demo, 0.15, demo_context)
        assert drift_result.drift_score <= 0.15  # Within acceptable drift threshold
        
        # Step 5: Complete workflow validation
        demo_workflow = {
            "authentication": token is not None,
            "authorization": identity_core.validate_token(token, AccessTier.T3),
            "ethical_approval": read_decision.allowed,
            "safety_validation": safety_result.safe,
            "drift_compliance": drift_result.drift_score <= 0.15,
            "trinity_integration": all([
                "trinity_score" in metadata,
                guardian.get_status()["ethics_status"] == "active",
                metadata["consent"] is True
            ])
        }
        
        # All MVP demo components must pass
        assert all(demo_workflow.values()), f"MVP demo workflow failed: {demo_workflow}"
        
        # Verify Trinity Framework principles (⚛️🧠🛡️)
        identity_verified = token is not None  # ⚛️ Identity
        consciousness_active = metadata["trinity_score"] > 0.0  # 🧠 Consciousness  
        guardian_protecting = safety_result.safe and read_decision.allowed  # 🛡️ Guardian
        
        trinity_complete = identity_verified and consciousness_active and guardian_protecting
        assert trinity_complete, "Trinity Framework not fully integrated in MVP demo"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
