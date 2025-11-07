"""
lukhas/core/policy_guard.py

Phase 5: Lane-aware replay policy checker with deterministic allow/deny logs.
Provides policy-gated learning over Experience Replay system.

Usage:
    from core.policy_guard import PolicyGuard, ReplayDecision

    guard = PolicyGuard(lane="experimental")
    decision = guard.check_replay(event_kind="action", payload={"risk_level": 0.2})
    if decision.allow:
        # Proceed with replay
        pass
"""
from __future__ import annotations

import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

# Optional Prometheus metrics
try:
    from prometheus_client import Counter, Histogram
    REPLAY_POLICY_DENIALS = Counter("lukhas_replay_policy_denials_total", "Policy denials", ["lane", "kind", "reason"])
    REPLAY_POLICY_ALLOWS = Counter("lukhas_replay_policy_allows_total", "Policy allows", ["lane", "kind"])
    POLICY_DECISIONS = Histogram("lukhas_policy_decision_duration_seconds", "Policy decision time", ["lane"])
    PROMOTION_ATTEMPTS_TOTAL = Counter("lukhas_promotion_attempts_total", "Cross-lane promotion attempts", ["source_lane", "target_lane"])
    PROMOTION_SUCCESS_TOTAL = Counter("lukhas_promotion_success_total", "Successful cross-lane promotions", ["source_lane", "target_lane"])
    PROM = True
except Exception:
    PROM = False
    class _NoopMetric:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def observe(self, *_): pass
        def set(self, *_): pass
    REPLAY_POLICY_DENIALS = _NoopMetric()
    REPLAY_POLICY_ALLOWS = _NoopMetric()
    POLICY_DECISIONS = _NoopMetric()
    PROMOTION_ATTEMPTS_TOTAL = _NoopMetric()
    PROMOTION_SUCCESS_TOTAL = _NoopMetric()


logger = logging.getLogger(__name__)


class PolicyResult(Enum):
    """Policy decision outcomes."""
    ALLOW = "allow"
    DENY_RISK = "deny_risk"
    DENY_LANE = "deny_lane"
    DENY_KIND = "deny_kind"
    DENY_RATE = "deny_rate"
    DENY_BUDGET = "deny_budget"


@dataclass(frozen=True)
class ReplayDecision:
    """Policy decision for replay request."""
    allow: bool
    result: PolicyResult
    reason: str
    lane: str
    event_kind: str
    decision_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_log_entry(self) -> dict[str, Any]:
        """Convert to deterministic log entry."""
        return {
            "decision_id": str(self.decision_id),
            "timestamp": self.timestamp.isoformat(),
            "lane": self.lane,
            "event_kind": self.event_kind,
            "result": self.result.value,
            "allow": self.allow,
            "reason": self.reason
        }


@dataclass
class LanePolicyConfig:
    """Lane-specific policy configuration."""
    # Risk thresholds (0.0 to 1.0)
    max_risk_level: float = 1.0

    # Allowed event kinds
    allowed_kinds: set[str] = field(default_factory=lambda: {
        "consciousness_tick", "tick_processed", "stream_started", "stream_stopped",
        "action", "intention", "memory_write", "reward", "breakthrough"
    })

    # Rate limiting (events per minute)
    max_replay_rate: int = 1000

    # Budget limits (replay operations per window)
    replay_budget: int = 100
    budget_window_minutes: int = 5

    # Cross-lane promotion requirements
    promotion_drift_threshold: float = 0.25
    promotion_coherence_threshold: float = 0.8
    promotion_window_minutes: int = 10


# Default lane configurations
DEFAULT_LANE_CONFIGS: dict[str, LanePolicyConfig] = {
    "experimental": LanePolicyConfig(
        max_risk_level=0.8,
        max_replay_rate=2000,
        replay_budget=200,
        promotion_drift_threshold=0.35,
        promotion_coherence_threshold=0.7
    ),
    "candidate": LanePolicyConfig(
        max_risk_level=0.5,
        max_replay_rate=1000,
        replay_budget=100,
        promotion_drift_threshold=0.25,
        promotion_coherence_threshold=0.8
    ),
    "prod": LanePolicyConfig(
        max_risk_level=0.2,
        max_replay_rate=500,
        replay_budget=50,
        promotion_drift_threshold=0.15,
        promotion_coherence_threshold=0.9
    )
}


class PolicyGuard:
    """
    Lane-aware replay policy checker for governance over Experience Replay.

    Provides deterministic allow/deny decisions based on lane-specific policies,
    risk assessment, rate limiting, and budget constraints.
    """

    def __init__(self, lane: str | None = None, custom_config: dict[str, LanePolicyConfig] | None = None):
        """
        Initialize policy guard.

        Args:
            lane: Target lane (defaults to LUKHAS_LANE env var)
            custom_config: Custom lane configuration overrides
        """
        self.lane = (lane or os.getenv("LUKHAS_LANE", "experimental")).lower()

        # Load configurations
        self.lane_configs = custom_config or DEFAULT_LANE_CONFIGS.copy()
        self.config = self.lane_configs.get(self.lane, DEFAULT_LANE_CONFIGS["experimental"])

        # Rate limiting and budget tracking
        self._replay_counts: dict[datetime, int] = {}  # minute -> count
        self._budget_usage: list[datetime] = []  # replay timestamps for budget window

        # Decision log for deterministic replay
        self._decision_log: list[ReplayDecision] = []

        logger.info(f"PolicyGuard initialized: lane={self.lane}, config={self.config}")

    def check_replay(
        self,
        event_kind: str,
        payload: dict[str, Any] | None = None,
        risk_level: float | None = None,
        source_lane: str | None = None
    ) -> ReplayDecision:
        """
        Check if replay is allowed under current policy.

        Args:
            event_kind: Type of event to replay
            payload: Event payload for analysis
            risk_level: Explicit risk level (0.0-1.0), or computed from payload
            source_lane: Source lane of the event (for cross-lane checks)

        Returns:
            ReplayDecision with allow/deny result and reasoning
        """
        start_time = datetime.now(timezone.utc)

        try:
            # 1. Check event kind allowlist
            if event_kind not in self.config.allowed_kinds:
                decision = ReplayDecision(
                    allow=False,
                    result=PolicyResult.DENY_KIND,
                    reason=f"Event kind '{event_kind}' not allowed in lane '{self.lane}'",
                    lane=self.lane,
                    event_kind=event_kind
                )
                self._log_decision(decision)
                return decision

            # 2. Check cross-lane restrictions
            if source_lane and source_lane != self.lane:
                # Record promotion attempt
                if PROM:
                    PROMOTION_ATTEMPTS_TOTAL.labels(source_lane=source_lane, target_lane=self.lane).inc()

                if not self._allow_cross_lane_replay(source_lane, self.lane):
                    decision = ReplayDecision(
                        allow=False,
                        result=PolicyResult.DENY_LANE,
                        reason=f"Cross-lane replay from '{source_lane}' to '{self.lane}' not permitted",
                        lane=self.lane,
                        event_kind=event_kind
                    )
                    self._log_decision(decision)
                    return decision

            # 3. Assess risk level
            computed_risk = risk_level if risk_level is not None else self._compute_risk(payload or {})

            if computed_risk > self.config.max_risk_level:
                decision = ReplayDecision(
                    allow=False,
                    result=PolicyResult.DENY_RISK,
                    reason=f"Risk level {computed_risk:.3f} exceeds threshold {self.config.max_risk_level:.3f}",
                    lane=self.lane,
                    event_kind=event_kind
                )
                self._log_decision(decision)
                return decision

            # 4. Check rate limiting
            if not self._check_rate_limit():
                decision = ReplayDecision(
                    allow=False,
                    result=PolicyResult.DENY_RATE,
                    reason=f"Replay rate limit {self.config.max_replay_rate}/min exceeded",
                    lane=self.lane,
                    event_kind=event_kind
                )
                self._log_decision(decision)
                return decision

            # 5. Check budget constraints
            if not self._check_budget():
                decision = ReplayDecision(
                    allow=False,
                    result=PolicyResult.DENY_BUDGET,
                    reason=f"Replay budget {self.config.replay_budget} ops/{self.config.budget_window_minutes}min exceeded",
                    lane=self.lane,
                    event_kind=event_kind
                )
                self._log_decision(decision)
                return decision

            # All checks passed - allow replay
            decision = ReplayDecision(
                allow=True,
                result=PolicyResult.ALLOW,
                reason="Policy checks passed",
                lane=self.lane,
                event_kind=event_kind
            )

            # Update counters
            self._record_replay()

            # Record successful cross-lane promotion
            if source_lane and source_lane != self.lane and PROM:
                PROMOTION_SUCCESS_TOTAL.labels(source_lane=source_lane, target_lane=self.lane).inc()

            self._log_decision(decision)

            return decision

        finally:
            # Record metrics
            if PROM:
                decision_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                POLICY_DECISIONS.labels(lane=self.lane).observe(decision_duration)

    def _compute_risk(self, payload: dict[str, Any]) -> float:
        """Compute risk level from event payload."""
        # Extract explicit risk indicators
        if "risk_level" in payload:
            return float(payload["risk_level"])

        if "error" in payload or "exception" in payload:
            return 0.7  # Errors are moderately risky

        if "external_action" in payload:
            return 0.6  # External actions have inherent risk

        # Default low risk for most events
        return 0.1

    def _allow_cross_lane_replay(self, source_lane: str, target_lane: str) -> bool:
        """Check if cross-lane replay is permitted."""
        # Define promotion path: experimental -> candidate -> prod
        lane_hierarchy = {"experimental": 0, "candidate": 1, "prod": 2}

        source_level = lane_hierarchy.get(source_lane, 0)
        target_level = lane_hierarchy.get(target_lane, 0)

        # Only allow replay from same or lower levels (more permissive -> more restrictive)
        return source_level <= target_level

    def _check_rate_limit(self) -> bool:
        """Check if replay rate is within limits."""
        now = datetime.now(timezone.utc)
        current_minute = now.replace(second=0, microsecond=0)

        # Clean old entries
        cutoff = current_minute - timedelta(minutes=1)
        self._replay_counts = {
            ts: count for ts, count in self._replay_counts.items()
            if ts >= cutoff
        }

        # Check current minute's count
        current_count = self._replay_counts.get(current_minute, 0)
        return current_count < self.config.max_replay_rate

    def _check_budget(self) -> bool:
        """Check if replay budget is available."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=self.config.budget_window_minutes)

        # Clean old entries
        self._budget_usage = [ts for ts in self._budget_usage if ts >= window_start]

        # Check if budget available
        return len(self._budget_usage) < self.config.replay_budget

    def _record_replay(self) -> None:
        """Record a replay for rate limiting and budget tracking."""
        now = datetime.now(timezone.utc)
        current_minute = now.replace(second=0, microsecond=0)

        # Update rate counter
        self._replay_counts[current_minute] = self._replay_counts.get(current_minute, 0) + 1

        # Update budget tracker
        self._budget_usage.append(now)

    def _log_decision(self, decision: ReplayDecision) -> None:
        """Log decision for deterministic replay and metrics."""
        # Add to decision log
        self._decision_log.append(decision)

        # Log deterministically
        log_entry = decision.to_log_entry()
        if decision.allow:
            logger.info(f"Policy ALLOW: {log_entry}")
        else:
            logger.warning(f"Policy DENY: {log_entry}")

        # Update Prometheus metrics
        if PROM:
            if decision.allow:
                REPLAY_POLICY_ALLOWS.labels(lane=decision.lane, kind=decision.event_kind).inc()
            else:
                REPLAY_POLICY_DENIALS.labels(
                    lane=decision.lane,
                    kind=decision.event_kind,
                    reason=decision.result.value
                ).inc()

    def get_decision_log(self, limit: int | None = None) -> list[ReplayDecision]:
        """Get recent policy decisions for audit/debugging."""
        if limit is None:
            return self._decision_log.copy()
        return self._decision_log[-limit:]

    def get_policy_stats(self) -> dict[str, Any]:
        """Get current policy statistics."""
        now = datetime.now(timezone.utc)

        # Calculate recent metrics
        recent_decisions = [
            d for d in self._decision_log
            if (now - d.timestamp).total_seconds() < 300  # Last 5 minutes
        ]

        allows = sum(1 for d in recent_decisions if d.allow)
        denies = len(recent_decisions) - allows

        return {
            "lane": self.lane,
            "total_decisions": len(self._decision_log),
            "recent_decisions_5min": len(recent_decisions),
            "recent_allows": allows,
            "recent_denies": denies,
            "current_budget_usage": len(self._budget_usage),
            "budget_capacity": self.config.replay_budget,
            "rate_limit_capacity": self.config.max_replay_rate,
            "max_risk_threshold": self.config.max_risk_level,
            "allowed_kinds": list(self.config.allowed_kinds)
        }

    def get_promotion_stats(self) -> dict[str, Any]:
        """Get promotion statistics for cross-lane operations."""
        now = datetime.now(timezone.utc)

        # Count cross-lane decisions in recent window
        recent_decisions = [
            d for d in self._decision_log
            if (now - d.timestamp).total_seconds() < 600  # Last 10 minutes
        ]

        cross_lane_attempts = 0
        cross_lane_successes = 0
        promotion_paths = defaultdict(int)
        success_paths = defaultdict(int)

        for decision in recent_decisions:
            # Check if this was a cross-lane operation (we need to store source_lane in payload)
            if hasattr(decision, 'source_lane') or 'source_lane' in (decision.reason or ''):
                cross_lane_attempts += 1
                path_key = f"unknown→{decision.lane}"  # We'll enhance this when we store source_lane
                promotion_paths[path_key] += 1

                if decision.allow:
                    cross_lane_successes += 1
                    success_paths[path_key] += 1

        return {
            "lane": self.lane,
            "recent_promotion_attempts_10min": cross_lane_attempts,
            "recent_promotion_successes_10min": cross_lane_successes,
            "promotion_success_rate": (cross_lane_successes / max(cross_lane_attempts, 1)),
            "promotion_paths": dict(promotion_paths),
            "successful_paths": dict(success_paths),
            "drift_threshold": self.config.promotion_drift_threshold,
            "coherence_threshold": self.config.promotion_coherence_threshold
        }

    def reset_stats(self) -> None:
        """Reset policy statistics (for testing)."""
        self._replay_counts.clear()
        self._budget_usage.clear()
        self._decision_log.clear()


def create_policy_guard(lane: str | None = None, **config_overrides) -> PolicyGuard:
    """Factory function for creating policy guards."""
    return PolicyGuard(lane=lane)
