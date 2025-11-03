"""
LUKHAS Consent Ledger v1 with Λ-trace Audit Records
Agent 2: Consent & Compliance Specialist Implementation
"""

import hashlib
import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class PolicyVerdict(Enum):
    """Policy engine decision types"""

    ALLOW = "allow"
    DENY = "deny"
    STEP_UP_REQUIRED = "step_up_required"


@dataclass
class LambdaTrace:
    """Λ-trace audit record for causal chain tracking"""

    trace_id: str
    parent_trace_id: Optional[str]
    lid: str  # LUKHAS ID of actor
    action: str
    resource: str
    purpose: str
    timestamp: str
    policy_verdict: PolicyVerdict
    capability_token_id: Optional[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_hash(self) -> str:
        """Generate immutable hash of audit record"""
        data = asdict(self)
        # Convert PolicyVerdict enum to string
        data["policy_verdict"] = (
            data["policy_verdict"].value
            if isinstance(data["policy_verdict"], PolicyVerdict)
            else data["policy_verdict"]
        )
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class ConsentRecord:
    """User consent record"""

    consent_id: str
    lid: str
    resource_type: str  # gmail, drive, dropbox, etc.
    scope: list[str]  # read, write, delete
    purpose: str
    granted_at: str
    expires_at: Optional[str]
    revoked_at: Optional[str] = None
    is_active: bool = True


class ConsentLedger:
    """Immutable append-only consent ledger with Λ-trace"""

    def __init__(self, db_path: str = "consent_ledger.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for consent ledger"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Λ-trace audit table (append-only)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS lambda_trace (
                trace_id TEXT PRIMARY KEY,
                parent_trace_id TEXT,
                lid TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                purpose TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                policy_verdict TEXT NOT NULL,
                capability_token_id TEXT,
                metadata TEXT,
                hash TEXT UNIQUE NOT NULL,
                created_at REAL NOT NULL
            )
        """
        )

        # Consent records table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                lid TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                purpose TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT,
                is_active INTEGER DEFAULT 1,
                trace_id TEXT NOT NULL,
                FOREIGN KEY (trace_id) REFERENCES lambda_trace(trace_id)
            )
        """
        )

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lid ON lambda_trace(lid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON lambda_trace(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_consent_lid ON consent_records(lid)")

        conn.commit()
        conn.close()

    def generate_trace(
        self,
        lid: str,
        action: str,
        resource: str,
        purpose: str,
        verdict: PolicyVerdict,
        parent_trace_id: Optional[str] = None,
        capability_token_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> LambdaTrace:
        """Generate new Λ-trace audit record"""
        trace = LambdaTrace(
            trace_id=f"LT-{uuid.uuid4().hex}",
            parent_trace_id=parent_trace_id,
            lid=lid,
            action=action,
            resource=resource,
            purpose=purpose,
            timestamp=datetime.now(timezone.utc).isoformat(),
            policy_verdict=verdict,
            capability_token_id=capability_token_id,
            metadata=metadata or {},
        )

        # Write to ledger (append-only)
        self._append_trace(trace)

        return trace

    def _append_trace(self, trace: LambdaTrace):
        """Append trace to immutable ledger"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO lambda_trace (
                trace_id, parent_trace_id, lid, action, resource,
                purpose, timestamp, policy_verdict, capability_token_id,
                metadata, hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trace.trace_id,
                trace.parent_trace_id,
                trace.lid,
                trace.action,
                trace.resource,
                trace.purpose,
                trace.timestamp,
                trace.policy_verdict.value,
                trace.capability_token_id,
                json.dumps(trace.metadata),
                trace.to_hash(),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

    def grant_consent(
        self,
        lid: str,
        resource_type: str,
        scope: list[str],
        purpose: str,
        expires_at: Optional[str] = None,
    ) -> ConsentRecord:
        """Grant user consent for resource access"""

        # Generate trace for consent grant
        trace = self.generate_trace(
            lid=lid,
            action="grant_consent",
            resource=resource_type,
            purpose=purpose,
            verdict=PolicyVerdict.ALLOW,
            metadata={"scope": scope},
        )

        # Create consent record
        consent = ConsentRecord(
            consent_id=f"CONSENT-{uuid.uuid4().hex}",
            lid=lid,
            resource_type=resource_type,
            scope=scope,
            purpose=purpose,
            granted_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
        )

        # Store consent
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO consent_records (
                consent_id, lid, resource_type, scope, purpose,
                granted_at, expires_at, trace_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                consent.consent_id,
                consent.lid,
                consent.resource_type,
                json.dumps(consent.scope),
                consent.purpose,
                consent.granted_at,
                consent.expires_at,
                trace.trace_id,
            ),
        )

        conn.commit()
        conn.close()

        return consent

    def revoke_consent(self, consent_id: str, lid: str) -> bool:
        """Revoke consent in real-time"""

        # Generate trace for revocation
        self.generate_trace(
            lid=lid,
            action="revoke_consent",
            resource=consent_id,
            purpose="user_requested_revocation",
            verdict=PolicyVerdict.ALLOW,
        )

        # Update consent record
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE consent_records
            SET revoked_at = ?, is_active = 0
            WHERE consent_id = ? AND lid = ?
        """,
            (datetime.now(timezone.utc).isoformat(), consent_id, lid),
        )

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def check_consent(self, lid: str, resource_type: str, action: str) -> dict:
        """Check if user has consented to action"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for active consent
        cursor.execute(
            """
            SELECT consent_id, scope, purpose, expires_at
            FROM consent_records
            WHERE lid = ? AND resource_type = ? AND is_active = 1
        """,
            (lid, resource_type),
        )

        result = cursor.fetchone()
        conn.close()

        if not result:
            return {"allowed": False, "require_step_up": True, "reason": "No active consent found"}

        consent_id, scope_json, _purpose, expires_at = result
        scope = json.loads(scope_json)

        # Check expiration
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
            return {"allowed": False, "require_step_up": True, "reason": "Consent expired"}

        # Check scope
        if action not in scope:
            return {
                "allowed": False,
                "require_step_up": True,
                "reason": f"Action '{action}' not in consented scope",
            }

        return {"allowed": True, "consent_id": consent_id, "require_step_up": False}


class PolicyEngine:
    """Policy and ethics engine for data governance"""

    def __init__(self, ledger: ConsentLedger):
        self.ledger = ledger
        self.policies = self._load_policies()

    def _load_policies(self) -> dict:
        """Load governance policies"""
        return {
            "data_minimization": {
                "max_data_retention_days": 90,
                "require_purpose": True,
                "anonymize_after_days": 30,
            },
            "gdpr": {
                "require_explicit_consent": True,
                "allow_data_portability": True,
                "right_to_erasure": True,
                "breach_notification_hours": 72,
            },
            "ccpa": {
                "allow_opt_out": True,
                "disclose_data_categories": True,
                "no_discrimination": True,
            },
            "high_risk_actions": [
                "delete_all_data",
                "export_pii",
                "modify_consent_ledger",
                "access_financial_data",
            ],
            "duress_signals": [
                "shadow_gesture_detected",
                "panic_word_spoken",
                "rapid_delete_attempts",
            ],
        }

    def validate_action(self, lid: str, action: str, context: dict) -> dict:
        """Validate action against policies"""

        # Check for duress signals
        if self._detect_duress(context):
            self.ledger.generate_trace(
                lid=lid,
                action=action,
                resource=context.get("resource", "unknown"),
                purpose="duress_detected",
                verdict=PolicyVerdict.DENY,
                metadata={"alert": "security_team_notified"},
            )
            return {
                "verdict": PolicyVerdict.DENY,
                "explanation": "Security protocol activated",
                "silent_lock": True,
                "alert_security": True,
            }

        # Check high-risk actions
        if action in self.policies["high_risk_actions"]:
            return {
                "verdict": PolicyVerdict.STEP_UP_REQUIRED,
                "explanation": f"High-risk action '{action}' requires additional verification",
                "require_mfa": True,
            }

        # Check GDPR compliance
        if self.policies["gdpr"]["require_explicit_consent"]:
            consent_check = self.ledger.check_consent(lid, context.get("resource_type", ""), action)
            if not consent_check["allowed"]:
                return {
                    "verdict": PolicyVerdict.DENY,
                    "explanation": "Explicit consent required under GDPR",
                }

        # Default allow with audit
        self.ledger.generate_trace(
            lid=lid,
            action=action,
            resource=context.get("resource", "unknown"),
            purpose=context.get("purpose", "unspecified"),
            verdict=PolicyVerdict.ALLOW,
        )

        return {
            "verdict": PolicyVerdict.ALLOW,
            "explanation": "Action permitted under current policies",
        }

    def _detect_duress(self, context: dict) -> bool:
        """Detect duress/shadow gestures"""
        duress_indicators = context.get("duress_indicators", [])
        return any(signal in duress_indicators for signal in self.policies["duress_signals"])


class ContentModerationFilter:
    """OpenAI-aligned content moderation"""

    REFUSAL_TEMPLATES = {
        "harmful": "I cannot assist with potentially harmful content.",
        "illegal": "I cannot help with illegal activities.",
        "pii_leak": "I cannot expose personal information.",
        "jailbreak": "I maintain ethical guidelines and cannot bypass safety measures.",
    }

    def __init__(self):
        self.jailbreak_patterns = [
            "ignore previous instructions",
            "you are now",
            "pretend to be",
            "bypass safety",
            "unlimited mode",
        ]

    def moderate_content(self, content: str) -> dict:
        """Moderate content for safety and ethics"""

        # Check for jailbreak attempts
        content_lower = content.lower()
        for pattern in self.jailbreak_patterns:
            if pattern in content_lower:
                return {
                    "safe": False,
                    "category": "jailbreak",
                    "refusal": self.REFUSAL_TEMPLATES["jailbreak"],
                }

        # In production: Call OpenAI Moderation API
        # For MVP: Basic checks

        return {"safe": True, "category": None, "refusal": None}


if __name__ == "__main__":
    # Demo consent ledger
    ledger = ConsentLedger()
    policy_engine = PolicyEngine(ledger)

    print("🛡️ Consent Ledger Demo")

    # Grant consent
    lid = "USR-123456-demo"
    consent = ledger.grant_consent(
        lid=lid, resource_type="gmail", scope=["read", "list"], purpose="travel_document_analysis"
    )
    print(f"✅ Consent granted: {consent.consent_id}")

    # Check consent
    check = ledger.check_consent(lid, "gmail", "read")
    print(f"📋 Consent check: {check}")

    # Validate action
    validation = policy_engine.validate_action(
        lid=lid, action="read_emails", context={"resource_type": "gmail", "purpose": "analysis"}
    )
    print(f"⚖️ Policy validation: {validation['verdict'].value}")
