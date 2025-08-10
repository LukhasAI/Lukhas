"""
SEEDRA Core - Advanced Identity Management System
Provides secure identity verification and management for LUKHAS
"""

import base64
import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


@dataclass
class IdentityProfile:
    """Represents a user identity profile"""

    user_id: str
    username: str
    email: str
    verification_level: int  # 0-5 scale
    biometric_hash: Optional[str] = None
    created_at: datetime = None
    last_verified: datetime = None
    access_level: str = "basic"
    metadata: Dict = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class VerificationAttempt:
    """Represents an identity verification attempt"""

    user_id: str
    method: str
    success: bool
    confidence: float
    timestamp: datetime
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class SEEDRACore:
    """Core SEEDRA identity management system"""

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.profiles: Dict[str, IdentityProfile] = {}
        self.verification_history: List[VerificationAttempt] = []
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        self.max_failed_attempts = 3
        self.lockout_duration = timedelta(minutes=15)
        self.locked_users: Dict[str, datetime] = {}

    async def create_identity(self, user_id: str, username: str, email: str) -> bool:
        """Create a new identity profile"""
        try:
            if user_id in self.profiles:
                logger.warning(f"Identity already exists: {user_id}")
                return False

            profile = IdentityProfile(
                user_id=user_id, username=username, email=email, verification_level=0
            )

            self.profiles[user_id] = profile
            logger.info(f"Created identity profile for {username}")
            return True

        except Exception as e:
            logger.error(f"Failed to create identity: {e}")
            return False

    async def verify_identity(self, user_id: str, method: str, data: Dict) -> Dict:
        """Verify user identity using specified method"""
        try:
            # Check if user is locked out
            if await self._is_user_locked(user_id):
                return {
                    "success": False,
                    "reason": "account_locked",
                    "retry_after": self.locked_users[user_id] + self.lockout_duration,
                }

            if user_id not in self.profiles:
                return {"success": False, "reason": "user_not_found"}

            profile = self.profiles[user_id]

            # Perform verification based on method
            verification_result = await self._perform_verification(
                profile, method, data
            )

            # Record attempt
            attempt = VerificationAttempt(
                user_id=user_id,
                method=method,
                success=verification_result["success"],
                confidence=verification_result.get("confidence", 0.0),
                timestamp=datetime.utcnow(),
                details=verification_result.get("details", {}),
            )
            self.verification_history.append(attempt)

            # Update profile if successful
            if verification_result["success"]:
                profile.last_verified = datetime.utcnow()
                profile.verification_level = min(5, profile.verification_level + 1)

                # Remove from locked users if present
                if user_id in self.locked_users:
                    del self.locked_users[user_id]
            else:
                # Handle failed attempts
                await self._handle_failed_attempt(user_id)

            return verification_result

        except Exception as e:
            logger.error(f"Identity verification failed: {e}")
            return {"success": False, "reason": "verification_error"}

    async def _perform_verification(
        self, profile: IdentityProfile, method: str, data: Dict
    ) -> Dict:
        """Perform the actual verification based on method"""
        if method == "password":
            return await self._verify_password(profile, data.get("password", ""))
        elif method == "biometric":
            return await self._verify_biometric(profile, data.get("biometric_data", ""))
        elif method == "token":
            return await self._verify_token(profile, data.get("token", ""))
        elif method == "multi_factor":
            return await self._verify_multi_factor(profile, data)
        else:
            return {"success": False, "reason": "unsupported_method"}

    async def _verify_password(self, profile: IdentityProfile, password: str) -> Dict:
        """Verify password-based authentication"""
        # For demo purposes - in production, use proper password hashing
        stored_hash = profile.metadata.get("password_hash")
        if not stored_hash:
            return {"success": False, "reason": "no_password_set"}

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        success = password_hash == stored_hash

        return {
            "success": success,
            "confidence": 0.8 if success else 0.0,
            "method": "password",
        }

    async def _verify_biometric(
        self, profile: IdentityProfile, biometric_data: str
    ) -> Dict:
        """Verify biometric authentication"""
        if not profile.biometric_hash:
            return {"success": False, "reason": "no_biometric_enrolled"}

        # Simulate biometric matching (in production, use proper biometric SDK)
        biometric_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
        confidence = 0.95 if biometric_hash == profile.biometric_hash else 0.0

        return {
            "success": confidence > 0.8,
            "confidence": confidence,
            "method": "biometric",
        }

    async def _verify_token(self, profile: IdentityProfile, token: str) -> Dict:
        """Verify token-based authentication"""
        try:
            # Decrypt and validate token
            decrypted = self.fernet.decrypt(token.encode())
            token_data = json.loads(decrypted.decode())

            # Check token validity
            if token_data.get("user_id") != profile.user_id:
                return {"success": False, "reason": "invalid_token"}

            # Check expiration
            issued_at = datetime.fromisoformat(token_data.get("issued_at"))
            if datetime.utcnow() - issued_at > timedelta(hours=24):
                return {"success": False, "reason": "token_expired"}

            return {"success": True, "confidence": 0.9, "method": "token"}

        except Exception:
            return {"success": False, "reason": "invalid_token"}

    async def _verify_multi_factor(self, profile: IdentityProfile, data: Dict) -> Dict:
        """Verify multi-factor authentication"""
        factors = data.get("factors", [])
        if len(factors) < 2:
            return {"success": False, "reason": "insufficient_factors"}

        total_confidence = 0.0
        successful_factors = 0

        for factor in factors:
            result = await self._perform_verification(
                profile, factor["method"], factor["data"]
            )
            if result["success"]:
                successful_factors += 1
                total_confidence += result["confidence"]

        # Require at least 2 successful factors
        success = successful_factors >= 2
        average_confidence = total_confidence / len(factors) if factors else 0.0

        return {
            "success": success,
            "confidence": average_confidence,
            "method": "multi_factor",
            "factors_verified": successful_factors,
        }

    async def _is_user_locked(self, user_id: str) -> bool:
        """Check if user is currently locked out"""
        if user_id not in self.locked_users:
            return False

        lockout_time = self.locked_users[user_id]
        if datetime.utcnow() - lockout_time > self.lockout_duration:
            del self.locked_users[user_id]
            return False

        return True

    async def _handle_failed_attempt(self, user_id: str):
        """Handle failed authentication attempt"""
        # Count recent failed attempts
        recent_failures = [
            attempt
            for attempt in self.verification_history
            if (
                attempt.user_id == user_id
                and not attempt.success
                and datetime.utcnow() - attempt.timestamp < timedelta(minutes=15)
            )
        ]

        if len(recent_failures) >= self.max_failed_attempts:
            self.locked_users[user_id] = datetime.utcnow()
            logger.warning(f"User {user_id} locked due to too many failed attempts")

    async def set_password(self, user_id: str, password: str) -> bool:
        """Set password for user"""
        try:
            if user_id not in self.profiles:
                return False

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.profiles[user_id].metadata["password_hash"] = password_hash
            return True

        except Exception as e:
            logger.error(f"Failed to set password: {e}")
            return False

    async def enroll_biometric(self, user_id: str, biometric_data: str) -> bool:
        """Enroll biometric data for user"""
        try:
            if user_id not in self.profiles:
                return False

            biometric_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
            self.profiles[user_id].biometric_hash = biometric_hash
            return True

        except Exception as e:
            logger.error(f"Failed to enroll biometric: {e}")
            return False

    async def generate_access_token(self, user_id: str) -> Optional[str]:
        """Generate encrypted access token for user"""
        try:
            if user_id not in self.profiles:
                return None

            token_data = {
                "user_id": user_id,
                "issued_at": datetime.utcnow().isoformat(),
                "access_level": self.profiles[user_id].access_level,
            }

            token_json = json.dumps(token_data)
            encrypted_token = self.fernet.encrypt(token_json.encode())
            return encrypted_token.decode()

        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            return None

    async def get_identity_summary(self, user_id: str) -> Optional[Dict]:
        """Get summary of user identity"""
        if user_id not in self.profiles:
            return None

        profile = self.profiles[user_id]
        recent_attempts = [
            attempt
            for attempt in self.verification_history
            if (
                attempt.user_id == user_id
                and datetime.utcnow() - attempt.timestamp < timedelta(days=7)
            )
        ]

        return {
            "user_id": profile.user_id,
            "username": profile.username,
            "verification_level": profile.verification_level,
            "access_level": profile.access_level,
            "last_verified": (
                profile.last_verified.isoformat() if profile.last_verified else None
            ),
            "has_biometric": profile.biometric_hash is not None,
            "recent_attempts": len(recent_attempts),
            "is_locked": await self._is_user_locked(user_id),
        }

    async def export_identity_data(self, user_id: str) -> Optional[str]:
        """Export user identity data (encrypted)"""
        try:
            if user_id not in self.profiles:
                return None

            profile = self.profiles[user_id]
            data = asdict(profile)

            # Convert datetime objects to strings
            if data["created_at"]:
                data["created_at"] = data["created_at"].isoformat()
            if data["last_verified"]:
                data["last_verified"] = data["last_verified"].isoformat()

            json_data = json.dumps(data)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            return base64.b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"Failed to export identity data: {e}")
            return None
