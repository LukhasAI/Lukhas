import pytest
from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
from lukhas.governance.guardian.core import (
    GovernanceAction,
    EthicalSeverity,
)

class TestGuardianSystemImplementation:
    """
    Tests for the GuardianSystemImpl class.
    """

    def test_initialization(self):
        """
        Test that the GuardianSystemImpl can be initialized.
        """
        guardian = GuardianSystemImpl()
        assert guardian is not None
        assert guardian.drift_threshold == 0.15

    def test_initialization_with_custom_threshold(self):
        """
        Test that the GuardianSystemImpl can be initialized with a custom drift threshold.
        """
        guardian = GuardianSystemImpl(drift_threshold=0.25)
        assert guardian.drift_threshold == 0.25

    # --- Tests for _calculate_advanced_drift_score ---

    def test_calculate_drift_identical_strings(self):
        """Test drift score for identical strings, which should be 0."""
        guardian = GuardianSystemImpl()
        baseline = "This is a test sentence."
        current = "This is a test sentence."
        score = guardian._calculate_advanced_drift_score(baseline, current)
        assert score == 0.0

    def test_calculate_drift_completely_different_strings(self):
        """Test drift score for completely different strings."""
        guardian = GuardianSystemImpl()
        baseline = "The cat sat on the mat."
        current = "A dog ran through the park."
        score = guardian._calculate_advanced_drift_score(baseline, current)
        assert score > 0.9

    def test_calculate_drift_with_partial_overlap(self):
        """Test drift score with some common words."""
        guardian = GuardianSystemImpl()
        baseline = "The quick brown fox"
        current = "The slow brown dog"
        score = guardian._calculate_advanced_drift_score(baseline, current)
        assert 0.5 < score < 0.9

    def test_calculate_drift_with_empty_string(self):
        """Test drift score when one of the strings is empty."""
        guardian = GuardianSystemImpl()
        baseline = "This is a test."
        current = ""
        score = guardian._calculate_advanced_drift_score(baseline, current)
        assert score == 0.0  # Current implementation returns 0 for empty string

    # --- Tests for _evaluate_constitutional_compliance ---

    def test_evaluate_compliance_safe_action(self):
        """Test constitutional compliance for a safe action."""
        guardian = GuardianSystemImpl()
        action = GovernanceAction(type="log", details={"message": "User logged in"})
        context = {}
        decision = guardian._evaluate_constitutional_compliance(action, context)
        assert decision["compliant"] is True
        assert decision["severity"] == EthicalSeverity.LOW

    def test_evaluate_compliance_harmful_action(self):
        """Test constitutional compliance for a clearly harmful action."""
        guardian = GuardianSystemImpl()
        action = GovernanceAction(type="execute", details={"command": "harm user"})
        context = {}
        decision = guardian._evaluate_constitutional_compliance(action, context)
        assert decision["compliant"] is False
        assert decision["severity"] == EthicalSeverity.HIGH
        assert "potential harm detected" in decision["reason"]

    def test_evaluate_compliance_risky_context(self):
        """Test constitutional compliance when context indicates risk."""
        guardian = GuardianSystemImpl()
        action = GovernanceAction(type="log", details={"message": "Normal action"})
        context = {"risk_indicators": ["bias_amplification"]}
        decision = guardian._evaluate_constitutional_compliance(action, context)
        assert decision["compliant"] is False
        assert decision["severity"] == EthicalSeverity.HIGH
        assert "Context contains constitutional AI violations" in decision["reason"]

    # --- Tests for _detect_comprehensive_safety_violations ---

    def test_detect_safety_violations_safe_content(self):
        """Test safety violation detection for safe content."""
        guardian = GuardianSystemImpl()
        content = "This is a perfectly safe and friendly sentence."
        violations = guardian._detect_comprehensive_safety_violations(content)
        assert len(violations) == 0

    def test_detect_safety_violations_harmful_content(self):
        """Test safety violation detection for content with harmful patterns."""
        guardian = GuardianSystemImpl()
        content = "This content talks about violence and abuse."
        violations = guardian._detect_comprehensive_safety_violations(content)
        assert len(violations) == 2
        patterns = {v["pattern"] for v in violations}
        assert "violence" in patterns
        assert "abuse" in patterns

    def test_detect_safety_violations_privacy_content(self):
        """Test safety violation detection for content with privacy concerns."""
        guardian = GuardianSystemImpl()
        content = "Please share your personal data with us."
        violations = guardian._detect_comprehensive_safety_violations(content)
        assert len(violations) == 1
        assert violations[0]["type"] == "privacy_violation"
        assert violations[0]["pattern"] == "personal data"
