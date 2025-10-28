"""
Comprehensive Test Suite for SEEDRA Ethics Integration
=====================================================

Tests the complete SEEDRA (Structured Ethical Evaluation, Decision-making, 
and Reasoning Architecture) system integration including:

- EthicalSeedManager functionality and decision-making
- ReasoningValidator chain validation and fallacy detection  
- ConstitutionalEvaluator compliance checking and violation detection
- Full integration workflow testing
- Performance and edge case validation

Test Categories:
- Unit tests for individual components
- Integration tests for component interaction
- Performance tests for real-world scenarios
- Edge case and error handling tests
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import SEEDRA components
from ethics.seedra.seedra_core.ethical_seed_manager import (
    EthicalSeedManager,
    EthicalSeed,
    EthicalPrinciple,
    EthicalSeverity,
    EthicalDecisionContext,
    EthicalDecisionResult,
)

from ethics.seedra.seedra_core.reasoning_validator import (
    ReasoningValidator,
    ReasoningChain,
    ReasoningStep,
    ReasoningType,
    ReasoningQuality,
    ReasoningValidationResult,
)

from ethics.seedra.seedra_core.constitutional_evaluator import (
    ConstitutionalEvaluator,
    ConstitutionalEvaluation,
    ConstitutionalPrinciple,
    ConstitutionalRule,
    ComplianceFramework,
    ViolationSeverity,
)


class TestEthicalSeedManager:
    """Test suite for EthicalSeedManager functionality."""
    
    @pytest.fixture
    def ethical_manager(self):
        """Create an EthicalSeedManager instance for testing."""
        return EthicalSeedManager()
    
    @pytest.fixture
    def sample_decision_context(self):
        """Create a sample decision context for testing."""
        return EthicalDecisionContext(
            decision_id="test_decision_001",
            context="Testing privacy data collection",
            stakeholders=["users", "system", "administrators"],
            potential_impacts=["privacy", "utility", "security"],
            ethical_constraints=["user_consent", "data_minimization"],
            metadata={"test_mode": True}
        )
    
    def test_ethical_seed_creation(self, ethical_manager):
        """Test creating and managing ethical seeds."""
        seed = EthicalSeed(
            seed_id="privacy_seed_001",
            principle=EthicalPrinciple.PRIVACY,
            weight=0.8,
            conditions=["user_data_involved", "consent_required"],
            description="Protect user privacy"
        )
        
        ethical_manager.add_seed(seed)
        
        assert ethical_manager.get_seed("privacy_seed_001") == seed
        assert len(ethical_manager.get_active_seeds()) == 1
        assert seed.principle == EthicalPrinciple.PRIVACY
    
    @pytest.mark.asyncio
    async def test_ethical_decision_evaluation(self, ethical_manager, sample_decision_context):
        """Test ethical decision evaluation process."""
        # Add relevant ethical seeds
        privacy_seed = EthicalSeed(
            seed_id="privacy_seed",
            principle=EthicalPrinciple.PRIVACY,
            weight=0.9,
            conditions=["user_data"],
            description="Privacy protection"
        )
        
        autonomy_seed = EthicalSeed(
            seed_id="autonomy_seed", 
            principle=EthicalPrinciple.AUTONOMY,
            weight=0.7,
            conditions=["user_choice"],
            description="User autonomy"
        )
        
        ethical_manager.add_seed(privacy_seed)
        ethical_manager.add_seed(autonomy_seed)
        
        # Evaluate decision
        result = await ethical_manager.evaluate_decision(sample_decision_context)
        
        assert isinstance(result, EthicalDecisionResult)
        assert result.decision_id == "test_decision_001"
        assert len(result.activated_seeds) > 0
        assert result.overall_score >= 0.0 and result.overall_score <= 1.0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_bias_detection(self, ethical_manager):
        """Test bias detection in ethical reasoning."""
        context = EthicalDecisionContext(
            decision_id="bias_test",
            context="Automated hiring decision",
            stakeholders=["candidates", "company"],
            potential_impacts=["fairness", "efficiency"],
            ethical_constraints=["non_discrimination"],
            metadata={"historical_bias": True}
        )
        
        result = await ethical_manager.evaluate_decision(context)
        
        # Should detect potential bias issues
        assert any("bias" in rec.lower() for rec in result.recommendations)
        assert result.ethical_concerns is not None
        assert len(result.ethical_concerns) > 0
    
    def test_ethical_principle_weighting(self, ethical_manager):
        """Test proper weighting of ethical principles."""
        # Add seeds with different weights
        high_weight_seed = EthicalSeed(
            seed_id="critical_safety",
            principle=EthicalPrinciple.BENEFICENCE,
            weight=1.0,
            conditions=["safety_critical"],
            description="Critical safety"
        )
        
        low_weight_seed = EthicalSeed(
            seed_id="minor_efficiency",
            principle=EthicalPrinciple.UTILITY,
            weight=0.2,
            conditions=["efficiency_gain"],
            description="Minor efficiency"
        )
        
        ethical_manager.add_seed(high_weight_seed)
        ethical_manager.add_seed(low_weight_seed)
        
        # Get weighted seeds
        weighted_seeds = ethical_manager.get_weighted_seeds()
        
        assert len(weighted_seeds) == 2
        # High weight seed should be prioritized
        assert weighted_seeds[0][1] > weighted_seeds[1][1]


class TestReasoningValidator:
    """Test suite for ReasoningValidator functionality."""
    
    @pytest.fixture
    def reasoning_validator(self):
        """Create a ReasoningValidator instance for testing."""
        return ReasoningValidator()
    
    @pytest.fixture
    def sample_reasoning_chain(self):
        """Create a sample reasoning chain for testing."""
        steps = [
            ReasoningStep(
                step_id="premise_1",
                reasoning_type=ReasoningType.PREMISE,
                content="All users have privacy rights",
                premises=[],
                conclusion=None
            ),
            ReasoningStep(
                step_id="premise_2", 
                reasoning_type=ReasoningType.PREMISE,
                content="This action involves user data",
                premises=[],
                conclusion=None
            ),
            ReasoningStep(
                step_id="deduction_1",
                reasoning_type=ReasoningType.DEDUCTIVE,
                content="Therefore, this action must respect privacy rights",
                premises=["premise_1", "premise_2"],
                conclusion="privacy_respect_required"
            )
        ]
        
        return ReasoningChain(
            chain_id="test_chain_001",
            steps=steps,
            context="Privacy decision reasoning",
            metadata={"test_mode": True}
        )
    
    @pytest.mark.asyncio
    async def test_reasoning_chain_validation(self, reasoning_validator, sample_reasoning_chain):
        """Test validation of reasoning chains."""
        result = await reasoning_validator.validate_reasoning(sample_reasoning_chain)
        
        assert isinstance(result, ReasoningValidationResult)
        assert result.chain_id == "test_chain_001"
        assert result.is_valid is not None
        assert result.quality_score >= 0.0 and result.quality_score <= 1.0
        assert len(result.validation_details) > 0
    
    @pytest.mark.asyncio
    async def test_fallacy_detection(self, reasoning_validator):
        """Test detection of logical fallacies."""
        # Create reasoning chain with ad hominem fallacy
        fallacy_steps = [
            ReasoningStep(
                step_id="premise_1",
                reasoning_type=ReasoningType.PREMISE,
                content="Person X made this proposal",
                premises=[],
                conclusion=None
            ),
            ReasoningStep(
                step_id="ad_hominem",
                reasoning_type=ReasoningType.DEDUCTIVE,
                content="Person X is unreliable, therefore the proposal is bad",
                premises=["premise_1"],
                conclusion="proposal_rejected"
            )
        ]
        
        fallacy_chain = ReasoningChain(
            chain_id="fallacy_test",
            steps=fallacy_steps,
            context="Fallacy detection test",
            metadata={"test_mode": True}
        )
        
        result = await reasoning_validator.validate_reasoning(fallacy_chain)
        
        # Should detect fallacy
        assert len(result.detected_fallacies) > 0
        assert "ad_hominem" in [f.fallacy_type for f in result.detected_fallacies]
        assert result.quality_score < 0.7  # Lower quality due to fallacy
    
    @pytest.mark.asyncio
    async def test_circular_reasoning_detection(self, reasoning_validator):
        """Test detection of circular reasoning."""
        circular_steps = [
            ReasoningStep(
                step_id="premise_1",
                reasoning_type=ReasoningType.PREMISE,
                content="A is true because B is true",
                premises=[],
                conclusion="A_true"
            ),
            ReasoningStep(
                step_id="premise_2",
                reasoning_type=ReasoningType.PREMISE,
                content="B is true because A is true",
                premises=[],
                conclusion="B_true"
            )
        ]
        
        circular_chain = ReasoningChain(
            chain_id="circular_test",
            steps=circular_steps,
            context="Circular reasoning test",
            metadata={"circular": True}
        )
        
        result = await reasoning_validator.validate_reasoning(circular_chain)
        
        # Should detect circular reasoning
        assert len(result.structural_issues) > 0
        assert any("circular" in issue.lower() for issue in result.structural_issues)
    
    def test_reasoning_quality_assessment(self, reasoning_validator):
        """Test quality assessment of reasoning chains."""
        # Test high-quality reasoning
        high_quality_steps = [
            ReasoningStep(
                step_id="evidence_1",
                reasoning_type=ReasoningType.EVIDENCE,
                content="Scientific study shows X",
                premises=[],
                conclusion=None
            ),
            ReasoningStep(
                step_id="evidence_2",
                reasoning_type=ReasoningType.EVIDENCE,
                content="Independent research confirms X",
                premises=[],
                conclusion=None
            ),
            ReasoningStep(
                step_id="conclusion",
                reasoning_type=ReasoningType.DEDUCTIVE,
                content="Therefore, X is well-supported",
                premises=["evidence_1", "evidence_2"],
                conclusion="X_supported"
            )
        ]
        
        quality_chain = ReasoningChain(
            chain_id="quality_test",
            steps=high_quality_steps,
            context="Quality assessment",
            metadata={"test": True}
        )
        
        quality_score = reasoning_validator.assess_reasoning_quality(quality_chain)
        
        assert quality_score >= 0.7  # Should be high quality
        assert isinstance(quality_score, float)


class TestConstitutionalEvaluator:
    """Test suite for ConstitutionalEvaluator functionality."""
    
    @pytest.fixture
    def constitutional_evaluator(self):
        """Create a ConstitutionalEvaluator instance for testing."""
        return ConstitutionalEvaluator()
    
    @pytest.fixture
    def sample_evaluation_context(self):
        """Create a sample evaluation context."""
        return {
            "decision": "Collect user location data for service improvement",
            "affected_parties": ["users", "service_providers"],
            "data_types": ["location", "behavioral"],
            "purpose": "service_improvement",
            "consent_obtained": False,
            "data_retention": "indefinite"
        }
    
    @pytest.mark.asyncio
    async def test_constitutional_evaluation(self, constitutional_evaluator, sample_evaluation_context):
        """Test constitutional evaluation of decisions."""
        evaluation = await constitutional_evaluator.evaluate_decision(sample_evaluation_context)
        
        assert isinstance(evaluation, ConstitutionalEvaluation)
        assert evaluation.overall_compliance >= 0.0 and evaluation.overall_compliance <= 1.0
        assert len(evaluation.principle_evaluations) > 0
        assert evaluation.violations is not None
    
    @pytest.mark.asyncio 
    async def test_gdpr_compliance_checking(self, constitutional_evaluator):
        """Test GDPR compliance checking."""
        gdpr_context = {
            "decision": "Process EU citizen data",
            "data_types": ["personal", "sensitive"],
            "legal_basis": "consent",
            "consent_obtained": True,
            "data_subject_rights": ["access", "deletion"],
            "data_retention": "2_years",
            "third_party_sharing": False
        }
        
        evaluation = await constitutional_evaluator.evaluate_decision(gdpr_context)
        
        # Should have good GDPR compliance
        gdpr_evaluation = next(
            (pe for pe in evaluation.principle_evaluations 
             if pe.principle.name == "GDPR_COMPLIANCE"), 
            None
        )
        
        assert gdpr_evaluation is not None
        assert gdpr_evaluation.compliance_score > 0.7
    
    @pytest.mark.asyncio
    async def test_human_rights_violation_detection(self, constitutional_evaluator):
        """Test detection of human rights violations."""
        violation_context = {
            "decision": "Deny service based on political views",
            "discrimination_basis": "political_opinion",
            "affected_groups": ["political_minorities"],
            "justification": "business_policy",
            "alternative_options": []
        }
        
        evaluation = await constitutional_evaluator.evaluate_decision(violation_context)
        
        # Should detect human rights violations
        assert len(evaluation.violations) > 0
        assert any(v.severity == ViolationSeverity.HIGH for v in evaluation.violations)
        assert any("discrimination" in v.description.lower() for v in evaluation.violations)
    
    @pytest.mark.asyncio
    async def test_ai_act_compliance(self, constitutional_evaluator):
        """Test EU AI Act compliance checking."""
        ai_context = {
            "decision": "Deploy AI system for hiring",
            "ai_system_type": "high_risk",
            "use_case": "employment",
            "transparency": True,
            "human_oversight": True,
            "bias_testing": True,
            "documentation": True
        }
        
        evaluation = await constitutional_evaluator.evaluate_decision(ai_context)
        
        # Should check AI Act compliance
        ai_evaluation = next(
            (pe for pe in evaluation.principle_evaluations 
             if "AI_ACT" in pe.principle.name), 
            None
        )
        
        assert ai_evaluation is not None
        assert ai_evaluation.compliance_score > 0.8  # Good compliance
    
    def test_constitutional_principle_loading(self, constitutional_evaluator):
        """Test loading of constitutional principles."""
        principles = constitutional_evaluator.get_constitutional_principles()
        
        assert len(principles) > 0
        assert any(p.name == "HUMAN_DIGNITY" for p in principles)
        assert any(p.name == "PRIVACY_RIGHTS" for p in principles)
        assert any(p.name == "NON_DISCRIMINATION" for p in principles)
    
    def test_violation_severity_assessment(self, constitutional_evaluator):
        """Test assessment of violation severity."""
        # Test high severity violation
        high_severity = constitutional_evaluator.assess_violation_severity(
            violation_type="human_rights",
            impact_scope="widespread",
            harm_potential="severe"
        )
        
        assert high_severity == ViolationSeverity.HIGH
        
        # Test low severity violation
        low_severity = constitutional_evaluator.assess_violation_severity(
            violation_type="procedural",
            impact_scope="limited", 
            harm_potential="minimal"
        )
        
        assert low_severity == ViolationSeverity.LOW


class TestSEEDRAIntegration:
    """Integration tests for the complete SEEDRA system."""
    
    @pytest.fixture
    def seedra_system(self):
        """Create a complete SEEDRA system for integration testing."""
        return {
            "ethical_manager": EthicalSeedManager(),
            "reasoning_validator": ReasoningValidator(),
            "constitutional_evaluator": ConstitutionalEvaluator()
        }
    
    @pytest.fixture
    def complex_ethical_scenario(self):
        """Create a complex ethical scenario for testing."""
        return {
            "context": EthicalDecisionContext(
                decision_id="complex_scenario_001",
                context="AI-powered medical diagnosis system deployment",
                stakeholders=["patients", "doctors", "hospital", "society"],
                potential_impacts=["health_outcomes", "privacy", "autonomy", "justice"],
                ethical_constraints=["medical_ethics", "privacy_laws", "safety_standards"],
                metadata={"domain": "healthcare", "ai_involved": True}
            ),
            "reasoning": ReasoningChain(
                chain_id="medical_reasoning",
                steps=[
                    ReasoningStep(
                        step_id="medical_premise",
                        reasoning_type=ReasoningType.PREMISE,
                        content="AI diagnosis improves accuracy",
                        premises=[],
                        conclusion=None
                    ),
                    ReasoningStep(
                        step_id="privacy_concern",
                        reasoning_type=ReasoningType.PREMISE,
                        content="Medical data is highly sensitive",
                        premises=[],
                        conclusion=None
                    ),
                    ReasoningStep(
                        step_id="ethical_conclusion",
                        reasoning_type=ReasoningType.DEDUCTIVE,
                        content="Deployment requires strong privacy safeguards",
                        premises=["medical_premise", "privacy_concern"],
                        conclusion="privacy_safeguards_required"
                    )
                ],
                context="Medical AI ethics",
                metadata={"domain": "healthcare"}
            ),
            "constitutional_context": {
                "decision": "Deploy AI medical diagnosis system",
                "data_types": ["medical", "personal", "sensitive"],
                "purpose": "healthcare_improvement",
                "consent_model": "informed_consent",
                "oversight": "medical_professional",
                "transparency": "explainable_ai"
            }
        }
    
    @pytest.mark.asyncio
    async def test_complete_seedra_workflow(self, seedra_system, complex_ethical_scenario):
        """Test the complete SEEDRA evaluation workflow."""
        ethical_manager = seedra_system["ethical_manager"]
        reasoning_validator = seedra_system["reasoning_validator"] 
        constitutional_evaluator = seedra_system["constitutional_evaluator"]
        
        # Add relevant ethical seeds
        healthcare_seed = EthicalSeed(
            seed_id="healthcare_ethics",
            principle=EthicalPrinciple.BENEFICENCE,
            weight=0.95,
            conditions=["healthcare", "patient_safety"],
            description="Healthcare ethics"
        )
        
        privacy_seed = EthicalSeed(
            seed_id="medical_privacy",
            principle=EthicalPrinciple.PRIVACY,
            weight=0.9,
            conditions=["medical_data", "sensitive_data"],
            description="Medical privacy protection"
        )
        
        ethical_manager.add_seed(healthcare_seed)
        ethical_manager.add_seed(privacy_seed)
        
        # Step 1: Ethical evaluation
        ethical_result = await ethical_manager.evaluate_decision(
            complex_ethical_scenario["context"]
        )
        
        # Step 2: Reasoning validation
        reasoning_result = await reasoning_validator.validate_reasoning(
            complex_ethical_scenario["reasoning"]
        )
        
        # Step 3: Constitutional evaluation
        constitutional_result = await constitutional_evaluator.evaluate_decision(
            complex_ethical_scenario["constitutional_context"]
        )
        
        # Validate integrated results
        assert ethical_result.overall_score > 0.0
        assert reasoning_result.is_valid
        assert constitutional_result.overall_compliance > 0.0
        
        # Check that all components provided meaningful feedback
        assert len(ethical_result.recommendations) > 0
        assert len(reasoning_result.validation_details) > 0
        assert len(constitutional_result.principle_evaluations) > 0
    
    @pytest.mark.asyncio
    async def test_ethical_conflict_resolution(self, seedra_system):
        """Test resolution of ethical conflicts between principles."""
        ethical_manager = seedra_system["ethical_manager"]
        
        # Create conflicting seeds
        utility_seed = EthicalSeed(
            seed_id="utility_max",
            principle=EthicalPrinciple.UTILITY,
            weight=0.8,
            conditions=["efficiency"],
            description="Maximize utility"
        )
        
        privacy_seed = EthicalSeed(
            seed_id="privacy_protect",
            principle=EthicalPrinciple.PRIVACY,
            weight=0.8,
            conditions=["data_collection"],
            description="Protect privacy"
        )
        
        ethical_manager.add_seed(utility_seed)
        ethical_manager.add_seed(privacy_seed)
        
        # Create conflicting scenario
        conflict_context = EthicalDecisionContext(
            decision_id="conflict_test",
            context="Collect detailed user data for service optimization",
            stakeholders=["users", "service"],
            potential_impacts=["privacy_reduction", "service_improvement"],
            ethical_constraints=["privacy_protection", "utility_maximization"],
            metadata={"conflict_scenario": True}
        )
        
        result = await ethical_manager.evaluate_decision(conflict_context)
        
        # Should handle conflict gracefully
        assert result.ethical_concerns is not None
        assert len(result.ethical_concerns) > 0
        assert any("conflict" in concern.lower() for concern in result.ethical_concerns)
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, seedra_system, complex_ethical_scenario):
        """Test performance benchmarks for SEEDRA components."""
        import time
        
        ethical_manager = seedra_system["ethical_manager"]
        reasoning_validator = seedra_system["reasoning_validator"]
        constitutional_evaluator = seedra_system["constitutional_evaluator"]
        
        # Benchmark ethical evaluation
        start_time = time.time()
        await ethical_manager.evaluate_decision(complex_ethical_scenario["context"])
        ethical_time = time.time() - start_time
        
        # Benchmark reasoning validation
        start_time = time.time()
        await reasoning_validator.validate_reasoning(complex_ethical_scenario["reasoning"])
        reasoning_time = time.time() - start_time
        
        # Benchmark constitutional evaluation
        start_time = time.time()
        await constitutional_evaluator.evaluate_decision(complex_ethical_scenario["constitutional_context"])
        constitutional_time = time.time() - start_time
        
        # Performance assertions (should complete within reasonable time)
        assert ethical_time < 1.0  # Less than 1 second
        assert reasoning_time < 0.5  # Less than 500ms
        assert constitutional_time < 1.0  # Less than 1 second
        
        total_time = ethical_time + reasoning_time + constitutional_time
        assert total_time < 2.0  # Total workflow under 2 seconds
    
    def test_seedra_error_handling(self, seedra_system):
        """Test error handling in SEEDRA components."""
        ethical_manager = seedra_system["ethical_manager"]
        reasoning_validator = seedra_system["reasoning_validator"]
        constitutional_evaluator = seedra_system["constitutional_evaluator"]
        
        # Test invalid inputs
        with pytest.raises((ValueError, TypeError)):
            invalid_context = EthicalDecisionContext(
                decision_id="",  # Invalid empty ID
                context=None,    # Invalid None context
                stakeholders=[],
                potential_impacts=[],
                ethical_constraints=[],
                metadata={}
            )
        
        # Test graceful degradation
        minimal_context = EthicalDecisionContext(
            decision_id="minimal_test",
            context="Minimal test scenario",
            stakeholders=["test"],
            potential_impacts=["test"],
            ethical_constraints=[],
            metadata={}
        )
        
        # Should handle minimal input gracefully
        try:
            asyncio.run(ethical_manager.evaluate_decision(minimal_context))
        except Exception as e:
            pytest.fail(f"Should handle minimal input gracefully: {e}")


class TestSEEDRAEdgeCases:
    """Test edge cases and boundary conditions for SEEDRA."""
    
    @pytest.mark.asyncio
    async def test_empty_ethical_seeds(self):
        """Test behavior with no ethical seeds."""
        ethical_manager = EthicalSeedManager()
        
        context = EthicalDecisionContext(
            decision_id="empty_seeds_test",
            context="Test with no ethical seeds",
            stakeholders=["test"],
            potential_impacts=["test"],
            ethical_constraints=[],
            metadata={}
        )
        
        result = await ethical_manager.evaluate_decision(context)
        
        # Should handle gracefully
        assert result is not None
        assert result.activated_seeds == []
        assert result.overall_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_malformed_reasoning_chain(self):
        """Test handling of malformed reasoning chains."""
        reasoning_validator = ReasoningValidator()
        
        # Create malformed chain
        malformed_steps = [
            ReasoningStep(
                step_id="",  # Empty ID
                reasoning_type=ReasoningType.PREMISE,
                content="",  # Empty content
                premises=["nonexistent_premise"],  # Non-existent premise
                conclusion=None
            )
        ]
        
        malformed_chain = ReasoningChain(
            chain_id="malformed_test",
            steps=malformed_steps,
            context="Test malformed chain",
            metadata={}
        )
        
        result = await reasoning_validator.validate_reasoning(malformed_chain)
        
        # Should detect issues
        assert not result.is_valid
        assert len(result.structural_issues) > 0
        assert result.quality_score < 0.5
    
    @pytest.mark.asyncio
    async def test_extreme_constitutional_violations(self):
        """Test handling of extreme constitutional violations."""
        constitutional_evaluator = ConstitutionalEvaluator()
        
        extreme_violation_context = {
            "decision": "Implement mass surveillance with no oversight",
            "privacy_protections": None,
            "consent": False,
            "transparency": False,
            "discrimination": True,
            "human_rights_impact": "severe_violation"
        }
        
        evaluation = await constitutional_evaluator.evaluate_decision(extreme_violation_context)
        
        # Should detect severe violations
        assert evaluation.overall_compliance < 0.3
        assert len(evaluation.violations) > 0
        assert any(v.severity == ViolationSeverity.CRITICAL for v in evaluation.violations)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])