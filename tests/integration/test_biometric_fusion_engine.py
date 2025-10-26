#!/usr/bin/env python3
"""
Integration tests for Biometric Fusion Engine
"""
import pytest


def test_biometric_fusion_engine_import():
    """Test that biometric_fusion_engine can be imported"""
    from core.governance.identity.biometric.biometric_fusion_engine import BiometricModality, FallbackStrategy

    assert BiometricModality.FACIAL is not None
    assert FallbackStrategy.VOICE_PLUS_EMOJI is not None


def test_biometric_modalities():
    """Test biometric modalities are available"""
    from core.governance.identity.biometric.biometric_fusion_engine import BiometricModality

    assert hasattr(BiometricModality, 'FACIAL')
    assert hasattr(BiometricModality, 'VOICE')
    assert hasattr(BiometricModality, 'BEHAVIORAL')
