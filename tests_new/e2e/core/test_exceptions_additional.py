"""
Additional tests for core common exceptions to expand coverage.
Covers guardian rejections, memory drift, timeouts, configuration, 
authentication/authorization flows, validation, GLYPH tokens, and circuit breaker behavior.

Based on PR #124 - expanding coverage from 49% to 89%
"""

import pytest

from lukhas.core.common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CircuitBreakerError,
    ConfigurationError,
    GLYPHTokenError,
    GuardianRejectionError,
    MemoryDriftError,
    ModuleTimeoutError,
    ValidationError,
    raise_guardian_rejection,
    raise_if_drift_excessive,
)


class TestGuardianRejectionError:
    def test_guardian_rejection_basic(self):
        """Test basic guardian rejection error."""
        with pytest.raises(GuardianRejectionError):
            raise GuardianRejectionError("Policy violation detected")

    def test_raise_guardian_rejection_helper(self):
        """Test guardian rejection helper function."""
        with pytest.raises(GuardianRejectionError, match="Test rejection"):
            raise_guardian_rejection("Test rejection", suggestion="Try a different approach")

class TestMemoryDriftError:
    def test_memory_drift_basic(self):
        """Test basic memory drift error."""
        with pytest.raises(MemoryDriftError):
            raise MemoryDriftError(
                "Memory drift threshold exceeded", 
                memory_id="test_memory",
                drift_level=0.8,
                threshold=0.5
            )

    def test_raise_if_drift_excessive_helper(self):
        """Test drift checking helper function."""
        # Should not raise for acceptable drift
        raise_if_drift_excessive("test_memory", 0.1, threshold=0.2)

        # Should raise for excessive drift
        with pytest.raises(MemoryDriftError):
            raise_if_drift_excessive("test_memory", 0.3, threshold=0.2)

class TestModuleTimeoutError:
    def test_module_timeout(self):
        """Test module timeout error."""
        with pytest.raises(ModuleTimeoutError):
            raise ModuleTimeoutError("Module failed to respond within timeout")

class TestConfigurationError:
    def test_configuration_error(self):
        """Test configuration error."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Invalid configuration parameter")

class TestAuthenticationError:
    def test_authentication_error(self):
        """Test authentication error."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Authentication failed")

class TestAuthorizationError:
    def test_authorization_error(self):
        """Test authorization error."""
        with pytest.raises(AuthorizationError):
            raise AuthorizationError("Insufficient permissions")

class TestValidationError:
    def test_validation_error(self):
        """Test validation error."""
        with pytest.raises(ValidationError):
            raise ValidationError("Input validation failed")

class TestGLYPHTokenError:
    def test_glyph_token_error(self):
        """Test GLYPH token error."""
        with pytest.raises(GLYPHTokenError):
            raise GLYPHTokenError("Invalid GLYPH token format")

class TestCircuitBreakerError:
    def test_circuit_breaker_error(self):
        """Test circuit breaker error."""
        with pytest.raises(CircuitBreakerError):
            raise CircuitBreakerError(
                "Circuit breaker is open",
                service_name="test_service",
                failure_count=5,
                threshold=3,
                reset_timeout=30.0
            )
