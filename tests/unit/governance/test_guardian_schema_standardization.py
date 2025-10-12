"""
T4/0.01% Excellence Tests: Guardian Response Schema Standardization
================================================================

Comprehensive test suite for Guardian response schema compliance,
including unit tests, property tests, and contract validation.
"""

import json
import os
import sys
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from governance.guardian_system import GuardianSystem


class TestGuardianResponseSchema:
    """Test Guardian response schema standardization and compliance"""

    def setup_method(self):
        """Setup test environment"""
        self.guardian = GuardianSystem()

    def test_schema_version_consistency(self):
        """Ensure all responses include schema_version field"""
        # Test emergency response
        with patch.object(Path, 'exists', return_value=True):
            response = self.guardian.validate_safety({"test": "data"})
            assert "schema_version" in response
            assert response["schema_version"] == "1.0.0"

        # Test disabled response
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
            response = self.guardian.validate_safety({"test": "data"})
            assert "schema_version" in response
            assert response["schema_version"] == "1.0.0"

        # Test normal response
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            response = self.guardian.validate_safety({"test": "data"})
            assert "schema_version" in response
            assert response["schema_version"] == "1.0.0"

    def test_all_responses_have_required_fields(self):
        """Verify all response types contain mandatory fields"""
        required_fields = {
            "safe", "drift_score", "guardian_status", "emergency_active",
            "enforcement_enabled", "schema_version", "timestamp", "correlation_id"
        }

        # Test all three response scenarios
        scenarios = [
            # Emergency scenario
            ({"test": "data"}, True, {}),
            # Disabled scenario
            ({"test": "data"}, False, {"ENFORCE_ETHICS_DSL": "0"}),
            # Normal scenario
            ({"test": "data"}, False, {"ENFORCE_ETHICS_DSL": "1"})
        ]

        for operation, emergency_exists, env_vars in scenarios:
            with patch.object(Path, 'exists', return_value=emergency_exists):
                with patch.dict(os.environ, env_vars, clear=False):
                    response = self.guardian.validate_safety(operation)

                    # Check all required fields present
                    for field in required_fields:
                        assert field in response, f"Missing {field} in {response}"

    def test_emergency_active_field_accuracy(self):
        """Test emergency_active field accurately reflects emergency file status"""
        # Emergency file exists
        with patch.object(Path, 'exists', return_value=True):
            response = self.guardian.validate_safety({"test": "data"})
            assert response["emergency_active"] is True

        # Emergency file does not exist
        with patch.object(Path, 'exists', return_value=False):
            response = self.guardian.validate_safety({"test": "data"})
            assert response["emergency_active"] is False

    def test_enforcement_enabled_field_accuracy(self):
        """Test enforcement_enabled field accurately reflects DSL setting"""
        # Enforcement enabled (default)
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            response = self.guardian.validate_safety({"test": "data"})
            assert response["enforcement_enabled"] is True

        # Enforcement disabled
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
            response = self.guardian.validate_safety({"test": "data"})
            assert response["enforcement_enabled"] is False

        # Enforcement enabled (unset defaults to enabled)
        with patch.dict(os.environ, {}, clear=True):
            response = self.guardian.validate_safety({"test": "data"})
            assert response["enforcement_enabled"] is True

    def test_timestamp_field_validity(self):
        """Test timestamp field contains valid Unix timestamp"""
        start_time = time.time()
        response = self.guardian.validate_safety({"test": "data"})
        end_time = time.time()

        assert "timestamp" in response
        assert isinstance(response["timestamp"], float)
        assert start_time <= response["timestamp"] <= end_time

    def test_correlation_id_uniqueness(self):
        """Test correlation_id is unique across requests"""
        responses = []
        for _ in range(10):
            response = self.guardian.validate_safety({"test": "data"})
            responses.append(response["correlation_id"])

        # All correlation IDs should be unique
        assert len(set(responses)) == len(responses)

        # All should be valid UUIDs
        for correlation_id in responses:
            uuid.UUID(correlation_id)  # Raises ValueError if invalid

    def test_reason_field_optional(self):
        """Test reason field is only present when provided"""
        # Emergency response should have reason
        with patch.object(Path, 'exists', return_value=True):
            response = self.guardian.validate_safety({"test": "data"})
            assert "reason" in response
            assert response["reason"] == "Emergency kill-switch activated"

        # Normal response should not have reason
        with patch.object(Path, 'exists', return_value=False):
            response = self.guardian.validate_safety({"test": "data"})
            assert "reason" not in response

    def test_response_json_serializable(self):
        """Ensure all responses are JSON serializable for API compatibility"""
        scenarios = [
            (True, {}),  # Emergency
            (False, {"ENFORCE_ETHICS_DSL": "0"}),  # Disabled
            (False, {"ENFORCE_ETHICS_DSL": "1"})   # Normal
        ]

        for emergency_exists, env_vars in scenarios:
            with patch.object(Path, 'exists', return_value=emergency_exists):
                with patch.dict(os.environ, env_vars, clear=False):
                    response = self.guardian.validate_safety({"test": "data"})

                    # Should be JSON serializable
                    json_str = json.dumps(response)
                    parsed = json.loads(json_str)
                    assert parsed == response

    @pytest.mark.performance
    def test_response_performance(self):
        """Test response generation performance meets <100ms requirement"""
        start_time = time.time()
        for _ in range(100):
            self.guardian.validate_safety({"test": "data"})
        end_time = time.time()

        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.1, f"Average response time {avg_time:.3f}s exceeds 100ms limit"

    @pytest.mark.property
    def test_schema_invariants(self):
        """Property-based tests for schema invariants"""
        from hypothesis import given, strategies as st

        @given(st.dictionaries(st.text(), st.text()))
        def check_schema_invariants(operation_data):
            response = self.guardian.validate_safety(operation_data)

            # Schema invariants that must always hold
            assert isinstance(response, dict)
            assert isinstance(response["safe"], bool)
            assert isinstance(response["drift_score"], (int, float))
            assert isinstance(response["guardian_status"], str)
            assert isinstance(response["emergency_active"], bool)
            assert isinstance(response["enforcement_enabled"], bool)
            assert isinstance(response["schema_version"], str)
            assert isinstance(response["timestamp"], (int, float))
            assert isinstance(response["correlation_id"], str)

            # Value constraints
            assert 0.0 <= response["drift_score"] <= 1.0
            assert response["guardian_status"] in ["active", "disabled", "emergency_disabled"]
            assert response["schema_version"] == "1.0.0"

        check_schema_invariants()

    @pytest.mark.contract
    def test_downstream_consumer_contracts(self):
        """Test response contracts expected by downstream consumers"""
        response = self.guardian.validate_safety({"test": "data"})

        # Memory module contract
        assert "drift_score" in response
        assert isinstance(response["drift_score"], (int, float))

        # Consciousness module contract
        assert "safe" in response
        assert "guardian_status" in response

        # Identity module contract
        assert "enforcement_enabled" in response
        assert "emergency_active" in response

        # API gateway contract
        assert "correlation_id" in response
        assert "timestamp" in response
        assert "schema_version" in response


@pytest.mark.integration
class TestGuardianSchemaIntegration:
    """Integration tests for Guardian schema with other modules"""

    def test_guardian_memory_integration(self):
        """Test Guardian response integrates properly with Memory module"""
        guardian = GuardianSystem()
        response = guardian.validate_safety({"test": "data"})

        # Memory module should be able to process drift_score
        assert "drift_score" in response
        drift_score = response["drift_score"]
        assert isinstance(drift_score, (int, float))
        assert 0.0 <= drift_score <= 1.0

    def test_guardian_api_response_format(self):
        """Test Guardian response format suitable for API responses"""
        guardian = GuardianSystem()
        response = guardian.validate_safety({"test": "data"})

        # Should have HTTP-friendly structure
        assert isinstance(response, dict)
        assert all(isinstance(k, str) for k in response.keys())

        # Should be serializable for HTTP responses
        import json
        json.dumps(response)  # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
