"""
Prometheus metrics for Guardian policy enforcement observability.

Tracks policy decision outcomes (allow/deny), denial reasons, and
performance metrics for the Policy Decision Point (PDP). Provides
visibility into authorization patterns and policy effectiveness.

Phase 3: Guardian enhancements for production monitoring.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Check if Prometheus client is available
try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not available, Guardian metrics disabled")

    # No-op fallback classes
    class _Nop:
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def observe(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass

    Counter = Histogram = Gauge = lambda *a, **kw: _Nop()  # type: ignore


# Guardian decision counter
# Tracks allow/deny decisions by scope, route, and effect
GUARDIAN_DECISION_TOTAL = Counter(
    "lukhas_guardian_decision_total",
    "Total Guardian policy decisions by outcome",
    ["outcome", "scope", "route"],
)

# Guardian denied reason counter
# Tracks why requests were denied (with reason label cardinality cap)
GUARDIAN_DENIED_REASON = Counter(
    "lukhas_guardian_denied_total",
    "Total Guardian denials by reason",
    ["reason", "route"],
)

# PDP evaluation latency
# Tracks time spent in policy decision evaluation
GUARDIAN_DECISION_LATENCY = Histogram(
    "lukhas_guardian_decision_duration_seconds",
    "Guardian policy decision evaluation latency",
    ["outcome"],
    buckets=[0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500, 1.0],
)

# Active policy version gauge
# Tracks the current policy etag for monitoring policy updates
GUARDIAN_POLICY_VERSION = Gauge(
    "lukhas_guardian_policy_version_info",
    "Guardian policy version information",
    ["etag", "tenant_id"],
)

# Policy rule evaluation counter
# Tracks how often each policy rule is evaluated
GUARDIAN_RULE_EVALUATIONS = Counter(
    "lukhas_guardian_rule_evaluations_total",
    "Total policy rule evaluations",
    ["rule_id", "effect"],
)


def _enabled() -> bool:
    """Check if Guardian metrics are enabled via environment."""
    return os.getenv("LUKHAS_GUARDIAN_METRICS", "1").lower() not in ("0", "false", "off")


def _cap_reason(reason: str, max_length: int = 64) -> str:
    """
    Cap denial reason length to prevent cardinality explosion.

    Args:
        reason: Raw denial reason string
        max_length: Maximum allowed length

    Returns:
        Truncated reason string
    """
    if not reason:
        return "unknown"

    # Normalize common patterns
    if reason.startswith("deny_rule_matched:"):
        return "deny_rule_matched"
    elif reason.startswith("allow_rule_matched:"):
        return "allow_matched"  # Should not be denied, but handle gracefully
    elif reason == "default_deny":
        return "default_deny"
    elif "scope" in reason.lower():
        return "insufficient_scope"
    elif "rate_limit" in reason.lower():
        return "rate_limit_exceeded"
    elif "forbidden" in reason.lower():
        return "forbidden"

    # Truncate and sanitize
    reason = reason[:max_length]
    # Remove any potentially sensitive data patterns
    reason = reason.split(":")[ 0]  # Take only prefix before colons
    return reason or "unknown"


def _normalize_route(route: str) -> str:
    """
    Normalize route to reduce cardinality.

    Args:
        route: Request route path

    Returns:
        Normalized route label
    """
    if not route:
        return "unknown"

    # Common API patterns
    if route.startswith("/v1/embeddings"):
        return "/v1/embeddings"
    elif route.startswith("/v1/responses"):
        return "/v1/responses"
    elif route.startswith("/v1/dreams"):
        return "/v1/dreams"
    elif route.startswith("/v1/models"):
        return "/v1/models"
    elif route.startswith("/v1/indexes"):
        return "/v1/indexes"
    elif route.startswith("/healthz") or route.startswith("/readyz"):
        return "/health"

    # Fallback: strip query params and truncate
    route = route.split("?")[0]
    return route[:64]


def record_decision(
    allow: bool,
    scope: Optional[str] = None,
    route: Optional[str] = None,
    reason: Optional[str] = None,
    duration_seconds: Optional[float] = None,
) -> None:
    """
    Record a Guardian policy decision outcome.

    Args:
        allow: True if request was allowed, False if denied
        scope: OAuth scope that was checked (optional)
        route: Request route path (optional)
        reason: Denial reason if denied (optional)
        duration_seconds: Decision evaluation time (optional)
    """
    if not _enabled() or not PROMETHEUS_AVAILABLE:
        return

    try:
        outcome = "allow" if allow else "deny"
        scope_label = scope or "none"
        route_label = _normalize_route(route or "unknown")

        # Record decision counter
        GUARDIAN_DECISION_TOTAL.labels(
            outcome=outcome,
            scope=scope_label,
            route=route_label,
        ).inc()

        # Record denial reason if denied
        if not allow and reason:
            capped_reason = _cap_reason(reason)
            GUARDIAN_DENIED_REASON.labels(
                reason=capped_reason,
                route=route_label,
            ).inc()

        # Record latency if provided
        if duration_seconds is not None:
            GUARDIAN_DECISION_LATENCY.labels(outcome=outcome).observe(duration_seconds)

    except Exception as e:
        # Never crash request processing due to metrics
        logger.debug(f"Failed to record Guardian decision metric: {e}")


def record_rule_evaluation(rule_id: str, effect: str) -> None:
    """
    Record a policy rule evaluation.

    Args:
        rule_id: Policy rule identifier
        effect: Rule effect ("Allow" or "Deny")
    """
    if not _enabled() or not PROMETHEUS_AVAILABLE:
        return

    try:
        # Truncate rule_id to prevent cardinality issues
        rule_label = rule_id[:32] if rule_id else "unknown"
        effect_label = effect.lower() if effect else "unknown"

        GUARDIAN_RULE_EVALUATIONS.labels(
            rule_id=rule_label,
            effect=effect_label,
        ).inc()
    except Exception as e:
        logger.debug(f"Failed to record rule evaluation metric: {e}")


def set_policy_version(etag: str, tenant_id: Optional[str] = None) -> None:
    """
    Set the current policy version gauge.

    Args:
        etag: Policy configuration etag/hash
        tenant_id: Tenant identifier (optional)
    """
    if not _enabled() or not PROMETHEUS_AVAILABLE:
        return

    try:
        # Truncate etag to first 8 chars for readability
        etag_label = etag[:8] if etag else "unknown"
        tenant_label = tenant_id or "global"

        GUARDIAN_POLICY_VERSION.labels(
            etag=etag_label,
            tenant_id=tenant_label,
        ).set(1)
    except Exception as e:
        logger.debug(f"Failed to set policy version metric: {e}")


def get_decision_stats() -> dict:
    """
    Get Guardian decision statistics summary.

    Returns:
        Dictionary with allow/deny counts (best effort, may be incomplete)
    """
    # Note: Prometheus counters don't expose their values easily in Python
    # This is a placeholder for external metrics scraping
    return {
        "note": "Guardian metrics available via /metrics endpoint",
        "metrics_enabled": _enabled() and PROMETHEUS_AVAILABLE,
    }
