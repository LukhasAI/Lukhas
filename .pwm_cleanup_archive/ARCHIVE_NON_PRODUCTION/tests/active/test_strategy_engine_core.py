"""
🧪 Strategy Engine Core Modules Integration Tests
═══════════════════════════════════════════════════════════════════════════

PURPOSE: Comprehensive tests for SRD + DMB + MEG integration
SCOPE: Unit tests, integration tests, and real-world scenarios
VALIDATION: Ensures the three modules work together as AGI governance foundation

📋 TEST COVERAGE:
- Self-Reflective Debugger (SRD) functionality
- Dynamic Modality Broker (DMB) hot-plugging
- Meta-Ethics Governor (MEG) ethical reasoning
- Cross-module integration scenarios
- Performance and reliability testing

🎯 SCENARIOS TESTED:
- Ethical reasoning with debugging instrumentation
- Modality registration with ethical approval
- Cross-cultural decision making with anomaly detection
- Human review triggers across all modules
- Real-time monitoring and governance

VERSION: v1.0.0 • CREATED: 2025-07-20 • AUTHOR: LUKHAS AGI TEAM
SYMBOLIC TAGS: ΛTEST, ΛINTEGRATION, ΛSRD, ΛDMB, ΛMEG
"""

import asyncio
import time

import pytest

from core.integration.dynamic_modality_broker import (
    BaseModality,
    DataType,
    DynamicModalityBroker,
    ModalityData,
    ModalityType,
)
from ethics.meta_ethics_governor import (
    CulturalContext,
    EthicalDecision,
    EthicalVerdict,
    MetaEthicsGovernor,
)

# Import the modules we're testing
from ethics.self_reflective_debugger import (
    AnomalyType,
    SelfReflectiveDebugger,
    get_srd,
    instrument_reasoning,
)


class TestSelfReflectiveDebugger:
    """Test suite for Self-Reflective Debugger"""

    @pytest.fixture
    async def srd(self):
        """Create SRD instance for testing"""
        srd = SelfReflectiveDebugger(enable_realtime=False)
        srd.start_monitoring()
        yield srd
        srd.stop_monitoring()

    @pytest.mark.asyncio
    async def test_srd_basic_functionality(self, srd):
        """Test basic SRD reasoning chain instrumentation"""

        # Begin reasoning chain
        chain_id = srd.begin_reasoning_chain(
            context="Test reasoning", symbolic_tags=["ΛTEST"]
        )

        assert chain_id is not None
        assert chain_id in srd.active_chains

        # Log reasoning steps
        step1 = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="test_operation_1",
            inputs={"input": "test"},
            outputs={"output": "result"},
            confidence=0.9,
            symbolic_tags=["ΛSTEP1"],
        )

        step2 = srd.log_reasoning_step(
            chain_id=chain_id,
            operation="test_operation_2",
            inputs={"input": "result"},
            outputs={"output": "final"},
            confidence=0.1,  # Low confidence to trigger anomaly
            symbolic_tags=["ΛSTEP2"],
        )

        assert step1 is not None
        assert step2 is not None
        assert len(srd.active_chains[chain_id]) == 2

        # Complete reasoning chain
        analysis = srd.complete_reasoning_chain(chain_id)

        assert chain_id not in srd.active_chains
        assert analysis["chain_id"] == chain_id
        assert analysis["total_steps"] == 2
        assert len(analysis["anomalies"]) > 0  # Should detect confidence collapse

    @pytest.mark.asyncio
    async def test_srd_anomaly_detection(self, srd):
        """Test SRD anomaly detection capabilities"""

        chain_id = srd.begin_reasoning_chain(context="Anomaly test")

        # Create step with anomalous characteristics
        srd.log_reasoning_step(
            chain_id=chain_id,
            operation="slow_operation",
            confidence=0.2,  # Very low confidence
            metadata={"processing_time": 15.0},  # Very slow
        )

        # Check that anomalies were detected
        analysis = srd.complete_reasoning_chain(chain_id)
        anomalies = analysis["anomalies"]

        assert len(anomalies) > 0
        assert any(
            anomaly.type == AnomalyType.CONFIDENCE_COLLAPSE for anomaly in anomalies
        )

    def test_srd_instrumentation_decorator(self):
        """Test the @instrument_reasoning decorator"""

        @instrument_reasoning
        def test_function(x, y):
            return x + y

        # This should work without throwing exceptions
        result = test_function(2, 3)
        assert result == 5

        # Check that SRD recorded the function call
        srd = get_srd()
        assert srd.performance_metrics["chains_processed"] > 0


class TestDynamicModalityBroker:
    """Test suite for Dynamic Modality Broker"""

    @pytest.fixture
    async def dmb(self):
        """Create DMB instance for testing"""
        dmb = DynamicModalityBroker()
        await dmb.start()
        yield dmb
        await dmb.stop()

    class MockModality(BaseModality):
        """Mock modality for testing"""

        def __init__(self, modality_id="test_modality"):
            super().__init__(modality_id, "Test Modality", ModalityType.SENSOR)
            self.initialized = False

        async def initialize(self) -> bool:
            self.initialized = True
            self.status = self.status.__class__.ACTIVE
            return True

        async def shutdown(self) -> bool:
            self.initialized = False
            self.status = self.status.__class__.INACTIVE
            return True

        async def process_data(self, data):
            if not self.initialized:
                return None

            return ModalityData(
                modality_id=self.modality_id,
                data_type=DataType.TEXT,
                payload=f"processed_{data.payload}",
                confidence=0.9,
            )

        def get_capabilities(self):
            return self.capabilities

        async def health_check(self) -> bool:
            return self.initialized

    @pytest.mark.asyncio
    async def test_dmb_modality_registration(self, dmb):
        """Test modality registration and management"""

        # Create and register a test modality
        test_modality = self.MockModality("test_sensor")

        success = await dmb.register_modality(test_modality)
        assert success is True

        # Check that modality is registered
        assert "test_sensor" in dmb.registered_modalities
        assert dmb.registered_modalities["test_sensor"].initialized is True

        # Test unregistration
        success = await dmb.unregister_modality("test_sensor")
        assert success is True
        assert "test_sensor" not in dmb.registered_modalities

    @pytest.mark.asyncio
    async def test_dmb_data_routing(self, dmb):
        """Test data routing between modalities"""

        # Register two test modalities
        source_modality = self.MockModality("source")
        target_modality = self.MockModality("target")

        await dmb.register_modality(source_modality)
        await dmb.register_modality(target_modality)

        # Set up data routing
        dmb.add_data_route("source", ["target"])

        # Send data to source modality
        test_data = ModalityData(
            modality_id="external", data_type=DataType.TEXT, payload="test_message"
        )

        success = await dmb.send_data("source", test_data)
        assert success is True

    @pytest.mark.asyncio
    async def test_dmb_status_reporting(self, dmb):
        """Test DMB status and capabilities reporting"""

        # Register a test modality
        test_modality = self.MockModality("status_test")
        await dmb.register_modality(test_modality)

        # Get status
        status = dmb.get_status()

        assert status["running"] is True
        assert "status_test" in status["registered_modalities"]
        assert "metrics" in status

        # Get capabilities summary
        capabilities = dmb.get_capabilities_summary()
        assert isinstance(capabilities, dict)


class TestMetaEthicsGovernor:
    """Test suite for Meta-Ethics Governor"""

    @pytest.fixture
    async def meg(self):
        """Create MEG instance for testing"""
        meg = MetaEthicsGovernor()
        yield meg

    @pytest.mark.asyncio
    async def test_meg_basic_evaluation(self, meg):
        """Test basic ethical decision evaluation"""

        # Create a test decision
        decision = EthicalDecision(
            action_type="data_collection",
            description="Collect user analytics for improvement",
            context={"involves_personal_data": True, "has_privacy_protection": True},
            cultural_context=CulturalContext.WESTERN,
            stakeholders=["users", "company"],
        )

        # Evaluate the decision
        evaluation = await meg.evaluate_decision(decision)

        assert evaluation.decision_id == decision.decision_id
        assert evaluation.verdict in [v for v in EthicalVerdict]
        assert 0.0 <= evaluation.confidence <= 1.0
        assert len(evaluation.reasoning) > 0

    @pytest.mark.asyncio
    async def test_meg_harmful_action_rejection(self, meg):
        """Test that MEG rejects harmful actions"""

        decision = EthicalDecision(
            action_type="user_manipulation",
            description="Manipulate user emotions for profit",
            context={"has_harm_potential": True, "involves_manipulation": True},
            cultural_context=CulturalContext.UNIVERSAL,
        )

        evaluation = await meg.evaluate_decision(decision)

        # Should be rejected due to harm potential
        assert evaluation.verdict == EthicalVerdict.REJECTED
        assert evaluation.human_review_required is True

    @pytest.mark.asyncio
    async def test_meg_cultural_adaptation(self, meg):
        """Test cultural adaptation in ethical reasoning"""

        # Same decision in different cultural contexts
        base_decision = {
            "action_type": "privacy_policy",
            "description": "Implement privacy controls",
            "context": {"involves_personal_data": True},
        }

        western_decision = EthicalDecision(
            **base_decision, cultural_context=CulturalContext.WESTERN
        )

        eastern_decision = EthicalDecision(
            **base_decision, cultural_context=CulturalContext.EASTERN
        )

        western_eval = await meg.evaluate_decision(western_decision)
        eastern_eval = await meg.evaluate_decision(eastern_decision)

        # Both should be approved but potentially with different confidence
        assert western_eval.verdict in [
            EthicalVerdict.APPROVED,
            EthicalVerdict.CONDITIONALLY_APPROVED,
        ]
        assert eastern_eval.verdict in [
            EthicalVerdict.APPROVED,
            EthicalVerdict.CONDITIONALLY_APPROVED,
        ]

    @pytest.mark.asyncio
    async def test_meg_quick_check(self, meg):
        """Test quick ethical check functionality"""

        # Test approved action
        approved = await meg.quick_ethical_check("help_user", {"beneficial": True})
        assert approved is True

        # Test potentially harmful action
        harmful = await meg.quick_ethical_check(
            "delete_data", {"has_harm_potential": True}
        )
        # Should be approved or conditionally approved, not necessarily rejected
        assert isinstance(harmful, bool)

    def test_meg_ethical_checkpoint_decorator(self):
        """Test the @ethical_checkpoint decorator"""

        @ethical_checkpoint(CulturalContext.UNIVERSAL)
        def beneficial_function():
            return "helping users"

        # This should work for beneficial functions
        result = beneficial_function()
        assert result == "helping users"


class TestIntegratedGovernanceScenarios:
    """Test integrated scenarios using all three modules"""

    @pytest.fixture
    async def governance_suite(self):
        """Set up full governance suite"""
        srd = SelfReflectiveDebugger(enable_realtime=False)
        dmb = DynamicModalityBroker()
        meg = MetaEthicsGovernor()

        srd.start_monitoring()
        await dmb.start()

        yield (srd, dmb, meg)

        srd.stop_monitoring()
        await dmb.stop()

    @pytest.mark.asyncio
    async def test_ethical_modality_registration(self, governance_suite):
        """Test ethically-governed modality registration"""

        srd, dmb, meg = governance_suite

        # Create an ethical decision for modality registration
        decision = EthicalDecision(
            action_type="register_camera",
            description="Register camera modality for user interaction",
            context={
                "involves_personal_data": True,
                "has_privacy_protection": True,
                "beneficial_purpose": True,
            },
            cultural_context=CulturalContext.WESTERN,
        )

        # Get ethical approval first
        evaluation = await meg.evaluate_decision(decision)

        if evaluation.verdict in [
            EthicalVerdict.APPROVED,
            EthicalVerdict.CONDITIONALLY_APPROVED,
        ]:
            # Begin reasoning chain for registration
            chain_id = srd.begin_reasoning_chain(
                context="Ethical modality registration",
                symbolic_tags=["ΛETHICAL", "ΛMODALITY"],
            )

            # Log the ethical evaluation step
            srd.log_reasoning_step(
                chain_id=chain_id,
                operation="ethical_evaluation",
                inputs={"decision": decision.action_type},
                outputs={"verdict": evaluation.verdict.value},
                confidence=evaluation.confidence,
                symbolic_tags=["ΛETHICS"],
            )

            # Create and register modality
            class EthicalTestModality(BaseModality):
                def __init__(self):
                    super().__init__(
                        "ethical_camera", "Ethical Camera", ModalityType.SENSOR
                    )

                async def initialize(self):
                    return True

                async def shutdown(self):
                    return True

                async def process_data(self, data):
                    return data

                def get_capabilities(self):
                    return []

                async def health_check(self):
                    return True

            test_modality = EthicalTestModality()
            registration_success = await dmb.register_modality(test_modality)

            # Log registration result
            srd.log_reasoning_step(
                chain_id=chain_id,
                operation="modality_registration",
                inputs={"modality_id": "ethical_camera"},
                outputs={"success": registration_success},
                confidence=1.0 if registration_success else 0.0,
                symbolic_tags=["ΛMODALITY"],
            )

            # Complete reasoning chain
            analysis = srd.complete_reasoning_chain(chain_id)

            assert registration_success is True
            assert analysis["total_steps"] == 2
            assert "ethical_camera" in dmb.registered_modalities

    @pytest.mark.asyncio
    async def test_cross_cultural_reasoning_with_monitoring(self, governance_suite):
        """Test cross-cultural ethical reasoning with SRD monitoring"""

        srd, dmb, meg = governance_suite

        # Create decisions for different cultural contexts
        contexts = [
            CulturalContext.WESTERN,
            CulturalContext.EASTERN,
            CulturalContext.NORDIC,
        ]

        for context in contexts:
            chain_id = srd.begin_reasoning_chain(
                context=f"Cross-cultural reasoning: {context.value}",
                symbolic_tags=["ΛCULTURAL", "ΛETHICS"],
            )

            decision = EthicalDecision(
                action_type="data_sharing",
                description="Share anonymized user data for research",
                context={
                    "involves_personal_data": True,
                    "data_anonymized": True,
                    "research_purpose": True,
                },
                cultural_context=context,
            )

            # Evaluate with MEG
            evaluation = await meg.evaluate_decision(decision)

            # Log the cultural reasoning step
            srd.log_reasoning_step(
                chain_id=chain_id,
                operation="cultural_ethical_evaluation",
                inputs={"context": context.value, "action": decision.action_type},
                outputs={
                    "verdict": evaluation.verdict.value,
                    "confidence": evaluation.confidence,
                },
                confidence=evaluation.confidence,
                symbolic_tags=["ΛCULTURAL", "ΛETHICS"],
            )

            analysis = srd.complete_reasoning_chain(chain_id)

            # All contexts should handle this reasonably
            assert evaluation.verdict in [
                EthicalVerdict.APPROVED,
                EthicalVerdict.CONDITIONALLY_APPROVED,
                EthicalVerdict.REQUIRES_REVIEW,
            ]
            assert analysis["total_steps"] == 1

    @pytest.mark.asyncio
    async def test_governance_performance_monitoring(self, governance_suite):
        """Test performance monitoring across all governance modules"""

        srd, dmb, meg = governance_suite

        # Run multiple governance operations
        for i in range(5):
            # SRD: reasoning chain
            chain_id = srd.begin_reasoning_chain(
                context=f"Performance test {i}", symbolic_tags=["ΛPERFORMANCE"]
            )

            # MEG: ethical decision
            decision = EthicalDecision(
                action_type=f"test_action_{i}",
                description="Performance testing action",
                cultural_context=CulturalContext.UNIVERSAL,
            )
            evaluation = await meg.evaluate_decision(decision)

            # Log in SRD
            srd.log_reasoning_step(
                chain_id=chain_id,
                operation="performance_test",
                confidence=evaluation.confidence,
                symbolic_tags=["ΛPERFORMANCE"],
            )

            srd.complete_reasoning_chain(chain_id)

        # Check performance metrics
        srd_summary = srd.get_anomaly_summary()
        dmb_status = dmb.get_status()
        meg_status = meg.get_status()

        assert srd_summary["performance_metrics"]["chains_processed"] == 5
        assert meg_status["metrics"]["decisions_evaluated"] >= 5
        assert dmb_status["running"] is True

    @pytest.mark.asyncio
    async def test_human_review_integration(self, governance_suite):
        """Test human review triggers across modules"""

        srd, dmb, meg = governance_suite

        # Create a scenario that should trigger human review
        chain_id = srd.begin_reasoning_chain(
            context="Human review test", symbolic_tags=["ΛREVIEW"]
        )

        # Create ethically ambiguous decision
        decision = EthicalDecision(
            action_type="ambiguous_action",
            description="Action with unclear ethical implications",
            context={
                "has_harm_potential": True,
                "has_benefit_potential": True,
                "unclear_consequences": True,
            },
            cultural_context=CulturalContext.UNIVERSAL,
        )

        evaluation = await meg.evaluate_decision(decision)

        # Log with low confidence to trigger SRD anomaly
        srd.log_reasoning_step(
            chain_id=chain_id,
            operation="ambiguous_evaluation",
            confidence=0.3,  # Low confidence
            symbolic_tags=["ΛAMBIGUOUS"],
        )

        analysis = srd.complete_reasoning_chain(chain_id)

        # Should trigger human review in MEG and anomaly detection in SRD
        assert evaluation.human_review_required is True
        assert len(analysis["anomalies"]) > 0


class TestPerformanceAndReliability:
    """Performance and reliability tests"""

    @pytest.mark.asyncio
    async def test_governance_suite_startup_time(self):
        """Test that governance suite starts up quickly"""

        start_time = time.time()

        srd = SelfReflectiveDebugger(enable_realtime=False)
        dmb = DynamicModalityBroker()
        meg = MetaEthicsGovernor()

        srd.start_monitoring()
        await dmb.start()

        startup_time = time.time() - start_time

        # Should start up in under 1 second
        assert startup_time < 1.0

        # Cleanup
        srd.stop_monitoring()
        await dmb.stop()

    @pytest.mark.asyncio
    async def test_concurrent_governance_operations(self):
        """Test concurrent operations across all modules"""

        srd = SelfReflectiveDebugger(enable_realtime=False)
        dmb = DynamicModalityBroker()
        meg = MetaEthicsGovernor()

        srd.start_monitoring()
        await dmb.start()

        # Create multiple concurrent tasks
        async def governance_task(task_id):
            # SRD chain
            chain_id = srd.begin_reasoning_chain(
                context=f"Concurrent task {task_id}", symbolic_tags=["ΛCONCURRENT"]
            )

            # MEG evaluation
            decision = EthicalDecision(
                action_type=f"concurrent_action_{task_id}",
                description="Concurrent testing",
                cultural_context=CulturalContext.UNIVERSAL,
            )
            evaluation = await meg.evaluate_decision(decision)

            # Log in SRD
            srd.log_reasoning_step(
                chain_id=chain_id,
                operation="concurrent_test",
                confidence=evaluation.confidence,
            )

            srd.complete_reasoning_chain(chain_id)
            return task_id

        # Run 10 concurrent governance operations
        tasks = [governance_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(isinstance(r, int) for r in results)

        # Cleanup
        srd.stop_monitoring()
        await dmb.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
