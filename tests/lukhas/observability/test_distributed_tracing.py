"""
Unit tests for distributed_tracing.py using pytest and mocker.
"""
import asyncio
import sys
from unittest.mock import MagicMock

import pytest

# Mock away the entire opentelemetry library at the sys.modules level.
# This ensures that our module's is_otel_available() will return False by default.
mock_otel = MagicMock()
mock_otel.trace.StatusCode.OK = "OK"
mock_otel.trace.StatusCode.ERROR = "ERROR"

# We must mock the submodules as well, as they are imported directly.
sys.modules['opentelemetry'] = mock_otel
sys.modules['opentelemetry.trace'] = mock_otel.trace
sys.modules['opentelemetry.propagate'] = mock_otel.propagate
sys.modules['opentelemetry.context'] = mock_otel.context


@pytest.fixture(autouse=True)
def cleanup_imports():
    """Ensure a clean slate for imports between tests."""
    yield
    # It's good practice to clean up sys.modules modifications if they affect other tests.
    # In this case, we want the mock to persist across all tests in this file.
    pass


@pytest.fixture
def mock_tracer(mocker):
    """Fixture to provide a mocked tracer."""
    tracer = MagicMock()
    span = MagicMock()
    span.__enter__.return_value = span
    tracer.start_as_current_span.return_value = span
    mocker.patch('lukhas.observability.distributed_tracing.get_tracer', return_value=tracer)
    return tracer, span


@pytest.mark.asyncio
async def test_trace_node_process_decorator_success(mocker, mock_tracer):
    """Verify the decorator traces a successful node execution."""
    mocker.patch('lukhas.observability.distributed_tracing.is_otel_available', return_value=True)

    # We need to re-import the module to pick up the patched is_otel_available
    from lukhas.observability import distributed_tracing
    distributed_tracing.trace.get_tracer.return_value = mock_tracer[0]


    class MockNode:
        name = "test_node"
        @distributed_tracing.trace_node_process
        async def process(self, ctx):
            return {"status": "ok"}

    node = MockNode()
    ctx = {"query": "test", "_trace_context": {}}
    result = await node.process(ctx)

    assert result["status"] == "ok"
    tracer, span = mock_tracer
    tracer.start_as_current_span.assert_called_once()
    span.set_attribute.assert_any_call("matriz.node.name", "test_node")
    span.set_status.assert_called_once_with("OK")
    assert "_trace_context" in result
    mock_otel.propagate.inject.assert_called_once()


@pytest.mark.asyncio
async def test_trace_node_process_decorator_failure(mocker, mock_tracer):
    """Verify the decorator traces a failed node execution."""
    mocker.patch('lukhas.observability.distributed_tracing.is_otel_available', return_value=True)

    from lukhas.observability import distributed_tracing
    distributed_tracing.trace.get_tracer.return_value = mock_tracer[0]

    class MockNode:
        name = "failing_node"
        @distributed_tracing.trace_node_process
        async def process(self, ctx):
            raise ValueError("test error")

    node = MockNode()
    ctx = {"query": "fail"}
    with pytest.raises(ValueError):
        await node.process(ctx)

    tracer, span = mock_tracer
    tracer.start_as_current_span.assert_called_once()
    span.set_status.assert_called_once_with("ERROR", description="test error")
    span.record_exception.assert_called_once()


def test_extract_context(mocker):
    """Verify context extraction is called when OTel is available."""
    mocker.patch('lukhas.observability.distributed_tracing.is_otel_available', return_value=True)
    from lukhas.observability import distributed_tracing

    carrier = {"traceparent": "00-test-trace-id-00"}
    distributed_tracing.extract_context(carrier)
    mock_otel.propagate.extract.assert_called_once()

def test_inject_context(mocker):
    """Verify context injection is called when OTel is available."""
    mocker.patch('lukhas.observability.distributed_tracing.is_otel_available', return_value=True)
    from lukhas.observability import distributed_tracing

    carrier = {}
    distributed_tracing.inject_context(carrier)
    mock_otel.propagate.inject.assert_called_once()
