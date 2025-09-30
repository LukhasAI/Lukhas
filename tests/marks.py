"""Test markers for LUKHAS testing"""
import pytest

# Marker for tests that are quarantined due to known AuthZ issues
authz_quarantine = pytest.mark.authz_quarantine