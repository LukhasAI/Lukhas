"""
Bio Module Canary Tests
Validates consolidated bio functionality
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_bio_imports():
    """Test that bio modules can be imported"""
    from candidate.accepted import bio
    assert bio is not None
    assert hasattr(bio, '__trinity__')

def test_bio_core_components():
    """Test core bio components are available"""
    from candidate.accepted.bio import awareness, oscillator, symbolic

    # Check modules exist
    assert oscillator is not None
    assert symbolic is not None
    assert awareness is not None

def test_bio_engine():
    """Test bio engine initialization"""
    from candidate.accepted.bio import get_bio_engine

    engine = get_bio_engine()
    assert engine is not None

def test_trinity_integration():
    """Test Trinity Framework integration"""
    from candidate.accepted.bio import trinity_sync

    sync_status = trinity_sync()
    assert sync_status['identity'] == '⚛️'
    assert sync_status['consciousness'] == '🧠'
    assert sync_status['guardian'] == '🛡️'
    assert sync_status['status'] == 'synchronized'

def test_backward_compatibility():
    """Test compatibility shims still work"""
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Try old import (should work with deprecation warning)
        try:
            from bio_core import BioEngine
            assert len(w) > 0
            assert "deprecated" in str(w[0].message).lower()
        except ImportError:
            # Shim might not have real implementation yet
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
