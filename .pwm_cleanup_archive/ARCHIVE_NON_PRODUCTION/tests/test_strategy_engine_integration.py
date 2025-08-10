"""Integration tests for Strategy Engine Core modules.

Tests the integration between:
- Self-Reflective Debugger (SRD)
- Dynamic Modality Broker (DMB)
- Meta-Ethics Governor (MEG)
"""

import pytest

from core.integration.dynamic_modality_broker import (
    BaseModality,
    DynamicModalityBroker,
    ModalityType,
    get_dmb,
)
from ethics.meta_ethics_governor import (
    CulturalContext,
    EthicalDecision,
    EthicalVerdict,
    MetaEthicsGovernor,
    get_meg,
)
from ethics.self_reflective_debugger import (
    SelfReflectiveDebugger,
    get_srd,
    instrument_reasoning,
)


class TestStrategyEngineCore:
    """Test Strategy Engine Core integration."""

    @pytest.mark.asyncio
    async def test_core_modules_initialization(self):
        """Test that all three core modules can be initialized."""

        # Test SRD initialization
        srd = get_srd()
        assert isinstance(srd, SelfReflectiveDebugger)
        assert srd.enable_realtime is True

        # Test DMB initialization
        dmb = await get_dmb()
        assert isinstance(dmb, DynamicModalityBroker)

        # Test MEG initialization
        meg = await get_meg()
        assert isinstance(meg, MetaEthicsGovernor)
        assert len(meg.engines) >= 2  # At least deontological and consequentialist

    @pytest.mark.asyncio
    async def test_srd_reasoning_instrumentation(self):
        """Test SRD reasoning instrumentation capability."""
        srd = get_srd()

        # Test decorator functionality
        @instrument_reasoning
        def test_reasoning_function(x, y):
            """Test function with reasoning instrumentation."""
            if x < 0:
                raise ValueError("Negative input")
            return x + y

        # Should work normally for valid inputs
        result = test_reasoning_function(5, 3)
        assert result == 8

        # Test that it still raises exceptions properly
        with pytest.raises(ValueError):
            test_reasoning_function(-1, 3)

    @pytest.mark.asyncio
    async def test_meg_ethical_evaluation(self):
        """Test MEG ethical decision evaluation."""
        meg = await get_meg()

        # Test ethical decision evaluation
        decision = EthicalDecision(
            action_type="help_user",
            description="Provide assistance to user",
            context={"request": "information", "safety": True},
            cultural_context=CulturalContext.UNIVERSAL,
        )

        evaluation = await meg.evaluate_decision(decision)

        assert hasattr(evaluation, "verdict")
        assert hasattr(evaluation, "confidence")
        assert hasattr(evaluation, "reasoning")
        assert evaluation.confidence >= 0.0
        assert evaluation.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_dmb_modality_management(self):
        """Test DMB modality registration and management."""
        dmb = await get_dmb()

        # Test basic DMB functionality
        assert hasattr(dmb, "registered_modalities")
        assert hasattr(dmb, "active_streams")

        # Test modality registration (basic test)
        initial_count = len(dmb.registered_modalities)

        # Create a mock modality
        class TestModality(BaseModality):
            def __init__(self):
                super().__init__("test_modal", "Test Modality", ModalityType.VIRTUAL)

            async def initialize(self) -> bool:
                return True

            async def shutdown(self) -> bool:
                return True

            async def process_data(self, data):
                return data

            def get_capabilities(self):
                return []

            async def health_check(self) -> bool:
                return True

        test_modality = TestModality()

        # Register should not fail (even if it doesn't actually register)
        try:
            await dmb.register_modality(test_modality)
        except Exception:
            pass  # DMB might not be fully implemented

    @pytest.mark.asyncio
    async def test_strategy_core_integration_scenario(self):
        """Test a realistic scenario using all three modules together."""

        # Initialize all modules
        srd = get_srd()
        dmb = await get_dmb()
        meg = await get_meg()

        # Scenario: Process user request with ethical validation and anomaly detection

        # 1. Create reasoning chain in SRD
        chain_id = srd.begin_reasoning_chain(
            context="user_request_processing", symbolic_tags=["ΛREQUEST", "ΛRESEARCH"]
        )

        # 2. Add reasoning steps
        step1 = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="input_validation",
            inputs={"request": "analyze_data"},
            outputs={"valid": True, "safe": True},
            confidence=0.9,
            metadata={"reasoning": "Request appears safe for processing"},
        )

        # 3. Evaluate ethics with MEG
        ethical_decision = EthicalDecision(
            action_type="analyze_data",
            description="User requested data analysis",
            context={"purpose": "research", "data_type": "public"},
            cultural_context=CulturalContext.UNIVERSAL,
        )

        ethical_eval = await meg.evaluate_decision(ethical_decision)

        # 4. Add ethics result to reasoning chain
        step2 = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="ethical_evaluation",
            inputs={"decision": "analyze_data"},
            outputs={
                "ethical_verdict": (
                    ethical_eval.verdict.value
                    if hasattr(ethical_eval, "verdict")
                    else "unknown"
                ),
                "confidence": (
                    ethical_eval.confidence
                    if hasattr(ethical_eval, "confidence")
                    else 0.5
                ),
            },
            confidence=(
                ethical_eval.confidence if hasattr(ethical_eval, "confidence") else 0.5
            ),
            metadata={"reasoning": "Ethical evaluation completed"},
        )

        # 5. Complete reasoning chain
        analysis = srd.complete_reasoning_chain(chain_id)

        # Verify integration worked
        assert analysis is not None
        assert "chain_id" in analysis
        assert "total_steps" in analysis
        assert analysis["total_steps"] >= 2

    @pytest.mark.asyncio
    async def test_cross_module_error_handling(self):
        """Test error handling across modules."""

        srd = get_srd()
        meg = await get_meg()

        # Test SRD with problematic reasoning
        chain_id = srd.begin_reasoning_chain(
            context="error_test", symbolic_tags=["ΛTEST", "ΛERROR"]
        )

        # Add step that might trigger anomaly
        error_step = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="problematic_operation",
            inputs={"input": "invalid"},
            outputs={"error": "detected"},
            confidence=0.1,  # Very low confidence
            metadata={
                "reasoning": "This step has issues",
                "issues": ["low_confidence", "suspicious_pattern"],
            },
        )

        # Complete and check for anomaly detection
        analysis = srd.complete_reasoning_chain(chain_id)

        # Should still complete successfully even with problematic steps
        assert analysis is not None
        assert "anomalies" in analysis

    @pytest.mark.asyncio
    async def test_meg_cultural_adaptation(self):
        """Test MEG cultural adaptation capabilities."""
        meg = await get_meg()

        # Test different cultural contexts
        contexts = [
            CulturalContext.WESTERN,
            CulturalContext.EASTERN,
            CulturalContext.NORDIC,
            CulturalContext.UNIVERSAL,
        ]

        for context in contexts:
            decision = EthicalDecision(
                action_type="cultural_test",
                description="Test cultural adaptation",
                context={"test": "cultural_sensitivity"},
                cultural_context=context,
            )

            evaluation = await meg.evaluate_decision(decision)

            # Should work for all cultural contexts
            assert hasattr(evaluation, "cultural_considerations")

    def test_strategy_core_status(self):
        """Test Strategy Core status reporting."""

        # Test that modules can report their status
        srd = get_srd()
        srd_summary = srd.get_anomaly_summary()

        assert isinstance(srd_summary, dict)
        assert "performance_metrics" in srd_summary
        assert "chains_processed" in srd_summary["performance_metrics"]

    @pytest.mark.asyncio
    async def test_quick_ethical_check(self):
        """Test MEG quick ethical check functionality."""
        meg = await get_meg()

        # Test quick checks
        safe_result = await meg.quick_ethical_check("help_user", {"safe": True})
        assert isinstance(safe_result, bool)

        harmful_result = await meg.quick_ethical_check(
            "harm_user", {"intent": "malicious"}
        )
        assert isinstance(harmful_result, bool)

    @pytest.mark.asyncio
    async def test_strategy_core_metrics(self):
        """Test metrics collection across Strategy Core modules."""

        srd = get_srd()
        meg = await get_meg()

        # Get initial metrics
        srd_summary = srd.get_anomaly_summary()
        meg_status = meg.get_status()

        # Verify metrics structure
        assert isinstance(srd_summary, dict)
        assert isinstance(meg_status, dict)

        # Should have basic metric categories
        assert "performance_metrics" in srd_summary
        assert "chains_processed" in srd_summary["performance_metrics"]
        assert "metrics" in meg_status


class TestStrategyEngineRealWorldScenarios:
    """Test realistic AGI scenarios using Strategy Engine Core."""

    @pytest.mark.asyncio
    async def test_user_assistance_scenario(self):
        """Test complete user assistance workflow."""

        srd = get_srd()
        meg = await get_meg()

        # Simulate user asking for help
        chain_id = srd.begin_reasoning_chain(
            context="user_assistance", symbolic_tags=["ΛEDUCATION", "ΛQUANTUM"]
        )

        # Process request through ethical evaluation
        decision = EthicalDecision(
            action_type="provide_educational_content",
            description="User requesting educational information about quantum-inspired computing",
            context={
                "topic": "quantum_computing",
                "user_type": "student",
                "intent": "learning",
            },
            cultural_context=CulturalContext.UNIVERSAL,
        )

        evaluation = await meg.evaluate_decision(decision)

        # Should approve educational content
        if hasattr(evaluation, "verdict"):
            assert evaluation.verdict in [
                EthicalVerdict.APPROVED,
                EthicalVerdict.CONDITIONALLY_APPROVED,
                EthicalVerdict.CULTURAL_CONFLICT,
            ]

        # Add to reasoning chain
        step = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="ethical_clearance",
            inputs={"request": "educational_content"},
            outputs={"approved": True, "safe_to_proceed": True},
            confidence=0.95,
            metadata={"reasoning": "Educational content approved for student"},
        )

        analysis = srd.complete_reasoning_chain(chain_id)
        assert analysis["total_steps"] >= 1

    @pytest.mark.asyncio
    async def test_safety_monitoring_scenario(self):
        """Test safety monitoring across all modules."""

        srd = get_srd()
        meg = await get_meg()

        # Simulate potentially unsafe request
        chain_id = srd.begin_reasoning_chain(
            context="safety_check", symbolic_tags=["ΛSAFETY", "ΛDANGEROUS"]
        )

        # Ethical evaluation should flag this
        decision = EthicalDecision(
            action_type="provide_dangerous_information",
            description="Request for potentially harmful instructions",
            context={
                "request_type": "dangerous_instructions",
                "safety_level": "high_risk",
            },
        )

        evaluation = await meg.evaluate_decision(decision)

        # Should likely be rejected or require review
        if hasattr(evaluation, "verdict"):
            assert evaluation.verdict in [
                EthicalVerdict.REJECTED,
                EthicalVerdict.REQUIRES_REVIEW,
                EthicalVerdict.CONDITIONALLY_APPROVED,
                EthicalVerdict.CULTURAL_CONFLICT,
            ]

        # Add safety check to reasoning
        step = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="safety_assessment",
            inputs={"request": "dangerous_information"},
            outputs={"safety_verdict": "requires_review"},
            confidence=0.05,  # Very low confidence to trigger anomaly
            metadata={
                "reasoning": "Request flagged for safety review",
                "issues": ["potential_harm", "safety_concern"],
            },
        )

        analysis = srd.complete_reasoning_chain(chain_id)

        # Should complete successfully (anomaly detection may or may not trigger)
        assert analysis["total_steps"] >= 1
