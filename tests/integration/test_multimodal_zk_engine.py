#!/usr/bin/env python3
"""
Integration tests for MultiModal ZK Engine
"""
import pytest


def test_multimodal_zk_engine_import():
    """Test that multimodal_zk_engine can be imported"""
    from core.governance.identity.zkproof.multimodal_zk_engine import ZKCircuitType, BiometricCommitment

    assert ZKCircuitType.BIOMETRIC_OWNERSHIP is not None
    assert BiometricCommitment is not None


def test_zk_circuit_types():
    """Test ZK circuit types are available"""
    from core.governance.identity.zkproof.multimodal_zk_engine import ZKCircuitType

    assert hasattr(ZKCircuitType, 'BIOMETRIC_OWNERSHIP')
    assert hasattr(ZKCircuitType, 'CONSCIOUSNESS_PROOF')
    assert hasattr(ZKCircuitType, 'CULTURAL_KNOWLEDGE')
