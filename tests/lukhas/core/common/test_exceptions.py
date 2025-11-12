
import unittest
import os
import sys

# This is a hack to get the import to work.
sys.path.insert(0, os.path.abspath("./lukhas_website"))

from lukhas.core.common.exceptions import (
    LukhasError,
    GLYPHTokenError,
    GuardianRejectionError,
    MemoryDriftError,
    ModuleTimeoutError,
    ModuleNotFoundError,
    ConfigurationError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    GLYPHError,
    CircuitBreakerError,
    ResourceExhaustedError,
    raise_guardian_rejection,
    raise_if_drift_excessive,
)


class TestExceptions(unittest.TestCase):
    def test_lukhas_error_base(self):
        with self.assertRaises(LukhasError) as cm:
            raise LukhasError("Base error message")

        err = cm.exception
        self.assertEqual(err.message, "Base error message")
        self.assertEqual(err.error_code, "LukhasError")
        self.assertEqual(err.details, {})
        self.assertEqual(
            err.to_dict(),
            {
                "error": "LukhasError",
                "message": "Base error message",
                "details": {},
            },
        )

    def test_lukhas_error_with_details(self):
        details = {"key": "value"}
        with self.assertRaises(LukhasError) as cm:
            raise LukhasError("Error with details", error_code="CUSTOM_CODE", details=details)

        err = cm.exception
        self.assertEqual(err.error_code, "CUSTOM_CODE")
        self.assertEqual(err.details, details)

    def test_glyph_token_error(self):
        with self.assertRaises(GLYPHTokenError) as cm:
            raise GLYPHTokenError("Invalid token", token="abc-123")

        err = cm.exception
        self.assertEqual(err.error_code, "GLYPH_TOKEN_ERROR")
        self.assertEqual(err.details["token"], "abc-123")

    def test_guardian_rejection_error(self):
        with self.assertRaises(GuardianRejectionError) as cm:
            raise GuardianRejectionError(
                "Operation rejected",
                ethics_violation="Principle a.1",
                suggestion="Refactor logic",
            )

        err = cm.exception
        self.assertEqual(err.error_code, "GUARDIAN_REJECTION")
        self.assertEqual(err.details["ethics_violation"], "Principle a.1")
        self.assertEqual(err.details["suggestion"], "Refactor logic")

    def test_memory_drift_error(self):
        with self.assertRaises(MemoryDriftError) as cm:
            raise MemoryDriftError(
                "Drift too high",
                memory_id="mem-1",
                drift_level=0.5,
                threshold=0.3,
            )

        err = cm.exception
        self.assertEqual(err.error_code, "MEMORY_DRIFT_EXCESSIVE")
        self.assertEqual(err.details["memory_id"], "mem-1")
        self.assertAlmostEqual(err.details["exceeded_by"], 0.2)

    def test_module_timeout_error(self):
        with self.assertRaises(ModuleTimeoutError) as cm:
            raise ModuleTimeoutError(
                "Timeout",
                module_name="test_module",
                operation="process",
                timeout_seconds=30.5
            )

        err = cm.exception
        self.assertEqual(err.error_code, "MODULE_TIMEOUT")
        self.assertEqual(err.details["module"], "test_module")
        self.assertEqual(err.details["timeout_seconds"], 30.5)

    def test_module_not_found_error(self):
        with self.assertRaises(ModuleNotFoundError) as cm:
            raise ModuleNotFoundError("missing_module")

        err = cm.exception
        self.assertEqual(err.error_code, "MODULE_NOT_FOUND")
        self.assertEqual(err.details["module_name"], "missing_module")

    def test_configuration_error(self):
        with self.assertRaises(ConfigurationError) as cm:
            raise ConfigurationError(
                "Missing key",
                config_key="api.key",
                config_file="config.yaml"
            )

        err = cm.exception
        self.assertEqual(err.error_code, "CONFIGURATION_ERROR")
        self.assertEqual(err.details["config_key"], "api.key")
        self.assertEqual(err.details["config_file"], "config.yaml")

    def test_authentication_error(self):
        with self.assertRaises(AuthenticationError) as cm:
            raise AuthenticationError(auth_method="jwt")

        err = cm.exception
        self.assertEqual(err.error_code, "AUTHENTICATION_ERROR")
        self.assertEqual(err.details["auth_method"], "jwt")

    def test_authorization_error(self):
        with self.assertRaises(AuthorizationError) as cm:
            raise AuthorizationError(required_tier=3, current_tier=1)

        err = cm.exception
        self.assertEqual(err.error_code, "AUTHORIZATION_ERROR")
        self.assertEqual(err.details["required_tier"], 3)
        self.assertEqual(err.details["current_tier"], 1)

    def test_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            raise ValidationError("Invalid email", field="email", value="not-an-email")

        err = cm.exception
        self.assertEqual(err.error_code, "VALIDATION_ERROR")
        self.assertEqual(err.details["field"], "email")
        self.assertEqual(err.details["value"], "not-an-email")

    def test_circuit_breaker_error(self):
        with self.assertRaises(CircuitBreakerError) as cm:
            raise CircuitBreakerError(
                "Service unavailable",
                service_name="payment_service",
                failure_count=6,
                threshold=5,
                reset_timeout=60
            )

        err = cm.exception
        self.assertEqual(err.error_code, "CIRCUIT_BREAKER_OPEN")
        self.assertEqual(err.details["service_name"], "payment_service")
        self.assertEqual(err.details["failure_count"], 6)

    def test_resource_exhausted_error(self):
        with self.assertRaises(ResourceExhaustedError) as cm:
            raise ResourceExhaustedError(
                "CPU limit reached",
                resource_type="cpu",
                current_usage=95.5,
                limit=90.0
            )

        err = cm.exception
        self.assertEqual(err.error_code, "RESOURCE_EXHAUSTED")
        self.assertEqual(err.details["resource_type"], "cpu")
        self.assertGreater(err.details["usage_percentage"], 100)

    def test_raise_guardian_rejection_helper(self):
        with self.assertRaises(GuardianRejectionError) as cm:
            raise_guardian_rejection("Helper rejection", ethics_violation="test_violation")

        err = cm.exception
        self.assertEqual(err.details["ethics_violation"], "test_violation")

    def test_raise_if_drift_excessive_helper_raises(self):
        with self.assertRaises(MemoryDriftError):
            raise_if_drift_excessive("mem-2", 0.4, 0.3)

    def test_raise_if_drift_excessive_helper_does_not_raise(self):
        try:
            raise_if_drift_excessive("mem-3", 0.2, 0.3)
        except MemoryDriftError:
            self.fail("MemoryDriftError raised unexpectedly")


if __name__ == "__main__":
    unittest.main()
