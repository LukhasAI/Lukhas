"""
Tests for Guardian Integrated Platform - Phase 2A Implementation.

Tests the integration of Guardian System ethics with NIAS economic platform.
"""

from unittest.mock import AsyncMock

import pytest

from candidate.core.business.guardian_integrated_platform import (
    GuardianIntegratedPlatform,
    GuardianSystemAdapter,
)


@pytest.fixture
def mock_budget_manager():
    """Mock budget manager for testing."""
    mock = AsyncMock()
    mock.check_budget.return_value = {"within_budget": True, "remaining_budget": 0.45}
    mock.record_usage.return_value = {"success": True}
    mock.get_aggregate_metrics.return_value = {"total_allocated": 100.0}
    return mock


@pytest.fixture
def mock_consciousness_cache():
    """Mock consciousness cache for testing."""
    mock = AsyncMock()
    mock.store_consciousness_state.return_value = {"cached": True}
    return mock


@pytest.fixture
def mock_revenue_tracker():
    """Mock revenue tracker for testing."""
    mock = AsyncMock()
    mock.record_conversion.return_value = {"user_earnings": 10.0, "platform_earnings": 15.0}
    mock.get_aggregate_metrics.return_value = {
        "total_revenue": 1000.0,
        "user_earnings": 400.0,
        "roi_percentage": 3537.0,
    }
    return mock


@pytest.fixture
def guardian_adapter():
    """Guardian System adapter instance."""
    return GuardianSystemAdapter()


@pytest.fixture
def integrated_platform(mock_budget_manager, mock_consciousness_cache, mock_revenue_tracker):
    """Guardian integrated platform instance."""
    return GuardianIntegratedPlatform(mock_budget_manager, mock_consciousness_cache, mock_revenue_tracker)


class TestGuardianSystemAdapter:
    """Test Guardian System ethics enforcement."""

    @pytest.mark.asyncio
    async def test_clean_content_approval(self, guardian_adapter):
        """Test that clean content gets approved."""
        clean_content = {
            "message": "Discover a new book that might interest you.",
            "categories": ["books"],
        }
        user_context = {"user_id": "test_user", "consent_preferences": {"opted_out_categories": []}}

        result = await guardian_adapter.check_content_ethics(clean_content, user_context)

        assert result["ethics_approved"] is True
        assert len(result["violations"]) == 0
        assert result["current_drift"] < 0.15  # Below threshold

    @pytest.mark.asyncio
    async def test_manipulative_content_detection(self, guardian_adapter):
        """Test detection of manipulative language."""
        manipulative_content = {
            "message": "You MUST act now! Limited time offer - don't miss out!",
            "categories": ["general"],
        }
        user_context = {"user_id": "test_user"}

        result = await guardian_adapter.check_content_ethics(manipulative_content, user_context)

        assert result["ethics_approved"] is False
        assert len(result["violations"]) > 0
        assert result["violations"][0]["violation_type"] == "manipulative_content"
        assert result["violations"][0]["severity"] == 0.8

    @pytest.mark.asyncio
    async def test_vulnerability_exploitation_detection(self, guardian_adapter):
        """Test detection of vulnerability exploitation."""
        exploitative_content = {
            "message": "Solve all your debt problems with this miracle solution!",
            "categories": ["financial"],
        }
        user_context = {
            "user_id": "vulnerable_user",
            "financial_stress": 0.8,  # High financial stress
        }

        result = await guardian_adapter.check_content_ethics(exploitative_content, user_context)

        assert result["ethics_approved"] is False
        violations = result["violations"]
        violation_types = [v["violation_type"] for v in violations]
        assert "vulnerability_exploitation" in violation_types
        assert "manipulative_content" in violation_types  # "miracle" triggers this too

    @pytest.mark.asyncio
    async def test_consent_violation_detection(self, guardian_adapter):
        """Test detection of consent violations."""
        content = {"message": "Check out this amazing gambling app!", "categories": ["gambling"]}
        user_context = {
            "user_id": "opted_out_user",
            "consent_preferences": {"opted_out_categories": ["gambling", "alcohol"]},
        }

        result = await guardian_adapter.check_content_ethics(content, user_context)

        assert result["ethics_approved"] is False
        assert any(v["violation_type"] == "consent_violation" for v in result["violations"])

    @pytest.mark.asyncio
    async def test_drift_threshold_enforcement(self, guardian_adapter):
        """Test that drift threshold is properly enforced."""
        # Simulate multiple violations to increase drift
        violation_content = {
            "message": "You must buy this miracle cure now - guaranteed results!",
            "categories": ["health"],
        }
        user_context = {"user_id": "test_user"}

        # Multiple violations should accumulate drift
        for _ in range(3):
            await guardian_adapter.check_content_ethics(violation_content, user_context)

        drift_metrics = await guardian_adapter.get_drift_metrics()
        assert drift_metrics.current_drift > 0.1
        assert drift_metrics.trend in ["increasing", "stable"]

    @pytest.mark.asyncio
    async def test_drift_reset(self, guardian_adapter):
        """Test drift reset functionality."""
        # Create some violations first
        violation_content = {"message": "Act now! Limited time!", "categories": ["general"]}
        await guardian_adapter.check_content_ethics(violation_content, {"user_id": "test"})

        # Verify drift increased
        assert guardian_adapter.current_drift > 0

        # Reset drift
        reset_success = await guardian_adapter.reset_drift()
        assert reset_success is True
        assert guardian_adapter.current_drift == 0.0
        assert len(guardian_adapter.violations_cache) == 0


class TestGuardianIntegratedPlatform:
    """Test complete Guardian integrated platform."""

    @pytest.mark.asyncio
    async def test_successful_ad_request_processing(self, integrated_platform):
        """Test successful advertising request with all checks passing."""
        consciousness_profile = {
            "user_id": "test_user",
            "values": ["sustainability", "creativity"],
            "consent_preferences": {"opted_out_categories": []},
        }
        product_context = {"categories": ["books"], "alignment_score": 0.9}

        result = await integrated_platform.process_advertising_request(
            "test_user", consciousness_profile, product_context
        )

        assert result["approved"] is True
        assert "ad_content" in result
        assert result["ethics_score"] > 0.8
        assert result["consciousness_resonance"] > 0.0
        assert result["ads_remaining_today"] == 4  # Started with 5 limit, used 1

    @pytest.mark.asyncio
    async def test_budget_limit_enforcement(self, integrated_platform, mock_budget_manager):
        """Test that budget limits are enforced."""
        # Mock budget exceeded
        mock_budget_manager.check_budget.return_value = {
            "within_budget": False,
            "remaining_budget": 0.0,
        }

        result = await integrated_platform.process_advertising_request(
            "test_user", {"user_id": "test_user"}, {"categories": ["general"]}
        )

        assert result["approved"] is False
        assert "budget limit" in result["reason"]
        assert result["budget_remaining"] == 0.0

    @pytest.mark.asyncio
    async def test_daily_ad_limit_enforcement(self, integrated_platform):
        """Test that daily ad limits (1-5 per day) are enforced."""
        # Mock that user has already seen 5 ads today
        integrated_platform._get_daily_ad_count = AsyncMock(return_value=5)

        result = await integrated_platform.process_advertising_request(
            "test_user", {"user_id": "test_user"}, {"categories": ["general"]}
        )

        assert result["approved"] is False
        assert "Daily ad limit reached" in result["reason"]
        assert result["ads_shown_today"] == 5

    @pytest.mark.asyncio
    async def test_ethics_violation_rejection(self, integrated_platform):
        """Test that content with ethics violations is rejected."""
        consciousness_profile = {
            "user_id": "vulnerable_user",
            "financial_stress": 0.9,
            "consent_preferences": {"opted_out_categories": []},
        }
        # This will trigger vulnerability exploitation detection
        product_context = {
            "categories": ["financial"],
            "message_override": "Solve all your debt problems now!",
        }

        result = await integrated_platform.process_advertising_request(
            "vulnerable_user", consciousness_profile, product_context
        )

        assert result["approved"] is False
        assert "ethics" in result["reason"] or "violations" in result

    @pytest.mark.asyncio
    async def test_high_drift_human_escalation(self, integrated_platform):
        """Test that high drift triggers human review escalation."""
        # Force high drift in guardian system
        integrated_platform.guardian.current_drift = 0.13  # Above 0.12 threshold

        result = await integrated_platform.process_advertising_request(
            "test_user", {"user_id": "test_user"}, {"categories": ["general"]}
        )

        assert result["approved"] is False
        assert result.get("escalated_to_human") is True
        assert "human review" in result["reason"]

    @pytest.mark.asyncio
    async def test_conversion_tracking_with_guardian_verification(self, integrated_platform):
        """Test conversion tracking with Guardian System verification."""
        conversion_result = await integrated_platform.track_conversion(
            user_id="test_user",
            ad_id="ad_123",
            conversion_value=25.00,
            product_metadata={"category": "books", "legitimate": True},
        )

        assert conversion_result["conversion_recorded"] is True
        assert conversion_result["user_earnings"] == 10.0  # 40% of something
        assert conversion_result["platform_earnings"] == 15.0  # 60% of something
        assert conversion_result["ethics_compliance"] == "guardian_verified"
        assert "drift_score" in conversion_result

    @pytest.mark.asyncio
    async def test_platform_health_metrics(self, integrated_platform):
        """Test comprehensive platform health metrics."""
        metrics = await integrated_platform.get_platform_health_metrics()

        # Guardian status
        assert "guardian_status" in metrics
        assert metrics["guardian_status"]["current_drift"] < 0.15
        assert metrics["guardian_status"]["status"] in ["healthy", "warning"]

        # Economics status
        assert "economics_status" in metrics
        assert metrics["economics_status"]["total_budget_allocated"] >= 0
        assert metrics["economics_status"]["platform_roi"] > 0

        # Ethical compliance
        assert "ethical_compliance" in metrics
        assert metrics["ethical_compliance"]["guardian_integrated"] is True
        assert metrics["ethical_compliance"]["profit_sharing_active"] is True

    @pytest.mark.asyncio
    async def test_consciousness_cache_integration(self, integrated_platform, mock_consciousness_cache):
        """Test that consciousness profiles are properly cached."""
        consciousness_profile = {"user_id": "test_user", "values": ["test"]}

        await integrated_platform.process_advertising_request(
            "test_user", consciousness_profile, {"categories": ["general"]}
        )

        # Verify cache was called to store consciousness state
        mock_consciousness_cache.store_consciousness_state.assert_called_once()
        args = mock_consciousness_cache.store_consciousness_state.call_args
        assert args[0][0] == "test_user"  # user_id
        assert args[1]["ttl_hours"] == 24  # 24-hour TTL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
