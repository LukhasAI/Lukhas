"""
Tests for the LUKHAS Decision Explainability Framework
"""

import pytest
import asyncio
from datetime import datetime
from core.explainability import (
    ExplanationLevel, ExplanationType, DecisionFactor,
    DecisionExplanation, get_decision_explainer,
    explain_decision, get_decision_comparison,
    get_decision_counterfactuals
)

class TestDecisionFactor:
    """Test DecisionFactor functionality"""
    
    def test_factor_creation(self):
        """Test creating a decision factor"""
        factor = DecisionFactor(
            name="Safety",
            value="risk level: high",
            weight=0.8,
            influence="negative",
            explanation="High risk level strongly influenced this choice",
            tags={"#TAG:safety", "#TAG:risk"}
        )
        
        assert factor.name == "Safety"
        assert factor.weight == 0.8
        assert factor.influence == "negative"
        assert "#TAG:safety" in factor.tags

class TestDecisionExplanation:
    """Test DecisionExplanation functionality"""
    
    def test_explanation_creation(self):
        """Test creating a decision explanation"""
        factors = [
            DecisionFactor("Safety", "high risk", 0.8, "negative", "High risk", {"#TAG:safety"}),
            DecisionFactor("Efficiency", "low usage", 0.6, "positive", "Efficient", {"#TAG:resource"})
        ]
        
        explanation = DecisionExplanation(
            decision_id="test-123",
            summary="Chose safe option despite efficiency trade-off",
            factors=factors,
            confidence_explanation="80% confidence due to clear safety concerns",
            process_steps=["Evaluated options", "Applied safety rules", "Selected safest"],
            alternatives_comparison={"Fast option": "Too risky"},
            counterfactuals=["If risk were lower"],
            relevant_tags={"#TAG:safety", "#TAG:decision"},
            hormonal_state={"cortisol": 0.7, "dopamine": 0.3}
        )
        
        assert explanation.decision_id == "test-123"
        assert len(explanation.factors) == 2
        assert explanation.hormonal_state["cortisol"] == 0.7
        
    def test_summary_level_explanation(self):
        """Test summary level human-readable output"""
        explanation = DecisionExplanation(
            decision_id="test-123",
            summary="Chose safe option despite efficiency trade-off",
            factors=[],
            confidence_explanation="High confidence",
            process_steps=[],
            alternatives_comparison={},
            counterfactuals=[],
            relevant_tags=set(),
            hormonal_state={}
        )
        
        summary = explanation.to_human_readable(ExplanationLevel.SUMMARY)
        assert summary == "Chose safe option despite efficiency trade-off"
        
    def test_standard_level_explanation(self):
        """Test standard level human-readable output"""
        factors = [
            DecisionFactor("Safety", "high risk", 0.8, "negative", "High risk level", set()),
            DecisionFactor("Efficiency", "low usage", 0.6, "positive", "Resource efficient", set())
        ]
        
        explanation = DecisionExplanation(
            decision_id="test-123",
            summary="Chose safe option",
            factors=factors,
            confidence_explanation="80% confidence",
            process_steps=[],
            alternatives_comparison={},
            counterfactuals=[],
            relevant_tags=set(),
            hormonal_state={}
        )
        
        standard = explanation.to_human_readable(ExplanationLevel.STANDARD)
        
        assert "Decision: Chose safe option" in standard
        assert "Key Factors:" in standard
        assert "↓ Safety: High risk level" in standard
        assert "↑ Efficiency: Resource efficient" in standard
        assert "Confidence: 80% confidence" in standard
        
    def test_detailed_level_explanation(self):
        """Test detailed level human-readable output"""
        factors = [
            DecisionFactor("Safety", "high risk", 0.8, "negative", "High risk level", {"#TAG:safety"})
        ]
        
        explanation = DecisionExplanation(
            decision_id="test-123",
            summary="Chose safe option",
            factors=factors,
            confidence_explanation="80% confidence",
            process_steps=["Step 1", "Step 2"],
            alternatives_comparison={"Fast option": "Too risky"},
            counterfactuals=["If risk were lower"],
            relevant_tags={"#TAG:safety", "#TAG:decision"},
            hormonal_state={"cortisol": 0.7}
        )
        
        detailed = explanation.to_human_readable(ExplanationLevel.DETAILED)
        
        assert "=== Detailed Decision Explanation ===" in detailed
        assert "Decision ID: test-123" in detailed
        assert "All Factors Considered:" in detailed
        assert "Decision Process:" in detailed
        assert "1. Step 1" in detailed
        assert "Why Not Other Alternatives:" in detailed
        assert "What Would Change This Decision:" in detailed
        assert "cortisol dominant" in detailed

class TestDecisionExplainer:
    """Test the main DecisionExplainer class"""
    
    def test_explainer_initialization(self):
        """Test explainer initializes correctly"""
        explainer = get_decision_explainer()
        
        assert explainer is not None
        assert hasattr(explainer, 'tag_registry')
        assert hasattr(explainer, 'endocrine_system')
        assert len(explainer.factor_library) > 0
        
    @pytest.mark.asyncio
    async def test_explain_simple_decision(self):
        """Test explaining a simple decision"""
        explainer = get_decision_explainer()
        
        context = {
            "decision_id": "test-001",
            "decision_type": "operational",
            "risk_level": 0.7,
            "ethical_weight": 0.5,
            "stakeholders": ["user", "system"]
        }
        
        outcome = {
            "selected_alternative": "option_a",
            "confidence": 0.8,
            "score": 0.85,
            "ethical_score": 0.9
        }
        
        explanation = await explainer.explain_decision(context, outcome)
        
        assert explanation.decision_id == "test-001"
        assert len(explanation.factors) > 0
        assert explanation.summary != ""
        assert explanation.confidence_explanation != ""
        
    @pytest.mark.asyncio
    async def test_causal_explanation(self):
        """Test generating causal explanations"""
        explainer = get_decision_explainer()
        
        context = {
            "decision_id": "test-002",
            "decision_type": "ethical",
            "ethical_weight": 0.8,
            "risk_level": 0.3
        }
        
        outcome = {
            "selected_alternative": "ethical_option",
            "confidence": 0.9,
            "ethical_score": 0.95
        }
        
        explanation = await explainer.explain_decision(
            context, outcome, ExplanationType.CAUSAL
        )
        
        # Should have ethical factors prominently
        ethical_factors = [f for f in explanation.factors if "ethical" in f.name.lower()]
        assert len(ethical_factors) > 0
        
    @pytest.mark.asyncio
    async def test_comparative_explanation(self):
        """Test generating comparative explanations"""
        explainer = get_decision_explainer()
        
        context = {
            "decision_id": "test-003",
            "alternatives": [
                {"id": "a", "name": "Option A", "score": 0.8},
                {"id": "b", "name": "Option B", "score": 0.6}
            ],
            "alternatives_count": 2
        }
        
        outcome = {
            "selected_alternative": "a",
            "score": 0.8
        }
        
        explanation = await explainer.explain_decision(
            context, outcome, ExplanationType.COMPARATIVE
        )
        
        assert "outperforming other alternatives" in explanation.summary
        
    @pytest.mark.asyncio
    async def test_counterfactual_explanation(self):
        """Test generating counterfactual explanations"""
        explainer = get_decision_explainer()
        
        context = {
            "decision_id": "test-004",
            "risk_level": 0.8,
            "resource_constrained": True
        }
        
        outcome = {
            "selected_alternative": "conservative_option",
            "confidence": 0.6
        }
        
        explanation = await explainer.explain_decision(
            context, outcome, ExplanationType.COUNTERFACTUAL
        )
        
        assert len(explanation.counterfactuals) > 0
        assert "would change" in explanation.summary
        
    @pytest.mark.asyncio
    async def test_factor_analysis(self):
        """Test factor analysis in decisions"""
        explainer = get_decision_explainer()
        
        # High risk context
        context = {
            "decision_id": "test-005",
            "risk_level": 0.9,
            "resource_constrained": True,
            "ethical_weight": 0.7,
            "has_history": True,
            "stakeholders": ["user", "admin", "system"]
        }
        
        outcome = {"confidence": 0.5}
        
        factors = await explainer._analyze_decision_factors(context, outcome)
        
        # Should identify multiple relevant factors
        assert len(factors) >= 3
        
        # Safety should be highly relevant
        safety_factors = [f for f in factors if "Safety" in f.name]
        assert len(safety_factors) > 0
        assert safety_factors[0].weight > 0.5
        
    @pytest.mark.asyncio
    async def test_hormonal_influence(self):
        """Test hormonal state influence on explanations"""
        explainer = get_decision_explainer()
        
        # Set high stress in endocrine system
        explainer.endocrine_system.trigger_stress_response(0.8)
        
        context = {"decision_id": "test-006"}
        outcome = {"confidence": 0.6}
        
        explanation = await explainer.explain_decision(context, outcome)
        
        # Should mention stress in confidence explanation
        assert "stress" in explanation.confidence_explanation.lower()
        
    def test_decision_report_generation(self):
        """Test generating reports from multiple explanations"""
        explainer = get_decision_explainer()
        
        # Create sample explanations
        explanations = []
        for i in range(5):
            factors = [
                DecisionFactor("Safety", "value", 0.7, "negative", "explanation", set()),
                DecisionFactor("Efficiency", "value", 0.5, "positive", "explanation", set())
            ]
            
            exp = DecisionExplanation(
                decision_id=f"test-{i}",
                summary=f"Decision {i}",
                factors=factors,
                confidence_explanation=f"{70 + i*5}% confidence",
                process_steps=[],
                alternatives_comparison={},
                counterfactuals=[],
                relevant_tags=set(),
                hormonal_state={"cortisol": 0.3 + i*0.1, "dopamine": 0.5}
            )
            explanations.append(exp)
        
        report = explainer.generate_decision_report(explanations)
        
        assert report["total_decisions_explained"] == 5
        assert len(report["dominant_factors"]) > 0
        assert "Safety" in [f["factor"] for f in report["dominant_factors"]]
        assert float(report["average_confidence"].rstrip('%')) > 70
        
    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """Test the convenience functions"""
        context = {
            "decision_id": "test-007",
            "decision_type": "operational"
        }
        
        outcome = {
            "selected_alternative": "option_x",
            "confidence": 0.75
        }
        
        # Test explain_decision
        explanation_text = await explain_decision(context, outcome)
        assert isinstance(explanation_text, str)
        assert len(explanation_text) > 10
        
        # Test get_decision_comparison
        comparison = await get_decision_comparison(context, outcome)
        assert isinstance(comparison, str)
        
        # Test get_decision_counterfactuals
        counterfactuals = await get_decision_counterfactuals(context, outcome)
        assert isinstance(counterfactuals, list)
        
    def test_error_handling(self):
        """Test error handling in explanations"""
        explainer = get_decision_explainer()
        
        # Test with minimal context - should still generate something
        async def test_minimal():
            explanation = await explainer.explain_decision({}, {})
            # Should generate some explanation even with minimal input
            assert explanation.summary != ""
            assert isinstance(explanation.summary, str)
            
        asyncio.run(test_minimal())
        
    @pytest.mark.asyncio
    async def test_dmb_style_explanation(self):
        """Test explaining decisions in DMB style format"""
        # Simulate DMB-style context without importing
        dmb_style_context = {
            "decision_id": "dmb-001",
            "decision_type": "strategic",
            "description": "Strategic planning decision",
            "stakeholders": ["management", "operations"],
            "urgency": 0.4,
            "complexity": 0.7,
            "ethical_weight": 0.5,
            "risk_level": 0.4,
            "resource_constrained": False,
            "alternatives_count": 3
        }
        
        dmb_style_outcome = {
            "selected_alternative": "plan_a",
            "confidence": 0.7,  # HIGH level = 0.7
            "score": 0.85,
            "ethical_score": 0.8
        }
        
        # Test explanation
        explainer = get_decision_explainer()
        explanation = await explainer.explain_decision(dmb_style_context, dmb_style_outcome)
        
        assert explanation.decision_id == "dmb-001"
        assert explanation.summary != ""
        assert len(explanation.factors) > 0
        assert "strategic" in str(explanation.relevant_tags).lower() or len(explanation.factors) > 0