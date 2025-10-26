#!/usr/bin/env python3
"""Integration tests for auth_guardian_integration module."""
import pytest


class TestAuthGuardianIntegration:
    """Integration tests for AuthenticationGuardian."""

    def test_module_imports(self):
        """Test that the module can be imported successfully."""
        from core.governance.auth_guardian_integration import (
            AuthDriftMetrics,
            AuthenticationGuardian,
            AuthEventType,
            ConstitutionalAuthPrinciples,
        )

        assert AuthEventType is not None
        assert AuthDriftMetrics is not None
        assert ConstitutionalAuthPrinciples is not None
        assert AuthenticationGuardian is not None

    def test_auth_event_type_enum(self):
        """Test AuthEventType enum structure."""
        from enum import Enum

        from core.governance.auth_guardian_integration import AuthEventType

        assert issubclass(AuthEventType, Enum)

    def test_authentication_guardian_class(self):
        """Test AuthenticationGuardian can be instantiated."""
        from core.governance.auth_guardian_integration import AuthenticationGuardian

        guardian = AuthenticationGuardian()
        assert guardian is not None
