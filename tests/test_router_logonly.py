"""
Test router log-only mode - ensures no dispatch when DISPATCH_ENABLED=false
"""
import os
from unittest.mock import Mock

import pytest

from matriz.adapters.bio_adapter import BioAdapter
from matriz.router import SymbolicMeshRouter
from tests.util.mk_msg import mk_test_message


def test_router_logonly_no_dispatch():
    """Verify router doesn't call node.handle() when in log-only mode"""
    # Ensure dispatch is disabled (default)
    os.environ.pop('DISPATCH_ENABLED', None)

    # Create mock logger
    log_calls = []
    def mock_logger(event, data):
        log_calls.append({"event": event, "data": data})

    # Create router
    router = SymbolicMeshRouter(log_fn=mock_logger)

    # Create mock adapter to track handle calls
    mock_adapter = Mock(spec=BioAdapter)
    mock_adapter.name = "mock-bio-adapter"

    # Register adapter
    router.register("homeostasis", mock_adapter)

    # Verify registration was logged
    assert len(log_calls) == 1
    assert log_calls[0]["event"] == "router.register"
    assert log_calls[0]["data"]["topic"] == "homeostasis"
    assert log_calls[0]["data"]["node"] == "mock-bio-adapter"

    # Create test message
    msg = mk_test_message(topic="homeostasis", payload={"delta": 5})

    # Publish message
    router.publish(msg)

    # Verify publish was logged
    assert len(log_calls) == 2
    assert log_calls[1]["event"] == "router.publish"
    assert log_calls[1]["data"]["topic"] == "homeostasis"
    assert log_calls[1]["data"]["lane"] == "experimental"

    # Verify adapter handle was NOT called (log-only mode)
    mock_adapter.handle.assert_not_called()


def test_router_start_logging():
    """Verify router.start() emits log"""
    log_calls = []
    def mock_logger(event, data):
        log_calls.append({"event": event, "data": data})

    router = SymbolicMeshRouter(log_fn=mock_logger)
    router.start()

    assert len(log_calls) == 1
    assert log_calls[0]["event"] == "router.start"


@pytest.mark.prod_only
def test_router_dispatch_when_enabled():
    """Test that dispatch works when DISPATCH_ENABLED=true (prod only)"""
    # This test would only run in candidate/prod lanes
    # For now, just verify the infrastructure exists
    os.environ['DISPATCH_ENABLED'] = 'true'

    log_calls = []
    def mock_logger(event, data):
        log_calls.append({"event": event, "data": data})

    router = SymbolicMeshRouter(log_fn=mock_logger)

    # Note: Actual dispatch implementation would be added later
    # For Phase 1, we verify log-only mode works correctly
    assert router.log == mock_logger
    assert hasattr(router, 'nodes')
    assert hasattr(router, 'publish')

    # Cleanup
    os.environ.pop('DISPATCH_ENABLED', None)
