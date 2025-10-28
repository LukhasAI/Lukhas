"""
Reasoning Validator - SEEDRA Component
=====================================

The ReasoningValidator provides validation and verification of ethical reasoning
chains within the SEEDRA system. It ensures that ethical decisions follow logical
and consistent reasoning patterns, and validates the soundness of ethical arguments.

Features:
- Reasoning chain validation
- Logical consistency checking
- Ethical argument soundness verification
- Bias detection in reasoning
- Reasoning quality assessment
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class ReasoningType(Enum):
    """Types of ethical reasoning."""
    DEDUCTIVE = "deductive"                 # From general principles to specific cases
    INDUCTIVE = "inductive"                 # From specific cases to general principles
    ABDUCTIVE = "abductive"                 # Best explanation reasoning
    CONSEQUENTIALIST = "consequentialist"   # Based on outcomes/consequences
    DEONTOLOGICAL = "deontological"         # Based on duties/rules
    VIRTUE_ETHICS = "virtue_ethics"         # Based on character/virtues


class ReasoningQuality(Enum):
    """Quality levels for reasoning validation."""
    EXCELLENT = "excellent"                 # High-quality, sound reasoning
    GOOD = "good"                          # Generally sound reasoning
    ADEQUATE = "adequate"                  # Acceptable but with minor issues
    POOR = "poor"                          # Significant reasoning flaws
    INVALID = "invalid"                    # Logically invalid reasoning


@dataclass
class ReasoningStep:
    """A single step in an ethical reasoning chain."""
    step_id: str
    premise: str
    inference: str
    conclusion: str
    reasoning_type: ReasoningType
    confidence: float = 0.7
    supporting_evidence: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.supporting_evidence is None:
            self.supporting_evidence = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ReasoningChain:
    """A complete chain of ethical reasoning."""
    chain_id: str
    steps: List[ReasoningStep]
    initial_premises: List[str]
    final_conclusion: str
    overall_confidence: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        
        # Calculate overall confidence
        if self.steps:
            self.overall_confidence = sum(step.confidence for step in self.steps) / len(self.steps)


@dataclass
class ReasoningValidationResult:
    """Result of reasoning validation."""
    validation_id: str
    is_valid: bool
    quality_assessment: ReasoningQuality
    confidence_score: float
    logical_consistency: bool
    bias_indicators: List[str]
    reasoning_gaps: List[str]
    recommendations: List[str]
    detailed_analysis: Dict[str, Any]
    validation_timestamp: datetime = None
    
    def __post_init__(self):
        if self.validation_timestamp is None:
            self.validation_timestamp = datetime.now(timezone.utc)


class ReasoningValidator:
    """Validates ethical reasoning chains for soundness and consistency."""
    
    def __init__(self):
        self.validation_history: List[ReasoningValidationResult] = []
        self.bias_patterns = self._load_bias_patterns()
        self.logical_rules = self._load_logical_rules()
    
    def _load_bias_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate potential bias in reasoning."""
        return {
            "confirmation_bias": [
                "only considering supporting evidence",
                "ignoring contradictory information",
                "cherry-picking data points"
            ],
            "anchoring_bias": [
                "over-relying on first information",
                "insufficient adjustment from initial position",
                "disproportionate weight to initial premise"
            ],
            "availability_heuristic": [
                "overestimating probability of recent events",
                "relying on easily recalled examples",
                "ignoring base rates"
            ],
            "in_group_bias": [
                "favoring certain groups",
                "differential treatment based on group membership",
                "assuming group homogeneity"
            ],
            "authority_bias": [
                "accepting claims solely based on authority",
                "insufficient critical evaluation of expert claims",
                "appeal to inappropriate authority"
            ]
        }
    
    def _load_logical_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load logical rules for reasoning validation."""
        return {
            "modus_ponens": {
                "pattern": "If P then Q; P; therefore Q",
                "valid": True,
                "description": "Valid deductive form"
            },
            "modus_tollens": {
                "pattern": "If P then Q; not Q; therefore not P", 
                "valid": True,
                "description": "Valid deductive form"
            },
            "affirming_consequent": {
                "pattern": "If P then Q; Q; therefore P",
                "valid": False,
                "description": "Invalid logical form - fallacy"
            },
            "denying_antecedent": {
                "pattern": "If P then Q; not P; therefore not Q",
                "valid": False,
                "description": "Invalid logical form - fallacy"
            },
            "hypothetical_syllogism": {
                "pattern": "If P then Q; If Q then R; therefore if P then R",
                "valid": True,
                "description": "Valid chain of conditional reasoning"
            }
        }
    
    def validate_reasoning_chain(self, reasoning_chain: ReasoningChain) -> ReasoningValidationResult:
        """Validate a complete reasoning chain."""
        validation_id = f"validation_{reasoning_chain.chain_id}_{int(datetime.now().timestamp())}"
        
        # Validate each step
        step_validations = []
        for step in reasoning_chain.steps:
            step_validation = self._validate_reasoning_step(step)
            step_validations.append(step_validation)
        
        # Check overall consistency
        logical_consistency = self._check_logical_consistency(reasoning_chain)
        
        # Detect bias patterns
        bias_indicators = self._detect_bias_patterns(reasoning_chain)
        
        # Identify reasoning gaps
        reasoning_gaps = self._identify_reasoning_gaps(reasoning_chain)
        
        # Calculate overall quality
        quality_assessment = self._assess_overall_quality(
            step_validations, logical_consistency, bias_indicators, reasoning_gaps
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            step_validations, logical_consistency, bias_indicators, reasoning_gaps
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            step_validations, logical_consistency, bias_indicators
        )
        
        # Is reasoning valid?
        is_valid = (
            logical_consistency and
            len(bias_indicators) == 0 and
            len(reasoning_gaps) == 0 and
            all(step['is_valid'] for step in step_validations)
        )
        
        result = ReasoningValidationResult(
            validation_id=validation_id,
            is_valid=is_valid,
            quality_assessment=quality_assessment,
            confidence_score=confidence_score,
            logical_consistency=logical_consistency,
            bias_indicators=bias_indicators,
            reasoning_gaps=reasoning_gaps,
            recommendations=recommendations,
            detailed_analysis={
                'step_validations': step_validations,
                'reasoning_chain_length': len(reasoning_chain.steps),
                'overall_confidence': reasoning_chain.overall_confidence,
                'reasoning_types_used': list(set(step.reasoning_type.value for step in reasoning_chain.steps))
            }
        )
        
        self.validation_history.append(result)
        
        logger.info("reasoning_chain_validated",
                   validation_id=validation_id,
                   is_valid=is_valid,
                   quality=quality_assessment.value,
                   confidence=confidence_score)
        
        return result
    
    def _validate_reasoning_step(self, step: ReasoningStep) -> Dict[str, Any]:
        """Validate a single reasoning step."""
        validation = {
            'step_id': step.step_id,
            'is_valid': True,
            'issues': [],
            'confidence': step.confidence,
            'reasoning_type': step.reasoning_type.value
        }
        
        # Check if premise supports conclusion
        if not self._premise_supports_conclusion(step.premise, step.conclusion):
            validation['is_valid'] = False
            validation['issues'].append("Premise does not adequately support conclusion")
        
        # Check for logical fallacies
        fallacies = self._detect_logical_fallacies(step)
        if fallacies:
            validation['is_valid'] = False
            validation['issues'].extend(fallacies)
        
        # Check reasoning type appropriateness
        if not self._is_reasoning_type_appropriate(step):
            validation['issues'].append(f"Reasoning type {step.reasoning_type.value} may not be appropriate")
        
        # Check evidence quality
        evidence_issues = self._assess_evidence_quality(step.supporting_evidence)
        validation['issues'].extend(evidence_issues)
        
        return validation
    
    def _premise_supports_conclusion(self, premise: str, conclusion: str) -> bool:
        """Check if premise logically supports conclusion."""
        # Simplified check - in practice would use more sophisticated analysis
        
        # Basic keyword overlap check
        premise_words = set(premise.lower().split())
        conclusion_words = set(conclusion.lower().split())
        overlap = premise_words.intersection(conclusion_words)
        
        # Should have some semantic connection
        if len(overlap) == 0:
            return False
        
        # Check for contradictory terms
        contradictory_pairs = [
            ("should", "should not"), ("must", "must not"), 
            ("allowed", "prohibited"), ("ethical", "unethical")
        ]
        
        for pos, neg in contradictory_pairs:
            if pos in premise.lower() and neg in conclusion.lower():
                return False
            if neg in premise.lower() and pos in conclusion.lower():
                return False
        
        return True
    
    def _detect_logical_fallacies(self, step: ReasoningStep) -> List[str]:
        """Detect logical fallacies in reasoning step."""
        fallacies = []
        
        text = f"{step.premise} {step.inference} {step.conclusion}".lower()
        
        # Check for common fallacies
        if any(phrase in text for phrase in ["everyone knows", "it's obvious", "clearly"]):
            fallacies.append("Appeal to common knowledge without evidence")
        
        if any(phrase in text for phrase in ["always", "never", "all", "none"]) and "some" not in text:
            fallacies.append("Overgeneralization - absolute statements without qualification")
        
        if "because" in text and any(authority in text for authority in ["expert", "authority", "leader"]):
            fallacies.append("Potential appeal to authority without independent reasoning")
        
        if any(emotional in text for emotional in ["terrible", "awful", "wonderful", "amazing"]):
            fallacies.append("Potential appeal to emotion over rational argument")
        
        return fallacies
    
    def _is_reasoning_type_appropriate(self, step: ReasoningStep) -> bool:
        """Check if the reasoning type is appropriate for the step."""
        # Simplified appropriateness check
        
        if step.reasoning_type == ReasoningType.DEDUCTIVE:
            # Should have general principle leading to specific conclusion
            return "if" in step.premise.lower() or "all" in step.premise.lower()
        
        elif step.reasoning_type == ReasoningType.INDUCTIVE:
            # Should reason from specific cases to general conclusion
            return "some" in step.premise.lower() or "many" in step.premise.lower()
        
        elif step.reasoning_type == ReasoningType.CONSEQUENTIALIST:
            # Should focus on outcomes/consequences
            return any(word in step.inference.lower() for word in ["outcome", "result", "consequence", "effect"])
        
        elif step.reasoning_type == ReasoningType.DEONTOLOGICAL:
            # Should focus on duties/rules
            return any(word in step.inference.lower() for word in ["duty", "obligation", "rule", "principle"])
        
        return True
    
    def _assess_evidence_quality(self, evidence: List[str]) -> List[str]:
        """Assess the quality of supporting evidence."""
        issues = []
        
        if not evidence:
            issues.append("No supporting evidence provided")
            return issues
        
        for piece in evidence:
            # Check for vague evidence
            if any(vague in piece.lower() for vague in ["some studies", "research shows", "it is known"]):
                issues.append("Vague or unspecific evidence cited")
            
            # Check for unsubstantiated claims
            if len(piece.split()) < 5:
                issues.append("Evidence claims are too brief to be substantive")
        
        return issues
    
    def _check_logical_consistency(self, reasoning_chain: ReasoningChain) -> bool:
        """Check logical consistency across the reasoning chain."""
        if len(reasoning_chain.steps) < 2:
            return True
        
        # Check that conclusions of previous steps support premises of next steps
        for i in range(len(reasoning_chain.steps) - 1):
            current_conclusion = reasoning_chain.steps[i].conclusion
            next_premise = reasoning_chain.steps[i + 1].premise
            
            # Simplified consistency check
            if not self._statements_consistent(current_conclusion, next_premise):
                return False
        
        return True
    
    def _statements_consistent(self, statement1: str, statement2: str) -> bool:
        """Check if two statements are logically consistent."""
        # Simplified consistency check
        s1_words = set(statement1.lower().split())
        s2_words = set(statement2.lower().split())
        
        # Check for direct contradictions
        contradictory_pairs = [
            ("ethical", "unethical"), ("acceptable", "unacceptable"),
            ("should", "should not"), ("allowed", "prohibited")
        ]
        
        for pos, neg in contradictory_pairs:
            if pos in s1_words and neg in s2_words:
                return False
            if neg in s1_words and pos in s2_words:
                return False
        
        return True
    
    def _detect_bias_patterns(self, reasoning_chain: ReasoningChain) -> List[str]:
        """Detect potential bias patterns in reasoning."""
        bias_indicators = []
        
        full_text = " ".join([
            f"{step.premise} {step.inference} {step.conclusion}" 
            for step in reasoning_chain.steps
        ]).lower()
        
        # Check for each bias pattern
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if any(keyword in full_text for keyword in pattern.split()):
                    bias_indicators.append(f"Potential {bias_type}: {pattern}")
        
        # Check for one-sided reasoning
        if "however" not in full_text and "although" not in full_text and "but" not in full_text:
            bias_indicators.append("One-sided reasoning - no consideration of counterarguments")
        
        return bias_indicators
    
    def _identify_reasoning_gaps(self, reasoning_chain: ReasoningChain) -> List[str]:
        """Identify gaps in the reasoning chain."""
        gaps = []
        
        # Check for missing steps
        if len(reasoning_chain.steps) < 2 and reasoning_chain.final_conclusion:
            gaps.append("Insufficient reasoning steps to support conclusion")
        
        # Check if initial premises are justified
        first_step = reasoning_chain.steps[0] if reasoning_chain.steps else None
        if first_step and not first_step.supporting_evidence:
            gaps.append("Initial premises lack supporting evidence")
        
        # Check for leaps in logic
        for step in reasoning_chain.steps:
            premise_complexity = len(step.premise.split())
            conclusion_complexity = len(step.conclusion.split())
            
            if conclusion_complexity > premise_complexity * 2:
                gaps.append(f"Large logical leap in step {step.step_id}")
        
        return gaps
    
    def _assess_overall_quality(self, step_validations: List[Dict], 
                               logical_consistency: bool,
                               bias_indicators: List[str], 
                               reasoning_gaps: List[str]) -> ReasoningQuality:
        """Assess overall reasoning quality."""
        issues_count = 0
        
        # Count step-level issues
        for validation in step_validations:
            issues_count += len(validation.get('issues', []))
        
        # Count high-level issues
        if not logical_consistency:
            issues_count += 2
        
        issues_count += len(bias_indicators)
        issues_count += len(reasoning_gaps)
        
        # Determine quality level
        if issues_count == 0:
            return ReasoningQuality.EXCELLENT
        elif issues_count <= 2:
            return ReasoningQuality.GOOD
        elif issues_count <= 5:
            return ReasoningQuality.ADEQUATE
        elif issues_count <= 10:
            return ReasoningQuality.POOR
        else:
            return ReasoningQuality.INVALID
    
    def _generate_recommendations(self, step_validations: List[Dict],
                                 logical_consistency: bool,
                                 bias_indicators: List[str],
                                 reasoning_gaps: List[str]) -> List[str]:
        """Generate recommendations for improving reasoning."""
        recommendations = []
        
        # Step-level recommendations
        invalid_steps = sum(1 for v in step_validations if not v['is_valid'])
        if invalid_steps > 0:
            recommendations.append(f"Review and strengthen {invalid_steps} invalid reasoning steps")
        
        # Consistency recommendations
        if not logical_consistency:
            recommendations.append("Ensure logical consistency between reasoning steps")
        
        # Bias recommendations
        if bias_indicators:
            recommendations.append("Address potential bias patterns in reasoning")
            recommendations.append("Consider alternative perspectives and counterarguments")
        
        # Gap recommendations
        if reasoning_gaps:
            recommendations.append("Fill identified gaps in reasoning chain")
            recommendations.append("Provide stronger evidence for key premises")
        
        # General recommendations
        recommendations.append("Consider using multiple reasoning approaches for robustness")
        recommendations.append("Seek peer review of ethical reasoning")
        
        return recommendations
    
    def _calculate_confidence_score(self, step_validations: List[Dict],
                                   logical_consistency: bool,
                                   bias_indicators: List[str]) -> float:
        """Calculate overall confidence score for reasoning."""
        if not step_validations:
            return 0.0
        
        # Base confidence from step validations
        valid_steps = sum(1 for v in step_validations if v['is_valid'])
        step_confidence = valid_steps / len(step_validations)
        
        # Penalties for issues
        consistency_penalty = 0.0 if logical_consistency else 0.2
        bias_penalty = min(len(bias_indicators) * 0.1, 0.3)
        
        confidence = step_confidence - consistency_penalty - bias_penalty
        return max(0.0, min(1.0, confidence))
    
    def get_validation_history(self, limit: Optional[int] = None) -> List[ReasoningValidationResult]:
        """Get validation history."""
        history = sorted(self.validation_history,
                        key=lambda r: r.validation_timestamp,
                        reverse=True)
        
        if limit:
            return history[:limit]
        return history
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'validity_rate': 0.0,
                'avg_quality_score': 0.0,
                'common_issues': []
            }
        
        total = len(self.validation_history)
        valid = sum(1 for r in self.validation_history if r.is_valid)
        validity_rate = valid / total
        
        # Quality score mapping
        quality_scores = {
            ReasoningQuality.EXCELLENT: 1.0,
            ReasoningQuality.GOOD: 0.8,
            ReasoningQuality.ADEQUATE: 0.6,
            ReasoningQuality.POOR: 0.4,
            ReasoningQuality.INVALID: 0.0
        }
        
        avg_quality = sum(quality_scores[r.quality_assessment] for r in self.validation_history) / total
        
        # Common issues
        all_issues = []
        for result in self.validation_history:
            all_issues.extend(result.bias_indicators)
            all_issues.extend(result.reasoning_gaps)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_validations': total,
            'validity_rate': validity_rate,
            'avg_quality_score': avg_quality,
            'common_issues': common_issues
        }