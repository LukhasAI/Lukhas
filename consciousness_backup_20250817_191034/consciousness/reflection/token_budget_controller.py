import logging

#!/usr/bin/env python3
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


ΛBot Token Budget Controller
===========================
Advanced budget management and API cost control system for ΛBot autonomous operations.
Based on the original ABot financial intelligence core with Python implementation.

Features:
- Daily budget limits with accumulation
- Intelligent API call decision making
- Conservation streak tracking
- Flex budget for critical operations
- Efficiency scoring system
- Financial health monitoring

Created: 2025-06-30
Status: PRODUCTION BUDGET CONTROLLER ✅
"""

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class BudgetPriority(Enum):
    """Priority levels for API calls"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CallUrgency(Enum):
    """Urgency levels for API operations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class APICallContext:
    """Context for analyzing API call necessity"""

    change_detected: bool = False
    error_detected: bool = False
    user_request: bool = False
    urgency: CallUrgency = CallUrgency.LOW
    estimated_cost: float = 0.001  # Default cost estimate
    alternative_available: bool = False
    description: str = ""


@dataclass
class BudgetDecision:
    """Decision result from budget analysis"""

    should_call: bool
    reason: str
    priority: BudgetPriority
    budget_impact: float
    alternative_action: str = ""
    confidence: float = 0.5
    estimated_cost: float = 0.0
    flex_budget_used: bool = False
    conservation_recommendation: str = ""


class TokenBudgetController:
    """
    Advanced token budget controller for ΛBot autonomous operations
    Implements intelligent API call decision making with cost optimization
    """

    def __init__(self, config_path: str = "/Users/A_G_I/Lukhas"):
        self.config_path = config_path
        self.state_file = os.path.join(config_path, "token_budget_state.json")

        # Original ABot financial intelligence core settings with ΛBot enhancements
        self.DAILY_BUDGET_LIMIT = 0.10  # $0.10 per day (strict after initial period)
        self.INITIAL_ALLOWANCE = 0.50  # $0.50 for first two days
        self.INITIAL_PERIOD_DAYS = 2  # Initial allowance period
        self.MAX_ACCUMULATED_CREDITS = (
            2.00  # $2.00 max accumulated (increased for emergency uses)
        )
        self.CONSERVATIVE_THRESHOLD = 0.05  # $0.05 warning threshold
        self.CRITICAL_THRESHOLD = 0.08  # $0.08 critical threshold
        self.FLEX_BUDGET_MULTIPLIER = 5.0  # 5 days worth of budget for flex override

        # Current state
        self.usage = []
        self.alerts = []
        self.monthly_spend = 0.0
        self.daily_spend = 0.0
        self.accumulated_credits = 0.0
        self.last_reset_date = datetime.now()
        self.last_daily_reset = datetime.now()
        self.first_run_date = datetime.now()  # Track when ΛBot first started
        self.is_initial_period = True  # Whether we're in the initial allowance period

        # Call logging for findings and recommendations
        self.call_log = []  # Detailed log of all API calls and decisions
        self.findings_log = []  # Log of findings from API calls
        self.recommendations_applied = []  # Track which recommendations were applied

        # ABot financial intelligence metrics
        self.conservation_streak = 0
        self.total_calls = 0
        self.total_calls_cost = 0.0
        self.money_saved_by_conservation = 0.0
        self.flex_budget_used = 0.0
        self.efficiency_score = 100.0
        self.peak_usage_days = []
        self.last_call_reason = ""

        # Rate limiting and CPU management
        self.last_api_call = 0.0
        self.min_call_interval = 1.0  # Minimum 1 second between calls
        self.call_count_window = []  # Track calls in sliding window
        self.max_calls_per_minute = 20

        # Initialize logging
        self.logger = logging.getLogger("TokenBudgetController")

        # Load existing state
        self.load_state()

        # Check for daily reset
        self.check_daily_reset()

    def load_state(self) -> None:
        """Load budget state from disk"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file) as f:
                    state = json.load(f)

                self.daily_spend = state.get("daily_spend", 0.0)
                self.monthly_spend = state.get("monthly_spend", 0.0)
                self.accumulated_credits = state.get("accumulated_credits", 0.0)
                self.conservation_streak = state.get("conservation_streak", 0)
                self.total_calls = state.get("total_calls", 0)
                self.total_calls_cost = state.get("total_calls_cost", 0.0)
                self.money_saved_by_conservation = state.get(
                    "money_saved_by_conservation", 0.0
                )
                self.flex_budget_used = state.get("flex_budget_used", 0.0)
                self.efficiency_score = state.get("efficiency_score", 100.0)
                self.peak_usage_days = state.get("peak_usage_days", [])
                self.last_call_reason = state.get("last_call_reason", "")

                # New ΛBot specific fields
                self.is_initial_period = state.get("is_initial_period", True)
                self.call_log = state.get("call_log", [])
                self.findings_log = state.get("findings_log", [])
                self.recommendations_applied = state.get("recommendations_applied", [])

                # Parse dates
                if "last_reset_date" in state:
                    self.last_reset_date = datetime.fromisoformat(
                        state["last_reset_date"]
                    )
                if "last_daily_reset" in state:
                    self.last_daily_reset = datetime.fromisoformat(
                        state["last_daily_reset"]
                    )
                if "first_run_date" in state:
                    self.first_run_date = datetime.fromisoformat(
                        state["first_run_date"]
                    )
                else:
                    self.first_run_date = (
                        datetime.now()
                    )  # Default for existing installations

                self.logger.info("Budget state loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load budget state: {e}")

    def save_state(self) -> None:
        """Save budget state to disk"""
        try:
            state = {
                "daily_spend": self.daily_spend,
                "monthly_spend": self.monthly_spend,
                "accumulated_credits": self.accumulated_credits,
                "conservation_streak": self.conservation_streak,
                "total_calls": self.total_calls,
                "total_calls_cost": self.total_calls_cost,
                "money_saved_by_conservation": self.money_saved_by_conservation,
                "flex_budget_used": self.flex_budget_used,
                "efficiency_score": self.efficiency_score,
                "peak_usage_days": self.peak_usage_days,
                "last_call_reason": self.last_call_reason,
                "is_initial_period": self.is_initial_period,
                "call_log": self.call_log[-100:],  # Keep last 100 call logs
                "findings_log": self.findings_log[-50:],  # Keep last 50 findings
                "recommendations_applied": self.recommendations_applied[
                    -50:
                ],  # Keep last 50 recommendations
                "first_run_date": self.first_run_date.isoformat(),
                "last_reset_date": self.last_reset_date.isoformat(),
                "last_daily_reset": self.last_daily_reset.isoformat(),
                "timestamp": datetime.now().isoformat(),
            }

            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save budget state: {e}")

    def check_daily_reset(self) -> None:
        """Daily budget reset with initial allowance logic for ΛBot"""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        last_reset_str = self.last_daily_reset.strftime("%Y-%m-%d")

        if today_str != last_reset_str:
            # Calculate days passed and days since first run
            days_passed = (now.date() - self.last_daily_reset.date()).days
            days_since_first_run = (now.date() - self.first_run_date.date()).days

            # Determine budget allocation based on initial period
            if (
                self.is_initial_period
                and days_since_first_run < self.INITIAL_PERIOD_DAYS
            ):
                # In initial period: $0.50 total allowance for first 2 days
                remaining_initial_days = self.INITIAL_PERIOD_DAYS - days_since_first_run
                daily_budget = self.INITIAL_ALLOWANCE / max(remaining_initial_days, 1)
                budget_to_add = min(
                    daily_budget * days_passed,
                    self.INITIAL_ALLOWANCE - self.daily_spend,
                )

                self.logger.info(
                    f"💰 ΛBot Initial Period: Day {days_since_first_run + 1} of {self.INITIAL_PERIOD_DAYS}"
                )
                self.logger.info(
                    f"💰 Initial allowance budget: ${budget_to_add:.4f} added"
                )

            elif (
                self.is_initial_period
                and days_since_first_run >= self.INITIAL_PERIOD_DAYS
            ):
                # Transition from initial period to strict daily budget
                self.is_initial_period = False
                budget_to_add = self.DAILY_BUDGET_LIMIT * days_passed

                self.logger.info(
                    f"💰 ΛBot transitioned to strict daily budget: ${self.DAILY_BUDGET_LIMIT}/day"
                )
                self.logger.info(
                    f"💰 Daily budget allocation: ${budget_to_add:.4f} for {days_passed} days"
                )

            else:
                # Normal operation: strict $0.10/day, unused accumulates
                unused_budget = max(0, self.DAILY_BUDGET_LIMIT - self.daily_spend)
                budget_to_add = unused_budget + (
                    self.DAILY_BUDGET_LIMIT * (days_passed - 1)
                )

                self.logger.info(
                    f"💰 ΛBot Daily Budget: ${unused_budget:.4f} unused + ${self.DAILY_BUDGET_LIMIT * (days_passed - 1):.4f} new"
                )

            # Add to accumulated credits (capped at MAX_ACCUMULATED_CREDITS)
            self.accumulated_credits = min(
                self.accumulated_credits + budget_to_add, self.MAX_ACCUMULATED_CREDITS
            )

            # Reset daily spend
            self.daily_spend = 0.0
            self.last_daily_reset = now

            # Track conservation if no calls were made
            if days_passed > 1:
                conservation_amount = (
                    self.DAILY_BUDGET_LIMIT * (days_passed - 1)
                    if not self.is_initial_period
                    else 0
                )
                self.track_conservation(days_passed - 1, conservation_amount)

            self.logger.info(
                f"💰 Total accumulated credits: ${self.accumulated_credits:.4f}"
            )
            self.save_state()

    def track_conservation(self, days: int, saved_amount: float) -> None:
        """Track conservation metrics"""
        self.conservation_streak += days
        self.money_saved_by_conservation += saved_amount
        self.update_efficiency_score()

    def update_efficiency_score(self) -> None:
        """Original ABot's efficiency scoring system"""
        if len(self.usage) == 0:
            self.efficiency_score = 100.0
            return

        total_budget_available = self.accumulated_credits + (
            self.DAILY_BUDGET_LIMIT * 30
        )  # Rough monthly estimate
        money_saved_ratio = self.money_saved_by_conservation / max(
            total_budget_available, 1
        )

        # Efficiency factors from original ABot
        conservation_bonus = min(self.conservation_streak * 2, 20)  # Max 20 points
        flex_budget_penalty = min(
            (self.flex_budget_used / max(total_budget_available, 1)) * 10, 10
        )  # Max 10 point penalty

        # Calculate score (0-100)
        base_score = 50
        savings_score = money_saved_ratio * 30  # Up to 30 points for savings
        conservation_score = conservation_bonus  # Up to 20 points for conservation

        self.efficiency_score = min(
            100,
            max(
                0, base_score + savings_score + conservation_score - flex_budget_penalty
            ),
        )

    def can_use_flex_budget(self, cost: float) -> bool:
        """Check if flex budget can be used (when accumulated credits > 5 days of budget)"""
        flex_threshold = self.DAILY_BUDGET_LIMIT * self.FLEX_BUDGET_MULTIPLIER
        return (
            self.accumulated_credits >= flex_threshold
            and self.flex_budget_used + cost <= self.accumulated_credits * 0.5
        )  # Max 50% of accumulated

    def rate_limit_check(self) -> bool:
        """Check if we're hitting rate limits (CPU protection)"""
        now = time.time()

        # Check minimum interval between calls
        if now - self.last_api_call < self.min_call_interval:
            return False

        # Check calls per minute
        cutoff_time = now - 60  # 1 minute ago
        self.call_count_window = [t for t in self.call_count_window if t > cutoff_time]

        return not len(self.call_count_window) >= self.max_calls_per_minute

    def analyze_call_necessity(self, context: APICallContext) -> BudgetDecision:
        """
        ABot's Intelligent Decision Making: Should we make this API call?
        Analyzes necessity, cost-benefit, and alternatives based on original ABot logic
        """
        self.refresh_daily_budget()

        should_call = False
        priority = BudgetPriority.LOW
        reason = ""
        alternative_action = ""
        flex_budget_used = False
        confidence = 0.5
        conservation_recommendation = ""

        # Rate limiting check first (CPU protection)
        if not self.rate_limit_check():
            return BudgetDecision(
                should_call=False,
                reason="Rate limit exceeded - protecting system resources",
                priority=BudgetPriority.LOW,
                budget_impact=0.0,
                alternative_action="Wait for rate limit window to reset",
                confidence=0.95,
                estimated_cost=context.estimated_cost,
                conservation_recommendation="Rate limiting prevents CPU overload",
            )

        # ABot Decision Logic - Critical situations always call
        if context.error_detected and context.urgency == CallUrgency.CRITICAL:
            should_call = True
            priority = BudgetPriority.CRITICAL
            reason = "Critical error detected - immediate intervention required"
            confidence = 0.95

        # User requests - usually call
        elif context.user_request:
            should_call = True
            priority = BudgetPriority.HIGH
            reason = "Direct user request - high priority"
            confidence = 0.9

        # Changes detected - call if budget allows
        elif context.change_detected:
            if self.daily_spend + context.estimated_cost <= self.DAILY_BUDGET_LIMIT:
                should_call = True
                priority = BudgetPriority.MEDIUM
                reason = "Changes detected - analysis beneficial"
                confidence = 0.75
            elif self.accumulated_credits >= context.estimated_cost:
                should_call = True
                priority = BudgetPriority.MEDIUM
                reason = "Changes detected - using accumulated credits"
                confidence = 0.7
            elif self.can_use_flex_budget(context.estimated_cost):
                should_call = True
                priority = BudgetPriority.MEDIUM
                reason = "Changes detected - flex budget override"
                flex_budget_used = True
                confidence = 0.6
                self.flex_budget_used += context.estimated_cost
            else:
                should_call = False
                priority = BudgetPriority.MEDIUM
                reason = "Changes detected but budget insufficient"
                alternative_action = (
                    "Queue for next budget refresh or accumulate more credits"
                )
                confidence = 0.8
                conservation_recommendation = (
                    "Consider batching requests or using local analysis"
                )

        # No changes - conserve budget intelligently
        else:
            should_call = False
            priority = BudgetPriority.LOW
            reason = "No significant changes detected - conserving budget"
            alternative_action = "Monitor for changes or wait for user request"
            confidence = 0.9
            conservation_recommendation = (
                "Budget conservation extends available credits"
            )

            # Track conservation
            self.conservation_streak += 1
            self.money_saved_by_conservation += context.estimated_cost

        # Override for urgent situations with flex budget
        if (
            not should_call
            and context.urgency == CallUrgency.HIGH
            and self.can_use_flex_budget(context.estimated_cost)
        ):
            should_call = True
            priority = BudgetPriority.HIGH
            reason = "High urgency - flex budget override approved"
            flex_budget_used = True
            self.flex_budget_used += context.estimated_cost
            confidence = 0.65

        # Record this decision
        self.last_call_reason = reason
        if not should_call:
            self.conservation_streak += 1
        else:
            self.conservation_streak = 0
            # Record API call timing for rate limiting
            now = time.time()
            self.last_api_call = now
            self.call_count_window.append(now)

        # Update efficiency metrics
        self.update_efficiency_score()

        decision = BudgetDecision(
            should_call=should_call,
            reason=reason,
            priority=priority,
            budget_impact=context.estimated_cost,
            alternative_action=alternative_action,
            confidence=confidence,
            estimated_cost=context.estimated_cost,
            flex_budget_used=flex_budget_used,
            conservation_recommendation=conservation_recommendation,
        )

        # Save state after decision
        self.save_state()

        return decision

    def record_api_call(
        self,
        cost: float,
        success: bool = True,
        description: str = "",
        findings: list[str] = None,
        recommendations: list[str] = None,
    ) -> None:
        """
        Record an actual API call with comprehensive logging

        Args:
            cost: Cost of the API call
            success: Whether the call was successful
            description: Description of the call
            findings: List of findings from the API call
            recommendations: List of recommendations from the API call
        """
        timestamp = datetime.now()

        if success:
            self.daily_spend += cost
            self.monthly_spend += cost
            self.total_calls += 1
            self.total_calls_cost += cost

            # Add to usage tracking
            self.usage.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "cost": cost,
                    "description": description,
                    "success": success,
                }
            )

            # Keep only last 100 usage records
            if len(self.usage) > 100:
                self.usage = self.usage[-100:]

            self.logger.info(f"💰 API call recorded: ${cost:.4f} - {description}")

        # Comprehensive call logging
        call_log_entry = {
            "timestamp": timestamp.isoformat(),
            "cost": cost,
            "success": success,
            "description": description,
            "daily_spend_after": self.daily_spend,
            "accumulated_credits_after": self.accumulated_credits,
            "findings": findings or [],
            "recommendations": recommendations or [],
        }

        self.call_log.append(call_log_entry)

        # Log findings separately for easy analysis
        if findings:
            for finding in findings:
                self.findings_log.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "finding": finding,
                        "source_call": description,
                        "cost": cost,
                    }
                )
                self.logger.info(f"🔍 Finding logged: {finding}")

        # Log recommendations for tracking application
        if recommendations:
            for recommendation in recommendations:
                rec_entry = {
                    "timestamp": timestamp.isoformat(),
                    "recommendation": recommendation,
                    "source_call": description,
                    "cost": cost,
                    "applied": False,  # Will be updated when applied
                    "applied_timestamp": None,
                }
                self.recommendations_applied.append(rec_entry)
                self.logger.info(f"📋 Recommendation logged: {recommendation}")

        # Keep logs manageable
        if len(self.call_log) > 1000:
            self.call_log = self.call_log[-1000:]
        if len(self.findings_log) > 500:
            self.findings_log = self.findings_log[-500:]
        if len(self.recommendations_applied) > 500:
            self.recommendations_applied = self.recommendations_applied[-500:]

        self.save_state()

    def mark_recommendation_applied(
        self, recommendation: str, details: str = ""
    ) -> None:
        """Mark a recommendation as applied"""
        for i, rec in enumerate(self.recommendations_applied):
            if not rec["applied"] and recommendation in rec["recommendation"]:
                self.recommendations_applied[i]["applied"] = True
                self.recommendations_applied[i][
                    "applied_timestamp"
                ] = datetime.now().isoformat()
                self.recommendations_applied[i]["application_details"] = details
                self.logger.info(f"✅ Recommendation applied: {recommendation}")
                break
        self.save_state()

    def refresh_daily_budget(self) -> None:
        """Original ABot daily budget refresh with accumulation"""
        now = datetime.now()
        days_since_reset = (now - self.last_daily_reset).days

        if days_since_reset >= 1:
            # Calculate unused budget from previous day(s)
            unused_budget = max(0, self.DAILY_BUDGET_LIMIT - self.daily_spend)

            # Add to accumulated credits (capped at MAX_ACCUMULATED_CREDITS)
            self.accumulated_credits = min(
                self.MAX_ACCUMULATED_CREDITS,
                self.accumulated_credits + (unused_budget * days_since_reset),
            )

            # Reset daily spend
            self.daily_spend = 0.0
            self.last_daily_reset = now

            # Track peak usage days
            if self.daily_spend >= self.CRITICAL_THRESHOLD:
                date_str = now.strftime("%Y-%m-%d")
                if date_str not in self.peak_usage_days:
                    self.peak_usage_days.append(date_str)

            self.logger.info(
                f"ΛBot Budget Reset: Daily={self.DAILY_BUDGET_LIMIT}, Accumulated={self.accumulated_credits:.3f}"
            )

    def get_financial_intelligence_report(self) -> dict[str, Any]:
        """Get comprehensive financial intelligence report with ΛBot enhancements"""
        self.refresh_daily_budget()

        # Determine current budget limit (initial period vs strict daily)
        current_daily_limit = self.DAILY_BUDGET_LIMIT
        if self.is_initial_period:
            days_since_first_run = (
                datetime.now().date() - self.first_run_date.date()
            ).days
            if days_since_first_run < self.INITIAL_PERIOD_DAYS:
                remaining_days = self.INITIAL_PERIOD_DAYS - days_since_first_run
                current_daily_limit = self.INITIAL_ALLOWANCE / max(remaining_days, 1)

        daily_usage_percentage = (self.daily_spend / current_daily_limit) * 100
        flex_budget_threshold = self.DAILY_BUDGET_LIMIT * self.FLEX_BUDGET_MULTIPLIER

        recommendations = []
        warnings = []

        # Generate recommendations based on ABot intelligence
        if self.conservation_streak > 3:
            recommendations.append(
                f"Excellent conservation streak! {self.conservation_streak} smart decisions saved ${self.money_saved_by_conservation:.3f}"
            )

        if self.accumulated_credits >= flex_budget_threshold:
            recommendations.append(
                "Flex budget available - can handle high-priority requests beyond daily limit"
            )

        if daily_usage_percentage > 80:
            warnings.append(
                "Approaching daily budget limit - consider conservative mode"
            )

        if self.efficiency_score < 70:
            recommendations.append(
                "Efficiency score low - review recent API call patterns"
            )

        # Check rate limiting status
        rate_limit_ok = self.rate_limit_check()
        if not rate_limit_ok:
            warnings.append("Rate limiting active - protecting CPU resources")

        # ΛBot specific recommendations based on findings
        recent_findings = [f["finding"] for f in self.findings_log[-10:]]
        pending_recommendations = [
            r for r in self.recommendations_applied[-10:] if not r["applied"]
        ]

        if len(pending_recommendations) > 5:
            warnings.append(
                f"{len(pending_recommendations)} recommendations pending application"
            )

        if len(recent_findings) > 0:
            recommendations.append(
                f"Recent findings available: {len(recent_findings)} items for review"
            )

        # Determine overall financial health
        overall_health = "good"
        if self.efficiency_score >= 85 and self.conservation_streak >= 2:
            overall_health = "excellent"
        elif daily_usage_percentage > 90 or self.efficiency_score < 60:
            overall_health = "concerning"
        elif daily_usage_percentage > 100:
            overall_health = "critical"

        return {
            "budget_status": {
                "current_daily_limit": current_daily_limit,
                "is_initial_period": self.is_initial_period,
                "days_since_first_run": (
                    datetime.now().date() - self.first_run_date.date()
                ).days,
                "used_today": self.daily_spend,
                "remaining_today": max(0, current_daily_limit - self.daily_spend),
                "percentage_used": daily_usage_percentage,
            },
            "accumulated_credits": self.accumulated_credits,
            "conservation_metrics": {
                "streak": self.conservation_streak,
                "total_saved": self.money_saved_by_conservation,
                "last_decision": self.last_call_reason,
                "efficiency": self.efficiency_score,
            },
            "call_tracking": {
                "total_calls_logged": len(self.call_log),
                "recent_findings": len(
                    [
                        f
                        for f in self.findings_log
                        if (
                            datetime.now() - datetime.fromisoformat(f["timestamp"])
                        ).days
                        < 1
                    ]
                ),
                "pending_recommendations": len(pending_recommendations),
                "applied_recommendations": len(
                    [r for r in self.recommendations_applied if r["applied"]]
                ),
            },
            "recommendations": recommendations,
            "warnings": warnings,
            "flex_budget_status": {
                "available": self.accumulated_credits >= flex_budget_threshold,
                "used": self.flex_budget_used,
                "threshold": flex_budget_threshold,
            },
            "rate_limiting": {
                "calls_per_minute": len(self.call_count_window),
                "max_calls_per_minute": self.max_calls_per_minute,
                "status": "ok" if rate_limit_ok else "limited",
            },
            "overall_financial_health": overall_health,
            "total_calls": self.total_calls,
            "total_cost": self.total_calls_cost,
            "recent_findings": recent_findings[-5:],  # Last 5 findings
            "pending_recommendations": [
                r["recommendation"] for r in pending_recommendations[-5:]
            ],  # Last 5 pending
        }


def main():
    """Test the budget controller"""
    controller = TokenBudgetController()

    # Test scenarios
    print("🤖 ΛBot Token Budget Controller Test")
    print("=" * 50)

    # Test 1: User request
    context = APICallContext(
        user_request=True,
        urgency=CallUrgency.HIGH,
        estimated_cost=0.02,
        description="User requested code analysis",
    )

    decision = controller.analyze_call_necessity(context)
    print(f"User Request Decision: {decision.should_call} - {decision.reason}")

    # Test 2: Change detected
    context = APICallContext(
        change_detected=True,
        urgency=CallUrgency.MEDIUM,
        estimated_cost=0.01,
        description="Code changes detected",
    )

    decision = controller.analyze_call_necessity(context)
    print(f"Change Detection Decision: {decision.should_call} - {decision.reason}")

    # Financial report
    report = controller.get_financial_intelligence_report()
    print("\n📊 Financial Intelligence Report:")
    print(
        f"Daily Budget: ${report['daily_budget_status']['used']:.3f} / ${controller.DAILY_BUDGET_LIMIT}"
    )
    print(f"Efficiency Score: {report['conservation_metrics']['efficiency']:.1f}")
    print(f"Conservation Streak: {report['conservation_metrics']['streak']}")
    print(f"Overall Health: {report['overall_financial_health']}")


if __name__ == "__main__":
    main()
