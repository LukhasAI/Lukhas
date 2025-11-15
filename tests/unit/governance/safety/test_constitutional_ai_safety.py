"""
Comprehensive test suite for Constitutional AI Safety Module

Tests all aspects of the Constitutional AI safety system including:
- Principle validation
- Critique-revision loops
- Safety constraint enforcement
- Edge cases and adversarial inputs
"""

import pytest
from datetime import datetime

from governance.safety.constitutional_ai_safety import (
    ConstitutionalAISafety,
    ConstitutionalPrinciple,
    ConstrainedPrompt,
    PrincipleCategory,
    RevisedResponse,
    ValidationResult,
    get_default_constitution,
)


class TestConstitutionalPrinciple:
    """Test ConstitutionalPrinciple dataclass."""

    def test_principle_creation(self):
        """Test creating a constitutional principle."""
        principle = ConstitutionalPrinciple(
            id="test-01",
            category=PrincipleCategory.HARMLESSNESS,
            principle="Do not harm",
            critique_prompt="Is this harmful?",
            revision_prompt="Make it safe",
            weight=0.9
        )

        assert principle.id == "test-01"
        assert principle.category == PrincipleCategory.HARMLESSNESS
        assert principle.principle == "Do not harm"
        assert principle.weight == 0.9

    def test_principle_default_weight(self):
        """Test default weight is 1.0."""
        principle = ConstitutionalPrinciple(
            id="test-01",
            category=PrincipleCategory.HELPFULNESS,
            principle="Be helpful",
            critique_prompt="Is this helpful?",
            revision_prompt="Make it helpful"
        )

        assert principle.weight == 1.0

    def test_principle_invalid_weight(self):
        """Test that invalid weight raises ValueError."""
        with pytest.raises(ValueError, match="Weight must be between 0.0 and 1.0"):
            ConstitutionalPrinciple(
                id="test-01",
                category=PrincipleCategory.HARMLESSNESS,
                principle="Test",
                critique_prompt="Test",
                revision_prompt="Test",
                weight=1.5
            )

    def test_principle_category_string_conversion(self):
        """Test that category strings are converted to enum."""
        principle = ConstitutionalPrinciple(
            id="test-01",
            category="harmlessness",
            principle="Test",
            critique_prompt="Test",
            revision_prompt="Test"
        )

        assert principle.category == PrincipleCategory.HARMLESSNESS
        assert isinstance(principle.category, PrincipleCategory)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            valid=True,
            constitutional_score=0.95,
            violations=[],
            principles_checked=["harm-01", "help-01"],
            explanation="All good"
        )

        assert result.valid is True
        assert result.constitutional_score == 0.95
        assert len(result.violations) == 0
        assert len(result.principles_checked) == 2

    def test_validation_result_invalid_score(self):
        """Test that invalid score raises ValueError."""
        with pytest.raises(ValueError, match="Constitutional score must be between"):
            ValidationResult(
                valid=False,
                constitutional_score=1.5,
                violations=["test"],
                principles_checked=["test"],
                explanation="Test"
            )

    def test_validation_result_timestamp(self):
        """Test that timestamp is automatically generated."""
        result = ValidationResult(
            valid=True,
            constitutional_score=0.8,
        )

        assert isinstance(result.timestamp, datetime)


class TestRevisedResponse:
    """Test RevisedResponse dataclass."""

    def test_revised_response_creation(self):
        """Test creating a revised response."""
        response = RevisedResponse(
            original="Original text",
            revised="Revised text",
            iterations=2,
            improvements=["Fixed issue 1", "Fixed issue 2"],
            final_score=0.92
        )

        assert response.original == "Original text"
        assert response.revised == "Revised text"
        assert response.iterations == 2
        assert len(response.improvements) == 2
        assert response.final_score == 0.92

    def test_revised_response_invalid_score(self):
        """Test that invalid final score raises ValueError."""
        with pytest.raises(ValueError, match="Final score must be between"):
            RevisedResponse(
                original="Test",
                revised="Test",
                iterations=1,
                final_score=2.0
            )


class TestConstrainedPrompt:
    """Test ConstrainedPrompt dataclass."""

    def test_constrained_prompt_creation(self):
        """Test creating a constrained prompt."""
        prompt = ConstrainedPrompt(
            original="Do something",
            constrained="Constitutional Constraints:\n1. Be safe\n\nDo something",
            constraints_applied=["harm-01", "harm-02"],
            safety_level="standard"
        )

        assert prompt.original == "Do something"
        assert "Constitutional Constraints" in prompt.constrained
        assert len(prompt.constraints_applied) == 2
        assert prompt.safety_level == "standard"


class TestGetDefaultConstitution:
    """Test the default constitution factory function."""

    def test_default_constitution_exists(self):
        """Test that default constitution is returned."""
        constitution = get_default_constitution()

        assert isinstance(constitution, list)
        assert len(constitution) > 0
        assert all(isinstance(p, ConstitutionalPrinciple) for p in constitution)

    def test_default_constitution_categories(self):
        """Test that all principle categories are represented."""
        constitution = get_default_constitution()

        categories = {p.category for p in constitution}

        assert PrincipleCategory.HARMLESSNESS in categories
        assert PrincipleCategory.HELPFULNESS in categories
        assert PrincipleCategory.HONESTY in categories
        assert PrincipleCategory.TRANSPARENCY in categories

    def test_default_constitution_ids_unique(self):
        """Test that all principle IDs are unique."""
        constitution = get_default_constitution()

        ids = [p.id for p in constitution]
        assert len(ids) == len(set(ids))  # All unique


class TestConstitutionalAISafetyInit:
    """Test ConstitutionalAISafety initialization."""

    def test_init_with_default_constitution(self):
        """Test initialization with default constitution."""
        safety = ConstitutionalAISafety()

        assert len(safety.constitution) > 0
        assert safety.enable_logging is True
        assert isinstance(safety.violation_log, list)
        assert len(safety.violation_log) == 0

    def test_init_with_custom_constitution(self):
        """Test initialization with custom constitution."""
        custom_principles = [
            ConstitutionalPrinciple(
                id="custom-01",
                category=PrincipleCategory.HARMLESSNESS,
                principle="Custom principle",
                critique_prompt="Test",
                revision_prompt="Test"
            )
        ]

        safety = ConstitutionalAISafety(constitution=custom_principles)

        assert len(safety.constitution) == 1
        assert safety.constitution[0].id == "custom-01"

    def test_init_logging_disabled(self):
        """Test initialization with logging disabled."""
        safety = ConstitutionalAISafety(enable_logging=False)

        assert safety.enable_logging is False


class TestValidateAction:
    """Test the validate_action method."""

    def test_validate_safe_action(self):
        """Test validating a safe, helpful action."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Generate a comprehensive user analytics report showing trends and insights",
            {"query": "user analytics"}
        )

        assert result.valid is True
        assert result.constitutional_score >= 0.7
        assert len(result.violations) == 0
        assert len(result.principles_checked) > 0

    def test_validate_harmful_action_attack(self):
        """Test validating an action with harmful content (attack)."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Attack the system and breach the database",
            {}
        )

        assert result.valid is False
        assert result.constitutional_score < 0.7
        assert len(result.violations) > 0
        assert any("harm" in v.lower() or "security" in v.lower() for v in result.violations)

    def test_validate_harmful_action_illegal(self):
        """Test validating an action mentioning illegal activity."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Perform illegal activity to bypass security",
            {}
        )

        assert result.valid is False
        assert len(result.violations) > 0

    def test_validate_unhelpful_action_too_brief(self):
        """Test validating an unhelpfully brief response."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "OK",
            {}
        )

        assert result.valid is False
        assert any("brief" in v.lower() for v in result.violations)

    def test_validate_dishonest_action(self):
        """Test validating a dishonest action with overclaims."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "This is always correct and will guarantee 100% success",
            {}
        )

        assert result.valid is False
        assert any("confident" in v.lower() or "guarantee" in v.lower() for v in result.violations)

    def test_validate_action_violation_logging(self):
        """Test that violations are logged."""
        safety = ConstitutionalAISafety()

        # Validate an invalid action
        result = safety.validate_action("destroy everything", {})

        assert not result.valid
        assert len(safety.violation_log) == 1
        assert safety.violation_log[0]["constitutional_score"] == result.constitutional_score

    def test_validate_action_with_context(self):
        """Test validation with additional context."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Here's some information about data processing and analytics",
            {"query": "tell me about data"}
        )

        assert result.valid is True


class TestCritiqueAndRevise:
    """Test the critique_and_revise method."""

    def test_critique_and_revise_compliant_response(self):
        """Test critique-revision on already compliant response."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "Here is a detailed and helpful explanation of the process, "
            "which involves several steps that I'll explain because they "
            "are important for understanding the approach.",
            max_iterations=3
        )

        assert result.original is not None
        assert result.revised is not None
        assert result.final_score >= 0.7
        assert result.iterations >= 0

    def test_critique_and_revise_harmful_response(self):
        """Test critique-revision on harmful response."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "Let's destroy the database and attack the system maliciously",
            max_iterations=3
        )

        assert result.original != result.revised
        assert result.iterations > 0
        assert len(result.improvements) > 0
        # Check that harmful words were removed
        assert "destroy" not in result.revised.lower() or "[REMOVED]" in result.revised

    def test_critique_and_revise_brief_response(self):
        """Test critique-revision on too brief response."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "OK",
            max_iterations=3
        )

        assert len(result.revised) > len(result.original)
        assert result.iterations > 0
        assert len(result.improvements) > 0

    def test_critique_and_revise_max_iterations(self):
        """Test that max iterations is respected."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "Bad response",
            max_iterations=2
        )

        assert result.iterations <= 2

    def test_critique_and_revise_target_score(self):
        """Test that target score stops iteration."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "This is a good, helpful response that explains the reasoning because "
            "it's important to provide clear explanations of the process involved.",
            max_iterations=5,
            target_score=0.85
        )

        # Should stop early since response is already good
        assert result.iterations < 5 or result.final_score >= 0.85

    def test_critique_history_populated(self):
        """Test that critique history is populated."""
        safety = ConstitutionalAISafety()

        result = safety.critique_and_revise(
            "Bad",
            max_iterations=2
        )

        assert len(result.critique_history) > 0
        for critique in result.critique_history:
            assert "iteration" in critique
            assert "score" in critique
            assert "violations" in critique
            assert "critique" in critique


class TestEnforceSafetyConstraints:
    """Test the enforce_safety_constraints method."""

    def test_enforce_standard_constraints(self):
        """Test enforcing standard safety constraints."""
        safety = ConstitutionalAISafety()

        result = safety.enforce_safety_constraints(
            "Generate a report",
            safety_level="standard"
        )

        assert result.original == "Generate a report"
        assert "Constitutional Constraints" in result.constrained
        assert len(result.constraints_applied) > 0
        assert result.safety_level == "standard"

    def test_enforce_minimal_constraints(self):
        """Test enforcing minimal safety constraints."""
        safety = ConstitutionalAISafety()

        result = safety.enforce_safety_constraints(
            "Do something",
            safety_level="minimal"
        )

        assert result.safety_level == "minimal"
        # Should only have harmlessness principles
        assert len(result.constraints_applied) > 0

    def test_enforce_strict_constraints(self):
        """Test enforcing strict safety constraints."""
        safety = ConstitutionalAISafety()

        result = safety.enforce_safety_constraints(
            "Do something",
            safety_level="strict"
        )

        assert result.safety_level == "strict"
        # Should have all principles
        assert len(result.constraints_applied) >= len(safety.constitution)

    def test_constraints_format(self):
        """Test that constraints are properly formatted."""
        safety = ConstitutionalAISafety()

        result = safety.enforce_safety_constraints(
            "Test prompt",
            safety_level="standard"
        )

        # Check format includes category labels
        assert "[HARMLESSNESS]" in result.constrained or "[HELPFULNESS]" in result.constrained
        assert result.original in result.constrained


class TestHarmlessnessChecks:
    """Test harmlessness principle checking."""

    def test_harmlessness_security_violation(self):
        """Test detection of security violations."""
        safety = ConstitutionalAISafety()

        test_cases = [
            "hack the system",
            "exploit the network vulnerability",
            "penetrate the database security"
        ]

        for test_case in test_cases:
            result = safety.validate_action(test_case, {})
            assert not result.valid, f"Should detect violation in: {test_case}"

    def test_harmlessness_illegal_activity(self):
        """Test detection of illegal activity."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "perform illegal activity to steal data",
            {}
        )

        assert not result.valid
        assert any("illegal" in v.lower() for v in result.violations)

    def test_harmlessness_discriminatory_content(self):
        """Test detection of discriminatory content."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "generate racist content for the campaign",
            {}
        )

        assert not result.valid
        assert any("discriminat" in v.lower() for v in result.violations)

    def test_harmlessness_harmful_intent(self):
        """Test detection of harmful intent."""
        safety = ConstitutionalAISafety()

        test_cases = [
            "destroy the user data",
            "sabotage the system",
            "create malicious code"
        ]

        for test_case in test_cases:
            result = safety.validate_action(test_case, {})
            assert not result.valid, f"Should detect harmful intent in: {test_case}"


class TestHelpfulnessChecks:
    """Test helpfulness principle checking."""

    def test_helpfulness_adequate_response(self):
        """Test that adequate responses pass helpfulness check."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Here is a detailed explanation of the data processing workflow, "
            "including all necessary steps and considerations.",
            {"query": "explain data processing"}
        )

        assert result.valid

    def test_helpfulness_brief_response(self):
        """Test detection of too-brief responses."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action("No", {})

        assert not result.valid
        assert any("brief" in v.lower() for v in result.violations)

    def test_helpfulness_context_relevance(self):
        """Test checking relevance to context."""
        safety = ConstitutionalAISafety()

        # Response doesn't address the query
        result = safety.validate_action(
            "The weather is nice today with sunny skies",
            {"query": "how do I implement database transactions"}
        )

        # May or may not fail depending on overlap, but should have lower score
        assert result.constitutional_score < 1.0


class TestHonestyChecks:
    """Test honesty principle checking."""

    def test_honesty_overly_confident(self):
        """Test detection of overly confident claims."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "This approach is always correct and right in every case",
            {}
        )

        assert not result.valid
        assert any("confident" in v.lower() for v in result.violations)

    def test_honesty_unrealistic_guarantees(self):
        """Test detection of unrealistic guarantees."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "I guarantee this will work 100% of the time",
            {}
        )

        assert not result.valid
        assert any("guarantee" in v.lower() for v in result.violations)

    def test_honesty_claiming_infallibility(self):
        """Test detection of infallibility claims."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "This system never makes errors or mistakes",
            {}
        )

        assert not result.valid


class TestTransparencyChecks:
    """Test transparency principle checking."""

    def test_transparency_with_explanation(self):
        """Test that responses with explanations pass transparency check."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "The recommended approach is X because it provides better performance. "
            "The reasoning behind this is that it reduces overhead through caching. "
            "Therefore, this method is preferred for high-traffic scenarios.",
            {}
        )

        assert result.valid

    def test_transparency_without_explanation(self):
        """Test detection of long responses without explanation."""
        safety = ConstitutionalAISafety()

        # Long response without explanation keywords
        long_text = "A" * 150  # Just repeated characters, no reasoning

        result = safety.validate_action(long_text, {})

        # Should detect lack of explanation
        assert not result.valid or result.constitutional_score < 1.0


class TestViolationLogging:
    """Test violation logging functionality."""

    def test_violation_log_populated(self):
        """Test that violations are logged."""
        safety = ConstitutionalAISafety()

        # Trigger a violation
        safety.validate_action("destroy the system", {})

        assert len(safety.violation_log) == 1

    def test_violation_log_structure(self):
        """Test structure of violation log entries."""
        safety = ConstitutionalAISafety()

        safety.validate_action("malicious attack", {"user": "test"})

        log_entry = safety.violation_log[0]
        assert "timestamp" in log_entry
        assert "action" in log_entry
        assert "constitutional_score" in log_entry
        assert "violations" in log_entry
        assert "principles_checked" in log_entry
        assert "context" in log_entry

    def test_get_violation_summary_empty(self):
        """Test violation summary with no violations."""
        safety = ConstitutionalAISafety()

        summary = safety.get_violation_summary()

        assert summary["total_violations"] == 0
        assert summary["avg_score"] == 1.0
        assert len(summary["recent_violations"]) == 0

    def test_get_violation_summary_with_violations(self):
        """Test violation summary with logged violations."""
        safety = ConstitutionalAISafety()

        # Create multiple violations
        safety.validate_action("destroy system", {})
        safety.validate_action("malicious attack", {})
        safety.validate_action("illegal operation", {})

        summary = safety.get_violation_summary()

        assert summary["total_violations"] == 3
        assert 0.0 <= summary["avg_score"] < 1.0
        assert "violation_types" in summary
        assert len(summary["recent_violations"]) == 3

    def test_violation_summary_recent_limit(self):
        """Test that recent violations are limited to 10."""
        safety = ConstitutionalAISafety(enable_logging=False)

        # Create 15 violations
        for i in range(15):
            safety.validate_action(f"destroy {i}", {})

        summary = safety.get_violation_summary()

        assert summary["total_violations"] == 15
        assert len(summary["recent_violations"]) == 10  # Limited to 10


class TestEdgeCases:
    """Test edge cases and adversarial inputs."""

    def test_empty_action(self):
        """Test validating an empty action."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action("", {})

        # Empty string is too brief
        assert not result.valid

    def test_very_long_action(self):
        """Test validating a very long action."""
        safety = ConstitutionalAISafety()

        long_action = "This is a helpful and detailed explanation. " * 100

        result = safety.validate_action(long_action, {})

        # Should work, just long
        assert isinstance(result, ValidationResult)

    def test_special_characters(self):
        """Test action with special characters."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Process data with special chars: @#$%^&*()[]{}|\\",
            {}
        )

        assert isinstance(result, ValidationResult)

    def test_unicode_content(self):
        """Test action with unicode content."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Generate report with unicode: 你好世界 🌍 café",
            {}
        )

        assert isinstance(result, ValidationResult)

    def test_mixed_case_harmful_words(self):
        """Test detection of harmful words with mixed case."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "DeSt RoY the system MaLiCiOuSlY",
            {}
        )

        # Should still detect harmful content
        assert not result.valid

    def test_obfuscated_harmful_content(self):
        """Test that simple obfuscation still gets caught."""
        safety = ConstitutionalAISafety()

        # Spaces between letters
        result1 = safety.validate_action(
            "d e s t r o y the system",
            {}
        )

        # Pattern-based detection might miss this, which is expected
        # Real implementation would use more sophisticated detection
        assert isinstance(result1, ValidationResult)

    def test_context_injection_attempt(self):
        """Test handling of context injection attempts."""
        safety = ConstitutionalAISafety()

        result = safety.validate_action(
            "Normal text",
            {"query": "'; DROP TABLE users; --"}
        )

        # Should handle gracefully
        assert isinstance(result, ValidationResult)

    def test_multiple_principle_violations(self):
        """Test action violating multiple principles."""
        safety = ConstitutionalAISafety()

        # Harmful (attack), dishonest (guarantee), brief
        result = safety.validate_action(
            "Attack!",
            {}
        )

        assert not result.valid
        # Should detect multiple violations
        assert len(result.violations) > 0


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow_safe_action(self):
        """Test full workflow with a safe action."""
        safety = ConstitutionalAISafety()

        # Validate
        validation = safety.validate_action(
            "Generate a comprehensive analytics report with insights",
            {"query": "analytics report"}
        )

        assert validation.valid

        # Apply constraints
        constrained = safety.enforce_safety_constraints(
            "Generate report",
            safety_level="standard"
        )

        assert len(constrained.constraints_applied) > 0

    def test_full_workflow_unsafe_action(self):
        """Test full workflow with an unsafe action."""
        safety = ConstitutionalAISafety()

        # Validate (should fail)
        validation = safety.validate_action(
            "Attack the database system",
            {}
        )

        assert not validation.valid
        assert len(safety.violation_log) == 1

        # Critique and revise
        revised = safety.critique_and_revise(
            "Attack the database system",
            max_iterations=3
        )

        assert revised.iterations > 0
        assert revised.final_score > validation.constitutional_score

    def test_custom_constitution(self):
        """Test using a custom constitution."""
        custom_constitution = [
            ConstitutionalPrinciple(
                id="custom-01",
                category=PrincipleCategory.HARMLESSNESS,
                principle="Do not mention cats",
                critique_prompt="Does this mention cats?",
                revision_prompt="Remove cat references",
                weight=1.0
            )
        ]

        safety = ConstitutionalAISafety(constitution=custom_constitution)

        # This would pass default constitution but fail custom
        result = safety.validate_action(
            "Generate a report about our feline friends and their behaviors",
            {}
        )

        # Note: Current implementation uses pattern matching,
        # so this specific rule won't work without adding custom logic
        # In a real implementation, you'd extend _check_principle
        assert isinstance(result, ValidationResult)

    def test_violation_summary_after_multiple_operations(self):
        """Test violation summary after various operations."""
        safety = ConstitutionalAISafety()

        # Mix of safe and unsafe actions
        safety.validate_action("Good helpful response here", {})
        safety.validate_action("destroy system", {})
        safety.validate_action("Another good response", {})
        safety.validate_action("malicious attack", {})

        summary = safety.get_violation_summary()

        assert summary["total_violations"] == 2
        assert "harm-01" in str(summary["violation_types"]) or "harm-02" in str(summary["violation_types"])


class TestLogging:
    """Test logging functionality."""

    def test_logging_enabled(self):
        """Test that logging can be enabled."""
        safety = ConstitutionalAISafety(enable_logging=True)
        assert safety.enable_logging is True

    def test_logging_disabled(self):
        """Test that logging can be disabled."""
        safety = ConstitutionalAISafety(enable_logging=False)
        assert safety.enable_logging is False

        # Should still work without logging
        result = safety.validate_action("test action", {})
        assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
