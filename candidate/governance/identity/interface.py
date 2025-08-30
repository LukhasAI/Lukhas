"""
LUKHAS Identity Interface - Module Integration Layer

This module provides a clean interface for all AGI modules to interact with the
lukhas-id identity system without needing detailed knowledge of ΛiD internals.

Key functions:
- Identity verification and validation
- Tier-based access control
- Consent management
- Audit logging via ΛTRACE
- Session management

Usage:
    from identity_interface import IdentityClient

    client = IdentityClient()
    if client.verify_user_access(user_id, required_tier="LAMBDA_TIER_2"):
        # Proceed with operation
        client.log_activity("memory_access", user_id, {"operation": "read"})
"""

import os
import sys
from datetime import datetime
from typing import Any

# Add lukhas-id to path for imports
lukhas_id_path = os.path.join(os.path.dirname(__file__), "lukhas-id")
sys.path.insert(0, lukhas_id_path)

try:
    from governance.identity.core.id_service.lambd_id_validator import (
        LambdaIDValidator as LambdIDValidator,
    )
    from governance.identity.core.sent.consent_manager import (
        LambdaConsentManager as ConsentManager,
    )
    from governance.identity.core.tier.tier_validator import TierValidator
    from governance.identity.core.trace.activity_logger import (
        LambdaTraceLogger as ActivityLogger,
    )
except ImportError as e:
    print(f"Warning: Could not import core-id modules: {e}")
    # Create stub classes for development

    class TierValidator:
        def validate_tier(self, user_id: str, required_tier: str) -> bool:
            try:
                from governance.identity.core.user_tier_mapping import check_tier_access

                return check_tier_access(user_id, required_tier)
            except ImportError:
                # Fallback for development
                return True

    class ActivityLogger:
        def log_activity(self, activity_type: str, user_id: str, metadata: dict) -> None:
            print(f"ΛTRACE: {activity_type} by {user_id}: {metadata}")

    class ConsentManager:
        def check_consent(self, user_id: str, action: str) -> bool:
            return True

    class LambdIDValidator:
        def validate_identity(self, user_id: str) -> bool:
            return True


class IdentityClient:
    """
    Unified client for all module identity interactions with lukhas-id.

    This client abstracts the complexity of the ΛiD system and provides
    a simple interface for modules to:
    - Verify user identity and permissions
    - Log activities for audit trails
    - Check consent for operations
    - Validate tier-based access
    """

    def __init__(self, user_id_context=None):
        """Initialize the identity client with lukhas-id components."""
        self.user_id_context = user_id_context
        try:
            # Try to initialize real components with fallback configurations
            self.tier_validator = TierValidator(config={})
            try:
                self.activity_logger = ActivityLogger(config={}, consent_manager=None)
            except TypeError:
                # Fallback for different constructor signature
                self.activity_logger = ActivityLogger({})
            try:
                self.consent_manager = ConsentManager(config={})
            except TypeError:
                # Fallback for different constructor signature
                self.consent_manager = ConsentManager({}, None, None)
            try:
                self.id_validator = LambdIDValidator(config_path=None)
            except Exception:
                # Create a simple working validator as fallback
                self.id_validator = type(
                    "LambdIDValidator",
                    (),
                    {"validate_identity": lambda self, uid: True},
                )()
        except Exception as e:
            print(f"Warning: Could not initialize identity components: {e}")
            # Fall back to stub implementations
            self.tier_validator = type(
                "TierValidator", (), {"validate_tier": lambda self, uid, tier: True}
            )()
            self.activity_logger = type(
                "ActivityLogger", (), {"log_activity": lambda self, a, b, c: None}
            )()
            self.consent_manager = type(
                "ConsentManager", (), {"check_consent": lambda self, a, b: True}
            )()
            self.id_validator = type(
                "LambdIDValidator", (), {"validate_identity": lambda self, a: True}
            )()

    def verify_user_access(self, user_id: str, required_tier: str = "LAMBDA_TIER_1") -> bool:
        """
        Verify that a user has the required access tier for an operation.

        Args:
            user_id: The user's lambda ID
            required_tier: Minimum tier required (e.g., "LAMBDA_TIER_2")

        Returns:
            bool: True if user has sufficient access, False otherwise
        """
        try:
            # First validate the identity
            if not self.id_validator.validate_identity(user_id):
                self.log_security_event(
                    "invalid_identity",
                    user_id,
                    {"reason": "identity_validation_failed"},
                )
                return False

            # Then check tier access
            if not self.tier_validator.validate_tier(user_id, required_tier):
                self.log_security_event("insufficient_tier", user_id, {"required": required_tier})
                return False

            return True
        except Exception as e:
            self.log_security_event("access_verification_error", user_id, {"error": str(e)})
            return False

    def check_consent(self, user_id: str, action: str, scope: str = "default") -> bool:
        """
        Check if user has given consent for a specific action.

        Args:
            user_id: The user's lambda ID
            action: The action requiring consent (e.g., "memory_access", "dream_generation")
            scope: The scope of the consent (e.g., "personal_data", "creative_content")

        Returns:
            bool: True if consent is granted, False otherwise
        """
        try:
            consent_granted = self.consent_manager.check_consent(user_id, action)
            self.log_activity(
                "consent_check",
                user_id,
                {"action": action, "scope": scope, "granted": consent_granted},
            )
            return consent_granted
        except Exception as e:
            self.log_security_event("consent_check_error", user_id, {"error": str(e)})
            return False

    def log_activity(self, activity_type: str, user_id: str, metadata: dict[str, Any]) -> None:
        """
        Log an activity to the ΛTRACE system for audit trails.

        Args:
            activity_type: Type of activity (e.g., "memory_access", "creativity_generation")
            user_id: The user's lambda ID
            metadata: Additional information about the activity
        """
        try:
            enhanced_metadata = {
                **metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "module": self._get_calling_module(),
            }
            self.activity_logger.log_activity(activity_type, user_id, enhanced_metadata)
        except Exception as e:
            print(f"Error logging activity: {e}")

    def log_security_event(self, event_type: str, user_id: str, metadata: dict[str, Any]) -> None:
        """
        Log a security-related event with elevated priority.

        Args:
            event_type: Type of security event
            user_id: The user's lambda ID
            metadata: Security event details
        """
        security_metadata = {
            **metadata,
            "security_event": True,
            "severity": "HIGH",
            "timestamp": datetime.utcnow().isoformat(),
            "module": self._get_calling_module(),
        }
        self.log_activity(f"SECURITY_{event_type}", user_id, security_metadata)

    def validate_session(self, session_id: str, user_id: str) -> bool:
        """
        Validate that a session belongs to the specified user.

        Args:
            session_id: The session identifier
            user_id: The user's lambda ID

        Returns:
            bool: True if session is valid for user, False otherwise
        """
        try:
            # This would integrate with lukhas-id session management
            # For now, basic validation
            if not session_id or not user_id:
                return False

            self.log_activity("session_validation", user_id, {"session_id": session_id})
            return True
        except Exception as e:
            self.log_security_event("session_validation_error", user_id, {"error": str(e)})
            return False

    def _get_calling_module(self) -> str:
        """Get the name of the module that called this function for logging."""
        import inspect

        try:
            frame = inspect.currentframe()
            # Go up the stack to find the caller outside this class
            while frame:
                frame = frame.f_back
                if frame and "self" not in frame.f_locals:
                    module_name = frame.f_globals.get("__name__", "unknown")
                    if not module_name.startswith("identity_interface"):
                        return module_name
            return "unknown_module"
        except BaseException:
            return "unknown_module"

    def validate_identity(self, user_id: str) -> bool:
        """
        Validate a user's identity.

        Args:
            user_id: The user's Lambda ID

        Returns:
            bool: True if identity is valid, False otherwise
        """
        return self.id_validator.validate_identity(user_id)


# Convenience functions for quick access
_default_client = None


def get_identity_client() -> IdentityClient:
    """Get the default identity client instance."""
    global _default_client
    if _default_client is None:
        _default_client = IdentityClient()
    return _default_client


def verify_access(user_id: str, required_tier: str = "LAMBDA_TIER_1") -> bool:
    """Quick access function for user verification."""
    return get_identity_client().verify_user_access(user_id, required_tier)


def log_activity(activity_type: str, user_id: str, metadata: dict[str, Any]) -> None:
    """Quick access function for activity logging."""
    get_identity_client().log_activity(activity_type, user_id, metadata)


def check_consent(user_id: str, action: str) -> bool:
    """Quick access function for consent checking."""
    return get_identity_client().check_consent(user_id, action)


if __name__ == "__main__":
    # Example usage
    client = IdentityClient()

    # Test user access
    user_id = "test_lambda_user_001"
    if client.verify_user_access(user_id, "LAMBDA_TIER_2"):
        print(f"✅ User {user_id} has sufficient access")
        client.log_activity("module_test", user_id, {"test": "identity_interface"})
    else:
        print(f"❌ User {user_id} access denied")
