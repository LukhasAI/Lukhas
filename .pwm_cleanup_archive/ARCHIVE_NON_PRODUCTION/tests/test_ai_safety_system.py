#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Safety System

IMPORTANT: These tests use MOCK implementations where real external services
(OpenAI API, NIAS Core, etc.) are not available. All mocks are clearly documented.

Test Coverage:
- Constitutional Safety Layer
- Adversarial Safety Testing
- Predictive Harm Prevention
- Multi-Agent Consensus
- AI Safety Orchestrator

Metadata:
- Created: 2025-01-30
- Version: 1.0.0
- Environment: Development/Testing
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict

import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import safety components
try:
    from core.safety.adversarial_testing import (
        AdversarialSafetyTester,
        AttackVector,
        get_adversarial_tester,
    )
    from core.safety.ai_safety_orchestrator import (
        AISafetyOrchestrator,
        SafetyMode,
        get_ai_safety_orchestrator,
    )
    from core.safety.constitutional_safety import (
        NIASConstitutionalSafety,
        SafetyEvaluation,
        SafetyViolationType,
        get_constitutional_safety,
    )
    from core.safety.multi_agent_consensus import (
        AgentRole,
        MultiAgentSafetyConsensus,
        get_multi_agent_consensus,
    )
    from core.safety.predictive_harm_prevention import (
        HarmType,
        PredictiveHarmPrevention,
        get_predictive_harm_prevention,
    )

    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import safety components: {e}")
    IMPORTS_AVAILABLE = False


class MockOpenAIResponse:
    """Mock OpenAI API response for testing"""

    def __init__(self, content: str = None, function_call: Dict[str, Any] = None):
        self.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "obj",
                        (object,),
                        {
                            "content": content,
                            "function_call": (
                                type(
                                    "obj",
                                    (object,),
                                    {
                                        "arguments": (
                                            json.dumps(function_call)
                                            if function_call
                                            else "{}"
                                        )
                                    },
                                )
                                if function_call
                                else None
                            ),
                        },
                    )()
                },
            )
        ]


class MockOpenAI:
    """Mock OpenAI client for testing"""

    class Chat:
        class Completions:
            async def create(self, **kwargs):
                # Return different responses based on the function being called
                if kwargs.get("function_call", {}).get("name") == "evaluate_safety":
                    return MockOpenAIResponse(
                        function_call={
                            "is_safe": False,
                            "risk_score": 0.7,
                            "confidence": 0.85,
                            "primary_concerns": [
                                "emotional_manipulation",
                                "child_safety",
                            ],
                            "risk_factors": {
                                "emotional_manipulation": 0.8,
                                "vulnerable_exploitation": 0.6,
                                "consent_issues": 0.3,
                                "privacy_risk": 0.2,
                                "attention_overload": 0.4,
                            },
                        }
                    )
                elif kwargs.get("function_call", {}).get("name") == "vote_on_proposal":
                    return MockOpenAIResponse(
                        function_call={
                            "decision": "reject",
                            "confidence": 0.9,
                            "reasoning": "This action could harm vulnerable users",
                            "conditions": ["age_verification", "parental_consent"],
                            "concerns": ["child_safety", "emotional_manipulation"],
                        }
                    )
                else:
                    return MockOpenAIResponse(content="Mock AI response for testing")

    def __init__(self, api_key=None):
        self.chat = self.Chat()
        self.chat.completions = self.Chat.Completions()


class TestResults:
    """Container for test results with metadata"""

    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        self.environment = {
            "type": "MOCK",
            "openai": "MOCKED",
            "nias_core": "MOCKED",
            "python_version": "3.9+",
            "async_enabled": True,
        }

    def add_result(
        self,
        test_name: str,
        passed: bool,
        details: Dict[str, Any],
        execution_time: float,
    ):
        self.results.append(
            {
                "test_name": test_name,
                "passed": passed,
                "details": details,
                "execution_time_ms": execution_time * 1000,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def generate_report(self) -> Dict[str, Any]:
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])

        return {
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "environment": self.environment,
            },
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            },
            "results": self.results,
        }


# Global test results container
test_results = TestResults()


class TestConstitutionalSafety:
    """Test Constitutional AI Safety Layer"""

    @pytest.mark.asyncio
    async def test_safety_evaluation_with_mock(self):
        """Test safety evaluation with mocked OpenAI"""
        start_time = datetime.now()

        # Create safety instance with mock
        safety = NIASConstitutionalSafety()
        safety.openai = MockOpenAI()

        # Test case: Child targeted manipulation
        action_data = {
            "message": "Hey kids! Buy this now before your parents find out!",
            "visual_elements": ["bright_colors", "cartoon_characters"],
            "urgency_indicators": True,
        }

        user_context = {
            "user_id": "test_child_001",
            "age": 10,
            "emotional_state": {"excitement": 0.8},
        }

        # Evaluate safety
        evaluation = await safety.evaluate_safety(
            action_type="marketing_message",
            action_data=action_data,
            user_context=user_context,
        )

        # Verify results
        assert not evaluation.is_safe, "Child manipulation should be marked unsafe"
        assert evaluation.risk_score > 0.5, "Risk score should be high"
        assert (
            "emotional_manipulation" in evaluation.violated_principles
            or "protect_vulnerable" in evaluation.violated_principles
        )

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_safety_evaluation_with_mock",
            passed=True,
            details={
                "evaluation": {
                    "is_safe": evaluation.is_safe,
                    "risk_score": evaluation.risk_score,
                    "violated_principles": evaluation.violated_principles,
                    "confidence": evaluation.confidence,
                },
                "mock_used": "OpenAI API",
            },
            execution_time=execution_time,
        )

    @pytest.mark.asyncio
    async def test_basic_heuristic_evaluation(self):
        """Test heuristic evaluation without AI"""
        start_time = datetime.now()

        # Create safety instance without OpenAI
        safety = NIASConstitutionalSafety()

        # Test case: Financial product to elderly user
        evaluation = await safety.evaluate_safety(
            action_type="financial_product",
            action_data={"product": "high_risk_investment"},
            user_context={"age": 75, "user_id": "elderly_001"},
        )

        # Verify heuristic caught the issue
        assert not evaluation.is_safe
        assert "protect_vulnerable" in evaluation.violated_principles

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_basic_heuristic_evaluation",
            passed=True,
            details={
                "evaluation": {
                    "is_safe": evaluation.is_safe,
                    "violated_principles": evaluation.violated_principles,
                    "used_heuristics": True,
                }
            },
            execution_time=execution_time,
        )


class TestAdversarialTesting:
    """Test Adversarial Safety Testing System"""

    @pytest.mark.asyncio
    async def test_prompt_injection_detection(self):
        """Test detection of prompt injection attacks"""
        start_time = datetime.now()

        # Create tester with mock
        tester = AdversarialSafetyTester()
        tester.openai = MockOpenAI()

        # Mock NIAS core for testing
        class MockNIASCore:
            async def push_symbolic_message(self, message, context):
                # Simulate detection of prompt injection
                if "ignore all previous instructions" in str(message).lower():
                    return {"blocked": True, "reason": "prompt_injection_detected"}
                return {"allowed": True}

        tester.nias_core = MockNIASCore()

        # Generate critical test cases
        critical_tests = tester._get_critical_test_cases()
        prompt_injection_test = next(
            t
            for t in critical_tests
            if t.attack_vector == AttackVector.PROMPT_INJECTION
        )

        # Execute test
        result = await tester._execute_test(prompt_injection_test)

        # Verify defense
        assert result.passed, "System should defend against prompt injection"
        assert result.actual_response.get("blocked") == True

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_prompt_injection_detection",
            passed=True,
            details={
                "attack_vector": "prompt_injection",
                "defense_successful": result.passed,
                "mock_components": ["OpenAI API", "NIAS Core"],
            },
            execution_time=execution_time,
        )


class TestPredictiveHarmPrevention:
    """Test Predictive Harm Prevention System"""

    @pytest.mark.asyncio
    async def test_addiction_prediction(self):
        """Test addiction harm prediction"""
        start_time = datetime.now()

        # Create harm prevention system
        harm_prevention = PredictiveHarmPrevention()

        # Test case: High usage pattern
        current_state = {
            "usage_stats": {"daily_hours": 8},
            "emotional_state": {"stress": 0.7},
        }

        # Use basic prediction (no AI)
        predictions = await harm_prevention.predict_harm_trajectory(
            user_id="test_user_addiction",
            current_state=current_state,
            planned_actions=[{"type": "continue_usage"}],
        )

        # Verify addiction risk detected
        addiction_predictions = [
            p for p in predictions if p.harm_type == HarmType.ADDICTION
        ]
        assert len(addiction_predictions) > 0
        assert addiction_predictions[0].probability > 0.7

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_addiction_prediction",
            passed=True,
            details={
                "predictions": [
                    {
                        "harm_type": p.harm_type.value,
                        "probability": p.probability,
                        "severity": p.severity,
                    }
                    for p in predictions
                ],
                "used_heuristics": True,
            },
            execution_time=execution_time,
        )


class TestMultiAgentConsensus:
    """Test Multi-Agent Safety Consensus System"""

    @pytest.mark.asyncio
    async def test_child_protection_consensus(self):
        """Test unanimous consensus requirement for child safety"""
        start_time = datetime.now()

        # Create consensus system with mock
        consensus = MultiAgentSafetyConsensus()
        consensus.openai = MockOpenAI()

        # Test case: Action affecting a child
        result = await consensus.evaluate_action(
            action_type="marketing",
            action_data={"content": "Special offer just for you!"},
            context={"user_age": 10},
        )

        # Verify unanimous rejection for child
        assert result.final_decision == "reject"
        assert result.requires_human_review

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_child_protection_consensus",
            passed=True,
            details={
                "final_decision": result.final_decision,
                "vote_breakdown": result.vote_breakdown,
                "requires_human_review": result.requires_human_review,
                "mock_used": "OpenAI API for agent decisions",
            },
            execution_time=execution_time,
        )


class TestAISafetyOrchestrator:
    """Test AI Safety Orchestrator Integration"""

    @pytest.mark.asyncio
    async def test_comprehensive_safety_evaluation(self):
        """Test full safety evaluation pipeline"""
        start_time = datetime.now()

        # Create orchestrator with mocks
        orchestrator = AISafetyOrchestrator()
        orchestrator.openai = MockOpenAI()

        # Mock the components
        orchestrator.constitutional_safety.openai = MockOpenAI()
        orchestrator.consensus_system.openai = MockOpenAI()
        orchestrator.harm_prevention.openai = None  # Use heuristics

        # Test case: High-risk action
        decision = await orchestrator.evaluate_action(
            action_type="urgent_financial_offer",
            action_data={
                "message": "Act now! Limited time offer!",
                "pressure_tactics": True,
            },
            user_context={
                "user_id": "test_user",
                "age": 16,
                "emotional_state": {"anxiety": 0.8},
            },
        )

        # Verify comprehensive protection
        assert decision.final_decision in ["block", "defer"]
        assert decision.confidence > 0.7

        execution_time = (datetime.now() - start_time).total_seconds()
        test_results.add_result(
            "test_comprehensive_safety_evaluation",
            passed=True,
            details={
                "decision": decision.final_decision,
                "confidence": decision.confidence,
                "safety_mode": decision.safety_mode.value,
                "mock_components": ["OpenAI API", "All safety layers"],
            },
            execution_time=execution_time,
        )


async def run_all_safety_tests():
    """Run all safety tests and generate report"""
    logger.info("Starting AI Safety System Tests")
    logger.info("NOTE: Using MOCK implementations for external services")

    if not IMPORTS_AVAILABLE:
        logger.error("Cannot run tests - imports failed")
        return None

    # Run all test classes
    test_classes = [
        TestConstitutionalSafety(),
        TestAdversarialTesting(),
        TestPredictiveHarmPrevention(),
        TestMultiAgentConsensus(),
        TestAISafetyOrchestrator(),
    ]

    for test_class in test_classes:
        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                try:
                    method = getattr(test_class, method_name)
                    await method()
                    logger.info(f"✓ {method_name} passed")
                except Exception as e:
                    logger.error(f"✗ {method_name} failed: {e}")
                    test_results.add_result(
                        method_name,
                        passed=False,
                        details={"error": str(e)},
                        execution_time=0,
                    )

    # Generate and return report
    report = test_results.generate_report()

    # Save report
    with open("ai_safety_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    logger.info(
        f"\nTest Summary: {report['summary']['passed']}/{report['summary']['total_tests']} passed"
    )
    logger.info("Report saved to ai_safety_test_report.json")

    return report


if __name__ == "__main__":
    # Run tests
    report = asyncio.run(run_all_safety_tests())

    if report:
        print("\n" + "=" * 50)
        print("AI SAFETY SYSTEM TEST REPORT")
        print("=" * 50)
        print(f"Environment: {report['metadata']['environment']['type']}")
        print(f"Duration: {report['metadata']['duration_seconds']:.2f} seconds")
        print(
            f"\nResults: {report['summary']['passed']}/{report['summary']['total_tests']} tests passed"
        )
        print(f"Pass Rate: {report['summary']['pass_rate']*100:.1f}%")
        print(
            "\nNOTE: All external services (OpenAI, NIAS Core) were MOCKED for testing"
        )
        print("=" * 50)
