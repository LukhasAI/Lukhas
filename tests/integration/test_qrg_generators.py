#!/usr/bin/env python3
"""
Integration tests for QRG Generators
"""
import pytest


def test_qrg_generators_import():
    """Test that qrg_generators can be imported"""
    import core.governance.identity.auth.qrg_generators

    assert core.governance.identity.auth.qrg_generators is not None
