"""
SEEDRA Core Framework
Secure Emotional & Encrypted Data for Realtime Access

This is the foundational consent and data management system for LUKHAS,
providing ethical guardrails for ABAS, DAST, and NIAS operations.
"""

import asyncio
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class ConsentLevel(Enum):
    """User consent levels for data access"""

    NONE = 0
    BASIC = 1
    ENHANCED = 2
    FULL = 3


class DataSensitivity(Enum):
    """Data sensitivity classification"""

    PUBLIC = 0
    PERSONAL = 1
    SENSITIVE = 2
    BIOMETRIC = 3
    EMOTIONAL = 4


class SEEDRACore:
    """
    Core SEEDRA implementation for consent management and data protection.

    Provides:
    - Granular consent management
    - Data encryption and access control
    - Ethical constraint enforcement
    - Real-time permission validation
    - Audit trail maintenance
    """

    def __init__(self):
        self.consent_registry: dict[str, dict[str, Any]] = {}
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.audit_log: list[dict[str, Any]] = []
        self.ethical_constraints: dict[str, Any] = (
            self._initialize_ethical_constraints()
        )
        self.data_classifications: dict[str, DataSensitivity] = {}
        self._lock = asyncio.Lock()

        logger.info("SEEDRA Core initialized")

    def _initialize_ethical_constraints(self) -> dict[str, Any]:
        """Initialize default ethical constraints"""
        return {
            "biometric_data": {
                "require_explicit_consent": True,
                "retention_days": 30,
                "on_device_only": True,
                "no_third_party_sharing": True,
            },
            "emotional_data": {
                "require_explicit_consent": True,
                "retention_days": 90,
                "anonymization_required": True,
                "therapeutic_use_only": False,
            },
            "behavioral_data": {
                "require_explicit_consent": False,
                "retention_days": 180,
                "aggregation_allowed": True,
                "marketing_use_allowed": False,
            },
            "location_data": {
                "require_explicit_consent": True,
                "retention_days": 7,
                "precision_limit": "city",
                "real_time_tracking": False,
            },
        }

    async def register_user_consent(
        self,
        user_id: str,
        consent_items: dict[str, bool],
        consent_level: ConsentLevel = ConsentLevel.BASIC,
        duration_days: int = 365,
    ) -> dict[str, Any]:
        """Register or update user consent preferences"""
        async with self._lock:
            timestamp = datetime.now()
            expiry = timestamp + timedelta(days=duration_days)

            consent_record = {
                "user_id": user_id,
                "consent_level": consent_level.value,
                "consent_items": consent_items,
                "timestamp": timestamp.isoformat(),
                "expiry": expiry.isoformat(),
                "version": self._generate_consent_version(user_id, timestamp),
                "active": True,
            }

            # Store consent record
            if user_id not in self.consent_registry:
                self.consent_registry[user_id] = {}

            self.consent_registry[user_id] = consent_record

            # Log consent update
            await self._log_audit_event(
                {
                    "event_type": "consent_registered",
                    "user_id": user_id,
                    "consent_level": consent_level.name,
                    "timestamp": timestamp.isoformat(),
                }
            )

            logger.info(
                f"Registered consent for user {user_id} at level {consent_level.name}"
            )

            return {
                "status": "success",
                "consent_version": consent_record["version"],
                "expiry": expiry.isoformat(),
            }

    async def check_consent(
        self, user_id: str, data_type: str, operation: str = "read"
    ) -> dict[str, Any]:
        """Check if user has consented to specific data operation"""
        async with self._lock:
            # Check if user has any consent record
            if user_id not in self.consent_registry:
                return {
                    "allowed": False,
                    "reason": "no_consent_record",
                    "required_action": "request_consent",
                }

            consent_record = self.consent_registry[user_id]

            # Check if consent is still valid
            if not self._is_consent_valid(consent_record):
                return {
                    "allowed": False,
                    "reason": "consent_expired",
                    "required_action": "renew_consent",
                }

            # Check specific consent item
            consent_items = consent_record.get("consent_items", {})
            consent_key = f"{data_type}_{operation}"

            if consent_key not in consent_items:
                # Check if data type has blanket consent
                if data_type in consent_items:
                    allowed = consent_items[data_type]
                else:
                    # Check consent level
                    allowed = self._check_consent_level(
                        ConsentLevel(consent_record["consent_level"]),
                        data_type,
                        operation,
                    )
            else:
                allowed = consent_items[consent_key]

            # Log consent check
            await self._log_audit_event(
                {
                    "event_type": "consent_checked",
                    "user_id": user_id,
                    "data_type": data_type,
                    "operation": operation,
                    "allowed": allowed,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "allowed": allowed,
                "consent_level": consent_record["consent_level"],
                "consent_version": consent_record["version"],
            }

    async def enforce_ethical_constraint(
        self, data_type: str, data_content: dict[str, Any], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Enforce ethical constraints on data operations"""
        constraints = self.ethical_constraints.get(data_type, {})

        # Check if explicit consent is required
        if constraints.get("require_explicit_consent", False):
            user_id = user_context.get("user_id")
            consent_check = await self.check_consent(user_id, data_type, "process")
            if not consent_check["allowed"]:
                return {
                    "allowed": False,
                    "reason": "explicit_consent_required",
                    "constraint": "ethical_requirement",
                }

        # Check data retention limits
        if "retention_days" in constraints:
            data_age = self._calculate_data_age(data_content)
            if data_age > constraints["retention_days"]:
                return {
                    "allowed": False,
                    "reason": "data_retention_exceeded",
                    "max_retention_days": constraints["retention_days"],
                }

        # Check processing restrictions
        if (
            constraints.get("on_device_only", False)
            and user_context.get("processing_location") != "device"
        ):
            return {"allowed": False, "reason": "on_device_processing_required"}

        # Check sharing restrictions
        if constraints.get("no_third_party_sharing", False):
            if user_context.get("destination_party") == "third_party":
                return {"allowed": False, "reason": "third_party_sharing_prohibited"}

        return {"allowed": True, "constraints_applied": list(constraints.keys())}

    async def create_session(
        self, user_id: str, session_type: str, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        """Create a new SEEDRA session for tracking data access"""
        session_id = self._generate_session_id(user_id, session_type)

        async with self._lock:
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "session_type": session_type,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "metadata": metadata or {},
                "access_log": [],
            }

            self.active_sessions[session_id] = session_data

            await self._log_audit_event(
                {
                    "event_type": "session_created",
                    "session_id": session_id,
                    "user_id": user_id,
                    "session_type": session_type,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return session_id

    async def log_data_access(
        self,
        session_id: str,
        data_type: str,
        operation: str,
        data_sensitivity: DataSensitivity,
        success: bool = True,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log data access within a session"""
        async with self._lock:
            if session_id not in self.active_sessions:
                logger.warning(
                    f"Attempted to log access for unknown session: {session_id}"
                )
                return

            access_record = {
                "timestamp": datetime.now().isoformat(),
                "data_type": data_type,
                "operation": operation,
                "sensitivity": data_sensitivity.name,
                "success": success,
                "metadata": metadata or {},
            }

            self.active_sessions[session_id]["access_log"].append(access_record)
            self.active_sessions[session_id][
                "last_activity"
            ] = datetime.now().isoformat()

            # Also log to audit trail
            await self._log_audit_event(
                {
                    "event_type": "data_access",
                    "session_id": session_id,
                    "data_type": data_type,
                    "operation": operation,
                    "sensitivity": data_sensitivity.name,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def get_user_data_summary(self, user_id: str) -> dict[str, Any]:
        """Get summary of user's data and consent status"""
        async with self._lock:
            consent_record = self.consent_registry.get(user_id, {})

            # Count active sessions
            active_session_count = sum(
                1
                for session in self.active_sessions.values()
                if session["user_id"] == user_id
            )

            # Get recent access logs
            recent_accesses = []
            for session in self.active_sessions.values():
                if session["user_id"] == user_id:
                    recent_accesses.extend(session["access_log"][-10:])

            return {
                "user_id": user_id,
                "consent_status": {
                    "has_consent": bool(consent_record),
                    "consent_level": (
                        ConsentLevel(consent_record.get("consent_level", 0)).name
                        if consent_record
                        else "NONE"
                    ),
                    "expiry": consent_record.get("expiry") if consent_record else None,
                    "is_valid": (
                        self._is_consent_valid(consent_record)
                        if consent_record
                        else False
                    ),
                },
                "active_sessions": active_session_count,
                "recent_data_accesses": sorted(
                    recent_accesses, key=lambda x: x["timestamp"], reverse=True
                )[:20],
            }

    async def revoke_consent(self, user_id: str) -> dict[str, Any]:
        """Revoke all consent for a user"""
        async with self._lock:
            if user_id in self.consent_registry:
                self.consent_registry[user_id]["active"] = False

                # End all active sessions
                sessions_ended = 0
                for session_id, session in list(self.active_sessions.items()):
                    if session["user_id"] == user_id:
                        del self.active_sessions[session_id]
                        sessions_ended += 1

                await self._log_audit_event(
                    {
                        "event_type": "consent_revoked",
                        "user_id": user_id,
                        "sessions_ended": sessions_ended,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                return {"status": "success", "sessions_ended": sessions_ended}

            return {"status": "no_consent_found", "user_id": user_id}

    def _is_consent_valid(self, consent_record: dict[str, Any]) -> bool:
        """Check if consent record is still valid"""
        if not consent_record.get("active", False):
            return False

        expiry_str = consent_record.get("expiry")
        if not expiry_str:
            return False

        expiry = datetime.fromisoformat(expiry_str)
        return datetime.now() < expiry

    def _check_consent_level(
        self, consent_level: ConsentLevel, data_type: str, operation: str
    ) -> bool:
        """Check if consent level allows specific operation"""
        # Basic level - only non-sensitive reads
        if consent_level == ConsentLevel.BASIC:
            return operation == "read" and data_type not in [
                "biometric_data",
                "emotional_data",
            ]

        # Enhanced level - most operations except biometric
        elif consent_level == ConsentLevel.ENHANCED:
            return data_type != "biometric_data" or operation == "read"

        # Full level - all operations allowed
        elif consent_level == ConsentLevel.FULL:
            return True

        # No consent
        return False

    def _generate_consent_version(self, user_id: str, timestamp: datetime) -> str:
        """Generate unique consent version hash"""
        data = f"{user_id}:{timestamp.isoformat()}:{id(self)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _generate_session_id(self, user_id: str, session_type: str) -> str:
        """Generate unique session ID"""
        data = f"{user_id}:{session_type}:{datetime.now().isoformat()}:{id(self)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def _calculate_data_age(self, data_content: dict[str, Any]) -> int:
        """Calculate age of data in days"""
        created_at = data_content.get("created_at")
        if not created_at:
            return 0

        created_date = datetime.fromisoformat(created_at)
        return (datetime.now() - created_date).days

    async def _log_audit_event(self, event: dict[str, Any]) -> None:
        """Log event to audit trail"""
        self.audit_log.append(event)

        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]

    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieve audit log entries"""
        filtered_log = self.audit_log

        if user_id:
            filtered_log = [e for e in filtered_log if e.get("user_id") == user_id]

        if event_type:
            filtered_log = [
                e for e in filtered_log if e.get("event_type") == event_type
            ]

        return filtered_log[-limit:]

    async def health_check(self) -> dict[str, Any]:
        """Check SEEDRA system health"""
        return {
            "status": "healthy",
            "active_users": len(self.consent_registry),
            "active_sessions": len(self.active_sessions),
            "audit_log_size": len(self.audit_log),
            "ethical_constraints": len(self.ethical_constraints),
            "timestamp": datetime.now().isoformat(),
        }


# Singleton instance
_seedra_instance = None


def get_seedra() -> SEEDRACore:
    """Get or create SEEDRA singleton instance"""
    global _seedra_instance
    if _seedra_instance is None:
        _seedra_instance = SEEDRACore()
    return _seedra_instance


__all__ = ["ConsentLevel", "DataSensitivity", "SEEDRACore", "get_seedra"]
