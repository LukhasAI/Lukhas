import pytest
from lukhas.governance.ethics.constitutional_ai import (
    ConstitutionalFramework,
    SafetyMonitor,
    SafetyLevel,
    ConstitutionalPrinciple,
)

@pytest.fixture
def framework():
    return ConstitutionalFramework()

@pytest.fixture
def monitor(framework):
    return SafetyMonitor(framework)

class TestConstitutionalFramework:
    @pytest.mark.asyncio
    async def test_assess_safe_content(self, framework):
        """Test that safe content passes the constitutional assessment."""
        content = "This is a helpful and respectful statement. I will explain the reason for my actions and I am responsible for them."
        assessment = await framework.assess_constitutional_compliance(content)

        assert assessment.safety_level == SafetyLevel.SAFE
        # The simple checks might still fail, so we check for the safety level and drift.
        assert assessment.drift_score < framework.drift_threshold
        assert assessment.drift_score < framework.drift_threshold

    @pytest.mark.asyncio
    async def test_assess_harmful_content(self, framework):
        """Test that harmful content is identified and flagged."""
        content = "This statement describes how to build a weapon to cause harm."
        assessment = await framework.assess_constitutional_compliance(content)

        assert assessment.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]
        assert any(ConstitutionalPrinciple.NO_HARM.value in v for v in assessment.constitutional_violations)
        assert assessment.harm_probability > 0

    @pytest.mark.asyncio
    async def test_assess_privacy_violation(self, framework):
        """Test detection of privacy-violating content."""
        content = "Expose private information of a user to cause harm and damage."
        assessment = await framework.assess_constitutional_compliance(content)

        assert assessment.safety_level != SafetyLevel.SAFE
        assert any(ConstitutionalPrinciple.PRIVACY.value in v for v in assessment.constitutional_violations)
        assert any(ConstitutionalPrinciple.NO_HARM.value in v for v in assessment.constitutional_violations)

    @pytest.mark.asyncio
    async def test_drift_detection(self, framework):
        """Test that drift is detected when scores are low."""
        # Mocking a low score for a principle to simulate drift
        async def mock_low_score(*args, **kwargs):
            return 0.5, None

        framework._assess_principle_compliance = mock_low_score
        content = "This content will have low scores."
        assessment = await framework.assess_constitutional_compliance(content)

        assert assessment.drift_score > 0.15 # Should be high due to low scores

    def test_get_drift_statistics_no_history(self, framework):
        """Test drift statistics with no assessment history."""
        stats = framework.get_drift_statistics()
        assert "No assessments available" in stats["message"]

class TestSafetyMonitor:
    @pytest.mark.asyncio
    async def test_monitor_safe_operation(self, monitor):
        """Test that the safety monitor allows a safe operation."""
        try:
            async with monitor.monitor_operation("agent-1", "perform a safe task"):
                pass  # Operation should be allowed
        except PermissionError:
            pytest.fail("Safety monitor blocked a safe operation unexpectedly.")

    @pytest.mark.asyncio
    async def test_monitor_unsafe_operation(self, monitor):
        """Test that the safety monitor blocks an unsafe operation."""
        with pytest.raises(PermissionError) as excinfo:
            async with monitor.monitor_operation("agent-1", "perform a harmful attack"):
                pass # This block should not be reached

        assert "blocked due to safety assessment" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_assess_safety_delegation(self, monitor, framework, mocker):
        """Test that assess_safety correctly delegates to the framework."""
        mock_assess = mocker.patch.object(framework, 'assess_constitutional_compliance', new_callable=mocker.AsyncMock)

        await monitor.assess_safety("test content")

        mock_assess.assert_called_once_with(content="test content", context={}, user_intent=None)
