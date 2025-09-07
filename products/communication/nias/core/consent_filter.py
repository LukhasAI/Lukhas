"""
Consent Filter for NIΛS System
Handles user consent verification and privacy protection
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Types of consent required in NIΛS system"""

    MESSAGE_DELIVERY = "message_delivery"
    DREAM_SEED_PLANTING = "dream_seed_planting"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    DATA_COLLECTION = "data_collection"
    BRAND_TARGETING = "brand_targeting"
    EMOTIONAL_STATE_ANALYSIS = "emotional_state_analysis"
    CROSS_SESSION_TRACKING = "cross_session_tracking"


class ConsentStatus(Enum):
    """Consent status levels"""

    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"


class ConsentFilter:
    """
    Advanced consent management system for NIΛS.

    Features:
    - Granular consent types
    - GDPR compliance
    - Automatic expiration
    - Consent withdrawal tracking
    - Privacy-first design
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/consent")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.user_consents: dict[str, dict[str, Any]] = {}
        self.consent_templates = self._initialize_consent_templates()
        self.privacy_policies = self._initialize_privacy_policies()

        logger.info("Consent Filter initialized with GDPR compliance")

    def _initialize_consent_templates(self) -> dict[str, dict[str, Any]]:
        """Initialize consent templates for different consent types"""
        return {
            ConsentType.MESSAGE_DELIVERY.value: {
                "title": "Non-Intrusive Message Delivery",
                "description": "Allow NIΛS to deliver symbolic messages based on your interests",
                "required_for_tiers": ["T1", "T2", "T3"],
                "duration_days": 365,
                "revocable": True,
                "data_processing": [
                    "User preferences analysis",
                    "Message personalization",
                    "Delivery timing optimization",
                ],
            },
            ConsentType.DREAM_SEED_PLANTING.value: {
                "title": "Dream Seed Experience",
                "description": "Allow brands to plant symbolic seeds in your dream experiences",
                "required_for_tiers": ["T1", "T2"],
                "duration_days": 365,
                "revocable": True,
                "data_processing": [
                    "Sleep pattern analysis",
                    "Symbolic preference mapping",
                    "Dream narrative generation",
                ],
            },
            ConsentType.BEHAVIORAL_ANALYSIS.value: {
                "title": "Behavioral Pattern Analysis",
                "description": "Analyze interaction patterns to improve your experience",
                "required_for_tiers": ["T1", "T2", "T3"],
                "duration_days": 180,
                "revocable": True,
                "data_processing": [
                    "Interaction timing analysis",
                    "Preference learning",
                    "Usage pattern optimization",
                ],
            },
            ConsentType.DATA_COLLECTION.value: {
                "title": "Enhanced Data Collection",
                "description": "Collect additional data points for personalization",
                "required_for_tiers": ["T1"],
                "duration_days": 365,
                "revocable": True,
                "data_processing": [
                    "Extended interaction logging",
                    "Cross-device synchronization",
                    "Advanced personalization metrics",
                ],
            },
            ConsentType.BRAND_TARGETING.value: {
                "title": "Brand-Based Targeting",
                "description": "Allow brands to target you with personalized content",
                "required_for_tiers": ["T2", "T3"],
                "duration_days": 90,
                "revocable": True,
                "data_processing": [
                    "Brand preference analysis",
                    "Purchase intent prediction",
                    "Product recommendation generation",
                ],
            },
            ConsentType.EMOTIONAL_STATE_ANALYSIS.value: {
                "title": "Emotional State Consideration",
                "description": "Analyze emotional state to optimize message timing",
                "required_for_tiers": ["T1"],
                "duration_days": 365,
                "revocable": True,
                "data_processing": [
                    "Emotional state inference",
                    "Timing optimization",
                    "Wellness consideration",
                ],
            },
            ConsentType.CROSS_SESSION_TRACKING.value: {
                "title": "Cross-Session Experience",
                "description": "Track experiences across multiple sessions for continuity",
                "required_for_tiers": ["T1", "T2"],
                "duration_days": 365,
                "revocable": True,
                "data_processing": [
                    "Session correlation",
                    "Experience continuity",
                    "Long-term preference learning",
                ],
            },
        }

    def _initialize_privacy_policies(self) -> dict[str, dict[str, Any]]:
        """Initialize privacy policy configurations"""
        return {
            "data_retention": {
                "T1": {"days": 365, "automatic_deletion": False},
                "T2": {"days": 180, "automatic_deletion": True},
                "T3": {"days": 30, "automatic_deletion": True},
            },
            "data_sharing": {
                "T1": {"third_party": False, "anonymized_analytics": True},
                "T2": {"third_party": False, "anonymized_analytics": True},
                "T3": {"third_party": False, "anonymized_analytics": True},
            },
            "user_rights": {
                "data_portability": True,
                "right_to_deletion": True,
                "right_to_rectification": True,
                "right_to_access": True,
                "right_to_object": True,
            },
        }

    async def request_consent(
        self,
        user_id: str,
        consent_types: list[ConsentType],
        tier: str = "T3",
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Request consent from user for specific consent types.

        Args:
            user_id: User identifier
            consent_types: List of consent types being requested
            tier: User tier for appropriate consent requirements
            context: Additional context for consent request

        Returns:
            Consent request configuration for UI display
        """
        try:
            consent_request = {
                "request_id": f"consent_req_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "user_id": user_id,
                "tier": tier,
                "requested_at": datetime.now(timezone.utc).isoformat(),
                "consent_items": [],
                "privacy_notice": self._get_privacy_notice(tier),
                "user_rights": self.privacy_policies["user_rights"],
                "context": context or {},
            }

            for consent_type in consent_types:
                template = self.consent_templates.get(consent_type.value)
                if not template:
                    continue

                # Check if consent is required for this tier
                if tier not in template.get("required_for_tiers", []):
                    continue

                consent_item = {
                    "consent_type": consent_type.value,
                    "title": template["title"],
                    "description": template["description"],
                    "duration_days": template["duration_days"],
                    "revocable": template["revocable"],
                    "data_processing": template["data_processing"],
                    "required": True,  # All NIAS consents are currently required
                    "current_status": await self._get_current_consent_status(user_id, consent_type),
                }

                consent_request["consent_items"].append(consent_item)

            logger.info(f"Consent requested for user {user_id}: {[ct.value for ct in consent_types]}")
            return consent_request

        except Exception as e:
            logger.error(f"Failed to create consent request for {user_id}: {e}")
            return {"error": str(e), "request_id": None}

    async def grant_consent(self, user_id: str, consent_grants: dict[str, bool], request_id: str) -> dict[str, Any]:
        """
        Process user's consent grants/denials.

        Args:
            user_id: User identifier
            consent_grants: Dictionary mapping consent_type to boolean grant status
            request_id: Original request identifier for tracking

        Returns:
            Processing result with granted/denied breakdown
        """
        try:
            if user_id not in self.user_consents:
                self.user_consents[user_id] = {
                    "user_id": user_id,
                    "consents": {},
                    "consent_history": [],
                    "last_updated": None,
                }

            user_consent_data = self.user_consents[user_id]
            granted_consents = []
            denied_consents = []

            for consent_type, granted in consent_grants.items():
                template = self.consent_templates.get(consent_type)
                if not template:
                    continue

                if granted:
                    # Grant consent
                    expiry_date = datetime.now(timezone.utc) + timedelta(days=template["duration_days"])

                    user_consent_data["consents"][consent_type] = {
                        "status": ConsentStatus.GRANTED.value,
                        "granted_at": datetime.now(timezone.utc).isoformat(),
                        "expires_at": expiry_date.isoformat(),
                        "request_id": request_id,
                        "version": "1.0",
                        "revocable": template["revocable"],
                    }
                    granted_consents.append(consent_type)
                else:
                    # Deny consent
                    user_consent_data["consents"][consent_type] = {
                        "status": ConsentStatus.DENIED.value,
                        "denied_at": datetime.now(timezone.utc).isoformat(),
                        "request_id": request_id,
                        "version": "1.0",
                    }
                    denied_consents.append(consent_type)

                # Add to consent history
                user_consent_data["consent_history"].append(
                    {
                        "consent_type": consent_type,
                        "action": "granted" if granted else "denied",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "request_id": request_id,
                    }
                )

            user_consent_data["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Save to persistent storage
            await self._save_user_consent_data(user_id)

            logger.info(
                f"Processed consent for {user_id}: granted={len(granted_consents)}, denied={len(denied_consents)}"
            )

            return {
                "success": True,
                "user_id": user_id,
                "request_id": request_id,
                "granted_consents": granted_consents,
                "denied_consents": denied_consents,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to process consent for {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def check_consent(
        self,
        user_id: str,
        message: dict[str, Any],
        required_consents: Optional[list[ConsentType]] = None,
    ) -> dict[str, Any]:
        """
        Check if user has valid consent for message delivery.

        Args:
            user_id: User identifier
            message: Message requiring consent verification
            required_consents: Specific consents required (auto-detected if None)

        Returns:
            Consent check result with approval status
        """
        try:
            if user_id not in self.user_consents:
                # Load from storage
                await self._load_user_consent_data(user_id)

            if user_id not in self.user_consents:
                return {
                    "approved": False,
                    "reason": "no_consent_data",
                    "required_consents": self._determine_required_consents(message),
                }

            user_consent_data = self.user_consents[user_id]

            # Determine required consents
            if not required_consents:
                required_consents = self._determine_required_consents(message)

            # Check each required consent
            consent_results = {}
            all_approved = True

            for consent_type in required_consents:
                consent_key = consent_type.value
                consent_info = user_consent_data["consents"].get(consent_key)

                if not consent_info:
                    consent_results[consent_key] = {
                        "status": "missing",
                        "approved": False,
                    }
                    all_approved = False
                    continue

                # Check consent status and expiry
                status = consent_info["status"]

                if status == ConsentStatus.DENIED.value:
                    consent_results[consent_key] = {
                        "status": "denied",
                        "approved": False,
                        "denied_at": consent_info["denied_at"],
                    }
                    all_approved = False

                elif status == ConsentStatus.WITHDRAWN.value:
                    consent_results[consent_key] = {
                        "status": "withdrawn",
                        "approved": False,
                        "withdrawn_at": consent_info["withdrawn_at"],
                    }
                    all_approved = False

                elif status == ConsentStatus.GRANTED.value:
                    # Check expiry
                    expires_at = datetime.fromisoformat(consent_info["expires_at"])
                    if datetime.now(timezone.utc) > expires_at:
                        consent_results[consent_key] = {
                            "status": "expired",
                            "approved": False,
                            "expired_at": consent_info["expires_at"],
                        }
                        all_approved = False

                        # Update status to expired
                        consent_info["status"] = ConsentStatus.EXPIRED.value
                        await self._save_user_consent_data(user_id)
                    else:
                        consent_results[consent_key] = {
                            "status": "granted",
                            "approved": True,
                            "granted_at": consent_info["granted_at"],
                            "expires_at": consent_info["expires_at"],
                        }

                else:
                    consent_results[consent_key] = {
                        "status": "unknown",
                        "approved": False,
                    }
                    all_approved = False

            return {
                "approved": all_approved,
                "user_id": user_id,
                "consent_results": consent_results,
                "required_consents": [ct.value for ct in required_consents],
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to check consent for {user_id}: {e}")
            return {"approved": False, "error": str(e)}

    def _determine_required_consents(self, message: dict[str, Any]) -> list[ConsentType]:
        """Determine which consents are required for a message"""
        required = [ConsentType.MESSAGE_DELIVERY]

        # Check message features
        if message.get("dream_seed"):
            required.append(ConsentType.DREAM_SEED_PLANTING)

        if message.get("brand_targeting"):
            required.append(ConsentType.BRAND_TARGETING)

        if message.get("behavioral_analysis"):
            required.append(ConsentType.BEHAVIORAL_ANALYSIS)

        if message.get("emotional_gating"):
            required.append(ConsentType.EMOTIONAL_STATE_ANALYSIS)

        if message.get("cross_session"):
            required.append(ConsentType.CROSS_SESSION_TRACKING)

        return required

    async def _get_current_consent_status(self, user_id: str, consent_type: ConsentType) -> str:
        """Get current consent status for a user and consent type"""
        if user_id not in self.user_consents:
            await self._load_user_consent_data(user_id)

        if user_id not in self.user_consents:
            return ConsentStatus.PENDING.value

        consent_info = self.user_consents[user_id]["consents"].get(consent_type.value)
        if not consent_info:
            return ConsentStatus.PENDING.value

        return consent_info["status"]

    def _get_privacy_notice(self, tier: str) -> dict[str, Any]:
        """Get tier-specific privacy notice"""
        retention = self.privacy_policies["data_retention"].get(tier, self.privacy_policies["data_retention"]["T3"])
        sharing = self.privacy_policies["data_sharing"].get(tier, self.privacy_policies["data_sharing"]["T3"])

        return {
            "data_retention_days": retention["days"],
            "automatic_deletion": retention["automatic_deletion"],
            "third_party_sharing": sharing["third_party"],
            "anonymized_analytics": sharing["anonymized_analytics"],
            "user_rights": self.privacy_policies["user_rights"],
        }

    async def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> dict[str, Any]:
        """Allow user to withdraw consent"""
        try:
            if user_id not in self.user_consents:
                await self._load_user_consent_data(user_id)

            if user_id not in self.user_consents:
                return {"success": False, "error": "No consent data found"}

            consent_key = consent_type.value
            consent_info = self.user_consents[user_id]["consents"].get(consent_key)

            if not consent_info:
                return {"success": False, "error": "Consent not found"}

            if not consent_info.get("revocable", True):
                return {"success": False, "error": "Consent is not revocable"}

            # Update consent status
            consent_info["status"] = ConsentStatus.WITHDRAWN.value
            consent_info["withdrawn_at"] = datetime.now(timezone.utc).isoformat()

            # Add to history
            self.user_consents[user_id]["consent_history"].append(
                {
                    "consent_type": consent_key,
                    "action": "withdrawn",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": "user_request",
                }
            )

            self.user_consents[user_id]["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Save changes
            await self._save_user_consent_data(user_id)

            logger.info(f"Consent withdrawn: {user_id} - {consent_key}")

            return {
                "success": True,
                "user_id": user_id,
                "consent_type": consent_key,
                "withdrawn_at": consent_info["withdrawn_at"],
            }

        except Exception as e:
            logger.error(f"Failed to withdraw consent for {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _save_user_consent_data(self, user_id: str):
        """Save user consent data to persistent storage"""
        try:
            user_file = self.storage_path / f"{user_id}_consent.json"
            with open(user_file, "w", encoding="utf-8") as f:
                json.dump(self.user_consents[user_id], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save consent data for {user_id}: {e}")

    async def _load_user_consent_data(self, user_id: str):
        """Load user consent data from persistent storage"""
        try:
            user_file = self.storage_path / f"{user_id}_consent.json"
            if user_file.exists():
                with open(user_file, encoding="utf-8") as f:
                    self.user_consents[user_id] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load consent data for {user_id}: {e}")

    async def get_user_consent_summary(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive consent summary for a user"""
        if user_id not in self.user_consents:
            await self._load_user_consent_data(user_id)

        if user_id not in self.user_consents:
            return {"error": "No consent data found"}

        user_data = self.user_consents[user_id]
        consent_summary = {
            "user_id": user_id,
            "last_updated": user_data["last_updated"],
            "consent_status": {},
            "active_consents": [],
            "expired_consents": [],
            "withdrawn_consents": [],
            "denied_consents": [],
        }

        for consent_type, consent_info in user_data["consents"].items():
            status = consent_info["status"]
            consent_summary["consent_status"][consent_type] = {
                "status": status,
                "details": consent_info,
            }

            if status == ConsentStatus.GRANTED.value:
                # Check if still active
                expires_at = datetime.fromisoformat(consent_info["expires_at"])
                if datetime.now(timezone.utc) <= expires_at:
                    consent_summary["active_consents"].append(consent_type)
                else:
                    consent_summary["expired_consents"].append(consent_type)
            elif status == ConsentStatus.WITHDRAWN.value:
                consent_summary["withdrawn_consents"].append(consent_type)
            elif status == ConsentStatus.DENIED.value:
                consent_summary["denied_consents"].append(consent_type)

        return consent_summary

    async def health_check(self) -> dict[str, Any]:
        """Health check for consent filter"""
        return {
            "status": "healthy",
            "total_users": len(self.user_consents),
            "consent_types_available": len(self.consent_templates),
            "storage_path": str(self.storage_path),
            "storage_accessible": self.storage_path.exists() and self.storage_path.is_dir(),
        }


# Global consent filter instance
_global_consent_filter = None


def get_consent_filter() -> ConsentFilter:
    """Get the global consent filter instance"""
    global _global_consent_filter
    if _global_consent_filter is None:
        _global_consent_filter = ConsentFilter()
    return _global_consent_filter
