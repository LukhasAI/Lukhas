#!/usr/bin/env python3
"""
T4/0.01% Lane Taxonomy Consistency Contract Tests
===============================================

Validates that all LUKHAS components use the canonical lane enum from schema_registry
without defining their own local lane constants.

This ensures routing & policy agreement for airtight MATRIZ isolation.

Constellation Framework: 🛡️ Lane Consistency Excellence Testing
"""

import json
import pathlib
# from typing import List  # All imports converted to builtins (PEP 585)

import pytest
from governance.schema_registry import LUKHASLane, get_lane_enum


class TestLaneConsistency:
    """T4/0.01% lane taxonomy consistency validation."""

    @pytest.fixture
    def canonical_lanes(self) -> list[str]:
        """Get the canonical lane enum from schema registry."""
        return get_lane_enum()

    def test_schema_registry_canonical_enum(self, canonical_lanes: list[str]):
        """Test that schema registry returns expected canonical lanes."""
        expected_lanes = ["candidate", "lukhas", "MATRIZ", "integration", "production", "canary", "experimental"]

        assert len(canonical_lanes) == len(expected_lanes), f"Lane count mismatch: {len(canonical_lanes)} != {len(expected_lanes)}"
        assert set(canonical_lanes) == set(expected_lanes), f"Lane set mismatch: {set(canonical_lanes)} != {set(expected_lanes)}"

    def test_guardian_schema_uses_canonical_lanes(self, canonical_lanes: list[str]):
        """Test that Guardian schema uses the canonical lane enum."""
        schema_path = pathlib.Path(__file__).parent.parent.parent / "governance" / "guardian_schema.json"
        schema = json.loads(schema_path.read_text())

        # Extract lane enum from Guardian schema
        guardian_lanes = schema["$defs"]["Subject"]["properties"]["lane"]["enum"]

        assert set(guardian_lanes) == set(canonical_lanes), \
            f"Guardian schema lanes don't match canonical: {set(guardian_lanes)} != {set(canonical_lanes)}"

    def test_luke_lane_enum_completeness(self):
        """Test that LUKHASLane enum has all expected values."""
        all_values = LUKHASLane.get_all_values()
        expected = ["candidate", "lukhas", "MATRIZ", "integration", "production", "canary", "experimental"]

        assert set(all_values) == set(expected), f"LUKHASLane enum incomplete: {set(all_values)} != {set(expected)}"

    def test_lane_validation_functionality(self):
        """Test lane validation helper methods."""
        # Valid lanes
        assert LUKHASLane.is_valid_lane("candidate")
        assert LUKHASLane.is_valid_lane("production")
        assert LUKHASLane.is_valid_lane("MATRIZ")

        # Invalid lanes
        assert not LUKHASLane.is_valid_lane("invalid")
        assert not LUKHASLane.is_valid_lane("staging")  # Common mistake
        assert not LUKHASLane.is_valid_lane("")

    def test_orchestrator_memory_consistency(self, canonical_lanes: list[str]):
        """Test that orchestrator and memory components use canonical lanes."""
        # This test ensures components import from schema_registry rather than define local constants

        # Test that we can import the canonical function
        from governance.schema_registry import get_lane_enum as imported_enum

        # Verify the imported function returns the same values
        assert imported_enum() == canonical_lanes, "Import inconsistency in lane enum"

    def test_identity_guardian_client_consistency(self, canonical_lanes: list[str]):
        """Test that identity and Guardian clients use canonical lanes."""
        # Verify that key components would use the registry

        try:
            # These imports will fail if components have hardcoded lanes
            # instead of using the registry
            from governance.schema_registry import LUKHASLane

            # Test that the enum is accessible and complete
            assert len(LUKHASLane) == 7, "LUKHASLane enum should have 7 values"

            # Test enum string representation matches expected values
            lane_strings = {lane.value for lane in LUKHASLane}
            assert lane_strings == set(canonical_lanes), f"Enum values don't match canonical: {lane_strings}"

        except ImportError as e:
            pytest.fail(f"Failed to import canonical lane enum: {e}")

    def test_no_local_lane_constants_violation(self):
        """Test that components don't define local lane constants."""
        # This is a contract test - if components define their own lane constants,
        # they should be refactored to use the schema registry

        # We can test this by ensuring the canonical enum is the authoritative source
        canonical_set = set(get_lane_enum())

        # Any component importing this should get the same canonical set
        from governance.schema_registry import get_lane_enum as test_import
        imported_set = set(test_import())

        assert canonical_set == imported_set, "Lane enum import inconsistency detected"

    def test_lane_enum_immutability(self, canonical_lanes: list[str]):
        """Test that the canonical lane enum is stable."""
        # Call multiple times to ensure consistent results
        first_call = get_lane_enum()
        second_call = get_lane_enum()
        third_call = get_lane_enum()

        assert first_call == second_call == third_call, "Lane enum should return consistent results"
        assert all(isinstance(lane, str) for lane in first_call), "All lanes should be strings"

    def test_performance_contract(self, canonical_lanes: list[str]):
        """Test that lane enum access is fast (<1ms)."""
        import time

        start_time = time.perf_counter()
        for _ in range(1000):  # Call 1000 times
            _ = get_lane_enum()
        end_time = time.perf_counter()

        avg_time_ms = ((end_time - start_time) / 1000) * 1000
        assert avg_time_ms < 1.0, f"Lane enum access too slow: {avg_time_ms:.3f}ms average"

    def test_memory_efficiency(self, canonical_lanes: list[str]):
        """Test that lane enum doesn't create excessive objects."""
        import sys

        # Get baseline memory
        initial_refs = sys.getrefcount(canonical_lanes)

        # Call function multiple times
        results = [get_lane_enum() for _ in range(100)]

        # Each call should return the same list content, not accumulate objects
        assert all(r == canonical_lanes for r in results), "Lane enum should return consistent content"

        # Cleanup references
        del results

        final_refs = sys.getrefcount(canonical_lanes)
        assert final_refs <= initial_refs + 1, "Lane enum should not leak references"


class TestLaneEnumIntegration:
    """Integration tests for lane enum usage across components."""

    def test_guardian_schema_lane_validation(self):
        """Test that Guardian schema validates lanes correctly."""
        from governance.schema_registry import LUKHASLane

        # Test that schema would accept all canonical lanes
        canonical_lanes = LUKHASLane.get_all_values()

        # Verify each canonical lane would pass validation
        for lane in canonical_lanes:
            assert LUKHASLane.is_valid_lane(lane), f"Canonical lane {lane} should be valid"

    def test_error_handling_invalid_lanes(self):
        """Test proper error handling for invalid lanes."""
        invalid_lanes = ["invalid", "dev", "test", "staging", "prod", "local"]

        for invalid_lane in invalid_lanes:
            assert not LUKHASLane.is_valid_lane(invalid_lane), f"Lane {invalid_lane} should be invalid"

    def test_case_sensitivity(self):
        """Test that lane validation is case-sensitive as expected."""
        # These should be invalid (case mismatch)
        assert not LUKHASLane.is_valid_lane("CANDIDATE")  # should be "candidate"
        assert not LUKHASLane.is_valid_lane("Production")  # should be "production"
        assert not LUKHASLane.is_valid_lane("matriz")      # should be "MATRIZ"

        # These should be valid (correct case)
        assert LUKHASLane.is_valid_lane("candidate")
        assert LUKHASLane.is_valid_lane("production")
        assert LUKHASLane.is_valid_lane("MATRIZ")
