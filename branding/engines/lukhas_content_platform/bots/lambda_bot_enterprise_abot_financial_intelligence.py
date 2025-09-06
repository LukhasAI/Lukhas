#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Autonomous Financial Intelligence System
Smart budget management with accumulation, conservation, and self-optimization
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime

logger = logging.getLogger("ABotFinancialIntelligence", timezone)


@dataclass
class FinancialMetrics:
    """LUKHAS AI ΛBot's financial tracking and intelligence"""

    # Daily budget system
    daily_budget: float = 0.10  # $0.10 per day
    current_balance: float = 0.0
    total_accumulated: float = 0.0
    last_budget_refresh: str = ""

    # Spending tracking
    today_spent: float = 0.0
    month_spent: float = 0.0
    total_spent: float = 0.0
    calls_today: int = 0
    calls_month: int = 0
    total_calls: int = 0

    # Intelligence metrics
    money_saved_by_conservation: float = 0.0
    days_without_calls: int = 0
    flex_budget_used: float = 0.0
    efficiency_score: float = 100.0

    # Usage patterns
    peak_usage_days: list[str] = None
    conservation_streak: int = 0
    last_call_reason: str = ""

    def __post_init__(self):
        if self.peak_usage_days is None:
            self.peak_usage_days = []


@dataclass
class CallDecision:
    """Smart decision making for API calls"""

    should_call: bool
    reason: str
    estimated_cost: float
    priority_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    budget_impact: float
    alternative_action: str = ""


class ABotFinancialIntelligence:
    """
    LUKHAS AI ΛBot's Autonomous Financial Management System'
    Smart, self-optimizing, budget-conscious AI financial decisions
    """

    def __init__(self, metrics_file: str = "LUKHAS AI ΛBot/config/abot_financial_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        self._refresh_daily_budget()

    def _load_metrics(self) -> FinancialMetrics:
        """Load financial metrics and intelligence data"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file) as f:
                    data = json.load(f)
                return FinancialMetrics(**data)
            else:
                return FinancialMetrics()
        except Exception as e:
            logger.warning(f"Could not load financial metrics: {e}")
            return FinancialMetrics()

    def _save_metrics(self):
        """Save financial metrics"""
        try:
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, "w") as f:
                json.dump(asdict(self.metrics), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save financial metrics: {e}")

    def _refresh_daily_budget(self):
        """Refresh daily budget and accumulate unused funds"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if self.metrics.last_budget_refresh != today:
            # Calculate days since last refresh
            if self.metrics.last_budget_refresh:
                last_date = datetime.strptime(self.metrics.last_budget_refresh, "%Y-%m-%d")
                days_passed = (datetime.now(timezone.utc) - last_date).days
            else:
                days_passed = 1

            # Add accumulated budget for missed days
            budget_to_add = self.metrics.daily_budget * days_passed

            # Add to current balance (accumulation!)
            self.metrics.current_balance += budget_to_add
            self.metrics.total_accumulated += budget_to_add
            self.metrics.last_budget_refresh = today

            # Reset daily counters
            self.metrics.today_spent = 0.0
            self.metrics.calls_today = 0

            # Conservation tracking
            if days_passed > 1:
                self.metrics.days_without_calls += days_passed - 1
                self.metrics.conservation_streak += days_passed - 1
                saved_money = self.metrics.daily_budget * (days_passed - 1)
                self.metrics.money_saved_by_conservation += saved_money

                logger.info(f"💰 Budget accumulated: ${budget_to_add:.4f} over {days_passed} days")
                logger.info(f"💚 Conserved: ${saved_money:.4f} by not making unnecessary calls")

            self._save_metrics()

    def analyze_call_necessity(self, context: dict) -> CallDecision:
        """
        LUKHAS AI ΛBot's intelligent decision making: Should we make this API call?'
        Analyzes necessity, cost-benefit, and alternatives
        """

        # Extract context information
        change_detected = context.get("change_detected", False)
        error_detected = context.get("error_detected", False)
        user_request = context.get("user_request", False)
        urgency_level = context.get("urgency", "MEDIUM")
        estimated_cost = context.get("estimated_cost", 0.001)
        context.get("alternative_available", False)

        # Decision logic
        priority_level = "LOW"
        should_call = False
        reason = ""
        alternative_action = ""

        # Critical situations - always call
        if error_detected and urgency_level == "CRITICAL":
            should_call = True
            priority_level = "CRITICAL"
            reason = "Critical error detected - immediate intervention required"

        # User requests - usually call
        elif user_request:
            should_call = True
            priority_level = "HIGH"
            reason = "Direct user request - high priority"

        # Changes detected - call if budget allows
        elif change_detected:
            if self.metrics.current_balance >= estimated_cost:
                should_call = True
                priority_level = "MEDIUM"
                reason = "Changes detected - analysis beneficial"
            else:
                should_call = False
                priority_level = "MEDIUM"
                reason = "Changes detected but budget insufficient"
                alternative_action = "Queue for next budget refresh"

        # No changes - conserve budget
        else:
            should_call = False
            priority_level = "LOW"
            reason = "No changes detected - conserving budget intelligently"
            alternative_action = "Continue monitoring, save budget for critical needs"

            # Track conservation
            self.metrics.conservation_streak += 1

        # Flex budget override for accumulated funds
        if not should_call and self.metrics.current_balance > (self.metrics.daily_budget * 5):
            # If we have 5+ days of budget, be more flexible
            if change_detected or (urgency_level in ["HIGH", "CRITICAL"]):
                should_call = True
                reason += " [FLEX BUDGET OVERRIDE: Sufficient accumulated funds]"
                self.metrics.flex_budget_used += estimated_cost

        # Budget impact calculation
        budget_impact = (
            (estimated_cost / self.metrics.current_balance) * 100 if self.metrics.current_balance > 0 else 100
        )

        return CallDecision(
            should_call=should_call,
            reason=reason,
            estimated_cost=estimated_cost,
            priority_level=priority_level,
            budget_impact=budget_impact,
            alternative_action=alternative_action,
        )

    def record_api_call(self, cost: float, reason: str, success: bool = True):
        """Record an API call and update financial metrics"""
        self.metrics.today_spent += cost
        self.metrics.month_spent += cost
        self.metrics.total_spent += cost
        self.metrics.current_balance -= cost

        self.metrics.calls_today += 1
        self.metrics.calls_month += 1
        self.metrics.total_calls += 1

        self.metrics.last_call_reason = reason

        # Reset conservation streak
        self.metrics.conservation_streak = 0

        # Update efficiency score
        self._update_efficiency_score()

        self._save_metrics()

        logger.info(f"💸 API Call recorded: ${cost:.4f} - {reason}")
        logger.info(f"💰 Remaining balance: ${self.metrics.current_balance:.4f}")

    def _update_efficiency_score(self):
        """Calculate LUKHAS AI ΛBot's financial efficiency score"""
        if self.metrics.total_calls == 0:
            self.metrics.efficiency_score = 100.0
            return

        # Base efficiency on money saved vs spent
        total_budget_available = self.metrics.total_accumulated
        money_saved_ratio = (
            self.metrics.money_saved_by_conservation / total_budget_available if total_budget_available > 0 else 0
        )

        # Efficiency factors
        conservation_bonus = min(self.metrics.conservation_streak * 2, 20)  # Max 20 points for conservation
        flex_budget_penalty = (
            (self.metrics.flex_budget_used / total_budget_available) * 10 if total_budget_available > 0 else 0
        )

        # Calculate score (0-100)
        base_score = 50
        savings_score = money_saved_ratio * 30  # Up to 30 points for savings
        conservation_score = conservation_bonus  # Up to 20 points for conservation
        penalty = min(flex_budget_penalty, 10)  # Max 10 point penalty

        self.metrics.efficiency_score = min(100, max(0, base_score + savings_score + conservation_score - penalty))

    def get_financial_report(self) -> dict:
        """Generate comprehensive financial report for Notion sync"""
        self._refresh_daily_budget()

        # Calculate projections
        daily_average = self.metrics.month_spent / max(datetime.now(timezone.utc).day, 1)
        monthly_projection = daily_average * 30
        days_remaining_at_current_rate = (
            self.metrics.current_balance / daily_average if daily_average > 0 else float("inf")
        )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "budget_status": {
                "current_balance": self.metrics.current_balance,
                "daily_budget": self.metrics.daily_budget,
                "total_accumulated": self.metrics.total_accumulated,
                "days_of_budget_remaining": days_remaining_at_current_rate,
            },
            "spending_analysis": {
                "today_spent": self.metrics.today_spent,
                "month_spent": self.metrics.month_spent,
                "total_spent": self.metrics.total_spent,
                "daily_average": daily_average,
                "monthly_projection": monthly_projection,
            },
            "intelligence_metrics": {
                "efficiency_score": self.metrics.efficiency_score,
                "money_saved_by_conservation": self.metrics.money_saved_by_conservation,
                "conservation_streak": self.metrics.conservation_streak,
                "days_without_calls": self.metrics.days_without_calls,
                "flex_budget_used": self.metrics.flex_budget_used,
            },
            "usage_patterns": {
                "calls_today": self.metrics.calls_today,
                "calls_month": self.metrics.calls_month,
                "total_calls": self.metrics.total_calls,
                "last_call_reason": self.metrics.last_call_reason,
                "peak_usage_days": self.metrics.peak_usage_days,
            },
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[str]:
        """LUKHAS AI ΛBot's financial recommendations"""
        recommendations = []

        if self.metrics.efficiency_score > 90:
            recommendations.append("🌟 Excellent financial management! Keep up the intelligent conservation.")
        elif self.metrics.efficiency_score > 70:
            recommendations.append("👍 Good budget discipline. Consider optimizing call frequency.")
        else:
            recommendations.append("⚠️ Review calling patterns. Too much budget usage detected.")

        if self.metrics.current_balance > (self.metrics.daily_budget * 10):
            recommendations.append(
                "💰 High budget accumulation. Consider upgrading to better models for enhanced performance."
            )

        if self.metrics.conservation_streak > 7:
            recommendations.append("💚 Outstanding conservation streak! Budget is building nicely.")

        if self.metrics.flex_budget_used > (self.metrics.daily_budget * 3):
            recommendations.append("🔄 High flex budget usage. Monitor necessity of overrides.")

        return recommendations


# Global financial intelligence instance
abot_financial_intelligence = ABotFinancialIntelligence()


def should_make_api_call(context: dict) -> CallDecision:
    """Quick function to check if LUKHAS AI ΛBot should make an API call"""
    return abot_financial_intelligence.analyze_call_necessity(context)


def record_smart_api_call(cost: float, reason: str, success: bool = True):
    """Record an API call in LUKHAS AI ΛBot's financial intelligence system"""
    abot_financial_intelligence.record_api_call(cost, reason, success)


def get_abot_financial_report() -> dict:
    """Get LUKHAS AI ΛBot's financial intelligence report for Notion sync"""
    return abot_financial_intelligence.get_financial_report()


if __name__ == "__main__":
    # Test the financial intelligence
    fi = ABotFinancialIntelligence()

    # Show current status
    report = fi.get_financial_report()
    print("💰 LUKHAS AI ΛBot Financial Intelligence Report:")
    print(f"   Current Balance: ${report['budget_status']['current_balance']:.4f}")
    print(f"   Efficiency Score: {report['intelligence_metrics']['efficiency_score']:.1f}%")
    print(f"   Money Saved: ${report['intelligence_metrics']['money_saved_by_conservation']:.4f}")
    print(f"   Conservation Streak: {report['intelligence_metrics']['conservation_streak']} decisions")

    # Test decision making
    test_context = {
        "change_detected": True,
        "user_request": False,
        "urgency": "MEDIUM",
        "estimated_cost": 0.001,
    }

    decision = fi.analyze_call_necessity(test_context)
    print("\n🧠 Decision Analysis:")
    print(f"   Should Call: {decision.should_call}")
    print(f"   Reason: {decision.reason}")
    print(f"   Priority: {decision.priority_level}")
    print(f"   Budget Impact: {decision.budget_impact:.1f}%")

    if decision.alternative_action:
        print(f"   Alternative: {decision.alternative_action}")
