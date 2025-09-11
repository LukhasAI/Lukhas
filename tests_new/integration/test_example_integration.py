"""
Example integration test - tests I/O, databases, APIs, file systems.
"""

import pytest


@pytest.mark.integration
def test_example_integration():
    """Example integration test."""
    assert True


@pytest.mark.integration
class TestDatabaseIntegration:
    """Database integration tests."""

    def test_db_connection(self):
        """Test database connectivity."""
        assert True


@pytest.mark.integration
class TestAPIIntegration:
    """API integration tests."""

    def test_external_api_calls(self):
        """Test external API integrations."""
        assert True
