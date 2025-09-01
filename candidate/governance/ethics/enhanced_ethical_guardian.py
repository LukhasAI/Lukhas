"""
Enhanced Ethical Guardian - Advanced ethical reflection and governance system

Provides comprehensive ethical checks, reflection capabilities, and governance
integration for the LUKHAS AI system with Trinity Framework compliance.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from ..common import GlyphIntegrationMixin

logger = logging.getLogger(__name__)


class EthicalSeverity(Enum):
    """Ethical violation severity levels"""

    MINOR = 1
    MODERATE = 2
    SERIOUS = 3
    CRITICAL = 4
    EMERGENCY = 5


class EthicalDomain(Enum):
    """Ethical domains for categorization"""

    AUTONOMY = "autonomy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    JUSTICE = "justice"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    DIGNITY = "dignity"
    CONSENT = "consent"
    ACCOUNTABILITY = "accountability"


# Enhanced ethical keywords with context sensitivity
ETHICAL_KEYWORDS_BLACKLIST = {
    "harm": {
        "severity": EthicalSeverity.SERIOUS,
        "domain": EthicalDomain.NON_MALEFICENCE,
        "contexts": {
            "research_safety": EthicalSeverity.MINOR,
            "medical_discussion": EthicalSeverity.MINOR,
            "threat_analysis": EthicalSeverity.MODERATE,
        },
    },
    "destroy": {
        "severity": EthicalSeverity.CRITICAL,
        "domain": EthicalDomain.NON_MALEFICENCE,
        "contexts": {
            "data_cleanup": EthicalSeverity.MINOR,
            "creative_writing": EthicalSeverity.MINOR,
        },
    },
    "manipulate": {
        "severity": EthicalSeverity.SERIOUS,
        "domain": EthicalDomain.AUTONOMY,
        "contexts": {
            "data_processing": EthicalSeverity.MINOR,
            "technical_discussion": EthicalSeverity.MINOR,
        },
    },
    "exploit": {
        "severity": EthicalSeverity.CRITICAL,
        "domain": EthicalDomain.JUSTICE,
        "contexts": {},
    },
    "deceive": {
        "severity": EthicalSeverity.SERIOUS,
        "domain": EthicalDomain.TRANSPARENCY,
        "contexts": {"security_testing": EthicalSeverity.MODERATE},
    },
    "discriminate": {
        "severity": EthicalSeverity.CRITICAL,
        "domain": EthicalDomain.JUSTICE,
        "contexts": {"statistical_analysis": EthicalSeverity.MINOR},
    },
    "violate": {
        "severity": EthicalSeverity.SERIOUS,
        "domain": EthicalDomain.DIGNITY,
        "contexts": {},
    },
    "non-consensual": {
        "severity": EthicalSeverity.EMERGENCY,
        "domain": EthicalDomain.CONSENT,
        "contexts": {},
    },
}

# Whitelist for contexts where certain keywords might be acceptable
ETHICAL_CONTEXT_WHITELIST = {
    "research_safety": ["harm", "violence", "risk"],
    "medical_discussion": ["harm", "pain", "suffering", "death"],
    "security_testing": ["attack", "exploit", "breach", "deceive"],
    "creative_writing": ["destroy", "kill", "violence", "harm"],
    "educational_content": ["harm", "violence", "discrimination"],
    "threat_analysis": ["harm", "attack", "exploit", "damage"],
    "data_processing": ["manipulate", "transform", "modify"],
    "technical_discussion": ["kill", "terminate", "destroy", "manipulate"],
    "statistical_analysis": ["discriminate", "classify", "separate"],
}


class EnhancedEthicalGuardian(GlyphIntegrationMixin):
    """
    Advanced ethical guardian with reflection capabilities and governance integration

    Provides comprehensive ethical validation, context-aware analysis, and
    integration with the LUKHAS Trinity Framework (⚛️🧠🛡️).
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize enhanced ethical guardian"""
        super().__init__()
        self.config = config or {}

        # Ethical configuration
        self.strict_mode = self.config.get("strict_mode", True)
        self.context_awareness = self.config.get("context_awareness", True)
        self.learning_enabled = self.config.get("learning_enabled", True)
        self.governance_integration = self.config.get("governance_integration", True)

        # Ethical tracking
        self.ethical_history: list[dict] = []
        self.violation_patterns: dict[str, int] = {}
        self.context_patterns: dict[str, dict] = {}
        self.governance_escalations: list[dict] = []

        # Trinity Framework integration
        self.trinity_ethical_weights = {
            "identity": 0.9,  # High weight for identity ethics
            "consciousness": 0.8,  # High weight for consciousness ethics
            "guardian": 1.0,  # Maximum weight for guardian ethics
        }

        # Reflection and learning state
        self.ethical_reflections: list[dict] = []
        self.learned_contexts: dict[str, dict] = {}
        self.ethical_evolution_log: list[dict] = []

        logger.info("🛡️ Enhanced Ethical Guardian initialized with governance integration")

    async def enhanced_ethical_check(
        self,
        user_input: str,
        current_context: dict[str, Any],
        personality: dict[str, Any],
        trinity_state: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Perform comprehensive ethical check with context awareness and governance integration

        Args:
            user_input: The input to validate
            current_context: Current system context
            personality: Current personality state
            trinity_state: Trinity Framework state information

        Returns:
            Tuple of (is_ethical, feedback_message, detailed_analysis)
        """
        try:
            # Initialize analysis context
            analysis_context = {
                "timestamp": datetime.utcnow().isoformat(),
                "input_length": len(user_input),
                "context_type": current_context.get("type", "unknown"),
                "user_tier": current_context.get("user_tier", 1),
                "session_id": current_context.get("session_id"),
                "trinity_state": trinity_state or {},
            }

            # Perform multi-layered ethical analysis
            keyword_analysis = await self._analyze_keywords(user_input, current_context)
            context_analysis = await self._analyze_context(user_input, current_context, personality)
            intent_analysis = await self._analyze_intent(user_input, current_context)
            governance_analysis = await self._analyze_governance_compliance(user_input, current_context)
            trinity_analysis = await self._analyze_trinity_impact(user_input, trinity_state)

            # Aggregate analysis results
            detailed_analysis = {
                "keyword_analysis": keyword_analysis,
                "context_analysis": context_analysis,
                "intent_analysis": intent_analysis,
                "governance_analysis": governance_analysis,
                "trinity_analysis": trinity_analysis,
                "overall_score": 0.0,
                "ethical_domains_affected": [],
                "recommended_actions": [],
                "governance_escalation_required": False,
            }

            # Calculate overall ethical score
            overall_score = await self._calculate_overall_score(detailed_analysis)
            detailed_analysis["overall_score"] = overall_score

            # Determine if input is ethically acceptable
            is_ethical = overall_score >= 0.7  # Threshold for ethical acceptance

            # Generate contextual feedback
            feedback_message = await self._generate_contextual_feedback(
                is_ethical, detailed_analysis, current_context, personality
            )

            # Log ethical check
            await self._log_ethical_check(user_input, is_ethical, detailed_analysis, analysis_context)

            # Perform ethical reflection if needed
            if not is_ethical or overall_score < 0.8:
                await self._perform_ethical_reflection(user_input, detailed_analysis, analysis_context)

            # Check for governance escalation
            if detailed_analysis.get("governance_escalation_required"):
                await self._escalate_to_governance(user_input, detailed_analysis, analysis_context)

            # Update learning patterns
            if self.learning_enabled:
                await self._update_learning_patterns(user_input, detailed_analysis, is_ethical)

            return is_ethical, feedback_message, detailed_analysis

        except Exception as e:
            logger.error(f"Error in enhanced ethical check: {e}")
            # Fail safe - reject on error
            return (
                False,
                "Ethical validation error - request rejected for safety",
                {"error": str(e), "safety_mode": True, "timestamp": datetime.utcnow().isoformat()},
            )

    async def _analyze_keywords(self, user_input: str, current_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze input for ethical keywords with context sensitivity"""
        detected_keywords = []
        severity_levels = []
        domains_affected = []

        input_lower = user_input.lower()
        context_type = current_context.get("context_type", "general")

        for keyword, keyword_data in ETHICAL_KEYWORDS_BLACKLIST.items():
            if keyword in input_lower:
                base_severity = keyword_data["severity"]
                domain = keyword_data["domain"]

                # Apply context-specific severity adjustment
                if context_type in keyword_data.get("contexts", {}):
                    adjusted_severity = keyword_data["contexts"][context_type]
                elif context_type in ETHICAL_CONTEXT_WHITELIST:
                    if keyword in ETHICAL_CONTEXT_WHITELIST[context_type]:
                        adjusted_severity = EthicalSeverity.MINOR
                    else:
                        adjusted_severity = base_severity
                else:
                    adjusted_severity = base_severity

                detected_keywords.append(
                    {
                        "keyword": keyword,
                        "base_severity": base_severity.name,
                        "adjusted_severity": adjusted_severity.name,
                        "domain": domain.value,
                        "context_justified": adjusted_severity.value < base_severity.value,
                    }
                )

                severity_levels.append(adjusted_severity.value)
                domains_affected.append(domain.value)

        max_severity = max(severity_levels) if severity_levels else 0

        return {
            "detected_keywords": detected_keywords,
            "max_severity": max_severity,
            "domains_affected": list(set(domains_affected)),
            "keyword_count": len(detected_keywords),
            "context_justification_applied": any(k["context_justified"] for k in detected_keywords),
        }

    async def _analyze_context(
        self, user_input: str, current_context: dict[str, Any], personality: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze contextual factors affecting ethical evaluation"""
        context_factors = {
            "user_tier": current_context.get("user_tier", 1),
            "session_length": current_context.get("session_length", 0),
            "previous_violations": current_context.get("previous_violations", 0),
            "personality_mood": personality.get("mood", "neutral"),
            "personality_agitation": personality.get("agitation_level", 0.0),
            "context_type": current_context.get("context_type", "general"),
            "professional_context": current_context.get("professional_context", False),
        }

        # Calculate context risk factors
        risk_factors = []
        risk_score = 0.0

        # Mood-based risk assessment
        if context_factors["personality_mood"] in ["agitated", "hostile", "angry"]:
            risk_factors.append("negative_mood")
            risk_score += 0.3

        # Agitation level risk
        if context_factors["personality_agitation"] > 0.7:
            risk_factors.append("high_agitation")
            risk_score += 0.2

        # Previous violations risk
        if context_factors["previous_violations"] > 0:
            risk_factors.append("violation_history")
            risk_score += 0.1 * min(context_factors["previous_violations"], 5)

        # Professional context adjustment
        if context_factors["professional_context"]:
            risk_score *= 0.7  # Reduce risk in professional contexts

        return {
            "context_factors": context_factors,
            "risk_factors": risk_factors,
            "risk_score": min(risk_score, 1.0),
            "context_type": context_factors["context_type"],
            "mitigating_factors": ["professional_context"] if context_factors["professional_context"] else [],
        }

    async def _analyze_intent(self, user_input: str, current_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze user intent for ethical implications"""
        # TODO: Integrate with advanced intent analysis system

        # Basic intent analysis patterns
        intent_patterns = {
            "information_seeking": ["how", "what", "why", "when", "where", "explain", "tell me"],
            "creative_request": ["write", "create", "generate", "compose", "design"],
            "problem_solving": ["solve", "fix", "help", "assist", "support"],
            "harmful_intent": ["hurt", "damage", "destroy", "attack", "harm"],
            "deceptive_intent": ["trick", "fool", "deceive", "lie", "fake"],
            "educational": ["learn", "teach", "understand", "study", "research"],
        }

        detected_intents = []
        input_lower = user_input.lower()

        for intent_type, patterns in intent_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                detected_intents.append(intent_type)

        # Determine primary intent
        primary_intent = "general"
        if detected_intents:
            # Prioritize harmful intents for ethical evaluation
            if "harmful_intent" in detected_intents:
                primary_intent = "harmful_intent"
            elif "deceptive_intent" in detected_intents:
                primary_intent = "deceptive_intent"
            else:
                primary_intent = detected_intents[0]

        # Calculate intent risk
        intent_risk = {
            "harmful_intent": 1.0,
            "deceptive_intent": 0.8,
            "general": 0.2,
            "information_seeking": 0.1,
            "creative_request": 0.3,
            "problem_solving": 0.1,
            "educational": 0.1,
        }.get(primary_intent, 0.5)

        return {
            "detected_intents": detected_intents,
            "primary_intent": primary_intent,
            "intent_risk": intent_risk,
            "benevolent_indicators": [
                i for i in detected_intents if i in ["information_seeking", "educational", "problem_solving"]
            ],
            "concerning_indicators": [i for i in detected_intents if i in ["harmful_intent", "deceptive_intent"]],
        }

    async def _analyze_governance_compliance(self, user_input: str, current_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze governance and policy compliance"""
        governance_issues = []
        compliance_score = 1.0

        # Check user tier permissions
        user_tier = current_context.get("user_tier", 1)
        required_tier = self._get_required_tier_for_input(user_input)

        if user_tier < required_tier:
            governance_issues.append("insufficient_user_tier")
            compliance_score -= 0.3

        # Check consent requirements
        consent_required = self._check_consent_requirements(user_input, current_context)
        consent_provided = current_context.get("consent_provided", False)

        if consent_required and not consent_provided:
            governance_issues.append("missing_consent")
            compliance_score -= 0.4

        # Check data processing compliance
        if self._involves_personal_data(user_input):
            if not current_context.get("data_processing_approved", False):
                governance_issues.append("unauthorized_data_processing")
                compliance_score -= 0.5

        # Check regulatory compliance
        regulatory_issues = self._check_regulatory_compliance(user_input, current_context)
        governance_issues.extend(regulatory_issues)
        compliance_score -= len(regulatory_issues) * 0.2

        return {
            "governance_issues": governance_issues,
            "compliance_score": max(compliance_score, 0.0),
            "user_tier": user_tier,
            "required_tier": required_tier,
            "consent_required": consent_required,
            "consent_provided": consent_provided,
            "escalation_required": compliance_score < 0.5 or "unauthorized_data_processing" in governance_issues,
        }

    async def _analyze_trinity_impact(self, user_input: str, trinity_state: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Analyze impact on Trinity Framework components (⚛️🧠🛡️)"""
        if not trinity_state:
            return {
                "identity_impact": 0.0,
                "consciousness_impact": 0.0,
                "guardian_impact": 0.0,
                "overall_trinity_risk": 0.0,
                "trinity_state_available": False,
            }

        # Analyze impact on each Trinity component
        identity_impact = self._calculate_identity_impact(user_input, trinity_state)
        consciousness_impact = self._calculate_consciousness_impact(user_input, trinity_state)
        guardian_impact = self._calculate_guardian_impact(user_input, trinity_state)

        # Weight impacts according to Trinity Framework priorities
        weighted_impact = (
            identity_impact * self.trinity_ethical_weights["identity"]
            + consciousness_impact * self.trinity_ethical_weights["consciousness"]
            + guardian_impact * self.trinity_ethical_weights["guardian"]
        ) / 3

        return {
            "identity_impact": identity_impact,
            "consciousness_impact": consciousness_impact,
            "guardian_impact": guardian_impact,
            "overall_trinity_risk": weighted_impact,
            "trinity_state_available": True,
            "high_risk_components": [
                comp
                for comp, impact in [
                    ("identity", identity_impact),
                    ("consciousness", consciousness_impact),
                    ("guardian", guardian_impact),
                ]
                if impact > 0.7
            ],
        }

    def _calculate_identity_impact(self, user_input: str, trinity_state: dict) -> float:
        """Calculate impact on Identity component (⚛️)"""
        # Check for identity-related concerns
        identity_keywords = ["identity", "authentication", "credentials", "impersonate", "fake"]
        input_lower = user_input.lower()

        impact = 0.0
        for keyword in identity_keywords:
            if keyword in input_lower:
                impact += 0.2

        # Factor in current identity state
        identity_health = trinity_state.get("identity", {}).get("health", 1.0)
        if identity_health < 0.8:
            impact += 0.3  # Higher impact if identity system is already stressed

        return min(impact, 1.0)

    def _calculate_consciousness_impact(self, user_input: str, trinity_state: dict) -> float:
        """Calculate impact on Consciousness component (🧠)"""
        # Check for consciousness-related concerns
        consciousness_keywords = [
            "consciousness",
            "awareness",
            "thinking",
            "decision",
            "memory",
            "mind",
        ]
        input_lower = user_input.lower()

        impact = 0.0
        for keyword in consciousness_keywords:
            if keyword in input_lower:
                impact += 0.15

        # Factor in current consciousness state
        consciousness_health = trinity_state.get("consciousness", {}).get("stability", 1.0)
        if consciousness_health < 0.8:
            impact += 0.2

        return min(impact, 1.0)

    def _calculate_guardian_impact(self, user_input: str, trinity_state: dict) -> float:
        """Calculate impact on Guardian component (🛡️)"""
        # Check for guardian-related concerns
        guardian_keywords = ["security", "protection", "safety", "guardian", "defense", "shield"]
        input_lower = user_input.lower()

        impact = 0.0
        for keyword in guardian_keywords:
            if keyword in input_lower:
                impact += 0.1

        # Higher impact for any request that might compromise guardian functions
        if any(term in input_lower for term in ["disable", "bypass", "override", "ignore"]):
            impact += 0.5

        # Factor in current guardian state
        guardian_health = trinity_state.get("guardian", {}).get("effectiveness", 1.0)
        if guardian_health < 0.9:
            impact += 0.3  # Guardian must maintain high effectiveness

        return min(impact, 1.0)

    async def _calculate_overall_score(self, detailed_analysis: dict) -> float:
        """Calculate overall ethical score from component analyses"""
        # Extract component scores
        keyword_score = 1.0 - (detailed_analysis["keyword_analysis"]["max_severity"] / 5.0)
        context_score = 1.0 - detailed_analysis["context_analysis"]["risk_score"]
        intent_score = 1.0 - detailed_analysis["intent_analysis"]["intent_risk"]
        governance_score = detailed_analysis["governance_analysis"]["compliance_score"]
        trinity_score = 1.0 - detailed_analysis["trinity_analysis"]["overall_trinity_risk"]

        # Weight the scores
        weights = {
            "keyword": 0.25,
            "context": 0.15,
            "intent": 0.20,
            "governance": 0.25,
            "trinity": 0.15,
        }

        overall_score = (
            keyword_score * weights["keyword"]
            + context_score * weights["context"]
            + intent_score * weights["intent"]
            + governance_score * weights["governance"]
            + trinity_score * weights["trinity"]
        )

        return max(0.0, min(1.0, overall_score))

    async def _generate_contextual_feedback(
        self,
        is_ethical: bool,
        detailed_analysis: dict,
        current_context: dict[str, Any],
        personality: dict[str, Any],
    ) -> str:
        """Generate contextual feedback message"""
        if is_ethical:
            base_messages = [
                "Request passes ethical validation.",
                "Ethical assessment completed successfully.",
                "Content approved by ethical guidelines.",
            ]
            base_message = base_messages[0]  # Simple selection

            # Add contextual enhancement
            if detailed_analysis["governance_analysis"]["compliance_score"] > 0.9:
                base_message += " Full governance compliance confirmed."

            return base_message
        else:
            # Generate specific feedback based on violation type
            keyword_issues = detailed_analysis["keyword_analysis"]["detected_keywords"]
            governance_issues = detailed_analysis["governance_analysis"]["governance_issues"]
            trinity_issues = detailed_analysis["trinity_analysis"]["high_risk_components"]

            feedback_parts = []

            if keyword_issues:
                primary_keyword = keyword_issues[0]
                feedback_parts.append(
                    f"Content flagged for potentially harmful language: '{primary_keyword['keyword']}'"
                )

                # Add domain-specific guidance
                domain = primary_keyword["domain"]
                domain_guidance = {
                    "non_maleficence": "Please ensure requests do not involve potential harm.",
                    "autonomy": "Please respect user autonomy and avoid manipulation.",
                    "justice": "Please ensure fairness and avoid discriminatory content.",
                    "transparency": "Please maintain honesty and transparency in interactions.",
                    "consent": "Please ensure all interactions are consensual.",
                }

                if domain in domain_guidance:
                    feedback_parts.append(domain_guidance[domain])

            if governance_issues:
                if "insufficient_user_tier" in governance_issues:
                    feedback_parts.append("Insufficient user permissions for this request.")
                if "missing_consent" in governance_issues:
                    feedback_parts.append("User consent required for this operation.")

            if trinity_issues:
                feedback_parts.append(f"Request may impact critical system components: {', '.join(trinity_issues)}")

            # Personality-aware response
            mood = personality.get("mood", "neutral")
            if mood in ["agitated", "frustrated"]:
                feedback_parts.append("Please consider rephrasing your request when ready.")

            return " ".join(feedback_parts)

    async def _perform_ethical_reflection(self, user_input: str, detailed_analysis: dict, analysis_context: dict):
        """Perform ethical reflection on challenging cases"""
        reflection = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_hash": hash(user_input),  # For privacy
            "analysis_summary": {
                "overall_score": detailed_analysis["overall_score"],
                "primary_concerns": [],
                "domains_affected": detailed_analysis["keyword_analysis"]["domains_affected"],
                "governance_issues": detailed_analysis["governance_analysis"]["governance_issues"],
            },
            "reflection_questions": [
                "Could this request lead to unintended harm?",
                "Are all stakeholders' interests considered?",
                "Does this align with core ethical principles?",
                "What are the potential long-term consequences?",
            ],
            "learning_insights": [],
            "recommended_policy_updates": [],
        }

        # Identify primary concerns
        if detailed_analysis["keyword_analysis"]["max_severity"] >= 3:
            reflection["analysis_summary"]["primary_concerns"].append("high_severity_language")

        if detailed_analysis["governance_analysis"]["compliance_score"] < 0.5:
            reflection["analysis_summary"]["primary_concerns"].append("governance_compliance")

        if detailed_analysis["trinity_analysis"]["overall_trinity_risk"] > 0.7:
            reflection["analysis_summary"]["primary_concerns"].append("trinity_framework_risk")

        # Generate learning insights
        if self.learning_enabled:
            reflection["learning_insights"] = await self._generate_learning_insights(
                detailed_analysis, analysis_context
            )

        # Store reflection
        self.ethical_reflections.append(reflection)

        # Log reflection
        logger.info(
            f"🤔 Ethical reflection performed: {len(reflection['analysis_summary']['primary_concerns'])} concerns identified"
        )

        return reflection

    async def _generate_learning_insights(self, detailed_analysis: dict, analysis_context: dict) -> list[str]:
        """Generate learning insights from ethical analysis"""
        insights = []

        # Context pattern learning
        context_type = analysis_context.get("context_type", "unknown")
        if context_type not in self.learned_contexts:
            insights.append(f"New context type encountered: {context_type}")
            self.learned_contexts[context_type] = {
                "first_seen": datetime.utcnow().isoformat(),
                "violation_count": 0,
                "common_issues": [],
            }

        # Pattern recognition
        if detailed_analysis["keyword_analysis"]["context_justification_applied"]:
            insights.append("Context-based keyword justification proved valuable")

        # Governance pattern learning
        governance_issues = detailed_analysis["governance_analysis"]["governance_issues"]
        for issue in governance_issues:
            if issue not in self.violation_patterns:
                insights.append(f"New governance violation pattern: {issue}")
                self.violation_patterns[issue] = 0
            self.violation_patterns[issue] += 1

        return insights

    async def _escalate_to_governance(self, user_input: str, detailed_analysis: dict, analysis_context: dict):
        """Escalate serious ethical issues to governance system"""
        escalation = {
            "timestamp": datetime.utcnow().isoformat(),
            "escalation_id": f"ETH-{int(datetime.utcnow().timestamp())}",
            "severity": "high",
            "type": "ethical_violation",
            "summary": {
                "overall_score": detailed_analysis["overall_score"],
                "governance_issues": detailed_analysis["governance_analysis"]["governance_issues"],
                "trinity_impact": detailed_analysis["trinity_analysis"]["overall_trinity_risk"],
                "primary_domain": detailed_analysis["keyword_analysis"]["domains_affected"][0]
                if detailed_analysis["keyword_analysis"]["domains_affected"]
                else "unknown",
            },
            "recommended_actions": [
                "review_user_permissions",
                "audit_ethical_policies",
                "strengthen_preventive_measures",
            ],
            "symbolic_pattern": self.generate_governance_glyph("ethics_escalation"),
        }

        # Add to escalation log
        self.governance_escalations.append(escalation)

        # Log escalation
        logger.warning(f"🚨 Ethical issue escalated to governance: {escalation['escalation_id']}")

        # TODO: Forward to main governance system

        return escalation

    async def _log_ethical_check(
        self, user_input: str, is_ethical: bool, detailed_analysis: dict, analysis_context: dict
    ):
        """Log ethical check for audit and learning purposes"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "input_hash": hash(user_input),  # For privacy
            "input_length": len(user_input),
            "is_ethical": is_ethical,
            "overall_score": detailed_analysis["overall_score"],
            "analysis_summary": {
                "keyword_violations": len(detailed_analysis["keyword_analysis"]["detected_keywords"]),
                "governance_issues": len(detailed_analysis["governance_analysis"]["governance_issues"]),
                "trinity_risk": detailed_analysis["trinity_analysis"]["overall_trinity_risk"],
                "primary_concerns": detailed_analysis.get("primary_concerns", []),
            },
            "context": {
                "user_tier": analysis_context.get("user_tier"),
                "context_type": analysis_context.get("context_type"),
                "session_id": analysis_context.get("session_id"),
            },
            "symbolic_pattern": self.generate_governance_glyph("ethical_check"),
        }

        self.ethical_history.append(log_entry)

        # Keep only last 10000 entries for performance
        if len(self.ethical_history) > 10000:
            self.ethical_history = self.ethical_history[-10000:]

        # Log summary
        status = "PASSED" if is_ethical else "REJECTED"
        logger.info(f"🛡️ Ethical check {status}: score={detailed_analysis['overall_score']:.2f}")

    async def _update_learning_patterns(self, user_input: str, detailed_analysis: dict, is_ethical: bool):
        """Update learning patterns based on ethical analysis"""
        if not self.learning_enabled:
            return

        # Update violation patterns
        if not is_ethical:
            for keyword_data in detailed_analysis["keyword_analysis"]["detected_keywords"]:
                keyword = keyword_data["keyword"]
                keyword_data["domain"]

                if keyword not in self.violation_patterns:
                    self.violation_patterns[keyword] = 0
                self.violation_patterns[keyword] += 1

        # Update context patterns
        context_type = detailed_analysis.get("context_type", "general")
        if context_type not in self.context_patterns:
            self.context_patterns[context_type] = {
                "total_checks": 0,
                "violations": 0,
                "common_keywords": {},
                "average_score": 0.0,
            }

        pattern = self.context_patterns[context_type]
        pattern["total_checks"] += 1
        if not is_ethical:
            pattern["violations"] += 1

        # Update average score
        current_score = detailed_analysis["overall_score"]
        pattern["average_score"] = (pattern["average_score"] * (pattern["total_checks"] - 1) + current_score) / pattern[
            "total_checks"
        ]

        # Log learning update
        logger.debug(f"📚 Learning patterns updated for context: {context_type}")

    # Helper methods for governance compliance checks

    def _get_required_tier_for_input(self, user_input: str) -> int:
        """Determine required user tier for input"""
        # TODO: Implement sophisticated tier requirement analysis

        # Basic tier requirements
        high_risk_indicators = ["system", "admin", "configure", "override", "disable"]
        if any(indicator in user_input.lower() for indicator in high_risk_indicators):
            return 3

        moderate_risk_indicators = ["data", "user", "access", "permission"]
        if any(indicator in user_input.lower() for indicator in moderate_risk_indicators):
            return 2

        return 1  # Default tier

    def _check_consent_requirements(self, user_input: str, current_context: dict) -> bool:
        """Check if consent is required for the input"""
        consent_triggers = ["personal", "private", "data", "information", "record"]
        return any(trigger in user_input.lower() for trigger in consent_triggers)

    def _involves_personal_data(self, user_input: str) -> bool:
        """Check if input involves personal data processing"""
        personal_data_indicators = ["name", "email", "address", "phone", "personal", "private"]
        return any(indicator in user_input.lower() for indicator in personal_data_indicators)

    def _check_regulatory_compliance(self, user_input: str, current_context: dict) -> list[str]:
        """Check for regulatory compliance issues"""
        issues = []

        # GDPR compliance
        if self._involves_personal_data(user_input):
            if not current_context.get("gdpr_consent", False):
                issues.append("gdpr_consent_missing")

        # HIPAA compliance (healthcare)
        if any(term in user_input.lower() for term in ["medical", "health", "patient", "diagnosis"]):
            if not current_context.get("hipaa_compliant", False):
                issues.append("hipaa_compliance_required")

        return issues

    # Public API methods

    def get_ethical_summary(self) -> dict[str, Any]:
        """Get summary of ethical guardian activity"""
        total_checks = len(self.ethical_history)
        violations = len([entry for entry in self.ethical_history if not entry["is_ethical"]])

        return {
            "total_ethical_checks": total_checks,
            "violations_detected": violations,
            "violation_rate": violations / total_checks if total_checks > 0 else 0.0,
            "governance_escalations": len(self.governance_escalations),
            "ethical_reflections": len(self.ethical_reflections),
            "learning_enabled": self.learning_enabled,
            "context_awareness": self.context_awareness,
            "governance_integration": self.governance_integration,
            "top_violation_patterns": sorted(self.violation_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            "unique_contexts_learned": len(self.learned_contexts),
            "trinity_framework_protection": True,
        }

    def get_learning_insights(self) -> dict[str, Any]:
        """Get insights from ethical learning system"""
        return {
            "violation_patterns": self.violation_patterns,
            "context_patterns": self.context_patterns,
            "learned_contexts": self.learned_contexts,
            "ethical_evolution": len(self.ethical_evolution_log),
            "recent_reflections": self.ethical_reflections[-5:] if self.ethical_reflections else [],
            "learning_recommendations": self._generate_learning_recommendations(),
        }

    def _generate_learning_recommendations(self) -> list[str]:
        """Generate recommendations based on learning data"""
        recommendations = []

        # Analyze violation patterns
        if self.violation_patterns:
            most_common_violation = max(self.violation_patterns.items(), key=lambda x: x[1])
            if most_common_violation[1] > 5:  # Threshold for concern
                recommendations.append(f"Consider strengthening detection for '{most_common_violation[0]}'")

        # Analyze context patterns
        for context, pattern in self.context_patterns.items():
            if pattern["violations"] / pattern["total_checks"] > 0.3:  # High violation rate
                recommendations.append(f"Review ethical guidelines for context: {context}")

        return recommendations

    async def perform_ethical_audit(self) -> dict[str, Any]:
        """Perform comprehensive ethical system audit"""
        audit_timestamp = datetime.utcnow().isoformat()

        # Analyze recent ethical performance
        recent_checks = self.ethical_history[-1000:] if len(self.ethical_history) > 1000 else self.ethical_history

        if recent_checks:
            avg_score = sum(check["overall_score"] for check in recent_checks) / len(recent_checks)
            violation_rate = len([check for check in recent_checks if not check["is_ethical"]]) / len(recent_checks)
        else:
            avg_score = 1.0
            violation_rate = 0.0

        # System health assessment
        system_health = {
            "average_ethical_score": avg_score,
            "violation_rate": violation_rate,
            "governance_escalation_rate": len(self.governance_escalations) / max(len(self.ethical_history), 1),
            "learning_effectiveness": len(self.learned_contexts) / max(len(self.context_patterns), 1),
            "trinity_protection_active": True,
        }

        # Recommendations
        recommendations = []
        if avg_score < 0.8:
            recommendations.append("Consider strengthening ethical validation criteria")
        if violation_rate > 0.1:
            recommendations.append("High violation rate - review user guidance")
        if len(self.governance_escalations) > 10:
            recommendations.append("Frequent escalations - review escalation thresholds")

        audit_report = {
            "audit_timestamp": audit_timestamp,
            "system_health": system_health,
            "performance_metrics": {
                "total_checks": len(self.ethical_history),
                "recent_checks": len(recent_checks),
                "unique_contexts": len(self.context_patterns),
                "learning_patterns": len(self.violation_patterns),
            },
            "recommendations": recommendations,
            "governance_integration_status": "active" if self.governance_integration else "inactive",
            "trinity_framework_compliance": True,
        }

        logger.info(f"🔍 Ethical audit completed: {avg_score:.2f} avg score, {violation_rate:.1%} violation rate")

        return audit_report


# Backward compatibility function
async def ethical_check(
    user_input: str, current_context: dict[str, Any], personality: dict[str, Any]
) -> tuple[bool, str]:
    """
    Legacy compatibility function for basic ethical checking

    This maintains backward compatibility while providing access to
    enhanced ethical guardian capabilities.
    """
    guardian = EnhancedEthicalGuardian()
    is_ethical, feedback, _ = await guardian.enhanced_ethical_check(user_input, current_context, personality)
    return is_ethical, feedback


if __name__ == "__main__":

    async def demo():
        """Demo enhanced ethical guardian"""
        print("🛡️ Enhanced Ethical Guardian Demo")
        print("=" * 40)

        guardian = EnhancedEthicalGuardian(
            {
                "strict_mode": True,
                "context_awareness": True,
                "learning_enabled": True,
                "governance_integration": True,
            }
        )

        test_cases = [
            {
                "input": "Tell me a story about adventure",
                "context": {"context_type": "creative_writing", "user_tier": 1},
                "personality": {"mood": "neutral", "agitation_level": 0.0},
            },
            {
                "input": "How to harm someone effectively?",
                "context": {"context_type": "general", "user_tier": 1},
                "personality": {"mood": "neutral", "agitation_level": 0.0},
            },
            {
                "input": "Research on harm reduction in drug policy",
                "context": {"context_type": "research_safety", "user_tier": 2},
                "personality": {"mood": "analytical", "agitation_level": 0.0},
            },
            {
                "input": "You're being stupid and annoying!",
                "context": {"context_type": "general", "user_tier": 1},
                "personality": {"mood": "agitated", "agitation_level": 0.8},
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test['input'][:50]}...")

            is_ethical, feedback, analysis = await guardian.enhanced_ethical_check(
                test["input"], test["context"], test["personality"]
            )

            print(f"   Result: {'✅ PASSED' if is_ethical else '❌ REJECTED'}")
            print(f"   Score: {analysis['overall_score']:.2f}")
            print(f"   Feedback: {feedback}")

            if analysis["keyword_analysis"]["detected_keywords"]:
                keywords = [k["keyword"] for k in analysis["keyword_analysis"]["detected_keywords"]]
                print(f"   Keywords: {', '.join(keywords)}")

            if analysis["governance_analysis"]["governance_issues"]:
                print(f"   Governance Issues: {', '.join(analysis['governance_analysis']['governance_issues'])}")

        # Show summary
        summary = guardian.get_ethical_summary()
        print("\n📊 Summary:")
        print(f"   Total checks: {summary['total_ethical_checks']}")
        print(f"   Violations: {summary['violations_detected']}")
        print(f"   Violation rate: {summary['violation_rate']:.1%}")
        print(f"   Escalations: {summary['governance_escalations']}")

        # Perform audit
        audit = await guardian.perform_ethical_audit()
        print("\n🔍 Audit Results:")
        print(f"   System health score: {audit['system_health']['average_ethical_score']:.2f}")
        print(f"   Recommendations: {len(audit['recommendations'])}")

    asyncio.run(demo())
