import asyncio

import pytest
from matriz.monitoring.prometheus_exporter import (
    execute_operation,
    memory_usage,
    operation_latency,
    operation_total,
)
from prometheus_client import REGISTRY


# Mock node and operation classes
class MockNode:
    def __init__(self, node_type):
        self.type = node_type

class MockOperation:
    def __init__(self, op_type, node_type, success=True):
        self.type = op_type
        self.node = MockNode(node_type)
        self.success = success

    async def execute(self):
        await asyncio.sleep(0.01)
        if not self.success:
            raise ValueError("Operation failed")
        return "result"

@pytest.fixture(autouse=True)
def clear_metrics():
    """Clear all metrics before each test."""
    for collector in list(REGISTRY._collector_to_names.keys()):
        # HACK: prometheus_client library says to not use the clear() method,
        # but it is the easiest way to ensure tests are isolated.
        if hasattr(collector, 'clear'):
            collector.clear()

def test_metrics_registration():
    """Tests that the metrics are registered with the Prometheus registry."""
    collectors = REGISTRY._collector_to_names.keys()
    assert operation_latency in collectors
    assert operation_total in collectors
    assert memory_usage in collectors

@pytest.mark.asyncio
async def test_latency_tracking():
    """Tests that the operation_latency histogram is updated."""
    operation = MockOperation("test_op", "test_node")
    await execute_operation(operation)

    samples = operation_latency.collect()[0].samples
    assert len(samples) > 0
    bucket_sample = next(s for s in samples if s.name == 'matriz_operation_latency_seconds_bucket' and '+Inf' in s.labels['le'])
    assert bucket_sample.value == 1.0
    assert bucket_sample.labels['operation_type'] == 'test_op'
    assert bucket_sample.labels['node_type'] == 'test_node'

    count_sample = next(s for s in samples if s.name == 'matriz_operation_latency_seconds_count')
    assert count_sample.value == 1.0

    sum_sample = next(s for s in samples if s.name == 'matriz_operation_latency_seconds_sum')
    assert sum_sample.value > 0.01

@pytest.mark.asyncio
async def test_counter_increments_on_success():
    """Tests that the operation_total counter is incremented on success."""
    operation = MockOperation("test_op", "test_node")
    await execute_operation(operation)

    samples = operation_total.collect()[0].samples
    # Filter for the specific metric sample, ignoring the auto-added '_created' sample
    sample = next(s for s in samples if s.name == 'matriz_operations_total')
    assert sample.value == 1.0
    assert sample.labels['operation_type'] == 'test_op'
    assert sample.labels['status'] == 'success'

@pytest.mark.asyncio
async def test_counter_increments_on_failure():
    """Tests that the operation_total counter is incremented on failure."""
    operation = MockOperation("test_op", "test_node", success=False)
    with pytest.raises(ValueError):
        await execute_operation(operation)

    samples = operation_total.collect()[0].samples
    sample = next(s for s in samples if s.name == 'matriz_operations_total')
    assert sample.value == 1.0
    assert sample.labels['operation_type'] == 'test_op'
    assert sample.labels['status'] == 'error'


def test_gauge_updates():
    """Tests that the memory_usage gauge can be updated."""
    from matriz.monitoring.prometheus_exporter import update_memory_usage
    update_memory_usage(component="test_component", usage_bytes=12345)
    samples = memory_usage.collect()[0].samples
    assert len(samples) == 1
    sample = samples[0]
    assert sample.value == 12345
    assert sample.labels['component'] == 'test_component'
