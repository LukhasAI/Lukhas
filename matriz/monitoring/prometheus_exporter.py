from prometheus_client import Counter, Gauge, Histogram

# Define metrics
operation_latency = Histogram(
    'matriz_operation_latency_seconds',
    'Operation latency in seconds',
    ['operation_type', 'node_type']
)

operation_total = Counter(
    'matriz_operations_total',
    'Total number of operations',
    ['operation_type', 'status']
)

memory_usage = Gauge(
    'matriz_memory_bytes',
    'Current memory usage in bytes',
    ['component']
)

# Instrumentation
async def execute_operation(operation):
    """
    Executes a given operation while collecting Prometheus metrics for latency and status.
    """
    try:
        with operation_latency.labels(
            operation_type=operation.type,
            node_type=operation.node.type
        ).time():
            result = await operation.execute()
            operation_total.labels(
                operation_type=operation.type,
                status='success'
            ).inc()
            return result
    except Exception:
        operation_total.labels(
            operation_type=operation.type,
            status='error'
        ).inc()
        # Re-raise the exception to not alter the original control flow
        raise

def update_memory_usage(component: str, usage_bytes: int):
    """
    Updates the memory usage gauge for a specific component.
    """
    memory_usage.labels(component=component).set(usage_bytes)
