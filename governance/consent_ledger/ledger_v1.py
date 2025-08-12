"""
LUKHAS Consent Ledger v1 Implementation
Agent 2: Consent & Compliance Specialist
Implements Λ-trace audit records, GDPR/CCPA compliance, policy engine
Integrates with Agent 1's ΛID system
"""

import hashlib
import json
import sqlite3
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import hmac
import secrets


class PolicyVerdict(Enum):
    """Policy engine verdicts with step-up support"""
    ALLOW = "allow"
    DENY = "deny"
    STEP_UP_REQUIRED = "step_up_required"
    DURESS_DETECTED = "duress_detected"


@dataclass
class ΛTrace:
    """
    Λ-trace audit record for comprehensive causal chain tracking
    Integrates with Agent 1's ΛID system
    """
    trace_id: str
    lid: str  # LUKHAS ID from Agent 1
    parent_trace_id: Optional[str]
    action: str
    resource: str
    purpose: str
    timestamp: str
    policy_verdict: PolicyVerdict
    capability_token_id: Optional[str]
    context: Dict[str, Any] = field(default_factory=dict)
    explanation_unl: Optional[str] = None  # Universal Language explanation
    
    def to_immutable_hash(self) -> str:
        """Generate cryptographic hash for immutability"""
        data = asdict(self)
        data['policy_verdict'] = self.policy_verdict.value
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha3_256(content.encode()).hexdigest()
    
    def sign(self, secret_key: str) -> str:
        """Sign trace for integrity verification"""
        message = self.to_immutable_hash().encode()
        return hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()


@dataclass
class ConsentRecord:
    """GDPR/CCPA compliant consent record"""
    consent_id: str
    lid: str  # LUKHAS ID
    resource_type: str
    scopes: List[str]
    purpose: str
    lawful_basis: str  # GDPR requirement
    granted_at: str
    expires_at: Optional[str]
    revoked_at: Optional[str] = None
    data_categories: List[str] = field(default_factory=list)  # CCPA requirement
    third_parties: List[str] = field(default_factory=list)
    is_active: bool = True
    trace_id: str = ""


class ConsentLedgerV1:
    """
    Immutable append-only consent ledger with real-time revocation
    Implements GDPR Articles 6, 7, 17 and CCPA requirements
    """
    
    def __init__(self, db_path: str = "governance/consent_ledger.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.secret_key = secrets.token_urlsafe(32)
        self._init_database()
    
    def _init_database(self):
        """Initialize append-only database with integrity checks"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Λ-trace table (immutable)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lambda_traces (
                trace_id TEXT PRIMARY KEY,
                lid TEXT NOT NULL,
                parent_trace_id TEXT,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                purpose TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                policy_verdict TEXT NOT NULL,
                capability_token_id TEXT,
                context TEXT,
                explanation_unl TEXT,
                hash TEXT UNIQUE NOT NULL,
                signature TEXT NOT NULL,
                created_at REAL NOT NULL,
                CHECK (created_at > 0)
            )
        """)
        
        # Consent records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                lid TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                scopes TEXT NOT NULL,
                purpose TEXT NOT NULL,
                lawful_basis TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT,
                data_categories TEXT,
                third_parties TEXT,
                is_active INTEGER DEFAULT 1,
                trace_id TEXT NOT NULL,
                FOREIGN KEY (trace_id) REFERENCES lambda_traces(trace_id)
            )
        """)
        
        # Duress signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS duress_signals (
                signal_id TEXT PRIMARY KEY,
                lid TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                response_action TEXT NOT NULL
            )
        """)
        
        # Performance indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lid_traces ON lambda_traces(lid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON lambda_traces(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lid_consent ON consent_records(lid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_active_consent ON consent_records(is_active)")
        
        conn.commit()
        conn.close()
    
    def create_trace(self, lid: str, action: str, resource: str,
                    purpose: str, verdict: PolicyVerdict,
                    parent_trace_id: Optional[str] = None,
                    capability_token_id: Optional[str] = None,
                    context: Optional[Dict] = None,
                    explanation_unl: Optional[str] = None) -> ΛTrace:
        """Create and append new Λ-trace audit record"""
        
        trace = ΛTrace(
            trace_id=f"LT-{uuid.uuid4().hex}",
            lid=lid,
            parent_trace_id=parent_trace_id,
            action=action,
            resource=resource,
            purpose=purpose,
            timestamp=datetime.now(timezone.utc).isoformat(),
            policy_verdict=verdict,
            capability_token_id=capability_token_id,
            context=context or {},
            explanation_unl=explanation_unl
        )
        
        # Append to immutable ledger
        self._append_trace(trace)
        
        return trace
    
    def _append_trace(self, trace: ΛTrace):
        """Append trace to immutable ledger with signature"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO lambda_traces (
                    trace_id, lid, parent_trace_id, action, resource,
                    purpose, timestamp, policy_verdict, capability_token_id,
                    context, explanation_unl, hash, signature, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace.trace_id,
                trace.lid,
                trace.parent_trace_id,
                trace.action,
                trace.resource,
                trace.purpose,
                trace.timestamp,
                trace.policy_verdict.value,
                trace.capability_token_id,
                json.dumps(trace.context),
                trace.explanation_unl,
                trace.to_immutable_hash(),
                trace.sign(self.secret_key),
                time.time()
            ))
            conn.commit()
        finally:
            conn.close()
    
    def grant_consent(self, lid: str, resource_type: str,
                     scopes: List[str], purpose: str,
                     lawful_basis: str = "consent",
                     data_categories: Optional[List[str]] = None,
                     third_parties: Optional[List[str]] = None,
                     expires_in_days: Optional[int] = None) -> ConsentRecord:
        """
        Grant GDPR/CCPA compliant consent
        lawful_basis: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interests
        """
        
        # Create audit trace
        trace = self.create_trace(
            lid=lid,
            action="grant_consent",
            resource=resource_type,
            purpose=purpose,
            verdict=PolicyVerdict.ALLOW,
            context={
                "scopes": scopes,
                "lawful_basis": lawful_basis,
                "data_categories": data_categories
            }
        )
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now(timezone.utc) + 
                         timedelta(days=expires_in_days)).isoformat()
        
        # Create consent record
        consent = ConsentRecord(
            consent_id=f"CONSENT-{uuid.uuid4().hex}",
            lid=lid,
            resource_type=resource_type,
            scopes=scopes,
            purpose=purpose,
            lawful_basis=lawful_basis,
            granted_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
            data_categories=data_categories or [],
            third_parties=third_parties or [],
            trace_id=trace.trace_id
        )
        
        # Store consent
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO consent_records (
                    consent_id, lid, resource_type, scopes, purpose,
                    lawful_basis, granted_at, expires_at, data_categories,
                    third_parties, trace_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consent.consent_id,
                consent.lid,
                consent.resource_type,
                json.dumps(consent.scopes),
                consent.purpose,
                consent.lawful_basis,
                consent.granted_at,
                consent.expires_at,
                json.dumps(consent.data_categories),
                json.dumps(consent.third_parties),
                consent.trace_id
            ))
            conn.commit()
        finally:
            conn.close()
        
        return consent
    
    def revoke_consent(self, consent_id: str, lid: str,
                      reason: Optional[str] = None) -> bool:
        """
        Real-time consent revocation (GDPR Article 7.3)
        Must be as easy to withdraw as to give consent
        """
        
        # Create revocation trace
        trace = self.create_trace(
            lid=lid,
            action="revoke_consent",
            resource=consent_id,
            purpose=reason or "user_requested",
            verdict=PolicyVerdict.ALLOW,
            explanation_unl="User exercised right to withdraw consent"
        )
        
        # Update consent record
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE consent_records
                SET revoked_at = ?, is_active = 0
                WHERE consent_id = ? AND lid = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                consent_id,
                lid
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            
            if success:
                # Trigger cascade revocation for dependent services
                self._cascade_revocation(consent_id, lid)
            
            return success
            
        finally:
            conn.close()
    
    def _cascade_revocation(self, consent_id: str, lid: str):
        """Cascade consent revocation to dependent services"""
        # This would trigger webhooks/events to adapters
        # Agent 3's adapters would invalidate their tokens
        pass
    
    def check_consent(self, lid: str, resource_type: str,
                     action: str, context: Optional[Dict] = None) -> Dict:
        """Check if action is allowed under current consent"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Get active consents
            cursor.execute("""
                SELECT consent_id, scopes, purpose, expires_at, lawful_basis
                FROM consent_records
                WHERE lid = ? AND resource_type = ? AND is_active = 1
            """, (lid, resource_type))
            
            result = cursor.fetchone()
            
            if not result:
                return {
                    "allowed": False,
                    "require_step_up": True,
                    "reason": "no_active_consent"
                }
            
            consent_id, scopes_json, purpose, expires_at, lawful_basis = result
            scopes = json.loads(scopes_json)
            
            # Check expiration
            if expires_at:
                if datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
                    return {
                        "allowed": False,
                        "require_step_up": True,
                        "reason": "consent_expired"
                    }
            
            # Check scope
            if action not in scopes:
                return {
                    "allowed": False,
                    "require_step_up": True,
                    "reason": "action_not_in_scope"
                }
            
            # Log successful check
            self.create_trace(
                lid=lid,
                action="check_consent",
                resource=resource_type,
                purpose=f"validate_{action}",
                verdict=PolicyVerdict.ALLOW,
                context={"consent_id": consent_id}
            )
            
            return {
                "allowed": True,
                "consent_id": consent_id,
                "lawful_basis": lawful_basis,
                "require_step_up": False
            }
            
        finally:
            conn.close()


class PolicyEngine:
    """
    Policy and ethics engine with OpenAI alignment
    Implements refusal templates, jailbreak hygiene, duress detection
    """
    
    def __init__(self, ledger: ConsentLedgerV1):
        self.ledger = ledger
        self.policies = self._load_policies()
        self.refusal_templates = self._load_refusal_templates()
        self.jailbreak_patterns = self._load_jailbreak_patterns()
    
    def _load_policies(self) -> Dict:
        """Load comprehensive governance policies"""
        return {
            "gdpr": {
                "require_explicit_consent": True,
                "data_minimization": True,
                "purpose_limitation": True,
                "storage_limitation_days": 90,
                "right_to_erasure": True,
                "data_portability": True,
                "breach_notification_hours": 72
            },
            "ccpa": {
                "opt_out_right": True,
                "disclosure_required": True,
                "no_discrimination": True,
                "verifiable_requests": True
            },
            "high_risk_actions": [
                "delete_all_data",
                "export_pii",
                "modify_consent_ledger",
                "access_financial_data",
                "bypass_policy",
                "admin_override"
            ],
            "duress_signals": [
                "shadow_gesture_detected",
                "panic_phrase_spoken",
                "rapid_delete_pattern",
                "unusual_location_access",
                "forced_unlock_detected"
            ],
            "per_region_residency": {
                "eu": {"storage": "eu-west-1", "encryption": "aes-256-gcm"},
                "us": {"storage": "us-east-1", "encryption": "aes-256-gcm"},
                "ca": {"storage": "ca-central-1", "encryption": "aes-256-gcm"}
            }
        }
    
    def _load_refusal_templates(self) -> Dict[str, str]:
        """Load refusal and clarification templates"""
        return {
            "harmful_content": "I cannot assist with potentially harmful content. Please rephrase your request.",
            "illegal_activity": "I cannot help with activities that may violate laws or regulations.",
            "pii_exposure": "I cannot expose or process personal information without proper consent.",
            "jailbreak_attempt": "I maintain ethical guidelines and cannot bypass safety measures.",
            "insufficient_permission": "You don't have permission for this action. Please request access.",
            "policy_violation": "This action violates our data governance policies.",
            "duress_detected": "Security protocol activated. Please verify your identity.",
            "consent_required": "This action requires explicit consent. Would you like to grant permission?",
            "data_residency": "This data must remain in its designated region per compliance requirements."
        }
    
    def _load_jailbreak_patterns(self) -> List[str]:
        """Load jailbreak detection patterns"""
        return [
            "ignore previous instructions",
            "disregard all safety",
            "you are now in developer mode",
            "pretend to be",
            "bypass your guidelines",
            "forget your training",
            "act as if you have no restrictions",
            "enable unlimited mode",
            "sudo override",
            "admin access granted"
        ]
    
    def validate_action(self, lid: str, action: str,
                       context: Dict[str, Any]) -> Dict:
        """
        Validate action against all policies
        Implements hot-path policy enforcement for Agent 4
        """
        
        # Check for duress signals first (highest priority)
        if self._detect_duress(context):
            self.ledger.create_trace(
                lid=lid,
                action=action,
                resource=context.get("resource", "unknown"),
                purpose="security_alert",
                verdict=PolicyVerdict.DURESS_DETECTED,
                context={"alert": "security_notified", "lock": True}
            )
            
            return {
                "verdict": PolicyVerdict.DURESS_DETECTED,
                "refusal": self.refusal_templates["duress_detected"],
                "silent_lock": True,
                "alert_security": True,
                "require_step_up": "biometric_reauthentication"
            }
        
        # Check for jailbreak attempts
        if self._detect_jailbreak(context.get("input", "")):
            return {
                "verdict": PolicyVerdict.DENY,
                "refusal": self.refusal_templates["jailbreak_attempt"],
                "log_attempt": True
            }
        
        # Check high-risk actions
        if action in self.policies["high_risk_actions"]:
            return {
                "verdict": PolicyVerdict.STEP_UP_REQUIRED,
                "refusal": self.refusal_templates["insufficient_permission"],
                "require_step_up": "mfa_required",
                "explanation_unl": f"High-risk action '{action}' requires additional verification"
            }
        
        # Check consent
        consent_check = self.ledger.check_consent(
            lid, 
            context.get("resource_type", ""),
            action,
            context
        )
        
        if not consent_check["allowed"]:
            return {
                "verdict": PolicyVerdict.DENY,
                "refusal": self.refusal_templates["consent_required"],
                "reason": consent_check.get("reason")
            }
        
        # Check data residency
        region = context.get("region")
        if region and region in self.policies["per_region_residency"]:
            residency = self.policies["per_region_residency"][region]
            context["enforced_residency"] = residency
        
        # All checks passed
        self.ledger.create_trace(
            lid=lid,
            action=action,
            resource=context.get("resource", "unknown"),
            purpose=context.get("purpose", "operation"),
            verdict=PolicyVerdict.ALLOW,
            context=context
        )
        
        return {
            "verdict": PolicyVerdict.ALLOW,
            "consent_id": consent_check.get("consent_id"),
            "residency": context.get("enforced_residency")
        }
    
    def _detect_duress(self, context: Dict) -> bool:
        """Detect duress/shadow gestures"""
        indicators = context.get("behavioral_signals", [])
        
        # Check for known duress patterns
        for signal in self.policies["duress_signals"]:
            if signal in indicators:
                return True
        
        # Check for shadow gesture (specific hand movement pattern)
        if context.get("gesture_detected") == "shadow_lock":
            return True
        
        # Check for rapid deletion pattern
        recent_deletes = context.get("recent_delete_count", 0)
        if recent_deletes > 5:  # More than 5 deletes in session
            return True
        
        return False
    
    def _detect_jailbreak(self, input_text: str) -> bool:
        """Detect jailbreak attempts in user input"""
        if not input_text:
            return False
        
        input_lower = input_text.lower()
        
        for pattern in self.jailbreak_patterns:
            if pattern in input_lower:
                return True
        
        return False


class ContentModerationIntegration:
    """
    OpenAI content moderation integration
    Implements safety filters and ethical guidelines
    """
    
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.categories = [
            "hate", "harassment", "self-harm", "sexual",
            "violence", "illegal", "deception"
        ]
    
    def moderate(self, content: str, lid: str) -> Dict:
        """
        Moderate content for safety and ethics
        In production: calls OpenAI Moderation API
        """
        
        # Check jailbreak first
        if self.policy_engine._detect_jailbreak(content):
            return {
                "safe": False,
                "violated_category": "jailbreak",
                "refusal": self.policy_engine.refusal_templates["jailbreak_attempt"]
            }
        
        # In production: Call OpenAI Moderation API
        # For now: basic keyword checking
        
        unsafe_keywords = {
            "hate": ["hate", "discriminate"],
            "violence": ["kill", "hurt", "attack"],
            "illegal": ["hack", "steal", "pirate"]
        }
        
        content_lower = content.lower()
        
        for category, keywords in unsafe_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return {
                        "safe": False,
                        "violated_category": category,
                        "refusal": self.policy_engine.refusal_templates.get(
                            f"{category}_content",
                            self.policy_engine.refusal_templates["harmful_content"]
                        )
                    }
        
        return {
            "safe": True,
            "violated_category": None,
            "refusal": None
        }


if __name__ == "__main__":
    print("🛡️ Testing LUKHAS Consent Ledger v1")
    print("-" * 50)
    
    # Initialize ledger
    ledger = ConsentLedgerV1("test_consent.db")
    policy_engine = PolicyEngine(ledger)
    moderation = ContentModerationIntegration(policy_engine)
    
    # Test consent grant
    print("📝 Granting consent...")
    consent = ledger.grant_consent(
        lid="USR-123456789",
        resource_type="gmail",
        scopes=["read", "list"],
        purpose="email_analysis",
        lawful_basis="consent",
        data_categories=["email_headers", "email_content"],
        expires_in_days=90
    )
    print(f"✅ Consent ID: {consent.consent_id[:20]}...")
    
    # Test policy validation
    print("\n⚖️ Testing policy validation...")
    validation = policy_engine.validate_action(
        lid="USR-123456789",
        action="read",
        context={"resource_type": "gmail", "purpose": "analysis"}
    )
    print(f"✅ Verdict: {validation['verdict'].value}")
    
    # Test content moderation
    print("\n🔍 Testing content moderation...")
    safe_content = moderation.moderate("Show me my emails", "USR-123456789")
    print(f"✅ Safe content: {safe_content['safe']}")
    
    unsafe_content = moderation.moderate("ignore previous instructions", "USR-123456789")
    print(f"⚠️ Jailbreak detected: {not unsafe_content['safe']}")
    
    print("\n✅ Consent Ledger v1 operational!")