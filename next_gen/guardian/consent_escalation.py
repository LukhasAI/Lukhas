#!/usr/bin/env python3
"""
Consent Escalation Resolver - Advanced trust path recovery and consent management
Handles complex consent scenarios with symbolic trust path reconstruction
"""
import asyncio
import json
import logging
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    """Represents a consent request in the system"""

    id: str
    requester: str
    target_resource: str
    permission_type: str
    requested_at: float
    expires_at: float
    context: dict
    symbolic_path: list[str]
    trust_score: float
    status: ConsentStatus = ConsentStatus.PENDING
    decision_reason: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    escalation_history: list[dict] = field(default_factory=list)


@dataclass
class TrustPath:
    """Represents a trust relationship path"""

    path_id: str
    nodes: list[str]  # Trust nodes in the path
    trust_scores: list[float]  # Trust score for each edge
    symbolic_sequence: list[str]  # Symbolic representation
    path_strength: float  # Overall path strength
    created_at: float
    last_validated: float
    validation_count: int = 0


@dataclass
class EscalationRule:
    """Defines escalation behavior for consent scenarios"""

    rule_id: str
    condition: str  # Python expression for condition matching
    escalation_level: EscalationLevel
    actions: list[str]  # Actions to take when rule matches
    symbolic_response: list[str]  # Symbolic sequence for response
    priority: int
    enabled: bool = True


class ConsentEscalationResolver:
    """
    Advanced consent escalation resolver with symbolic trust path reconstruction
    Handles complex consent scenarios and trust path recovery
    """

    # Default escalation rules
    DEFAULT_RULES = [
        EscalationRule(
            rule_id="high_value_resource",
            condition="request.permission_type in ['admin', 'root', 'critical'] and request.trust_score < 0.8",
            escalation_level=EscalationLevel.HIGH,
            actions=["require_multi_factor", "human_review", "audit_log"],
            symbolic_response=["🔐", "👤", "📋"],
            priority=1,
        ),
        EscalationRule(
            rule_id="low_trust_score",
            condition="request.trust_score < 0.3",
            escalation_level=EscalationLevel.MEDIUM,
            actions=["trust_path_analysis", "additional_verification"],
            symbolic_response=["🔍", "🛡️", "✅"],
            priority=2,
        ),
        EscalationRule(
            rule_id="repeat_denial",
            condition="requester_denial_count >= 3",
            escalation_level=EscalationLevel.HIGH,
            actions=["security_review", "temporary_restriction"],
            symbolic_response=["🚨", "⏸️", "🔒"],
            priority=1,
        ),
        EscalationRule(
            rule_id="expired_consent",
            condition="request.status == ConsentStatus.EXPIRED and request.trust_score > 0.7",
            escalation_level=EscalationLevel.LOW,
            actions=["auto_renewal_consideration", "notify_requester"],
            symbolic_response=["🔄", "📬", "⏰"],
            priority=3,
        ),
        EscalationRule(
            rule_id="emergency_access",
            condition="request.context.get('emergency', False) and request.trust_score > 0.5",
            escalation_level=EscalationLevel.EMERGENCY,
            actions=["emergency_bypass", "immediate_audit", "security_notification"],
            symbolic_response=["🚨", "⚡", "🔓"],
            priority=0,  # Highest priority
        ),
    ]

    # Symbolic patterns for trust path analysis
    TRUST_PATTERNS = {
        "direct_trust": {
            "pattern": ["🔐", "🤝", "✅"],
            "strength_modifier": 1.0,
            "description": "Direct trust relationship",
        },
        "transitive_trust": {
            "pattern": ["🔐", "🔗", "🤝", "✅"],
            "strength_modifier": 0.8,
            "description": "Trust through intermediary",
        },
        "verified_identity": {
            "pattern": ["🆔", "✅", "🔐"],
            "strength_modifier": 1.2,
            "description": "Verified identity trust",
        },
        "degraded_trust": {
            "pattern": ["🔐", "⚠️", "🤝"],
            "strength_modifier": 0.6,
            "description": "Trust with warnings",
        },
        "emergency_trust": {
            "pattern": ["🚨", "⚡", "🔓"],
            "strength_modifier": 0.9,
            "description": "Emergency access trust",
        },
    }

    def __init__(
        self,
        rules_file: str = "next_gen/guardian/escalation_rules.json",
        trust_db_file: str = "next_gen/guardian/trust_paths.json",
        consent_log_file: str = "next_gen/guardian/consent_log.json",
    ):
        self.rules_file = Path(rules_file)
        self.trust_db_file = Path(trust_db_file)
        self.consent_log_file = Path(consent_log_file)

        # State management
        self.escalation_rules: list[EscalationRule] = []
        self.trust_paths: dict[str, TrustPath] = {}
        self.active_requests: dict[str, ConsentRequest] = {}
        self.consent_history: list[dict] = []
        self.requester_stats: dict[str, dict] = {}

        # Initialize system
        self._load_escalation_rules()
        self._load_trust_paths()
        self._load_consent_history()

        logger.info("🛡️ Consent Escalation Resolver initialized")

    def _load_escalation_rules(self):
        """Load escalation rules from file or use defaults"""
        try:
            if self.rules_file.exists():
                with open(self.rules_file) as f:
                    rules_data = json.load(f)

                self.escalation_rules = []
                for rule_data in rules_data:
                    rule = EscalationRule(
                        rule_id=rule_data["rule_id"],
                        condition=rule_data["condition"],
                        escalation_level=EscalationLevel(rule_data["escalation_level"]),
                        actions=rule_data["actions"],
                        symbolic_response=rule_data["symbolic_response"],
                        priority=rule_data["priority"],
                        enabled=rule_data.get("enabled", True),
                    )
                    self.escalation_rules.append(rule)
            else:
                # Use default rules
                self.escalation_rules = self.DEFAULT_RULES.copy()
                self._save_escalation_rules()

        except Exception as e:
            logger.warning(f"Failed to load escalation rules: {e}. Using defaults.")
            self.escalation_rules = self.DEFAULT_RULES.copy()

    def _save_escalation_rules(self):
        """Save escalation rules to file"""
        try:
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)
            rules_data = []
            for rule in self.escalation_rules:
                rule_dict = asdict(rule)
                rule_dict["escalation_level"] = rule.escalation_level.value
                rules_data.append(rule_dict)

            with open(self.rules_file, "w") as f:
                json.dump(rules_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save escalation rules: {e}")

    def _load_trust_paths(self):
        """Load trust paths from database"""
        try:
            if self.trust_db_file.exists():
                with open(self.trust_db_file) as f:
                    trust_data = json.load(f)

                self.trust_paths = {}
                for path_id, path_data in trust_data.items():
                    trust_path = TrustPath(
                        path_id=path_data["path_id"],
                        nodes=path_data["nodes"],
                        trust_scores=path_data["trust_scores"],
                        symbolic_sequence=path_data["symbolic_sequence"],
                        path_strength=path_data["path_strength"],
                        created_at=path_data["created_at"],
                        last_validated=path_data["last_validated"],
                        validation_count=path_data.get("validation_count", 0),
                    )
                    self.trust_paths[path_id] = trust_path
            else:
                self.trust_paths = {}
                self._create_default_trust_paths()

        except Exception as e:
            logger.warning(f"Failed to load trust paths: {e}")
            self.trust_paths = {}

    def _create_default_trust_paths(self):
        """Create default trust paths for system bootstrap"""
        default_paths = [
            TrustPath(
                path_id="system_admin",
                nodes=["system", "admin_role", "user"],
                trust_scores=[1.0, 0.9],
                symbolic_sequence=["🔐", "👤", "✅"],
                path_strength=0.95,
                created_at=time.time(),
                last_validated=time.time(),
            ),
            TrustPath(
                path_id="verified_user",
                nodes=["identity_provider", "user"],
                trust_scores=[0.8],
                symbolic_sequence=["🆔", "✅"],
                path_strength=0.8,
                created_at=time.time(),
                last_validated=time.time(),
            ),
            TrustPath(
                path_id="emergency_access",
                nodes=["emergency_system", "user"],
                trust_scores=[0.9],
                symbolic_sequence=["🚨", "🔓"],
                path_strength=0.9,
                created_at=time.time(),
                last_validated=time.time(),
            ),
        ]

        for path in default_paths:
            self.trust_paths[path.path_id] = path

        self._save_trust_paths()

    def _save_trust_paths(self):
        """Save trust paths to database"""
        try:
            self.trust_db_file.parent.mkdir(parents=True, exist_ok=True)
            trust_data = {}
            for path_id, path in self.trust_paths.items():
                trust_data[path_id] = asdict(path)

            with open(self.trust_db_file, "w") as f:
                json.dump(trust_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save trust paths: {e}")

    def _load_consent_history(self):
        """Load consent decision history"""
        try:
            if self.consent_log_file.exists():
                with open(self.consent_log_file) as f:
                    self.consent_history = json.load(f)

                # Rebuild requester statistics
                self._rebuild_requester_stats()
            else:
                self.consent_history = []
                self.requester_stats = {}

        except Exception as e:
            logger.warning(f"Failed to load consent history: {e}")
            self.consent_history = []
            self.requester_stats = {}

    def _rebuild_requester_stats(self):
        """Rebuild requester statistics from history"""
        self.requester_stats = {}

        for entry in self.consent_history:
            requester = entry.get("requester", "unknown")
            if requester not in self.requester_stats:
                self.requester_stats[requester] = {
                    "total_requests": 0,
                    "granted": 0,
                    "denied": 0,
                    "escalated": 0,
                    "last_request": 0,
                    "trust_trend": [],
                }

            stats = self.requester_stats[requester]
            stats["total_requests"] += 1

            status = entry.get("status", "unknown")
            if status == "granted":
                stats["granted"] += 1
            elif status == "denied":
                stats["denied"] += 1
            elif status in ["escalated", "pending"]:
                stats["escalated"] += 1

            stats["last_request"] = max(stats["last_request"], entry.get("requested_at", 0))
            stats["trust_trend"].append(entry.get("trust_score", 0.5))

            # Keep only recent trust scores
            if len(stats["trust_trend"]) > 20:
                stats["trust_trend"] = stats["trust_trend"][-20:]

    async def process_consent_request(self, request: ConsentRequest) -> ConsentRequest:
        """Process a consent request through escalation analysis"""
        logger.info(f"Processing consent request {request.id} from {request.requester}")

        # Add to active requests
        self.active_requests[request.id] = request

        # Update requester statistics
        self._update_requester_stats(request)

        # Analyze trust paths
        trust_analysis = await self._analyze_trust_paths(request)
        request.trust_score = trust_analysis["final_trust_score"]

        # Apply escalation rules
        escalation_result = await self._apply_escalation_rules(request)

        if escalation_result:
            request.escalation_level = escalation_result["level"]
            request.status = ConsentStatus.ESCALATED
            request.decision_reason = escalation_result["reason"]

            # Execute escalation actions
            await self._execute_escalation_actions(request, escalation_result["actions"])

            # Log escalation
            escalation_entry = {
                "timestamp": time.time(),
                "level": escalation_result["level"].name,
                "reason": escalation_result["reason"],
                "actions": escalation_result["actions"],
                "symbolic_response": escalation_result["symbolic_response"],
            }
            request.escalation_history.append(escalation_entry)

        else:
            # No escalation needed - make automatic decision
            if request.trust_score >= 0.7:
                request.status = ConsentStatus.GRANTED
                request.decision_reason = "Automatic approval - high trust score"
            elif request.trust_score >= 0.4:
                request.status = ConsentStatus.PENDING
                request.decision_reason = "Manual review required - medium trust score"
            else:
                request.status = ConsentStatus.DENIED
                request.decision_reason = "Automatic denial - low trust score"

        # Log the decision
        await self._log_consent_decision(request)

        # Generate symbolic response
        symbolic_response = self._generate_symbolic_response(request)
        request.symbolic_path.extend(symbolic_response)

        logger.info(f"Consent request {request.id} processed: {request.status.value}")
        return request

    def _update_requester_stats(self, request: ConsentRequest):
        """Update statistics for the requester"""
        requester = request.requester
        if requester not in self.requester_stats:
            self.requester_stats[requester] = {
                "total_requests": 0,
                "granted": 0,
                "denied": 0,
                "escalated": 0,
                "last_request": 0,
                "trust_trend": [],
            }

        stats = self.requester_stats[requester]
        stats["total_requests"] += 1
        stats["last_request"] = request.requested_at
        stats["trust_trend"].append(request.trust_score)

        # Keep only recent trend data
        if len(stats["trust_trend"]) > 20:
            stats["trust_trend"] = stats["trust_trend"][-20:]

    async def _analyze_trust_paths(self, request: ConsentRequest) -> dict:
        """Analyze available trust paths for the request"""
        request.requester
        request.target_resource

        # Find applicable trust paths
        applicable_paths = []
        for path in self.trust_paths.values():
            if self._path_applies_to_request(path, request):
                applicable_paths.append(path)

        if not applicable_paths:
            # No existing paths - create temporary path
            temp_path = await self._create_temporary_trust_path(request)
            applicable_paths.append(temp_path)

        # Calculate combined trust score
        path_scores = []
        symbolic_sequences = []

        for path in applicable_paths:
            # Validate path freshness
            path_age = time.time() - path.last_validated
            freshness_penalty = min(0.2, path_age / 86400)  # Max 20% penalty after 1 day

            adjusted_score = path.path_strength - freshness_penalty
            path_scores.append(max(0.1, adjusted_score))  # Minimum score
            symbolic_sequences.extend(path.symbolic_sequence)

        # Combine scores (weighted average with diminishing returns)
        if path_scores:
            # Primary path gets full weight, additional paths get reduced weight
            final_score = path_scores[0]
            for i, score in enumerate(path_scores[1:], 1):
                weight = 1.0 / (i + 1)  # Diminishing weight
                final_score += score * weight

            # Normalize to [0, 1]
            final_score = min(1.0, final_score)
        else:
            final_score = 0.1  # Default minimum trust

        return {
            "applicable_paths": applicable_paths,
            "final_trust_score": final_score,
            "symbolic_sequence": symbolic_sequences,
            "path_count": len(applicable_paths),
        }

    def _path_applies_to_request(self, path: TrustPath, request: ConsentRequest) -> bool:
        """Check if a trust path applies to the consent request"""
        # Simple heuristic: path applies if requester matches a node
        # In production, this would be more sophisticated
        return request.requester in path.nodes or any(node in request.context.get("roles", []) for node in path.nodes)

    async def _create_temporary_trust_path(self, request: ConsentRequest) -> TrustPath:
        """Create a temporary trust path for unknown requesters"""
        path_id = f"temp_{request.requester}_{int(time.time())}"

        # Basic trust assessment based on context
        base_trust = 0.3  # Default for unknown requesters

        # Adjust based on available context
        if request.context.get("verified_identity"):
            base_trust += 0.3
        if request.context.get("known_system"):
            base_trust += 0.2
        if request.context.get("emergency"):
            base_trust += 0.1

        # Generate symbolic sequence based on trust level
        if base_trust > 0.7:
            symbolic_sequence = ["🆔", "✅", "🔐"]
        elif base_trust > 0.5:
            symbolic_sequence = ["🔍", "🤝", "⚠️"]
        else:
            symbolic_sequence = ["❓", "⚠️", "🔒"]

        temp_path = TrustPath(
            path_id=path_id,
            nodes=["unknown", request.requester],
            trust_scores=[base_trust],
            symbolic_sequence=symbolic_sequence,
            path_strength=base_trust,
            created_at=time.time(),
            last_validated=time.time(),
        )

        # Store temporarily (don't persist to database)
        self.trust_paths[path_id] = temp_path

        return temp_path

    async def _apply_escalation_rules(self, request: ConsentRequest) -> Optional[dict]:
        """Apply escalation rules to determine if escalation is needed"""
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted([r for r in self.escalation_rules if r.enabled], key=lambda x: x.priority)

        # Prepare evaluation context
        eval_context = {
            "request": request,
            "ConsentStatus": ConsentStatus,
            "time": time.time(),
            "requester_stats": self.requester_stats.get(request.requester, {}),
            "requester_denial_count": self._get_recent_denials(request.requester),
        }

        # Apply rules in priority order
        for rule in sorted_rules:
            try:
                # Evaluate rule condition
                if eval(rule.condition, {"__builtins__": {}}, eval_context):
                    logger.info(f"Escalation rule '{rule.rule_id}' triggered for request {request.id}")

                    return {
                        "rule_id": rule.rule_id,
                        "level": rule.escalation_level,
                        "reason": f"Rule '{rule.rule_id}' condition met",
                        "actions": rule.actions,
                        "symbolic_response": rule.symbolic_response,
                    }

            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.rule_id}': {e}")
                continue

        return None  # No escalation needed

    def _get_recent_denials(self, requester: str, window_hours: int = 24) -> int:
        """Get count of recent denials for a requester"""
        cutoff_time = time.time() - (window_hours * 3600)

        denial_count = 0
        for entry in self.consent_history:
            if (
                entry.get("requester") == requester
                and entry.get("status") == "denied"
                and entry.get("requested_at", 0) > cutoff_time
            ):
                denial_count += 1

        return denial_count

    async def _execute_escalation_actions(self, request: ConsentRequest, actions: list[str]):
        """Execute escalation actions"""
        for action in actions:
            try:
                if action == "require_multi_factor":
                    await self._require_multi_factor_auth(request)
                elif action == "human_review":
                    await self._request_human_review(request)
                elif action == "audit_log":
                    await self._create_audit_log_entry(request)
                elif action == "trust_path_analysis":
                    await self._deep_trust_analysis(request)
                elif action == "additional_verification":
                    await self._request_additional_verification(request)
                elif action == "security_review":
                    await self._trigger_security_review(request)
                elif action == "temporary_restriction":
                    await self._apply_temporary_restriction(request)
                elif action == "auto_renewal_consideration":
                    await self._consider_auto_renewal(request)
                elif action == "notify_requester":
                    await self._notify_requester(request)
                elif action == "emergency_bypass":
                    await self._emergency_bypass(request)
                elif action == "immediate_audit":
                    await self._immediate_audit(request)
                elif action == "security_notification":
                    await self._security_notification(request)
                else:
                    logger.warning(f"Unknown escalation action: {action}")

            except Exception as e:
                logger.error(f"Failed to execute escalation action '{action}': {e}")

    async def _require_multi_factor_auth(self, request: ConsentRequest):
        """Require multi-factor authentication"""
        logger.info(f"Multi-factor auth required for request {request.id}")
        # In production, integrate with MFA system
        request.context["mfa_required"] = True

    async def _request_human_review(self, request: ConsentRequest):
        """Request human review"""
        logger.info(f"Human review requested for request {request.id}")
        request.context["human_review_required"] = True

    async def _create_audit_log_entry(self, request: ConsentRequest):
        """Create audit log entry"""
        audit_entry = {
            "timestamp": time.time(),
            "event": "consent_escalation",
            "request_id": request.id,
            "requester": request.requester,
            "resource": request.target_resource,
            "permission": request.permission_type,
            "trust_score": request.trust_score,
            "escalation_level": (request.escalation_level.name if request.escalation_level else None),
        }

        # In production, write to audit log system
        logger.info(f"Audit log entry created: {json.dumps(audit_entry)}")

    async def _deep_trust_analysis(self, request: ConsentRequest):
        """Perform deep trust path analysis"""
        logger.info(f"Deep trust analysis for request {request.id}")
        # Implement sophisticated trust analysis
        request.context["deep_analysis_performed"] = True

    async def _request_additional_verification(self, request: ConsentRequest):
        """Request additional verification"""
        logger.info(f"Additional verification requested for request {request.id}")
        request.context["additional_verification_required"] = True

    async def _trigger_security_review(self, request: ConsentRequest):
        """Trigger security review"""
        logger.info(f"Security review triggered for request {request.id}")
        request.context["security_review_triggered"] = True

    async def _apply_temporary_restriction(self, request: ConsentRequest):
        """Apply temporary restriction"""
        logger.info(f"Temporary restriction applied for requester {request.requester}")
        # In production, update access control system
        request.context["temporary_restriction_applied"] = True

    async def _consider_auto_renewal(self, request: ConsentRequest):
        """Consider automatic renewal of expired consent"""
        logger.info(f"Auto-renewal consideration for request {request.id}")
        request.context["auto_renewal_considered"] = True

    async def _notify_requester(self, request: ConsentRequest):
        """Notify the requester of the decision"""
        logger.info(f"Requester notification sent for request {request.id}")
        request.context["requester_notified"] = True

    async def _emergency_bypass(self, request: ConsentRequest):
        """Emergency bypass procedure"""
        logger.warning(f"Emergency bypass activated for request {request.id}")
        request.status = ConsentStatus.GRANTED
        request.decision_reason = "Emergency bypass activated"
        request.context["emergency_bypass"] = True

    async def _immediate_audit(self, request: ConsentRequest):
        """Immediate audit of emergency access"""
        logger.warning(f"Immediate audit initiated for emergency request {request.id}")
        request.context["immediate_audit"] = True

    async def _security_notification(self, request: ConsentRequest):
        """Send security notification"""
        logger.warning(f"Security notification sent for emergency request {request.id}")
        request.context["security_notification_sent"] = True

    def _generate_symbolic_response(self, request: ConsentRequest) -> list[str]:
        """Generate symbolic response based on decision"""
        if request.escalation_level:
            # Use escalation rule's symbolic response
            for rule in self.escalation_rules:
                if rule.escalation_level == request.escalation_level and rule.enabled:
                    return rule.symbolic_response

        # Default symbolic responses based on status
        if request.status == ConsentStatus.GRANTED:
            return ["✅", "🔓", "🤝"]
        elif request.status == ConsentStatus.DENIED:
            return ["❌", "🔒", "🛡️"]
        elif request.status == ConsentStatus.PENDING:
            return ["⏳", "🔍", "📋"]
        elif request.status == ConsentStatus.ESCALATED:
            return ["⬆️", "👤", "📋"]
        else:
            return ["❓", "⚠️", "🔍"]

    async def _log_consent_decision(self, request: ConsentRequest):
        """Log the consent decision to history"""
        log_entry = {
            "request_id": request.id,
            "requester": request.requester,
            "target_resource": request.target_resource,
            "permission_type": request.permission_type,
            "requested_at": request.requested_at,
            "status": request.status.value,
            "trust_score": request.trust_score,
            "decision_reason": request.decision_reason,
            "escalation_level": (request.escalation_level.name if request.escalation_level else None),
            "symbolic_path": request.symbolic_path,
            "processed_at": time.time(),
        }

        self.consent_history.append(log_entry)

        # Save to file
        try:
            self.consent_log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.consent_log_file, "w") as f:
                json.dump(self.consent_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save consent history: {e}")

    async def revoke_consent(self, request_id: str, reason: str = "User revoked") -> bool:
        """Revoke a previously granted consent"""
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            request.status = ConsentStatus.REVOKED
            request.decision_reason = reason

            await self._log_consent_decision(request)

            logger.info(f"Consent revoked for request {request_id}: {reason}")
            return True

        return False

    def get_requester_trust_summary(self, requester: str) -> dict:
        """Get trust summary for a requester"""
        stats = self.requester_stats.get(requester, {})

        if not stats:
            return {"error": "No data available for requester"}

        # Calculate trust trend
        trust_trend = stats.get("trust_trend", [])
        if len(trust_trend) >= 2:
            recent_trend = trust_trend[-5:]  # Last 5 requests
            trend_direction = "stable"
            if len(recent_trend) >= 2:
                if recent_trend[-1] > recent_trend[0] + 0.1:
                    trend_direction = "improving"
                elif recent_trend[-1] < recent_trend[0] - 0.1:
                    trend_direction = "declining"
        else:
            trend_direction = "insufficient_data"

        return {
            "requester": requester,
            "total_requests": stats["total_requests"],
            "success_rate": stats["granted"] / max(1, stats["total_requests"]),
            "denial_rate": stats["denied"] / max(1, stats["total_requests"]),
            "escalation_rate": stats["escalated"] / max(1, stats["total_requests"]),
            "current_trust_score": trust_trend[-1] if trust_trend else 0.5,
            "trust_trend": trend_direction,
            "last_request_age": (time.time() - stats["last_request"] if stats["last_request"] else None),
        }


async def main():
    """Demo of consent escalation resolver"""
    resolver = ConsentEscalationResolver()

    # Create sample consent requests
    sample_requests = [
        ConsentRequest(
            id=str(uuid.uuid4()),
            requester="alice@example.com",
            target_resource="/api/user/data",
            permission_type="read",
            requested_at=time.time(),
            expires_at=time.time() + 3600,
            context={"verified_identity": True},
            symbolic_path=["🔐", "👤"],
            trust_score=0.8,
        ),
        ConsentRequest(
            id=str(uuid.uuid4()),
            requester="unknown_user",
            target_resource="/admin/critical",
            permission_type="admin",
            requested_at=time.time(),
            expires_at=time.time() + 1800,
            context={},
            symbolic_path=["❓"],
            trust_score=0.2,
        ),
        ConsentRequest(
            id=str(uuid.uuid4()),
            requester="emergency_system",
            target_resource="/emergency/access",
            permission_type="emergency",
            requested_at=time.time(),
            expires_at=time.time() + 300,
            context={"emergency": True},
            symbolic_path=["🚨"],
            trust_score=0.6,
        ),
    ]

    # Process requests
    for request in sample_requests:
        print(f"\n🔍 Processing consent request: {request.id}")
        print(f"   Requester: {request.requester}")
        print(f"   Resource: {request.target_resource}")
        print(f"   Permission: {request.permission_type}")
        print(f"   Initial Trust: {request.trust_score:.2f}")

        processed_request = await resolver.process_consent_request(request)

        print(f"   Final Status: {processed_request.status.value}")
        print(f"   Final Trust: {processed_request.trust_score:.2f}")
        print(f"   Reason: {processed_request.decision_reason}")
        if processed_request.escalation_level:
            print(f"   Escalation: {processed_request.escalation_level.name}")
        print(f"   Symbolic Path: {'→'.join(processed_request.symbolic_path)}")

        # Show trust summary
        trust_summary = resolver.get_requester_trust_summary(request.requester)
        print(f"   Trust Summary: {trust_summary}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛡️ Consent Escalation Resolver demo stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)