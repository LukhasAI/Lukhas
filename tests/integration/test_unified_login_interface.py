#!/usr/bin/env python3
"""
Integration tests for Unified Login Interface
"""
import pytest


def test_unified_login_interface_import():
    """Test that unified_login_interface can be imported"""
    import core.governance.identity.unified_login_interface

    assert core.governance.identity.unified_login_interface is not None
