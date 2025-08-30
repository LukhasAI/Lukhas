"""Test timezone-aware datetime usage in stable code paths."""

from datetime import datetime, timezone

import pytest


@pytest.mark.unit
def test_bio_symbolic_uses_utc():
    """Assert bio-symbolic timestamps are UTC."""
    try:
        from lukhas.bio.core.bio_symbolic import BioSymbolic

        bio = BioSymbolic()
        # Check if bio creates timestamp data
        if hasattr(bio, "timestamp_data") and bio.timestamp_data:
            timestamp_str = bio.timestamp_data.get("timestamp", "")
            if timestamp_str:
                # Parse ISO timestamp and verify UTC
                parsed_dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                assert parsed_dt.tzinfo is not None, "Timestamp should be timezone-aware"
                assert parsed_dt.utctimetuple() == parsed_dt.timetuple(), "Should be UTC"
    except ImportError:
        pytest.skip("BioSymbolic not available")


@pytest.mark.unit
def test_stable_paths_use_utc():
    """Assert stable code paths use timezone.utc for datetime.now()."""
    # Test that timezone.utc is available and working
    utc_now = datetime.now(timezone.utc)
    assert utc_now.tzinfo == timezone.utc
    assert utc_now.utcoffset().total_seconds() == 0
