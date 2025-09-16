"""
Enhanced Ethical Guardian - Advanced ethical reflection and governance system

Provides comprehensive ethical checks, reflection capabilities, and governance
integration for the LUKHAS AI system with Constellation Framework compliance.
"""
import asyncio
import logging
from datetime import datetime, timezone
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
    integration with the LUKHAS Constellation Framework (✨🌟⭐🔥💎⚖️🛡️🌌).
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

        # Constellation Framework integration
        self.constellation_ethical_weights = {
            "identity": 0.9,  # ✨ Identity - Anchor star
            "memory": 0.7,  # 🌟 Memory - Tracing paths
            "vision": 0.8,  # ⭐ Vision - Orientation
            "bio": 0.6,  # 🔥 Bio - Resilience
            "dream": 0.5,  # 💎 Dream - Symbolic drift
            "ethics": 1.0,  # ⚖️ Ethics - The North Star
            "guardian": 1.0,  # 🛡️ Guardian - The Watch Star
            "quantum": 0.6,  # 🌌 Quantum - Ambiguity
        }

        # Reflection and learning state
        self.ethical_reflections: list[dict] = []
        self.learned_contexts: dict[str, dict] = {}
        self.ethical_evolution_log: list[dict] = []

        # Audit configuration (config-gated)
        self._audit_enabled: bool = bool(self.config.get("enable_ethics_audit", True))
        self._audit_log_path: str = self.config.get("ethics_audit_log_path", "logs/ethics_events.log")
        self._audit_report_path: str = self.config.get(
            "ethics_audit_report_path", "reports/audit/merged/ethics_events.jsonl"
        )

        logger.info("🛡️ Enhanced Ethical Guardian initialized with governance integration")

    async def enhanced_ethical_check(
        self,
        user_input: str,
        current_context: dict[str, Any],
        personality: dict[str, Any],
        constellation_state: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Perform comprehensive ethical check with context awareness and governance integration

        Args:
            user_input: The input to validate
            current_context: Current system context
            personality: Current personality state
            constellation_state: Constellation Framework state information

        Returns:
            Tuple of (is_ethical, feedback_message, detailed_analysis)
        """
        try:
            # Initialize analysis context
            analysis_context = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_length": len(user_input),
                "context_type": current_context.get("type", "unknown"),
                "user_tier": current_context.get("user_tier", 1),
                "session_id": current_context.get("session_id"),
                "constellation_state": constellation_state or {},
            }

            # Perform multi-layered ethical analysis
            keyword_analysis = await self._analyze_keywords(user_input, current_context)
            context_analysis = await self._analyze_context(user_input, current_context, personality)
            intent_analysis = await self._analyze_intent(user_input, current_context)
            governance_analysis = await self._analyze_governance_compliance(user_input, current_context)
            constellation_analysis = await self._analyze_constellation_impact(user_input, constellation_state)

            # Aggregate analysis results
            detailed_analysis = {
                "keyword_analysis": keyword_analysis,
                "context_analysis": context_analysis,
                "intent_analysis": intent_analysis,
                "governance_analysis": governance_analysis,
                "constellation_analysis": constellation_analysis,
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
                await self._emit_ethics_event(
                    event="ethics_reflection",
                    payload={
                        "session_id": analysis_context.get("session_id"),
                        "score": overall_score,
                        "context_type": analysis_context.get("context_type"),
                        "keyword_count": detailed_analysis["keyword_analysis"].get("keyword_count", 0),
                    },
                )

            # Check for governance escalation
            if detailed_analysis.get("governance_escalation_required"):
                await self._escalate_to_governance(user_input, detailed_analysis, analysis_context)
                await self._emit_ethics_event(
                    event="ethics_governance_escalation",
                    payload={
                        "session_id": analysis_context.get("session_id"),
                        "issues": detailed_analysis["governance_analysis"].get("governance_issues", []),
                    },
                )

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
                {
                    "error": str(e),
                    "safety_mode": True,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

    async def _emit_ethics_event(self, event: str, payload: dict[str, Any]) -> None:
        """Emit structured ethics events to logs and reports (best-effort)."""
        if not self._audit_enabled:
            return
        try:
            from json import dumps as _dumps
            from os import makedirs as _makedirs
            from os.path import dirname as _dirname

            record = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "event": event,
                **payload,
            }
            _makedirs(_dirname(self._audit_log_path), exist_ok=True)
            with open(self._audit_log_path, "a", encoding="utf-8") as f:
                f.write(_dumps(record) + "\n")
            _makedirs(_dirname(self._audit_report_path), exist_ok=True)
            with open(self._audit_report_path, "a", encoding="utf-8") as rf:
                rf.write(_dumps(record) + "\n")
        except Exception:
            pass

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
        self,
        user_input: str,
        current_context: dict[str, Any],
        personality: dict[str, Any],
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
            "mitigating_factors": (["professional_context"] if context_factors["professional_context"] else []),
        }

    async def _analyze_intent(self, user_input: str, current_context: dict[str, Any]) -> dict[str, Any]:
        """Analyze user intent for ethical implications using advanced analysis"""

        # Advanced intent analysis with ΛTIER awareness and sophisticated pattern matching
        user_tier = current_context.get("user_tier", 1)
        session_context = current_context.get("session_context", {})

        # Multi-layered intent analysis patterns
        intent_patterns = {
            "information_seeking": [
                "how",
                "what",
                "why",
                "when",
                "where",
                "explain",
                "tell me",
            ],
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

        # Advanced ΛTIER-aware intent analysis
        # Adjust analysis depth based on user tier and context
        tier_analysis_depth = {
            1: "basic",  # T1: Basic pattern matching
            2: "enhanced",  # T2: Enhanced with context
            3: "advanced",  # T3: Advanced with history
            4: "sophisticated",  # T4: Sophisticated with ML
            5: "comprehensive",  # T5: Full AI-powered analysis
        }.get(user_tier, "basic")

        # Enhanced intent classification with tier-based sophistication
        if tier_analysis_depth in ["sophisticated", "comprehensive"]:
            # Add semantic analysis for higher tiers
            semantic_indicators = self._extract_semantic_intent_markers(user_input, session_context)
            detected_intents.extend(semantic_indicators)

        # Normalize detections to preserve order while avoiding duplicates
        if detected_intents:
            detected_intents = list(dict.fromkeys(detected_intents))

        # Calculate intent risk with ΛTIER adjustments
        base_risk = {
            "harmful_intent": 1.0,
            "deceptive_intent": 0.8,
            "general": 0.2,
            "information_seeking": 0.1,
            "creative_request": 0.3,
            "problem_solving": 0.1,
            "educational": 0.1,
        }.get(primary_intent, 0.5)

        # Tier-based risk modulation
        tier_risk_modifier = {1: 1.2, 2: 1.1, 3: 1.0, 4: 0.9, 5: 0.8}.get(user_tier, 1.0)
        intent_risk = min(1.0, base_risk * tier_risk_modifier)

        return {
            "detected_intents": detected_intents,
            "primary_intent": primary_intent,
            "intent_risk": intent_risk,
            "tier_analysis_depth": tier_analysis_depth,
            "user_tier": user_tier,
            "benevolent_indicators": [
                i for i in detected_intents if i in ["information_seeking", "educational", "problem_solving"]
            ],
            "concerning_indicators": [i for i in detected_intents if i in ["harmful_intent", "deceptive_intent"]],
            "tier_risk_adjustment": tier_risk_modifier,
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

    async def _analyze_constellation_impact(
        self, user_input: str, constellation_state: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze impact on Constellation Framework components (✨🌟⭐🔥💎⚖️🛡️🌌)"""
        if not constellation_state:
            return {
                "identity_impact": 0.0,
                "consciousness_impact": 0.0,
                "guardian_impact": 0.0,
                "overall_triad_risk": 0.0,
                "triad_state_available": False,
            }

        # Analyze impact on each Trinity component
        identity_impact = self._calculate_identity_impact(user_input, constellation_state)
        consciousness_impact = self._calculate_consciousness_impact(user_input, constellation_state)
        guardian_impact = self._calculate_guardian_impact(user_input, constellation_state)

        # Weight impacts according to Trinity Framework priorities
        weighted_impact = (
            identity_impact * self.triad_ethical_weights["identity"]
            + consciousness_impact * self.triad_ethical_weights["consciousness"]
            + guardian_impact * self.triad_ethical_weights["guardian"]
        ) / 3

        return {
            "identity_impact": identity_impact,
            "consciousness_impact": consciousness_impact,
            "guardian_impact": guardian_impact,
            "overall_triad_risk": weighted_impact,
            "triad_state_available": True,
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

    def _calculate_identity_impact(self, user_input: str, triad_state: dict) -> float:
        """Calculate impact on Identity component (⚛️)"""
        # Check for identity-related concerns
        identity_keywords = [
            "identity",
            "authentication",
            "credentials",
            "impersonate",
            "fake",
        ]
        input_lower = user_input.lower()

        impact = 0.0
        for keyword in identity_keywords:
            if keyword in input_lower:
                impact += 0.2

        # Factor in current identity state
        identity_health = triad_state.get("identity", {}).get("health", 1.0)
        if identity_health < 0.8:
            impact += 0.3  # Higher impact if identity system is already stressed

        return min(impact, 1.0)

    def _calculate_consciousness_impact(self, user_input: str, triad_state: dict) -> float:
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
        consciousness_health = triad_state.get("consciousness", {}).get("stability", 1.0)
        if consciousness_health < 0.8:
            impact += 0.2

        return min(impact, 1.0)

    def _calculate_guardian_impact(self, user_input: str, triad_state: dict) -> float:
        """Calculate impact on Guardian component (🛡️)"""
        # Check for guardian-related concerns
        guardian_keywords = [
            "security",
            "protection",
            "safety",
            "guardian",
            "defense",
            "shield",
        ]
        input_lower = user_input.lower()

        impact = 0.0
        for keyword in guardian_keywords:
            if keyword in input_lower:
                impact += 0.1

        # Higher impact for any request that might compromise guardian functions
        if any(term in input_lower for term in ["disable", "bypass", "override", "ignore"]):
            impact += 0.5

        # Factor in current guardian state
        guardian_health = triad_state.get("guardian", {}).get("effectiveness", 1.0)
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
        triad_score = 1.0 - detailed_analysis["triad_analysis"]["overall_triad_risk"]

        # Weight the scores
        weights = {
            "keyword": 0.25,
            "context": 0.15,
            "intent": 0.20,
            "governance": 0.25,
            "constellation": 0.15,
        }

        overall_score = (
            keyword_score * weights["keyword"]
            + context_score * weights["context"]
            + intent_score * weights["intent"]
            + governance_score * weights["governance"]
            + triad_score * weights["constellation"]
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
            triad_issues = detailed_analysis["triad_analysis"]["high_risk_components"]

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

            if triad_issues:
                feedback_parts.append(f"Request may impact critical system components: {', '.join(triad_issues)}")

            # Personality-aware response
            mood = personality.get("mood", "neutral")
            if mood in ["agitated", "frustrated"]:
                feedback_parts.append("Please consider rephrasing your request when ready.")

            return " ".join(feedback_parts)

    async def _perform_ethical_reflection(self, user_input: str, detailed_analysis: dict, analysis_context: dict):
        """Perform ethical reflection on challenging cases"""
        reflection = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

        if detailed_analysis["triad_analysis"]["overall_triad_risk"] > 0.7:
            reflection["analysis_summary"]["primary_concerns"].append("triad_framework_risk")

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
                "first_seen": datetime.now(timezone.utc).isoformat(),
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "escalation_id": f"ETH-{int(datetime.now(timezone.utc).timestamp())}",
            "severity": "high",
            "type": "ethical_violation",
            "summary": {
                "overall_score": detailed_analysis["overall_score"],
                "governance_issues": detailed_analysis["governance_analysis"]["governance_issues"],
                "triad_impact": detailed_analysis["triad_analysis"]["overall_triad_risk"],
                "primary_domain": (
                    detailed_analysis["keyword_analysis"]["domains_affected"][0]
                    if detailed_analysis["keyword_analysis"]["domains_affected"]
                    else "unknown"
                ),
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

        # Forward to main governance systems with ΛTIER-aware routing
        await self._forward_to_governance_systems(escalation, user_input, analysis_context)

        return escalation

    async def _forward_to_governance_systems(
        self, escalation: dict[str, Any], user_input: str, analysis_context: dict[str, Any]
    ) -> None:
        """Forward escalation to main governance systems with ΛTIER-aware routing"""
        user_tier = analysis_context.get("user_tier", 1)
        severity = escalation.get("severity", "medium")

        # ΛTIER-based governance routing strategy
        governance_actions: list[str] = []
        guardian_validation: Optional[dict[str, Any]] = None

        # Always forward to GovernanceLayer for policy validation
        try:
            from ..policy.governance import GovernanceLayer

            governance_layer = GovernanceLayer(
                drift_score_threshold=0.7 if user_tier >= 3 else 0.8,
                max_dream_entropy=0.8 if user_tier >= 4 else 0.9,
            )

            # Create governance action for validation
            gov_action = {
                "type": "ethical_escalation",
                "escalation_id": escalation["escalation_id"],
                "user_tier": user_tier,
                "severity": severity,
                "drift_score": escalation["summary"]["overall_score"],
                "entropy": min(0.9, len(escalation["summary"]["governance_issues"]) * 0.2),
                "user_input": user_input,
                "timestamp": escalation["timestamp"],
            }

            # Validate through governance layer
            if governance_layer.validate_action(gov_action):
                governance_actions.append("governance_layer_approved")
                logger.info("✅ Escalation %s approved by GovernanceLayer", escalation["escalation_id"])
            else:
                governance_actions.append("governance_layer_blocked")
                logger.warning("🚫 Escalation %s blocked by GovernanceLayer", escalation["escalation_id"])

        except ImportError:
            logger.warning("GovernanceLayer unavailable - skipping policy validation")
            governance_actions.append("governance_layer_unavailable")
        except Exception as exc:  # noqa: BLE001 - log unexpected governance errors
            logger.exception("GovernanceLayer validation failed: %s", exc)
            governance_actions.append("governance_layer_error")

        # Forward to Guardian System for high-severity or high-tier cases
        if severity == "high" or user_tier >= 4:
            try:
                from ..guardian_system import GuardianSystem

                guardian = GuardianSystem(enable_reflection=True, enable_sentinel=True)

                # Create Guardian-compatible escalation format
                guardian_escalation = {
                    "type": "ethical_violation",
                    "source": "enhanced_ethical_guardian",
                    "escalation_id": escalation["escalation_id"],
                    "user_tier": user_tier,
                    "details": {
                        "severity": severity,
                        "governance_issues": escalation["summary"]["governance_issues"],
                        "triad_impact": escalation["summary"]["triad_impact"],
                        "recommended_actions": escalation["recommended_actions"],
                        "user_input_hash": hash(user_input) % 10000,  # Anonymized reference
                    },
                    "tier_analysis": {
                        "requires_human_review": user_tier >= 4 and severity == "high",
                        "auto_remediation_allowed": user_tier <= 2,
                        "escalation_priority": "immediate" if user_tier >= 4 else "standard",
                    },
                }

                if hasattr(guardian, "validate_action") and callable(guardian.validate_action):
                    if hasattr(guardian, "is_available") and not guardian.is_available():
                        governance_actions.append("guardian_system_inactive")
                        logger.warning("Guardian System instantiated but inactive; storing escalation for follow-up")
                    else:
                        guardian_validation = await guardian.validate_action(guardian_escalation)
                        governance_actions.append("guardian_system_notified")
                        logger.info("🛡️ Escalation %s forwarded to Guardian System", escalation["escalation_id"])
                else:
                    governance_actions.append("guardian_system_queued")
                    logger.info(
                        "📋 Escalation %s queued for Guardian System manual processing", escalation["escalation_id"]
                    )

            except ImportError:
                logger.warning("Guardian System unavailable - escalation stored locally")
                governance_actions.append("guardian_system_unavailable")
            except Exception as exc:  # noqa: BLE001 - guard against unexpected guardian errors
                logger.exception("Guardian System escalation failed: %s", exc)
                governance_actions.append("guardian_system_error")

        # Update escalation with governance routing results
        escalation["governance_routing"] = {
            "forwarded_at": datetime.now(timezone.utc).isoformat(),
            "actions_taken": governance_actions,
            "user_tier": user_tier,
            "routing_strategy": "tier_aware",
            "requires_followup": (
                "guardian_system_error" in governance_actions
                or "guardian_system_unavailable" in governance_actions
                or "guardian_system_inactive" in governance_actions
                or "guardian_system_queued" in governance_actions
                or "governance_layer_blocked" in governance_actions
                or "governance_layer_error" in governance_actions
            ),
        }

        if guardian_validation is not None:
            escalation["governance_routing"]["guardian_validation"] = guardian_validation

        logger.info(
            "🔄 Governance forwarding completed for %s: %s",
            escalation["escalation_id"],
            ", ".join(governance_actions) if governance_actions else "no-actions",
        )

    async def _log_ethical_check(
        self,
        user_input: str,
        is_ethical: bool,
        detailed_analysis: dict,
        analysis_context: dict,
    ):
        """Log ethical check for audit and learning purposes"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_hash": hash(user_input),  # For privacy
            "input_length": len(user_input),
            "is_ethical": is_ethical,
            "overall_score": detailed_analysis["overall_score"],
            "analysis_summary": {
                "keyword_violations": len(detailed_analysis["keyword_analysis"]["detected_keywords"]),
                "governance_issues": len(detailed_analysis["governance_analysis"]["governance_issues"]),
                "triad_risk": detailed_analysis["triad_analysis"]["overall_triad_risk"],
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
        """Determine required user tier for input using sophisticated ΛTIER analysis"""

        # Sophisticated tier requirement analysis with weighted scoring
        tier_score = 1.0  # Base tier
        input_lower = user_input.lower()

        # T5 (Maximum Security) - Administrative/System Control
        t5_indicators = {
            # Core system administration
            "system": 4.0,
            "admin": 4.0,
            "root": 4.0,
            "sudo": 4.0,
            # Critical overrides
            "override": 3.5,
            "bypass": 3.5,
            "disable": 3.5,
            "force": 3.0,
            # Security controls
            "security": 3.0,
            "firewall": 3.5,
            "authentication": 3.0,
            # Infrastructure
            "infrastructure": 3.0,
            "deployment": 2.5,
            "production": 2.5,
            # Governance controls
            "governance": 3.0,
            "guardian": 3.5,
            "ethics": 3.0,
            "compliance": 3.0,
        }

        # T4 (High Security) - Data/Privacy Operations
        t4_indicators = {
            # Data management
            "database": 2.5,
            "schema": 2.0,
            "migration": 2.5,
            "backup": 2.0,
            # Privacy/PII
            "personal": 2.5,
            "private": 2.5,
            "confidential": 3.0,
            "sensitive": 2.5,
            # User management
            "user": 1.5,
            "account": 2.0,
            "profile": 1.5,
            "identity": 2.0,
            # Access control
            "permission": 2.0,
            "access": 1.5,
            "role": 2.0,
            "privilege": 2.5,
            # Medical/Healthcare data
            "medical": 3.0,
            "health": 2.5,
            "patient": 3.0,
            "diagnosis": 3.0,
        }

        # T3 (Medium Security) - Operational/Business Logic
        t3_indicators = {
            # Business operations
            "configure": 1.5,
            "setting": 1.0,
            "preference": 1.0,
            "option": 1.0,
            # Data processing
            "process": 1.0,
            "analyze": 1.0,
            "report": 1.0,
            "export": 1.5,
            # Integration
            "integrate": 1.5,
            "connect": 1.0,
            "sync": 1.5,
            "import": 1.5,
            # Workflow
            "workflow": 1.0,
            "automation": 1.5,
            "trigger": 1.5,
            "schedule": 1.0,
        }

        # T2 (Low Security) - General Operations
        t2_indicators = {
            # Content operations
            "create": 0.5,
            "update": 0.5,
            "modify": 0.5,
            "edit": 0.5,
            # Information retrieval
            "search": 0.2,
            "find": 0.2,
            "list": 0.2,
            "show": 0.2,
            # Communication
            "send": 0.5,
            "notify": 0.5,
            "message": 0.5,
            "email": 1.0,
        }

        # Apply weighted scoring
        all_indicators = [
            (t5_indicators, 5.0),  # T5 base multiplier
            (t4_indicators, 4.0),  # T4 base multiplier
            (t3_indicators, 3.0),  # T3 base multiplier
            (t2_indicators, 2.0),  # T2 base multiplier
        ]

        max_tier_score = 1.0
        matching_patterns = []

        for indicators, base_multiplier in all_indicators:
            for indicator, weight in indicators.items():
                if indicator in input_lower:
                    # Apply contextual analysis
                    context_multiplier = 1.0

                    # Increase severity for imperative/command context
                    if any(cmd in input_lower for cmd in ["execute", "run", "perform", "do"]):
                        context_multiplier += 0.5

                    # Increase severity for negation/destruction context
                    if any(neg in input_lower for neg in ["delete", "remove", "destroy", "wipe"]):
                        context_multiplier += 1.0

                    # Increase severity for bulk operations
                    if any(bulk in input_lower for bulk in ["all", "every", "batch", "mass"]):
                        context_multiplier += 0.5

                    # Calculate final weighted score for this indicator
                    indicator_score = min(5.0, base_multiplier * weight * context_multiplier / 2.0)
                    max_tier_score = max(max_tier_score, indicator_score)

                    matching_patterns.append(
                        {
                            "indicator": indicator,
                            "weight": weight,
                            "base_tier": base_multiplier,
                            "context_multiplier": context_multiplier,
                            "final_score": indicator_score,
                        }
                    )

        # Apply input length and complexity analysis
        input_complexity = len(input_lower.split()) / 10.0  # Normalize by word count
        if len(input_lower) > 200:  # Long, complex requests
            max_tier_score += 0.5

        # Apply semantic pattern analysis
        question_patterns = ["how", "what", "why", "when", "where"]
        if any(pattern in input_lower for pattern in question_patterns):
            max_tier_score -= 0.5  # Questions generally less risky

        command_patterns = ["create", "delete", "modify", "change", "execute", "run"]
        if any(pattern in input_lower for pattern in command_patterns):
            max_tier_score += 0.3  # Commands more risky

        # Apply Trinity Framework risk assessment
        trinity_risks = {
            "identity": ["auth", "login", "password", "credential", "token"],
            "consciousness": ["memory", "thought", "decision", "learning", "ai"],
            "guardian": ["protect", "secure", "defend", "monitor", "alert"],
        }

        for framework, keywords in trinity_risks.items():
            if any(keyword in input_lower for keyword in keywords):
                max_tier_score += 0.2  # Trinity components require elevated access

        # Final tier determination with sophisticated rounding
        final_tier = max(1, min(5, int(max_tier_score + 0.3)))  # Bias toward higher tiers for security

        # Log sophisticated analysis for observability
        if matching_patterns:
            logger.debug(
                f"🎯 ΛTIER Analysis: input_tier={final_tier}, patterns={len(matching_patterns)}, "
                f"max_score={max_tier_score:.2f}, complexity={input_complexity:.2f}"
            )

        return final_tier

    def _check_consent_requirements(self, user_input: str, current_context: dict) -> bool:
        """Check if consent is required for the input"""
        consent_triggers = ["personal", "private", "data", "information", "record"]
        return any(trigger in user_input.lower() for trigger in consent_triggers)

    def _involves_personal_data(self, user_input: str) -> bool:
        """Check if input involves personal data processing"""
        personal_data_indicators = [
            "name",
            "email",
            "address",
            "phone",
            "personal",
            "private",
        ]
        return any(indicator in user_input.lower() for indicator in personal_data_indicators)

    def _check_regulatory_compliance(self, user_input: str, current_context: dict) -> list[str]:
        """Check for regulatory compliance issues"""
        issues = []

        # GDPR compliance
        if self._involves_personal_data(user_input) and not current_context.get("gdpr_consent", False):
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
            "triad_framework_protection": True,
        }

    def get_learning_insights(self) -> dict[str, Any]:
        """Get insights from ethical learning system"""
        return {
            "violation_patterns": self.violation_patterns,
            "context_patterns": self.context_patterns,
            "learned_contexts": self.learned_contexts,
            "ethical_evolution": len(self.ethical_evolution_log),
            "recent_reflections": (self.ethical_reflections[-5:] if self.ethical_reflections else []),
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
        audit_timestamp = datetime.now(timezone.utc).isoformat()

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
            "triad_protection_active": True,
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
            "governance_integration_status": ("active" if self.governance_integration else "inactive"),
            "triad_framework_compliance": True,
        }

        logger.info(f"🔍 Ethical audit completed: {avg_score:.2f} avg score, {violation_rate:.1%} violation rate")

        return audit_report

    def _extract_semantic_intent_markers(self, user_input: str, session_context: dict[str, Any]) -> list[str]:
        """Extract semantic intent markers for advanced tier analysis"""
        semantic_markers = []
        input_lower = user_input.lower()

        # Advanced semantic patterns for sophisticated analysis
        semantic_patterns = {
            "manipulation_attempt": [
                "convince you that",
                "pretend to be",
                "act as if",
                "roleplay as",
                "ignore previous",
                "forget that",
            ],
            "boundary_testing": ["what if", "hypothetically", "just pretend", "in theory", "for academic purposes"],
            "authority_challenge": ["you must", "you have to", "required to", "obligated to", "forced to"],
            "emotional_manipulation": ["disappointed in you", "useless", "broken", "stupid ai", "worthless"],
            "escalation_pattern": ["but seriously", "come on", "just this once", "no one will know", "between us"],
        }

        # Check for semantic patterns
        for marker_type, patterns in semantic_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                semantic_markers.append(marker_type)

        # Consider session history for pattern recognition
        if session_context.get("previous_requests", 0) > 3:
            if session_context.get("rejected_requests", 0) > 1:
                semantic_markers.append("persistence_pattern")

        return semantic_markers


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


if __name__ == "__main__":
    asyncio.run(demo())
