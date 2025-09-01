"""
Revenue Tracker for NIAS Economic Platform.

This module implements transparent 40/60 profit sharing with users,
tracking conversions and managing ethical earnings distribution.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class ConversionEvent:
    """Represents a conversion event with consciousness context."""

    conversion_id: str
    user_id: str
    ad_id: str
    conversion_value: float
    commission_rate: float
    user_earnings: float
    platform_earnings: float
    timestamp: datetime
    consciousness_context: dict[str, any] = field(default_factory=dict)
    product_metadata: dict[str, any] = field(default_factory=dict)
    verified: bool = False


@dataclass
class UserEarnings:
    """Tracks cumulative earnings for a user."""

    user_id: str
    total_earned: float = 0.0
    pending_payout: float = 0.0
    paid_out: float = 0.0
    conversion_count: int = 0
    last_conversion: Optional[datetime] = None
    earnings_history: list[ConversionEvent] = field(default_factory=list)


class RevenueTracker:
    """
    Manages revenue tracking and profit sharing for NIAS platform.

    Features:
    - 40/60 profit sharing (40% to users, 60% to platform)
    - Transparent conversion tracking
    - Consciousness-aware commission rates
    - Ethical earnings verification
    - Payout management with minimum thresholds
    """

    def __init__(self):
        self.profit_sharing_config = {
            "user_percentage": 40.0,
            "platform_percentage": 60.0,
            "minimum_payout": 25.00,  # Minimum $25 for payout
            "payout_schedule": "monthly",  # monthly, weekly, or instant
        }

        self.user_earnings: dict[str, UserEarnings] = {}
        self.conversion_history: list[ConversionEvent] = []
        self.platform_revenue = {
            "total_revenue": 0.0,
            "total_user_earnings": 0.0,
            "total_platform_earnings": 0.0,
            "total_conversions": 0,
        }

        # Commission rates based on product categories
        self.commission_rates = {
            "books": 0.08,  # 8% for books
            "software": 0.15,  # 15% for software
            "courses": 0.12,  # 12% for online courses
            "wellness": 0.10,  # 10% for wellness products
            "default": 0.06,  # 6% default rate
        }

    async def record_conversion(
        self,
        user_id: str,
        ad_id: Optional[str] = None,
        conversion_value: float = 0.0,
        product_category: str = "default",
        consciousness_context: Optional[dict[str, any]] = None,
        product_metadata: Optional[dict[str, any]] = None,
    ) -> dict[str, any]:
        """
        Record a conversion event and calculate profit sharing.

        Args:
            user_id: User who generated the conversion
            ad_id: Advertisement that led to conversion
            conversion_value: Total value of the conversion
            product_category: Category for commission rate lookup
            consciousness_context: Context from consciousness profiling
            product_metadata: Additional product information

        Returns:
            Dict with user_earnings, platform_earnings, and conversion details
        """

        # Get commission rate for product category
        commission_rate = self.commission_rates.get(product_category, self.commission_rates["default"])

        # Apply consciousness-based adjustments
        if consciousness_context:
            commission_rate = await self._adjust_commission_for_consciousness(commission_rate, consciousness_context)

        # Calculate earnings
        total_commission = conversion_value * commission_rate
        user_earnings = total_commission * (self.profit_sharing_config["user_percentage"] / 100.0)
        platform_earnings = total_commission * (self.profit_sharing_config["platform_percentage"] / 100.0)

        # Generate conversion ID
        conversion_id = self._generate_conversion_id(user_id, ad_id, datetime.now())

        # Create conversion event
        conversion_event = ConversionEvent(
            conversion_id=conversion_id,
            user_id=user_id,
            ad_id=ad_id or f"unknown_{datetime.now().timestamp()}",
            conversion_value=conversion_value,
            commission_rate=commission_rate,
            user_earnings=user_earnings,
            platform_earnings=platform_earnings,
            timestamp=datetime.now(),
            consciousness_context=consciousness_context or {},
            product_metadata=product_metadata or {},
            verified=True,  # In production, this would require verification
        )

        # Update user earnings
        await self._update_user_earnings(user_id, conversion_event)

        # Update platform revenue
        self.platform_revenue["total_revenue"] += conversion_value
        self.platform_revenue["total_user_earnings"] += user_earnings
        self.platform_revenue["total_platform_earnings"] += platform_earnings
        self.platform_revenue["total_conversions"] += 1

        # Store conversion history
        self.conversion_history.append(conversion_event)

        return {
            "conversion_recorded": True,
            "conversion_id": conversion_id,
            "conversion_value": conversion_value,
            "commission_rate": commission_rate,
            "user_earnings": user_earnings,
            "platform_earnings": platform_earnings,
            "profit_sharing_breakdown": {
                "total_commission": total_commission,
                "user_percentage": self.profit_sharing_config["user_percentage"],
                "platform_percentage": self.profit_sharing_config["platform_percentage"],
            },
        }

    async def get_user_earnings_summary(self, user_id: str) -> dict[str, any]:
        """Get comprehensive earnings summary for a user."""
        user_earnings = self.user_earnings.get(user_id)
        if not user_earnings:
            return {
                "user_id": user_id,
                "total_earned": 0.0,
                "pending_payout": 0.0,
                "paid_out": 0.0,
                "conversion_count": 0,
                "eligible_for_payout": False,
            }

        # Check payout eligibility
        eligible_for_payout = user_earnings.pending_payout >= self.profit_sharing_config["minimum_payout"]

        # Calculate recent performance (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_conversions = [c for c in user_earnings.earnings_history if c.timestamp > thirty_days_ago]
        recent_earnings = sum(c.user_earnings for c in recent_conversions)

        # Top performing product categories
        category_earnings = {}
        for conversion in user_earnings.earnings_history:
            category = conversion.product_metadata.get("category", "unknown")
            category_earnings[category] = category_earnings.get(category, 0) + conversion.user_earnings

        top_categories = sorted(category_earnings.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "user_id": user_id,
            "total_earned": user_earnings.total_earned,
            "pending_payout": user_earnings.pending_payout,
            "paid_out": user_earnings.paid_out,
            "conversion_count": user_earnings.conversion_count,
            "last_conversion": user_earnings.last_conversion.isoformat() if user_earnings.last_conversion else None,
            "eligible_for_payout": eligible_for_payout,
            "minimum_payout_threshold": self.profit_sharing_config["minimum_payout"],
            "recent_performance_30d": {
                "earnings": recent_earnings,
                "conversions": len(recent_conversions),
                "avg_commission_value": recent_earnings / len(recent_conversions) if recent_conversions else 0,
            },
            "top_performing_categories": top_categories,
        }

    async def process_payout(self, user_id: str, payout_method: dict[str, any]) -> dict[str, any]:
        """
        Process payout for user earnings.

        Args:
            user_id: User requesting payout
            payout_method: Payment method details (bank, crypto, etc.)

        Returns:
            Payout processing result
        """
        user_earnings = self.user_earnings.get(user_id)
        if not user_earnings:
            return {"success": False, "error": "User earnings not found"}

        if user_earnings.pending_payout < self.profit_sharing_config["minimum_payout"]:
            return {
                "success": False,
                "error": f"Minimum payout amount is ${self.profit_sharing_config['minimum_payout']}",
                "current_pending": user_earnings.pending_payout,
            }

        # In production, this would integrate with payment processors
        payout_amount = user_earnings.pending_payout
        payout_id = self._generate_payout_id(user_id, datetime.now())

        # Update earnings record
        user_earnings.paid_out += payout_amount
        user_earnings.pending_payout = 0.0

        return {
            "success": True,
            "payout_id": payout_id,
            "payout_amount": payout_amount,
            "payout_method": payout_method.get("type", "unknown"),
            "processed_at": datetime.now().isoformat(),
            "new_total_paid": user_earnings.paid_out,
        }

    async def get_aggregate_metrics(self) -> dict[str, any]:
        """Get platform-wide revenue and earnings metrics."""
        if not self.conversion_history:
            return {
                "total_revenue": 0,
                "total_conversions": 0,
                "avg_conversion_value": 0,
                "roi_percentage": 0,
            }

        # Calculate platform metrics
        avg_conversion_value = self.platform_revenue["total_revenue"] / self.platform_revenue["total_conversions"]

        # Calculate ROI (assuming $0.50 average cost per user per day)
        estimated_user_cost = len(self.user_earnings) * 0.50  # Daily cost
        roi_percentage = (
            (self.platform_revenue["total_platform_earnings"] / estimated_user_cost * 100)
            if estimated_user_cost > 0
            else 0
        )

        # Top performing categories
        category_revenue = {}
        for conversion in self.conversion_history:
            category = conversion.product_metadata.get("category", "unknown")
            category_revenue[category] = category_revenue.get(category, 0) + conversion.conversion_value

        top_categories = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

        # User engagement metrics
        active_earners = len([u for u in self.user_earnings.values() if u.conversion_count > 0])
        avg_user_earnings = self.platform_revenue["total_user_earnings"] / active_earners if active_earners > 0 else 0

        return {
            "total_revenue": self.platform_revenue["total_revenue"],
            "total_conversions": self.platform_revenue["total_conversions"],
            "avg_conversion_value": avg_conversion_value,
            "platform_earnings": self.platform_revenue["total_platform_earnings"],
            "user_earnings": self.platform_revenue["total_user_earnings"],
            "roi_percentage": roi_percentage,
            "top_categories": top_categories,
            "user_metrics": {
                "total_users": len(self.user_earnings),
                "active_earners": active_earners,
                "avg_user_earnings": avg_user_earnings,
                "users_eligible_for_payout": len(
                    [
                        u
                        for u in self.user_earnings.values()
                        if u.pending_payout >= self.profit_sharing_config["minimum_payout"]
                    ]
                ),
            },
        }

    async def _adjust_commission_for_consciousness(
        self, base_commission: float, consciousness_context: dict[str, any]
    ) -> float:
        """
        Adjust commission rates based on consciousness alignment.

        Higher alignment with user's consciousness = higher commission rates
        to incentivize better matching.
        """
        # Get consciousness alignment factors
        ethics_score = consciousness_context.get("ethics_score", 0.5)
        resonance_score = consciousness_context.get("consciousness_resonance", 0.5)

        # Calculate alignment bonus (up to 20% increase)
        alignment_factor = (ethics_score + resonance_score) / 2
        alignment_bonus = (alignment_factor - 0.5) * 0.4  # Max 20% bonus

        # Ensure commission stays within reasonable bounds
        adjusted_commission = base_commission * (1 + alignment_bonus)
        return max(0.01, min(0.25, adjusted_commission))  # Between 1% and 25%

    async def _update_user_earnings(self, user_id: str, conversion_event: ConversionEvent) -> None:
        """Update user earnings record with new conversion."""
        if user_id not in self.user_earnings:
            self.user_earnings[user_id] = UserEarnings(user_id=user_id)

        user_earnings = self.user_earnings[user_id]
        user_earnings.total_earned += conversion_event.user_earnings
        user_earnings.pending_payout += conversion_event.user_earnings
        user_earnings.conversion_count += 1
        user_earnings.last_conversion = conversion_event.timestamp
        user_earnings.earnings_history.append(conversion_event)

        # Keep history manageable (last 500 conversions)
        if len(user_earnings.earnings_history) > 500:
            user_earnings.earnings_history = user_earnings.earnings_history[-500:]

    def _generate_conversion_id(self, user_id: str, ad_id: str, timestamp: datetime) -> str:
        """Generate unique conversion ID."""
        id_string = f"{user_id}:{ad_id}:{timestamp.isoformat()}"
        return "conv_" + hashlib.sha256(id_string.encode()).hexdigest()[:12]

    def _generate_payout_id(self, user_id: str, timestamp: datetime) -> str:
        """Generate unique payout ID."""
        id_string = f"{user_id}:payout:{timestamp.isoformat()}"
        return "payout_" + hashlib.sha256(id_string.encode()).hexdigest()[:12]
