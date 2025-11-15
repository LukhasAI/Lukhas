"""
╔══════════════════════════════════════════════════════════════
║ 📊 GUARDIAN Compliance Analytics Test Suite
║ Part of LUKHAS AI Guardian System
╠══════════════════════════════════════════════════════════════
║ TYPE: TEST_SUITE
║ PURPOSE: Testing compliance analytics and reporting
╚══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import pytest

# Import analytics module
try:
    from guardian.compliance_analytics import (
        ComplianceMetricsSummary,
        ComplianceTrend,
        GuardianComplianceAnalytics,
    )
    from guardian.constitutional_compliance import (
        GuardianConstitutionalCompliance,
        GuardianDecisionCategory,
    )

    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

logger = logging.getLogger(__name__)


@pytest.fixture
def anyio_backend() -> str:
    """Restrict pytest-anyio to the asyncio backend for these tests."""
    return "asyncio"


class TestGuardianComplianceAnalytics:
    """Test suite for Guardian Compliance Analytics"""

    @pytest.fixture
    async def compliance_with_data(self):
        """Create compliance system with sample data"""
        if not ANALYTICS_AVAILABLE:
            pytest.skip("Analytics module not available")

        compliance = GuardianConstitutionalCompliance()
        await compliance.initialize_compliance_system()

        # Add sample compliance checks
        sample_operations = [
            {
                "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
                "user_consent": True,
                "data_minimization": True,
                "security_measures": ["encryption"],
                "reasoning": "Test operation",
            },
            {
                "decision_category": GuardianDecisionCategory.ACCESS_CONTROL,
                "user_consent": True,
                "decision_criteria": {"valid": True},
            },
            {
                "decision_category": GuardianDecisionCategory.DATA_GOVERNANCE,
                # Minimal fields for variety
            },
        ]

        for i, op in enumerate(sample_operations):
            identity_id = f"test_analytics_identity_{i}"
            await compliance.verify_identity_compliance(identity_id, op)

        yield compliance

        await compliance.shutdown_compliance_system()

    @pytest.fixture
    async def analytics_system(self, compliance_with_data):
        """Create analytics system with compliance data"""
        return GuardianComplianceAnalytics(compliance_with_data)

    @pytest.mark.anyio
    async def test_analytics_initialization(self, compliance_with_data):
        """Test analytics system initializes correctly"""
        analytics = GuardianComplianceAnalytics(compliance_with_data)

        assert analytics.compliance_system == compliance_with_data
        assert analytics.cache_ttl.total_seconds() == 300  # 5 minutes

    @pytest.mark.anyio
    async def test_metrics_summary_generation(self, analytics_system):
        """Test generating comprehensive metrics summary"""
        summary = await analytics_system.generate_metrics_summary(
            time_period_days=7, include_trends=False
        )

        assert isinstance(summary, ComplianceMetricsSummary)
        assert summary.total_operations > 0
        assert 0.0 <= summary.compliance_rate <= 1.0
        assert 0.0 <= summary.average_constitutional_score <= 1.0
        assert summary.generated_at is not None

        # Should have category breakdown
        assert len(summary.category_breakdown) > 0

    @pytest.mark.anyio
    async def test_metrics_summary_with_trends(self, analytics_system):
        """Test metrics summary includes trend analysis"""
        summary = await analytics_system.generate_metrics_summary(
            time_period_days=7, include_trends=True
        )

        assert isinstance(summary, ComplianceMetricsSummary)
        # Trends may be empty if not enough data, but should be a list
        assert isinstance(summary.compliance_trends, list)

    @pytest.mark.anyio
    async def test_category_breakdown(self, analytics_system):
        """Test category breakdown in metrics summary"""
        summary = await analytics_system.generate_metrics_summary(time_period_days=7)

        assert len(summary.category_breakdown) > 0

        for category, stats in summary.category_breakdown.items():
            assert "count" in stats
            assert "compliant" in stats
            assert "avg_score" in stats
            assert "compliance_rate" in stats
            assert 0.0 <= stats["compliance_rate"] <= 1.0

    @pytest.mark.anyio
    async def test_principle_compliance_rates(self, analytics_system):
        """Test principle compliance rate calculation"""
        summary = await analytics_system.generate_metrics_summary(time_period_days=7)

        # Should have principle compliance rates
        if summary.principle_compliance_rates:
            for principle, rate in summary.principle_compliance_rates.items():
                assert 0.0 <= rate <= 1.0
                assert isinstance(principle, str)

    @pytest.mark.anyio
    async def test_alerts_and_recommendations(self, analytics_system):
        """Test that alerts and recommendations are generated"""
        summary = await analytics_system.generate_metrics_summary(time_period_days=7)

        # Should have lists for alerts/recommendations (may be empty)
        assert isinstance(summary.critical_issues, list)
        assert isinstance(summary.warnings, list)
        assert isinstance(summary.recommendations, list)

    @pytest.mark.anyio
    async def test_identity_compliance_profile(self, analytics_system, compliance_with_data):
        """Test generating identity-specific compliance profile"""
        # Get an identity that has checks
        identity_id = "test_analytics_identity_0"

        profile = await analytics_system.get_identity_compliance_profile(identity_id)

        assert profile["identity_id"] == identity_id
        assert profile["total_operations"] > 0
        assert "first_operation" in profile
        assert "last_operation" in profile
        assert "compliance_status_breakdown" in profile
        assert "average_constitutional_score" in profile
        assert "risk_level" in profile

        # Risk level should be valid
        assert profile["risk_level"] in ["low", "moderate", "high"]

    @pytest.mark.anyio
    async def test_identity_profile_no_data(self, analytics_system):
        """Test identity profile for identity with no checks"""
        profile = await analytics_system.get_identity_compliance_profile("nonexistent_identity")

        assert profile["total_operations"] == 0
        assert "message" in profile

    @pytest.mark.anyio
    async def test_compliance_dashboard_data(self, analytics_system):
        """Test generating dashboard-ready data"""
        dashboard = await analytics_system.generate_compliance_dashboard_data()

        assert "overview" in dashboard
        assert "recent_24h" in dashboard
        assert "weekly_summary" in dashboard
        assert "trends" in dashboard
        assert "alerts" in dashboard
        assert "generated_at" in dashboard

        # Overview should have key metrics
        assert "total_operations" in dashboard["overview"]
        assert "compliance_rate" in dashboard["overview"]
        assert "average_score" in dashboard["overview"]

        # Alerts should have categories
        assert "critical" in dashboard["alerts"]
        assert "warnings" in dashboard["alerts"]
        assert "recommendations" in dashboard["alerts"]

    @pytest.mark.anyio
    async def test_trend_calculation(self, analytics_system):
        """Test compliance trend calculation"""
        trends = await analytics_system._calculate_compliance_trends(days=7)

        # May be empty if not enough data
        assert isinstance(trends, list)

        for trend in trends:
            assert isinstance(trend, ComplianceTrend)
            assert trend.metric_name is not None
            assert trend.trend_direction in ["improving", "declining", "stable"]
            assert 0.0 <= trend.confidence_level <= 1.0

    @pytest.mark.anyio
    async def test_risk_level_assessment(self, analytics_system):
        """Test risk level assessment in identity profiles"""
        # Create compliance system with varying compliance rates
        compliance = GuardianConstitutionalCompliance()
        await compliance.initialize_compliance_system()

        # Add operations for one identity
        identity_id = "risk_test_identity"
        
        # Add compliant operations
        for i in range(9):
            op = {
                "decision_category": GuardianDecisionCategory.IDENTITY_VERIFICATION,
                "user_consent": True,
                "data_minimization": True,
                "security_measures": ["encryption"],
            }
            await compliance.verify_identity_compliance(identity_id, op)

        # Add one non-compliant
        await compliance.verify_identity_compliance(identity_id, {
            "decision_category": GuardianDecisionCategory.DATA_GOVERNANCE,
        })

        analytics = GuardianComplianceAnalytics(compliance)
        profile = await analytics.get_identity_compliance_profile(identity_id)

        # Should have a risk level
        assert "risk_level" in profile
        assert profile["risk_level"] in ["low", "moderate", "high"]

        await compliance.shutdown_compliance_system()


class TestComplianceMetricsSummary:
    """Test ComplianceMetricsSummary dataclass"""

    def test_summary_creation(self):
        """Test creating metrics summary"""
        if not ANALYTICS_AVAILABLE:
            pytest.skip("Analytics module not available")

        summary = ComplianceMetricsSummary(
            summary_id="test-summary",
            total_operations=100,
            compliance_rate=0.85,
        )

        assert summary.summary_id == "test-summary"
        assert summary.total_operations == 100
        assert summary.compliance_rate == 0.85
        assert isinstance(summary.generated_at, datetime)

    def test_summary_defaults(self):
        """Test summary default values"""
        if not ANALYTICS_AVAILABLE:
            pytest.skip("Analytics module not available")

        summary = ComplianceMetricsSummary(summary_id="test")

        assert summary.total_operations == 0
        assert summary.compliance_rate == 0.0
        assert summary.compliant_count == 0
        assert isinstance(summary.category_breakdown, dict)
        assert isinstance(summary.compliance_trends, list)


class TestComplianceTrend:
    """Test ComplianceTrend dataclass"""

    def test_trend_creation(self):
        """Test creating compliance trend"""
        if not ANALYTICS_AVAILABLE:
            pytest.skip("Analytics module not available")

        trend = ComplianceTrend(
            trend_id="test-trend",
            metric_name="Compliance Rate",
            time_period_days=7,
            current_value=0.85,
            previous_value=0.80,
            change_percentage=6.25,
            trend_direction="improving",
        )

        assert trend.trend_id == "test-trend"
        assert trend.metric_name == "Compliance Rate"
        assert trend.current_value == 0.85
        assert trend.previous_value == 0.80
        assert trend.trend_direction == "improving"


if __name__ == "__main__":
    """Run tests with pytest"""
    import sys

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Run tests
    pytest.main([__file__, "-v", "-s", "--tb=short", *sys.argv[1:]])
