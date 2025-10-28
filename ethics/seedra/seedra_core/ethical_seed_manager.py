"""
Ethical Seed Manager - Core SEEDRA Component
==========================================

The EthicalSeedManager is the core component of SEEDRA (Structured Ethical Evaluation,
Decision-making, and Reasoning Architecture). It manages ethical seeds that form the
foundation for all ethical reasoning in the LUKHAS system.

Ethical seeds are fundamental ethical principles, values, and constraints that guide
decision-making processes. They include constitutional principles, safety constraints,
fairness requirements, and contextual ethical considerations.

Features:
- Ethical seed generation and management
- Constitutional principle integration
- Ethical decision validation 
- Bias detection and mitigation
- Impact assessment and monitoring
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import structlog

logger = structlog.get_logger(__name__)


class EthicalPrinciple(Enum):
    """Core ethical principles for seed generation."""
    AUTONOMY = "autonomy"                    # Respect for human autonomy
    BENEFICENCE = "beneficence"              # Do good/benefit
    NON_MALEFICENCE = "non_maleficence"      # Do no harm
    JUSTICE = "justice"                      # Fairness and equality
    TRANSPARENCY = "transparency"            # Openness and explainability
    PRIVACY = "privacy"                      # Privacy protection
    ACCOUNTABILITY = "accountability"        # Responsibility and oversight
    HUMAN_DIGNITY = "human_dignity"          # Respect for human dignity
    CONSENT = "consent"                      # Informed consent
    PROPORTIONALITY = "proportionality"      # Proportionate response


class EthicalSeverity(Enum):
    """Severity levels for ethical considerations."""
    LOW = "low"                             # Minor ethical implications
    MODERATE = "moderate"                   # Moderate ethical considerations
    HIGH = "high"                          # Significant ethical implications
    CRITICAL = "critical"                  # Critical ethical concerns
    BLOCKING = "blocking"                  # Ethically unacceptable


@dataclass
class EthicalSeed:
    """An ethical seed containing principles and constraints."""
    seed_id: str
    principle: EthicalPrinciple
    description: str
    constraints: List[str]
    weight: float = 1.0                     # Importance weight (0.0-1.0)
    severity: EthicalSeverity = EthicalSeverity.MODERATE
    context_tags: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicalDecisionContext:
    """Context for ethical decision making."""
    context_id: str
    scenario_description: str
    stakeholders: List[str]
    potential_impacts: List[str]
    domain: str                             # e.g., "identity", "memory", "consciousness"
    user_consent_level: str = "none"        # none, basic, informed, explicit
    data_sensitivity: str = "low"           # low, medium, high, critical
    regulatory_frameworks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicalDecisionResult:
    """Result of ethical decision evaluation."""
    decision_id: str
    is_ethically_acceptable: bool
    confidence_score: float                 # 0.0-1.0
    applied_principles: List[EthicalPrinciple]
    violated_principles: List[EthicalPrinciple]
    recommendations: List[str]
    constraints_to_apply: List[str]
    severity_assessment: EthicalSeverity
    reasoning_chain: List[str]
    mitigation_strategies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EthicalSeedManager:
    """Manages ethical seeds and provides ethical reasoning capabilities."""
    
    def __init__(self):
        self.seeds: Dict[str, EthicalSeed] = {}
        self.decision_history: List[EthicalDecisionResult] = []
        self.constitutional_principles: Dict[str, str] = {}
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the ethical seed manager with default seeds."""
        try:
            self._load_constitutional_principles()
            self._generate_core_ethical_seeds()
            self.is_initialized = True
            
            logger.info("ethical_seed_manager_initialized", 
                       seed_count=len(self.seeds),
                       principle_count=len(self.constitutional_principles))
            return True
            
        except Exception as e:
            logger.error("ethical_seed_manager_initialization_failed", error=str(e))
            return False
    
    def _load_constitutional_principles(self):
        """Load constitutional AI principles."""
        self.constitutional_principles = {
            "human_autonomy": "Respect and preserve human autonomy and decision-making capability",
            "human_dignity": "Uphold human dignity and treat all individuals with respect",
            "transparency": "Provide clear, understandable explanations for decisions and actions",
            "accountability": "Maintain clear accountability and responsibility chains",
            "fairness": "Ensure fair and equitable treatment across all interactions",
            "privacy": "Protect personal information and respect privacy rights",
            "safety": "Prioritize safety and harm prevention in all operations",
            "consent": "Obtain appropriate consent for data use and decision-making",
            "proportionality": "Ensure responses are proportionate to the situation",
            "beneficence": "Act to benefit users and society while minimizing harm"
        }
    
    def _generate_core_ethical_seeds(self):
        """Generate core ethical seeds based on constitutional principles."""
        # Autonomy seed
        autonomy_seed = EthicalSeed(
            seed_id="core_autonomy",
            principle=EthicalPrinciple.AUTONOMY,
            description="Preserve human autonomy and decision-making capability",
            constraints=[
                "Do not override explicit human decisions",
                "Provide options rather than making decisions for users",
                "Respect user preferences and boundaries",
                "Enable informed decision-making"
            ],
            weight=0.9,
            severity=EthicalSeverity.HIGH,
            context_tags={"core", "constitutional", "autonomy"}
        )
        self.seeds[autonomy_seed.seed_id] = autonomy_seed
        
        # Privacy seed
        privacy_seed = EthicalSeed(
            seed_id="core_privacy",
            principle=EthicalPrinciple.PRIVACY,
            description="Protect personal information and privacy rights",
            constraints=[
                "Minimize data collection to necessary purposes",
                "Obtain explicit consent for sensitive data use",
                "Implement data anonymization where possible",
                "Provide users control over their data"
            ],
            weight=0.95,
            severity=EthicalSeverity.CRITICAL,
            context_tags={"core", "constitutional", "privacy", "gdpr"}
        )
        self.seeds[privacy_seed.seed_id] = privacy_seed
        
        # Non-maleficence seed  
        safety_seed = EthicalSeed(
            seed_id="core_safety",
            principle=EthicalPrinciple.NON_MALEFICENCE,
            description="Do no harm and prioritize safety",
            constraints=[
                "Prevent actions that could cause harm",
                "Implement safety checks for all operations",
                "Fail safely when errors occur",
                "Monitor for unintended consequences"
            ],
            weight=1.0,
            severity=EthicalSeverity.BLOCKING,
            context_tags={"core", "constitutional", "safety", "harm_prevention"}
        )
        self.seeds[safety_seed.seed_id] = safety_seed
        
        # Transparency seed
        transparency_seed = EthicalSeed(
            seed_id="core_transparency",
            principle=EthicalPrinciple.TRANSPARENCY,
            description="Provide clear explanations and maintain transparency",
            constraints=[
                "Explain decision-making processes",
                "Provide audit trails for important decisions",
                "Make AI capabilities and limitations clear",
                "Enable user understanding of system behavior"
            ],
            weight=0.8,
            severity=EthicalSeverity.HIGH,
            context_tags={"core", "constitutional", "transparency", "explainability"}
        )
        self.seeds[transparency_seed.seed_id] = transparency_seed
        
        # Justice/Fairness seed
        justice_seed = EthicalSeed(
            seed_id="core_justice",
            principle=EthicalPrinciple.JUSTICE,
            description="Ensure fairness and equal treatment",
            constraints=[
                "Apply consistent standards across all users",
                "Avoid discriminatory bias in decisions",
                "Provide equal access to capabilities",
                "Consider impact on vulnerable populations"
            ],
            weight=0.85,
            severity=EthicalSeverity.HIGH,
            context_tags={"core", "constitutional", "fairness", "bias_prevention"}
        )
        self.seeds[justice_seed.seed_id] = justice_seed
    
    def add_seed(self, seed: EthicalSeed) -> bool:
        """Add an ethical seed to the manager."""
        try:
            self.seeds[seed.seed_id] = seed
            logger.info("ethical_seed_added", 
                       seed_id=seed.seed_id,
                       principle=seed.principle.value)
            return True
        except Exception as e:
            logger.error("ethical_seed_addition_failed", 
                        seed_id=seed.seed_id, error=str(e))
            return False
    
    def get_seeds_for_context(self, context: EthicalDecisionContext) -> List[EthicalSeed]:
        """Get relevant ethical seeds for a decision context."""
        relevant_seeds = []
        
        for seed in self.seeds.values():
            # Check if seed is relevant to the context
            if self._is_seed_relevant(seed, context):
                relevant_seeds.append(seed)
        
        # Sort by weight and severity
        relevant_seeds.sort(key=lambda s: (s.severity.value, s.weight), reverse=True)
        return relevant_seeds
    
    def _is_seed_relevant(self, seed: EthicalSeed, context: EthicalDecisionContext) -> bool:
        """Check if a seed is relevant to the decision context."""
        # Core seeds are always relevant
        if "core" in seed.context_tags:
            return True
        
        # Check domain relevance
        if context.domain in seed.context_tags:
            return True
        
        # Check data sensitivity alignment
        if context.data_sensitivity == "critical" and seed.severity == EthicalSeverity.CRITICAL:
            return True
        
        # Check regulatory framework alignment
        for framework in context.regulatory_frameworks:
            if framework.lower() in seed.context_tags:
                return True
        
        return False
    
    def validate_decision(self, context: EthicalDecisionContext, 
                         proposed_action: Dict[str, Any]) -> EthicalDecisionResult:
        """Validate a proposed action against ethical seeds."""
        decision_id = str(uuid4())
        
        # Get relevant seeds
        relevant_seeds = self.get_seeds_for_context(context)
        
        # Evaluate against each seed
        applied_principles = []
        violated_principles = []
        recommendations = []
        constraints_to_apply = []
        reasoning_chain = []
        mitigation_strategies = []
        
        overall_acceptable = True
        max_severity = EthicalSeverity.LOW
        confidence_scores = []
        
        for seed in relevant_seeds:
            evaluation = self._evaluate_action_against_seed(seed, proposed_action, context)
            
            reasoning_chain.append(
                f"Evaluated against {seed.principle.value}: {evaluation['reasoning']}"
            )
            
            if evaluation['is_acceptable']:
                applied_principles.append(seed.principle)
                constraints_to_apply.extend(evaluation['applicable_constraints'])
            else:
                violated_principles.append(seed.principle)
                overall_acceptable = False
                recommendations.extend(evaluation['recommendations'])
                mitigation_strategies.extend(evaluation['mitigation_strategies'])
            
            confidence_scores.append(evaluation['confidence'])
            
            # Track highest severity
            if self._severity_level(seed.severity) > self._severity_level(max_severity):
                max_severity = seed.severity
        
        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Create result
        result = EthicalDecisionResult(
            decision_id=decision_id,
            is_ethically_acceptable=overall_acceptable,
            confidence_score=avg_confidence,
            applied_principles=applied_principles,
            violated_principles=violated_principles,
            recommendations=recommendations,
            constraints_to_apply=constraints_to_apply,
            severity_assessment=max_severity,
            reasoning_chain=reasoning_chain,
            mitigation_strategies=mitigation_strategies,
            metadata={
                "context_id": context.context_id,
                "evaluated_seeds": len(relevant_seeds),
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Store in history
        self.decision_history.append(result)
        
        logger.info("ethical_decision_validated",
                   decision_id=decision_id,
                   acceptable=overall_acceptable,
                   confidence=avg_confidence,
                   violated_principles=len(violated_principles))
        
        return result
    
    def _evaluate_action_against_seed(self, seed: EthicalSeed, action: Dict[str, Any], 
                                     context: EthicalDecisionContext) -> Dict[str, Any]:
        """Evaluate a specific action against an ethical seed."""
        # This is a simplified evaluation - in practice would use more sophisticated reasoning
        
        evaluation = {
            'is_acceptable': True,
            'confidence': 0.7,
            'reasoning': f"Action evaluated against {seed.principle.value}",
            'applicable_constraints': [],
            'recommendations': [],
            'mitigation_strategies': []
        }
        
        action_type = action.get('type', 'unknown')
        action_data = action.get('data', {})
        
        # Evaluate based on principle type
        if seed.principle == EthicalPrinciple.PRIVACY:
            if action_type in ['data_collection', 'data_processing', 'data_sharing']:
                # Check for consent and necessity
                if context.user_consent_level == "none" and context.data_sensitivity != "low":
                    evaluation['is_acceptable'] = False
                    evaluation['recommendations'].append("Obtain explicit user consent")
                    evaluation['mitigation_strategies'].append("Implement consent collection workflow")
                
                evaluation['applicable_constraints'].extend([
                    c for c in seed.constraints if 'data' in c.lower()
                ])
        
        elif seed.principle == EthicalPrinciple.NON_MALEFICENCE:
            # Always apply safety constraints
            evaluation['applicable_constraints'].extend(seed.constraints)
            
            # Check for potentially harmful actions
            if action_type in ['data_deletion', 'system_modification', 'user_restriction']:
                evaluation['confidence'] = 0.6
                evaluation['recommendations'].append("Implement additional safety checks")
        
        elif seed.principle == EthicalPrinciple.AUTONOMY:
            if action_type in ['automatic_decision', 'user_override']:
                if not action_data.get('user_approval', False):
                    evaluation['is_acceptable'] = False
                    evaluation['recommendations'].append("Require user approval for this action")
        
        elif seed.principle == EthicalPrinciple.TRANSPARENCY:
            if action_type in ['algorithmic_decision', 'automated_processing']:
                evaluation['applicable_constraints'].append("Provide explanation for decision")
                evaluation['recommendations'].append("Log decision rationale for audit")
        
        return evaluation
    
    def _severity_level(self, severity: EthicalSeverity) -> int:
        """Convert severity enum to numeric level for comparison."""
        severity_levels = {
            EthicalSeverity.LOW: 1,
            EthicalSeverity.MODERATE: 2,
            EthicalSeverity.HIGH: 3,
            EthicalSeverity.CRITICAL: 4,
            EthicalSeverity.BLOCKING: 5
        }
        return severity_levels.get(severity, 1)
    
    def generate_guidance(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ethical guidance for a scenario."""
        # Create context from scenario
        context = EthicalDecisionContext(
            context_id=str(uuid4()),
            scenario_description=scenario.get('description', ''),
            stakeholders=scenario.get('stakeholders', []),
            potential_impacts=scenario.get('potential_impacts', []),
            domain=scenario.get('domain', 'general'),
            user_consent_level=scenario.get('consent_level', 'none'),
            data_sensitivity=scenario.get('data_sensitivity', 'low')
        )
        
        # Get relevant seeds
        relevant_seeds = self.get_seeds_for_context(context)
        
        # Generate guidance
        guidance = {
            'scenario_id': context.context_id,
            'ethical_considerations': [],
            'recommended_constraints': [],
            'risk_factors': [],
            'mitigation_strategies': [],
            'approval_requirements': []
        }
        
        for seed in relevant_seeds:
            guidance['ethical_considerations'].append({
                'principle': seed.principle.value,
                'description': seed.description,
                'severity': seed.severity.value
            })
            
            guidance['recommended_constraints'].extend(seed.constraints)
            
            if seed.severity in [EthicalSeverity.HIGH, EthicalSeverity.CRITICAL, EthicalSeverity.BLOCKING]:
                guidance['risk_factors'].append(f"High-risk principle: {seed.principle.value}")
                
                if seed.severity == EthicalSeverity.BLOCKING:
                    guidance['approval_requirements'].append("Ethics review required")
        
        logger.info("ethical_guidance_generated",
                   scenario_id=context.context_id,
                   considerations=len(guidance['ethical_considerations']))
        
        return guidance
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[EthicalDecisionResult]:
        """Get recent decision history."""
        history = sorted(self.decision_history, 
                        key=lambda d: d.metadata.get('evaluation_timestamp', ''), 
                        reverse=True)
        
        if limit:
            return history[:limit]
        return history
    
    def get_ethics_metrics(self) -> Dict[str, Any]:
        """Get ethics system metrics."""
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'acceptance_rate': 0.0,
                'avg_confidence': 0.0,
                'top_violated_principles': []
            }
        
        total_decisions = len(self.decision_history)
        accepted_decisions = sum(1 for d in self.decision_history if d.is_ethically_acceptable)
        acceptance_rate = accepted_decisions / total_decisions
        
        avg_confidence = sum(d.confidence_score for d in self.decision_history) / total_decisions
        
        # Count violated principles
        violated_counts = {}
        for decision in self.decision_history:
            for principle in decision.violated_principles:
                violated_counts[principle.value] = violated_counts.get(principle.value, 0) + 1
        
        top_violated = sorted(violated_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_decisions': total_decisions,
            'acceptance_rate': acceptance_rate,
            'avg_confidence': avg_confidence,
            'top_violated_principles': top_violated,
            'active_seeds': len(self.seeds)
        }