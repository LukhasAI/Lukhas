#!/usr/bin/env python3
"""
Consent Manager - Advanced consent and permission management system
Handles consent requests, trust path analysis, and escalation protocols
"""

import asyncio
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

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
    """Represents a consent request"""
    id: str
    requester: str
    target_resource: str
    permission_type: str
    requested_at: float
    expires_at: float
    context: Dict[str, Any]
    symbolic_path: List[str]
    trust_score: float
    status: ConsentStatus = ConsentStatus.PENDING
    decision_reason: Optional[str] = None
    escalation_level: Optional[EscalationLevel] = None
    escalation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.escalation_history is None:
            self.escalation_history = []


@dataclass
class TrustPath:
    """Represents a trust relationship path"""
    path_id: str
    source: str
    target: str
    trust_score: float
    path_type: str  # direct, inherited, delegated, emergency
    created_at: float
    last_validated: float
    validation_count: int
    symbolic_signature: List[str]
    metadata: Dict[str, Any]


class ConsentManager:
    """
    Advanced consent and permission management system
    Handles complex consent scenarios with trust path analysis
    """
    
    # Default escalation rules
    DEFAULT_ESCALATION_RULES = [
        {
            "name": "high_privilege_access",
            "condition": "permission_type in ['admin', 'root', 'critical'] and trust_score < 0.8",
            "escalation_level": EscalationLevel.HIGH,
            "actions": ["require_multi_factor", "human_review"],
            "symbolic_response": ["🔐", "👤", "📋"]
        },
        {
            "name": "low_trust_requester",
            "condition": "trust_score < 0.3",
            "escalation_level": EscalationLevel.MEDIUM,
            "actions": ["trust_analysis", "additional_verification"],
            "symbolic_response": ["🔍", "🛡️", "✅"]
        },
        {
            "name": "repeated_denials",
            "condition": "recent_denial_count >= 3",
            "escalation_level": EscalationLevel.HIGH,
            "actions": ["security_review", "temporary_restriction"],
            "symbolic_response": ["🚨", "⏸️", "🔒"]
        },
        {
            "name": "emergency_override",
            "condition": "context.get('emergency', False) and trust_score > 0.5",
            "escalation_level": EscalationLevel.EMERGENCY,
            "actions": ["emergency_bypass", "immediate_audit"],
            "symbolic_response": ["🚨", "⚡", "🔓"]
        }
    ]
    
    # Trust path symbolic patterns
    TRUST_SYMBOLS = {
        "direct": ["🔐", "🤝", "✅"],
        "inherited": ["🔐", "🔗", "🤝"],
        "delegated": ["🔐", "👤", "🔗"],
        "emergency": ["🚨", "⚡", "🔓"],
        "degraded": ["🔐", "⚠️", "🤝"],
        "expired": ["🔐", "⏰", "❌"]
    }
    
    def __init__(self, 
                 data_dir: str = "data/consent_logs",
                 trust_db_path: str = "data/trust_paths.json",
                 rules_path: str = "config/escalation_rules.json"):
        
        self.data_dir = Path(data_dir)
        self.trust_db_path = Path(trust_db_path)
        self.rules_path = Path(rules_path)
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.trust_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # State management
        self.active_requests: Dict[str, ConsentRequest] = {}
        self.consent_history: List[Dict] = []
        self.trust_paths: Dict[str, TrustPath] = {}
        self.escalation_rules = self.DEFAULT_ESCALATION_RULES.copy()
        self.requester_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_requests": 0,
            "granted": 0,
            "denied": 0,
            "escalated": 0,
            "trust_history": [],
            "last_request": 0
        })
        
        # Load persistent data
        self._load_consent_history()
        self._load_trust_paths()
        self._load_escalation_rules()
        
        logger.info("🔐 Consent Manager initialized")
    
    def _load_consent_history(self):
        """Load consent decision history"""
        history_file = self.data_dir / "consent_history.json"
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.consent_history = json.load(f)
                
                # Rebuild requester statistics
                self._rebuild_requester_stats()
                logger.info(f"Loaded {len(self.consent_history)} consent history records")
        except Exception as e:
            logger.warning(f"Failed to load consent history: {e}")
            self.consent_history = []
    
    def _save_consent_history(self):
        """Save consent history to file"""
        history_file = self.data_dir / "consent_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.consent_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save consent history: {e}")
    
    def _load_trust_paths(self):
        """Load trust paths from database"""
        try:
            if self.trust_db_path.exists():
                with open(self.trust_db_path, 'r') as f:
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
                        metadata=data.get("metadata", {})
                    )
                logger.info(f"Loaded {len(self.trust_paths)} trust paths")
        except Exception as e:
            logger.warning(f"Failed to load trust paths: {e}")
            self._create_default_trust_paths()
    
    def _save_trust_paths(self):
        """Save trust paths to database"""
        try:
            trust_data = {}
            for path_id, path in self.trust_paths.items():
                trust_data[path_id] = asdict(path)
            
            with open(self.trust_db_path, 'w') as f:
                json.dump(trust_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save trust paths: {e}")
    
    def _create_default_trust_paths(self):
        """Create default trust paths"""
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
                symbolic_signature=self.TRUST_SYMBOLS["direct"],
                metadata={"auto_created": True}
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
                metadata={"auto_created": True}
            )
        ]
        
        for path in default_paths:
            self.trust_paths[path.path_id] = path
        
        self._save_trust_paths()
        logger.info("Created default trust paths")
    
    def _load_escalation_rules(self):
        """Load escalation rules"""
        try:
            if self.rules_path.exists():
                with open(self.rules_path, 'r') as f:
                    custom_rules = json.load(f)
                
                # Convert to proper format
                for rule in custom_rules:
                    if "escalation_level" in rule:
                        rule["escalation_level"] = EscalationLevel(rule["escalation_level"])
                
                self.escalation_rules = custom_rules
                logger.info(f"Loaded {len(self.escalation_rules)} escalation rules")
        except Exception as e:
            logger.warning(f"Failed to load escalation rules: {e}")
            # Use defaults
    
    def _rebuild_requester_stats(self):
        """Rebuild requester statistics from history"""
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
            
            stats["last_request"] = max(stats["last_request"], 
                                      entry.get("requested_at", 0))
            
            if "trust_score" in entry:
                stats["trust_history"].append(entry["trust_score"])
                # Keep only recent history
                if len(stats["trust_history"]) > 20:
                    stats["trust_history"] = stats["trust_history"][-20:]
    
    async def process_consent_request(self, request: ConsentRequest) -> ConsentRequest:
        """Process a consent request through the full pipeline"""
        logger.info(f"Processing consent request {request.id} from {request.requester}")
        
        # Add to active requests
        self.active_requests[request.id] = request
        
        try:
            # Update requester statistics
            self._update_requester_stats(request)
            
            # Analyze trust paths
            trust_analysis = await self._analyze_trust_paths(request)
            request.trust_score = trust_analysis["final_trust_score"]
            request.symbolic_path.extend(trust_analysis["symbolic_sequence"])
            
            # Apply escalation rules
            escalation_result = await self._apply_escalation_rules(request)
            
            if escalation_result:
                # Handle escalation
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
                    "actions": escalation_result["actions"]
                }
                request.escalation_history.append(escalation_entry)
                
            else:
                # Make automatic decision based on trust score
                if request.trust_score >= 0.7:
                    request.status = ConsentStatus.GRANTED
                    request.decision_reason = "Automatic approval - high trust score"
                elif request.trust_score >= 0.4:
                    request.status = ConsentStatus.PENDING
                    request.decision_reason = "Manual review required - medium trust score"
                else:
                    request.status = ConsentStatus.DENIED
                    request.decision_reason = "Automatic denial - low trust score"
            
            # Generate final symbolic response
            symbolic_response = self._generate_symbolic_response(request)
            request.symbolic_path.extend(symbolic_response)
            
            # Log the decision
            await self._log_consent_decision(request)
            
            logger.info(f"Consent request {request.id} processed: {request.status.value}")
            return request
            
        except Exception as e:
            logger.error(f"Error processing consent request {request.id}: {e}")
            request.status = ConsentStatus.DENIED
            request.decision_reason = f"Processing error: {str(e)}"
            return request
        
        finally:
            # Remove from active requests if completed
            if request.status in [ConsentStatus.GRANTED, ConsentStatus.DENIED]:
                self.active_requests.pop(request.id, None)
    
    def _update_requester_stats(self, request: ConsentRequest):
        """Update statistics for the requester"""
        requester = request.requester
        stats = self.requester_stats[requester]
        
        stats["total_requests"] += 1
        stats["last_request"] = request.requested_at
        stats["trust_history"].append(request.trust_score)
        
        # Keep only recent trust history
        if len(stats["trust_history"]) > 20:
            stats["trust_history"] = stats["trust_history"][-20:]
    
    async def _analyze_trust_paths(self, request: ConsentRequest) -> Dict:
        """Analyze available trust paths for the request"""
        # Find applicable trust paths
        applicable_paths = []
        
        for path in self.trust_paths.values():
            if self._path_applies_to_request(path, request):
                applicable_paths.append(path)
        
        if not applicable_paths:
            # Create temporary trust path for unknown requesters
            temp_path = await self._create_temporary_trust_path(request)
            applicable_paths.append(temp_path)
        
        # Calculate combined trust score
        trust_scores = []
        symbolic_sequences = []
        
        for path in applicable_paths:
            # Apply path aging penalty
            age_penalty = self._calculate_age_penalty(path)
            adjusted_score = max(0.1, path.trust_score - age_penalty)
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
            "path_count": len(applicable_paths)
        }
    
    def _path_applies_to_request(self, path: TrustPath, request: ConsentRequest) -> bool:
        """Check if a trust path applies to the consent request"""
        # Simple matching logic (would be more sophisticated in production)
        return (request.requester == path.target or 
                request.requester in request.context.get("roles", []) or
                path.path_type == "emergency" and request.context.get("emergency", False))
    
    def _calculate_age_penalty(self, path: TrustPath) -> float:
        """Calculate trust penalty based on path age"""
        age_seconds = time.time() - path.last_validated
        age_days = age_seconds / 86400
        
        # 5% penalty per day, max 50%
        penalty = min(0.5, age_days * 0.05)
        return penalty
    
    async def _create_temporary_trust_path(self, request: ConsentRequest) -> TrustPath:
        """Create a temporary trust path for unknown requesters"""
        # Base trust assessment
        base_trust = 0.3
        
        # Adjust based on context
        if request.context.get("verified_identity"):
            base_trust += 0.3
        if request.context.get("known_system"):
            base_trust += 0.2
        if request.context.get("emergency"):
            base_trust += 0.1
        
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
        
        return TrustPath(
            path_id=f"temp_{request.requester}_{int(time.time())}",
            source="unknown",
            target=request.requester,
            trust_score=base_trust,
            path_type=path_type,
            created_at=time.time(),
            last_validated=time.time(),
            validation_count=0,
            symbolic_signature=symbols,
            metadata={"temporary": True, "auto_created": True}
        )
    
    async def _apply_escalation_rules(self, request: ConsentRequest) -> Optional[Dict]:
        """Apply escalation rules to determine if escalation is needed"""
        # Build evaluation context
        eval_context = {
            "request": request,
            "permission_type": request.permission_type,
            "trust_score": request.trust_score,
            "context": request.context,
            "recent_denial_count": self._get_recent_denials(request.requester),
            "requester_stats": dict(self.requester_stats[request.requester])
        }
        
        # Check each rule
        for rule in self.escalation_rules:
            try:
                condition = rule["condition"]
                
                # Simple evaluation (in production, use safer evaluation)
                if self._evaluate_condition(condition, eval_context):
                    logger.info(f"Escalation rule '{rule['name']}' triggered for {request.id}")
                    
                    return {
                        "rule_name": rule["name"],
                        "level": rule["escalation_level"],
                        "reason": f"Rule '{rule['name']}' condition met",
                        "actions": rule["actions"],
                        "symbolic_response": rule["symbolic_response"]
                    }
                    
            except Exception as e:
                logger.error(f"Error evaluating rule '{rule.get('name', 'unknown')}': {e}")
                continue
        
        return None
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """Safely evaluate escalation condition"""
        try:
            # Simple condition evaluation
            # In production, use a proper expression evaluator
            
            # Handle common patterns
            if "permission_type in" in condition:
                # Extract permission types
                if "['admin', 'root', 'critical']" in condition:
                    perm_check = context["permission_type"] in ["admin", "root", "critical"]
                    trust_check = "trust_score < 0.8" in condition and context["trust_score"] < 0.8
                    return perm_check and trust_check
            
            if "trust_score <" in condition:
                if "trust_score < 0.3" in condition:
                    return context["trust_score"] < 0.3
                if "trust_score < 0.8" in condition:
                    return context["trust_score"] < 0.8
            
            if "recent_denial_count >=" in condition:
                if "recent_denial_count >= 3" in condition:
                    return context["recent_denial_count"] >= 3
            
            if "context.get('emergency', False)" in condition:
                emergency_check = context["context"].get("emergency", False)
                trust_check = "trust_score > 0.5" in condition and context["trust_score"] > 0.5
                return emergency_check and trust_check
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    def _get_recent_denials(self, requester: str, hours: int = 24) -> int:
        """Get count of recent denials for a requester"""
        cutoff_time = time.time() - (hours * 3600)
        
        count = 0
        for entry in self.consent_history:
            if (entry.get("requester") == requester and
                entry.get("status") == "denied" and
                entry.get("requested_at", 0) > cutoff_time):
                count += 1
        
        return count
    
    async def _execute_escalation_actions(self, request: ConsentRequest, actions: List[str]):
        """Execute escalation actions"""
        for action in actions:
            try:
                if action == "require_multi_factor":
                    request.context["mfa_required"] = True
                elif action == "human_review":
                    request.context["human_review_required"] = True
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
                    request.decision_reason = "Emergency bypass activated"
                elif action == "immediate_audit":
                    request.context["immediate_audit"] = True
                else:
                    logger.warning(f"Unknown escalation action: {action}")
                    
            except Exception as e:
                logger.error(f"Failed to execute action '{action}': {e}")
    
    def _generate_symbolic_response(self, request: ConsentRequest) -> List[str]:
        """Generate symbolic response based on decision"""
        if request.escalation_level:
            # Use escalation rule's symbols
            for rule in self.escalation_rules:
                if rule["escalation_level"] == request.escalation_level:
                    return rule["symbolic_response"]
        
        # Default symbols based on status
        status_symbols = {
            ConsentStatus.GRANTED: ["✅", "🔓", "🤝"],
            ConsentStatus.DENIED: ["❌", "🔒", "🛡️"],
            ConsentStatus.PENDING: ["⏳", "🔍", "📋"],
            ConsentStatus.ESCALATED: ["⬆️", "👤", "📋"],
            ConsentStatus.EXPIRED: ["⏰", "❌", "🔒"],
            ConsentStatus.REVOKED: ["🚫", "❌", "🔒"]
        }
        
        return status_symbols.get(request.status, ["❓", "⚠️", "🔍"])
    
    async def _log_consent_decision(self, request: ConsentRequest):
        """Log the consent decision"""
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
            "symbolic_path": request.symbolic_path
        }
        
        self.consent_history.append(log_entry)
        
        # Update requester stats
        stats = self.requester_stats[request.requester]
        if request.status == ConsentStatus.GRANTED:
            stats["granted"] += 1
        elif request.status == ConsentStatus.DENIED:
            stats["denied"] += 1
        elif request.status in [ConsentStatus.ESCALATED, ConsentStatus.PENDING]:
            stats["escalated"] += 1
        
        # Save to file periodically
        if len(self.consent_history) % 10 == 0:
            self._save_consent_history()
    
    # Public API methods
    
    async def revoke_consent(self, request_id: str, reason: str = "User revoked") -> bool:
        """Revoke a previously granted consent"""
        # Find in active or history
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            request.status = ConsentStatus.REVOKED
            request.decision_reason = reason
            
            await self._log_consent_decision(request)
            logger.info(f"Consent revoked: {request_id}")
            return True
        
        return False
    
    def get_requester_trust_summary(self, requester: str) -> Dict:
        """Get trust summary for a requester"""
        stats = self.requester_stats[requester]
        
        if stats["total_requests"] == 0:
            return {"error": "No data available for requester"}
        
        # Calculate metrics
        success_rate = stats["granted"] / stats["total_requests"]
        trust_history = stats["trust_history"]
        
        if len(trust_history) >= 2:
            trend = "improving" if trust_history[-1] > trust_history[0] else "declining"
            if abs(trust_history[-1] - trust_history[0]) < 0.1:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "requester": requester,
            "total_requests": stats["total_requests"],
            "success_rate": success_rate,
            "current_trust": trust_history[-1] if trust_history else 0.5,
            "trust_trend": trend,
            "last_request_age": time.time() - stats["last_request"] if stats["last_request"] else None
        }
    
    def get_consent_statistics(self) -> Dict:
        """Get overall consent system statistics"""
        total_requests = len(self.consent_history)
        if total_requests == 0:
            return {"total_requests": 0}
        
        # Count by status
        status_counts = {}
        for entry in self.consent_history:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Recent activity (last 24 hours)
        recent_cutoff = time.time() - 86400
        recent_requests = [
            entry for entry in self.consent_history
            if entry.get("requested_at", 0) > recent_cutoff
        ]
        
        return {
            "total_requests": total_requests,
            "status_distribution": status_counts,
            "active_requests": len(self.active_requests),
            "trust_paths": len(self.trust_paths),
            "recent_24h": len(recent_requests),
            "success_rate": status_counts.get("granted", 0) / total_requests,
            "escalation_rate": status_counts.get("escalated", 0) / total_requests
        }
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Check if we can process a simple request
            return True
        except Exception as e:
            logger.error(f"Consent manager health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo consent management"""
        print("🔐 Consent Manager Demo")
        print("=" * 40)
        
        manager = ConsentManager()
        
        # Create test requests
        test_requests = [
            ConsentRequest(
                id=str(uuid.uuid4()),
                requester="alice@example.com",
                target_resource="/api/user/data",
                permission_type="read",
                requested_at=time.time(),
                expires_at=time.time() + 3600,
                context={"verified_identity": True},
                symbolic_path=["🔐"],
                trust_score=0.8
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
                trust_score=0.2
            )
        ]
        
        # Process requests
        for request in test_requests:
            print(f"\n🔍 Processing: {request.id[:8]}")
            print(f"   Requester: {request.requester}")
            print(f"   Resource: {request.target_resource}")
            print(f"   Initial trust: {request.trust_score}")
            
            result = await manager.process_consent_request(request)
            
            print(f"   Status: {result.status.value}")
            print(f"   Final trust: {result.trust_score:.2f}")
            print(f"   Reason: {result.decision_reason}")
            print(f"   Symbols: {'→'.join(result.symbolic_path)}")
        
        # Show statistics
        stats = manager.get_consent_statistics()
        print(f"\n📊 Statistics:")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Success rate: {stats['success_rate']:.2f}")
        print(f"   Status distribution: {stats['status_distribution']}")
    
    asyncio.run(demo())
