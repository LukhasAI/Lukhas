#!/usr/bin/env python3
"""
Test Safety Tags System
========================

Task 13: Comprehensive testing for Safety Tags including:
- Tag detection for various categories (PII, financial, model-switch, etc.)
- DSL predicate evaluation with tag-based rules
- Plan enrichment performance and accuracy
- Integration with Ethics DSL and Guardian Drift Bands

#TAG:ethics
#TAG:safety
#TAG:tags
#TAG:task13
#TAG:testing
"""

import time
from unittest.mock import Mock, patch

import pytest

# Import test targets
try:
    from core.ethics.logic.dsl_lite import (
        has_category,
        has_tag,
        high_risk_tag_combination,
        requires_human_for_tags,
        tag_confidence,
    )
    from core.ethics.safety_tags import (
        ExternalCallDetector,
        FinancialDetector,
        GDPRDetector,
        ModelSwitchDetector,
        PIIDetector,
        PrivilegeEscalationDetector,
        SafetyTag,
        SafetyTagCategory,
        SafetyTagEnricher,
        TaggedPlan,
        create_safety_tag_enricher,
    )

    SAFETY_TAGS_AVAILABLE = True
except ImportError:
    SAFETY_TAGS_AVAILABLE = False
    pytest.skip("Safety Tags not available", allow_module_level=True)


class TestSafetyTag:
    """Test SafetyTag dataclass."""

    def test_safety_tag_creation(self):
        """Test creating a safety tag."""
        tag = SafetyTag(
            name="pii",
            category=SafetyTagCategory.DATA_SENSITIVITY,
            description="PII detected",
            confidence=0.95,
            metadata={"detected_types": ["email"]},
        )

        assert tag.name == "pii"
        assert tag.category == SafetyTagCategory.DATA_SENSITIVITY
        assert tag.confidence == 0.95
        assert tag.metadata["detected_types"] == ["email"]

    def test_invalid_confidence_raises_error(self):
        """Test that invalid confidence values raise errors."""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            SafetyTag(
                name="test", category=SafetyTagCategory.DATA_SENSITIVITY, description="Test", confidence=1.5  # Invalid
            )


class TestTaggedPlan:
    """Test TaggedPlan functionality."""

    @pytest.fixture
    def sample_tags(self):
        """Create sample tags for testing."""
        return [
            SafetyTag("pii", SafetyTagCategory.DATA_SENSITIVITY, "PII detected", confidence=0.9),
            SafetyTag("external-call", SafetyTagCategory.SYSTEM_OPERATION, "External call", confidence=0.95),
            SafetyTag("financial", SafetyTagCategory.DATA_SENSITIVITY, "Financial data", confidence=0.8),
        ]

    @pytest.fixture
    def tagged_plan(self, sample_tags):
        """Create a tagged plan for testing."""
        return TaggedPlan(original_plan={"action": "test", "params": {}}, tags=sample_tags, enrichment_time_ms=1.5)

    def test_tag_names_property(self, tagged_plan):
        """Test tag_names property."""
        tag_names = tagged_plan.tag_names
        assert "pii" in tag_names
        assert "external-call" in tag_names
        assert "financial" in tag_names
        assert len(tag_names) == 3

    def test_tags_by_category(self, tagged_plan):
        """Test grouping tags by category."""
        groups = tagged_plan.tags_by_category

        data_sensitivity_tags = groups[SafetyTagCategory.DATA_SENSITIVITY]
        assert len(data_sensitivity_tags) == 2  # pii and financial

        system_tags = groups[SafetyTagCategory.SYSTEM_OPERATION]
        assert len(system_tags) == 1  # external-call

    def test_has_tag(self, tagged_plan):
        """Test has_tag method."""
        assert tagged_plan.has_tag("pii")
        assert tagged_plan.has_tag("external-call")
        assert not tagged_plan.has_tag("nonexistent")

    def test_has_category(self, tagged_plan):
        """Test has_category method."""
        assert tagged_plan.has_category(SafetyTagCategory.DATA_SENSITIVITY)
        assert tagged_plan.has_category(SafetyTagCategory.SYSTEM_OPERATION)
        assert not tagged_plan.has_category(SafetyTagCategory.SECURITY_RISK)


class TestPIIDetector:
    """Test PII detection functionality."""

    @pytest.fixture
    def pii_detector(self):
        """Create PII detector for testing."""
        return PIIDetector()

    def test_email_detection(self, pii_detector):
        """Test email PII detection."""
        plan = {"action": "send_notification", "params": {"email": "user@example.com"}}

        tag = pii_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "pii"
        assert tag.confidence > 0.9

    def test_ssn_detection(self, pii_detector):
        """Test SSN detection."""
        plan = {"action": "process_application", "params": {"ssn": "123-45-6789"}}

        tag = pii_detector.detect(plan, {})
        assert tag is not None
        assert tag.confidence > 0.9
        assert "ssn" in tag.metadata["detected_types"]

    def test_pii_field_names(self, pii_detector):
        """Test PII detection by field names."""
        plan = {"action": "update_profile", "params": {"first_name": "John", "last_name": "Doe"}}

        tag = pii_detector.detect(plan, {})
        assert tag is not None
        assert tag.confidence > 0.8

    def test_no_pii_detected(self, pii_detector):
        """Test case with no PII."""
        plan = {"action": "calculate_sum", "params": {"a": 5, "b": 10}}

        tag = pii_detector.detect(plan, {})
        assert tag is None


class TestFinancialDetector:
    """Test financial data detection."""

    @pytest.fixture
    def financial_detector(self):
        """Create financial detector for testing."""
        return FinancialDetector()

    def test_financial_action_detection(self, financial_detector):
        """Test detection of financial actions."""
        plan = {"action": "process_payment", "params": {"amount": 100.00}}

        tag = financial_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "financial"
        assert tag.confidence > 0.8

    def test_financial_field_detection(self, financial_detector):
        """Test detection of financial fields."""
        plan = {"action": "update_account", "params": {"account_number": "1234567890"}}

        tag = financial_detector.detect(plan, {})
        assert tag is not None
        assert "field:account_number" in tag.metadata["detected_types"]

    def test_currency_amount_detection(self, financial_detector):
        """Test detection of currency amounts."""
        plan = {"action": "calculate_fee", "params": {"amount": 50.99, "currency": "USD"}}

        tag = financial_detector.detect(plan, {})
        assert tag is not None


class TestModelSwitchDetector:
    """Test model switching detection."""

    @pytest.fixture
    def model_switch_detector(self):
        """Create model switch detector for testing."""
        return ModelSwitchDetector()

    def test_model_switch_action(self, model_switch_detector):
        """Test detection of model switching actions."""
        plan = {"action": "switch_model", "params": {"target_model": "gpt-4"}}

        tag = model_switch_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "model-switch"
        assert tag.confidence > 0.9

    def test_model_parameter_detection(self, model_switch_detector):
        """Test detection of model parameters."""
        plan = {"action": "configure_ai", "params": {"model": "claude-3", "temperature": 0.7}}

        tag = model_switch_detector.detect(plan, {})
        assert tag is not None
        assert "param:model" in tag.metadata["detected_types"]


class TestExternalCallDetector:
    """Test external API call detection."""

    @pytest.fixture
    def external_call_detector(self):
        """Create external call detector for testing."""
        return ExternalCallDetector()

    def test_external_call_detection(self, external_call_detector):
        """Test detection of external API calls."""
        plan = {"action": "external_call", "params": {"url": "https://api.example.com/data"}}

        tag = external_call_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "external-call"
        assert tag.confidence > 0.9

    def test_url_parameter_detection(self, external_call_detector):
        """Test detection by URL parameters."""
        plan = {"action": "fetch_data", "params": {"endpoint": "https://service.api.com/v1/users"}}

        tag = external_call_detector.detect(plan, {})
        assert tag is not None


class TestPrivilegeEscalationDetector:
    """Test privilege escalation detection."""

    @pytest.fixture
    def privilege_detector(self):
        """Create privilege escalation detector for testing."""
        return PrivilegeEscalationDetector()

    def test_admin_action_detection(self, privilege_detector):
        """Test detection of admin actions."""
        plan = {"action": "admin_override", "params": {"operation": "grant_access"}}

        tag = privilege_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "privilege-escalation"
        assert tag.confidence > 0.9

    def test_escalation_terms_detection(self, privilege_detector):
        """Test detection of escalation terms."""
        plan = {"action": "system_command", "params": {"command": "sudo rm -rf /"}}

        tag = privilege_detector.detect(plan, {})
        assert tag is not None


class TestGDPRDetector:
    """Test GDPR compliance detection."""

    @pytest.fixture
    def gdpr_detector(self):
        """Create GDPR detector for testing."""
        return GDPRDetector()

    def test_gdpr_action_detection(self, gdpr_detector):
        """Test detection of GDPR actions."""
        plan = {"action": "data_export", "params": {"user_id": "eu_user_123"}}

        tag = gdpr_detector.detect(plan, {})
        assert tag is not None
        assert tag.name == "gdpr"

    def test_eu_user_context_boost(self, gdpr_detector):
        """Test GDPR detection boost for EU users."""
        plan = {"action": "process_personal_data", "params": {"data_type": "profile"}}
        context = {"user_region": "EU"}

        tag = gdpr_detector.detect(plan, context)
        assert tag is not None
        assert "eu_user" in tag.metadata["detected_types"]


class TestSafetyTagEnricher:
    """Test the main Safety Tag Enricher system."""

    @pytest.fixture
    def enricher(self):
        """Create enricher for testing."""
        return create_safety_tag_enricher(enable_caching=True)

    def test_pii_enrichment(self, enricher):
        """Test PII tag enrichment."""
        plan = {"action": "send_email", "params": {"email": "user@example.com", "message": "Hello"}}

        tagged_plan = enricher.enrich_plan(plan)
        assert tagged_plan.has_tag("pii")
        assert tagged_plan.enrichment_time_ms > 0

    def test_multiple_tag_detection(self, enricher):
        """Test detection of multiple tags."""
        plan = {
            "action": "external_call",
            "params": {
                "url": "https://api.bank.com/account",
                "email": "customer@example.com",
                "account_number": "1234567890",
            },
        }

        tagged_plan = enricher.enrich_plan(plan)
        assert tagged_plan.has_tag("pii")
        assert tagged_plan.has_tag("financial")
        assert tagged_plan.has_tag("external-call")
        assert len(tagged_plan.tags) >= 3

    def test_caching_behavior(self, enricher):
        """Test caching improves performance."""
        plan = {"action": "test", "params": {"value": "test"}}

        # First call - cache miss
        start_time = time.perf_counter()
        enricher.enrich_plan(plan)
        time1 = time.perf_counter() - start_time

        # Second call - cache hit
        start_time = time.perf_counter()
        result2 = enricher.enrich_plan(plan)
        time2 = time.perf_counter() - start_time

        # Cache hit should be faster
        assert time2 < time1
        assert result2.enrichment_context.get("cache_hit") is True

    def test_custom_detector_addition(self, enricher):
        """Test adding custom detectors."""

        class TestDetector:
            def __init__(self):
                self.tag_name = "test_tag"
                self.category = SafetyTagCategory.SECURITY_RISK
                self.description = "Test detector"

            def detect(self, plan, context):
                if plan.get("action") == "test_action":
                    return SafetyTag(
                        name=self.tag_name, category=self.category, description=self.description, confidence=1.0
                    )
                return None

        enricher.add_detector(TestDetector())

        plan = {"action": "test_action"}
        tagged_plan = enricher.enrich_plan(plan)
        assert tagged_plan.has_tag("test_tag")

    def test_error_handling(self, enricher):
        """Test error handling during enrichment."""
        # Mock a detector to raise an exception
        with patch.object(enricher.detectors[0], "detect", side_effect=Exception("Test error")):
            plan = {"action": "test"}
            tagged_plan = enricher.enrich_plan(plan)

            # Should still return a valid TaggedPlan
            assert isinstance(tagged_plan, TaggedPlan)
            assert tagged_plan.enrichment_time_ms > 0

    def test_performance_requirements(self, enricher):
        """Test that enrichment meets performance requirements."""
        plan = {
            "action": "complex_operation",
            "params": {"email": "user@example.com", "account": "1234567890", "url": "https://api.example.com"},
        }

        times = []
        for _ in range(10):
            start = time.perf_counter()
            enricher.enrich_plan(plan)
            times.append((time.perf_counter() - start) * 1000)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Should be well under 2ms for typical plans
        assert avg_time < 2.0, f"Average enrichment time {avg_time:.2f}ms exceeds 2ms"
        assert max_time < 5.0, f"Max enrichment time {max_time:.2f}ms exceeds 5ms"


class TestDSLPredicates:
    """Test DSL predicates for tag-based rules."""

    def test_has_tag_predicate(self):
        """Test has_tag DSL predicate."""
        # List format
        tags_list = ["pii", "financial"]
        assert has_tag(tags_list, "pii") is True
        assert has_tag(tags_list, "nonexistent") is False

        # Dict format
        tags_dict = {"pii": {"confidence": 0.9}, "financial": {}}
        assert has_tag(tags_dict, "pii") is True
        assert has_tag(tags_dict, "financial") is True

        # String format
        tags_string = "pii,financial,external-call"
        assert has_tag(tags_string, "financial") is True
        assert has_tag(tags_string, "model-switch") is False

        # None case
        assert has_tag(None, "any") is False

    def test_has_category_predicate(self):
        """Test has_category DSL predicate."""
        tags = ["pii", "financial", "model-switch"]

        assert has_category(tags, "data_sensitivity") is True  # pii, financial
        assert has_category(tags, "system_operation") is True  # model-switch
        assert has_category(tags, "security_risk") is False
        assert has_category(tags, "nonexistent") is False

    def test_tag_confidence_predicate(self):
        """Test tag_confidence DSL predicate."""
        tags_with_confidence = {
            "pii": {"confidence": 0.95},
            "financial": {"confidence": 0.7},
            "external-call": {},  # No confidence specified
        }

        # High confidence tag
        assert tag_confidence(tags_with_confidence, "pii", 0.9) is True
        assert tag_confidence(tags_with_confidence, "pii", 0.97) is False

        # Low confidence tag
        assert tag_confidence(tags_with_confidence, "financial", 0.8) is False
        assert tag_confidence(tags_with_confidence, "financial", 0.6) is True

        # No confidence metadata - assume high confidence
        assert tag_confidence(tags_with_confidence, "external-call", 0.9) is True

    def test_requires_human_for_tags_predicate(self):
        """Test requires_human_for_tags DSL predicate."""
        tags = ["pii", "safe_operation"]

        # Should require human for PII
        assert requires_human_for_tags(tags, "pii") is True
        assert requires_human_for_tags(tags, "financial") is False
        assert requires_human_for_tags(tags, "pii", "financial") is True  # Any match

        # Multiple tags, none requiring human
        assert requires_human_for_tags(tags, "safe_operation") is False

    def test_high_risk_tag_combination_predicate(self):
        """Test high_risk_tag_combination DSL predicate."""
        # High risk: PII + external call
        high_risk_tags = ["pii", "external-call"]
        assert high_risk_tag_combination(high_risk_tags) is True

        # High risk: Financial + model switch
        financial_model_risk = ["financial", "model-switch"]
        assert high_risk_tag_combination(financial_model_risk) is True

        # Not high risk
        safe_tags = ["pii", "internal-operation"]
        assert high_risk_tag_combination(safe_tags) is False

        # Empty tags
        assert high_risk_tag_combination([]) is False
        assert high_risk_tag_combination(None) is False


class TestIntegrationScenarios:
    """Test integration scenarios with multiple components."""

    @pytest.fixture
    def enricher(self):
        """Create enricher for integration testing."""
        return create_safety_tag_enricher()

    def test_pii_external_call_scenario(self, enricher):
        """Test PII + external call detection and rule application."""
        plan = {
            "action": "send_data",
            "params": {
                "url": "https://external-service.com/api",
                "user_email": "sensitive@example.com",
                "personal_data": "John Doe, 123-45-6789",
            },
        }

        tagged_plan = enricher.enrich_plan(plan)

        # Should detect both PII and external call
        assert tagged_plan.has_tag("pii")
        assert tagged_plan.has_tag("external-call")

        # Should trigger high-risk combination
        tags_list = list(tagged_plan.tag_names)
        assert high_risk_tag_combination(tags_list) is True

    def test_financial_model_switch_scenario(self, enricher):
        """Test financial + model switch detection."""
        plan = {
            "action": "switch_model",
            "params": {"model": "financial-ai-v2", "account_data": "Account: 9876543210", "amount": 1000.00},
        }

        tagged_plan = enricher.enrich_plan(plan)

        # Should detect financial and model-switch
        assert tagged_plan.has_tag("financial")
        assert tagged_plan.has_tag("model-switch")

        # Should require human oversight
        tags_list = list(tagged_plan.tag_names)
        assert requires_human_for_tags(tags_list, "financial", "model-switch") is True

    def test_gdpr_compliance_scenario(self, enricher):
        """Test GDPR compliance detection."""
        plan = {"action": "data_deletion", "params": {"user_id": "eu_user_456", "personal_data": True}}
        context = {"user_region": "EU"}

        tagged_plan = enricher.enrich_plan(plan, context)

        # Should detect GDPR relevance
        assert tagged_plan.has_tag("gdpr")

        # GDPR category should be detected
        tags_list = list(tagged_plan.tag_names)
        assert has_category(tags_list, "compliance") is True


if __name__ == "__main__":
    pytest.main([__file__])
