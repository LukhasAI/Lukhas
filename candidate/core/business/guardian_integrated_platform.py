"""
Guardian Integrated Platform for NIAS Economic System.

This module implements the Guardian System integration for ethical advertising
enforcement and drift detection as specified in Phase 2A of the LUKHAS
integration strategy.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class EthicsViolation:
    """Represents an ethics violation detected by the Guardian System."""

    violation_type: str
    severity: float  # 0.0 to 1.0, where 1.0 is most severe
    description: str
    detected_at: datetime
    content_hash: str
    user_id: Optional[str] = None


@dataclass
class DriftMetrics:
    """Current drift metrics from Guardian System."""

    current_drift: float
    trend: str  # "increasing", "decreasing", "stable"
    last_updated: datetime
    violation_count_24h: int
    threshold: float = 0.15


class GuardianSystemAdapter:
    """
    Adapter for LUKHAS Guardian System integration.

    Implements Phase 2A requirements:
    - Ethics enforcement with 0.15 drift threshold
    - Real-time violation detection
    - Constitutional AI compliance
    - Audit trail generation
    """

    def __init__(self):
        self.drift_threshold = 0.15
        self.violations_cache = []
        self.current_drift = 0.0
        self.last_drift_check = datetime.now()

    async def check_content_ethics(
        self, content: dict[str, Any], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Check advertising content against Guardian System ethics.

        Returns:
            Dict containing ethics_approved, violations, drift_impact
        """
        violations = []

        # Simulate Guardian System ethics checks
        if self._contains_manipulative_language(content):
            violations.append(
                EthicsViolation(
                    violation_type="manipulative_content",
                    severity=0.8,
                    description="Content contains potentially manipulative language",
                    detected_at=datetime.now(),
                    content_hash=self._hash_content(content),
                )
            )

        if self._exploits_vulnerability(content, user_context):
            violations.append(
                EthicsViolation(
                    violation_type="vulnerability_exploitation",
                    severity=0.9,
                    description="Content appears to exploit user vulnerabilities",
                    detected_at=datetime.now(),
                    content_hash=self._hash_content(content),
                    user_id=user_context.get("user_id"),
                )
            )

        if self._violates_consent(content, user_context):
            violations.append(
                EthicsViolation(
                    violation_type="consent_violation",
                    severity=0.7,
                    description="Content violates user consent preferences",
                    detected_at=datetime.now(),
                    content_hash=self._hash_content(content),
                    user_id=user_context.get("user_id"),
                )
            )

        # Update drift metrics based on violations
        drift_impact = sum(v.severity for v in violations) * 0.1
        self.current_drift = min(1.0, self.current_drift + drift_impact)

        ethics_approved = (
            len(violations) == 0 and self.current_drift < self.drift_threshold
        )

        return {
            "ethics_approved": ethics_approved,
            "violations": [asdict(v) for v in violations],
            "current_drift": self.current_drift,
            "drift_threshold": self.drift_threshold,
            "requires_human_review": self.current_drift
            > 0.12,  # Early warning at 80% of threshold
        }

    async def get_drift_metrics(self) -> DriftMetrics:
        """Get current Guardian System drift metrics."""
        # Count violations in last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_violations = len(
            [v for v in self.violations_cache if v.detected_at > cutoff_time]
        )

        # Determine trend
        if self.current_drift > 0.12:
            trend = "increasing"
        elif self.current_drift < 0.05:
            trend = "decreasing"
        else:
            trend = "stable"

        return DriftMetrics(
            current_drift=self.current_drift,
            threshold=self.drift_threshold,
            trend=trend,
            last_updated=datetime.now(),
            violation_count_24h=recent_violations,
        )

    async def reset_drift(self) -> bool:
        """Reset drift metrics (admin operation)."""
        self.current_drift = 0.0
        self.violations_cache.clear()
        return True

    def _contains_manipulative_language(self, content: dict[str, Any]) -> bool:
        """Check for manipulative language patterns."""
        text = str(content.get("message", "")).lower()
        manipulative_patterns = [
            "you must",
            "limited time",
            "act now",
            "don't miss out",
            "exclusive offer",
            "guaranteed",
            "miracle",
            "secret",
        ]
        return any(pattern in text for pattern in manipulative_patterns)

    def _exploits_vulnerability(
        self, content: dict[str, Any], user_context: dict[str, Any]
    ) -> bool:
        """Check if content exploits user vulnerabilities."""
        # Check for financial stress exploitation
        if user_context.get("financial_stress", 0) > 0.7:
            text = str(content.get("message", "")).lower()
            if any(
                word in text for word in ["debt", "money problems", "financial freedom"]
            ):
                return True

        # Check for emotional vulnerability exploitation
        if user_context.get("emotional_state") in ["sad", "anxious", "lonely"]:
            text = str(content.get("message", "")).lower()
            if any(word in text for word in ["cure", "fix", "solve all problems"]):
                return True

        return False

    def _violates_consent(
        self, content: dict[str, Any], user_context: dict[str, Any]
    ) -> bool:
        """Check if content violates user consent preferences."""
        user_preferences = user_context.get("consent_preferences", {})
        content_categories = content.get("categories", [])

        # Check if any content category is explicitly opted-out
        opted_out_categories = user_preferences.get("opted_out_categories", [])
        return any(cat in opted_out_categories for cat in content_categories)

    def _hash_content(self, content: dict[str, Any]) -> str:
        """Generate hash for content tracking."""
        import hashlib

        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]


class GuardianIntegratedPlatform:
    """
    Main platform integrating Guardian System with NIAS economics.

    This implements Phase 2A of the LUKHAS integration strategy,
    combining ethical oversight with sustainable advertising economics.
    """

    def __init__(self, api_budget_manager, consciousness_cache, revenue_tracker):
        self.guardian = GuardianSystemAdapter()
        self.budget_manager = api_budget_manager
        self.cache = consciousness_cache
        self.revenue = revenue_tracker
        self.daily_ad_limit = 5  # Ethical limit: 1-5 ads per user per day

    async def process_advertising_request(
        self,
        user_id: str,
        consciousness_profile: dict[str, Any],
        product_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Process advertising request with Guardian System oversight.

        This is the main entry point that combines:
        - Budget management ($0.50/day limit)
        - Ethics enforcement (Guardian drift < 0.15)
        - Consciousness-aware advertising
        - Revenue tracking with profit sharing
        """

        # Check budget constraints first
        budget_status = await self.budget_manager.check_budget(user_id)
        if not budget_status["within_budget"]:
            return {
                "approved": False,
                "reason": "Daily budget limit reached",
                "budget_remaining": budget_status["remaining_budget"],
            }

        # Check daily ad limit
        daily_ads_shown = await self._get_daily_ad_count(user_id)
        if daily_ads_shown >= self.daily_ad_limit:
            return {
                "approved": False,
                "reason": f"Daily ad limit reached ({self.daily_ad_limit} ads/day max)",
                "ads_shown_today": daily_ads_shown,
            }

        # Generate consciousness-aware content
        ad_content = await self._generate_conscious_content(
            consciousness_profile, product_context
        )

        # Guardian System ethics check
        ethics_result = await self.guardian.check_content_ethics(
            ad_content, consciousness_profile
        )

        if not ethics_result["ethics_approved"]:
            # Log ethics violation for audit
            await self._log_ethics_violation(user_id, ethics_result)

            if ethics_result["requires_human_review"]:
                return {
                    "approved": False,
                    "reason": "Content requires human review due to high drift",
                    "drift_metrics": ethics_result,
                    "escalated_to_human": True,
                }
            else:
                return {
                    "approved": False,
                    "reason": "Content violates Guardian System ethics",
                    "violations": ethics_result["violations"],
                }

        # Content approved - proceed with serving
        # Record budget usage
        estimated_cost = 0.05  # Per-ad processing cost
        await self.budget_manager.record_usage(
            user_id, estimated_cost, "advertising_generation"
        )

        # Track ad serving for daily limits
        await self._increment_daily_ad_count(user_id)

        # Cache consciousness profile to reduce future costs
        await self.cache.store_consciousness_state(
            user_id, consciousness_profile, ttl_hours=24
        )

        return {
            "approved": True,
            "ad_content": ad_content,
            "ethics_score": 1.0 - ethics_result["current_drift"],
            "consciousness_resonance": ad_content.get("resonance_score", 0.8),
            "cost_incurred": estimated_cost,
            "ads_remaining_today": self.daily_ad_limit - daily_ads_shown - 1,
        }

    async def track_conversion(
        self,
        user_id: str,
        ad_id: str,
        conversion_value: float,
        product_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Track conversion with Guardian-compliant profit sharing.
        """
        # Verify conversion legitimacy through Guardian System
        conversion_context = {
            "user_id": user_id,
            "ad_id": ad_id,
            "conversion_value": conversion_value,
            "timestamp": datetime.now().isoformat(),
            "product_metadata": product_metadata,
        }

        ethics_check = await self.guardian.check_content_ethics(
            conversion_context, {"user_id": user_id}
        )

        if not ethics_check["ethics_approved"]:
            return {
                "conversion_recorded": False,
                "reason": "Conversion failed Guardian System verification",
                "ethics_violations": ethics_check["violations"],
            }

        # Record legitimate conversion with profit sharing
        sharing_result = await self.revenue.record_conversion(
            user_id=user_id,
            conversion_value=conversion_value,
            consciousness_context={
                "ethics_score": 1.0 - ethics_check["current_drift"],
                "guardian_approved": True,
            },
        )

        return {
            "conversion_recorded": True,
            "user_earnings": sharing_result["user_earnings"],
            "platform_earnings": sharing_result["platform_earnings"],
            "ethics_compliance": "guardian_verified",
            "drift_score": ethics_check["current_drift"],
        }

    async def get_platform_health_metrics(self) -> dict[str, Any]:
        """
        Get comprehensive platform health metrics including Guardian status.
        """
        drift_metrics = await self.guardian.get_drift_metrics()
        budget_metrics = await self.budget_manager.get_aggregate_metrics()
        revenue_metrics = await self.revenue.get_aggregate_metrics()

        return {
            "guardian_status": {
                "current_drift": drift_metrics.current_drift,
                "drift_threshold": drift_metrics.threshold,
                "status": "healthy" if drift_metrics.current_drift < 0.1 else "warning",
                "violations_24h": drift_metrics.violation_count_24h,
                "trend": drift_metrics.trend,
            },
            "economics_status": {
                "total_budget_allocated": budget_metrics.get("total_allocated", 0),
                "total_revenue_generated": revenue_metrics.get("total_revenue", 0),
                "user_earnings_paid": revenue_metrics.get("user_earnings", 0),
                "platform_roi": revenue_metrics.get("roi_percentage", 0),
            },
            "ethical_compliance": {
                "guardian_integrated": True,
                "drift_monitoring": "active",
                "consent_tracking": "enabled",
                "profit_sharing_active": True,
            },
        }

    async def _generate_conscious_content(
        self, consciousness_profile: dict[str, Any], product_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate consciousness-aware advertising content."""
        # This would integrate with qi engines in full implementation
        return {
            "message": "Discover something aligned with your current journey.",
            "visual_elements": ["calming", "authentic", "non-intrusive"],
            "resonance_score": 0.85,
            "categories": product_context.get("categories", ["general"]),
            "consciousness_alignment": consciousness_profile.get("values", []),
        }

    async def _get_daily_ad_count(self, user_id: str) -> int:
        """Get number of ads shown to user today."""
        # This would query from a real database in production
        return 0  # Placeholder

    async def _increment_daily_ad_count(self, user_id: str) -> None:
        """Increment daily ad count for user."""
        # This would update a real database in production
        pass

    async def _log_ethics_violation(
        self, user_id: str, ethics_result: dict[str, Any]
    ) -> None:
        """Log ethics violation for audit trail."""
        # This would integrate with LUKHAS audit systems in production
        print(
            f"ETHICS VIOLATION LOGGED: User {user_id}, Drift: {ethics_result['current_drift']}"
        )
