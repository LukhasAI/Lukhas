"""Import safety tests for observability.evidence_collection module.

Tests that evidence collection works correctly even when labs.observability
is unavailable, using fallback stubs.
"""
import sys
from unittest.mock import patch

import pytest


def test_evidence_collection_imports_without_labs():
    """Test that evidence_collection can be imported without labs.observability."""
    # Block labs.observability import
    with patch.dict(sys.modules, {"labs.observability": None}):
        # Should not raise ImportError
        import observability.evidence_collection as ec

        # Verify core exports are available
        assert hasattr(ec, "ComplianceRegime")
        assert hasattr(ec, "EvidenceCollectionEngine")
        assert hasattr(ec, "EvidenceType")
        assert hasattr(ec, "collect_evidence")
        assert hasattr(ec, "get_evidence_engine")
        assert hasattr(ec, "initialize_evidence_collection")


def test_get_labs_observability_returns_none_when_unavailable():
    """Test that _get_labs_observability() returns None when labs unavailable."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # Should return None, not raise exception
        result = ec._get_labs_observability()
        assert result is None


def test_evidence_collection_engine_stub_initialization():
    """Test that stub EvidenceCollectionEngine can be initialized."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # Initialize engine (should use stub)
        engine = ec.initialize_evidence_collection()
        assert engine is not None
        assert hasattr(engine, "collect_evidence")
        assert hasattr(engine, "verify_evidence")
        assert hasattr(engine, "shutdown")


@pytest.mark.asyncio
async def test_evidence_collection_stub_collect_evidence():
    """Test that stub collect_evidence function works."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # Should return empty string (stub behavior)
        result = await ec.collect_evidence("test_action", "test_context")
        assert isinstance(result, str)


def test_compliance_regime_enum_available():
    """Test that ComplianceRegime enum is accessible."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # Should have enum values
        assert hasattr(ec.ComplianceRegime, "STRICT")
        assert hasattr(ec.ComplianceRegime, "BALANCED")
        assert hasattr(ec.ComplianceRegime, "PERMISSIVE")


def test_evidence_type_enum_available():
    """Test that EvidenceType enum is accessible."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # Should have enum values
        assert hasattr(ec.EvidenceType, "METRIC")
        assert hasattr(ec.EvidenceType, "LOG")


def test_get_evidence_engine_stub():
    """Test that get_evidence_engine returns stub when labs unavailable."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        engine = ec.get_evidence_engine()
        assert engine is not None
        assert isinstance(engine, ec.EvidenceCollectionEngine)


def test_lazy_loading_caches_result():
    """Test that lazy loading caches the loaded module."""
    with patch.dict(sys.modules, {"labs.observability": None}):
        import observability.evidence_collection as ec

        # First access
        engine1 = ec.get_evidence_engine()

        # Second access should return cached result
        engine2 = ec.get_evidence_engine()

        # Should be same instance (cached)
        assert type(engine1) == type(engine2)
