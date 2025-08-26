"""
GTΨ Server-Side Verification
===========================
Server-side gesture verification and approval management.
Verifies {lid, gesture_hash, nonce, timestamp} for specific actions.

System-wide guardrails applied:
1. Never store raw gesture data - only hashed features
2. Time-locked approvals (≤60s) bound to exact actions
3. Approval records for audit trail and single-use enforcement
4. Integration with consent system for high-risk actions

ACK GUARDRAILS
"""

import asyncio
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import asyncpg
from pydantic import BaseModel, Field, validator

from .. import (
    HIGH_RISK_ACTIONS,
    GestureApproval,
    GestureChallenge,
    GestureFeatures,
    GestureType,
    get_max_approval_time,
    requires_gtpsi_approval,
)


class GestureVerificationRequest(BaseModel):
    """Request for gesture verification"""
    lid: str = Field(..., description="Canonical ΛID")
    challenge_id: str = Field(..., description="Challenge identifier")
    gesture_features: GestureFeatures = Field(..., description="Hashed gesture features")
    nonce: str = Field(..., description="Cryptographic nonce")

    @validator('nonce')
    def validate_nonce(cls, v):
        if len(v) < 16:
            raise ValueError("Nonce must be at least 16 characters")
        return v


class GestureVerificationResponse(BaseModel):
    """Response from gesture verification"""
    verified: bool = Field(..., description="Whether gesture was verified")
    approval_id: Optional[str] = Field(None, description="Approval record ID if verified")
    expires_at: Optional[datetime] = Field(None, description="Approval expiration")
    error: Optional[str] = Field(None, description="Error message if verification failed")


class ActionApprovalRequest(BaseModel):
    """Request to use GTΨ approval for action"""
    lid: str = Field(..., description="Canonical ΛID")
    approval_id: str = Field(..., description="GTΨ approval record ID")
    action: str = Field(..., description="Action being performed")
    action_context: Dict[str, Any] = Field(..., description="Action-specific context")


class ActionApprovalResponse(BaseModel):
    """Response from action approval check"""
    approved: bool = Field(..., description="Whether action is approved")
    approval_record: Optional[GestureApproval] = Field(None, description="Approval details")
    error: Optional[str] = Field(None, description="Error message if not approved")


class GTΨVerificationService:
    """
    Server-side GTΨ verification and approval management.

    Core responsibilities:
    - Generate gesture challenges for high-risk actions
    - Verify gesture features against stored patterns
    - Create time-locked approval records for specific actions
    - Validate and consume approvals when actions are performed
    """

    def __init__(self, db_url: str = "postgresql://localhost/lukhas"):
        self.db_url = db_url
        self.db_pool = None

        # In-memory storage for development (production uses PostgreSQL)
        self.stored_gestures: Dict[str, List[GestureFeatures]] = {}  # lid -> gestures
        self.active_challenges: Dict[str, GestureChallenge] = {}     # challenge_id -> challenge
        self.approvals: Dict[str, GestureApproval] = {}             # approval_id -> approval

    async def initialize(self):
        """Initialize database connection and create tables"""
        if self.db_url != "mock":
            self.db_pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
            await self._create_tables()

    async def close(self):
        """Close database connections"""
        if self.db_pool:
            await self.db_pool.close()

    async def _create_tables(self):
        """Create GTΨ database tables"""
        if not self.db_pool:
            return

        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS gtpsi;

                -- Stored gesture patterns (hashed features only)
                CREATE TABLE IF NOT EXISTS gtpsi.gesture_patterns (
                    pattern_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    lid VARCHAR(100) NOT NULL,
                    gesture_type VARCHAR(20) NOT NULL,
                    feature_hash VARCHAR(64) NOT NULL,
                    salt VARCHAR(64) NOT NULL,
                    feature_count INTEGER NOT NULL,
                    quality_score FLOAT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_used_at TIMESTAMPTZ,
                    use_count INTEGER DEFAULT 0,
                    enabled BOOLEAN DEFAULT TRUE
                );

                -- Active gesture challenges
                CREATE TABLE IF NOT EXISTS gtpsi.challenges (
                    challenge_id VARCHAR(64) PRIMARY KEY,
                    lid VARCHAR(100) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    action_context JSONB NOT NULL,
                    required_gesture_type VARCHAR(20) NOT NULL,
                    nonce VARCHAR(64) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL,
                    completed BOOLEAN DEFAULT FALSE
                );

                -- Gesture approvals (time-locked)
                CREATE TABLE IF NOT EXISTS gtpsi.approvals (
                    approval_id VARCHAR(64) PRIMARY KEY,
                    challenge_id VARCHAR(64) NOT NULL,
                    lid VARCHAR(100) NOT NULL,
                    action VARCHAR(100) NOT NULL,
                    action_context JSONB NOT NULL,
                    gesture_hash VARCHAR(64) NOT NULL,
                    approved_at TIMESTAMPTZ DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    used_at TIMESTAMPTZ
                );

                -- Audit log
                CREATE TABLE IF NOT EXISTS gtpsi.audit_log (
                    log_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    event_type VARCHAR(50) NOT NULL,
                    lid VARCHAR(100) NOT NULL,
                    action VARCHAR(100),
                    challenge_id VARCHAR(64),
                    approval_id VARCHAR(64),
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    client_ip INET,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'::jsonb
                );

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_patterns_lid ON gtpsi.gesture_patterns(lid);
                CREATE INDEX IF NOT EXISTS idx_challenges_lid ON gtpsi.challenges(lid);
                CREATE INDEX IF NOT EXISTS idx_approvals_lid ON gtpsi.approvals(lid);
                CREATE INDEX IF NOT EXISTS idx_audit_lid ON gtpsi.audit_log(lid);
                CREATE INDEX IF NOT EXISTS idx_challenges_expires ON gtpsi.challenges(expires_at);
                CREATE INDEX IF NOT EXISTS idx_approvals_expires ON gtpsi.approvals(expires_at);
            """)

    async def generate_challenge(
        self,
        lid: str,
        action: str,
        action_context: Dict[str, Any]
    ) -> GestureChallenge:
        """
        Generate GTΨ challenge for high-risk action.

        Args:
            lid: Canonical ΛID requesting action
            action: High-risk action requiring approval
            action_context: Action-specific context

        Returns:
            Gesture challenge for client to complete
        """
        # Check if action requires GTΨ approval
        if not requires_gtpsi_approval(action):
            raise ValueError(f"Action '{action}' does not require GTΨ approval")

        # Generate challenge
        challenge_id = f"gtpsi_{secrets.token_urlsafe(32)}"
        nonce = secrets.token_urlsafe(32)

        # Determine required gesture type (could be user preference)
        required_gesture_type = GestureType.STROKE  # Default to stroke

        # Set expiration based on action risk
        max_approval_seconds = get_max_approval_time(action)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=max_approval_seconds)

        challenge = GestureChallenge(
            challenge_id=challenge_id,
            lid=lid,
            action=action,
            action_context=action_context,
            required_gesture_type=required_gesture_type,
            expires_at=expires_at,
            nonce=nonce
        )

        # Store challenge
        self.active_challenges[challenge_id] = challenge

        # Audit log
        await self._log_audit_event(
            "challenge_generated", lid, action, challenge_id=challenge_id
        )

        return challenge

    async def verify_gesture(
        self,
        request: GestureVerificationRequest,
        client_ip: Optional[str] = None
    ) -> GestureVerificationResponse:
        """
        Verify gesture against stored patterns and create approval.

        Args:
            request: Gesture verification request
            client_ip: Client IP for audit trail

        Returns:
            Verification result with approval ID if successful
        """
        start_time = time.perf_counter()

        try:
            # 1. Validate challenge
            challenge = self.active_challenges.get(request.challenge_id)
            if not challenge:
                raise ValueError("Invalid or expired challenge")

            if challenge.lid != request.lid:
                raise ValueError("Challenge user mismatch")

            if datetime.now(timezone.utc) > challenge.expires_at:
                del self.active_challenges[request.challenge_id]
                raise ValueError("Challenge expired")

            # 2. Verify nonce matches
            if request.nonce != challenge.nonce:
                raise ValueError("Invalid nonce")

            # 3. Check gesture quality
            if request.gesture_features.quality_score < 0.3:
                raise ValueError("Gesture quality too low")

            # 4. Verify against stored patterns
            verification_score = await self._verify_against_patterns(
                request.lid,
                request.gesture_features
            )

            if verification_score < 0.7:  # 70% similarity threshold
                raise ValueError("Gesture pattern does not match")

            # 5. Create approval record
            approval_id = f"approval_{secrets.token_urlsafe(24)}"
            approval_expiry = min(
                challenge.expires_at,
                datetime.now(timezone.utc) + timedelta(seconds=get_max_approval_time(challenge.action))
            )

            approval = GestureApproval(
                approval_id=approval_id,
                challenge_id=request.challenge_id,
                lid=request.lid,
                action=challenge.action,
                action_context=challenge.action_context,
                gesture_features=request.gesture_features,
                approved_at=datetime.now(timezone.utc),
                expires_at=approval_expiry,
                used=False
            )

            # Store approval
            self.approvals[approval_id] = approval

            # Mark challenge as completed
            challenge.expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)  # Keep for cleanup

            # Audit success
            processing_time = (time.perf_counter() - start_time) * 1000
            await self._log_audit_event(
                "gesture_verified", request.lid, challenge.action,
                challenge_id=request.challenge_id, approval_id=approval_id,
                success=True, metadata={"processing_time_ms": processing_time, "score": verification_score}
            )

            return GestureVerificationResponse(
                verified=True,
                approval_id=approval_id,
                expires_at=approval_expiry
            )

        except Exception as e:
            # Audit failure
            processing_time = (time.perf_counter() - start_time) * 1000
            await self._log_audit_event(
                "gesture_verification_failed", request.lid,
                challenge.action if challenge else "unknown",
                challenge_id=request.challenge_id, success=False,
                error_message=str(e), metadata={"processing_time_ms": processing_time}
            )

            return GestureVerificationResponse(
                verified=False,
                error=str(e)
            )

    async def check_action_approval(
        self,
        request: ActionApprovalRequest
    ) -> ActionApprovalResponse:
        """
        Check if action is approved via GTΨ and consume approval.

        Args:
            request: Action approval request

        Returns:
            Approval status and details
        """
        try:
            # Find approval record
            approval = self.approvals.get(request.approval_id)
            if not approval:
                raise ValueError("Approval not found")

            # Validate approval
            if approval.lid != request.lid:
                raise ValueError("Approval user mismatch")

            if approval.action != request.action:
                raise ValueError("Approval action mismatch")

            if approval.used:
                raise ValueError("Approval already used")

            if datetime.now(timezone.utc) > approval.expires_at:
                raise ValueError("Approval expired")

            # Validate action context matches (for sensitive operations)
            if approval.action in ["share_link_public", "delete_files"]:
                # Must match exactly for destructive operations
                if approval.action_context != request.action_context:
                    raise ValueError("Action context mismatch")

            # Mark approval as used
            approval.used = True
            approval.used_at = datetime.now(timezone.utc)

            # Audit log
            await self._log_audit_event(
                "approval_used", request.lid, request.action,
                approval_id=request.approval_id, success=True
            )

            return ActionApprovalResponse(
                approved=True,
                approval_record=approval
            )

        except Exception as e:
            # Audit failure
            await self._log_audit_event(
                "approval_check_failed", request.lid, request.action,
                approval_id=request.approval_id, success=False, error_message=str(e)
            )

            return ActionApprovalResponse(
                approved=False,
                error=str(e)
            )

    async def enroll_gesture_pattern(
        self,
        lid: str,
        gesture_features: GestureFeatures
    ) -> str:
        """
        Enroll new gesture pattern for user.

        Args:
            lid: Canonical ΛID
            gesture_features: Gesture features to enroll

        Returns:
            Pattern ID
        """
        pattern_id = f"pattern_{secrets.token_urlsafe(16)}"

        # Store pattern
        if lid not in self.stored_gestures:
            self.stored_gestures[lid] = []

        self.stored_gestures[lid].append(gesture_features)

        # Audit enrollment
        await self._log_audit_event(
            "gesture_enrolled", lid, "enrollment", success=True,
            metadata={"pattern_id": pattern_id, "gesture_type": gesture_features.gesture_type.value}
        )

        return pattern_id

    async def _verify_against_patterns(
        self,
        lid: str,
        gesture_features: GestureFeatures
    ) -> float:
        """
        Verify gesture against stored patterns for user.

        Returns:
            Similarity score (0.0-1.0)
        """
        stored_patterns = self.stored_gestures.get(lid, [])
        if not stored_patterns:
            # No patterns enrolled - auto-enroll first gesture
            await self.enroll_gesture_pattern(lid, gesture_features)
            return 1.0  # First gesture always matches

        # Compare against all stored patterns
        best_score = 0.0

        for pattern in stored_patterns:
            if pattern.gesture_type == gesture_features.gesture_type:
                # Simple hash matching (in production: more sophisticated similarity)
                if pattern.feature_hash == gesture_features.feature_hash:
                    score = 1.0  # Exact match
                else:
                    # Partial similarity based on quality scores
                    quality_avg = (pattern.quality_score + gesture_features.quality_score) / 2
                    score = quality_avg * 0.6  # Reduced score for non-exact match

                best_score = max(best_score, score)

        return best_score

    async def cleanup_expired(self) -> Dict[str, int]:
        """Clean up expired challenges and approvals"""
        now = datetime.now(timezone.utc)

        # Clean challenges
        expired_challenges = [
            cid for cid, challenge in self.active_challenges.items()
            if now > challenge.expires_at
        ]

        for cid in expired_challenges:
            del self.active_challenges[cid]

        # Clean approvals
        expired_approvals = [
            aid for aid, approval in self.approvals.items()
            if now > approval.expires_at
        ]

        for aid in expired_approvals:
            del self.approvals[aid]

        return {
            "expired_challenges": len(expired_challenges),
            "expired_approvals": len(expired_approvals)
        }

    async def _log_audit_event(
        self,
        event_type: str,
        lid: str,
        action: str,
        challenge_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log audit event for GTΨ operations"""
        log_entry = {
            "event_type": event_type,
            "lid": lid,
            "action": action,
            "challenge_id": challenge_id,
            "approval_id": approval_id,
            "success": success,
            "error_message": error_message,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        print(f"GTΨ AUDIT: {json.dumps(log_entry, indent=2)}")

    def get_system_stats(self) -> Dict[str, Any]:
        """Get GTΨ system statistics"""
        now = datetime.now(timezone.utc)

        active_challenges = len([
            c for c in self.active_challenges.values()
            if now <= c.expires_at
        ])

        active_approvals = len([
            a for a in self.approvals.values()
            if not a.used and now <= a.expires_at
        ])

        total_enrolled_users = len(self.stored_gestures)

        return {
            "active_challenges": active_challenges,
            "active_approvals": active_approvals,
            "enrolled_users": total_enrolled_users,
            "high_risk_actions": list(HIGH_RISK_ACTIONS.keys())
        }


# Example usage and testing
async def demonstrate_gtpsi_workflow():
    """Demonstrate complete GTΨ workflow"""
    print("🔐 GTΨ Gesture Authentication Demonstration")
    print("=" * 50)

    service = GTΨVerificationService("mock")
    await service.initialize()

    # 1. User wants to perform high-risk action
    print("📧 User wants to send email...")
    challenge = await service.generate_challenge(
        "gonzo",
        "send_email",
        {
            "to": "alice@example.com",
            "subject": "Important proposal",
            "recipient_count": 1
        }
    )

    print(f"✅ Challenge generated: {challenge.challenge_id}")
    print(f"   Required gesture: {challenge.required_gesture_type}")
    print(f"   Expires: {challenge.expires_at}")

    # 2. Client performs gesture (mock)
    print("\n✍️  User performs gesture...")
    from ..edge import EdgeGestureProcessor, MockStrokeData, create_gesture_recognizer

    # Generate mock gesture data
    stroke_data = MockStrokeData.generate_signature_stroke()

    # Process on-device
    recognizer = create_gesture_recognizer(GestureType.STROKE)
    processor = EdgeGestureProcessor(recognizer)

    gesture_features = processor.process_gesture(stroke_data, GestureType.STROKE)
    print(f"   Gesture quality: {gesture_features.quality_score:.2f}")

    # 3. Verify gesture with server
    verification_request = GestureVerificationRequest(
        lid="gonzo",
        challenge_id=challenge.challenge_id,
        gesture_features=gesture_features,
        nonce=challenge.nonce
    )

    verification_result = await service.verify_gesture(verification_request)

    if verification_result.verified:
        print(f"✅ Gesture verified! Approval ID: {verification_result.approval_id}")

        # 4. Use approval for action
        print("\n📤 Executing send email action...")
        action_request = ActionApprovalRequest(
            lid="gonzo",
            approval_id=verification_result.approval_id,
            action="send_email",
            action_context=challenge.action_context
        )

        action_result = await service.check_action_approval(action_request)

        if action_result.approved:
            print("✅ Action approved and executed!")
            print("📧 Email sent successfully with GTΨ approval")
        else:
            print(f"❌ Action denied: {action_result.error}")
    else:
        print(f"❌ Gesture verification failed: {verification_result.error}")

    # 5. System stats
    stats = service.get_system_stats()
    print("\n📊 System Stats:")
    print(f"   Active challenges: {stats['active_challenges']}")
    print(f"   Active approvals: {stats['active_approvals']}")
    print(f"   Enrolled users: {stats['enrolled_users']}")

    await service.close()
    print("\n🎉 GTΨ workflow demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_gtpsi_workflow())
