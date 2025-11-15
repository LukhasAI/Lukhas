"""Lane-specific metrics for LUKHAS.

These metrics are tagged with a "lane" label to distinguish between
`candidate`, `core`, and `lukhas` code paths.
"""

from observability.prometheus_registry import counter, gauge

LANE_OPERATIONS_TOTAL = counter(
    "lane_operations_total",
    "Total number of operations executed in a specific lane.",
    ["lane", "operation"],
)

LANE_ACTIVE_REQUESTS = gauge(
    "lane_active_requests",
    "Number of active requests in a specific lane.",
    ["lane"],
)
