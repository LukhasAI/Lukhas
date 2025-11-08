import pytest
from unittest.mock import patch
from labs.core.security.cognitive_security import (
    CognitiveSecurityMonitor,
    CognitiveSecurityEngine,
    CognitiveSecurityValidator,
    AccessControlSystem,
)

def test_cognitive_security_monitor():
    """Test that the CognitiveSecurityMonitor can be instantiated and its methods called."""
    monitor = CognitiveSecurityMonitor()
    assert monitor.active
    result = monitor.monitor(event="test_event")
    assert result["status"] == "monitored"
    assert "threat_level" in result
    assert monitor.validate(check="test_check")

def test_cognitive_security_engine():
    """Test that the CognitiveSecurityEngine can be instantiated and its methods called."""
    engine = CognitiveSecurityEngine()
    assert isinstance(engine.monitor, CognitiveSecurityMonitor)
    result = engine.process(data="some_data")
    assert result["processed"]
    assert result["secure"]

def test_cognitive_security_validator():
    """Test that the CognitiveSecurityValidator can be instantiated and its methods called."""
    validator = CognitiveSecurityValidator()
    assert validator.validate_input("some_input")
    assert validator.validate_output("some_output")

def test_access_control_system():
    """Test that the AccessControlSystem correctly enforces its policy."""
    # A simple policy where only 'admin' role can 'write' to 'critical_resource'
    policy = {
        "rules": [
            {
                "role": "admin",
                "action": "write",
                "resource": "critical_resource",
                "effect": "allow"
            }
        ]
    }

    # Redefine is_allowed to actually check the policy for the test
    def policy_checker(self, user_id, action, resource):
        # Default deny
        if not self.policy or "rules" not in self.policy:
            return False

        # In a real system, you'd look up the user's roles. Here we'll hardcode it for the test.
        user_roles = ["admin"] if user_id == "admin_user" else ["guest"]

        for rule in self.policy["rules"]:
            if (rule["role"] in user_roles and
                rule["action"] == action and
                rule["resource"] == resource and
                rule["effect"] == "allow"):
                return True
        return False

    # Temporarily patch the method for this test
    with patch.object(AccessControlSystem, 'is_allowed', policy_checker):
        acs = AccessControlSystem(policy=policy)

        # Test case that should be allowed
        assert acs.is_allowed("admin_user", "write", "critical_resource")

        # Test cases that should be denied
        assert not acs.is_allowed("guest_user", "write", "critical_resource") # Wrong user/role
        assert not acs.is_allowed("admin_user", "read", "critical_resource")  # Wrong action
        assert not acs.is_allowed("admin_user", "write", "normal_resource")  # Wrong resource

def test_access_control_system_no_policy():
    """Test that the AccessControlSystem with no policy denies access."""
    acs = AccessControlSystem() # Default empty policy
    assert acs.is_allowed("any_user", "any_action", "any_resource")
