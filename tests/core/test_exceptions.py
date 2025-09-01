import pytest
from lukhas.core.common.exceptions import (
    LukhasError,
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

class TestLukhasError:
    def test_base_error_initialization(self):
        err = LukhasError("A base error occurred", error_code="BASE_ERROR", details={"key": "value"})
        assert err.message == "A base error occurred"
        assert err.error_code == "BASE_ERROR"
        assert err.details == {"key": "value"}

    def test_to_dict(self):
        err = LukhasError("Test message", "TEST_CODE", {"detail1": "value1"})
        err_dict = err.to_dict()
        assert err_dict["error"] == "TEST_CODE"
        assert err_dict["message"] == "Test message"
        assert err_dict["details"]["detail1"] == "value1"

class TestSpecificExceptions:
    def test_guardian_rejection_error(self):
        err = GuardianRejectionError("Operation rejected", ethics_violation="test_violation", suggestion="do_better")
        assert err.error_code == "GUARDIAN_REJECTION"
        assert err.details["ethics_violation"] == "test_violation"
        assert err.details["suggestion"] == "do_better"

    def test_memory_drift_error(self):
        err = MemoryDriftError("Drift detected", memory_id="mem1", drift_level=0.5, threshold=0.4)
        assert err.error_code == "MEMORY_DRIFT_EXCESSIVE"
        assert err.details["memory_id"] == "mem1"
        assert err.details["drift_level"] == 0.5
        assert pytest.approx(err.details["exceeded_by"]) == 0.1

    def test_module_timeout_error(self):
        err = ModuleTimeoutError("Timeout", module_name="test_mod", operation="test_op", timeout_seconds=10.0)
        assert err.error_code == "MODULE_TIMEOUT"
        assert err.details["module"] == "test_mod"
        assert err.details["operation"] == "test_op"

    def test_validation_error(self):
        err = ValidationError("Invalid input", field="username", value="user-123", constraint="alphanumeric")
        assert err.error_code == "VALIDATION_ERROR"
        assert err.details["field"] == "username"
        assert err.details["constraint"] == "alphanumeric"

class TestConvenienceFunctions:
    def test_raise_guardian_rejection(self):
        with pytest.raises(GuardianRejectionError) as excinfo:
            raise_guardian_rejection("Rejected", ethics_violation="test_eth_vio")
        assert excinfo.value.message == "Rejected"
        assert excinfo.value.details["ethics_violation"] == "test_eth_vio"

    def test_raise_if_drift_excessive_raises(self):
        with pytest.raises(MemoryDriftError):
            raise_if_drift_excessive("mem_id", 0.5, 0.4)

    def test_raise_if_drift_excessive_does_not_raise(self):
        try:
            raise_if_drift_excessive("mem_id", 0.3, 0.4)
        except MemoryDriftError:
            pytest.fail("MemoryDriftError raised unexpectedly")
