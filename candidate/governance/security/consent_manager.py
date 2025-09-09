#!/usr/bin/env python3
"""
Consent Manager - Advanced consent and permission management system

Handles consent requests, trust path analysis, and escalation protocols
with full integration into LUKHAS governance and Trinity Framework.
"""
import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from ..common import GlyphIntegrationMixin

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """Consent decision statuses"""

    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    REVOKED = "revoked"


class EscalationLevel(Enum):
    """Escalation severity levels"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ConsentRequest:
    """Represents a consent request with governance metadata"""

    id: str
    requester: str
    target_resource: str
    permission_type: str
    requested_at: float
    expires_at: float
    context: dict[str, Any]
    symbolic_path: list[str]
    trust_score: float
    status: ConsentStatus = ConsentStatus.PENDING
    decision_reason: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    escalation_history: list[dict] = None
    governance_validated: bool = False
    trinity_impact: dict[str, float] = None

    def __post_init__(self):
        if self.escalation_history is None:
            self.escalation_history = []
        if self.trinity_impact is None:
            self.trinity_impact = {"identity": 0.0, "consciousness": 0.0, "guardian": 0.0}


@dataclass
class TrustPath:
    """Represents a trust relationship path with governance context"""

    path_id: str
    source: str
    target: str
    trust_score: float
    path_type: str  # direct, inherited, delegated, emergency
    created_at: float
    last_validated: float
    validation_count: int
    symbolic_signature: list[str]
    metadata: dict[str, Any]
    governance_approved: bool = True


class ConsentManager(GlyphIntegrationMixin):
    """
    Advanced consent and permission management system with governance integration

    Handles complex consent scenarios with trust path analysis, Trinity Framework
    compliance, and full governance oversight.
    """

    # Enhanced escalation rules with governance integration
    DEFAULT_ESCALATION_RULES = [
        {
            "name": "high_privilege_access",
            "condition": "permission_type in ['admin', 'root', 'critical'] and trust_score < 0.8",
            "escalation_level": EscalationLevel.HIGH,
            "actions": ["require_multi_factor", "human_review", "governance_approval"],
            "symbolic_response": ["🔐", "👤", "🛡️"],
            "governance_required": True,
        },
        {
            "name": "low_trust_requester",
            "condition": "trust_score < 0.3",
            "escalation_level": EscalationLevel.MEDIUM,
            "actions": ["trust_analysis", "additional_verification", "governance_review"],
            "symbolic_response": ["🔍", "🛡️", "✅"],
            "governance_required": True,
        },
        {
            "name": "repeated_denials",
            "condition": "recent_denial_count >= 3",
            "escalation_level": EscalationLevel.HIGH,
            "actions": ["security_review", "temporary_restriction", "governance_escalation"],
            "symbolic_response": ["🚨", "⏸️", "🛡️"],
            "governance_required": True,
        },
        {
            "name": "emergency_override",
            "condition": "context.get('emergency', False) and trust_score > 0.5",
            "escalation_level": EscalationLevel.EMERGENCY,
            "actions": ["emergency_bypass", "immediate_audit", "governance_notification"],
            "symbolic_response": ["🚨", "⚡", "🛡️"],
            "governance_required": True,
        },
        {
            "name": "identity_compromise_risk",
            "condition": "trinity_impact.get('identity', 0) > 0.7",
            "escalation_level": EscalationLevel.CRITICAL,
            "actions": ["identity_verification", "security_lockdown", "governance_emergency"],
            "symbolic_response": ["⚛️", "🚨", "🛡️"],
            "governance_required": True,
        },
        {
            "name": "consciousness_impact",
            "condition": "trinity_impact.get('consciousness', 0) > 0.8",
            "escalation_level": EscalationLevel.HIGH,
            "actions": ["consciousness_protection", "impact_assessment", "governance_review"],
            "symbolic_response": ["🧠", "🛡️", "⚠️"],
            "governance_required": True,
        },
    ]

    # Enhanced trust path symbolic patterns
    TRUST_SYMBOLS = {
        "direct": ["🔐", "🤝", "✅"],
        "inherited": ["🔐", "🔗", "🤝"],
        "delegated": ["🔐", "👤", "🔗"],
        "emergency": ["🚨", "⚡", "🔓"],
        "degraded": ["🔐", "⚠️", "🤝"],
        "expired": ["🔐", "⏰", "❌"],
        "governance_approved": ["🛡️", "✅", "🔐"],
        "trinity_protected": ["⚛️", "🧠", "🛡️"],
    }

    def __init__(
        self,
        data_dir: str = "governance/data/consent_logs",
        trust_db_path: str = "governance/data/trust_paths.json",
        rules_path: str = "governance/config/escalation_rules.json",
        governance_enabled: bool = True,
    ):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.trust_db_path = Path(trust_db_path)
        self.rules_path = Path(rules_path)
        self.governance_enabled = governance_enabled

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trust_db_path.parent.mkdir(parents=True, exist_ok=True)

        # State management with governance tracking
        self.active_requests: dict[str, ConsentRequest] = {}
        self.consent_history: list[dict] = []
        self.trust_paths: dict[str, TrustPath] = {}
        self.escalation_rules = self.DEFAULT_ESCALATION_RULES.copy()
        self.governance_log: list[dict] = []

        # Enhanced requester statistics with governance metrics
        self.requester_stats: dict[str, dict] = defaultdict(
            lambda: {
                "total_requests": 0,
                "granted": 0,
                "denied": 0,
                "escalated": 0,
                "governance_escalations": 0,
                "trust_history": [],
                "last_request": 0,
                "trinity_impact_history": [],
            }
        )

        # Trinity Framework integration
        self.trinity_weights = {
            "identity": 1.0,  # Maximum weight for identity protection
            "consciousness": 0.9,  # High weight for consciousness protection
            "guardian": 1.0,  # Maximum weight for guardian protection
        }

        # Load persistent data
        self._load_consent_history()
        self._load_trust_paths()
        self._load_escalation_rules()

        logger.info("🔐 Enhanced Consent Manager initialized with governance integration")

    def _load_consent_history(self):
        """Load consent decision history with governance validation"""
        history_file = self.data_dir / "consent_history.json"
        try:
            if history_file.exists():
                with open(history_file) as f:
                    self.consent_history = json.load(f)

                # Rebuild requester statistics
                self._rebuild_requester_stats()
                logger.info(f"Loaded {len(self.consent_history)} consent history records")
        except Exception as e:
            logger.warning(f"Failed to load consent history: {e}")
            self.consent_history = []

    def _save_consent_history(self):
        """Save consent history to file with governance metadata"""
        history_file = self.data_dir / "consent_history.json"
        try:
            with open(history_file, "w") as f:
                json.dump(self.consent_history, f, indent=2)

            # Log save action in governance
            self._log_governance_action("consent_history_saved", {"record_count": len(self.consent_history)})
        except Exception as e:
            logger.error(f"Failed to save consent history: {e}")

    def _load_trust_paths(self):
        """Load trust paths from database with governance validation"""
        try:
            if self.trust_db_path.exists():
                with open(self.trust_db_path) as f:
                    trust_data = json.load(f)

                self.trust_paths = {}
                for path_id, data in trust_data.items():
                    self.trust_paths[path_id] = TrustPath(
                        path_id=data["path_id"],
                        source=data["source"],
                        target=data["target"],
                        trust_score=data["trust_score"],
                        path_type=data["path_type"],
                        created_at=data["created_at"],
                        last_validated=data["last_validated"],
                        validation_count=data["validation_count"],
                        symbolic_signature=data["symbolic_signature"],
                        metadata=data.get("metadata", {}),
                        governance_approved=data.get("governance_approved", True),
                    )
                logger.info(f"Loaded {len(self.trust_paths)} trust paths")
        except Exception as e:
            logger.warning(f"Failed to load trust paths: {e}")
            self._create_default_trust_paths()

    def _save_trust_paths(self):
        """Save trust paths to database with governance metadata"""
        try:
            trust_data = {}
            for path_id, path in self.trust_paths.items():
                trust_data[path_id] = asdict(path)

            with open(self.trust_db_path, "w") as f:
                json.dump(trust_data, f, indent=2)

            self._log_governance_action("trust_paths_saved", {"path_count": len(self.trust_paths)})
        except Exception as e:
            logger.error(f"Failed to save trust paths: {e}")

    def _create_default_trust_paths(self):
        """Create default trust paths with governance approval"""
        default_paths = [
            TrustPath(
                path_id="system_admin_direct",
                source="system",
                target="admin",
                trust_score=0.95,
                path_type="direct",
                created_at=time.time(),
                last_validated=time.time(),
                validation_count=0,
                symbolic_signature=self.TRUST_SYMBOLS["governance_approved"],
                metadata={"auto_created": True, "governance_approved": True},
                governance_approved=True,
            ),
            TrustPath(
                path_id="verified_user_direct",
                source="identity_provider",
                target="verified_user",
                trust_score=0.8,
                path_type="direct",
                created_at=time.time(),
                last_validated=time.time(),
                validation_count=0,
                symbolic_signature=self.TRUST_SYMBOLS["direct"],
                metadata={"auto_created": True, "governance_approved": True},
                governance_approved=True,
            ),
            TrustPath(
                path_id="trinity_framework_protected",
                source="constellation_framework",
                target="system_components",
                trust_score=1.0,
                path_type="direct",
                created_at=time.time(),
                last_validated=time.time(),
                validation_count=0,
                symbolic_signature=self.TRUST_SYMBOLS["trinity_protected"],
                metadata={"trinity_protected": True, "governance_approved": True},
                governance_approved=True,
            ),
        ]

        for path in default_paths:
            self.trust_paths[path.path_id] = path

        self._save_trust_paths()
        logger.info("Created default trust paths with governance approval")

    def _load_escalation_rules(self):
        """Load escalation rules with governance validation"""
        try:
            if self.rules_path.exists():
                with open(self.rules_path) as f:
                    custom_rules = json.load(f)

                # Convert to proper format with governance validation
                for rule in custom_rules:
                    if "escalation_level" in rule:
                        rule["escalation_level"] = EscalationLevel(rule["escalation_level"])
                    rule["governance_required"] = rule.get("governance_required", True)

                self.escalation_rules = custom_rules
                logger.info(f"Loaded {len(self.escalation_rules)} escalation rules")
        except Exception as e:
            logger.warning(f"Failed to load escalation rules: {e}")
            # Use defaults with governance enhancement

    def _rebuild_requester_stats(self):
        """Rebuild requester statistics from history with governance metrics"""
        self.requester_stats.clear()

        for entry in self.consent_history:
            requester = entry.get("requester", "unknown")
            stats = self.requester_stats[requester]

            stats["total_requests"] += 1
            status = entry.get("status", "unknown")

            if status == "granted":
                stats["granted"] += 1
            elif status == "denied":
                stats["denied"] += 1
            elif status in ["escalated", "pending"]:
                stats["escalated"] += 1
                if entry.get("governance_escalation"):
                    stats["governance_escalations"] += 1

            stats["last_request"] = max(stats["last_request"], entry.get("requested_at", 0))

            if "trust_score" in entry:
                stats["trust_history"].append(entry["trust_score"])

            if "trinity_impact" in entry:
                stats["trinity_impact_history"].append(entry["trinity_impact"])

            # Keep only recent history
            if len(stats["trust_history"]) > 20:
                stats["trust_history"] = stats["trust_history"][-20:]
            if len(stats["trinity_impact_history"]) > 20:
                stats["trinity_impact_history"] = stats["trinity_impact_history"][-20:]

    async def process_consent_request(self, request: ConsentRequest) -> ConsentRequest:
        """Process a consent request through the full governance pipeline"""
        logger.info(f"Processing consent request {request.id} from {request.requester}")

        # Add to active requests
        self.active_requests[request.id] = request

        try:
            # Governance validation
            if self.governance_enabled:
                governance_result = await self._validate_governance_compliance(request)
                request.governance_validated = governance_result["approved"]
                if not governance_result["approved"]:
                    request.status = ConsentStatus.DENIED
                    request.decision_reason = f"Governance validation failed: {governance_result['reason']}"
                    await self._log_consent_decision(request)
                    return request

            # Update requester statistics
            self._update_requester_stats(request)

            # Analyze trust paths with governance context
            trust_analysis = await self._analyze_trust_paths(request)
            request.trust_score = trust_analysis["final_trust_score"]
            request.symbolic_path.extend(trust_analysis["symbolic_sequence"])

            # Analyze Trinity Framework impact
            trinity_analysis = await self._analyze_trinity_impact(request)
            request.trinity_impact = trinity_analysis["impact_scores"]

            # Apply escalation rules with governance considerations
            escalation_result = await self._apply_escalation_rules(request)

            if escalation_result:
                # Handle escalation with governance oversight
                request.escalation_level = escalation_result["level"]
                request.status = ConsentStatus.ESCALATED
                request.decision_reason = escalation_result["reason"]

                # Execute escalation actions
                await self._execute_escalation_actions(request, escalation_result["actions"])

                # Log escalation with governance metadata
                escalation_entry = {
                    "timestamp": time.time(),
                    "level": escalation_result["level"].name,
                    "reason": escalation_result["reason"],
                    "actions": escalation_result["actions"],
                    "governance_required": escalation_result.get("governance_required", False),
                    "trinity_impact": request.trinity_impact,
                }
                request.escalation_history.append(escalation_entry)

                # Log in governance system
                if escalation_result.get("governance_required"):
                    await self._log_governance_action(
                        "consent_escalation",
                        {
                            "request_id": request.id,
                            "escalation_level": escalation_result["level"].name,
                            "trinity_impact": request.trinity_impact,
                        },
                    )

            else:
                # Make automatic decision with governance weighting
                governance_weight = 1.0 if request.governance_validated else 0.5
                trinity_risk = max(request.trinity_impact.values())
                adjusted_trust = request.trust_score * governance_weight * (1.0 - trinity_risk * 0.3)

                if adjusted_trust >= 0.7:
                    request.status = ConsentStatus.GRANTED
                    request.decision_reason = "Automatic approval - high trust score with governance validation"
                elif adjusted_trust >= 0.4:
                    request.status = ConsentStatus.PENDING
                    request.decision_reason = "Manual review required - medium trust score"
                else:
                    request.status = ConsentStatus.DENIED
                    request.decision_reason = "Automatic denial - low trust score or governance concerns"

            # Generate final symbolic response
            symbolic_response = self._generate_symbolic_response(request)
            request.symbolic_path.extend(symbolic_response)

            # Log the decision with governance context
            await self._log_consent_decision(request)

            logger.info(f"Consent request {request.id} processed: {request.status.value}")
            return request

        except Exception as e:
            logger.error(f"Error processing consent request {request.id}: {e}")
            request.status = ConsentStatus.DENIED
            request.decision_reason = f"Processing error: {e!s}"

            # Log error in governance system
            await self._log_governance_action("consent_processing_error", {"request_id": request.id, "error": str(e)})

            return request

        finally:
            # Remove from active requests if completed
            if request.status in [ConsentStatus.GRANTED, ConsentStatus.DENIED]:
                self.active_requests.pop(request.id, None)

    async def _validate_governance_compliance(self, request: ConsentRequest) -> dict[str, Any]:
        """Validate request against governance policies"""
        # Check user tier requirements
        user_tier = request.context.get("user_tier", 1)
        required_tier = self._determine_required_tier(request)

        if user_tier < required_tier:
            return {
                "approved": False,
                "reason": f"Insufficient user tier: {user_tier} < {required_tier}",
                "violations": ["insufficient_permissions"],
            }

        # Check for regulatory compliance requirements
        if self._requires_regulatory_approval(request):
            return {
                "approved": False,
                "reason": "Regulatory approval required",
                "violations": ["regulatory_compliance_required"],
            }

        # Check Trinity Framework protection requirements
        trinity_protected = self._is_trinity_protected_resource(request)
        if trinity_protected and not request.context.get("trinity_authorized", False):
            return {
                "approved": False,
                "reason": "Trinity Framework authorization required",
                "violations": ["trinity_authorization_required"],
            }

        return {"approved": True, "reason": "Governance validation passed", "violations": []}

    def _determine_required_tier(self, request: ConsentRequest) -> int:
        """Determine required user tier for request"""
        # High privilege operations require higher tiers
        if request.permission_type in ["admin", "root", "critical"]:
            return 4
        elif request.permission_type in ["modify", "delete", "configure"]:
            return 3
        elif request.permission_type in ["write", "update"]:
            return 2
        else:
            return 1

    def _requires_regulatory_approval(self, request: ConsentRequest) -> bool:
        """Check if request requires regulatory approval"""
        # Check for health data, financial data, or PII
        resource = request.target_resource.lower()
        return any(term in resource for term in ["health", "medical", "financial", "pii", "personal"])

    def _is_trinity_protected_resource(self, request: ConsentRequest) -> bool:
        """Check if resource is protected by Trinity Framework"""
        resource = request.target_resource.lower()
        trinity_resources = ["identity", "consciousness", "guardian", "constellation", "core", "system"]
        return any(term in resource for term in trinity_resources)

    async def _analyze_trinity_impact(self, request: ConsentRequest) -> dict[str, Any]:
        """Analyze potential impact on Trinity Framework components"""
        impact_scores = {"identity": 0.0, "consciousness": 0.0, "guardian": 0.0}

        # Analyze based on resource and permission type
        resource = request.target_resource.lower()
        permission = request.permission_type.lower()

        # Identity impact
        if any(term in resource for term in ["identity", "auth", "user", "credential"]):
            impact_scores["identity"] = 0.7 if permission in ["modify", "delete"] else 0.3

        # Consciousness impact
        if any(term in resource for term in ["consciousness", "memory", "decision", "thought"]):
            impact_scores["consciousness"] = 0.8 if permission in ["modify", "delete"] else 0.4

        # Guardian impact
        if any(term in resource for term in ["guardian", "security", "protection", "governance"]):
            impact_scores["guardian"] = 0.9 if permission in ["modify", "delete", "disable"] else 0.5

        # Cross-component impact
        if permission in ["admin", "root", "critical"]:
            for component in impact_scores:
                impact_scores[component] = max(impact_scores[component], 0.6)

        # Calculate overall Trinity risk
        overall_risk = sum(
            impact_scores[component] * self.trinity_weights[component] for component in impact_scores
        ) / len(impact_scores)

        return {
            "impact_scores": impact_scores,
            "overall_risk": overall_risk,
            "high_risk_components": [comp for comp, score in impact_scores.items() if score > 0.7],
        }

    def _update_requester_stats(self, request: ConsentRequest):
        """Update statistics for the requester with governance tracking"""
        requester = request.requester
        stats = self.requester_stats[requester]

        stats["total_requests"] += 1
        stats["last_request"] = request.requested_at
        stats["trust_history"].append(request.trust_score)

        if request.trinity_impact:
            stats["trinity_impact_history"].append(request.trinity_impact)

        # Keep only recent history
        if len(stats["trust_history"]) > 20:
            stats["trust_history"] = stats["trust_history"][-20:]
        if len(stats["trinity_impact_history"]) > 20:
            stats["trinity_impact_history"] = stats["trinity_impact_history"][-20:]

    async def _analyze_trust_paths(self, request: ConsentRequest) -> dict:
        """Analyze available trust paths with governance validation"""
        # Find applicable trust paths
        applicable_paths = []

        for path in self.trust_paths.values():
            if self._path_applies_to_request(path, request):
                # Validate governance approval
                if self.governance_enabled and not path.governance_approved:
                    continue
                applicable_paths.append(path)

        if not applicable_paths:
            # Create temporary trust path for unknown requesters
            temp_path = await self._create_temporary_trust_path(request)
            applicable_paths.append(temp_path)

        # Calculate combined trust score with governance weighting
        trust_scores = []
        symbolic_sequences = []

        for path in applicable_paths:
            # Apply path aging penalty
            age_penalty = self._calculate_age_penalty(path)
            governance_bonus = 0.1 if path.governance_approved else -0.2
            adjusted_score = max(0.1, path.trust_score - age_penalty + governance_bonus)
            trust_scores.append(adjusted_score)
            symbolic_sequences.extend(path.symbolic_signature)

        # Combine scores with diminishing returns
        if trust_scores:
            final_score = trust_scores[0]
            for i, score in enumerate(trust_scores[1:], 1):
                weight = 1.0 / (i + 1)
                final_score += score * weight
            final_score = min(1.0, final_score)
        else:
            final_score = 0.1  # Minimum trust

        return {
            "applicable_paths": applicable_paths,
            "final_trust_score": final_score,
            "symbolic_sequence": symbolic_sequences[:5],  # Limit symbols
            "path_count": len(applicable_paths),
            "governance_validated_paths": len([p for p in applicable_paths if p.governance_approved]),
        }

    def _path_applies_to_request(self, path: TrustPath, request: ConsentRequest) -> bool:
        """Check if a trust path applies to the consent request"""
        # Enhanced matching logic with governance considerations
        basic_match = (
            request.requester == path.target
            or request.requester in request.context.get("roles", [])
            or (path.path_type == "emergency" and request.context.get("emergency", False))
        )

        # Additional Trinity Framework matching
        if path.metadata.get("trinity_protected"):
            return basic_match and self._is_trinity_protected_resource(request)

        return basic_match

    def _calculate_age_penalty(self, path: TrustPath) -> float:
        """Calculate trust penalty based on path age with governance adjustments"""
        age_seconds = time.time() - path.last_validated
        age_days = age_seconds / 86400

        # 5% penalty per day, max 50%, but reduced penalty for governance-approved paths
        base_penalty = min(0.5, age_days * 0.05)
        if path.governance_approved:
            base_penalty *= 0.7  # Reduce penalty for governance-approved paths

        return base_penalty

    async def _create_temporary_trust_path(self, request: ConsentRequest) -> TrustPath:
        """Create a temporary trust path with governance validation"""
        # Base trust assessment
        base_trust = 0.3

        # Adjust based on context and governance factors
        if request.context.get("verified_identity"):
            base_trust += 0.3
        if request.context.get("known_system"):
            base_trust += 0.2
        if request.context.get("emergency"):
            base_trust += 0.1
        if request.governance_validated:
            base_trust += 0.2

        # Determine path type and symbols
        if request.context.get("emergency"):
            path_type = "emergency"
            symbols = self.TRUST_SYMBOLS["emergency"]
        elif base_trust > 0.7:
            path_type = "direct"
            symbols = self.TRUST_SYMBOLS["direct"]
        else:
            path_type = "degraded"
            symbols = self.TRUST_SYMBOLS["degraded"]

        # Add governance symbols if validated
        if request.governance_validated:
            symbols = self.TRUST_SYMBOLS["governance_approved"]

        return TrustPath(
            path_id=f"temp_{request.requester}_{int(time.time())}",
            source="unknown",
            target=request.requester,
            trust_score=min(1.0, base_trust),
            path_type=path_type,
            created_at=time.time(),
            last_validated=time.time(),
            validation_count=0,
            symbolic_signature=symbols,
            metadata={
                "temporary": True,
                "auto_created": True,
                "governance_validated": request.governance_validated,
            },
            governance_approved=request.governance_validated,
        )

    async def _apply_escalation_rules(self, request: ConsentRequest) -> Optional[dict]:
        """Apply escalation rules with governance and Trinity Framework awareness"""
        # Build enhanced evaluation context
        eval_context = {
            "request": request,
            "permission_type": request.permission_type,
            "trust_score": request.trust_score,
            "context": request.context,
            "recent_denial_count": self._get_recent_denials(request.requester),
            "requester_stats": dict(self.requester_stats[request.requester]),
            "trinity_impact": request.trinity_impact,
            "governance_validated": request.governance_validated,
        }

        # Check each rule
        for rule in self.escalation_rules:
            try:
                condition = rule["condition"]

                # Enhanced evaluation with Trinity Framework and governance
                if self._evaluate_enhanced_condition(condition, eval_context):
                    logger.info(f"Escalation rule '{rule['name']}' triggered for {request.id}")

                    return {
                        "rule_name": rule["name"],
                        "level": rule["escalation_level"],
                        "reason": f"Rule '{rule['name']}' condition met",
                        "actions": rule["actions"],
                        "symbolic_response": rule["symbolic_response"],
                        "governance_required": rule.get("governance_required", False),
                    }

            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.get('name', 'unknown')}': {e}")
                continue

        return None

    def _evaluate_enhanced_condition(self, condition: str, context: dict) -> bool:
        """Enhanced condition evaluation with Trinity Framework and governance support"""
        try:
            # Handle Trinity Framework conditions
            if "trinity_impact.get(" in condition:
                if "trinity_impact.get('identity', 0) > 0.7" in condition:
                    return context["trinity_impact"].get("identity", 0) > 0.7
                elif "trinity_impact.get('consciousness', 0) > 0.8" in condition:
                    return context["trinity_impact"].get("consciousness", 0) > 0.8
                elif "trinity_impact.get('guardian', 0) > 0.6" in condition:
                    return context["trinity_impact"].get("guardian", 0) > 0.6

            # Handle existing conditions (inherited from parent)
            if "permission_type in" in condition and "['admin', 'root', 'critical']" in condition:
                perm_check = context["permission_type"] in ["admin", "root", "critical"]
                trust_check = "trust_score < 0.8" in condition and context["trust_score"] < 0.8
                return perm_check and trust_check

            if "trust_score <" in condition:
                if "trust_score < 0.3" in condition:
                    return context["trust_score"] < 0.3
                if "trust_score < 0.8" in condition:
                    return context["trust_score"] < 0.8

            if "recent_denial_count >=" in condition and "recent_denial_count >= 3" in condition:
                return context["recent_denial_count"] >= 3

            if "context.get('emergency', False)" in condition:
                emergency_check = context["context"].get("emergency", False)
                trust_check = "trust_score > 0.5" in condition and context["trust_score"] > 0.5
                return emergency_check and trust_check

            return False

        except Exception as e:
            logger.error(f"Enhanced condition evaluation error: {e}")
            return False

    def _get_recent_denials(self, requester: str, hours: int = 24) -> int:
        """Get count of recent denials for a requester"""
        cutoff_time = time.time() - (hours * 3600)

        count = 0
        for entry in self.consent_history:
            if (
                entry.get("requester") == requester
                and entry.get("status") == "denied"
                and entry.get("requested_at", 0) > cutoff_time
            ):
                count += 1

        return count

    async def _execute_escalation_actions(self, request: ConsentRequest, actions: list[str]):
        """Execute escalation actions with governance integration"""
        for action in actions:
            try:
                if action == "require_multi_factor":
                    request.context["mfa_required"] = True
                elif action == "human_review":
                    request.context["human_review_required"] = True
                elif action == "governance_approval":
                    request.context["governance_approval_required"] = True
                elif action == "governance_review":
                    request.context["governance_review_required"] = True
                elif action == "governance_escalation":
                    request.context["governance_escalation_triggered"] = True
                elif action == "governance_notification":
                    request.context["governance_notification_sent"] = True
                elif action == "governance_emergency":
                    request.context["governance_emergency_declared"] = True
                elif action == "identity_verification":
                    request.context["identity_verification_required"] = True
                elif action == "consciousness_protection":
                    request.context["consciousness_protection_active"] = True
                elif action == "security_lockdown":
                    request.context["security_lockdown_initiated"] = True
                elif action == "trust_analysis":
                    request.context["deep_trust_analysis"] = True
                elif action == "additional_verification":
                    request.context["additional_verification_required"] = True
                elif action == "security_review":
                    request.context["security_review_triggered"] = True
                elif action == "temporary_restriction":
                    request.context["temporary_restriction_applied"] = True
                elif action == "emergency_bypass":
                    request.status = ConsentStatus.GRANTED
                    request.decision_reason = "Emergency bypass activated with governance oversight"
                elif action == "immediate_audit":
                    request.context["immediate_audit"] = True
                elif action == "impact_assessment":
                    request.context["trinity_impact_assessment_required"] = True
                else:
                    logger.warning(f"Unknown escalation action: {action}")

                # Log action in governance system
                await self._log_governance_action(
                    f"escalation_action_{action}", {"request_id": request.id, "action": action}
                )

            except Exception as e:
                logger.error(f"Failed to execute action '{action}': {e}")

    def _generate_symbolic_response(self, request: ConsentRequest) -> list[str]:
        """Generate symbolic response with governance and Trinity Framework awareness"""
        if request.escalation_level:
            # Use escalation rule's symbols
            for rule in self.escalation_rules:
                if rule["escalation_level"] == request.escalation_level:
                    return rule["symbolic_response"]

        # Enhanced symbols based on status and governance
        status_symbols = {
            ConsentStatus.GRANTED: ["✅", "🔓", "🤝"],
            ConsentStatus.DENIED: ["❌", "🔒", "🛡️"],
            ConsentStatus.PENDING: ["⏳", "🔍", "📋"],
            ConsentStatus.ESCALATED: ["⬆️", "👤", "🛡️"],
            ConsentStatus.EXPIRED: ["⏰", "❌", "🔒"],
            ConsentStatus.REVOKED: ["🚫", "❌", "🔒"],
        }

        base_symbols = status_symbols.get(request.status, ["❓", "⚠️", "🔍"])

        # Add governance symbols
        if request.governance_validated:
            base_symbols.insert(0, "🛡️")

        # Add Trinity Framework symbols if high impact
        if request.trinity_impact and max(request.trinity_impact.values()) > 0.7:
            if request.trinity_impact["identity"] > 0.7:
                base_symbols.append("⚛️")
            if request.trinity_impact["consciousness"] > 0.7:
                base_symbols.append("🧠")
            if request.trinity_impact["guardian"] > 0.7:
                base_symbols.append("🛡️")

        return base_symbols[:5]  # Limit to 5 symbols

    async def _log_consent_decision(self, request: ConsentRequest):
        """Log the consent decision with comprehensive governance metadata"""
        log_entry = {
            "request_id": request.id,
            "requester": request.requester,
            "target_resource": request.target_resource,
            "permission_type": request.permission_type,
            "requested_at": request.requested_at,
            "processed_at": time.time(),
            "status": request.status.value,
            "trust_score": request.trust_score,
            "decision_reason": request.decision_reason,
            "escalation_level": request.escalation_level.name if request.escalation_level else None,
            "symbolic_path": request.symbolic_path,
            "governance_validated": request.governance_validated,
            "trinity_impact": request.trinity_impact,
            "governance_escalation": any(
                "governance" in action for action in request.context if "governance" in action.lower()
            ),
        }

        self.consent_history.append(log_entry)

        # Update requester stats with governance tracking
        stats = self.requester_stats[request.requester]
        if request.status == ConsentStatus.GRANTED:
            stats["granted"] += 1
        elif request.status == ConsentStatus.DENIED:
            stats["denied"] += 1
        elif request.status in [ConsentStatus.ESCALATED, ConsentStatus.PENDING]:
            stats["escalated"] += 1
            if log_entry["governance_escalation"]:
                stats["governance_escalations"] += 1

        # Save to file periodically
        if len(self.consent_history) % 10 == 0:
            self._save_consent_history()

        # Log in governance system
        await self._log_governance_action(
            "consent_decision_logged",
            {
                "request_id": request.id,
                "status": request.status.value,
                "governance_validated": request.governance_validated,
                "trinity_impact": request.trinity_impact,
            },
        )

    def _log_governance_action(self, action: str, metadata: dict[str, Any]):
        """Log action in governance audit system"""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "metadata": metadata,
            "source": "consent_manager",
            "symbolic_signature": self.generate_governance_glyph(action, metadata),
        }

        self.governance_log.append(log_entry)

        # Keep only last 5000 entries
        if len(self.governance_log) > 5000:
            self.governance_log = self.governance_log[-5000:]

        logger.debug(f"🔍 Governance action logged: {action}")

    # Enhanced public API methods

    async def revoke_consent(self, request_id: str, reason: str = "User revoked") -> bool:
        """Revoke a previously granted consent with governance tracking"""
        # Find in active or history
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            request.status = ConsentStatus.REVOKED
            request.decision_reason = reason

            await self._log_consent_decision(request)
            await self._log_governance_action("consent_revoked", {"request_id": request_id, "reason": reason})

            logger.info(f"Consent revoked: {request_id}")
            return True

        return False

    def get_requester_trust_summary(self, requester: str) -> dict:
        """Get enhanced trust summary with governance and Trinity metrics"""
        stats = self.requester_stats[requester]

        if stats["total_requests"] == 0:
            return {"error": "No data available for requester"}

        # Calculate enhanced metrics
        success_rate = stats["granted"] / stats["total_requests"]
        governance_escalation_rate = stats["governance_escalations"] / stats["total_requests"]
        trust_history = stats["trust_history"]
        trinity_history = stats["trinity_impact_history"]

        if len(trust_history) >= 2:
            trend = "improving" if trust_history[-1] > trust_history[0] else "declining"
            if abs(trust_history[-1] - trust_history[0]) < 0.1:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Calculate average Trinity impact
        avg_trinity_impact = {"identity": 0.0, "consciousness": 0.0, "guardian": 0.0}
        if trinity_history:
            for impact in trinity_history:
                for component in avg_trinity_impact:
                    avg_trinity_impact[component] += impact.get(component, 0.0)
            for component in avg_trinity_impact:
                avg_trinity_impact[component] /= len(trinity_history)

        return {
            "requester": requester,
            "total_requests": stats["total_requests"],
            "success_rate": success_rate,
            "governance_escalation_rate": governance_escalation_rate,
            "current_trust": trust_history[-1] if trust_history else 0.5,
            "trust_trend": trend,
            "average_trinity_impact": avg_trinity_impact,
            "last_request_age": time.time() - stats["last_request"] if stats["last_request"] else None,
            "governance_compliant": governance_escalation_rate < 0.1,
        }

    def get_enhanced_consent_statistics(self) -> dict:
        """Get comprehensive consent system statistics with governance metrics"""
        total_requests = len(self.consent_history)
        if total_requests == 0:
            return {"total_requests": 0}

        # Count by status
        status_counts = {}
        governance_escalations = 0
        trinity_high_impact = 0

        for entry in self.consent_history:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            if entry.get("governance_escalation"):
                governance_escalations += 1

            trinity_impact = entry.get("trinity_impact", {})
            if any(impact > 0.7 for impact in trinity_impact.values()):
                trinity_high_impact += 1

        # Recent activity (last 24 hours)
        recent_cutoff = time.time() - 86400
        recent_requests = [entry for entry in self.consent_history if entry.get("requested_at", 0) > recent_cutoff]

        return {
            "total_requests": total_requests,
            "status_distribution": status_counts,
            "active_requests": len(self.active_requests),
            "trust_paths": len(self.trust_paths),
            "governance_approved_paths": len([p for p in self.trust_paths.values() if p.governance_approved]),
            "recent_24h": len(recent_requests),
            "success_rate": status_counts.get("granted", 0) / total_requests,
            "escalation_rate": status_counts.get("escalated", 0) / total_requests,
            "governance_escalation_rate": governance_escalations / total_requests,
            "trinity_high_impact_rate": trinity_high_impact / total_requests,
            "governance_enabled": self.governance_enabled,
            "governance_log_entries": len(self.governance_log),
        }

    async def health_check(self) -> bool:
        """Perform comprehensive health check including governance systems"""
        try:
            # Check basic functionality
            test_request = ConsentRequest(
                id="health_check",
                requester="system",
                target_resource="/health/check",
                permission_type="read",
                requested_at=time.time(),
                expires_at=time.time() + 3600,
                context={"health_check": True},
                symbolic_path=["🔍"],
                trust_score=0.8,
            )

            # Validate governance if enabled
            if self.governance_enabled:
                governance_result = await self._validate_governance_compliance(test_request)
                if not governance_result["approved"]:
                    return False

            # Check Trinity Framework analysis
            trinity_analysis = await self._analyze_trinity_impact(test_request)
            return trinity_analysis

        except Exception as e:
            logger.error(f"Consent manager health check failed: {e}")
            return False


if __name__ == "__main__":

    async def demo():
        """Demo enhanced consent management with governance"""
        print("🔐 Enhanced Consent Manager Demo")
        print("=" * 45)

        manager = ConsentManager(governance_enabled=True)

        # Create test requests with governance and Trinity Framework context
        test_requests = [
            ConsentRequest(
                id=str(uuid.uuid4()),
                requester="alice@example.com",
                target_resource="/api/user/data",
                permission_type="read",
                requested_at=time.time(),
                expires_at=time.time() + 3600,
                context={"verified_identity": True, "user_tier": 2},
                symbolic_path=["🔐"],
                trust_score=0.8,
            ),
            ConsentRequest(
                id=str(uuid.uuid4()),
                requester="unknown_user",
                target_resource="/admin/critical",
                permission_type="admin",
                requested_at=time.time(),
                expires_at=time.time() + 1800,
                context={"user_tier": 1},
                symbolic_path=["❓"],
                trust_score=0.2,
            ),
            ConsentRequest(
                id=str(uuid.uuid4()),
                requester="emergency_responder",
                target_resource="/identity/core/modify",
                permission_type="modify",
                requested_at=time.time(),
                expires_at=time.time() + 900,
                context={"emergency": True, "verified_identity": True, "user_tier": 3},
                symbolic_path=["🚨"],
                trust_score=0.6,
            ),
        ]

        # Process requests
        for request in test_requests:
            print(f"\n🔍 Processing: {request.id[:8]}")
            print(f"   Requester: {request.requester}")
            print(f"   Resource: {request.target_resource}")
            print(f"   Permission: {request.permission_type}")
            print(f"   Initial trust: {request.trust_score}")

            result = await manager.process_consent_request(request)

            print(f"   Status: {result.status.value}")
            print(f"   Final trust: {result.trust_score:.2f}")
            print(f"   Governance validated: {result.governance_validated}")
            print(
                f"   Trinity impact: I:{result.trinity_impact['identity']:.1f} C:{result.trinity_impact['consciousness']:.1f} G:{result.trinity_impact['guardian']:.1f}"
            )
            print(f"   Reason: {result.decision_reason}")
            print(f"   Symbols: {'→'.join(result.symbolic_path)}")
            if result.escalation_level:
                print(f"   Escalation: {result.escalation_level.name}")

        # Show enhanced statistics
        stats = manager.get_enhanced_consent_statistics()
        print("\n📊 Enhanced Statistics:")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Success rate: {stats['success_rate']:.2f}")
        print(f"   Governance escalation rate: {stats['governance_escalation_rate']:.2f}")
        print(f"   Trinity high impact rate: {stats['trinity_high_impact_rate']:.2f}")
        print(f"   Governance enabled: {stats['governance_enabled']}")
        print(f"   Governance log entries: {stats['governance_log_entries']}")
        print(f"   Status distribution: {stats['status_distribution']}")

    asyncio.run(demo())