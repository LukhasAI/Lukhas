"""
Example unit test - fast, isolated, no I/O.
Unit tests should mirror the src/ structure: lukhas/ and candidate/
"""

import pytest


@pytest.mark.unit
def test_example_unit():
    """Example unit test."""
    assert True


# Example structure for lukhas module tests
class TestLukhasCore:
    """Unit tests for lukhas.core modules."""

    @pytest.mark.unit
    def test_core_functionality(self):
        """Test core functionality."""
        assert True


# Example structure for candidate module tests
class TestCandidateModules:
    """Unit tests for candidate modules."""

    @pytest.mark.unit
    def test_candidate_functionality(self):
        """Test candidate functionality."""
        assert True
