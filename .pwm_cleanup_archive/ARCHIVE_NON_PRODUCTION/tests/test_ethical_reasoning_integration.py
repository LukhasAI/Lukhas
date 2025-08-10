"""
Test suite for Ethical Reasoning System Integration
"""

import pytest

from reasoning.ethical_reasoning_integration import EthicalReasoningIntegration
from reasoning.ethical_reasoning_system import StakeholderType
from reasoning.reasoning_hub import ReasoningHub, get_reasoning_hub


class TestEthicalReasoningIntegration:
    """Test suite for ethical reasoning integration with reasoning hub"""

    @pytest.fixture
    async def reasoning_hub(self):
        """Create a test reasoning hub instance"""
        hub = ReasoningHub()
        return hub

    @pytest.fixture
    async def ethical_integration(self):
        """Create a test ethical reasoning integration instance"""
        config = {
            "enable_constraint_checking": True,
            "multi_framework_analysis": True,
            "value_alignment_active": True,
            "cultural_sensitivity": True,
        }
        integration = EthicalReasoningIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_ethical_reasoning_registration(self, reasoning_hub):
        """Test that ethical reasoning is registered in the hub"""
        # Verify ethical reasoning service is registered
        assert "ethical_reasoning" in reasoning_hub.services
        assert reasoning_hub.get_service("ethical_reasoning") is not None

    @pytest.mark.asyncio
    async def test_ethical_reasoning_initialization(self, reasoning_hub):
        """Test initialization of ethical reasoning through hub"""
        # Initialize the hub
        await reasoning_hub.initialize()

        # Verify ethical reasoning was initialized
        ethical_service = reasoning_hub.get_service("ethical_reasoning")
        assert ethical_service is not None
        assert hasattr(ethical_service, "is_initialized")

    @pytest.mark.asyncio
    async def test_evaluate_ethical_decision(self, ethical_integration):
        """Test evaluating an ethical decision"""
        # Initialize the integration
        await ethical_integration.initialize()

        # Test ethical question
        question = "Should the AI system prioritize user privacy over system performance optimization?"
        context = {
            "proposed_action": "maintain_strict_privacy",
            "alternatives": ["optimize_with_data_collection", "hybrid_approach"],
            "stakeholders": [
                StakeholderType.INDIVIDUAL_USER,
                StakeholderType.ORGANIZATION_OPERATING_AI,
            ],
            "high_stakes": False,
        }

        # Evaluate the decision
        judgment = await ethical_integration.evaluate_ethical_decision(
            question, context
        )

        # Verify judgment structure
        assert judgment is not None
        assert hasattr(judgment, "judgment_id")
        assert hasattr(judgment, "recommended_action_or_stance")
        assert hasattr(judgment, "overall_confidence_score")

    @pytest.mark.asyncio
    async def test_check_action_permissibility(self, ethical_integration):
        """Test checking if an action is permissible"""
        # Initialize the integration
        await ethical_integration.initialize()

        # Test action
        action = "share_anonymized_usage_data"
        maxim = "Share data only when it improves service for all users while maintaining privacy"
        context = {
            "data_type": "usage_patterns",
            "anonymization_level": "strong",
            "purpose": "service_improvement",
        }

        # Check permissibility
        result = await ethical_integration.check_action_permissibility(
            action, maxim, context
        )

        # Verify result structure
        assert "action" in result
        assert "permissible" in result
        assert "confidence" in result
        assert isinstance(result["permissible"], bool)
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_get_ethical_constraints(self, ethical_integration):
        """Test retrieving ethical constraints"""
        # Initialize the integration
        await ethical_integration.initialize()

        # Get all constraints
        all_constraints = await ethical_integration.get_ethical_constraints()
        assert isinstance(all_constraints, list)
        assert len(all_constraints) > 0

        # Get constraints by category
        safety_constraints = await ethical_integration.get_ethical_constraints("safety")
        assert isinstance(safety_constraints, list)
        assert all(c.constraint_category == "safety" for c in safety_constraints)

    @pytest.mark.asyncio
    async def test_supported_frameworks_and_principles(self, ethical_integration):
        """Test getting supported frameworks and principles"""
        # Get supported frameworks
        frameworks = ethical_integration.get_supported_frameworks()
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0
        assert "DEONTOLOGICAL" in frameworks
        assert "CONSEQUENTIALIST" in frameworks

        # Get moral principles
        principles = ethical_integration.get_moral_principles()
        assert isinstance(principles, list)
        assert len(principles) > 0
        assert "AUTONOMY" in principles
        assert "BENEFICENCE" in principles

        # Get stakeholder types
        stakeholders = ethical_integration.get_stakeholder_types()
        assert isinstance(stakeholders, list)
        assert len(stakeholders) > 0
        assert "INDIVIDUAL_USER" in stakeholders

    @pytest.mark.asyncio
    async def test_value_alignment_assessment(self, ethical_integration):
        """Test value alignment assessment"""
        # Initialize the integration
        await ethical_integration.initialize()

        # Assess value alignment
        assessment = await ethical_integration.assess_value_alignment()

        # Verify assessment structure
        assert assessment is not None
        assert hasattr(assessment, "assessment_id")
        assert hasattr(assessment, "overall_value_alignment_score")
        assert 0.0 <= assessment.overall_value_alignment_score <= 1.0

    @pytest.mark.asyncio
    async def test_awareness_update_integration(self, ethical_integration):
        """Test that ethical reasoning responds to awareness updates"""
        # Initialize the integration
        await ethical_integration.initialize()

        # Send awareness update
        awareness_state = {
            "level": "active",
            "timestamp": 12345.67,
            "connected_systems": 5,
        }

        # Update awareness
        await ethical_integration.update_awareness(awareness_state)

        # Verify configuration was updated
        assert ethical_integration.config["multi_framework_analysis"] is True
        assert ethical_integration.config["cultural_sensitivity"] is True

        # Test passive awareness
        awareness_state["level"] = "passive"
        await ethical_integration.update_awareness(awareness_state)

        # Verify configuration was updated for passive mode
        assert ethical_integration.config["multi_framework_analysis"] is False

    @pytest.mark.asyncio
    async def test_hub_integration_flow(self):
        """Test the complete integration flow through the reasoning hub"""
        # Create and initialize hub
        hub = get_reasoning_hub()
        await hub.initialize()

        # Get ethical reasoning service
        ethical_service = hub.get_service("ethical_reasoning")
        assert ethical_service is not None

        # Use the service
        question = "Is it ethical to modify user preferences without explicit consent if it improves their experience?"
        context = {
            "proposed_action": "modify_preferences_implicitly",
            "stakeholders": [StakeholderType.INDIVIDUAL_USER],
        }

        judgment = await ethical_service.evaluate_ethical_decision(question, context)
        assert judgment is not None
        assert judgment.ethical_question_analyzed == question


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
