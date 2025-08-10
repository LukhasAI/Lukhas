"""
Test NIAS Transparency Layers
Comprehensive tests for the 7-tier transparency system implementation
"""

from datetime import datetime

import pytest
from nias.integration.nias_integration_hub import (
    NIASIntegrationHub,
    TransparencyLevel,
    UserTier,
)


class TestNIASTransparencyLayers:
    """Test suite for NIAS transparency layer implementation"""

    @pytest.fixture
    async def nias_hub(self):
        """Create a NIAS integration hub instance for testing"""
        hub = NIASIntegrationHub()
        await hub.initialize()
        return hub

    @pytest.mark.asyncio
    async def test_transparency_level_mapping(self, nias_hub):
        """Test that user tiers map to correct transparency levels"""
        test_cases = [
            (UserTier.GUEST, TransparencyLevel.MINIMAL),
            (UserTier.STANDARD, TransparencyLevel.SUMMARY),
            (UserTier.PREMIUM, TransparencyLevel.DETAILED),
            (UserTier.ENTERPRISE, TransparencyLevel.COMPREHENSIVE),
            (UserTier.ADMIN, TransparencyLevel.TECHNICAL),
            (UserTier.DEVELOPER, TransparencyLevel.AUDIT_TRAIL),
            (UserTier.AUDITOR, TransparencyLevel.FULL_DEBUG),
        ]

        for user_tier, expected_level in test_cases:
            user_context = {"tier": user_tier.value}
            level = await nias_hub.get_transparency_level(user_context)
            assert (
                level == expected_level
            ), f"Tier {user_tier} should map to {expected_level}"

    @pytest.mark.asyncio
    async def test_transparency_preference_override(self, nias_hub):
        """Test that explicit transparency preferences override tier defaults"""
        user_context = {
            "tier": "standard",  # Would normally get SUMMARY
            "transparency_preference": "detailed",  # Requesting DETAILED
        }

        level = await nias_hub.get_transparency_level(user_context)
        assert level == TransparencyLevel.DETAILED

    @pytest.mark.asyncio
    async def test_generate_minimal_explanation(self, nias_hub):
        """Test minimal explanation generation for guest users"""
        decision = {
            "id": "test_decision_1",
            "action": "filtered",
            "reason": "policy_match",
        }

        user_context = {"tier": "guest"}
        explanation = await nias_hub.generate_explanation(decision, user_context)

        assert explanation["transparency_level"] == "minimal"
        assert explanation["user_tier"] == "guest"
        assert "content" in explanation
        assert explanation["content"]["type"] == "minimal"
        assert "system policies" in explanation["content"]["summary"]

    @pytest.mark.asyncio
    async def test_generate_detailed_explanation(self, nias_hub):
        """Test detailed explanation generation for premium users"""
        decision = {
            "id": "test_decision_2",
            "action": "filtered",
            "reason": "inappropriate_content",
            "matched_categories": ["violence", "profanity"],
            "confidence": "high",
            "policies_triggered": ["policy_1", "policy_2"],
            "suggested_alternatives": ["alternative_1", "alternative_2"],
        }

        user_context = {"tier": "premium"}
        explanation = await nias_hub.generate_explanation(decision, user_context)

        assert explanation["transparency_level"] == "detailed"
        content = explanation["content"]
        assert content["type"] == "detailed"
        assert "categories" in content
        assert "policy_details" in content
        assert "alternatives" in content
        assert "appeal_process" in content

    @pytest.mark.asyncio
    async def test_generate_audit_trail_explanation(self, nias_hub):
        """Test audit trail explanation generation for developers"""
        decision = {
            "id": "test_decision_3",
            "action": "allowed",
            "symbolic_trace": ["rule_1", "rule_2"],
            "ethics_check": {"passed": True},
            "consent_status": {"verified": True},
        }

        user_context = {"tier": "developer"}
        explanation = await nias_hub.generate_explanation(decision, user_context)

        assert explanation["transparency_level"] == "audit_trail"
        content = explanation["content"]
        assert content["type"] == "audit_trail"
        assert "audit_trail" in content
        assert "symbolic_trace" in content
        assert "system_state" in content

    @pytest.mark.asyncio
    async def test_explanation_caching(self, nias_hub):
        """Test that explanations are cached correctly"""
        decision = {"id": "cached_decision", "action": "filtered"}
        user_context = {"tier": "standard"}

        # First call should generate and cache
        explanation1 = await nias_hub.generate_explanation(decision, user_context)
        cache_size_1 = len(nias_hub.explanation_cache)

        # Second call should retrieve from cache
        explanation2 = await nias_hub.generate_explanation(decision, user_context)
        cache_size_2 = len(nias_hub.explanation_cache)

        assert cache_size_1 == cache_size_2  # No new cache entry
        assert explanation1 == explanation2  # Same explanation returned

    @pytest.mark.asyncio
    async def test_query_recording(self, nias_hub):
        """Test that queries are recorded for transparency"""
        initial_count = len(nias_hub.query_history)

        query = {"type": "content_filter", "id": "query_123"}
        user_context = {"tier": "premium"}

        await nias_hub.record_query(query, user_context)

        assert len(nias_hub.query_history) == initial_count + 1
        recorded_query = nias_hub.query_history[-1]
        assert recorded_query["query_type"] == "content_filter"
        assert recorded_query["user_tier"] == "premium"
        assert recorded_query["transparency_level"] == "detailed"

    @pytest.mark.asyncio
    async def test_mutation_recording_with_audit(self, nias_hub):
        """Test that significant mutations trigger audit entries"""
        mutation = {
            "type": "policy_update",
            "id": "policy_123",
            "affected_policies": ["policy_123"],
            "approval_status": "approved",
        }
        user_context = {"tier": "admin"}

        await nias_hub.record_mutation(mutation, user_context)

        assert len(nias_hub.mutation_history) > 0
        recorded_mutation = nias_hub.mutation_history[-1]
        assert recorded_mutation["mutation_type"] == "policy_update"
        assert recorded_mutation["transparency_level"] == "technical"

    @pytest.mark.asyncio
    async def test_filter_content_with_transparency(self, nias_hub):
        """Test content filtering with transparency layer integration"""
        content = {"id": "content_123", "type": "text", "data": "Test content"}

        # Test with different user tiers
        for tier in ["guest", "standard", "premium", "admin"]:
            user_context = {"tier": tier, "user_id": f"test_user_{tier}"}

            result = await nias_hub.filter_content(content, user_context)

            assert "explanation" in result
            assert result["explanation"]["user_tier"] == tier
            assert "timestamp" in result

            # Higher tiers should get more detailed explanations
            if tier in ["premium", "admin"]:
                assert "content" in result["explanation"]
                explanation_content = result["explanation"]["content"]
                assert explanation_content["type"] in [
                    "detailed",
                    "comprehensive",
                    "technical",
                ]

    @pytest.mark.asyncio
    async def test_transparency_report_generation(self, nias_hub):
        """Test transparency report generation based on user tier"""
        # Add some test data
        for i in range(5):
            await nias_hub.record_query(
                {"type": "test_query", "id": f"query_{i}"}, {"tier": "standard"}
            )

        # Test reports for different tiers
        test_cases = [
            ("guest", ["summary"]),
            ("premium", ["detailed_stats"]),
            ("auditor", ["complete_analytics"]),
        ]

        for tier, expected_sections in test_cases:
            user_context = {"tier": tier}
            report = await nias_hub.get_transparency_report(user_context)

            assert report["user_tier"] == tier
            assert "generated_at" in report

            for section in expected_sections:
                assert section in report

    @pytest.mark.asyncio
    async def test_natural_language_explanations(self, nias_hub):
        """Test natural language explanation generation"""
        decision = {
            "id": "nl_test",
            "action": "filtered",
            "reason": "policy_violation",
            "matched_categories": ["spam", "misleading"],
            "confidence": "high",
        }

        test_cases = [
            ("guest", "according to our policies"),
            ("standard", "matched these categories"),
            ("premium", "triggered"),
            ("admin", "Technical Analysis"),
        ]

        for tier, expected_phrase in test_cases:
            user_context = {"tier": tier}
            nl_explanation = await nias_hub.get_natural_language_explanation(
                decision, user_context
            )

            assert isinstance(nl_explanation, str)
            assert expected_phrase in nl_explanation

    @pytest.mark.asyncio
    async def test_policy_update_permissions(self, nias_hub):
        """Test that only authorized tiers can update policies"""
        policy_update = {"policy_id": "test_policy", "changes": {"threshold": 0.8}}

        # Test unauthorized tiers
        for tier in ["guest", "standard", "premium"]:
            user_context = {"tier": tier}
            result = await nias_hub.update_policy(policy_update, user_context)

            assert not result.get("success", True)
            assert "Insufficient permissions" in result.get("error", "")

        # Test authorized tiers
        for tier in ["admin", "developer", "auditor"]:
            user_context = {"tier": tier}
            result = await nias_hub.update_policy(policy_update, user_context)

            # Should have explanation even if update fails
            assert "explanation" in result or "error" not in result

    @pytest.mark.asyncio
    async def test_query_system_state_visibility(self, nias_hub):
        """Test system state query returns appropriate info based on tier"""
        query = {"type": "general", "id": "state_query_1"}

        visibility_tests = [
            ("guest", "basic_info"),
            ("premium", "detailed_info"),
            ("auditor", "complete_info"),
        ]

        for tier, expected_section in visibility_tests:
            user_context = {"tier": tier}
            state = await nias_hub.query_system_state(query, user_context)

            assert "operational_status" in state
            assert expected_section in state

            # Verify progressive disclosure
            if tier == "auditor":
                assert "query_analytics" in state["complete_info"]
                assert "compliance" in state["complete_info"]

    @pytest.mark.asyncio
    async def test_performance_metrics_calculation(self, nias_hub):
        """Test performance metrics calculation"""
        # Add some test data
        for i in range(10):
            nias_hub.query_history.append(
                {"timestamp": datetime.now().isoformat(), "query_type": "test"}
            )

        metrics = await nias_hub._get_performance_metrics()

        assert "avg_processing_time_ms" in metrics
        assert "p95_processing_time_ms" in metrics
        assert "cache_hit_rate" in metrics
        assert metrics["cache_hit_rate"] >= 0

    @pytest.mark.asyncio
    async def test_history_size_limits(self, nias_hub):
        """Test that query and mutation histories respect size limits"""
        # Add more than limit
        for i in range(1200):
            await nias_hub.record_query(
                {"type": "test", "id": f"query_{i}"}, {"tier": "standard"}
            )

        assert len(nias_hub.query_history) == 1000  # Should be limited

        # Verify most recent are kept
        assert nias_hub.query_history[-1]["query_id"] == "query_1199"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
