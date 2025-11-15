"""
╔══════════════════════════════════════════════════════════════
║ 📊 GUARDIAN Compliance Analytics & Reporting
║ Part of LUKHAS AI Guardian System
╠══════════════════════════════════════════════════════════════
║ TYPE: ANALYTICS_SYSTEM
║ ROLE: Advanced compliance analytics and trend analysis
║ PURPOSE: Compliance metrics visualization and reporting
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Identity compliance tracking
║ 🧠 CONSCIOUSNESS: Ethical decision analysis
║ 🛡️ GUARDIAN: Compliance enforcement analytics
╚══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ComplianceTrend:
    """Compliance trend analysis over time"""

    trend_id: str
    metric_name: str
    time_period_days: int
    
    # Trend data
    current_value: float = 0.0
    previous_value: float = 0.0
    change_percentage: float = 0.0
    trend_direction: str = "stable"  # "improving", "declining", "stable"
    
    # Time series data
    daily_values: list[tuple[datetime, float]] = field(default_factory=list)
    
    # Analysis
    volatility: float = 0.0
    confidence_level: float = 0.0


@dataclass
class ComplianceMetricsSummary:
    """Summary of compliance metrics across all dimensions"""

    summary_id: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Overall metrics
    total_operations: int = 0
    compliance_rate: float = 0.0
    average_constitutional_score: float = 0.0
    
    # By status
    compliant_count: int = 0
    review_required_count: int = 0
    non_compliant_count: int = 0
    emergency_override_count: int = 0
    
    # By category
    category_breakdown: dict[str, dict[str, Any]] = field(default_factory=dict)
    
    # By principle
    principle_compliance_rates: dict[str, float] = field(default_factory=dict)
    
    # Trends
    compliance_trends: list[ComplianceTrend] = field(default_factory=list)
    
    # Alerts
    critical_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class GuardianComplianceAnalytics:
    """
    Guardian Compliance Analytics System
    
    Provides advanced analytics, trend analysis, and visualization support
    for Guardian constitutional compliance data.
    """

    def __init__(self, compliance_system):
        """
        Initialize analytics system
        
        Args:
            compliance_system: GuardianConstitutionalCompliance instance to analyze
        """
        self.compliance_system = compliance_system
        self.analytics_cache = {}
        self.cache_ttl = timedelta(minutes=5)
        
        logger.info("📊 Guardian Compliance Analytics initialized")

    async def generate_metrics_summary(
        self,
        time_period_days: int = 7,
        include_trends: bool = True
    ) -> ComplianceMetricsSummary:
        """
        Generate comprehensive compliance metrics summary
        
        Args:
            time_period_days: Number of days to analyze
            include_trends: Whether to include trend analysis
            
        Returns:
            ComplianceMetricsSummary with detailed metrics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_period_days)
        
        # Filter checks within time period
        period_checks = [
            check for check in self.compliance_system.compliance_checks
            if check.validation_timestamp >= cutoff_date
        ]
        
        summary = ComplianceMetricsSummary(
            summary_id=f"summary-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            total_operations=len(period_checks),
        )
        
        if not period_checks:
            logger.warning("⚠️ No compliance checks in specified time period")
            return summary
        
        # Calculate status counts
        from guardian.constitutional_compliance import ComplianceStatus
        
        for check in period_checks:
            if check.compliance_status == ComplianceStatus.COMPLIANT:
                summary.compliant_count += 1
            elif check.compliance_status == ComplianceStatus.REVIEW_REQUIRED:
                summary.review_required_count += 1
            elif check.compliance_status == ComplianceStatus.NON_COMPLIANT:
                summary.non_compliant_count += 1
            elif check.compliance_status == ComplianceStatus.EMERGENCY_OVERRIDE:
                summary.emergency_override_count += 1
        
        # Calculate compliance rate
        summary.compliance_rate = summary.compliant_count / len(period_checks)
        
        # Calculate average constitutional score
        summary.average_constitutional_score = sum(
            check.constitutional_score for check in period_checks
        ) / len(period_checks)
        
        # Category breakdown
        category_stats = defaultdict(lambda: {
            "count": 0,
            "compliant": 0,
            "avg_score": 0.0,
            "scores": []
        })
        
        for check in period_checks:
            cat = check.decision_category.value
            category_stats[cat]["count"] += 1
            category_stats[cat]["scores"].append(check.constitutional_score)
            if check.compliance_status == ComplianceStatus.COMPLIANT:
                category_stats[cat]["compliant"] += 1
        
        for cat, stats in category_stats.items():
            stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"])
            stats["compliance_rate"] = stats["compliant"] / stats["count"]
            del stats["scores"]  # Don't need raw scores in summary
            summary.category_breakdown[cat] = stats
        
        # Principle compliance rates
        principle_compliance = defaultdict(lambda: {"total": 0, "compliant": 0})
        
        for check in period_checks:
            for principle, compliant in check.principles_validated.items():
                principle_compliance[principle]["total"] += 1
                if compliant:
                    principle_compliance[principle]["compliant"] += 1
        
        for principle, stats in principle_compliance.items():
            summary.principle_compliance_rates[principle] = (
                stats["compliant"] / stats["total"] if stats["total"] > 0 else 0.0
            )
        
        # Generate alerts and recommendations
        if summary.compliance_rate < 0.7:
            summary.critical_issues.append(
                f"Low compliance rate: {summary.compliance_rate:.1%}"
            )
            summary.recommendations.append(
                "Review and strengthen compliance processes to improve compliance rate"
            )
        
        if summary.non_compliant_count > len(period_checks) * 0.1:
            summary.warnings.append(
                f"High non-compliance rate: {summary.non_compliant_count} / {len(period_checks)}"
            )
        
        if summary.emergency_override_count > 0:
            summary.warnings.append(
                f"{summary.emergency_override_count} emergency overrides in period"
            )
            summary.recommendations.append(
                "Review emergency overrides for policy compliance"
            )
        
        # Low-performing principles
        for principle, rate in summary.principle_compliance_rates.items():
            if rate < 0.6:
                summary.critical_issues.append(
                    f"Low compliance for principle '{principle}': {rate:.1%}"
                )
                summary.recommendations.append(
                    f"Improve compliance processes for {principle}"
                )
        
        # Include trend analysis if requested
        if include_trends:
            trends = await self._calculate_compliance_trends(time_period_days)
            summary.compliance_trends = trends
        
        logger.info(
            f"📊 Generated metrics summary: {summary.total_operations} ops, "
            f"{summary.compliance_rate:.1%} compliance rate"
        )
        
        return summary

    async def _calculate_compliance_trends(self, days: int) -> list[ComplianceTrend]:
        """Calculate compliance trends over time period"""
        trends = []
        
        # Calculate daily compliance rates
        daily_rates = defaultdict(list)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        for check in self.compliance_system.compliance_checks:
            if check.validation_timestamp >= cutoff:
                date = check.validation_timestamp.date()
                from guardian.constitutional_compliance import ComplianceStatus
                is_compliant = 1.0 if check.compliance_status == ComplianceStatus.COMPLIANT else 0.0
                daily_rates[date].append(is_compliant)
        
        # Convert to time series
        time_series = []
        for date in sorted(daily_rates.keys()):
            avg_compliance = sum(daily_rates[date]) / len(daily_rates[date])
            dt = datetime.combine(date, datetime.min.time(), timezone.utc)
            time_series.append((dt, avg_compliance))
        
        if len(time_series) >= 2:
            # Calculate trend
            current_value = time_series[-1][1]
            previous_value = time_series[0][1]
            change = ((current_value - previous_value) / previous_value * 100) if previous_value > 0 else 0.0
            
            trend_direction = "stable"
            if change > 5:
                trend_direction = "improving"
            elif change < -5:
                trend_direction = "declining"
            
            # Calculate volatility (standard deviation)
            values = [v for _, v in time_series]
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            volatility = variance ** 0.5
            
            trend = ComplianceTrend(
                trend_id=f"trend-compliance-{days}d",
                metric_name="Compliance Rate",
                time_period_days=days,
                current_value=current_value,
                previous_value=previous_value,
                change_percentage=change,
                trend_direction=trend_direction,
                daily_values=time_series,
                volatility=volatility,
                confidence_level=0.8 if len(time_series) >= 7 else 0.5,
            )
            
            trends.append(trend)
        
        return trends

    async def get_identity_compliance_profile(self, identity_id: str) -> dict[str, Any]:
        """
        Get detailed compliance profile for a specific identity
        
        Args:
            identity_id: Identity to analyze
            
        Returns:
            Dictionary with identity compliance profile
        """
        checks = self.compliance_system.checks_by_identity.get(identity_id, [])
        
        if not checks:
            return {
                "identity_id": identity_id,
                "total_operations": 0,
                "message": "No compliance checks found for this identity"
            }
        
        from guardian.constitutional_compliance import ComplianceStatus
        
        profile = {
            "identity_id": identity_id,
            "total_operations": len(checks),
            "first_operation": checks[0].validation_timestamp.isoformat(),
            "last_operation": checks[-1].validation_timestamp.isoformat(),
            "compliance_status_breakdown": {
                "compliant": sum(1 for c in checks if c.compliance_status == ComplianceStatus.COMPLIANT),
                "review_required": sum(1 for c in checks if c.compliance_status == ComplianceStatus.REVIEW_REQUIRED),
                "non_compliant": sum(1 for c in checks if c.compliance_status == ComplianceStatus.NON_COMPLIANT),
                "emergency_override": sum(1 for c in checks if c.compliance_status == ComplianceStatus.EMERGENCY_OVERRIDE),
            },
            "average_constitutional_score": sum(c.constitutional_score for c in checks) / len(checks),
            "oversight_required_count": sum(1 for c in checks if c.oversight_required),
            "emergency_operations": sum(1 for c in checks if c.emergency_context),
        }
        
        # Category breakdown
        category_counts = defaultdict(int)
        for check in checks:
            category_counts[check.decision_category.value] += 1
        profile["operations_by_category"] = dict(category_counts)
        
        # Risk assessment
        compliance_rate = profile["compliance_status_breakdown"]["compliant"] / len(checks)
        
        if compliance_rate >= 0.9:
            profile["risk_level"] = "low"
        elif compliance_rate >= 0.7:
            profile["risk_level"] = "moderate"
        else:
            profile["risk_level"] = "high"
        
        profile["recommendations"] = []
        if compliance_rate < 0.7:
            profile["recommendations"].append("Review identity operations for compliance issues")
        if profile["oversight_required_count"] > len(checks) * 0.3:
            profile["recommendations"].append("High oversight requirement - consider additional training")
        
        return profile

    async def generate_compliance_dashboard_data(self) -> dict[str, Any]:
        """
        Generate data optimized for compliance dashboard visualization
        
        Returns:
            Dictionary with dashboard-ready compliance data
        """
        metrics = await self.compliance_system.get_compliance_metrics()
        summary = await self.generate_metrics_summary(time_period_days=7, include_trends=True)
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_checks = [
            c for c in self.compliance_system.compliance_checks
            if c.validation_timestamp >= recent_cutoff
        ]
        
        dashboard = {
            "overview": {
                "total_operations": metrics["system_metrics"]["total_checks"],
                "compliance_rate": metrics["compliance_rate"],
                "average_score": metrics["system_metrics"]["average_constitutional_score"],
                "oversight_rate": metrics["oversight_rate"],
            },
            "recent_24h": {
                "operations": len(recent_checks),
                "compliance_rate": (
                    sum(1 for c in recent_checks 
                        if c.compliance_status.value == "compliant") / len(recent_checks)
                    if recent_checks else 0.0
                ),
            },
            "weekly_summary": {
                "compliance_rate": summary.compliance_rate,
                "average_score": summary.average_constitutional_score,
                "category_breakdown": summary.category_breakdown,
                "principle_compliance": summary.principle_compliance_rates,
            },
            "trends": [
                {
                    "metric": t.metric_name,
                    "current": t.current_value,
                    "change": t.change_percentage,
                    "direction": t.trend_direction,
                }
                for t in summary.compliance_trends
            ],
            "alerts": {
                "critical": summary.critical_issues,
                "warnings": summary.warnings,
                "recommendations": summary.recommendations,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        return dashboard


__all__ = [
    "ComplianceTrend",
    "ComplianceMetricsSummary",
    "GuardianComplianceAnalytics",
]
