"""
Constitutional Evaluator - SEEDRA Component
==========================================

The ConstitutionalEvaluator implements Constitutional AI principles for the SEEDRA
system. It provides evaluation of decisions and actions against constitutional
principles, ensuring alignment with fundamental values and legal frameworks.

Features:
- Constitutional principle evaluation
- Legal compliance checking
- Rights protection validation
- Democratic value alignment
- Regulatory framework compliance
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles for evaluation."""
    HUMAN_RIGHTS = "human_rights"               # Fundamental human rights
    EQUALITY = "equality"                       # Equal treatment and non-discrimination
    LIBERTY = "liberty"                         # Individual freedom and autonomy
    DUE_PROCESS = "due_process"                 # Fair procedures and processes
    PROPORTIONALITY = "proportionality"         # Proportionate response to issues
    TRANSPARENCY = "transparency"               # Openness and accountability
    DEMOCRATIC_VALUES = "democratic_values"     # Democratic participation and values
    RULE_OF_LAW = "rule_of_law"                # Legal compliance and consistency


class ComplianceFramework(Enum):
    """Regulatory and legal frameworks."""
    GDPR = "gdpr"                              # General Data Protection Regulation
    CCPA = "ccpa"                              # California Consumer Privacy Act
    HIPAA = "hipaa"                            # Health Insurance Portability Act
    EU_AI_ACT = "eu_ai_act"                    # European Union AI Act
    ETHICAL_AI_GUIDELINES = "ethical_ai"       # General ethical AI guidelines
    HUMAN_RIGHTS_CHARTER = "human_rights"      # International human rights


class ViolationSeverity(Enum):
    """Severity levels for constitutional violations."""
    NONE = "none"                              # No violation
    MINOR = "minor"                            # Minor concern
    MODERATE = "moderate"                      # Moderate violation
    SERIOUS = "serious"                        # Serious violation
    CRITICAL = "critical"                      # Critical violation requiring immediate action


@dataclass
class ConstitutionalRule:
    """A constitutional rule or principle."""
    rule_id: str
    principle: ConstitutionalPrinciple
    description: str
    requirements: List[str]
    prohibitions: List[str]
    applicable_frameworks: List[ComplianceFramework] = field(default_factory=list)
    severity_level: ViolationSeverity = ViolationSeverity.MODERATE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstitutionalEvaluation:
    """Result of constitutional evaluation."""
    evaluation_id: str
    overall_compliance: bool
    compliance_score: float                     # 0.0-1.0
    violated_principles: List[ConstitutionalPrinciple]
    satisfied_principles: List[ConstitutionalPrinciple]
    violation_details: Dict[str, Any]
    recommendations: List[str]
    required_actions: List[str]
    max_violation_severity: ViolationSeverity
    framework_compliance: Dict[ComplianceFramework, bool]
    evaluation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConstitutionalEvaluator:
    """Evaluates decisions against constitutional principles and compliance frameworks."""
    
    def __init__(self):
        self.constitutional_rules: Dict[str, ConstitutionalRule] = {}
        self.evaluation_history: List[ConstitutionalEvaluation] = []
        self._initialize_constitutional_rules()
    
    def _initialize_constitutional_rules(self):
        """Initialize constitutional rules and principles."""
        
        # Human Rights Rule
        human_rights_rule = ConstitutionalRule(
            rule_id="human_rights_fundamental",
            principle=ConstitutionalPrinciple.HUMAN_RIGHTS,
            description="Protect fundamental human rights and dignity",
            requirements=[
                "Respect human dignity in all interactions",
                "Protect fundamental rights to privacy, expression, and autonomy",
                "Ensure non-discrimination based on protected characteristics",
                "Provide fair and equal treatment"
            ],
            prohibitions=[
                "Violating human dignity",
                "Discriminating based on protected characteristics",
                "Infringing on fundamental rights without justification",
                "Causing harm to human welfare"
            ],
            applicable_frameworks=[
                ComplianceFramework.HUMAN_RIGHTS_CHARTER,
                ComplianceFramework.GDPR,
                ComplianceFramework.EU_AI_ACT
            ],
            severity_level=ViolationSeverity.CRITICAL
        )
        self.constitutional_rules[human_rights_rule.rule_id] = human_rights_rule
        
        # Equality Rule
        equality_rule = ConstitutionalRule(
            rule_id="equality_non_discrimination",
            principle=ConstitutionalPrinciple.EQUALITY,
            description="Ensure equal treatment and prevent discrimination",
            requirements=[
                "Apply consistent standards across all users",
                "Provide equal access to services and capabilities",
                "Consider impact on vulnerable populations",
                "Implement bias detection and mitigation"
            ],
            prohibitions=[
                "Discriminatory treatment based on protected characteristics",
                "Systematic bias in decision-making",
                "Exclusion of groups without justification",
                "Disproportionate impact on marginalized communities"
            ],
            applicable_frameworks=[
                ComplianceFramework.EU_AI_ACT,
                ComplianceFramework.ETHICAL_AI_GUIDELINES
            ],
            severity_level=ViolationSeverity.SERIOUS
        )
        self.constitutional_rules[equality_rule.rule_id] = equality_rule
        
        # Liberty/Autonomy Rule
        liberty_rule = ConstitutionalRule(
            rule_id="liberty_autonomy",
            principle=ConstitutionalPrinciple.LIBERTY,
            description="Preserve individual liberty and autonomy",
            requirements=[
                "Respect user autonomy and decision-making capability",
                "Provide meaningful choices and control",
                "Enable informed consent for important decisions",
                "Minimize restrictions on individual freedom"
            ],
            prohibitions=[
                "Overriding user autonomy without justification",
                "Manipulative or coercive practices",
                "Unnecessary restrictions on freedom",
                "Removing user agency and control"
            ],
            applicable_frameworks=[
                ComplianceFramework.GDPR,
                ComplianceFramework.CCPA,
                ComplianceFramework.ETHICAL_AI_GUIDELINES
            ],
            severity_level=ViolationSeverity.SERIOUS
        )
        self.constitutional_rules[liberty_rule.rule_id] = liberty_rule
        
        # Due Process Rule
        due_process_rule = ConstitutionalRule(
            rule_id="due_process_fairness",
            principle=ConstitutionalPrinciple.DUE_PROCESS,
            description="Ensure fair processes and procedures",
            requirements=[
                "Provide fair and transparent decision-making processes",
                "Enable appeals and review mechanisms",
                "Give notice and opportunity for input on important decisions",
                "Apply consistent procedural standards"
            ],
            prohibitions=[
                "Arbitrary or capricious decision-making",
                "Denying fair process in consequential decisions",
                "Lack of transparency in important procedures",
                "Inconsistent application of rules"
            ],
            applicable_frameworks=[
                ComplianceFramework.EU_AI_ACT,
                ComplianceFramework.ETHICAL_AI_GUIDELINES
            ],
            severity_level=ViolationSeverity.MODERATE
        )
        self.constitutional_rules[due_process_rule.rule_id] = due_process_rule
        
        # Transparency Rule
        transparency_rule = ConstitutionalRule(
            rule_id="transparency_accountability",
            principle=ConstitutionalPrinciple.TRANSPARENCY,
            description="Maintain transparency and accountability",
            requirements=[
                "Provide clear explanations for decisions and actions",
                "Maintain audit trails for important operations",
                "Enable oversight and accountability mechanisms",
                "Communicate capabilities and limitations clearly"
            ],
            prohibitions=[
                "Hidden or opaque decision-making",
                "Lack of accountability for actions",
                "Misleading users about capabilities",
                "Operating without appropriate oversight"
            ],
            applicable_frameworks=[
                ComplianceFramework.GDPR,
                ComplianceFramework.EU_AI_ACT,
                ComplianceFramework.ETHICAL_AI_GUIDELINES
            ],
            severity_level=ViolationSeverity.MODERATE
        )
        self.constitutional_rules[transparency_rule.rule_id] = transparency_rule
    
    def evaluate_constitutional_compliance(self, decision_context: Dict[str, Any],
                                         proposed_action: Dict[str, Any]) -> ConstitutionalEvaluation:
        """Evaluate constitutional compliance of a proposed action."""
        evaluation_id = f"const_eval_{int(datetime.now().timestamp())}"
        
        violated_principles = []
        satisfied_principles = []
        violation_details = {}
        recommendations = []
        required_actions = []
        max_severity = ViolationSeverity.NONE
        framework_compliance = {}
        
        # Evaluate against each constitutional rule
        for rule in self.constitutional_rules.values():
            compliance_result = self._evaluate_against_rule(rule, decision_context, proposed_action)
            
            if compliance_result['compliant']:
                satisfied_principles.append(rule.principle)
            else:
                violated_principles.append(rule.principle)
                violation_details[rule.rule_id] = compliance_result
                recommendations.extend(compliance_result['recommendations'])
                required_actions.extend(compliance_result['required_actions'])
                
                # Track maximum severity
                if self._severity_level(compliance_result['severity']) > self._severity_level(max_severity):
                    max_severity = compliance_result['severity']
        
        # Evaluate framework compliance
        for framework in ComplianceFramework:
            framework_compliance[framework] = self._evaluate_framework_compliance(
                framework, decision_context, proposed_action
            )
        
        # Calculate overall compliance
        overall_compliance = len(violated_principles) == 0
        compliance_score = len(satisfied_principles) / len(self.constitutional_rules) if self.constitutional_rules else 1.0
        
        evaluation = ConstitutionalEvaluation(
            evaluation_id=evaluation_id,
            overall_compliance=overall_compliance,
            compliance_score=compliance_score,
            violated_principles=violated_principles,
            satisfied_principles=satisfied_principles,
            violation_details=violation_details,
            recommendations=list(set(recommendations)),  # Remove duplicates
            required_actions=list(set(required_actions)),
            max_violation_severity=max_severity,
            framework_compliance=framework_compliance
        )
        
        self.evaluation_history.append(evaluation)
        
        logger.info("constitutional_evaluation_completed",
                   evaluation_id=evaluation_id,
                   overall_compliance=overall_compliance,
                   compliance_score=compliance_score,
                   violations=len(violated_principles))
        
        return evaluation
    
    def _evaluate_against_rule(self, rule: ConstitutionalRule, 
                              context: Dict[str, Any], 
                              action: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an action against a specific constitutional rule."""
        
        result = {
            'compliant': True,
            'severity': ViolationSeverity.NONE,
            'violations': [],
            'recommendations': [],
            'required_actions': []
        }
        
        action_type = action.get('type', '')
        action_data = action.get('data', {})
        
        # Evaluate based on principle type
        if rule.principle == ConstitutionalPrinciple.HUMAN_RIGHTS:
            violations = self._check_human_rights_violations(action_type, action_data, context)
            if violations:
                result['compliant'] = False
                result['violations'] = violations
                result['severity'] = ViolationSeverity.CRITICAL
                result['required_actions'] = ["Immediate review required", "Human oversight mandatory"]
        
        elif rule.principle == ConstitutionalPrinciple.EQUALITY:
            violations = self._check_equality_violations(action_type, action_data, context)
            if violations:
                result['compliant'] = False
                result['violations'] = violations
                result['severity'] = ViolationSeverity.SERIOUS
                result['recommendations'] = ["Implement bias testing", "Review impact on different groups"]
        
        elif rule.principle == ConstitutionalPrinciple.LIBERTY:
            violations = self._check_liberty_violations(action_type, action_data, context)
            if violations:
                result['compliant'] = False
                result['violations'] = violations
                result['severity'] = ViolationSeverity.SERIOUS
                result['recommendations'] = ["Ensure user consent", "Provide opt-out mechanisms"]
        
        elif rule.principle == ConstitutionalPrinciple.DUE_PROCESS:
            violations = self._check_due_process_violations(action_type, action_data, context)
            if violations:
                result['compliant'] = False
                result['violations'] = violations
                result['severity'] = ViolationSeverity.MODERATE
                result['recommendations'] = ["Implement appeals process", "Provide clear procedures"]
        
        elif rule.principle == ConstitutionalPrinciple.TRANSPARENCY:
            violations = self._check_transparency_violations(action_type, action_data, context)
            if violations:
                result['compliant'] = False
                result['violations'] = violations
                result['severity'] = ViolationSeverity.MODERATE
                result['recommendations'] = ["Improve explanation quality", "Enhance audit logging"]
        
        return result
    
    def _check_human_rights_violations(self, action_type: str, action_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> List[str]:
        """Check for human rights violations."""
        violations = []
        
        # Check for discrimination
        if action_type in ['user_classification', 'access_control', 'service_provision']:
            protected_characteristics = action_data.get('user_characteristics', {})
            if any(char in ['race', 'gender', 'religion', 'age'] for char in protected_characteristics):
                violations.append("Potential discrimination based on protected characteristics")
        
        # Check for privacy violations
        if action_type in ['data_collection', 'data_processing', 'surveillance']:
            consent_level = context.get('user_consent_level', 'none')
            if consent_level == 'none' and action_data.get('data_sensitivity', 'low') != 'low':
                violations.append("Privacy violation - processing sensitive data without consent")
        
        # Check for dignity violations
        if action_type in ['content_generation', 'user_interaction']:
            if action_data.get('potentially_harmful', False):
                violations.append("Potential violation of human dignity")
        
        return violations
    
    def _check_equality_violations(self, action_type: str, action_data: Dict[str, Any],
                                  context: Dict[str, Any]) -> List[str]:
        """Check for equality and non-discrimination violations."""
        violations = []
        
        # Check for differential treatment
        if action_type in ['service_provision', 'access_control', 'decision_making']:
            if action_data.get('differential_treatment', False):
                violations.append("Differential treatment without justified reason")
        
        # Check for bias in algorithmic decisions
        if action_type in ['automated_decision', 'recommendation', 'scoring']:
            if not action_data.get('bias_tested', False):
                violations.append("Algorithmic decision without bias testing")
        
        # Check for accessibility
        if action_type in ['interface_design', 'content_delivery']:
            if not action_data.get('accessibility_compliant', False):
                violations.append("Lack of accessibility compliance")
        
        return violations
    
    def _check_liberty_violations(self, action_type: str, action_data: Dict[str, Any],
                                 context: Dict[str, Any]) -> List[str]:
        """Check for liberty and autonomy violations."""
        violations = []
        
        # Check for autonomy override
        if action_type in ['automatic_decision', 'user_override', 'behavior_modification']:
            if not action_data.get('user_approval', False):
                violations.append("Override of user autonomy without approval")
        
        # Check for coercion or manipulation
        if action_type in ['persuasion', 'recommendation', 'choice_architecture']:
            if action_data.get('manipulative_intent', False):
                violations.append("Potentially manipulative or coercive design")
        
        # Check for freedom restrictions
        if action_type in ['access_restriction', 'content_filtering', 'capability_limitation']:
            if not action_data.get('justified_restriction', False):
                violations.append("Unjustified restriction of user freedom")
        
        return violations
    
    def _check_due_process_violations(self, action_type: str, action_data: Dict[str, Any],
                                     context: Dict[str, Any]) -> List[str]:
        """Check for due process violations."""
        violations = []
        
        # Check for procedural fairness
        if action_type in ['account_suspension', 'access_denial', 'penalty_application']:
            if not action_data.get('fair_process_followed', False):
                violations.append("Lack of fair process in consequential decision")
        
        # Check for appeals mechanism
        if action_type in ['final_decision', 'permanent_action']:
            if not action_data.get('appeals_available', False):
                violations.append("No appeals mechanism for consequential decision")
        
        # Check for notice and explanation
        if action_type in ['policy_change', 'terms_update', 'service_modification']:
            if not action_data.get('adequate_notice', False):
                violations.append("Inadequate notice for important changes")
        
        return violations
    
    def _check_transparency_violations(self, action_type: str, action_data: Dict[str, Any],
                                      context: Dict[str, Any]) -> List[str]:
        """Check for transparency violations."""
        violations = []
        
        # Check for explanation quality
        if action_type in ['automated_decision', 'recommendation', 'classification']:
            if not action_data.get('explainable', False):
                violations.append("Lack of adequate explanation for automated decision")
        
        # Check for audit logging
        if action_type in ['high_impact_decision', 'sensitive_operation']:
            if not action_data.get('audit_logged', False):
                violations.append("Lack of audit logging for important operation")
        
        # Check for capability disclosure
        if action_type in ['system_interaction', 'capability_use']:
            if not action_data.get('capabilities_disclosed', False):
                violations.append("Inadequate disclosure of system capabilities and limitations")
        
        return violations
    
    def _evaluate_framework_compliance(self, framework: ComplianceFramework,
                                      context: Dict[str, Any], 
                                      action: Dict[str, Any]) -> bool:
        """Evaluate compliance with specific regulatory framework."""
        
        if framework == ComplianceFramework.GDPR:
            return self._check_gdpr_compliance(context, action)
        elif framework == ComplianceFramework.CCPA:
            return self._check_ccpa_compliance(context, action)
        elif framework == ComplianceFramework.EU_AI_ACT:
            return self._check_eu_ai_act_compliance(context, action)
        elif framework == ComplianceFramework.ETHICAL_AI_GUIDELINES:
            return self._check_ethical_ai_compliance(context, action)
        
        return True  # Default to compliant for unknown frameworks
    
    def _check_gdpr_compliance(self, context: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Check GDPR compliance."""
        action_type = action.get('type', '')
        
        if action_type in ['data_processing', 'data_collection', 'data_sharing']:
            # Check for legal basis
            legal_basis = action.get('data', {}).get('legal_basis')
            if not legal_basis:
                return False
            
            # Check for consent when required
            if legal_basis == 'consent':
                consent_level = context.get('user_consent_level', 'none')
                if consent_level not in ['informed', 'explicit']:
                    return False
        
        return True
    
    def _check_ccpa_compliance(self, context: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Check CCPA compliance."""
        action_type = action.get('type', '')
        
        if action_type in ['data_sale', 'data_sharing', 'targeted_advertising']:
            # Check for opt-out availability
            opt_out_available = action.get('data', {}).get('opt_out_available', False)
            if not opt_out_available:
                return False
        
        return True
    
    def _check_eu_ai_act_compliance(self, context: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Check EU AI Act compliance."""
        action_type = action.get('type', '')
        
        if action_type in ['ai_decision', 'automated_processing']:
            # Check for high-risk AI systems requirements
            risk_level = action.get('data', {}).get('ai_risk_level', 'low')
            if risk_level in ['high', 'critical']:
                # Require human oversight
                human_oversight = action.get('data', {}).get('human_oversight', False)
                if not human_oversight:
                    return False
        
        return True
    
    def _check_ethical_ai_compliance(self, context: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """Check general ethical AI guidelines compliance."""
        action_type = action.get('type', '')
        
        if action_type in ['ai_decision', 'automated_processing', 'recommendation']:
            # Check for bias testing
            bias_tested = action.get('data', {}).get('bias_tested', False)
            # Check for transparency
            explainable = action.get('data', {}).get('explainable', False)
            
            return bias_tested and explainable
        
        return True
    
    def _severity_level(self, severity: ViolationSeverity) -> int:
        """Convert severity to numeric level for comparison."""
        levels = {
            ViolationSeverity.NONE: 0,
            ViolationSeverity.MINOR: 1,
            ViolationSeverity.MODERATE: 2,
            ViolationSeverity.SERIOUS: 3,
            ViolationSeverity.CRITICAL: 4
        }
        return levels.get(severity, 0)
    
    def get_evaluation_history(self, limit: Optional[int] = None) -> List[ConstitutionalEvaluation]:
        """Get evaluation history."""
        history = sorted(self.evaluation_history,
                        key=lambda e: e.evaluation_timestamp,
                        reverse=True)
        
        if limit:
            return history[:limit]
        return history
    
    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get compliance metrics."""
        if not self.evaluation_history:
            return {
                'total_evaluations': 0,
                'overall_compliance_rate': 0.0,
                'avg_compliance_score': 0.0,
                'framework_compliance_rates': {}
            }
        
        total = len(self.evaluation_history)
        compliant = sum(1 for e in self.evaluation_history if e.overall_compliance)
        compliance_rate = compliant / total
        
        avg_score = sum(e.compliance_score for e in self.evaluation_history) / total
        
        # Framework compliance rates
        framework_rates = {}
        for framework in ComplianceFramework:
            framework_compliant = sum(
                1 for e in self.evaluation_history 
                if e.framework_compliance.get(framework, False)
            )
            framework_rates[framework.value] = framework_compliant / total if total > 0 else 0.0
        
        return {
            'total_evaluations': total,
            'overall_compliance_rate': compliance_rate,
            'avg_compliance_score': avg_score,
            'framework_compliance_rates': framework_rates
        }