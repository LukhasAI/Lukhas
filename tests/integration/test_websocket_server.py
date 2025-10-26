#!/usr/bin/env python3
"""
Integration tests for WebSocket Server
"""
import pytest


def test_websocket_server_import():
    """Test that websocket_server can be imported"""
    import core.governance.identity.auth_backend.websocket_server

    assert core.governance.identity.auth_backend.websocket_server is not None
