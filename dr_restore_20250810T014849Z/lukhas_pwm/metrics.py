"""
LUKHAS Metrics Collection ⚛️📊
Prometheus-compatible metrics for monitoring and alerting.
"""

import time

from prometheus_client import REGISTRY
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from prometheus_client import generate_latest

# Counters for security events
incident_blocked_tool = Counter(
    "lukhas_incident_blocked_tool_total",
    "Total number of blocked tool attempts",
    ["attempted_tool", "safety_mode"],
)

strict_auto_tighten = Counter(
    "lukhas_strict_auto_tighten_total",
    "Number of times safety auto-tightened to strict",
    ["trigger_reason"],
)

openai_errors = Counter(
    "lukhas_openai_errors_total",
    "OpenAI API errors by type",
    ["error_type", "status_code"],
)

# Histograms for performance
tool_duration_ms = Histogram(
    "lukhas_tool_duration_milliseconds",
    "Tool execution duration in milliseconds",
    ["tool_name", "status"],
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
)

openai_latency_ms = Histogram(
    "lukhas_openai_latency_milliseconds",
    "OpenAI API call latency in milliseconds",
    ["model", "safety_mode"],
    buckets=(100, 250, 500, 1000, 2000, 3000, 5000, 10000),
)

token_usage = Histogram(
    "lukhas_token_usage",
    "Tokens used per request",
    ["direction", "model"],  # direction: input/output
    buckets=(10, 50, 100, 250, 500, 1000, 2000, 4000, 8000),
)

# Gauges for current state
current_safety_mode = Gauge(
    "lukhas_current_safety_mode",
    "Current safety mode (0=creative, 1=balanced, 2=strict)",
    ["session_id"],
)

active_tool_calls = Gauge(
    "lukhas_active_tool_calls", "Number of currently active tool calls"
)

feedback_lut_temperature = Gauge(
    "lukhas_feedback_lut_temperature_delta",
    "Current LUT temperature adjustment",
)

# Rate tracking
requests_per_minute = Counter(
    "lukhas_requests_per_minute",
    "Requests processed per minute",
    ["endpoint", "status"],
)


class MetricsCollector:
    """Centralized metrics collection"""

    def __init__(self):
        self.start_time = time.time()

    def record_blocked_tool(self, tool_name: str, safety_mode: str):
        """Record a blocked tool attempt"""
        incident_blocked_tool.labels(
            attempted_tool=tool_name, safety_mode=safety_mode
        ).inc()

    def record_auto_tighten(self, reason: str = "high_risk"):
        """Record auto-tightening to strict mode"""
        strict_auto_tighten.labels(trigger_reason=reason).inc()

    def record_openai_error(self, error_type: str, status_code: int = 0):
        """Record OpenAI API error"""
        openai_errors.labels(error_type=error_type, status_code=str(status_code)).inc()

    def record_tool_duration(
        self, tool_name: str, duration_ms: float, status: str = "success"
    ):
        """Record tool execution duration"""
        tool_duration_ms.labels(tool_name=tool_name, status=status).observe(duration_ms)

    def record_openai_latency(
        self, model: str, latency_ms: float, safety_mode: str = "balanced"
    ):
        """Record OpenAI API latency"""
        openai_latency_ms.labels(model=model, safety_mode=safety_mode).observe(
            latency_ms
        )

    def record_token_usage(
        self, input_tokens: int, output_tokens: int, model: str = "gpt-4"
    ):
        """Record token usage"""
        token_usage.labels(direction="input", model=model).observe(input_tokens)
        token_usage.labels(direction="output", model=model).observe(output_tokens)

    def set_safety_mode(self, mode: str, session_id: str = "default"):
        """Update current safety mode gauge"""
        mode_values = {"creative": 0, "balanced": 1, "strict": 2}
        current_safety_mode.labels(session_id=session_id).set(mode_values.get(mode, 1))

    def set_active_tools(self, count: int):
        """Update active tool calls gauge"""
        active_tool_calls.set(count)

    def set_lut_temperature(self, delta: float):
        """Update LUT temperature adjustment gauge"""
        feedback_lut_temperature.set(delta)

    def record_request(self, endpoint: str, status: str = "success"):
        """Record API request"""
        requests_per_minute.labels(endpoint=endpoint, status=status).inc()

    def get_metrics(self) -> bytes:
        """Generate Prometheus metrics output"""
        return generate_latest(REGISTRY)

    def check_alert_conditions(self) -> list:
        """Check for alert conditions"""
        alerts = []

        # Get current metric values (simplified for demo)
        # In production, query Prometheus or use metric._value

        # Check blocked tools rate
        # if blocked_tools_per_hour > 10:
        #     alerts.append({
        #         "level": "warning",
        #         "message": "High rate of blocked tool attempts",
        #         "metric": "incident_blocked_tool",
        #         "threshold": 10
        #     })

        # Check auto-tightening rate
        # if auto_tighten_per_hour > 5:
        #     alerts.append({
        #         "level": "warning",
        #         "message": "Frequent auto-tightening to strict mode",
        #         "metric": "strict_auto_tighten",
        #         "threshold": 5
        #     })

        # Check error rate
        # if openai_errors_per_minute > 1:
        #     alerts.append({
        #         "level": "critical",
        #         "message": "High OpenAI API error rate",
        #         "metric": "openai_errors",
        #         "threshold": 1
        #     })

        return alerts


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    return _metrics_collector
